# pii-redaction.03comprehend-apis Comprehend Personally Identifiable Information (PII) Application Programming Interfaces (APIs)

> The sync detect and contains calls, the async Simple Storage Service (S3) redaction job, and how they are billed.

## Index

- [1. DetectPiiEntities](#1-detectpiientities)
- [2. ContainsPiiEntities](#2-containspiientities)
- [3. StartPiiEntitiesDetectionJob](#3-startpiientitiesdetectionjob)
  - [3.1 Request Fields](#31-request-fields)
  - [3.2 Code: Start and Poll](#32-code-start-and-poll)
- [4. Pricing Shape](#4-pricing-shape)

Back to [00index](pii-redaction.00index.md).

## 1. DetectPiiEntities

`DetectPiiEntities(Text, LanguageCode)` says WHERE the Personally Identifiable Information (PII) is.

- Returns `Entities[]`
  - `Type`
  - `Score` (0–1)
  - `BeginOffset`, `EndOffset`
- Text cap per request
  - order of magnitude: 100 kilobytes (KB) 8-bit Unicode Transformation Format (UTF-8); check the quota page
  - chunk long docs and shift offsets
- Languages: English and Spanish for PII
  - the shared enum lists more; check the docs

```python
# app/infra/_04safety_02pii_redaction.py
MAX_SYNC_BYTES = 90_000  # under the ~100 KB sync cap with margin; split on whitespace


def detect_pii(text: str, language_code: str | None = None) -> list[PiiEntity]:
    lang = language_code or get_pii_settings().language_code
    out: list[PiiEntity] = []
    for offset, chunk in _chunks(text):  # (char_offset, chunk) pieces under MAX_SYNC_BYTES
        if not chunk.strip():
            continue
        resp = _comprehend().detect_pii_entities(Text=chunk, LanguageCode=lang)
        out.extend(
            # shift chunk-relative offsets back to positions in the full text
            PiiEntity(e["Type"], float(e["Score"]), offset + int(e["BeginOffset"]), offset + int(e["EndOffset"]))
            for e in resp.get("Entities", [])
        )
    return out
```

- Catch
  - An entity sitting on a chunk boundary can be missed
  - Over the cap ⇒ `TextSizeLimitExceededException`

## 2. ContainsPiiEntities

`ContainsPiiEntities(Text, LanguageCode)` says only WHICH types are present.

- Returns `Labels[]`: `Name` (type), `Score`
- No offsets
  - a gate: skip detect + redact for the many messages with no PII

```python
# app/infra/_04safety_02pii_redaction.py
def contains_pii(text: str, language_code: str | None = None) -> dict[str, float]:
    lang = language_code or get_pii_settings().language_code
    chunk = _chunks(text)[0][1] if text else ""  # only the first chunk is checked for long text
    if not chunk.strip():
        return {}
    resp = _comprehend().contains_pii_entities(Text=chunk, LanguageCode=lang)
    return {lbl["Name"]: float(lbl["Score"]) for lbl in resp.get("Labels", [])}
```

- Catch
  - When most messages contain PII, the gate is a wasted extra call

## 3. StartPiiEntitiesDetectionJob

The async S3 batch job writes redacted copies or offsets for whole corpora.

### 3.1 Request Fields

- `InputDataConfig.S3Uri` + `InputFormat`
  - `ONE_DOC_PER_FILE` | `ONE_DOC_PER_LINE`
- `OutputDataConfig.S3Uri` + `KmsKeyId`
- `Mode`
  - `ONLY_REDACTION`: writes redacted copies
  - `ONLY_OFFSETS`: writes entity JavaScript Object Notation (JSON)
- `RedactionConfig` (ONLY_REDACTION)
  - `PiiEntityTypes` (or `ALL`)
  - `MaskMode`: `MASK` | `REPLACE_WITH_PII_ENTITY_TYPE`
  - `MaskCharacter`: one char, e.g. `*`
- `DataAccessRoleArn`
  - Comprehend assumes it to read input and write output
- `ClientRequestToken`: idempotent start
- Limit: one MaskMode for every type in the job
  - per-type policies need ONLY_OFFSETS + your own apply step

### 3.2 Code: Start and Poll

```python
# app/infra/_04safety_02pii_redaction.py
def start_redaction_job(
    input_s3_uri: str,
    output_s3_uri: str,
    policy: RedactionPolicy,
    mode: str = "ONLY_REDACTION",
    mask_mode: str = "REPLACE_WITH_PII_ENTITY_TYPE",  # [EMAIL]: better for retrieval than MASK
    input_format: str = "ONE_DOC_PER_LINE",
    job_name: str | None = None,
    client_token: str | None = None,
) -> str:
    s = get_pii_settings()
    kwargs: Json = {
        "InputDataConfig": {"S3Uri": input_s3_uri, "InputFormat": input_format},  # ONE_DOC_PER_FILE | ONE_DOC_PER_LINE
        "OutputDataConfig": {"S3Uri": output_s3_uri, "KmsKeyId": s.kms_key_id},
        "Mode": mode,
        "DataAccessRoleArn": s.data_access_role_arn,  # Comprehend assumes it; caller needs iam:PassRole
        "JobName": job_name or f"a-pii-{uuid.uuid4().hex[:8]}",
        "LanguageCode": s.language_code,
        "ClientRequestToken": client_token or str(uuid.uuid4()),  # retried start is idempotent
        "Tags": [{"Key": "Component", "Value": "04.02"}],
    }
    if mode == "ONLY_REDACTION":
        kwargs["RedactionConfig"] = {
            "PiiEntityTypes": policy.redacted_types() or ["ALL"],
            "MaskMode": mask_mode,  # ONE mode for every type in the job
            "MaskCharacter": policy.mask_char,  # single character; used by MASK only
        }
    resp = _comprehend().start_pii_entities_detection_job(**kwargs)
    return str(resp["JobId"])


def wait_for_job(job_id: str, timeout_s: float = 3600.0) -> Json:
    """Poll with capped exponential backoff + jitter. Jobs take minutes; in prod prefer EventBridge over polling."""
    deadline = time.monotonic() + timeout_s
    attempt = 0
    while True:
        job = describe_job(job_id)  # status, message (failure reason), output_s3_uri
        if job["status"] in JOB_TERMINAL:  # COMPLETED | FAILED | STOPPED
            return job
        if time.monotonic() > deadline:
            raise TimeoutError(f"PII job {job_id} still {job['status']} after {timeout_s}s")
        time.sleep(max(5.0, backoff(attempt, base=5.0, cap=60.0)))
        attempt += 1
```

- Catch
  - AccessDenied shows up in the job `Message` field
    - fix: role trusts `comprehend.amazonaws.com`, Key Management Service (KMS) grant present
  - The job redacts content, not file names or S3 tags

## 4. Pricing Shape

- Per unit of 100 characters
- 3-unit minimum per request (Comprehend pricing page, 2026-11)
  - tiny messages cost the minimum
