# converse Bedrock Converse Application Programming Interface (API)

> One model-agnostic chat Application Programming Interface (API) over many Bedrock models; history, tools, and retries stay your job.

## Index

- [1. Source And Scope](#1-source-and-scope)
- [2. One-Minute Version](#2-one-minute-version)
- [3. File Index](#3-file-index)
- [4. Code Map](#4-code-map)
- [5. Gaps](#5-gaps)
- [References](#references)

---

## 1. Source And Scope

This component covers the Bedrock runtime chat path end to end.

- Lectures: AIP-C01 #7–#10, #22 (slides p.17–24, 52–53)
- Scope: Python + Java + Terraform
- Terraform: `terraform/modules/01bedrock_01converse/`
  - App-role policy for invoke + list
  - Embedding-model invoke for [embeddings](../02rag/embeddings.00index.md)
  - Application inference profile `a-app-profile`
- Code
  - Python: `app/{config,api,domain,infra,service}/_01bedrock_01converse.py`
  - Java: `com/lc/a/{config,api,domain,infra,service}/_01bedrock_01converse/`
- Numbers: Amazon Bedrock User Guide and API Reference, read 2026-11
  - Unless marked "order of magnitude"

## 2. One-Minute Version

Bedrock is a managed gateway; Converse is its uniform chat envelope.

- What
  - **Bedrock**: a managed gateway to many foundation models behind one Amazon Web Services (AWS) API
    - Anthropic, Amazon Nova, Meta, Mistral, ...
  - **Converse**: the model-agnostic chat API on the `bedrock-runtime` endpoint
- Why
  - One request shape for every chat model
    - `messages`, `system`, `inferenceConfig`, `toolConfig`
  - Identity and Access Management (IAM), Virtual Private Cloud (VPC) endpoints, CloudTrail, Key Management Service (KMS), and quotas come from AWS
    - Not from a vendor key
- How

→ pick a model Identifier (ID) or an inference profile ID (`us.anthropic...`)  
→ send `messages` (role + content blocks) + `system` + `inferenceConfig`  
→ read `output.message`, `stopReason`, `usage` (tokens), `metrics.latencyMs`  
→ on `stopReason = tool_use`: run the tool, send back a `toolResult`, call again

- Catch
  - Converse normalizes the envelope, not the model
    - Prompts, quality, and limits still differ per model
    - Provider-only features go through `additionalModelRequestFields` or `InvokeModel`
  - The service is stateless: you resend the whole history every turn

  ⇒ cost and latency grow with conversation length

  - On-demand calls throttle (`ThrottlingException`) at account quotas
    - Quotas are per model per Region
- 🗣 "Converse is a uniform envelope over many models; the history, the tools, and the retries are still your job."
- 🗣 "The tool-use loop is just: model asks, you execute, you answer with the same toolUseId."
- 🗣 "Throttling is a capacity signal: retry with jitter, then add an inference profile or provisioned throughput."

## 3. File Index

Read top to bottom: foundations, then the call, then the edges.

- Foundations
  - [01 Why, picture, control vs data plane](converse.01why-and-planes.md)
  - [02 Model access, model IDs, inference profiles](converse.02model-ids.md)
  - [03 InvokeModel vs Converse](converse.03invoke-vs-converse.md)
- The call
  - [04 Converse request and response, prompt caching](converse.04request-response.md)
  - [05 Conversation state on a stateless API](converse.05conversation-state.md)
  - [06 ConverseStream events](converse.06stream.md)
  - [07 Tool use loop](converse.07tool-use.md)
  - [08 Multimodal content blocks](converse.08multimodal.md)
- Running it
  - [09 Throttling, errors, retries](converse.09errors-retries.md)
  - [10 Throughput modes](converse.10throughput.md)
- Decide and defend
  - [98 Trade-offs: when to use, knobs, comparison, failure modes](converse.98tradeoffs.md)
  - [99 Interview questions](converse.99interview.md)

## 4. Code Map

Python is the code shown in these docs; Java paths are listed for orientation only.

| Concept file | Python (`app/`) | Java (`com/lc/a/`) |
|---|---|---|
| 01 clients | `infra/_01bedrock_01converse.py` `ConverseShowcase.runtime` / `.control` | `config/_01bedrock_01converse/ConverseConfig` `bedrockRuntimeClient`, `bedrockRuntimeAsyncClient` |
| 02 list models | `infra/…` `ConverseShowcase.list_foundation_models` | — |
| 02 list profiles | `infra/…` `ConverseShowcase.list_inference_profiles` | — |
| 02 app profile | `infra/…` `ConverseShowcase.converse_via_app_profile` | — |
| 03 InvokeModel | `infra/…` `ConverseShowcase.invoke_model_anthropic` | — |

| Concept file | Python (`app/`) | Java (`com/lc/a/`) |
|---|---|---|
| 04 basic call | `infra/…` `ConverseShowcase.converse_basic` | `service/_01bedrock_01converse/ConverseService.converse` |
| 04 parsing | `infra/…` `parse_converse_response` → `domain/…` `ConverseResult` | `service/…/ConverseService.toResult` |
| 04 caching | `infra/…` `ConverseShowcase.converse_cached_system` | — |
| 05 multi-turn | `service/…` `ChatService.send`, `domain/…` `ConversationStore`, `infra/…` `InMemoryConversationStore` | — |
| 06 stream | `infra/…` `ConverseShowcase.converse_stream` → `domain/…` `StreamEvent` | `service/…/ConverseService.converseStream` |

| Concept file | Python (`app/`) | Java (`com/lc/a/`) |
|---|---|---|
| 07 tool loop | `infra/…` `ConverseShowcase.converse_with_tools`, `service/…` `DEMO_TOOLS` | `service/…/ConverseService.converseWithTools`, `DemoTools` |
| 08 image | `infra/…` `ConverseShowcase.converse_image` | — |
| 08 document | `infra/…` `ConverseShowcase.converse_document`, `domain/…` `safe_document_name` | — |
| 09 retry | `infra/…` `ConverseShowcase.converse_with_retry`, `is_retryable` | `service/…/ConverseService.isRetryable` + `shared/Retry` |
| Representational State Transfer (REST) (+ Server-Sent Events (SSE)) | `api/_01bedrock_01converse.py` `router` (`/converse`) | `api/_01bedrock_01converse/ConverseController` (`/converse`, SSE `/converse/stream`) |

- `…` = the same component module, e.g. `infra/_01bedrock_01converse.py`.

## 5. Gaps

These topics are documented but not coded.

- `InvokeModelWithResponseStream` (native streaming)
- Batch inference jobs (`CreateModelInvocationJob`)
- Video and Simple Storage Service (S3)-sourced media blocks
- `CountTokens`, service tiers, latency-optimized inference
- DynamoDB `ConversationStore` adapter
  - Only the port + in-memory adapter exist
- Guardrails in Converse → [guardrails](../04safety/guardrails.00index.md)

## References

- [aws-samples/amazon-bedrock-samples](https://github.com/aws-samples/amazon-bedrock-samples) — Converse, tool use, multimodal notebooks
- [Amazon Bedrock User Guide: Carry out a conversation with the Converse API operations](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html)
- [Amazon Bedrock User Guide: Supported models and model features](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference-supported-models-features.html)
- [Amazon Bedrock User Guide: Increase throughput with cross-Region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html)
- [Amazon Bedrock API Reference: Converse](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html)
