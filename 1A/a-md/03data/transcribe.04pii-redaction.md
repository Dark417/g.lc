# transcribe Personally Identifiable Information (PII) Redaction

> Redact before the transcript reaches the model or the log.

## Index

- [1. ContentRedaction](#1-contentredaction)
- [2. Dual Output And Limits](#2-dual-output-and-limits)

## 1. ContentRedaction

Transcribe can replace Personally Identifiable Information (PII) spans in the transcript text during the job.

- `RedactionType=PII`: the only value
- `RedactionOutput`
  - `redacted`
  - `redacted_and_unredacted`
- `PiiEntityTypes`: optional, default ALL
- Detail and comparison with Comprehend and Guardrails: [pii-redaction](../04safety/pii-redaction.00index.md)

```python
# app/infra/_03data_03transcribe.py  (inside start_job)
if redact:
    kwargs["ContentRedaction"] = {
        "RedactionType": "PII",  # the only value
        "RedactionOutput": cfg.redaction_output,  # redacted | redacted_and_unredacted
        "PiiEntityTypes": [t.strip() for t in cfg.pii_entity_types.split(",")],  # "ALL" or a list
    }
```

- **Catch**: redaction language support is narrower than transcription
  - Check the supported-languages page

## 2. Dual Output And Limits

Redaction changes only the text, so the sensitive surface does not disappear.

- `redacted_and_unredacted` writes both transcripts
  - Store the raw one encrypted with a tighter policy
  - ⚠️ Dual output doubles the sensitive store
- Text-only: audio keeps the PII
  - Lifecycle the audio too
- Redact before logging
- Keep unredacted output access-controlled

→ Raw transcript sent to the Large Language Model (LLM)  
⇒ PII leaks into the summary.  
→ Redact first, summarize the redacted transcript.
