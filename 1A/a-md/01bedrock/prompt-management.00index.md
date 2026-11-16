# prompt-management Bedrock Prompt Management

> Store prompts as versioned Amazon Web Services (AWS) resources and run a pinned version by Amazon Resource Name (ARN).

## Index

- [1. Source And Scope](#1-source-and-scope)
- [2. One-Minute Version](#2-one-minute-version)
- [3. File Index](#3-file-index)
- [4. Code Map](#4-code-map)
- [5. Gaps](#5-gaps)
- [References](#references)

---

## 1. Source And Scope

This component covers prompts as managed, versioned Bedrock resources.

- Lectures: AIP-C01 #27 (slides p.58)
- Scope: Python + Terraform
- Terraform: `terraform/modules/01bedrock_03prompt_management/`
  - `a-prompt`: one TEXT variant, input variables, inference config
  - App policy
- Code
  - Python: `app/{config,api,domain,infra}/_01bedrock_03prompt_management.py`
- Related
  - [converse](converse.00index.md)
  - [prompt-flows](prompt-flows.00index.md)
  - [prompt-engineering](prompt-engineering.00index.md)
- Numbers: Amazon Bedrock User Guide, "Prompt management", read 2026-11
  - Unless marked "order of magnitude"

## 2. One-Minute Version

A prompt version is a deploy artifact referenced by ARN.

- What
  - **Bedrock Prompt Management** stores prompts as AWS resources
  - **Prompt** = template with `{{variables}}` + model + inference settings
    - In one or more variants
- Why
  - Prompts change more often than code
  - Treat them as reviewed, versioned, rollback-able artifacts
  - Owned by more than developers
- How

→ create the prompt (DRAFT) with variants and input variables  
→ test it, then `CreatePromptVersion` = immutable snapshot `...:prompt/ID:1`  
→ call Converse with `modelId = <prompt version ARN>` and `promptVariables`  
→ roll back = point config at the previous version ARN

- Catch
  - Converse with a prompt ARN runs the default variant only
    - It ignores your `system` / `inferenceConfig` / `toolConfig`
    - They live in the prompt
  - A/B testing variants is your code's job
    - Pick a variant, render, call
  - Another AWS dependency on the request path
    - Cache rendered templates if you render locally
- 🗣 "A prompt version is a deploy artifact: immutable, reviewed, and referenced by ARN."
- 🗣 "Pin the version ARN in config; DRAFT is for the playground, never for production."

## 3. File Index

Read top to bottom: why, the model, the lifecycle, then running it.

- Foundations
  - [01 Why it was created, picture](prompt-management.01why.md)
  - [02 Prompt, variant, template, variables](prompt-management.02variants-variables.md)
- Lifecycle and runtime
  - [03 Draft and versions](prompt-management.03draft-versions.md)
  - [04 Running a managed prompt](prompt-management.04running.md)
- Decide and defend
  - [98 Trade-offs: when to use, knobs, comparison, failure modes](prompt-management.98tradeoffs.md)
  - [99 Interview questions](prompt-management.99interview.md)

## 4. Code Map

Python only; this component has no Java code.

| Concept file | Python (`app/`) |
|---|---|
| 02 create prompt (TEXT + CHAT variants, variables, inference config) | `infra/_01bedrock_03prompt_management.py` `PromptManagementShowcase.create_prompt` |
| 02 prompt model | `domain/…` `ManagedPrompt`, `PromptVariant` |
| 03 edit DRAFT | `infra/…` `PromptManagementShowcase.update_prompt_draft` |
| 03 immutable version (idempotent `clientToken`) | `infra/…` `PromptManagementShowcase.create_prompt_version` |
| 03 get DRAFT or a version | `infra/…` `PromptManagementShowcase.get_prompt` → `domain/…` `ManagedPrompt` |

| Concept file | Python (`app/`) |
|---|---|
| 03 list prompts / versions (paginated) | `infra/…` `PromptManagementShowcase.list_prompts`, `.list_versions` |
| 04 render locally (strict variables) | `domain/…` `render_variant`, `infra/…` `PromptManagementShowcase.converse_rendered_variant` |
| 04 Converse with prompt ARN + `promptVariables` | `infra/…` `PromptManagementShowcase.converse_managed_prompt` |
| Representational State Transfer (REST) Application Programming Interface (API) | `api/_01bedrock_03prompt_management.py` `router` (`/prompts`) |
| Terraform prompt resource | `terraform/modules/01bedrock_03prompt_management/` (`aws_bedrockagent_prompt.main`) |

- `…` = the same component module, e.g. `infra/_01bedrock_03prompt_management.py`.

## 5. Gaps

These topics are documented but not coded.

- Traffic-split A/B between versions
  - Needs a router + metrics
- Prompt use inside Agents (06agents) and Flows resource nodes
  - [prompt-flows](prompt-flows.00index.md) uses an inline prompt
- `DeletePrompt` and version cleanup

## References

- [aws-samples/amazon-bedrock-samples: prompt management examples](https://github.com/aws-samples/amazon-bedrock-samples)
- [Amazon Bedrock User Guide: Construct and store reusable prompts with Prompt management](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management.html)
- [Amazon Bedrock API Reference: CreatePrompt](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent_CreatePrompt.html)
- [Amazon Bedrock User Guide: Test a prompt using Prompt management (run with Converse)](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-test.html)
