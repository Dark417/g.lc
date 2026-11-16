# data-automation Invoke And Poll

> Run Bedrock Data Automation (BDA): async vs sync, idempotent submit with `clientToken`, polling with backoff, and the end-to-end use case.

## Index

- [1. Sync Vs Async](#1-sync-vs-async)
- [2. Async Invoke](#2-async-invoke)
- [3. Polling](#3-polling)
- [4. End-To-End Use Case](#4-end-to-end-use-case)

## 1. Sync Vs Async

Async is the general path; sync is only for small single files.

| Mode | Application Programming Interface (API) | Input / output | Use for |
|---|---|---|---|
| Async | `InvokeDataAutomationAsync` | Simple Storage Service (S3) in, S3 out, invocation Amazon Resource Name (ARN) | Batch, long audio, video, large Portable Document Format files (PDFs) |
| Sync | `InvokeDataAutomation` | Result returned inline | Small single files |

- Async completion: poll status, or listen on EventBridge
- **Catch**: sync has smaller input limits
  - Check the quota page
  - The code here shows async because it is the general path

## 2. Async Invoke

The same `run_id` always maps to the same `clientToken`, so a retried submit is not double-billed.

- `dataAutomationProfileArn` is required
- Output `s3Uri` is a prefix
  - BDA adds `<invocation-id>/` under it
- Per-run output prefix ⇒ listing and cleanup stay cheap

```python
# app/infra/_03data_01data_automation.py
def invoke_async(input_s3_uri: str, run_id: str | None = None) -> JobRef:
    cfg = get_bda_settings()
    bucket = get_settings().data_bucket
    run_id = run_id or uuid.uuid4().hex
    output_uri = f"s3://{bucket}/{cfg.output_prefix}{run_id}/"  # per-run prefix
    resp = _runtime().invoke_data_automation_async(
        clientToken=run_id,  # idempotency: a retry with the same token returns the same invocation
        inputConfiguration={"s3Uri": input_s3_uri},
        outputConfiguration={"s3Uri": output_uri},
        dataAutomationConfiguration={
            "dataAutomationProjectArn": cfg.project_arn,
            "stage": cfg.stage,  # LIVE | DEVELOPMENT
        },
        dataAutomationProfileArn=cfg.profile_arn,
        # encryptionConfiguration={"kmsKeyId": "..."}  # optional: CMK for the output
        # notificationConfiguration={"eventBridgeConfiguration": {"eventBridgeEnabled": True}}  # push, no polling
    )
    return JobRef(invocation_arn=resp["invocationArn"], output_s3_uri=output_uri)
```

- **Catch**: Customer Managed Key (CMK) output encryption needs `kms:GenerateDataKey` for the caller
- **Catch**: policy must allow `data-automation-profile/*` and the project ARN
  - Else `AccessDenied` on invoke

## 3. Polling

Polling uses full-jitter backoff and a hard deadline.

- Use for demos and low volume
- At volume use EventBridge instead
- Two clients
  - `bedrock-data-automation`: control plane (blueprints, projects)
  - `bedrock-data-automation-runtime`: invoke + status

```python
# app/infra/_03data_01data_automation.py
def wait_for_job(job: JobRef, deadline_s: float | None = None) -> tuple[JobStatus, dict[str, Any]]:
    end = time.monotonic() + (deadline_s or get_bda_settings().poll_deadline_s)
    attempt = 0
    while True:
        resp = _runtime().get_data_automation_status(invocationArn=job.invocation_arn)
        status = JobStatus(resp["status"])
        if status in TERMINAL:
            return status, resp
        if time.monotonic() >= end:
            raise TimeoutError(f"{job.invocation_arn} still {status} after deadline")
        time.sleep(backoff(attempt, base=1.0, cap=15.0))  # full-jitter, capped at 15 s
        attempt += 1
```

- **Catch**: large video can outlive your deadline
  - Status stays `InProgress`
  - Use a longer deadline or EventBridge
- **Catch**: `ServiceError` may be retried; `ClientError` not

## 4. End-To-End Use Case

The service submits, waits, reads, and returns the custom-output fields.

→ Build the input Uniform Resource Identifier (URI) from the key under `bda/input/`  
→ `invoke_async` → `wait_for_job` → `read_job_result`  
→ Return `inference_result` of the first custom output

```python
# app/service/_03data_01data_automation.py
def extract_invoice(key: str, run_id: str | None = None) -> dict[str, Any]:
    uri = f"s3://{get_settings().data_bucket}/{get_bda_settings().input_prefix}{key}"
    job = invoke_async(uri, run_id)
    status, resp = wait_for_job(job)
    result = read_job_result(status, resp)
    if result.status is not JobStatus.SUCCESS:
        # error dict instead of raising, so the caller can route it to review
        return {"status": result.status.value, "error": result.error}
    fields = result.custom_output[0].get("inference_result", {}) if result.custom_output else {}
    return {"status": "Success", "invocation_arn": job.invocation_arn, "fields": fields}
```

```python
# app/api/_03data_01data_automation.py
class ExtractRequest(BaseModel):
    key: str = Field(min_length=1, description="object key under bda/input/")
    run_id: str | None = Field(default=None, description="idempotency token; same id, same job")


@router.post("/extract")
def extract(body: ExtractRequest) -> dict[str, Any]:
    return service.extract_invoice(body.key, body.run_id)
```

- **Catch**: a synchronous Hypertext Transfer Protocol (HTTP) call that waits for an async job only fits demos
  - Production: S3 event → submit, EventBridge → read
