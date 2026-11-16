# pii-redaction.98tradeoffs Personally Identifiable Information (PII) Redaction Trade-offs

> Which Personally Identifiable Information (PII) tool to use when, the knobs, best practices, comparison, and failure modes.

## Index

- [1. When to Use / Not](#1-when-to-use--not)
- [2. Knobs](#2-knobs)
- [3. Best Practices](#3-best-practices)
- [4. Comparison](#4-comparison)
- [5. Failure Modes](#5-failure-modes)

Back to [00index](pii-redaction.00index.md).

## 1. When to Use / Not

Comprehend for custom policy, Guardrails when already on a guarded Bedrock call, jobs for corpora.

- Use Comprehend-based redaction when
  - You need per-type actions, thresholds, or reversible pseudonyms
  - Scrubbing documents before indexing or fine-tuning
  - The model is not on Bedrock and you want PII out before it leaves your boundary
- Use Guardrails sensitive-info when
  - The call is already a Bedrock call with a guardrail
  - one call covers PII + content + topics
- Use the async job when
  - Thousands of documents in Simple Storage Service (S3)
  - latency is irrelevant
  - one mask mode is acceptable
- Do not use
  - As the only control for regulated data
    - add access control, encryption, retention
  - For structured columns (Database (DB) fields named `email`)
    - column-level masking / Lake Formation is exact and cheaper
  - For languages the detector does not support
    - results look clean and are not

## 2. Knobs

| Knob | Values (default) | Trade-off | Change when |
|---|---|---|---|
| `min_score` | 0–1 (code default 0.8) | low = more masking, more False Positive (FP) | misses found in audits (lower) / answers degraded (raise) |
| Action per type | MASK / REPLACE / PSEUDONYMIZE / BLOCK / KEEP | reversible vs not | answer must contain the value → PSEUDONYMIZE |
| `MaskMode` (job) | MASK / REPLACE_WITH_PII_ENTITY_TYPE | REPLACE keeps meaning for Retrieval-Augmented Generation (RAG) | indexing for retrieval → REPLACE |
| `MaskCharacter` (job) | one char (`*`) | none | User Interface (UI) conventions |
| `Mode` (job) | ONLY_REDACTION / ONLY_OFFSETS | OFFSETS = your own policy | per-type actions needed |

| Knob | Values (default) | Trade-off | Change when |
|---|---|---|---|
| `InputFormat` (job) | ONE_DOC_PER_FILE / ONE_DOC_PER_LINE | per-line = JavaScript Object Notation Lines (JSONL) records | ticket exports |
| Stream window | chars held back (code: 64) | latency vs split-entity leaks | long entities (International Bank Account Number (IBAN), addresses) → larger |
| Contains pre-check | on / off | extra call when PII present | PII rate > ~50% → skip the pre-check (order of magnitude) |
| Hash-Based Message Authentication Code (HMAC) key | secret, rotated | rotation breaks joins | key exposure, policy cycle |

```python
# app/config/_04safety_02pii_redaction.py
class PiiSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_PII_", env_file=".env", extra="ignore")

    language_code: str = "en"  # PII detection: en | es (check the docs for current languages)
    min_score: float = 0.8  # default confidence threshold; per-type overrides live in RedactionPolicy
    data_access_role_arn: str = "arn:aws:iam::ACCOUNT_ID:role/a-comprehend-pii"  # output comprehend_pii_role_arn
    kms_key_id: str = "alias/a-data"  # encrypts job output (OutputDataConfig.KmsKeyId)
    guardrail_id: str = "GUARDRAIL_ID"  # terraform output guardrail_id (guardrails)
    hmac_key: str = ""  # empty = random per process (tokens not stable across restarts)
    stream_window: int = 64  # chars held back by the streaming redactor
```

## 3. Best Practices

Each rule names the failure it prevents.

- Redact before indexing, not only at query time
  - prevents the vector store from becoming a PII store
- Log entity types and counts, never matched values
  - prevents logs from re-creating the leak
- Keep thresholds per type
  - prevents one global number from either leaking Social Security Numbers (SSNs) or mangling names
- Use REPLACE (type tags) for model input
  - keeps grammar so answers stay coherent
- Keep the HMAC key in Key Management Service (KMS) / Secrets Manager
  - prevents dictionary reversal of pseudonyms
- Re-check the output with a guardrail
  - catches PII the model introduced itself
- Evaluate on a labeled set with your own data ([evaluations](evaluations.00index.md))
  - prevents trusting vendor-average recall

## 4. Comparison

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| Comprehend PII (sync) | Machine Learning (ML) Named Entity Recognition (NER) Application Programming Interface (API) with offsets | Offsets + scores ⇒ any policy; no hosting | Per-call cost and latency; limited languages | Request path with custom rules or pseudonyms |
| Comprehend PII job | Async S3 batch | Cheap at scale, writes redacted copies | One mask mode; minutes of latency | Pre-index scrubbing of S3 corpora |
| Bedrock Guardrails sensitive info | Policy inside guardrail | One call with other safety checks; regex | `{TYPE}` mask only, no thresholds, Bedrock path | Already guarding Bedrock calls |
| Transcribe redaction | Automatic Speech Recognition (ASR) with PII redaction | Redacts in the transcript directly | Audio only, language subset | Call-center audio |

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| Comprehend Medical DetectPHI | Clinical NER | Protected Health Information (PHI) categories clinical notes need | Medical text only; detection only | Healthcare text |
| Macie | S3 discovery | Finds where PII lives at scale | No inline redaction | Inventory and compliance of buckets |
| Microsoft Presidio (open source) | Regex + NER framework | Self-hosted, extensible, anonymizers incl. encrypt | You host and tune it | Multi-cloud, on-prem, custom recognizers |
| Regex only | Pattern list | Free, exact for formats | Misses names/addresses | Format-bound ids (account numbers) |

- Default
  - Comprehend `DetectPiiEntities` + policy object on the request path
  - Comprehend async job for corpora
  - Guardrails ANONYMIZE as the output net
  - unless the call is already a Bedrock call with a guardrail and masking with `{TYPE}` is enough
    - Guardrails alone
- Deciding variable
  - does anyone need the original value back (pseudonymize)
  - do you need per-type thresholds

Pick: Comprehend + policy object, unless a guarded Bedrock call with `{TYPE}` masking is enough.

## 5. Failure Modes

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Entity split across stream chunks | per-chunk detection | PII in transcripts of streamed answers | hold-back window; sync guardrail mode |
| Garbled text after redaction | left-to-right apply shifts offsets | wrong characters masked in tests | apply right-to-left; resolve overlaps |
| Over-masking | low threshold; "May", "Jordan" as names | answer quality drops; FP audit | per-type thresholds; KEEP list |
| Missed PII | high threshold; unsupported language; Optical Character Recognition (OCR) noise | sampled audits, canary strings | lower threshold; language detection first; regex backstop |
| Pseudonyms reversed | unsalted hash of low-entropy ids | security review | keyed HMAC, key in KMS |

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Vault leak | broad detokenize rights | CloudTrail on vault access | separate role, audit, rate limits |
| Redacted copy still has PII in metadata | job redacts content, not file names / S3 tags | Macie on output prefix | scrub metadata separately |
| Job fails AccessDenied | role trust or KMS grant missing | job `Message` field | trust `comprehend.amazonaws.com`, KMS grant |
| Long doc rejected | over the sync text cap | `TextSizeLimitExceededException` | chunk + offset shift, or async job |
| Logs hold raw prompts | invocation logging on before redaction | grep logs for canaries | redact before the model call |
