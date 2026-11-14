# 01bedrock.03prompt-management Why It Was Created

> The pain of prompts as string literals, what Prompt Management adds, and how the pieces fit.

## Index

- [1. Why It Was Created](#1-why-it-was-created)
  - [1.1 The Pain Before](#11-the-pain-before)
  - [1.2 Prompt Management](#12-prompt-management)
  - [1.3 Common Use Cases](#13-common-use-cases)
- [2. Picture](#2-picture)
- [3. Two Clients](#3-two-clients)

Back to [00index](01bedrock.03prompt-management.00index.md).

---

## 1. Why It Was Created

Prompt Management turned prompts from code literals into governed resources.

### 1.1 The Pain Before

- Prompts as string literals in code

  ⇒ every wording change is a code deploy

- No history of which prompt produced which output
- Product and domain experts could not edit prompts safely

### 1.2 Prompt Management

- General Availability (GA) 2024-11
- Prompts as first-class resources
  - versions
  - tags
  - Identity and Access Management (IAM)
- Runs directly in
  - Converse ([01bedrock.01converse](01bedrock.01converse.00index.md))
  - Agents
  - Flows ([01bedrock.04prompt-flows](01bedrock.04prompt-flows.00index.md) prompt node)

### 1.3 Common Use Cases

- Shared prompt library across teams
  - summarize, classify, extract
- Safe rollout and rollback of prompt changes
- Comparing variants in the console
  - model A vs model B
  - wording A vs B

## 2. Picture

One prompt holds variants in DRAFT; versions freeze it; config points at a version.

```text
prompt a-prompt  (arn:...:prompt/ABCDE12345)
  DRAFT  ── editable
  │  variant "default"  TEXT "Summarize {{topic}} for {{audience}} ..."  model + inferenceConfig
  │  variant "concise"  TEXT "In 3 bullets, summarize {{topic}} ..."     (compare in console)
  │
  ├── CreatePromptVersion → version 1  arn:...:prompt/ABCDE12345:1   (immutable snapshot)
  └── CreatePromptVersion → version 2  arn:...:prompt/ABCDE12345:2

app config: A_PROMPTS_PROMPT_ARN=arn:...:prompt/ABCDE12345:2
   → Converse(modelId=<that ARN>, promptVariables={topic: {text: ...}, audience: {text: ...}})
   → Bedrock renders the default variant, calls its model with its inference config
```

- Notice: the app holds only an Amazon Resource Name (ARN); model and settings come from the prompt.

## 3. Two Clients

- Prompts are managed on `bedrock-agent`.
  - The control plane for prompts, flows, agents, knowledge bases.
- Prompts run on `bedrock-runtime`.
- No Amazon Web Services (AWS) call at import time.

```python
# app/infra/_01bedrock_03prompt_management.py
class PromptManagementShowcase:
    def __init__(self, settings: PromptsSettings | None = None) -> None:
        self.settings = settings or get_prompts_settings()

    @property
    def agent(self) -> Any:
        """Control plane for prompts, flows, agents, knowledge bases."""
        return aws.client("bedrock-agent")

    @property
    def runtime(self) -> Any:
        return aws.client("bedrock-runtime")  # Converse with a prompt ARN
```

- Catch: two endpoints need two sets of IAM actions.
  - See [04 running](01bedrock.03prompt-management.04running.md#2-option-a-converse-with-the-prompt-arn) for the runtime permissions.
