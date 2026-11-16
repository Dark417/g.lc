# guardrails.01why-picture Why Guardrails and the Picture

> Why a managed guardrail exists and where its checks sit around the model.

## Index

- [1. Why It Was Created](#1-why-it-was-created)
  - [1.1 The Pain Before It](#11-the-pain-before-it)
  - [1.2 What It Changes](#12-what-it-changes)
  - [1.3 Common Use Cases](#13-common-use-cases)
- [2. Picture](#2-picture)
  - [2.1 Evaluation Rules](#21-evaluation-rules)
  - [2.2 Code: Verdict Model](#22-code-verdict-model)

Back to [00index](guardrails.00index.md).

## 1. Why It Was Created

Before guardrails, every team enforced safety its own way, inside the prompt.

### 1.1 The Pain Before It

- Every team wrote its own regex lists, moderation calls, and "please don't" prompt lines
- System-prompt rules are advice to the model, not enforcement
  - a jailbreak removes them
- Policies drifted per app, per model
- No audit of what was blocked

### 1.2 What It Changes

- One resource, one id, many apps and models
- Same policy for prompts and responses
- Assessments + CloudWatch metrics = audit trail of interventions

### 1.3 Common Use Cases

- Customer chatbot
  - block investment / medical advice topics
  - mask emails and phones
- Retrieval-Augmented Generation (RAG): block answers that are not grounded in retrieved passages
- Agents: prompt-injection filter on tool results and user text
- Third-party model gateway: `ApplyGuardrail` before and after a non-Bedrock call

## 2. Picture

One guardrail version wraps the model with an input check and an output check.

```text
                         guardrail a-guardrail : version 1 (immutable)
                ┌───────────────────────────────────────────────────────────┐
 user text ───► │ INPUT  : content · prompt attack · topics · words · PII   │──► blocked? → blockedInputMessaging
                └───────────────────────────────────────────────────────────┘
                                   │ pass (PII may be masked)
                                   ▼
                              foundation model   (skipped if input blocked: no model tokens billed)
                                   │
                ┌───────────────────────────────────────────────────────────┐
 model text ──► │ OUTPUT : content · topics · words · PII · grounding ·     │──► blocked? → blockedOutputsMessaging
                │          relevance · automated reasoning                  │
                └───────────────────────────────────────────────────────────┘
                                   │ pass / anonymized
                                   ▼
                               response + trace (assessments per policy)
```

Notice that an input block skips the model entirely, so no model tokens are billed.

### 2.1 Evaluation Rules

- Evaluation order inside one check
  - all configured policies run in parallel over the content
  - order of magnitude: tens to a few hundred ms
  - check CloudWatch `InvocationLatency`
- Any one policy with action BLOCK and a hit ⇒ the whole call intervenes
- ANONYMIZE hits alone ⇒ `GUARDRAIL_INTERVENED` too
  - but the masked text is returned, not the canned message

### 2.2 Code: Verdict Model

- The app works with one parsed verdict per check
  - `intervened` covers block OR anonymize
  - `blocked` means the canned message replaced the text

```python
# app/domain/_04safety_01guardrails.py
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
class PolicyHit:
    """One finding from one policy. `match` holds the sensitive text itself: never log it."""

    policy: str  # topic | content | word | managed_word | pii | regex | automated_reasoning
    name: str  # topic name, filter type, PII type, regex name, AR finding kind
    action: str  # BLOCKED | ANONYMIZED | NONE
    detected: bool  # True also in detect mode (action NONE)
    confidence: str = ""  # content filters: NONE | LOW | MEDIUM | HIGH
    match: str = ""
```

- Catch
  - `PolicyHit.match` is the sensitive text itself
  - the Representational State Transfer (REST) adapter never echoes it; log assessments, not raw text
