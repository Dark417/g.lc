# guardrails Guardrails

> A managed, versioned policy layer that checks text going into and out of a model.

## Index

- [1. Source and Scope](#1-source-and-scope)
- [2. One-Minute Version](#2-one-minute-version)
- [3. File Index](#3-file-index)
  - [3.1 Concept](#31-concept)
  - [3.2 Calling and Operating](#32-calling-and-operating)
  - [3.3 Decisions and Interview](#33-decisions-and-interview)
- [4. Code Map](#4-code-map)
- [5. Gaps](#5-gaps)
- [References](#references)

## 1. Source and Scope

Lectures: AIP-C01 #23–#25, #34 (slides p.54–56, 69–70).

- Scope: Python + Java + Terraform
  - x-md shows Python code only
- Terraform: `terraform/` module `04safety_01guardrails`
  - `a-guardrail` with every policy type
  - version `v1`
  - app Identity and Access Management (IAM)
- Code
  - Python: `app/*/_04safety_01guardrails.py` (slice `guardrails`)
  - Java: `com/lc/a/*/_04safety_01guardrails/` (`a.guardrails.enabled`)
- Field names
  - checked against the botocore 1.44 service model (`bedrock`, `bedrock-runtime`)
  - and the Amazon Web Services (AWS) provider 6.73 schema, 2026-11
- Numbers
  - Bedrock User Guide "Guardrails" + quota page, read 2026-11
  - unless marked "order of magnitude"

## 2. One-Minute Version

A guardrail is a policy engine on both sides of the model.

- What
  - A managed policy layer that inspects text (and images) going into and out of a model
  - One guardrail = up to six policies + blocked messages + Key Management Service (KMS) key, versioned
- Why
  - Models follow instructions, including malicious ones
  - Safety must be enforced outside the prompt
    - the same way for every model and every team
- How
  - Policies
    - content filters (incl. prompt attack)
    - denied topics
    - word filters
    - sensitive information (Personally Identifiable Information (PII) + regex)
    - contextual grounding
    - Automated Reasoning
  - Each policy runs on the input, the output, or both
  - Result per call
    - `action` = `GUARDRAIL_INTERVENED` or `NONE`
    - plus per-policy assessments
  - Intervene ⇒ block (return the canned message) or anonymize (mask PII, keep going)
  - Three call styles
    - `ApplyGuardrail`: standalone check on any text, any model, even non-Bedrock
    - `Converse` / `InvokeModel` + `guardrailConfig`: Bedrock runs input check → model → output check
    - Knowledge Base (KB) `RetrieveAndGenerate` / Agents: guardrail attached by id + version
- Catch
  - Classifiers, not proofs ⇒ false positives and false negatives
    - tune on a labeled set ([evaluations](evaluations.00index.md))
  - Prompt-attack filter is input-only
    - it scans everything unless you tag user content
  - Streaming sync mode adds latency
    - async mode can leak a chunk before the block
  - Use a numbered version in prod
    - `DRAFT` changes under you
  - Paid per 1,000-character text unit per policy
    - long Retrieval-Augmented Generation (RAG) contexts multiply cost
- 🗣 "A guardrail is a policy engine on both sides of the model, versioned like code and enforced outside the prompt."
- 🗣 "ApplyGuardrail decouples safety from the model: same policy for Bedrock, SageMaker, or OpenAI."
- 🗣 "Tag the user's text with guardContent, or the prompt-attack filter will flag your own system prompt."

## 3. File Index

Read top to bottom: concept, then calling, then decisions.

### 3.1 Concept

- [01why-picture](guardrails.01why-picture.md)
  - Why it was created, use cases
  - Picture of the input → model → output checks
- [02policies](guardrails.02policies.md)
  - The six policies table
  - Content filters, denied topics, word filters
  - Spec as code (`GuardrailSpec`, `default_spec`)
- [03sensitive-grounding](guardrails.03sensitive-grounding.md)
  - Sensitive information (PII + regex)
  - Contextual grounding
- [04prompt-attacks](guardrails.04prompt-attacks.md)
  - Attack types, defense in depth
  - `guardContent` tagging, bias vs misuse

### 3.2 Calling and Operating

- [05call-styles](guardrails.05call-styles.md)
  - `ApplyGuardrail`, Converse + `guardrailConfig`, guarded chat service
  - Request and response fields, inline checks
- [06streaming](guardrails.06streaming.md)
  - Sync vs async stream processing
- [07versions-tiers](guardrails.07versions-tiers.md)
  - DRAFT vs versions, promotion workflow
  - Tiers, detect mode, account enforcement
- [08automated-reasoning](guardrails.08automated-reasoning.md)
  - Automated Reasoning checks and findings

### 3.3 Decisions and Interview

- [98tradeoffs](guardrails.98tradeoffs.md)
  - When to use / not, knobs, best practices
  - Comparison, failure modes
- [99interview](guardrails.99interview.md)
  - Level 4 (L4) + Level 5 (L5) questions, L5-only design questions

## 4. Code Map

Python paths follow the layer-first layout; the Java column lists the Java adapter where one exists.

| Scenario | Concept file | Python | Java |
|---|---|---|---|
| Policy builders | 02, 03, 08 | `app/infra/_04safety_01guardrails.py` `content_policy`, `topic_policy`, `word_policy`, `sensitive_information_policy`, `contextual_grounding_policy`, `automated_reasoning_policy`, `cross_region_config` | — |
| Create guardrail (config as code) | 02 | `infra` `create_guardrail` | — |
| Update DRAFT | 07 | `infra` `update_guardrail` | — |
| Snapshot a version | 07 | `infra` `create_guardrail_version` | — |
| Wait for READY | 07 | `infra` `wait_until_ready` | — |
| Read / list with pagination | 07 | `infra` `get_guardrail`, `list_guardrails`, `list_versions` | — |

| Scenario | Concept file | Python | Java |
|---|---|---|---|
| Standalone check | 05 | `infra` `apply_guardrail` → `domain` `GuardrailVerdict` | `com/lc/a/infra/_04safety_01guardrails/GuardrailClient.java` `apply` |
| Parse assessments | 05 | `infra` `parse_apply_response` | `GuardrailClient.toVerdict` |
| Grounding check of a RAG answer | 03 | `infra` `check_grounding` | `GuardrailClient.checkGrounding` |
| Converse + guardrailConfig + trace | 05 | `infra` `converse_guarded` | `GuardrailClient.converseGuarded` |
| guardContent: guard only user text | 04 | `infra` `converse_guard_user_text_only` | `GuardrailClient.converseGuarded` (guardContent block) |
| Stream sync vs async | 06 | `infra` `converse_stream_guarded` | — |

| Scenario | Concept file | Python | Java |
|---|---|---|---|
| Inline checks without a guardrail | 05 | `infra` `invoke_guardrail_checks` | — |
| DRAFT → version workflow | 07 | `app/service/_04safety_01guardrails.py` `promote_draft` | — |
| Guard input → model → guard output | 05 | `service` `GuardedChatService.chat` | `service/_04safety_01guardrails/GuardedChatService.chat` |
| Representational State Transfer (REST) | — | `app/api/_04safety_01guardrails.py` (`/guardrails/...`) | `api/_04safety_01guardrails/GuardrailController` (`/guardrails/...`) |

## 5. Gaps

Known gaps between this doc and the code.

- Automated Reasoning policy build workflow (create policy, build, tests)
  - Software Development Kit (SDK) operations listed in [08automated-reasoning](guardrails.08automated-reasoning.md), not coded
- Account/org enforced guardrails (`PutEnforcedGuardrailConfiguration`): doc only
- Cross-account guardrail resource policy (`aws_bedrock_guardrail_resource_policy`): doc only
- Image content filtering
  - request shape shown in `apply_guardrail` (image block), not exercised
- `InvokeModel` input tags (`amazon-bedrock-guardrails-guardContent_<suffix>`): doc only
- `InvokeGuardrailChecks` is new in botocore 1.44
  - IAM action name assumed `bedrock:InvokeGuardrailChecks` (verify)

## References

- [aws-samples/amazon-bedrock-samples — responsible_ai / guardrails notebooks](https://github.com/aws-samples/amazon-bedrock-samples/tree/main/responsible_ai)
- [Bedrock User Guide — Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)
- [Bedrock User Guide — ApplyGuardrail Application Programming Interface (API)](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-use-independent-api.html)
- [Bedrock User Guide — Automated Reasoning checks](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-automated-reasoning-checks.html)
- [AWS Machine Learning (ML) Blog — Guardrails ApplyGuardrail for any model](https://aws.amazon.com/blogs/machine-learning/implement-model-independent-safety-measures-with-amazon-bedrock-guardrails/)
