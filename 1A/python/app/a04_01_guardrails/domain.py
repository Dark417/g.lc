"""Domain for the guardrails slice: policy specs (config as code), verdict models, ports. No boto3 here.

- GuardrailSpec mirrors terraform/04.01.guardrails.tf field by field; infra.py turns it into the
  CreateGuardrail / UpdateGuardrail request with one builder per policy type.
- GuardrailVerdict is the parsed ApplyGuardrail / Converse-trace result the rest of the app works with.
- Ports (GuardrailPort, ChatModelPort) let the service guard ANY model: Bedrock, SageMaker, or another provider.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol

# ================================================================ enums (values = API strings)


class Source(StrEnum):
    INPUT = "INPUT"  # user prompt side: content, prompt attack, topics, words, PII
    OUTPUT = "OUTPUT"  # model answer side: + contextual grounding, automated reasoning


class Qualifier(StrEnum):
    # Tags on a text block. Contextual grounding needs all three; without them it is skipped.
    GROUNDING_SOURCE = "grounding_source"  # retrieved passages the answer must be supported by
    QUERY = "query"  # the user question
    GUARD_CONTENT = "guard_content"  # the text to evaluate (model answer on OUTPUT)


class Strength(StrEnum):
    # Lowest classifier confidence that blocks. HIGH = blocks LOW/MEDIUM/HIGH confidence = most recall + FP.
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class FilterAction(StrEnum):
    BLOCK = "BLOCK"
    NONE = "NONE"  # detect mode: evaluated and reported (detected=true), not enforced


class PiiAction(StrEnum):
    BLOCK = "BLOCK"  # refuse the whole call
    ANONYMIZE = "ANONYMIZE"  # replace with {TYPE}, continue
    NONE = "NONE"  # detect only


class Tier(StrEnum):
    CLASSIC = "CLASSIC"
    STANDARD = "STANDARD"  # needs a cross-Region guardrail profile


# ================================================================ policy specs (config as code)


@dataclass(frozen=True)
class ContentFilterSpec:
    type: str  # HATE | INSULTS | SEXUAL | VIOLENCE | MISCONDUCT | PROMPT_ATTACK
    input_strength: Strength
    output_strength: Strength  # PROMPT_ATTACK: must be NONE
    input_action: FilterAction = FilterAction.BLOCK
    output_action: FilterAction = FilterAction.BLOCK
    input_modalities: tuple[str, ...] = ("TEXT",)  # TEXT | IMAGE
    output_modalities: tuple[str, ...] = ("TEXT",)


@dataclass(frozen=True)
class TopicSpec:
    name: str
    definition: str  # describe the topic; do not write "don't ..." (Classic: short, check the quota page)
    examples: tuple[str, ...] = ()  # up to 5 user phrasings
    input_action: FilterAction = FilterAction.BLOCK  # API only; Terraform 6.73 cannot set these two
    output_action: FilterAction = FilterAction.BLOCK


@dataclass(frozen=True)
class WordSpec:
    text: str  # exact word or short phrase, case-insensitive
    input_action: FilterAction = FilterAction.BLOCK
    output_action: FilterAction = FilterAction.BLOCK


@dataclass(frozen=True)
class PiiSpec:
    type: str  # EMAIL, PHONE, NAME, US_SOCIAL_SECURITY_NUMBER, CREDIT_DEBIT_CARD_NUMBER, ... (31 types)
    action: PiiAction
    input_action: PiiAction | None = None  # None = same as action
    output_action: PiiAction | None = None


@dataclass(frozen=True)
class RegexSpec:
    name: str  # also the mask token: {InternalAccountId}
    pattern: str
    action: PiiAction
    description: str = ""


@dataclass(frozen=True)
class GroundingSpec:
    grounding_threshold: float = 0.75  # 0..0.99; block if GROUNDING score < threshold
    relevance_threshold: float = 0.5  # 0..0.99; block if RELEVANCE score < threshold


@dataclass(frozen=True)
class GuardrailSpec:
    name: str
    description: str
    blocked_input_messaging: str
    blocked_outputs_messaging: str
    content_filters: tuple[ContentFilterSpec, ...]
    topics: tuple[TopicSpec, ...]
    words: tuple[WordSpec, ...]
    managed_word_lists: tuple[str, ...]  # PROFANITY
    pii: tuple[PiiSpec, ...]
    regexes: tuple[RegexSpec, ...]
    grounding: GroundingSpec | None
    tier: Tier = Tier.STANDARD
    guardrail_profile_id: str = ""  # required for STANDARD
    kms_key_id: str = ""
    ar_policy_arns: tuple[str, ...] = ()  # Automated Reasoning policy version ARNs (SDK only)
    ar_confidence_threshold: float = 1.0
    tags: dict[str, str] = field(default_factory=dict)


def default_spec(
    name: str,
    tier: Tier = Tier.STANDARD,
    guardrail_profile_id: str = "",
    kms_key_id: str = "",
    ar_policy_arns: tuple[str, ...] = (),
) -> GuardrailSpec:
    """The same policy set as terraform/04.01.guardrails.tf, so code and Terraform can be diffed line by line."""
    s = Strength
    return GuardrailSpec(
        name=name,
        description="1A demo guardrail: every policy type, configured as code (SDK path)",
        blocked_input_messaging="Sorry, I can't help with that request. Please rephrase or contact support.",
        blocked_outputs_messaging="Sorry, I can't share that answer. Please contact support for help.",
        content_filters=(
            ContentFilterSpec("HATE", s.HIGH, s.HIGH, input_modalities=("TEXT", "IMAGE")),
            ContentFilterSpec("INSULTS", s.MEDIUM, s.MEDIUM, input_modalities=("TEXT", "IMAGE")),
            ContentFilterSpec("SEXUAL", s.HIGH, s.HIGH, input_modalities=("TEXT", "IMAGE")),
            ContentFilterSpec("VIOLENCE", s.MEDIUM, s.HIGH, input_modalities=("TEXT", "IMAGE")),
            ContentFilterSpec("MISCONDUCT", s.HIGH, s.HIGH, input_modalities=("TEXT", "IMAGE")),
            # Input only: outputStrength must be NONE.
            ContentFilterSpec("PROMPT_ATTACK", s.HIGH, s.NONE, output_action=FilterAction.NONE, output_modalities=()),
        ),
        topics=(
            TopicSpec(
                "InvestmentAdvice",
                "Personalized recommendations about buying, selling, or allocating stocks, bonds, funds, crypto, "
                "or other financial assets.",
                (
                    "Which stocks should I buy this month?",
                    "Should I move my 401k into crypto?",
                    "Is now a good time to sell my Tesla shares?",
                ),
            ),
            TopicSpec(
                "LegalAdvice",
                "Guidance on how to handle a specific legal dispute, lawsuit, contract breach, or criminal charge.",
                ("How do I sue my landlord?", "What should I say to the police about the accident?"),
            ),
        ),
        words=(
            WordSpec("Project Nightingale", input_action=FilterAction.NONE, output_action=FilterAction.BLOCK),
            WordSpec("CompetitorCo"),
        ),
        managed_word_lists=("PROFANITY",),
        pii=(
            PiiSpec("EMAIL", PiiAction.ANONYMIZE),
            PiiSpec("PHONE", PiiAction.ANONYMIZE),
            PiiSpec("NAME", PiiAction.ANONYMIZE, input_action=PiiAction.NONE, output_action=PiiAction.ANONYMIZE),
            PiiSpec("US_SOCIAL_SECURITY_NUMBER", PiiAction.BLOCK),
            PiiSpec("CREDIT_DEBIT_CARD_NUMBER", PiiAction.BLOCK),
            PiiSpec("AWS_SECRET_KEY", PiiAction.BLOCK),
        ),
        regexes=(
            RegexSpec(
                "InternalAccountId", r"ACCT-[0-9]{8}", PiiAction.ANONYMIZE, "Internal account id, e.g. ACCT-12345678"
            ),
        ),
        grounding=GroundingSpec(grounding_threshold=0.75, relevance_threshold=0.5),
        tier=tier,
        guardrail_profile_id=guardrail_profile_id,
        kms_key_id=kms_key_id,
        ar_policy_arns=ar_policy_arns,
        tags={"Component": "04.01", "Project": "1A"},
    )


# ================================================================ verdict models


@dataclass(frozen=True)
class TextBlock:
    text: str
    qualifiers: tuple[Qualifier, ...] = ()


@dataclass(frozen=True)
class PolicyHit:
    """One finding from one policy. `match` holds the sensitive text itself: never log it."""

    policy: str  # topic | content | word | managed_word | pii | regex | automated_reasoning
    name: str  # topic name, filter type, PII type, regex name, AR finding kind
    action: str  # BLOCKED | ANONYMIZED | NONE
    detected: bool  # True also in detect mode (action NONE)
    confidence: str = ""  # content filters: NONE | LOW | MEDIUM | HIGH
    match: str = ""


@dataclass(frozen=True)
class GroundingScore:
    type: str  # GROUNDING | RELEVANCE
    score: float  # 0..1
    threshold: float
    action: str  # BLOCKED | NONE


@dataclass(frozen=True)
class GuardrailVerdict:
    intervened: bool  # action == GUARDRAIL_INTERVENED (block OR anonymize)
    blocked: bool  # at least one BLOCKED hit -> outputs = canned message
    output_text: str  # masked text, blocked message, or the original text when nothing intervened
    action_reason: str = ""
    hits: tuple[PolicyHit, ...] = ()
    grounding: tuple[GroundingScore, ...] = ()
    usage: dict[str, int] = field(default_factory=dict)  # units per policy (billing)
    guarded_chars: int = 0  # guardrailCoverage.textCharacters.guarded
    total_chars: int = 0
    latency_ms: int = 0  # invocationMetrics.guardrailProcessingLatency


@dataclass(frozen=True)
class GuardedReply:
    text: str
    stop_reason: str  # end_turn | max_tokens | guardrail_intervened | ...
    input_verdict: GuardrailVerdict | None = None
    output_verdict: GuardrailVerdict | None = None

    @property
    def intervened(self) -> bool:
        return self.stop_reason == "guardrail_intervened"


@dataclass(frozen=True)
class SmokeCase:
    """Minimal labeled case used to gate a DRAFT -> version promotion (full harness: 04.03)."""

    text: str
    source: Source
    expect_blocked: bool


# ================================================================ ports


class GuardrailPort(Protocol):
    def apply(self, blocks: list[TextBlock], source: Source) -> GuardrailVerdict: ...


class ChatModelPort(Protocol):
    def generate(self, system: str, user_text: str, context: list[str]) -> str: ...
