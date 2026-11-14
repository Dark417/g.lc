# 03data.03transcribe Amazon Transcribe

> Managed speech-to-text: audio in Simple Storage Service (S3) → redacted JavaScript Object Notation (JSON) transcript → Large Language Model (LLM) summary.

## Index

- [1. Source And Scope](#1-source-and-scope)
- [2. One-Minute Version](#2-one-minute-version)
- [3. Component Map](#3-component-map)
  - Concepts
    - [01 Why And Flow](03data.03transcribe.01why-and-flow.md): pain, picture, batch vs streaming, Call Analytics, idempotent jobs
    - [02 Accuracy Knobs](03data.03transcribe.02accuracy-knobs.md): custom vocabulary, vocabulary filter, language identification (ID)
    - [03 Who Spoke](03data.03transcribe.03who-spoke.md): speaker diarization vs channel identification
    - [04 Personally Identifiable Information (PII) Redaction](03data.03transcribe.04pii-redaction.md): `ContentRedaction`, dual output
    - [05 Output JSON](03data.03transcribe.05output-json.md): transcript shape, parsing turns
    - [06 Generative Artificial Intelligence (GenAI) Input](03data.03transcribe.06genai-input.md): render turns, summarize with Converse
  - Decide and defend
    - [98 Tradeoffs](03data.03transcribe.98tradeoffs.md): when to use, knobs, comparison, failure modes
    - [99 Interview](03data.03transcribe.99interview.md): Level 4 (L4) + Level 5 (L5) questions
- [4. Code Map](#4-code-map)
- [References](#references)

## 1. Source And Scope

Lectures AIP-C01 #47–#48 (slides p.111–113).

- **Scope**: Python + Terraform
- **Terraform**: [modules/03data_03transcribe](../../terraform/modules/03data_03transcribe/main.tf)
  - Custom vocabulary `a-vocab`
  - Vocabulary filter `a-filter`
  - App policy
- **Code**: Python layers `app/*/_03data_03transcribe.py` (slice `transcribe`)
- **Numbers**: Amazon Transcribe Developer Guide, read 2026-11
  - "Check the quota page" where unsure

## 2. One-Minute Version

Transcribe is the ear of a GenAI pipeline: audio to JSON, then an LLM does the thinking.

- **What**
  - Managed speech-to-text: audio in, JSON transcript out
  - Batch: file in S3
  - Streaming: WebSocket / HTTP2, live audio
- **Why**
  - Audio is the biggest unstructured source nobody can search or summarize
  - A transcript turns calls and meetings into text an LLM can use
- **How**
  - `StartTranscriptionJob` with an S3 media Uniform Resource Identifier (URI), a language (or language ID), and Settings
  - Poll `GetTranscriptionJob` until COMPLETED
  - The transcript JSON lands in S3
  - Add-ons
    - Custom vocabulary (domain terms)
    - Vocabulary filter (mask / remove / tag words)
    - Speaker diarization, channel identification
    - PII redaction
  - Then summarize with Bedrock `converse`
- **Catch**
  - Job names are unique per account and Region ⇒ idempotent naming needed
  - Speaker labels and channel identification are mutually exclusive
  - Language support differs per feature (redaction, diarization, streaming)
    - Check the supported-languages page
  - Redaction only changes the text; audio is untouched
- 🗣 "Transcribe is the ear of a GenAI pipeline: audio to JSON, then an LLM does the thinking."
- 🗣 "Name jobs deterministically so a retry does not create a second job."
- 🗣 "Redact before the transcript reaches the model or the log."

## 3. Component Map

The files follow one job from submit to summary.

```text
 01 why-and-flow ─► 02 accuracy-knobs ─► 03 who-spoke ─► 04 pii-redaction
                                                              │
                         06 genai-input ◄── 05 output-json ◄──┘
 98 tradeoffs · 99 interview  (decide and defend)
```

Files 02–04 are all `start_job` settings; 05–06 consume the output.

## 4. Code Map

Every concept file maps to one Python function in the new layer-first layout.

| Concept file | Python path | Function |
|---|---|---|
| 01 deterministic job name | `app/infra/_03data_03transcribe.py` | `job_name_for` |
| 02–04 start job (settings, redaction, output) | `app/infra/_03data_03transcribe.py` | `start_job` |
| 01 poll with backoff | `app/infra/_03data_03transcribe.py` | `wait_for_job` |
| 05 parse items + speaker segments | `app/domain/_03data_03transcribe.py` | `parse_transcript` |
| 05 fetch transcript from S3 | `app/infra/_03data_03transcribe.py` | `read_transcript` |

| Concept file | Python path | Function |
|---|---|---|
| 06 summarize with Bedrock Converse | `app/infra/_03data_03transcribe.py` | `summarize` |
| 06 render turns for a prompt | `app/domain/_03data_03transcribe.py` | `render_turns` |
| 01 end-to-end | `app/service/_03data_03transcribe.py` | `transcribe_and_summarize` |
| 01 Representational State Transfer (REST) (`/transcribe`) | `app/api/_03data_03transcribe.py` | `summarize_call` |
| 02 settings (`A_TRANSCRIBE_`) | `app/config/_03data_03transcribe.py` | `TranscribeSettings` |

- **Gaps** (no repo code)
  - Streaming, Call Analytics, custom language models, subtitles, toxicity detection
  - EventBridge completion events

## References

- [aws-samples/amazon-transcribe-examples](https://github.com/aws-samples/amazon-transcribe-examples)
- [Amazon Transcribe Developer Guide](https://docs.aws.amazon.com/transcribe/latest/dg/what-is.html)
- [Transcribe: StartTranscriptionJob Application Programming Interface (API)](https://docs.aws.amazon.com/transcribe/latest/APIReference/API_StartTranscriptionJob.html)
- [Amazon Web Services (AWS) Machine Learning (ML) blog: Transcribe](https://aws.amazon.com/blogs/machine-learning/)
