# 04safety.02pii-redaction.02toolbox The Personally Identifiable Information (PII) Toolbox

> Which Amazon Web Services (AWS) tool handles Personally Identifiable Information (PII) at which place, and how Guardrails differs from Comprehend.

## Index

- [1. Tools by Place](#1-tools-by-place)
- [2. Guardrails vs Comprehend on the Request Path](#2-guardrails-vs-comprehend-on-the-request-path)
- [3. Transcribe Redaction](#3-transcribe-redaction)
- [4. Comprehend Medical](#4-comprehend-medical)
- [5. Macie](#5-macie)

Back to [00index](04safety.02pii-redaction.00index.md).

## 1. Tools by Place

Each tool fits one place in the data flow.

| Tool | Where | Input | Output | Actions |
|---|---|---|---|---|
| Comprehend `DetectPiiEntities` | request path | text (sync, size-capped) | type, score, begin/end offsets | you apply |
| Comprehend `ContainsPiiEntities` | request path pre-check | text | labels (types + score), no offsets | yes/no gate |
| Comprehend `StartPiiEntitiesDetectionJob` | batch, Simple Storage Service (S3) | files or one-doc-per-line | redacted copy or offsets JavaScript Object Notation (JSON) | MASK / REPLACE_WITH_PII_ENTITY_TYPE |
| Bedrock Guardrails sensitive info | model call path | prompt / answer | masked text or block | BLOCK / ANONYMIZE / NONE + regex |

| Tool | Where | Input | Output | Actions |
|---|---|---|---|---|
| Transcribe `ContentRedaction` | audio → text | audio job / stream | `[PII]` in transcript | redacted or redacted_and_unredacted |
| Comprehend Medical `DetectPHI` | clinical text | text | Protected Health Information (PHI) entities + offsets | you apply |
| Amazon Macie | S3 at rest | buckets | findings (EventBridge, Security Hub) | discover only, no inline redaction |

## 2. Guardrails vs Comprehend on the Request Path

Guardrails bundles PII with other safety checks; Comprehend gives you the raw offsets.

- Guardrails
  - one call also does content/topic checks
  - masks with `{TYPE}`
  - no per-type confidence threshold exposed as a knob
  - coded in [04safety.01guardrails.03sensitive-grounding](04safety.01guardrails.03sensitive-grounding.md)
- Comprehend
  - offsets + scores
  - your own policy: thresholds, pseudonyms, per-type actions

## 3. Transcribe Redaction

Lecture 47; coded in 03data.03transcribe.

- Batch
  - `ContentRedaction = {RedactionType: "PII", RedactionOutput: "redacted" | "redacted_and_unredacted", PiiEntityTypes: [...]}`
- `redacted_and_unredacted` writes both transcripts
  - the unredacted one needs its own access control
- Streaming
  - `ContentRedactionType=PII`: redact
  - `ContentIdentificationType=PII`: label only
- Language support is a subset (check the docs)

```python
# illustrative: Transcribe batch job with PII redaction (real code lives in 03data.03transcribe)
transcribe.start_transcription_job(
    TranscriptionJobName=name,
    Media={"MediaFileUri": audio_s3_uri},
    LanguageCode="en-US",
    ContentRedaction={
        "RedactionType": "PII",
        "RedactionOutput": "redacted",  # "redacted_and_unredacted" also writes the raw transcript
        "PiiEntityTypes": ["NAME", "PHONE", "SSN"],
    },
)
```

## 4. Comprehend Medical

Lecture 52.

- `DetectPHI`: Health Insurance Portability and Accountability Act (HIPAA)-style PHI
  - names, ages, dates, Identifiers (IDs), addresses, professions …
- Detection only
  - apply offsets with the same `redact_text` logic ([04redaction-rules](04safety.02pii-redaction.04redaction-rules.md))

## 5. Macie

Lecture 225, mention only.

- Managed + custom data identifiers over S3 objects
- Sampling-based automated discovery
- Finds which buckets hold PII
  - decides what goes through the redaction job before indexing
