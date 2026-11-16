# pii-redaction.04redaction-rules Redaction Rules as Code

> A policy object maps entity types to actions; a pure function applies it to detector offsets, right-to-left.

## Index

- [1. The Policy Object](#1-the-policy-object)
  - [1.1 Code: Policy and Defaults](#11-code-policy-and-defaults)
- [2. Apply Algorithm](#2-apply-algorithm)
  - [2.1 Why Right-to-Left](#21-why-right-to-left)
  - [2.2 Code: redact_text](#22-code-redact_text)
  - [2.3 Code: Detect + Apply](#23-code-detect--apply)
- [3. Threshold Trade-off](#3-threshold-trade-off)

Back to [00index](pii-redaction.00index.md).

## 1. The Policy Object

The console shows checkboxes per entity type; in code it is a policy object.

- `entity type → action`
  - MASK, REPLACE, PSEUDONYMIZE, BLOCK, KEEP
- `min_score` per policy (optionally per type)
- `mask_char`
- Default action for unlisted types

### 1.1 Code: Policy and Defaults

```python
# app/domain/_04safety_02pii_redaction.py
class RedactAction(StrEnum):
    MASK = "MASK"  # "jane@x.com" -> "**********"   irreversible, keeps length
    REPLACE = "REPLACE"  # -> "[EMAIL]"                 irreversible, keeps meaning for the model
    PSEUDONYMIZE = "PSEUDONYMIZE"  # -> "<<EMAIL_9f2c1a7b>>"  reversible through the vault
    BLOCK = "BLOCK"  # refuse the whole text
    KEEP = "KEEP"  # detected but allowed (e.g. DATE_TIME in a scheduling bot)


@dataclass(frozen=True)
class RedactionPolicy:
    rules: dict[str, RedactAction]
    default_action: RedactAction = RedactAction.REPLACE
    min_score: float = 0.8
    per_type_min_score: dict[str, float] = field(default_factory=dict)  # low for SSN, higher for NAME
    mask_char: str = "*"

    def action_for(self, entity_type: str) -> RedactAction:
        return self.rules.get(entity_type, self.default_action)

    def threshold_for(self, entity_type: str) -> float:
        return self.per_type_min_score.get(entity_type, self.min_score)
```

```python
# app/domain/_04safety_02pii_redaction.py
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
```

## 2. Apply Algorithm

Threshold, then BLOCK check, then overlaps, then replace from the end.

→ detect entities  
→ drop entities with score < threshold  
→ if any entity's action is BLOCK ⇒ refuse the request  
→ resolve overlaps (keep the higher score, then the longer span)  
→ sort by `BeginOffset` descending  
→ replace `text[begin:end]` with the action's output

### 2.1 Why Right-to-Left

- Replacing a span changes the length of everything after it
- Edits from the end keep earlier offsets valid
- Offsets are character offsets
  - they must match Python `str` indexes (code points)
  - test with multi-byte text; mismatched units corrupt text silently

### 2.2 Code: redact_text

```python
# app/domain/_04safety_02pii_redaction.py
def resolve_overlaps(entities: list[PiiEntity]) -> list[PiiEntity]:
    """Keep non-overlapping spans: higher score wins, then the longer span (e.g. ADDRESS over a NAME inside it)."""
    kept: list[PiiEntity] = []
    for e in sorted(entities, key=lambda x: (-x.score, -x.length, x.begin)):
        if all(e.end <= k.begin or e.begin >= k.end for k in kept):
            kept.append(e)
    return kept


def redact_text(
    text: str, entities: list[PiiEntity], policy: RedactionPolicy, vault: PseudonymVault | None = None
) -> RedactionResult:
    confident = [e for e in entities if e.score >= policy.threshold_for(e.type)]
    skipped = len(entities) - len(confident)
    blocked = tuple(sorted({e.type for e in confident if policy.action_for(e.type) == RedactAction.BLOCK}))
    if blocked:
        return RedactionResult(text="", skipped_low_score=skipped, blocked_types=blocked)

    out = text
    applied: list[PiiEntity] = []
    for e in sorted(resolve_overlaps(confident), key=lambda x: x.begin, reverse=True):  # right-to-left
        action = policy.action_for(e.type)
        if action == RedactAction.KEEP:
            continue
        value = text[e.begin : e.end]
        out = out[: e.begin] + _replacement(e, value, action, policy, vault) + out[e.end :]
        applied.append(e)
    applied.reverse()  # report in reading order
    return RedactionResult(text=out, applied=tuple(applied), skipped_low_score=skipped)
```

- `_replacement` per action
  - MASK: `mask_char * len(value)`
  - REPLACE: `[TYPE]`
  - PSEUDONYMIZE: `vault.tokenize(...)`
    - no vault ⇒ degrade to irreversible `[TYPE]`, never leak
- Catch
  - Works on offsets from any detector, so Comprehend Medical `DetectPHI` reuses it

### 2.3 Code: Detect + Apply

- The contains-gate skips detect on Personally Identifiable Information (PII)-free text

```python
# app/infra/_04safety_02pii_redaction.py
def redact(
    text: str, policy: RedactionPolicy, vault: PseudonymVault | None = None, precheck: bool = True
) -> RedactionResult:
    """Contains (optional gate) -> detect -> policy apply. Returns redacted text + types/counts to log."""
    if precheck and len(text.encode()) <= MAX_SYNC_BYTES:
        labels = contains_pii(text, None)
        if not any(score >= policy.threshold_for(t) for t, score in labels.items()):
            return RedactionResult(text=text)  # nothing confident: no detect call
    return redact_text(text, detect_pii(text), policy, vault)
```

## 3. Threshold Trade-off

One global number either leaks or mangles; set thresholds per type.

- Low (0.5)
  - catches more
  - masks "May" (month) as a name ⇒ hurts answer quality
- High (0.95)
  - clean text
  - misses partial names ⇒ leak
- Set per type
  - Social Security Number (SSN) and card at 0.5 (cost of a miss is high)
  - NAME at 0.8 (order of magnitude; tune on data)
- Choose on a labeled sample of real text
  - measure recall and precision per type at several thresholds
