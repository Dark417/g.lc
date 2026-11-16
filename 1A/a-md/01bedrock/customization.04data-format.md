# customization Data Format And Upload

> JavaScript Object Notation (JSON) Lines (JSONL) in the base model's format, validated locally, uploaded to Simple Storage Service (S3) with a separate validation set.

## Index

- [1. JSONL Formats](#1-jsonl-formats)
  - [1.1 Writing Records](#11-writing-records)
- [2. Validation Set And Quotas](#2-validation-set-and-quotas)
- [3. Quality Rules](#3-quality-rules)
- [4. Local Pre-Flight Validation](#4-local-pre-flight-validation)
- [5. Upload To S3](#5-upload-to-s3)

Back to [00index](customization.00index.md).

---

## 1. JSONL Formats

The base model decides the record shape.

- JSONL: one JSON object per line, 8-bit Unicode Transformation Format (UTF-8)
- Format depends on the base model
  - Check the model's customization page
- Shapes
  - **Prompt/completion** (older text models)
    - `{"prompt": "...", "completion": "..."}`
  - **Conversation** (Nova and newer)
    - `{"schemaVersion": "bedrock-conversation-2024", "system": [{"text": ...}], "messages": [{"role": "user", ...}, {"role": "assistant", ...}]}`
  - **Continued pre-training**
    - `{"input": "<raw text>"}`

### 1.1 Writing Records

- One `TrainingExample` = the exact output you want for this input.

```python
# app/domain/_01bedrock_02customization.py
CONVERSATION_SCHEMA = "bedrock-conversation-2024"

@dataclass(frozen=True)
class TrainingExample:
    prompt: str
    completion: str  # the exact target output
    system: str = ""

def to_jsonl_line(example: TrainingExample, fmt: DatasetFormat) -> str:
    if fmt == DatasetFormat.PROMPT_COMPLETION:
        record: dict[str, Any] = {"prompt": example.prompt, "completion": example.completion}
    else:
        record = {
            "schemaVersion": CONVERSATION_SCHEMA,
            "messages": [
                {"role": "user", "content": [{"text": example.prompt}]},
                {"role": "assistant", "content": [{"text": example.completion}]},
            ],
        }
        if example.system:
            record["system"] = [{"text": example.system}]
    return json.dumps(record, ensure_ascii=False)

def write_jsonl(examples: Iterable[TrainingExample], fmt: DatasetFormat) -> bytes:
    return ("\n".join(to_jsonl_line(e, fmt) for e in examples) + "\n").encode("utf-8")
```

- Catch: the continued pre-training `{"input": ...}` shape is not coded.

## 2. Validation Set And Quotas

- Validation set
  - Separate file, same format
  - Never overlapping with training
- Quotas are per model
  - maximum records
  - file size
  - tokens per record

  ⇒ check the quotas page

## 3. Quality Rules

- Outputs must be exactly what you want the model to produce
- Cover edge cases and refusals
- Deduplicate
- Remove Personally Identifiable Information (PII)
  - See [pii-redaction](../04safety/pii-redaction.00index.md)

## 4. Local Pre-Flight Validation

Validate locally so the paid job does not fail an hour in.

- Checks
  - UTF-8
  - one JSON object per line
  - required keys
  - role order: user → assistant, ending on assistant
  - non-empty text
  - size guard
  - exact duplicates

```python
# app/domain/_01bedrock_02customization.py
def _check_record(record: dict[str, Any], fmt: DatasetFormat) -> list[str]:
    if fmt == DatasetFormat.PROMPT_COMPLETION:
        return [f"missing or empty '{k}'" for k in ("prompt", "completion") if not str(record.get(k, "")).strip()]
    problems: list[str] = []
    if record.get("schemaVersion") != CONVERSATION_SCHEMA:
        problems.append(f"schemaVersion must be {CONVERSATION_SCHEMA}")
    messages = record.get("messages")
    if not isinstance(messages, list) or len(messages) < 2:
        return problems + ["messages must hold at least one user + assistant turn"]
    for i, m in enumerate(messages):
        expected = "user" if i % 2 == 0 else "assistant"  # strict alternation
        if m.get("role") != expected:
            problems.append(f"message {i} role {m.get('role')!r}, expected {expected!r}")
    if messages[-1].get("role") != "assistant":
        problems.append("last message must be the assistant (the target output)")
    return problems
```

```python
# app/domain/_01bedrock_02customization.py  (inside validate_jsonl, per line)
if len(line) > max_record_chars:
    report.errors.append(f"line {n}: {len(line)} chars > {max_record_chars}")
digest = hashlib.sha256(line.encode()).hexdigest()  # exact-duplicate detection
if digest in seen:
    report.duplicates += 1
seen.add(digest)
```

```python
# app/config/_01bedrock_02customization.py
dataset_format: str = "conversation"  # conversation (bedrock-conversation-2024) | prompt_completion
max_record_chars: int = 40_000  # local guard; the real limit is tokens per record per model (quotas page)
```

- Catch: model-specific limits (records, tokens) still apply.
- The Representational State Transfer (REST) route `/dataset/preview` renders and validates without any Amazon Web Services (AWS) call.

## 5. Upload To S3

→ write JSONL in the base model's format  
→ validate train and validation locally  
→ reject train/validation overlap  
→ upload to `customization/train/` and `customization/validation/`

```python
# app/infra/_01bedrock_02customization.py
def upload_dataset(self, train, validation) -> tuple[str, str, ValidationReport]:
    fmt = DatasetFormat(self.settings.dataset_format)
    train_bytes, val_bytes = write_jsonl(train, fmt), write_jsonl(validation, fmt)
    report = validate_jsonl(train_bytes, fmt, self.settings.max_record_chars)
    val_report = validate_jsonl(val_bytes, fmt, self.settings.max_record_chars)
    report.errors += [f"validation {e}" for e in val_report.errors]
    overlap = {(e.prompt, e.completion) for e in train} & {(e.prompt, e.completion) for e in validation}
    if overlap:  # validation must never overlap training
        report.errors.append(f"{len(overlap)} examples appear in both train and validation")
    if not report.ok:
        raise CustomizationError("; ".join(report.errors[:20]))
    train_key = f"{self.settings.prefix}/train/train.jsonl"
    val_key = f"{self.settings.prefix}/validation/validation.jsonl"
    for key, body in ((train_key, train_bytes), (val_key, val_bytes)):
        self.s3.put_object(Bucket=self.settings.bucket, Key=key, Body=body, ContentType="application/jsonl")
    return self._uri("train/train.jsonl"), self._uri("validation/validation.jsonl"), report
```

- Catch: only exact duplicates across both sets are detected.
- Catch: the bucket is Server-Side Encryption with Key Management Service (KMS) (SSE-KMS); the service role needs the KMS grant.
