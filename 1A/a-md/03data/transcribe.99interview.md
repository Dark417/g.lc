# transcribe Interview

> Interview questions on Amazon Transcribe, with Level 4 (L4) answers and Level 5 (L5) extras.

## Index

- [1. Core Questions](#1-core-questions)
  - [Q1 Batch Vs Streaming](#q1-batch-vs-streaming)
  - [Q2 Domain Term Accuracy](#q2-domain-term-accuracy)
  - [Q3 Diarization Vs Channel Identification](#q3-diarization-vs-channel-identification)
  - [Q4 Personally Identifiable Information (PII) Redaction Cost](#q4-personally-identifiable-information-pii-redaction-cost)
  - [Q5 Feeding A Transcript To A Large Language Model (LLM)](#q5-feeding-a-transcript-to-a-large-language-model-llm)
- [2. L5-Only Questions](#2-l5-only-questions)
  - [Q6 Call Analytics At 100k Calls A Day](#q6-call-analytics-at-100k-calls-a-day)
  - [Q7 Whisper Over Transcribe](#q7-whisper-over-transcribe)

## 1. Core Questions

Each answer gives the L4 baseline, then what L5 adds.

### Q1 Batch Vs Streaming

**Q:** Batch vs streaming transcription?

**L4 answer**

- Batch: file in Simple Storage Service (S3), async, most features
- Streaming: live audio, partial results, fewer features

**L5 extra**

- Streaming trades accuracy and features for latency
- Choose by user-visible latency requirement

### Q2 Domain Term Accuracy

**Q:** How do you improve accuracy for domain terms?

**L4 answer**

- Custom vocabulary
- Custom language model if needed

**L5 extra**

- Measure Word Error Rate (WER) before and after on a golden set
- Vocabulary is cheap and reversible
- Custom Language Model (CLM) needs training data

### Q3 Diarization Vs Channel Identification

**Q:** Diarization vs channel identification?

**L4 answer**

- Diarization separates speakers in one channel
- Channel identification (ID) uses stereo channels

**L5 extra**

- Channel ID is deterministic
- Diarization is a model and degrades with overlapping speech
- They are mutually exclusive

### Q4 Personally Identifiable Information (PII) Redaction Cost

**Q:** How does PII redaction work and what does it cost you?

**L4 answer**

- `ContentRedaction` with entity types
- Produces a redacted transcript; optionally the original too

**L5 extra**

- Text-only: audio keeps the PII ⇒ lifecycle the audio too
- Dual output doubles the sensitive store

### Q5 Feeding A Transcript To A Large Language Model (LLM)

**Q:** How do you feed a transcript to an LLM?

**L4 answer**

- Parse turns
- Redact
- Summarize with `converse`

**L5 extra**

- Window long calls and reduce
- Keep timestamps as citation metadata

## 2. L5-Only Questions

These test design ownership and scale.

### Q6 Call Analytics At 100k Calls A Day

**Q:** Design call-recording analytics for 100k calls a day.

**L5 answer**

→ S3 event → queue → worker submits jobs with deterministic names  
→ EventBridge on completion → parse → LLM summary → store

- Throttle to quota
- Dead-Letter Queue (DLQ) failed jobs
- Per-call cost metric
- Redact before analytics
- Raw audio and transcript in a restricted bucket with lifecycle

### Q7 Whisper Over Transcribe

**Q:** When would you pick Whisper over Transcribe?

**L5 answer**

- Unsupported language or a domain needing fine-tuned weights
- Volume high enough that Graphics Processing Unit (GPU) hours beat per-minute pricing
- You then own
  - Redaction
  - Diarization (extra models)
  - Scaling and monitoring
