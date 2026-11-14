# 01bedrock.04prompt-flows Interview Questions

> L4 answers plus L5 extras on Flows: nodes, deployment, Step Functions, security, design.

## Index

- [1. Core Questions](#1-core-questions)
  - [1.1 What Is A Flow](#11-what-is-a-flow)
  - [1.2 Deploy And Roll Back](#12-deploy-and-roll-back)
  - [1.3 Flows vs Step Functions](#13-flows-vs-step-functions)
  - [1.4 Securing A Flow](#14-securing-a-flow)
- [2. L5-Only Questions](#2-l5-only-questions)
  - [2.1 Support Triage Pipeline](#21-support-triage-pipeline)

Back to [00index](01bedrock.04prompt-flows.00index.md).

---

## 1. Core Questions

Each question has an L4 baseline and an L5 extension.

### 1.1 What Is A Flow

**Q1:** What is a Bedrock Flow and what nodes does it have?

**L4 answer**

- A managed Directed Acyclic Graph (DAG) of nodes for Generative Artificial Intelligence (GenAI) pipelines
- Input, Prompt, KnowledgeBase, Condition, Lambda, Agent, Iterator/Collector, Storage, Output

**L5 extra**

- Data connections map named outputs to named inputs
  - With JSONPath-like expressions
- Runs as an execution role
  - Caller needs `InvokeFlow` on the alias
- Each Output node emits one `flowOutputEvent`
  - Completion is a separate event

Details: [02 nodes and connections](01bedrock.04prompt-flows.02nodes-connections.md), [04 invoke](01bedrock.04prompt-flows.04invoke.md).

### 1.2 Deploy And Roll Back

**Q2:** How do you deploy and roll back a flow?

**L4 answer**

- Prepare the DRAFT, create a version, point an alias at it
- Rollback = point the alias back to the previous version

**L5 extra**

- Definition in Terraform/JSON with Continuous Integration (CI) validation
- Canary: two aliases, or route a share of traffic in the caller
- Prompt nodes referencing managed prompt versions
  - Decouple prompt changes from graph changes

Details: [03 lifecycle](01bedrock.04prompt-flows.03lifecycle.md).

### 1.3 Flows vs Step Functions

**Q3:** Flows vs Step Functions?

**L4 answer**

- Flows: short GenAI chains with native prompt/KB nodes
- Step Functions: general workflows with retries, waits, long runs

**L5 extra**

- Step Functions gives
  - per-step retry policies
  - callbacks (`waitForTaskToken`) for human approval
  - execution history for audit
- Flows trade that for less plumbing on prompt nodes
- Common combo: Step Functions calls Bedrock directly or invokes a flow as one step

Details: [98 trade-offs](01bedrock.04prompt-flows.98tradeoffs.md#3-comparison).

### 1.4 Securing A Flow

**Q4:** How do you secure a flow?

**L4 answer**

- Least-privilege execution role
- Guardrails on prompt nodes

**L5 extra**

- Trust policy with `aws:SourceAccount` / `aws:SourceArn` (confused deputy)
- `iam:PassRole` restricted to bedrock and to that role
- Customer Managed Key (CMK) encryption
- Traces may contain Personally Identifiable Information (PII)

  ⇒ control who reads them

Details: [05 execution role](01bedrock.04prompt-flows.05execution-role.md).

## 2. L5-Only Questions

These test design ownership and trade-offs.

### 2.1 Support Triage Pipeline

**L5-only Q5:** A support team wants a "triage → retrieve → answer → escalate to human" pipeline. Design it.

**L5 answer**

- Triage + retrieve + answer is a short chain → Flow
  - Condition on intent
  - Knowledge Base (KB) node
  - Prompt node with guardrail
- Escalation to a human waits hours → Step Functions with a task token
  - It invokes the flow as a step
- Or all in code if the team already owns a service and needs tests
- Trade-off: visual ownership by the support team vs testability and long-running control
