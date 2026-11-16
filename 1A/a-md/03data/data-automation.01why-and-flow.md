# data-automation Why And Flow

> Why Bedrock Data Automation (BDA) exists, the end-to-end flow from Simple Storage Service (S3) to result JavaScript Object Notation (JSON), and how the result is read back.

## Index

- [1. Why It Was Created](#1-why-it-was-created)
  - [1.1 The Pain Before It](#11-the-pain-before-it)
  - [1.2 Common Use Cases](#12-common-use-cases)
- [2. Picture](#2-picture)
- [3. Job Status And Result Shape](#3-job-status-and-result-shape)
- [4. Reading Results](#4-reading-results)

## 1. Why It Was Created

BDA unifies multi-service extraction behind one invoke and one result schema per modality.

### 1.1 The Pain Before It

- Extraction pipelines were stitched together
  - Textract for Optical Character Recognition (OCR)
  - Transcribe for audio
  - Rekognition for images
  - A Large Language Model (LLM) to structure the output
- Each step has its own output shape, errors and cost

⇒ Glue code and drift.  
→ BDA puts it behind one invoke and one result schema per modality.

### 1.2 Common Use Cases

- Invoices, forms, contracts → fields
- Call recordings → transcript + summary
- Video → chapters, scene summaries
- Pre-processing before Retrieval-Augmented Generation (RAG) chunking

## 2. Picture

The client submits once, then polls status and reads results from the output prefix.

```text
 S3 bda/input/invoice.pdf
        │ InvokeDataAutomationAsync (project, profile, output uri)
        ▼
 ┌──────────────── BDA ────────────────┐
 │ modality router → standard output   │
 │                 → blueprint fields  │  (custom output)
 └──────────────────┬──────────────────┘
                    ▼
 S3 bda/output/<invocation-id>/job_metadata.json
                              /0/standard_output/0/result.json
                              /0/custom_output/0/result.json
 client ── GetDataAutomationStatus
           (Created → InProgress → Success | ServiceError | ClientError)
```

Notice that results never come back on the invoke call; they land in S3 under the invocation id.

## 3. Job Status And Result Shape

The status enum decides retry behavior, so the code models it explicitly.

- **Terminal states**: `Success`, `ServiceError`, `ClientError`
- **`ServiceError`**: BDA side failed
  - Safe to resubmit
- **`ClientError`**: your input failed
  - Resubmitting the same file fails again

```python
# app/domain/_03data_01data_automation.py
class JobStatus(StrEnum):
    # GetDataAutomationStatus.status values
    CREATED = "Created"
    IN_PROGRESS = "InProgress"
    SUCCESS = "Success"
    SERVICE_ERROR = "ServiceError"  # BDA side: safe to resubmit
    CLIENT_ERROR = "ClientError"  # your input: resubmitting the same file fails again


TERMINAL = {JobStatus.SUCCESS, JobStatus.SERVICE_ERROR, JobStatus.CLIENT_ERROR}


@dataclass
class JobResult:
    status: JobStatus
    metadata: dict[str, Any] = field(default_factory=dict)  # job_metadata.json
    standard_output: list[dict[str, Any]] = field(default_factory=list)
    custom_output: list[dict[str, Any]] = field(default_factory=list)
    error: str = ""
```

- ⚠️ Retry only on `ServiceError`, never on `ClientError`

## 4. Reading Results

Reading is a two-hop lookup: status response → metadata file → result files.

- The status response gives the metadata file Uniform Resource Identifier (URI)
- The metadata lists result paths per asset and segment
  - `standard_output_path`
  - `custom_output_path`

```python
# app/infra/_03data_01data_automation.py
def read_job_result(status: JobStatus, status_resp: dict[str, Any]) -> JobResult:
    if status is not JobStatus.SUCCESS:
        return JobResult(status=status, error=f"{status_resp.get('errorType')}: {status_resp.get('errorMessage')}")
    metadata = _read_json(status_resp["outputConfiguration"]["s3Uri"])  # job_metadata.json
    result = JobResult(status=status, metadata=metadata)
    # Metadata shape (verify against a real run): output_metadata[] -> segment_metadata[]
    for asset in metadata.get("output_metadata", []):
        for seg in asset.get("segment_metadata", []):
            if seg.get("standard_output_path"):
                result.standard_output.append(_read_json(seg["standard_output_path"]))
            if seg.get("custom_output_path"):
                result.custom_output.append(_read_json(seg["custom_output_path"]))
    return result
```

- **Catch**: the metadata shape is undocumented in detail
  - Verify against a real run before depending on it
- **Catch**: reading output needs `kms:Decrypt` when output is Customer Managed Key (CMK)-encrypted
  - See [98 failure modes](data-automation.98tradeoffs.md#4-failure-modes)
