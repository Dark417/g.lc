# 03data.03transcribe Tradeoffs

> When Transcribe is the right ear, the knobs that keep it safe and cheap, how it compares, and how it fails.

## Index

- [1. When To Use / Not](#1-when-to-use--not)
- [2. Knobs And Best Practices](#2-knobs-and-best-practices)
- [3. Comparison](#3-comparison)
- [4. Failure Modes](#4-failure-modes)

## 1. When To Use / Not

Transcribe fits audio you must search, summarize or analyze on Amazon Web Services (AWS) with Personally Identifiable Information (PII) controls.

- **Use**
  - Audio you must search, summarize or analyze
  - On AWS, with PII controls
- **Don't use**
  - Need custom model weights or unusual languages ⇒ Whisper on SageMaker
  - Real-time voice conversation ⇒ speech-to-speech (Nova Sonic) or streaming

## 2. Knobs And Best Practices

Each rule names the failure it prevents.

- **Deterministic job name** = hash of media Uniform Resource Identifier (URI) + settings
  - Retries are idempotent
- **Own the output**: `OutputBucketName` + `OutputKey` + a Customer Managed Key (CMK)
  - Otherwise Transcribe uses a service-owned location with a temporary Uniform Resource Locator (URL)
- **Poll with backoff** (jobs take minutes)
  - Or use EventBridge on job state change
- **Vocabulary first** (hours of work saved)
  - Custom Language Model (CLM) only when measured Word Error Rate (WER) stays high
- **Stereo calls** ⇒ channel identification, not diarization
- **Redact before logging**
  - Keep unredacted output access-controlled
- **Keep the job lifecycle**
  - Delete old jobs (retention in the console list is limited)
  - Lifecycle the Simple Storage Service (S3) prefix

## 3. Comparison

The deciding variable is language coverage and who runs the infrastructure.

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| Amazon Transcribe | Managed Automatic Speech Recognition (ASR) | No ops; redaction, diarization, vocab | Language/feature gaps; per-minute price | AWS pipeline, PII needs |
| Whisper on SageMaker | Open model on your endpoint | Many languages; full control | You run Graphics Processing Units (GPUs), scaling, redaction | Unsupported languages, offline |
| Google/Azure speech | Other clouds | Strong models | Cross-cloud data movement | Already on that cloud |
| Prompt a multimodal model with audio | Large Language Model (LLM) reads audio directly | One call for transcript + task | Less control, cost, length limits | Short clips, prototypes |

Pick: Transcribe for AWS workloads, unless the language is unsupported (Whisper) or you need model control.

## 4. Failure Modes

Request errors fail loudly; PII leaks and duplicate cost fail quietly.

**Request and job errors**

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| `ConflictException` | Job name reused | Application Programming Interface (API) error | Deterministic name + get the existing job |
| Job FAILED | Bad format, wrong sample rate | `FailureReason` | Convert audio, set `MediaFormat` |
| `BadRequest` on settings | Diarization + channel identification (ID) together | API error | Pick one |
| Output unreadable | S3/Key Management Service (KMS) permission for the caller | AccessDenied | Allow `s3:PutObject`, KMS data key |
| Vocabulary not ready | State PENDING/FAILED | `GetVocabulary` | Wait for READY; fix phrase format |

**Quiet failures**

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| PII leaks into the summary | Raw transcript sent to the LLM | Review | Redact first, summarize redacted |
| Cost surprise | Re-transcribing duplicates | Billing | Idempotent names, dedup by hash |
