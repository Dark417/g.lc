"""Domain for PII redaction: the redaction policy (rules as code), entities, the vault port, pure apply logic.

- No boto3 here: redact_text works on offsets from ANY detector (Comprehend, Comprehend Medical, Presidio, regex).
- Entity types use Comprehend names (EMAIL, PHONE, SSN, CREDIT_DEBIT_NUMBER, ...); Guardrails uses different
  names for some (US_SOCIAL_SECURITY_NUMBER, CREDIT_DEBIT_CARD_NUMBER).
"""

import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol

# ================================================================ policy (how you configure redaction in code)


class RedactAction(StrEnum):
    MASK = "MASK"  # "jane@x.com" -> "**********"   irreversible, keeps length
    REPLACE = "REPLACE"  # -> "[EMAIL]"                 irreversible, keeps meaning for the model
    PSEUDONYMIZE = "PSEUDONYMIZE"  # -> "<<EMAIL_9f2c1a7b>>"  reversible through the vault
    BLOCK = "BLOCK"  # refuse the whole text
    KEEP = "KEEP"  # detected but allowed (e.g. DATE_TIME in a scheduling bot)


@dataclass(frozen=True)
class RedactionPolicy:
    """Entity type -> action, plus confidence thresholds. The code equivalent of the console checkboxes.

    min_score: default threshold (0..1). Entities scoring below their threshold are ignored.
    per_type_min_score: overrides; low for high-cost misses (SSN), higher for noisy types (NAME).
    """

    rules: dict[str, RedactAction]
    default_action: RedactAction = RedactAction.REPLACE
    min_score: float = 0.8
    per_type_min_score: dict[str, float] = field(default_factory=dict)
    mask_char: str = "*"

    def action_for(self, entity_type: str) -> RedactAction:
        return self.rules.get(entity_type, self.default_action)

    def threshold_for(self, entity_type: str) -> float:
        return self.per_type_min_score.get(entity_type, self.min_score)

    def redacted_types(self) -> list[str]:
        """Types the async job should handle (anything not KEEP); unlisted types fall to default_action."""
        return sorted(t for t, a in self.rules.items() if a != RedactAction.KEEP)


def default_policy(min_score: float = 0.8) -> RedactionPolicy:
    a = RedactAction
    return RedactionPolicy(
        rules={
            "SSN": a.BLOCK,  # never accepted in chat
            "CREDIT_DEBIT_NUMBER": a.BLOCK,
            "AWS_SECRET_KEY": a.BLOCK,
            "PASSWORD": a.BLOCK,
            "EMAIL": a.PSEUDONYMIZE,  # the answer may need it back ("we emailed <<EMAIL_..>>")
            "PHONE": a.PSEUDONYMIZE,
            "NAME": a.PSEUDONYMIZE,
            "ADDRESS": a.REPLACE,
            "BANK_ACCOUNT_NUMBER": a.MASK,
            "IP_ADDRESS": a.MASK,
            "DATE_TIME": a.KEEP,  # dates are rarely identifying alone and the bot needs them
        },
        default_action=a.REPLACE,
        min_score=min_score,
        per_type_min_score={"SSN": 0.5, "CREDIT_DEBIT_NUMBER": 0.5, "AWS_SECRET_KEY": 0.5, "NAME": 0.85},
    )


# ================================================================ entities and results


@dataclass(frozen=True)
class PiiEntity:
    type: str
    score: float
    begin: int  # character offset, inclusive
    end: int  # character offset, exclusive

    @property
    def length(self) -> int:
        return self.end - self.begin


@dataclass(frozen=True)
class RedactionResult:
    text: str  # redacted text ("" when blocked)
    applied: tuple[PiiEntity, ...] = ()
    skipped_low_score: int = 0
    blocked_types: tuple[str, ...] = ()

    @property
    def blocked(self) -> bool:
        return bool(self.blocked_types)

    def summary(self) -> dict[str, int]:
        """Types + counts: the only thing safe to log."""
        counts: dict[str, int] = {}
        for e in self.applied:
            counts[e.type] = counts.get(e.type, 0) + 1
        return counts


class PiiBlockedError(Exception):
    def __init__(self, types: tuple[str, ...]) -> None:
        super().__init__(f"text contains blocked PII types: {sorted(set(types))}")
        self.types = types


# ================================================================ vault port (reversible pseudonyms)

TOKEN_RE = re.compile(r"<<([A-Z_]+)_([0-9a-f]{8,32})>>")


class PseudonymVault(Protocol):
    """Reversible tokenization. tokenize must be deterministic per (type, value) within one key epoch."""

    def tokenize(self, entity_type: str, value: str) -> str: ...

    def detokenize(self, token: str) -> str | None: ...


def detokenize_text(text: str, vault: PseudonymVault) -> str:
    """Replace <<TYPE_hash>> tokens with original values. Only for an authorized caller, after output checks."""

    def sub(m: re.Match[str]) -> str:
        value = vault.detokenize(m.group(0))
        return value if value is not None else m.group(0)

    return TOKEN_RE.sub(sub, text)


# ================================================================ pure apply logic


def resolve_overlaps(entities: list[PiiEntity]) -> list[PiiEntity]:
    """Keep non-overlapping spans: higher score wins, then the longer span (e.g. ADDRESS over a NAME inside it)."""
    kept: list[PiiEntity] = []
    for e in sorted(entities, key=lambda x: (-x.score, -x.length, x.begin)):
        if all(e.end <= k.begin or e.begin >= k.end for k in kept):
            kept.append(e)
    return kept


def _replacement(e: PiiEntity, value: str, action: RedactAction, policy: RedactionPolicy, vault: PseudonymVault | None) -> str:
    if action == RedactAction.MASK:
        return policy.mask_char * len(value)
    if action == RedactAction.REPLACE:
        return f"[{e.type}]"
    if action == RedactAction.PSEUDONYMIZE:
        if vault is None:
            return f"[{e.type}]"  # no vault -> degrade to irreversible replace, never leak
        return vault.tokenize(e.type, value)
    return value  # KEEP


def redact_text(
    text: str, entities: list[PiiEntity], policy: RedactionPolicy, vault: PseudonymVault | None = None
) -> RedactionResult:
    """Apply a policy to detector offsets: threshold -> BLOCK check -> overlaps -> replace right-to-left.

    Right-to-left because each replacement changes the length of the text after it; editing from the end keeps
    every earlier offset valid. Catch: offsets must be in the same unit as Python str indexes (code points).
    """
    confident = [e for e in entities if e.score >= policy.threshold_for(e.type)]
    skipped = len(entities) - len(confident)
    blocked = tuple(sorted({e.type for e in confident if policy.action_for(e.type) == RedactAction.BLOCK}))
    if blocked:
        return RedactionResult(text="", skipped_low_score=skipped, blocked_types=blocked)

    out = text
    applied: list[PiiEntity] = []
    for e in sorted(resolve_overlaps(confident), key=lambda x: x.begin, reverse=True):
        action = policy.action_for(e.type)
        if action == RedactAction.KEEP:
            continue
        value = text[e.begin : e.end]
        out = out[: e.begin] + _replacement(e, value, action, policy, vault) + out[e.end :]
        applied.append(e)
    applied.reverse()  # report in reading order
    return RedactionResult(text=out, applied=tuple(applied), skipped_low_score=skipped)
