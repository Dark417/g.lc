# 1architecture — Agentic System Architecture

> The whole system around an agent: its components, how one request flows end to end, where state lives, and how it's deployed.
> Group 1 (agent core). Core runtime: [1harness.md](1harness.md). Wire formats: [1aa-msg.md](1aa-msg.md).
> Concept level, no code (AGENTS.md §8b). Last updated: 2026-11-16.

## Index
- [0. One-minute version](#0-one-minute-version)
- [1. Concept](#1-concept)
- [2. The components, by zone](#2-the-components-by-zone)
- [3. One request, end to end](#3-one-request-end-to-end)
- [4. Where state lives](#4-where-state-lives)
- [5. Deployment shapes](#5-deployment-shapes)
- [6. System design view: the big decisions](#6-system-design-view-the-big-decisions)
- [7. Failure modes](#7-failure-modes)
- [Where this fits](#where-this-fits)
- [References](#references)

---

## 0. One-minute version
- **What:** an agent product is a normal backend with one unusual component, a harness that calls a model in a loop.
- **Why:** the model is a small part. Auth, tools, data, state, safety, evals and operations are most of the system.
- **How:** UI, API, harness, model gateway, tools, data stores, and a control plane for guardrails, approvals and tracing.
- **Catch:** model calls are slow, costly and non-deterministic, so the system must stream, bound, queue and trace them.
- 🗣 "An agent system is a backend where one dependency is slow, expensive and sometimes wrong, so the design is about bounding it."

---

## 1. Concept
`boundary`

- **Plain idea:** design it like any service with a risky dependency, like a payment gateway that sometimes makes things up.
- **Picture it:** an internal support assistant.
  - A user asks in a web chat. The API checks who they are.
  - The harness pulls policy documents, calls the model, and maybe calls a ticketing tool.
  - A guardrail checks the answer; risky actions wait for approval.
  - Every step is traced; the answer streams back.
- **How it works**
  1. The edge authenticates the user and opens a stream.
  2. The harness loads the session and builds context.
  3. It calls the model through a gateway, runs tools through policy checks, and loops as needed.
  4. Results stream back; state and the trace are saved.
  5. Long or risky work moves to queues and human approval.
- **The catch**
  - Latency is seconds, not milliseconds, so streaming and async jobs are needed.
  - Cost depends on steps and tokens, not requests.
  - Correctness can't be unit-tested alone; it needs evals on real cases.
- 🗣 "I treat the model as an untrusted, slow, metered dependency behind a port."

---

## 2. The components, by zone
`boundary` ★★★

```
  [UI] --stream--> [API / BFF] --> [HARNESS] --> [model gateway] --> [LLM]
                      |               |  \-------> [tools] --> [MCP servers] --> [business systems]
                   [identity]         |  \-------> [sub-agents / remote agents (A2A)]
                                      |--> [session store] [memory] [retrieval] [artifacts]
                                      |--> [guardrails] [human approval] [queue / workflow engine]
                   every component --> [tracing, metrics, logs, evals]
```

| Zone | Components | Job | Holds state? |
|---|---|---|---|
| Edge | UI, API gateway / BFF, identity provider | auth, rate limits, streaming | request-scoped |
| Core | harness, model gateway, LLM | loop, context, routing, fallback | harness should be stateless |
| Tools | in-process tools, MCP servers, sandbox, business systems | act on the world | business data lives here |
| Agents | sub-agents, remote agents | delegated work | their own tasks |
| Data | session store, memory, retrieval index, artifact store | history, facts, knowledge, files | yes |
| Control and ops | guardrails, human approver, queue, observability, evals | bound, pause, retry, see, prove | policies, traces |

- **The harness touches almost every edge.** That's why it's the place for policy, budgets and tracing.
- **The model gateway** gives one place for provider keys, routing, fallback, rate limits and cost tracking (e.g. LiteLLM, or the cloud provider's own).
- **Tools reach business systems** directly or through MCP servers (3mcp.md).
- 🗣 "The harness is the hub. Put the rules there, not in the prompt."

---

## 3. One request, end to end
`boundary` ★★★

1. **Edge:** the UI sends the message; the API validates the token, applies rate limits, opens an SSE stream.
2. **Load:** the harness loads session state and relevant memory for this user.
3. **Context:** it adds instructions, tool definitions and retrieved documents the user may see.
4. **Input guardrail:** checks for injection, PII rules, off-topic requests.
5. **Model call:** through the gateway, with timeout, fallback and token cap.
6. **Tool step:** the model asks for a tool; the harness checks permissions as this user, asks for approval if risky, runs it, shapes the result.
7. **Loop:** steps 5–6 repeat within step, token and time budgets.
8. **Output guardrail:** checks grounding, policy and PII before anything leaves.
9. **Respond:** tokens and progress stream to the UI; sources are cited.
10. **Persist:** state, trace and cost are saved; feedback buttons tie back to the trace ID.

- **Long-running variant:** the API returns a run ID right away; a worker runs the agent from a queue; the UI follows progress by stream or polling.
- 🗣 "Auth at the edge, permissions at every tool call, guardrails on the way in and out, a trace across all of it."

---

## 4. Where state lives
`software` ★★★

| State | Lifetime | Typical store | Why there |
|---|---|---|---|
| Request context | one call | memory | rebuilt each turn |
| Session / run state | one conversation or run | Postgres, Redis, DynamoDB, framework session service | any worker can resume |
| Checkpoints | per graph step | framework checkpointer, workflow engine | crash recovery, human pauses |
| Long-term memory | across sessions | vector store or DB per user | personalization |
| Knowledge | until re-indexed | vector or search index | retrieval |
| Artifacts | files and outputs | object storage | large items, passed by reference |
| Audit and traces | retention policy | trace backend, log store | debugging, compliance |

- **Rule:** the harness process holds nothing that matters. Everything durable goes to a store.
- Detail on memory and state: 2memory-state.md.

---

## 5. Deployment shapes
`software` ★★

| Shape | How | Good at | Weak at | Choose when |
|---|---|---|---|---|
| Harness inside the API service | one container: API + agent | simplest; low latency | scaling and deploys are coupled | MVP, small teams |
| Separate agent service | API calls an agent service over HTTP / gRPC | independent scaling, separate owners | one more hop | several apps share agents |
| Queue + workers | API enqueues; workers run agents | long runs, retries, smooth load | more moving parts; async UX | runs over ~30 seconds or batch work |
| Managed agent runtime | hosted runtime, e.g. Bedrock AgentCore, Vertex AI Agent Engine | session isolation, scaling, built-in tracing | provider lock-in, less control | team wants less ops on one cloud |
| Serverless functions | each step or tool in a function | pay per use | timeouts and cold starts for long runs | short, bursty tools |

- **Cloud mapping**
  - AWS: API Gateway / ALB, ECS or Lambda, Bedrock (models), AgentCore (runtime, memory, identity, gateway), DynamoDB / Aurora, SQS, CloudWatch / X-Ray.
  - Google Cloud: Cloud Run, Vertex AI (models), Agent Engine (runtime), Cloud SQL / Firestore, Pub/Sub, Cloud Trace / Logging.
  - Framework detail per ecosystem: group 5 docs.
- 🗣 "Inline for an MVP, a queue once runs get long, a managed runtime when the team wants less to operate."

---

## 6. System design view: the big decisions
`boundary` ★★★

| Decision | Options | How to decide |
|---|---|---|
| Control shape | single call, workflow, loop, graph, multi-agent | is the path known? see [1harness.md](1harness.md) |
| Sync vs async | stream in the request vs queue + run ID | expected run length and failure tolerance |
| Model access | direct SDK vs gateway | gateway once you have several models, keys or teams |
| Hosting | own containers vs managed runtime | ops capacity, cloud commitment, control needs |
| Tool integration | in-process functions vs MCP servers | MCP when tools are shared across agents or teams |
| State | in-process vs external store | external for anything resumable or audited |
| Safety | prompt rules vs code checks | code checks for anything that matters (4guardrails.md, 4access.md) |
| Quality | manual testing vs eval pipeline | eval gate before any prompt or model change (4evals.md) |

- **Numbers to bring (order of magnitude; measure your own)**
  - Model call: hundreds of milliseconds to tens of seconds, depending on model and output length.
  - Agent run: several model calls, so seconds to minutes.
  - Cost per task = tokens per step × steps per task × price per token.
- **Default architecture for a first production agent**
  - Stateless harness in a container behind the API, streaming over SSE.
  - Gateway for models; tools as typed functions, with MCP for shared ones.
  - Postgres or DynamoDB for sessions; vector index for knowledge.
  - Guardrails and approval in the harness; OpenTelemetry traces to one backend; eval gate in CI.
  - Add a queue and workers when runs pass ~30 seconds.

---

## 7. Failure modes
`boundary`

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Provider outage | model API down or rate-limited | error rate per provider | gateway fallback; degrade to a simpler path |
| Request timeouts | long runs inside a sync request | gateway or LB timeouts | queue + run ID; stream progress |
| State lost on deploy | state kept in process memory | runs vanish during rollouts | external session store and checkpoints |
| Tenant data leak | retrieval or tools not filtered by user | cross-tenant eval cases fail | filter by user in the query; per-user tool credentials |
| Cost spike | loops, retries, long contexts | cost per task over baseline | budgets per run; alerts on cost metrics |
| Blind debugging | no trace across components | "can't reproduce" on bad answers | one trace ID from UI to tool calls |

---

## Where this fits
- **Place:** L8 and L9 of [1a-bp.md](../1a-bp.md). The frame every other group-1 doc plugs into.
- **Time it deserves:** 25 minutes; §2, §3 and §6. It's the opening of any agentic design answer.
- **I should be able to…**
  - Draw the zones and name one component in each.
  - Walk one request in ten steps, naming where auth, permissions and guardrails sit.
  - Choose a deployment shape and say when I'd add a queue.
  - Say where each kind of state lives and why.

## References
1. [Anthropic — Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — augmented LLM and agent building blocks.
2. [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) — managed runtime, memory, identity, gateway, observability.
3. [Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview) — managed agent hosting on Google Cloud.
4. [OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — tracing across model and tool calls.
