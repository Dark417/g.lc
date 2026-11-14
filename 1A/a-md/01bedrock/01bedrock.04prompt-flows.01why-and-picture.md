# 01bedrock.04prompt-flows Why Flows And Picture

> Why managed prompt chains exist, where they show up, and how the demo flow moves data.

## Index

- [1. Why It Was Created](#1-why-it-was-created)
  - [1.1 The Pain Before](#11-the-pain-before)
  - [1.2 Flows](#12-flows)
  - [1.3 Common Use Cases](#13-common-use-cases)
- [2. Picture](#2-picture)
- [3. Two Clients](#3-two-clients)

Back to [00index](01bedrock.04prompt-flows.00index.md).

---

## 1. Why It Was Created

Flows replaced per-team glue code for multi-step Generative Artificial Intelligence (GenAI) tasks.

### 1.1 The Pain Before

- Multi-step GenAI tasks lived in ad-hoc glue code
  - classify → retrieve → answer → format
- Each team re-wrote
  - retries
  - prompt wiring
  - versioning

### 1.2 Flows

- **Flows** (General Availability (GA) 2024-11, formerly "Prompt Flows")
  - Visual builder + Application Programming Interface (API) for prompt chains
  - Branching and Amazon Web Services (AWS) integrations

### 1.3 Common Use Cases

- Route a request by intent to different prompts
  - Condition node
- Retrieval-Augmented Generation (RAG) pipeline
  - KnowledgeBase node → Prompt node → Output
- Document processing
  - Lambda pre-processing → Prompt extraction → Simple Storage Service (S3) Storage node

## 2. Picture

The demo flow `a-flow` is Input → Prompt → Output.

```text
InvokeFlow(alias)
   │ inputs: [{nodeName: FlowInput, nodeOutputName: document,
   │           content: {document: "..."}}]
   ▼
┌───────────┐ document  ┌────────────────────────┐ modelCompletion ┌────────────┐
│ FlowInput │──────────►│ Summarize (Prompt)     │────────────────►│ FlowOutput │──► flowOutputEvent
│  (Input)  │  →topic   │ inline TEXT template   │   →document     │  (Output)  │──► flowCompletionEvent
└───────────┘           │ model + inferenceConfig│                 └────────────┘
                        └────────────────────────┘
                 runs as the flow execution role (a-flow-role): InvokeModel
```

- Notice: each arrow maps a named output to a named input.

## 3. Two Clients

- Flows are built on `bedrock-agent` (control plane).
- Flows run on `bedrock-agent-runtime` (data plane).
- Clients are lazy: no AWS call at import time.

```python
# app/infra/_01bedrock_04prompt_flows.py
class FlowsShowcase:
    def __init__(self, settings: FlowsSettings | None = None) -> None:
        self.settings = settings or get_flows_settings()

    @property
    def agent(self) -> Any:
        return aws.client("bedrock-agent")  # build: validate, create, prepare, version, alias

    @property
    def agent_runtime(self) -> Any:
        return aws.client("bedrock-agent-runtime")  # run: InvokeFlow
```

- Catch: Terraform owns `a-flow`.
  - `create_flow` in code only shows the same definition.
