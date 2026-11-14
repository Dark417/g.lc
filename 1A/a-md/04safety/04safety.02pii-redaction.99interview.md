# 04safety.02pii-redaction.99interview Personally Identifiable Information (PII) Redaction Interview Questions

> Level 4 (L4) + Level 5 (L5) answers on where to redact, how to apply offsets, streaming, tokenization, tool choice, and thresholds.

## Index

- [1. Core Questions](#1-core-questions)
  - [1.1 Where to Redact in Retrieval-Augmented Generation (RAG)](#11-where-to-redact-in-retrieval-augmented-generation-rag)
  - [1.2 Right-to-Left](#12-right-to-left)
  - [1.3 Streaming Redaction](#13-streaming-redaction)
  - [1.4 Masking vs Tokenization](#14-masking-vs-tokenization)
  - [1.5 Comprehend vs Guardrails](#15-comprehend-vs-guardrails)
  - [1.6 Confidence Threshold](#16-confidence-threshold)
- [2. L5-Only Questions](#2-l5-only-questions)
  - [2.1 Call-Center Assistant](#21-call-center-assistant)
  - [2.2 Proving No PII Reached the Provider](#22-proving-no-pii-reached-the-provider)

Back to [00index](04safety.02pii-redaction.00index.md).

## 1. Core Questions

Each question has a bounded L4 answer and an L5 extension.

### 1.1 Where to Redact in Retrieval-Augmented Generation (RAG)

**Q:** Where in a RAG system do you redact Personally Identifiable Information (PII)?

**L4 answer**

- Before indexing: scrub source documents (async job or detect + apply)
- On the request: redact the user prompt before the model and logs
- On the response: guardrail output check

**L5 extra**

- Each place a copy is made is a boundary
  - index, prompt logs, provider, cache, analytics
- Pre-index redaction must use REPLACE (type tags) to keep retrieval quality
- If answers need real values
  - keep pseudonyms in the index
  - detokenize at the edge for authorized users

See [01why-picture](04safety.02pii-redaction.01why-picture.md).

### 1.2 Right-to-Left

**Q:** Why apply redactions right-to-left?

**L4 answer**

- Offsets refer to the original string
- Replacing an early span shifts later offsets

**L5 extra**

- Also resolve overlapping entities first (keep higher score / longer span)
- Offsets are character offsets
  - test with multi-byte text
  - mismatched units corrupt text silently

See [04redaction-rules](04safety.02pii-redaction.04redaction-rules.md).

### 1.3 Streaming Redaction

**Q:** How do you redact a streaming answer?

**L4 answer**

- Buffer chunks
- Emit only text that is safely before any possible entity
- Hold a tail window

**L5 extra**

- Window size = longest entity you care about + margin
  - never cut inside a detected entity
- Each flush costs a detect call ⇒ batch by size, not per token
- On Bedrock, guardrail sync mode does this for you
  - async mode skips masking

See [05streaming](04safety.02pii-redaction.05streaming.md).

### 1.4 Masking vs Tokenization

**Q:** Masking vs tokenization — when each?

**L4 answer**

- Masking is irreversible: logs, analytics, model input
- Tokenization keeps a mapping in a vault so authorized code can restore values

**L5 extra**

- Deterministic tokens enable joins but are linkable; random tokens are not
- Keyed Hash-Based Message Authentication Code (HMAC) prevents dictionary attacks on low-entropy ids
- Vault becomes the high-value target
  - separate account
  - audited detokenize

See [06pseudonymization](04safety.02pii-redaction.06pseudonymization.md).

### 1.5 Comprehend vs Guardrails

**Q:** Comprehend vs Guardrails for PII?

**L4 answer**

- Comprehend gives offsets and scores, so you write the policy
- Guardrails masks or blocks inside the model call, plus other safety policies

**L5 extra**

- Use both
  - Comprehend on input for pseudonymization and logs
  - Guardrails on output as the net
- Guardrails regex covers internal ids
  - Comprehend has no custom regex ⇒ add your own regex pass

See [02toolbox](04safety.02pii-redaction.02toolbox.md).

### 1.6 Confidence Threshold

**Q:** How do you choose the confidence threshold?

**L4 answer**

- Labeled sample of real text
- Measure recall and precision per type at several thresholds

**L5 extra**

- Asymmetric costs: a missed Social Security Number (SSN) is worse than a masked month
  - per-type thresholds
- Re-tune when input distribution changes (new product, new language)

## 2. L5-Only Questions

Depth, scale, and design ownership.

### 2.1 Call-Center Assistant

**Q:** Design PII handling for a call-center Generative Artificial Intelligence (GenAI) assistant (audio → summary → Customer Relationship Management (CRM)).

→ Transcribe with `ContentRedaction` (`redacted` only unless a regulated process needs both).  
→ Comprehend detect on the transcript for types Transcribe does not cover; pseudonymize customer ids.  
→ Bedrock summary with guardrail (PII ANONYMIZE + grounding on the transcript).  
→ Detokenize only the CRM fields that need real values, in the CRM write path.

- Logs: types + counts
- Macie on the transcript buckets
- Retention limits per bucket

### 2.2 Proving No PII Reached the Provider

**Q:** A regulator asks you to prove no PII reached the model provider. What evidence do you have?

- Redaction is before the call
  - enforced in one shared library or gateway
- Invocation logs contain only redacted prompts
  - sampled audits with canary PII strings
- Detection recall measured per type on a labeled set
  - with the threshold history
- Gaps to admit
  - Machine Learning (ML) recall < 100%
  - so the claim is "reduced", not "none"
