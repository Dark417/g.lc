# 04safety.01guardrails.98tradeoffs Guardrails Trade-offs

> When to use guardrails, which knobs to turn, how they compare, and how they fail.

## Index

- [1. When to Use / Not](#1-when-to-use--not)
- [2. Knobs](#2-knobs)
- [3. Best Practices](#3-best-practices)
- [4. Comparison](#4-comparison)
- [5. Failure Modes](#5-failure-modes)

Back to [00index](04safety.01guardrails.00index.md).

## 1. When to Use / Not

Guardrails fit any generation path; they do not replace authorization or data-at-rest scanning.

- Use
  - Any user-facing generation: chat, summarization, Retrieval-Augmented Generation (RAG) answers
  - Untrusted input reaching an agent: user text, web pages, tool results
  - A compliance rule must hold for every model and team
  - Non-Bedrock models that need the same policy (`ApplyGuardrail`)
- Do not use (alone)
  - Authorization
    - "may this user see document X" is Identity and Access Management (IAM) / Knowledge Base (KB) metadata filters, not a guardrail
  - Bulk Personally Identifiable Information (PII) discovery in data at rest
    - Macie / Comprehend jobs ([04safety.02pii-redaction](04safety.02pii-redaction.00index.md))
  - Fact checking against world knowledge
    - grounding only checks against the source you pass
  - Hard real-time paths where hundreds of ms per call are unacceptable
    - async stream mode or a smaller policy set

## 2. Knobs

Each knob trades recall against false positives, latency, or cost.

| Knob | Values (default) | Trade-off | Change when |
|---|---|---|---|
| Content strength | NONE/LOW/MEDIUM/HIGH | higher = more recall, more false positives | eval shows misses (raise) or False Positive (FP) rate > target (lower) |
| PROMPT_ATTACK input | HIGH typical | FP on role-play / dev instructions | tag user input before raising |
| Content `inputAction`/`outputAction` | BLOCK (default) / NONE | NONE = detect only | shadow-testing a new policy |
| Denied topic definition | ≤ 200 chars Classic (check) | vague = over-blocking | FP on adjacent topics |
| PII action | BLOCK / ANONYMIZE / NONE | BLOCK = refuse; ANONYMIZE = keep flow | identifiers that must never pass (Social Security Number (SSN), card) → BLOCK |
| Regex | pattern + action | catastrophic backtracking, FP on look-alikes | internal ids not in the built-in list |

| Knob | Values (default) | Trade-off | Change when |
|---|---|---|---|
| Grounding threshold | 0–0.99 | higher = stricter, more refusals | RAG answers hallucinate (raise) |
| Relevance threshold | 0–0.99 | higher = blocks partial answers | off-topic answers |
| Tier | CLASSIC / STANDARD | STANDARD = better, cross-Region | non-English or obfuscated attacks |
| Stream mode | sync / async | latency vs leakage | Time To First Token (TTFT) critical, low risk |
| Trace | disabled / enabled / enabled_full | full = raw model output in response | debugging only |
| `outputScope` | INTERVENTIONS / FULL | FULL = bigger response | evaluation, score tuning |
| Key Management Service (KMS) key | AWS-owned / Customer Managed Key (CMK) | CMK = control + cost | regulated data |

- The repo's knobs live in slice settings (env prefix `A_GUARDRAILS_`)

```python
# app/config/_04safety_01guardrails.py
class GuardrailsSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_GUARDRAILS_", env_file=".env", extra="ignore")

    guardrail_id: str = "GUARDRAIL_ID"  # terraform output guardrail_id (id or full ARN both work)
    guardrail_version: str = "1"  # terraform output guardrail_version; "DRAFT" only for testing
    sdk_guardrail_name: str = "a-guardrail-sdk"  # config-as-code scenario never fights Terraform
    kms_key_id: str = "alias/a-data"  # base_kms CMK; key id, ARN, or alias
    tier: str = "STANDARD"  # CLASSIC | STANDARD (STANDARD needs guardrail_profile_id)
    guardrail_profile_id: str = "us.guardrail.v1:0"  # system cross-Region guardrail profile (us/eu/apac prefix)
    trace: str = "enabled"  # disabled | enabled | enabled_full (full = raw model output in the response)
    stream_mode: str = "sync"  # sync | async
```

## 3. Best Practices

Each rule names the failure it prevents.

- Pin a numbered version in prod
  - prevents a DRAFT edit from changing live behavior
- Tag only untrusted text with `guardContent`
  - prevents prompt-attack FP on system prompts
- Guard input before retrieval, not only before generation
  - prevents paying for retrieval + tokens on blocked requests
- Shadow new policies in detect mode
  - prevents a launch-day FP storm
- Keep a labeled eval set per policy ([04safety.03evaluations](04safety.03evaluations.00index.md))
  - prevents tuning by anecdote
- Write blocked messages that tell the user what to do
  - prevents silent failure User Experience (UX)
- Alarm on `InvocationsIntervened` rate (CloudWatch `AWS/Bedrock/Guardrails`)
  - detects attacks and regressions
- Log assessments, not raw text
  - prevents the audit log becoming a PII store
- Terraform and Software Development Kit (SDK) show the same policy
  - Terraform owns the resource
  - SDK create/update is for tooling and tests, not a second source of truth

## 4. Comparison

Bedrock Guardrails is the managed default on Amazon Web Services (AWS); open-source options win off AWS or for dialog logic.

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| Bedrock Guardrails | Managed policy engine, 6 policies, versioned | One resource for all models; PII + grounding + Automated Reasoning (AR) built in; no infra | AWS-only; per-text-unit cost; limited custom logic | AWS stack, managed default |
| NVIDIA NeMo Guardrails | Open-source dialog rails (Colang flows) | Programmable conversation flows; self-hosted | You run it; LLM-based rails add latency | Complex dialog policies, multi-cloud |
| Guardrails AI (open source) | Validators on Large Language Model (LLM) output (schema, PII, toxicity) | Rich validator hub; structured output repair | Mostly output-side; you host models | Output schema validation + custom checks |
| Llama Guard / ShieldGemma | Open safety classifier models | Self-hosted, tunable taxonomy | You serve and evaluate it; no PII/grounding | Data must stay in your Virtual Private Cloud (VPC), custom taxonomy |
| Azure AI Content Safety / OpenAI Moderation | Cloud moderation Application Programming Interfaces (APIs) | Simple, cheap per call | Content categories only; other cloud | Already on that cloud |
| System prompt rules | "Never discuss X" in the prompt | Free | Not enforcement; jailbreakable | Never as the only layer |

- Default: Bedrock Guardrails
  - via `guardrailConfig`, or `ApplyGuardrail` for non-Bedrock models
  - unless policies must run outside AWS or need dialog-flow logic
    - NeMo Guardrails or a self-hosted classifier
- Deciding variable
  - where the model runs
  - whether you can accept the per-unit cost on long contexts

Pick: Bedrock Guardrails, unless the model runs outside AWS or needs dialog-flow rails.

## 5. Failure Modes

Most failures are configuration scope: what gets evaluated, and which version runs.

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| System prompt flagged as attack | PROMPT_ATTACK evaluates untagged system text | high `InvocationsIntervened`, contentPolicy PROMPT_ATTACK on benign traffic | tag user input with `guardContent` |
| Over-blocking a topic | vague definition, broad examples | FP rate on labeled set; user complaints | sharpen definition; add negative eval cases; detect mode |
| PII leaks in stream | async mode with ANONYMIZE | output logs contain PII | sync mode for PII policies |
| Grounding blocks good answers | threshold too high; source truncated | GROUNDING scores just below threshold | lower threshold; shorter, better passages |
| Grounding not applied | missing `grounding_source` / `query` qualifiers | `contextualGroundingPolicy` absent from assessment | pass all three qualifiers |

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Prod behavior changes silently | app points at DRAFT | version in trace = DRAFT | pin a number |
| Cost spike | long RAG context through every policy | `usage` units; Bedrock bill | guard only user text + answer; drop unneeded policies |
| Throttling | guardrail TPS quota | `ThrottlingException` | retries with jitter; quota increase |
| Regex backtracking / FP | greedy pattern | latency, false hits | anchor patterns, test on corpus |
| Raw output in logs | `trace=enabled_full` in prod | `modelOutput` in logs | `enabled` in prod |
