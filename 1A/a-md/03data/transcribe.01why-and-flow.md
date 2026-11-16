# transcribe Why And Flow

> Why Transcribe exists, the batch job flow, batch vs streaming, Call Analytics, and idempotent job naming.

## Index

- [1. Why It Was Created](#1-why-it-was-created)
- [2. Picture](#2-picture)
- [3. API Choice](#3-api-choice)
  - [3.1 Batch Vs Streaming](#31-batch-vs-streaming)
  - [3.2 Call Analytics](#32-call-analytics)
- [4. Idempotent Job Naming](#4-idempotent-job-naming)
- [5. Polling And End-To-End](#5-polling-and-end-to-end)

## 1. Why It Was Created

Transcribe is Automatic Speech Recognition (ASR) as an Application Programming Interface (API) with domain adaptation knobs.

- **The pain**: ASR needed
  - Machine Learning (ML) teams
  - Graphics Processing Units (GPUs)
  - Per-language models
- **Use cases**
  - Contact-center analytics, meeting notes, media captions
  - Voice input to an agent
  - Compliance search over recordings

## 2. Picture

One batch job: submit with output location, poll, then parse and summarize.

```text
 S3 transcribe/in/call.wav
        │ StartTranscriptionJob(name, Settings, ContentRedaction,
        │                       OutputBucketName, OutputKey)
        ▼
   Transcribe (QUEUED → IN_PROGRESS → COMPLETED | FAILED)
        ▼
 S3 transcribe/out/<name>.json ─► parse turns ─► converse ─► summary
```

Notice the output lands in your bucket because the job names `OutputBucketName` and `OutputKey`.

## 3. API Choice

Pick the API by latency need and by how specialized the use case is.

### 3.1 Batch Vs Streaming

| Mode | Input | Latency | Features |
|---|---|---|---|
| Batch | Whole file in Simple Storage Service (S3) | Minutes, async | Higher accuracy options, all features |
| Streaming | Live audio | Seconds, partial results | Fewer features/languages |

- Streaming Software Development Kit (SDK) is not shown in code here
- Streaming trades accuracy and features for latency
- Pick by latency need, not by habit

### 3.2 Call Analytics

- Separate API: `StartCallAnalyticsJob`
- Adds
  - Sentiment per turn
  - Talk-time, interruptions
  - Categories
  - Issue summary
- Use when the whole job is contact-center
  - Otherwise plain transcription plus a Large Language Model (LLM) is simpler

```python
# illustrative (no repo code)
client("transcribe").start_call_analytics_job(
    CallAnalyticsJobName=name,
    Media={"MediaFileUri": media_uri},
    DataAccessRoleArn=role_arn,
    ChannelDefinitions=[{"ChannelId": 0, "ParticipantRole": "AGENT"},
                        {"ChannelId": 1, "ParticipantRole": "CUSTOMER"}],
)
```

- **Catch**: Call Analytics is priced and scoped separately from plain transcription

## 4. Idempotent Job Naming

Job names are unique per account and Region, so the name itself is the idempotency key.

- Deterministic name = hash of media Uniform Resource Identifier (URI) + options
  - Same media + same options = same name = retry-safe
- Allowed characters: letters, digits, `.`, `_`, `-`; max 200
- `job_prefix` `a-` matches the Identity and Access Management (IAM) scope `transcription-job/a-*`
- A repeated name raises `ConflictException`
  - `start_job` treats it as "already started"

```python
# app/infra/_03data_03transcribe.py
def job_name_for(media_uri: str, diarize: bool, redact: bool) -> str:
    digest = hashlib.sha256(f"{media_uri}|{diarize}|{redact}".encode()).hexdigest()[:24]
    return f"{get_transcribe_settings().job_prefix}{digest}"


# inside start_job
    try:
        client("transcribe").start_transcription_job(**kwargs)
    except ClientError as e:
        if e.response["Error"]["Code"] != "ConflictException":
            raise  # ConflictException = same name already started: fine
    return name
```

- **Catch**: change an option and the name changes
- **Catch**: delete old jobs before re-running the same name
- **Catch**: idempotent names also stop re-transcribing duplicates (cost)

## 5. Polling And End-To-End

Jobs take minutes, so polling backs off to 30 s; EventBridge on job state change scales better.

```python
# app/infra/_03data_03transcribe.py
def wait_for_job(name: str) -> dict[str, Any]:
    """Poll GetTranscriptionJob (QUEUED, IN_PROGRESS, COMPLETED, FAILED) with backoff."""
    end = time.monotonic() + get_transcribe_settings().poll_deadline_s
    attempt = 0
    while True:
        job = client("transcribe").get_transcription_job(TranscriptionJobName=name)["TranscriptionJob"]
        if job["TranscriptionJobStatus"] in ("COMPLETED", "FAILED"):
            return job
        if time.monotonic() >= end:
            raise TimeoutError(f"{name} still {job['TranscriptionJobStatus']}")
        time.sleep(backoff(attempt, base=2.0, cap=30.0))
        attempt += 1
```

```python
# app/service/_03data_03transcribe.py
def transcribe_and_summarize(key: str, diarize: bool = True, redact: bool = True) -> dict[str, Any]:
    uri = f"s3://{get_settings().data_bucket}/{get_transcribe_settings().input_prefix}{key}"
    name = start_job(uri, diarize, redact)
    job = wait_for_job(name)
    if job["TranscriptionJobStatus"] == "FAILED":
        # failed jobs return the reason instead of raising
        return {"job": name, "status": "FAILED", "reason": job.get("FailureReason", "")}
    transcript = read_transcript(name)
    return {"job": name, "status": "COMPLETED", "turns": len(transcript.turns), "summary": summarize(transcript)}
```

```python
# app/api/_03data_03transcribe.py
class TranscribeRequest(BaseModel):
    key: str = Field(min_length=1, description="object key under transcribe/in/")
    diarize: bool = True
    redact: bool = True


@router.post("/summarize")
def summarize_call(body: TranscribeRequest) -> dict[str, Any]:
    return service.transcribe_and_summarize(body.key, body.diarize, body.redact)
```

- **Catch**: `FAILED` usually means bad format or wrong sample rate
  - Read `FailureReason`
  - Convert audio, set `MediaFormat`
