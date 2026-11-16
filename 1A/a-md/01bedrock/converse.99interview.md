# converse Interview Questions

> Seven L4 + L5 questions and two L5-only design questions on the Converse Application Programming Interface (API).

## Index

- [1. Core Questions](#1-core-questions)
  - [1.1 InvokeModel vs Converse](#11-invokemodel-vs-converse)
  - [1.2 Tool-Use Round Trip](#12-tool-use-round-trip)
  - [1.3 Slow Answers](#13-slow-answers)
  - [1.4 Throttling At Peak](#14-throttling-at-peak)
  - [1.5 Inference Profiles](#15-inference-profiles)
  - [1.6 State On A Stateless API](#16-state-on-a-stateless-api)
  - [1.7 stopReason Handling](#17-stopreason-handling)
- [2. L5-Only Questions](#2-l5-only-questions)
  - [2.1 Multi-Tenant Call Path](#21-multi-tenant-call-path)
  - [2.2 Leaving Converse](#22-leaving-converse)

Back to [00index](converse.00index.md).

---

## 1. Core Questions

Each question has a bounded L4 answer and an L5 extension.

### 1.1 InvokeModel vs Converse

**Q1:** What is the difference between InvokeModel and Converse?

**L4 answer**

- InvokeModel takes and returns provider-native JavaScript Object Notation (JSON)
- Converse takes typed messages, system, inference config, and tools
  - The same for every chat model
- Converse returns `stopReason`, `usage`, and `latencyMs` in a fixed shape

**L5 extra**

- Both are authorized by `bedrock:InvokeModel`
  - Streaming by `InvokeModelWithResponseStream`
- Converse is a normalization layer
  - Provider-only knobs go through `additionalModelRequestFields`
- InvokeModel stays necessary for embeddings and image generation
- Choose Converse to keep a model swap a config change, not a code change

Study: [03 InvokeModel vs Converse](converse.03invoke-vs-converse.md)

### 1.2 Tool-Use Round Trip

**Q2:** Walk through a tool-use round trip.

**L4 answer**

- Send `toolConfig` with JSON-schema tool specs
- Model returns `stopReason = tool_use` with `toolUse` blocks
- Run the tool
- Send a user message with `toolResult` carrying the same `toolUseId`
- Call again until `end_turn`

**L5 extra**

- Append the assistant message unchanged
  - Including any text and reasoning blocks
- Answer every parallel `toolUse` in one user message
- Validate inputs and authorize per caller
  - Bedrock never executes tools
- Cap rounds
- Return errors as `status: error` so the model can recover

Study: [07 tool use](converse.07tool-use.md)

### 1.3 Slow Answers

**Q3:** Users report slow answers. What do you change?

**L4 answer**

- Switch to ConverseStream so the first tokens show immediately
- Lower `maxTokens` and shorten prompts

**L5 extra**

- Streaming cuts time to first token, not total latency or cost
- Prompt caching (`cachePoint`) cuts prefill time on long stable prefixes
- Smaller model for easy requests
- Latency-optimized inference where offered
- Measure `metrics.latencyMs` vs client time
  - Separates model time from network and retries

Study: [06 stream](converse.06stream.md), [04 prompt caching](converse.04request-response.md#3-prompt-caching)

### 1.4 Throttling At Peak

**Q4:** You get `ThrottlingException` at peak. Options?

**L4 answer**

- Retry with exponential backoff and jitter
- Request a quota increase

**L5 extra**

- Cross-Region inference profile spreads load over several Regions
  - At the same price
- Oversized `maxTokens` consumes Tokens Per Minute (TPM) quota early ⇒ right-size it
- Steady high load → provisioned throughput
- Offline load → batch
- Cap retries and shed load
  - Retries amplify a capacity problem

Study: [09 errors and retries](converse.09errors-retries.md), [10 throughput](converse.10throughput.md)

### 1.5 Inference Profiles

**Q5:** What is an inference profile, and why use an application inference profile?

**L4 answer**

- A system inference profile (`us.` prefix) routes one model across several Regions
- An application inference profile is your copy with your tags

**L5 extra**

- Identity and Access Management (IAM) must allow the profile Amazon Resource Name (ARN)
  - And the foundation model in each destination Region
- Data may be processed in any Region in the set ⇒ check residency
- Application profiles give per-app cost allocation
  - And per-app CloudWatch metrics
  - Without changing model choice

Study: [02 model Identifiers (IDs)](converse.02model-ids.md)

### 1.6 State On A Stateless API

**Q6:** How do you keep conversation state with a stateless API?

**L4 answer**

- Store messages per conversation and resend them each turn

**L5 extra**

- Store behind a port
  - DynamoDB keyed by conversation, sorted by sequence, with Time to Live (TTL)
- Trim by token budget
- Keep role alternation valid
- Summarize old turns
- Cache the stable prefix
  - Per-turn cost otherwise grows linearly with history

Study: [05 conversation state](converse.05conversation-state.md)

### 1.7 stopReason Handling

**Q7:** Which `stopReason` values must the caller handle?

**L4 answer**

- `end_turn`: done
- `tool_use`: run tools
- `max_tokens`: truncated

**L5 extra**

- `guardrail_intervened` / `content_filtered`
  - Show a safe message; don't retry blindly
- `malformed_tool_use` / `malformed_model_output`
  - Retry once, then fail
- `model_context_window_exceeded`
  - Trim or summarize, then retry

Study: [04 response fields](converse.04request-response.md#21-fields)

## 2. L5-Only Questions

These test design ownership beyond the API surface.

### 2.1 Multi-Tenant Call Path

**L5-only Q8:** Design the Bedrock call path for a multi-tenant Software as a Service (SaaS) with a 99.9% Service Level Objective (SLO).

**L5 answer**

- Config
  - Model ID and limits per tenant in config
  - An application inference profile per tenant tier for cost
- Capacity
  - Cross-Region profile for capacity
  - Provisioned throughput for the top tier
- Client
  - Adaptive retries, capped app retries
  - Circuit breaker
  - Fallback to a smaller model
- Per-tenant token budgets enforced before the call
  - TPM is shared across tenants
- Observability
  - `usage`, `latencyMs`, `stopReason`, and throttles per tenant
  - Via `requestMetadata` + invocation logs
- Trade-off: a fallback model keeps availability but changes quality
  - ⇒ needs evals ([evaluations](../04safety/evaluations.00index.md))

### 2.2 Leaving Converse

**L5-only Q9:** When would you leave Converse for a vendor API or self-hosting?

**L5 answer**

- A product-critical feature exists only in the vendor API
  - And waiting costs more than the governance gap
- The model is not on Bedrock, or you need custom kernels / Graphics Processing Unit (GPU) control
  - → SageMaker or vLLM
- Very high steady volume where owned GPUs beat per-token pricing
  - Only with an ops team
- Keep a thin internal port (`ChatModel`)
  - So the switch is an adapter change
