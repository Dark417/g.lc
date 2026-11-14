# 01bedrock.01converse Why Bedrock, Picture, Planes

> Why Bedrock and Converse exist, how a call flows, and which endpoint does what.

## Index

- [1. Why It Was Created](#1-why-it-was-created)
  - [1.1 The Pain Before](#11-the-pain-before)
  - [1.2 Bedrock, InvokeModel, Converse](#12-bedrock-invokemodel-converse)
  - [1.3 Common Use Cases](#13-common-use-cases)
- [2. Picture](#2-picture)
- [3. Control Plane vs Data Plane](#3-control-plane-vs-data-plane)
  - [3.1 Two Endpoints](#31-two-endpoints)
  - [3.2 Two Lazy Clients](#32-two-lazy-clients)

Back to [00index](01bedrock.01converse.00index.md).

---

## 1. Why It Was Created

Bedrock solved governance; Converse then solved per-vendor request shapes.

### 1.1 The Pain Before

- Each model vendor had its own Application Programming Interface (API), auth, Software Development Kit (SDK), and data-handling terms
- Enterprises needed one place for:
  - Identity and Access Management (IAM)
  - private networking
  - audit
  - billing

### 1.2 Bedrock, InvokeModel, Converse

- **Bedrock** (General Availability (GA) 2023-09)
  - Serverless model hosting
    - No Graphics Processing Units (GPUs), no endpoints to size for on-demand use
  - Prompts and outputs are not used to train the base models
    - Source: Bedrock data-protection page
- **InvokeModel** came first
  - Body = the provider's native JavaScript Object Notation (JSON)

  ⇒ switching from Claude to Nova meant rewriting request and response parsing

- **Converse** (2024-05)
  - One message format across chat models
  - Plus tool use, documents, images, guardrails

### 1.3 Common Use Cases

- Chat assistants
- Summarization, extraction, classification
- Agents that call tools (backend APIs, databases)
- Document and image Question and Answer (Q&A) (invoices, screenshots, Portable Document Format files (PDFs))

## 2. Picture

One runtime endpoint; the `modelId` decides where capacity comes from.

```text
app (IAM role a-app)
   │  SigV4 over HTTPS (VPC endpoint bedrock-runtime, base_network)
   ▼
bedrock-runtime  ── Converse / ConverseStream / InvokeModel / InvokeModelWithResponseStream
   │
   ├── modelId = foundation model      anthropic.claude-...-v1:0     (one Region)
   ├── modelId = inference profile     us.anthropic.claude-...-v1:0  (routes across US Regions)
   ├── modelId = app inference profile arn:...:application-inference-profile/xyz (cost tags)
   └── modelId = provisioned model     arn:...:provisioned-model/xyz (bought capacity)
            │
            ▼
   model provider fleet (run by AWS) → tokens back

bedrock (control plane) ── ListFoundationModels, GetFoundationModel, inference profiles,
                           customization jobs, provisioned throughput, guardrails, logging
```

- Notice: the same `Converse` call works for all four `modelId` kinds.

## 3. Control Plane vs Data Plane

Bedrock splits management and inference into separate endpoints.

### 3.1 Two Endpoints

- **`bedrock`** (control plane)
  - Manages things
    - list models, inference profiles
    - customization, provisioned throughput
    - guardrails, invocation logging
  - Low call rates
  - Used by setup code and Terraform
- **`bedrock-runtime`** (data plane)
  - Runs inference
    - `Converse`, `ConverseStream`
    - `InvokeModel`, `InvokeModelWithResponseStream`
    - `ApplyGuardrail`, `CountTokens`
  - High call rates
  - On the request path
- Separate endpoints

  ⇒ separate Virtual Private Cloud (VPC) endpoints and separate IAM actions

- Agents, knowledge bases, prompts, flows have their own pair
  - `bedrock-agent` / `bedrock-agent-runtime`

### 3.2 Two Lazy Clients

- The showcase exposes one property per plane.
- Clients come from `app.shared.aws` on first use.
  - No Amazon Web Services (AWS) call at import time.
- A shared runtime client = a shared adaptive rate limiter.

```python
# app/infra/_01bedrock_01converse.py
class ConverseShowcase:
    def __init__(self, settings: ConverseSettings | None = None) -> None:
        self.settings = settings or get_converse_settings()

    @property
    def runtime(self) -> Any:
        """Data plane: Converse, ConverseStream, InvokeModel."""
        return aws.client("bedrock-runtime")  # shared client = shared adaptive rate limiter

    @property
    def control(self) -> Any:
        """Control plane: models, inference profiles, customization, provisioned throughput."""
        return aws.client("bedrock")
```

- Catch: two endpoints need two VPC endpoints and two IAM action sets.
  - Missing one ⇒ setup works but inference fails, or the reverse.
