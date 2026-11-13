"""Use case: the lecture-51 pipeline (Comprehend -> Bedrock -> Guardrail), with reversible pseudonyms.

user text
  -> Comprehend redact (pseudonymize EMAIL/PHONE/NAME, block SSN/card)
  -> Bedrock Converse on the pseudonymized prompt (model + invocation logs never see raw values)
  -> ApplyGuardrail(OUTPUT) on the answer (catches PII the model produced itself)
  -> detokenize for the authorized caller
"""

from dataclasses import dataclass

from app.a04_02_pii_redaction import infra
from app.a04_02_pii_redaction.domain import PseudonymVault, RedactionPolicy, detokenize_text

SYSTEM = (
    "You are a support assistant. Placeholders like <<EMAIL_ab12cd34>> stand for real customer data: "
    "copy them verbatim when you need them and never guess what they contain."
)


@dataclass(frozen=True)
class PipelineResult:
    answer: str
    blocked: bool
    blocked_reason: str
    input_pii: dict[str, int]  # types + counts redacted from the prompt
    output_pii: dict[str, int]  # types + counts the output guardrail found
    model_prompt: str  # exactly what the model saw (pseudonymized): safe to log


def redact_converse_guard(
    user_text: str, policy: RedactionPolicy, vault: PseudonymVault, reidentify: bool = True
) -> PipelineResult:
    """Pseudonymize -> model -> output guardrail -> detokenize. reidentify=False for callers not allowed raw values."""
    red = infra.redact(user_text, policy, vault)
    if red.blocked:
        reason = f"input contains {', '.join(red.blocked_types)}"
        return PipelineResult("Please don't share that kind of data here.", True, reason, {}, {}, "")

    answer = infra.converse_text(SYSTEM, red.text)
    blocked, guarded, out_counts = infra.guard_output(answer)
    if blocked:
        return PipelineResult(guarded, True, "output guardrail", red.summary(), out_counts, red.text)

    final = detokenize_text(guarded, vault) if reidentify else guarded
    return PipelineResult(final, False, "", red.summary(), out_counts, red.text)
