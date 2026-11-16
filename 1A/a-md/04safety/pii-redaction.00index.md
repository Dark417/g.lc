# pii-redaction Personally Identifiable Information (PII) Detection and Redaction

> Find personal data in text and remove or replace it before it reaches a model, an index, a log, or the wrong user.

## Index

- [1. Source and Scope](#1-source-and-scope)
- [2. One-Minute Version](#2-one-minute-version)
- [3. File Index](#3-file-index)
  - [3.1 Concept](#31-concept)
  - [3.2 Mechanics](#32-mechanics)
  - [3.3 Decisions and Interview](#33-decisions-and-interview)
- [4. Code Map](#4-code-map)
- [5. Gaps](#5-gaps)
- [References](#references)

## 1. Source and Scope

Lectures: AIP-C01 #26, #49–#51 (slides p.57, 114–118).

- Tie-ins
  - #47 Transcribe (p.111–113)
  - #52 Comprehend Medical (p.119)
  - #210 data masking
  - #225 Macie (mention only)
- Scope: Python + Terraform
  - no Java: the backend path uses Guardrails ([guardrails](guardrails.00index.md))
  - Comprehend Personally Identifiable Information (PII) (sync + async job): Python
  - Guardrails sensitive-information filters: summarized here, coded in guardrails
  - Transcribe redaction, Comprehend Medical, Macie: doc only
    - Transcribe code lives in transcribe
- Terraform: `terraform/` module `04safety_02pii_redaction`
  - Comprehend data-access role `a-comprehend-pii`
  - app policy
- Code: Python `app/*/_04safety_02pii_redaction.py` (slice `pii`)
- Field names
  - checked against the botocore 1.44 service model (`comprehend`, `bedrock-runtime`), 2026-11
- Numbers
  - Comprehend Developer Guide + pricing page, read 2026-11
  - unless marked "order of magnitude"

## 2. One-Minute Version

Detect gives offsets; a policy decides the action; edits apply right-to-left.

- What
  - Find personal data (names, emails, Social Security Numbers (SSNs), card numbers, keys) in text and remove or replace it
  - Before it reaches a model, an index, a log, or a user who should not see it
- Why
  - Prompts, Retrieval-Augmented Generation (RAG) indexes, and invocation logs are new copies of customer data
  - Each copy widens the General Data Protection Regulation (GDPR) / Health Insurance Portability and Accountability Act (HIPAA) / Payment Card Industry (PCI) scope and the breach blast radius
- How
  - Detect: a Machine Learning (ML) detector returns entity type + character offsets + confidence score
  - Decide per type
    - mask (`*****`)
    - replace with type (`[EMAIL]`)
    - pseudonymize (`<<EMAIL_1a2b>>`)
    - block
    - keep
  - Apply edits right-to-left so earlier offsets stay valid
  - Tools by place
    - Data at rest in Simple Storage Service (S3) → Macie (discover) + Comprehend async job (redacted copy)
    - Request / response path → Comprehend `DetectPiiEntities` or Guardrails sensitive-info filter
    - Audio → Transcribe `ContentRedaction`
    - Clinical text → Comprehend Medical `DetectPHI`
- Catch
  - Detectors miss and over-fire
    - set a confidence threshold per type and measure it
  - Streaming splits an entity across chunks
    - hold back a tail buffer before emitting
  - Masking is irreversible
    - use a vault-backed pseudonym when the answer must contain the real value
  - The redaction service itself sees the raw PII
    - it belongs inside your compliance boundary
- 🗣 "Redact at every boundary where data gets copied: ingest, prompt, log, response."
- 🗣 "Detection gives offsets; policy decides the action; apply right-to-left."
- 🗣 "Masking forgets, pseudonymization remembers: pick by whether anyone must ever get the value back."

## 3. File Index

Read top to bottom: where PII lives, then the tools, then the mechanics.

### 3.1 Concept

- [01why-picture](pii-redaction.01why-picture.md)
  - Why managed detectors exist, use cases
  - Picture: where PII is handled
- [02toolbox](pii-redaction.02toolbox.md)
  - Comprehend, Guardrails, Transcribe, Comprehend Medical, Macie

### 3.2 Mechanics

- [comprehend-apis](pii-redaction.03comprehend-apis.md)
  - `DetectPiiEntities`, `ContainsPiiEntities`, async job, pricing shape
- [04redaction-rules](pii-redaction.04redaction-rules.md)
  - Policy object, right-to-left apply, thresholds
- [05streaming](pii-redaction.05streaming.md)
  - Token-level redaction, hold-back window
- [06pseudonymization](pii-redaction.06pseudonymization.md)
  - Masking vs reversible tokenization, salted Hash-Based Message Authentication Code (HMAC), vault
- [07pipeline](pii-redaction.07pipeline.md)
  - Comprehend + Lambda + Bedrock pipeline (lecture 51)

### 3.3 Decisions and Interview

- [98tradeoffs](pii-redaction.98tradeoffs.md)
  - When to use / not, knobs, best practices, comparison, failure modes
- [99interview](pii-redaction.99interview.md)
  - Level 4 (L4) + Level 5 (L5) questions, L5-only design questions

## 4. Code Map

Python only; the layer-first paths below replace the old slice package.

| Scenario | Concept file | Python |
|---|---|---|
| Redaction rules as code | 04 | `app/domain/_04safety_02pii_redaction.py` `RedactionPolicy`, `default_policy` |
| Detect entities (sync, chunked) | 03 | `app/infra/_04safety_02pii_redaction.py` `detect_pii` |
| Cheap pre-check | 03 | `infra` `contains_pii` |
| Apply right-to-left, overlaps, thresholds, BLOCK | 04 | `domain` `redact_text` |
| Detect + apply in one call | 04 | `infra` `redact` |
| Async batch job with `RedactionConfig` | 03 | `infra` `start_redaction_job` |

| Scenario | Concept file | Python |
|---|---|---|
| Poll the job with backoff | 03 | `infra` `describe_job`, `wait_for_job` |
| Reversible pseudonyms (salted HMAC + vault port) | 06 | `domain` `PseudonymVault`, `infra` `InMemoryPseudonymVault` |
| Streaming redactor (tail buffer) | 05 | `infra` `StreamingRedactor` |
| Pipeline: redact → Bedrock → guardrail → detokenize | 07 | `app/service/_04safety_02pii_redaction.py` `redact_converse_guard` |
| Representational State Transfer (REST) | — | `app/api/_04safety_02pii_redaction.py` (`/pii/...`) |

## 5. Gaps

Known gaps between this doc and the code.

- Transcribe `ContentRedaction`: doc only here (coded in transcribe)
- Comprehend Medical `DetectPHI`: doc only (same apply logic as `redact_text`)
- Macie discovery jobs: doc only
- DynamoDB/Key Management Service (KMS) vault adapter: port + in-memory adapter only
- Language detection before PII detection (`DetectDominantLanguage`): mentioned, not coded

## References

- [aws-samples/amazon-comprehend-examples](https://github.com/aws-samples/amazon-comprehend-examples)
- [Comprehend Developer Guide — PII detection](https://docs.aws.amazon.com/comprehend/latest/dg/pii.html)
- [Transcribe Developer Guide — Redacting PII](https://docs.aws.amazon.com/transcribe/latest/dg/pii-redaction.html)
- [Bedrock User Guide — Guardrails sensitive information filters](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-sensitive-filters.html)
- [Microsoft Presidio](https://github.com/microsoft/presidio)
