# 01bedrock.01converse Trade-offs

> When to use Converse, the knobs that matter, how it compares, and how it fails.

## Index

- [1. When To Use / Not](#1-when-to-use--not)
- [2. Knobs And Best Practices](#2-knobs-and-best-practices)
  - [2.1 Model Choice](#21-model-choice)
  - [2.2 inferenceConfig](#22-inferenceconfig)
  - [2.3 Conversation State](#23-conversation-state)
  - [2.4 Tools And Streaming](#24-tools-and-streaming)
  - [2.5 Cost, Reliability, Security](#25-cost-reliability-security)
- [3. Comparison](#3-comparison)
- [4. Failure Modes](#4-failure-modes)

Back to [00index](01bedrock.01converse.00index.md).

---

## 1. When To Use / Not

Converse is the default; three other paths cover its gaps.

- Use Converse when
  - Chat, extraction, tool use, image or document Question and Answer (Q&A) on Bedrock models
  - You may swap models later without rewriting parsing
    - A/B, cost cascades
  - You need guardrails, prompt caching, or managed prompts in one call
    - Managed prompts: [01bedrock.03prompt-management](01bedrock.03prompt-management.00index.md)
- Use InvokeModel when
  - Embeddings ([02rag.01embeddings](../02rag/02rag.01embeddings.00index.md)), image generation, rerank
  - A provider feature is not in Converse yet
  - You already have native-format prompts and want byte-exact control
- Use batch inference when
  - Offline bulk jobs (millions of records), no user waiting
- Avoid Bedrock entirely when
  - The model is not on Bedrock and you need Graphics Processing Unit (GPU) control
    - ⇒ SageMaker endpoint or self-hosted vLLM
  - You need a vendor feature on day one
    - ⇒ the vendor Application Programming Interface (API) directly (with its compliance trade-offs)

## 2. Knobs And Best Practices

Each rule names the failure it prevents.

### 2.1 Model Choice

- Config, never code: model Identifier (ID) from env
  - `A_CONVERSE_MODEL_ID` (Python), `a.models.text` (Java)
  - Prevents: redeploying to switch models
- Prefer an inference profile ID for production traffic
  - Prevents: single-Region throttling
- Use an application inference profile per app or tenant
  - Prevents: unattributable Bedrock spend

### 2.2 inferenceConfig

- `maxTokens` sized to the task
  - Classification: tens
  - Answers: hundreds to low thousands
  - Prevents: early throttling and runaway cost
- `temperature` 0–0.3 for extraction and tools
  - Higher for creative text
- `stopSequences` to cut known trailers

### 2.3 Conversation State

- Store history behind a port (`ConversationStore`)
  - DynamoDB in production
- Trim by message count or token budget
  - Keep the first `user` message valid
  - Prevents: `ValidationException` on role order and context-window errors
- Summarize old turns once history exceeds a budget
- Detail: [05 conversation state](01bedrock.01converse.05conversation-state.md)

### 2.4 Tools And Streaming

- Tools
  - Short, precise `description`s and tight schemas (`required`, `enum`)
  - Validate `input` before executing
  - Return errors as `toolResult` with `status: error`
  - Cap rounds (5 here)
- Streaming
  - Stream every user-facing answer
  - Handle `messageStop` and `metadata` separately: usage arrives last

### 2.5 Cost, Reliability, Security

- Cost
  - `cachePoint` after a long stable system prompt or document
  - Log `usage` and `latencyMs` per call
    - [05ops.01observability](../05ops/05ops.01observability.00index.md) adds CloudWatch metrics
  - Small model first; escalate to a larger one only when needed (cascade)
- Reliability
  - Adaptive Software Development Kit (SDK) retries + app-level backoff with a cap
  - Timeouts: read timeout ≥ longest expected generation, or stream
    - 60 s in `app.shared.aws`
- Security
  - Virtual Private Cloud (VPC) endpoint for `bedrock-runtime` ([base_network](../../terraform/modules/base_network/main.tf))
  - Identity and Access Management (IAM) scoped to model Amazon Resource Names (ARNs) (component Terraform)
  - Never put secrets or raw Personally Identifiable Information (PII) in prompts without guardrails
    - [04safety.01guardrails](../04safety/04safety.01guardrails.00index.md), [04safety.02pii-redaction](../04safety/04safety.02pii-redaction.00index.md)

## 3. Comparison

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| Bedrock Converse | Unified chat API over Bedrock models | One shape for many models; tools, docs, images, guardrails, caching; Amazon Web Services (AWS) IAM/VPC/audit | Lowest common denominator; new provider features may lag | Default for chat and tool use on AWS |
| Bedrock InvokeModel | Provider-native JavaScript Object Notation (JSON) through Bedrock | Every provider feature Bedrock exposes; embeddings and images | Per-provider parsing; swapping models = rewrite | Embeddings, image gen, native-only features |
| OpenAI-compatible endpoints (Bedrock's Chat Completions-compatible API, LiteLLM, gateways) | OpenAI request shape in front of many models | Reuse OpenAI SDK code; easy multi-cloud | Mapping gaps (tools, multimodal, caching); support varies per model | Porting an OpenAI-based app; multi-provider gateway |
| Direct vendor API (Anthropic, OpenAI) | The model maker's own endpoint | Newest features first; vendor docs match 1:1 | Separate keys, billing, network path, data terms; no AWS IAM | Feature needed now; not bound to AWS compliance |

- Deciding variable: do you need AWS-native governance more than day-one vendor features?
  - Governance = IAM, VPC, CloudTrail, one bill
- Pick: Converse, unless
  - you need embeddings / image generation / a native-only feature → InvokeModel
  - a feature is not yet on Bedrock → the vendor API

## 4. Failure Modes

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Throttling | Requests Per Minute (RPM)/TPM quota per model per Region | `ThrottlingException`; CloudWatch `InvocationThrottles` | Backoff + jitter; cross-Region profile; smaller `maxTokens`; quota increase; provisioned throughput |
| Truncated answer | `maxTokens` too low | `stopReason = max_tokens` | Raise cap; ask for shorter output; continue in a new turn |
| Role-order error | History starts with `assistant` or repeats a role | `ValidationException` | Trim history in pairs; merge consecutive same-role turns |
| Tool loop never ends | Model keeps calling tools | Round counter hits the cap | Cap rounds; better tool descriptions; return clear errors |
| Bad tool input | Model invents fields or types | Schema validation fails | Validate, return `status: error`, let the model retry once |
| Mid-stream failure | Error event after 200 OK | Exception while iterating the stream | Treat partial output as failed; retry whole call or tell the user |

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Model unavailable | Bare model ID that needs a profile; legacy model | `ValidationException` / `ResourceNotFoundException` | Use the profile ID; track `modelLifecycle` |
| Access denied | IAM missing profile or destination-Region model ARN | `AccessDeniedException` | Grant profile ARN + `foundation-model` ARNs in all profile Regions |
| Context overflow | History or document too large | `stopReason = model_context_window_exceeded` or `ValidationException` | Trim, summarize, retrieve (Retrieval-Augmented Generation (RAG)) instead of stuffing |
| Cost blow-up | Resending long history every turn | `usage.inputTokens` grows per turn | `cachePoint`; summarize; shorter system prompt |
| Timeout | Long generation on sync call | `ModelTimeoutException` / read timeout | Stream; lower `maxTokens`; raise read timeout |
