# prompt-flows Bedrock Prompt Flows

> A managed Directed Acyclic Graph (DAG) of nodes for short Generative Artificial Intelligence (GenAI) pipelines, deployed through versions and aliases.

## Index

- [1. Source And Scope](#1-source-and-scope)
- [2. One-Minute Version](#2-one-minute-version)
- [3. File Index](#3-file-index)
- [4. Code Map](#4-code-map)
- [5. Gaps](#5-gaps)
- [References](#references)

---

## 1. Source And Scope

This component covers building, deploying, and invoking a Bedrock Flow.

- Lectures: AIP-C01 #28 (slides p.59–61)
- Scope: Python + Terraform
- Terraform: `terraform/modules/01bedrock_04prompt_flows/`
  - `a-flow`: Input → Prompt (inline) → Output
  - Execution role `a-flow-role`
  - App policy
- Code: Python `app/{config,api,domain,infra}/_01bedrock_04prompt_flows.py`
- Related: [prompt-management](prompt-management.00index.md)
  - Prompt nodes can reference managed prompts
- Numbers: Amazon Bedrock User Guide, "Amazon Bedrock Flows", read 2026-11
  - Unless marked "order of magnitude"

## 2. One-Minute Version

Flows chain prompts, retrieval, and logic without orchestration code.

- What
  - **Bedrock Flows**: a managed DAG of nodes for GenAI pipelines
  - Nodes
    - Input, Prompt, KnowledgeBase, Condition
    - LambdaFunction, Agent, Iterator/Collector, InlineCode
    - Storage/Retrieval (Simple Storage Service (S3)), Output, ...
- Why
  - Chain prompts, retrieval, and business logic without writing orchestration code
  - Versioned and aliased like a deployable artifact
  - Built visually or as JavaScript Object Notation (JSON)
- How

→ define nodes + connections (Terraform here, or `CreateFlow`)  
→ `PrepareFlow` validates and builds the DRAFT  
→ `CreateFlowVersion` snapshots it; `CreateFlowAlias` points a stable name at a version  
→ `InvokeFlow(flowId, aliasId, inputs)` streams `flowOutputEvent`s and a `flowCompletionEvent`

- Catch
  - Expressions and data typing are limited
    - Complex logic ends up in Lambda nodes anyway
  - Short, synchronous request/response pipelines
    - Not for long-running or human-in-the-loop work
  - Testing and debugging = traces, not a debugger
- 🗣 "Flows are a managed DAG for prompt chains: great for linear GenAI pipelines, wrong for long-running workflows."
- 🗣 "Invoke the alias, never the draft: the alias is how you deploy and roll back."

## 3. File Index

Read top to bottom: what it is, how it is wired, how it ships and runs.

- Foundations
  - [01 Why it was created, picture](prompt-flows.01why-and-picture.md)
  - [02 Nodes and connections](prompt-flows.02nodes-connections.md)
- Shipping and running
  - [03 Lifecycle: draft, prepare, version, alias](prompt-flows.03lifecycle.md)
  - [04 Invoking a flow](prompt-flows.04invoke.md)
  - [05 Security: the execution role](prompt-flows.05execution-role.md)
- Decide and defend
  - [98 Trade-offs: when to use, knobs, comparison, failure modes](prompt-flows.98tradeoffs.md)
  - [99 Interview questions](prompt-flows.99interview.md)

## 4. Code Map

Python only; this component has no Java code.

| Concept file | Python (`app/`) |
|---|---|
| 02 definition as data | `domain/_01bedrock_04prompt_flows.py` `build_summary_flow` |
| 02 validate | `infra/…` `FlowsShowcase.validate_definition` |
| 02 create from code | `infra/…` `FlowsShowcase.create_flow` |
| 03 prepare + poll | `infra/…` `FlowsShowcase.prepare_flow` |
| 03 version + alias | `infra/…` `create_flow_version`, `create_flow_alias`, `point_alias` |

| Concept file | Python (`app/`) |
|---|---|
| 03 list versions | `infra/…` `FlowsShowcase.list_flow_versions` |
| 04 invoke + parse | `infra/…` `FlowsShowcase.invoke_flow` → `domain/…` `FlowRun` |
| Representational State Transfer (REST) | `api/_01bedrock_04prompt_flows.py` `router` (`/flows`) |
| 05 flow + role | `terraform/modules/01bedrock_04prompt_flows/` (`aws_bedrockagent_flow.main`, `aws_iam_role.flow`) |

- `…` = the same component module, e.g. `infra/_01bedrock_04prompt_flows.py`.

## 5. Gaps

These topics are documented but not coded.

- Condition, KnowledgeBase, Lambda, Iterator/Collector nodes
  - Only Input → Prompt → Output is coded
- Multi-turn flows (`flowMultiTurnInputRequestEvent` + `executionId`)
  - Parsed but not driven
- Flow alias canary / traffic split

## References

- [aws-samples/amazon-bedrock-samples: flows examples](https://github.com/aws-samples/amazon-bedrock-samples)
- [Amazon Bedrock User Guide: Build an end-to-end generative AI workflow with Amazon Bedrock Flows](https://docs.aws.amazon.com/bedrock/latest/userguide/flows.html)
- [Amazon Bedrock User Guide: Node types for your flow](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-nodes.html)
- [Amazon Bedrock User Guide: Create a service role for Amazon Bedrock Flows](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-permissions.html)
