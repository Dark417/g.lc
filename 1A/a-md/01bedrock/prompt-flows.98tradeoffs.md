# prompt-flows Trade-offs

> When Flows fit, the knobs that keep them safe, how they compare, and how they fail.

## Index

- [1. When To Use / Not](#1-when-to-use--not)
- [2. Knobs And Best Practices](#2-knobs-and-best-practices)
- [3. Comparison](#3-comparison)
- [4. Failure Modes](#4-failure-modes)

Back to [00index](prompt-flows.00index.md).

---

## 1. When To Use / Not

Flows fit short, fixed chains; long or model-driven work belongs elsewhere.

- Use when
  - A linear or lightly branched Generative Artificial Intelligence (GenAI) pipeline
    - Seconds, not hours
  - Non-developers should see or edit the chain visually
  - You want versions + aliases for prompt chains
    - Without a deploy pipeline per change
- Avoid when
  - Long-running, retries per step, waits, or human approval
    - ⇒ Step Functions (lecture 301)
  - Open-ended tool use where the model decides the steps
    - ⇒ an agent (06agents)
  - Heavy business logic, unit tests, and code review matter most
    - ⇒ orchestration in code

## 2. Knobs And Best Practices

Each rule names the failure it prevents.

- Invoke aliases only; deploy by moving the alias
  - Prevents: DRAFT edits reaching users
- Keep the definition in Terraform (or JavaScript Object Notation (JSON) in git)
  - Prevents: console-only drift with no review
- Use managed prompts ([prompt-management](prompt-management.00index.md)) in prompt nodes
  - When prompts change faster than the graph
- Attach a guardrail to prompt and Knowledge Base (KB) nodes that see user input
- Validate (`ValidateFlowDefinition`) in Continuous Integration (CI) before `UpdateFlow`
- Keep Lambda nodes small and idempotent
  - Prevents: duplicate side effects on retries
- Enable traces in test, sample them in production
  - Cost, Personally Identifiable Information (PII)
- Least-privilege execution role per flow
- `concurrencyConfiguration: Manual` to protect downstream quotas
  - Model Tokens Per Minute (TPM), Lambda concurrency

## 3. Comparison

Duration and control flow decide the tool.

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| Bedrock Flows | Managed GenAI Directed Acyclic Graph (DAG) with prompt/KB/agent/Lambda nodes | Native Bedrock nodes; visual; versions + aliases; no servers | Limited expressions; sync and short; debugging via traces; Bedrock-only | Linear or lightly branched prompt chains |
| Step Functions (+ Bedrock integrations) | General workflow engine, state machine in Amazon States Language (ASL) | Retries per step, waits, callbacks (human approval), long runs, wide Amazon Web Services (AWS) integrations | More boilerplate for prompt plumbing; per-transition cost | Long-running, auditable, Human-in-the-Loop (HITL) business workflows |
| Code orchestration (Python/Java, LangGraph) | The app calls Converse/Retrieve itself | Full control, unit tests, any logic, any vendor | You own retries, versioning, deployment | Complex or evolving logic; agents; existing services |

- Deciding variable: duration and control flow
  - Seconds and a fixed chain → Flows
  - Minutes to days, retries, approvals → Step Functions
  - Complex or model-driven logic → code
- Pick: orchestration in code for backend services, unless the chain is simple and owned by non-developers → Flows, or long-running / HITL → Step Functions.

## 4. Failure Modes

Most failures are wiring, permissions, or skipped lifecycle steps.

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Flow not prepared | Invoking after `UpdateFlow` without `PrepareFlow` | `ValidationException` / old behavior | Prepare, then version + move alias |
| Broken wiring | Wrong `sourceOutput` / `targetInput` names or types | `ValidateFlowDefinition` errors; `Failed` status | Validate in CI; consistent naming |
| Wrong expression | `$.data.x` path does not exist | Empty or failed node output in traces | Test with traces; validate input shape |
| Access denied in a node | Execution role lacks model/KB/Lambda permission | `dependencyFailedException` / `accessDeniedException` events | Grant the node's action to the execution role |

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| PassRole denied | Creator lacks `iam:PassRole` | `AccessDeniedException` on create/update | Allow PassRole on that role, to bedrock only |
| Throttling | Model TPM shared with other traffic | `throttlingException` event | Manual concurrency; inference profile; retry on the caller |
| DRAFT in production | Invoking the test alias | Behavior changes without release | Invoke a real alias pinned to a version |
| Timeout | Long Lambda or big generation | Stream error / client timeout | Move long work to Step Functions; smaller `maxTokens` |
