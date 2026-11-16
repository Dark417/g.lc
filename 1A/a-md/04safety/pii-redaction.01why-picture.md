# pii-redaction.01why-picture Why Personally Identifiable Information (PII) Redaction and Where It Happens

> Why managed Personally Identifiable Information (PII) detectors exist and at which boundaries a Generative Artificial Intelligence (GenAI) system redacts.

## Index

- [1. Why It Was Created](#1-why-it-was-created)
  - [1.1 The Pain Before It](#11-the-pain-before-it)
  - [1.2 What Managed Detectors Add](#12-what-managed-detectors-add)
  - [1.3 Common Use Cases](#13-common-use-cases)
- [2. Picture: Where PII Is Handled](#2-picture-where-pii-is-handled)
  - [2.1 Rules](#21-rules)
  - [2.2 Code: Entity and Result](#22-code-entity-and-result)

Back to [00index](pii-redaction.00index.md).

## 1. Why It Was Created

Regexes and hand-built Named Entity Recognition (NER) could not keep up, and the Large Language Model (LLM) era multiplies copies of data.

### 1.1 The Pain Before It

- Regexes catch Social Security Numbers (SSNs) and cards
  - but not names, addresses, or "my wife's birthday is …"
- Hand-built NER models per team, per language, never retrained
- LLM era adds new copies
  - prompt logs
  - vector stores
  - fine-tune sets
  - model-provider retention

### 1.2 What Managed Detectors Add

- Pretrained Machine Learning (ML) NER for ~30+ PII types with scores
  - Comprehend: 36 types in the botocore 1.44 enum, incl. `ALL`
- Same Application Programming Interface (API) for real-time and batch
- No model to host

### 1.3 Common Use Cases

- Scrub support tickets before building a Retrieval-Augmented Generation (RAG) index
- Mask user prompts before they hit model invocation logs
- Redact call-center transcripts (Transcribe) before analytics
- Remove Protected Health Information (PHI) from clinical notes before summarization (Comprehend Medical)

## 2. Picture: Where PII Is Handled

Each arrow that copies data is a redaction boundary.

```text
   S3 raw docs ──► Macie (discover, classify)          at rest
        │
        └──► Comprehend async job (ONLY_REDACTION) ──► S3 redacted ──► KB / vector index
                                                                       (pre-index scrubbing)
   user ──► API ──► Comprehend detect + policy ──► pseudonymized prompt ──► Bedrock model
                    (or Guardrails input ANONYMIZE)                              │
                                                                                 ▼
   user ◄── detokenize (authorized only) ◄── Guardrails output check (PII, BLOCK/ANONYMIZE)
                                                                                 │
   logs ◄────────────────────────── only redacted text + entity types, never raw values
```

Notice that the model only sees pseudonyms, and only an authorized user gets real values back.

### 2.1 Rules

- Redact at the earliest boundary that copies the data, then again on output
- Output check still matters
  - the model can produce PII from its training data or from retrieved docs

### 2.2 Code: Entity and Result

- The domain works on offsets from ANY detector
  - Comprehend, Comprehend Medical, Presidio, regex
- Entity types use Comprehend names (`SSN`, `CREDIT_DEBIT_NUMBER`)
  - Guardrails names some differently (`US_SOCIAL_SECURITY_NUMBER`, `CREDIT_DEBIT_CARD_NUMBER`)

```python
# app/domain/_04safety_02pii_redaction.py
@dataclass(frozen=True)
class PiiEntity:
    type: str
    score: float
    begin: int  # character offset, inclusive
    end: int  # character offset, exclusive


@dataclass(frozen=True)
class RedactionResult:
    text: str  # redacted text ("" when blocked)
    applied: tuple[PiiEntity, ...] = ()
    skipped_low_score: int = 0
    blocked_types: tuple[str, ...] = ()

    def summary(self) -> dict[str, int]:
        """Types + counts: the only thing safe to log."""
        counts: dict[str, int] = {}
        for e in self.applied:
            counts[e.type] = counts.get(e.type, 0) + 1
        return counts
```

- Catch
  - Logs get `summary()` (types + counts), never matched values
