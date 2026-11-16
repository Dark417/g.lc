# comprehend Batch And Async

> Scale beyond one text: size limits, `BatchDetect*` with per-item `ErrorList`, and async Simple Storage Service (S3) jobs.

## Index

- [1. Size Limits And Trimming](#1-size-limits-and-trimming)
- [2. Batch Calls And ErrorList](#2-batch-calls-and-errorlist)
- [3. Async Jobs](#3-async-jobs)

## 1. Size Limits And Trimming

Sync Application Programming Interfaces (APIs) limit input size in bytes, so the code trims on an 8-bit Unicode Transformation Format (UTF-8) boundary.

- Documented limits differ per API
  - Check the quota page
- Cut text on sentence boundaries when you can
  - Sentiment of a truncated text is partial

```python
# app/config/_03data_04comprehend.py
class ComprehendSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_COMPREHEND_", env_file=".env", extra="ignore")

    default_language: str = "en"  # BCP-47-ish code; Detect* APIs support a limited language list
    max_text_bytes: int = 5000  # keep sync input small (limits differ per API: check the quota page)
    batch_size: int = 25  # BatchDetect* documents per call (documented maximum, check the quota page)
    min_entity_score: float = 0.8  # drop low-confidence entities
    negative_threshold: float = 0.7  # NEGATIVE score above this routes to the strong model
```

```python
# app/infra/_03data_04comprehend.py
def _trim(text: str) -> str:
    """Cut to max bytes on a UTF-8 boundary (the sync APIs limit input size in bytes)."""
    return text.encode()[: get_comprehend_settings().max_text_bytes].decode(errors="ignore")
```

- **Catch**: over the limit raises `TextSizeLimitExceededException`
  - Chunk text

## 2. Batch Calls And ErrorList

The Hypertext Transfer Protocol (HTTP) call succeeds while individual items fail, so `ErrorList` must always be read.

- Input: a list of texts, up to 25 per call
- Output
  - `ResultList` with `Index`
  - `ErrorList` with `Index`, `ErrorCode`, `ErrorMessage`
- Split larger lists; retry only failed indexes

```python
# app/infra/_03data_04comprehend.py
def batch_detect_entities(texts: list[str], lang: str | None = None) -> BatchResult:
    cfg = get_comprehend_settings()
    out = BatchResult()
    for start in range(0, len(texts), cfg.batch_size):
        chunk = [_trim(t) for t in texts[start : start + cfg.batch_size]]
        resp = _c().batch_detect_entities(TextList=chunk, LanguageCode=lang or cfg.default_language)
        # response indexes are relative to the chunk: map back to the global input index
        for item in resp["ResultList"]:
            out.ok[start + item["Index"]] = [e for e in item["Entities"] if e["Score"] >= cfg.min_entity_score]
        for err in resp["ErrorList"]:
            out.failed[start + err["Index"]] = f"{err['ErrorCode']}: {err['ErrorMessage']}"
    return out
```

```python
# app/domain/_03data_04comprehend.py
@dataclass
class BatchResult:
    ok: dict[int, list[dict]] = field(default_factory=dict)  # input index -> entities
    failed: dict[int, str] = field(default_factory=dict)  # input index -> "ErrorCode: message"
```

```python
# app/api/_03data_04comprehend.py
@router.post("/entities/batch")
def entities_batch(body: BatchRequest) -> dict[str, Any]:
    r = infra.batch_detect_entities(body.texts)
    return {"ok": r.ok, "failed": r.failed}
```

- **Catch**: reading only `ResultList` ⇒ silent partial failure
  - Missing indexes are the only signal
- **Catch**: bursts throttle (`ThrottlingException`)
  - Adaptive retries in the shared client, backoff, batch

## 3. Async Jobs

Async jobs read a corpus from S3 and write results to S3.

- `StartEntitiesDetectionJob` etc.
- Poll `Describe*Job`
- Jobs for offline; batch APIs for near-real-time

```python
# illustrative (no repo code)
job = client("comprehend").start_entities_detection_job(
    InputDataConfig={"S3Uri": "s3://bucket/comprehend/in/", "InputFormat": "ONE_DOC_PER_LINE"},
    OutputDataConfig={"S3Uri": "s3://bucket/comprehend/out/"},
    DataAccessRoleArn=role_arn,  # Comprehend reads and writes S3 with this role
    LanguageCode="en",
)
client("comprehend").describe_entities_detection_job(JobId=job["JobId"])  # poll until COMPLETED
```

- **Catch**: async jobs have startup latency
  - Not for request paths
