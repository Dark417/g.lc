# 04safety.02pii-redaction.07pipeline Comprehend + Lambda + Bedrock Pipeline

> The lecture-51 pipeline: pseudonymize the prompt, call the model, guard the output, detokenize for the authorized caller.

## Index

- [1. Flow](#1-flow)
- [2. Design Notes](#2-design-notes)
- [3. Code: Pipeline Service](#3-code-pipeline-service)
- [4. Code: Output Guardrail Net](#4-code-output-guardrail-net)

Back to [00index](04safety.02pii-redaction.00index.md).

## 1. Flow

A contains-check gates the common no-PII path; the output guardrail is the final net.

```text
API Gateway ─► Lambda ─► comprehend.contains_pii_entities ──(none)──────────────┐
                           │ (some)                                            │
                           └─► detect_pii_entities ─► policy ─► pseudonymize ──┤
                                                                               ▼
                                                                  bedrock.converse
                                                                               │
                                       guardrail apply_guardrail(OUTPUT) ◄─────┘
                                               │
                                     detokenize (if authorized) ─► response
```

Notice that detokenize is the last step and only runs for authorized callers.

## 2. Design Notes

- Lambda holds only the redaction logic
  - the vault and the model are behind Identity and Access Management (IAM)
- Contains-first saves detect calls on the common no-PII path
- Order of magnitude latency added
  - tens to low hundreds of ms per Comprehend call; measure
- The model and invocation logs never see raw values
- The system prompt tells the model to copy placeholders verbatim

## 3. Code: Pipeline Service

→ Comprehend redact (pseudonymize EMAIL/PHONE/NAME, block Social Security Number (SSN)/card).  
→ Bedrock Converse on the pseudonymized prompt.  
→ `ApplyGuardrail(OUTPUT)` on the answer (catches Personally Identifiable Information (PII) the model produced itself).  
→ Detokenize for the authorized caller.

```python
# app/service/_04safety_02pii_redaction.py
SYSTEM = (
    "You are a support assistant. Placeholders like <<EMAIL_ab12cd34>> stand for real customer data: "
    "copy them verbatim when you need them and never guess what they contain."
)


def redact_converse_guard(
    user_text: str, policy: RedactionPolicy, vault: PseudonymVault, reidentify: bool = True
) -> PipelineResult:
    """reidentify=False for callers not allowed raw values."""
    red = infra.redact(user_text, policy, vault)
    if red.blocked:
        reason = f"input contains {', '.join(red.blocked_types)}"
        return PipelineResult("Please don't share that kind of data here.", True, reason, {}, {}, "")

    answer = infra.converse_text(SYSTEM, red.text)  # plain Converse, no guardrailConfig
    blocked, guarded, out_counts = infra.guard_output(answer)
    if blocked:
        return PipelineResult(guarded, True, "output guardrail", red.summary(), out_counts, red.text)

    final = detokenize_text(guarded, vault) if reidentify else guarded
    # model_prompt = red.text: exactly what the model saw (pseudonymized), safe to log
    return PipelineResult(final, False, "", red.summary(), out_counts, red.text)
```

## 4. Code: Output Guardrail Net

- Calls `ApplyGuardrail` directly
  - the slice does not import the guardrails package
  - both point at the same Terraform output `guardrail_id`
- ANONYMIZE hits come back masked as `{EMAIL}`

```python
# app/infra/_04safety_02pii_redaction.py
def guard_output(text: str) -> tuple[bool, str, dict[str, int]]:
    s = get_pii_settings()
    resp = _runtime().apply_guardrail(
        guardrailIdentifier=s.guardrail_id,
        guardrailVersion=s.guardrail_version,
        source="OUTPUT",
        content=[{"text": {"text": text}}],
    )
    counts: dict[str, int] = {}
    blocked = False
    for a in resp.get("assessments", []):
        sens = a.get("sensitiveInformationPolicy", {})
        for hit in sens.get("piiEntities", []) + sens.get("regexes", []):
            key = hit.get("type") or hit.get("name", "REGEX")
            counts[key] = counts.get(key, 0) + 1  # types + counts only, never the match
            blocked = blocked or hit["action"] == "BLOCKED"
        for f in a.get("contentPolicy", {}).get("filters", []) + a.get("topicPolicy", {}).get("topics", []):
            blocked = blocked or f["action"] == "BLOCKED"
    if resp["action"] == "GUARDRAIL_INTERVENED" and resp.get("outputs"):
        text = "".join(o.get("text", "") for o in resp["outputs"])
    return blocked, text, counts
```

- Catch
  - `ResourceNotFoundException` ⇒ set `A_PII_GUARDRAIL_ID` to the Terraform output `guardrail_id`
