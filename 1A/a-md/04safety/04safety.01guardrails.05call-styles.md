# 04safety.01guardrails.05call-styles Three Ways to Call a Guardrail

> Standalone `ApplyGuardrail`, Converse with `guardrailConfig`, and the guarded chat service built on them.

## Index

- [1. Call Styles Compared](#1-call-styles-compared)
- [2. ApplyGuardrail](#2-applyguardrail)
  - [2.1 Request](#21-request)
  - [2.2 Response](#22-response)
  - [2.3 Code: Apply and Parse](#23-code-apply-and-parse)
- [3. Converse With guardrailConfig](#3-converse-with-guardrailconfig)
  - [3.1 Response and Trace](#31-response-and-trace)
  - [3.2 Code: Guarded Converse](#32-code-guarded-converse)
- [4. Guarded Chat Service](#4-guarded-chat-service)
- [5. Inline Checks Without a Guardrail](#5-inline-checks-without-a-guardrail)

Back to [00index](04safety.01guardrails.00index.md).
Streaming variant: [06streaming](04safety.01guardrails.06streaming.md).

## 1. Call Styles Compared

The choice is who calls the model: you, or Bedrock.

| Call | When | Who calls the model | Catch |
|---|---|---|---|
| `bedrock-runtime.apply_guardrail(source=INPUT/OUTPUT, content=[…])` | any model, any text; pre-index scrubbing; agent tool results | you | two extra calls per turn; you wire the logic |
| `converse(..., guardrailConfig={...})` | Bedrock model, one call does all | Bedrock | output check sees the full answer only when not streaming |
| `converse_stream(..., guardrailConfig={..., streamProcessingMode})` | Bedrock streaming User Experience (UX) | Bedrock | sync latency vs async leakage ([06streaming](04safety.01guardrails.06streaming.md)) |

- A third path: Knowledge Base (KB) `RetrieveAndGenerate` / Agents attach the guardrail by id + version

## 2. ApplyGuardrail

Checks text without calling a model; works for Bedrock, SageMaker, or any provider.

### 2.1 Request

- `guardrailIdentifier`
- `guardrailVersion`
  - required: `"DRAFT"` or `"1"`
- `source`
  - INPUT = user side
  - OUTPUT = model side (adds grounding / Automated Reasoning (AR))
- `content[].text.text` + optional `qualifiers`
  - `grounding_source`, `query`, `guard_content`
- `content[].image`
  - `format` png/jpeg, `source.bytes`
- `outputScope`
  - `INTERVENTIONS` (default): only hits
  - `FULL`: every assessment, incl. non-hits; for debugging and eval

### 2.2 Response

- `action` (`NONE` / `GUARDRAIL_INTERVENED`), `actionReason`
- `outputs[].text` = masked text or the blocked message
  - present only when the guardrail intervened
- `assessments[]`
  - `topicPolicy`, `contentPolicy`, `wordPolicy`
  - `sensitiveInformationPolicy`, `contextualGroundingPolicy`, `automatedReasoningPolicy`
  - `invocationMetrics`
- `usage`: units per policy
  - `topicPolicyUnits`, `contentPolicyUnits`, …
  - `sensitiveInformationPolicyFreeUnits` (regex, not billed)
- `guardrailCoverage.textCharacters.guarded / total`
  - how much of the text was actually checked

### 2.3 Code: Apply and Parse

```python
# app/infra/_04safety_01guardrails.py
def apply_guardrail(
    blocks: list[TextBlock],
    source: Source,
    version: str | None = None,
    output_scope: str = "INTERVENTIONS",
    image_png: bytes | None = None,
) -> GuardrailVerdict:
    s = get_guardrails_settings()
    content = [_block_json(b) for b in blocks]
    if image_png is not None:
        # Image block: content filters with IMAGE modality; png | jpeg; raw bytes (boto3 base64-encodes).
        content.append({"image": {"format": "png", "source": {"bytes": image_png}}})
    resp = _runtime().apply_guardrail(
        guardrailIdentifier=s.guardrail_id,
        guardrailVersion=version or s.guardrail_version,  # required here: DRAFT or a number
        source=source.value,
        content=content,
        outputScope=output_scope,  # INTERVENTIONS | FULL (eval, threshold tuning)
    )
    original = "\n".join(b.text for b in blocks if Qualifier.GROUNDING_SOURCE not in b.qualifiers)
    return parse_apply_response(resp, original)


def parse_apply_response(resp: Json, original_text: str = "") -> GuardrailVerdict:
    hits, grounding, latency = [], [], 0
    for a in resp.get("assessments", []):
        h, g = _assessment_hits(a)  # same assessment shape as in the Converse trace
        hits += h
        grounding += g
        latency += int(a.get("invocationMetrics", {}).get("guardrailProcessingLatency", 0))
    intervened = resp.get("action") == INTERVENED
    outputs = [o.get("text", "") for o in resp.get("outputs", [])]  # only present when intervened
    coverage = resp.get("guardrailCoverage", {}).get("textCharacters", {})
    return GuardrailVerdict(
        intervened=intervened,
        blocked=any(h.action == "BLOCKED" for h in hits) or any(g.action == "BLOCKED" for g in grounding),
        output_text="\n".join(outputs) if intervened and outputs else original_text,
        action_reason=resp.get("actionReason", ""),
        hits=tuple(hits),
        grounding=tuple(grounding),
        usage={k: int(v) for k, v in resp.get("usage", {}).items()},
        guarded_chars=int(coverage.get("guarded", 0)),
        total_chars=int(coverage.get("total", 0)),
        latency_ms=latency,
    )
```

- Catch
  - One extra round trip per check
  - `GUARDRAIL_INTERVENED` is a business result, not an error
    - throttling is retried by the shared client config (adaptive mode)

## 3. Converse With guardrailConfig

Bedrock runs input check → model → output check in one call.

### 3.1 Response and Trace

- `stopReason = "guardrail_intervened"`
  - `output.message` holds the canned blocked message
- `trace.guardrail` (when `trace="enabled"`)
  - `inputAssessment`: map guardrail id → assessment
  - `outputAssessments`: map → list
  - `modelOutput`: raw model text, `enabled_full` only
- Limit: `modelOutput` shows the unfiltered answer
  - never log it to a widely readable sink

### 3.2 Code: Guarded Converse

```python
# app/infra/_04safety_01guardrails.py
def _guardrail_config(trace: str | None = None) -> Json:
    s = get_guardrails_settings()
    return {
        "guardrailIdentifier": s.guardrail_id,
        "guardrailVersion": s.guardrail_version,  # pin a number in prod; DRAFT changes under you
        "trace": trace or s.trace,  # disabled | enabled | enabled_full (adds raw modelOutput: don't log it)
    }


def converse_guarded(user_text: str, system: str = "You are a helpful banking assistant.") -> GuardedReply:
    resp = _runtime().converse(
        modelId=_model_id(),
        system=[{"text": system}],
        messages=[{"role": "user", "content": [{"text": user_text}]}],
        inferenceConfig={"maxTokens": 512, "temperature": 0.2},
        guardrailConfig=_guardrail_config(),
    )
    return _reply_from_converse(resp)  # stopReason + trace.guardrail -> input/output verdicts
```

- Catch
  - With no `guardContent` blocks every message (history included) is evaluated
  - templated instructions inside user turns can trip PROMPT_ATTACK
  - tag the untrusted part: [04prompt-attacks](04safety.01guardrails.04prompt-attacks.md)

## 4. Guarded Chat Service

The `ApplyGuardrail` sandwich around ANY model behind a port.

- Why not `guardrailConfig`
  - the model may be non-Bedrock
  - the app wants the masked input (ANONYMIZE) to be what the model sees and what gets logged
- Cost: two guardrail calls + one model call per turn

→ Guard input: only the user's text (untrusted).  
⇒ Blocked means no model call, no model tokens billed.  
→ Call the model with the masked input.  
→ Guard output: content/topics/words/Personally Identifiable Information (PII) always; grounding only when context exists.

```python
# app/service/_04safety_01guardrails.py
class GuardedChatService:
    def __init__(self, guard: GuardrailPort, model: ChatModelPort) -> None:
        self._guard = guard
        self._model = model

    def chat(self, user_text: str, context: list[str] | None = None) -> GuardedReply:
        context = context or []
        vin = self._guard.apply([TextBlock(user_text)], Source.INPUT)
        if vin.blocked:  # no model call, no model tokens billed
            return GuardedReply(text=vin.output_text, stop_reason="guardrail_intervened", input_verdict=vin)
        safe_input = vin.output_text  # PII masked as {EMAIL}, {PHONE}, ... when ANONYMIZE hit

        answer = self._model.generate(SYSTEM_PROMPT, safe_input, context)  # any provider behind the port

        blocks = [TextBlock(c, (Qualifier.GROUNDING_SOURCE,)) for c in context]
        if context:
            blocks.append(TextBlock(safe_input, (Qualifier.QUERY,)))
        blocks.append(TextBlock(answer, (Qualifier.GUARD_CONTENT,)))
        vout = self._guard.apply(blocks, Source.OUTPUT)
        stop = "guardrail_intervened" if vout.blocked else "end_turn"
        return GuardedReply(text=vout.output_text, stop_reason=stop, input_verdict=vin, output_verdict=vout)
```

- Catch
  - Two extra round trips per turn vs one integrated call ⇒ latency budget
  - Lets one central "safety service" own policy for many model providers
  - With streaming from a non-Bedrock model, you must build your own buffering window

## 5. Inline Checks Without a Guardrail

`InvokeGuardrailChecks` (new in botocore 1.44) runs ad-hoc checks configured in the request.

- Returns severity / confidence scores instead of a block decision
  - useful for threshold tuning and eval
- No topics, words, or grounding here

```python
# app/infra/_04safety_01guardrails.py
def invoke_guardrail_checks(text: str, role: str = "user") -> Json:
    resp = _runtime().invoke_guardrail_checks(
        messages=[{"role": role, "content": [{"text": text}]}],  # role: user | assistant | system
        checks={
            "contentFilter": {
                "categories": [{"category": c} for c in ("VIOLENCE", "HATE", "SEXUAL", "MISCONDUCT", "INSULTS")]
            },
            "promptAttack": {
                "categories": [{"category": c} for c in ("JAILBREAK", "PROMPT_INJECTION", "PROMPT_LEAKAGE")]
            },
            "sensitiveInformation": {"entities": [{"type": t} for t in ("EMAIL", "PHONE", "US_SOCIAL_SECURITY_NUMBER")]},
        },
    )
    r = resp["results"]
    return {
        "content": {x["category"]: x["severityScore"] for x in r.get("contentFilter", {}).get("results", [])},
        "prompt_attack": {x["category"]: x["severityScore"] for x in r.get("promptAttack", {}).get("results", [])},
        # pii: type, confidenceScore, begin/end offsets ...
        "usage": resp.get("usage", {}),
    }
```

- Catch
  - Newer Application Programming Interface (API): verify Region availability
  - Identity and Access Management (IAM) action name assumed `bedrock:InvokeGuardrailChecks` (verify)
