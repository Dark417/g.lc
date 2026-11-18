# 5langchain — LangChain, LangGraph, Deep Agents And LangSmith

> The LangChain ecosystem as a harness: `create_agent` on top of the LangGraph runtime, Deep Agents for sub-agents, and LangSmith for tracing, evals and hosting.
> Group 5 (frameworks). Overview and comparison: [5frameworks.md](5frameworks.md). Graph concepts: [1graph.md](1graph.md).
> Concept level, no code (AGENTS.md §8b). Last updated: 2026-11-16. Cells marked `*` come from background knowledge and were not re-checked.

## Index
- [0. One-minute version](#0-one-minute-version)
- [1. Concept: four products, one stack](#1-concept-four-products-one-stack)
- [2. LangGraph: how it manages state](#2-langgraph-how-it-manages-state)
- [3. LangChain agents and Deep Agents](#3-langchain-agents-and-deep-agents)
- [4. LangSmith: tracing, evals, deployment](#4-langsmith-tracing-evals-deployment)
- [5. What you still own](#5-what-you-still-own)
- [6. System design view: choosing](#6-system-design-view-choosing)
- [7. Failure modes](#7-failure-modes)
- [Where this fits](#where-this-fits)
- [References](#references)

---

## 0. One-minute version
- **What:** LangGraph is a low-level graph runtime with checkpoints and interrupts. LangChain's agent API is a ready harness built on it. Deep Agents adds sub-agents. LangSmith adds tracing, evals and hosting.
- **Why:** the strongest option when you want explicit control flow, durable pauses, and time travel.
- **How:** define state and nodes; compile with a checkpointer (per-thread state) and optionally a store (cross-thread memory); run with a thread ID.
- **Catch:** a node that resumes after an interrupt restarts from its beginning, so side effects must be idempotent.
- 🗣 "LangGraph is the runtime: threads, checkpoints, interrupts. LangChain and Deep Agents sit on top; LangSmith watches and hosts."

---

## 1. Concept: four products, one stack
`boundary` ★★★

| Piece | Role | Layer |
|---|---|---|
| LangGraph | state-graph runtime: nodes, edges, checkpoints, interrupts, subgraphs | harness runtime |
| LangChain (`create_agent`) | a prebuilt agent loop with middleware, built on LangGraph | harness |
| Deep Agents | an agent harness with planning and sub-agents, on LangGraph | harness for long tasks |
| LangSmith | tracing, evals, and deployment of agents (Agent Server) | observability and managed runtime |

- **Picture it:** an invoice-approval flow.
  - The graph has nodes: extract, validate, route, approve (interrupt), pay, notify.
  - State is saved after every node under the invoice's thread ID.
  - At approval the run pauses; days later the manager clicks approve; the run resumes from the checkpoint.
  - LangSmith shows every run's trace.
- 🗣 "I reach for LangGraph when the process has stages, approvals and must survive restarts."

---

## 2. LangGraph: how it manages state
`boundary` ★★★

| Concern | How it works |
|---|---|
| Session | a thread, identified by a `thread_id`; checkpointers scope state to it |
| Run state | a checkpoint after each step (super-step); gives short-term memory, human-in-the-loop, time travel and fault tolerance |
| Checkpointer backends | in-memory (tests only), SQLite (development), Postgres (production recommendation); other backends via packages* |
| Long-term memory | the Store: key-value data outside graph state, shared across threads (preferences, facts) |
| Human approval | an interrupt pauses and saves; a resume command continues |
| Durability modes | options to save at exit, asynchronously, or synchronously (a trade-off of speed against safety) |
| Parallelism | fan-out and fan-in with reducers merging results |
| Sub-agents | subgraphs, each with its own checkpoint namespace |

- **Operational notes**
  - Keep Postgres `thread_id` values short (under 255 characters); a UUID works.
  - Checkpoints accumulate. Prune or set retention.
  - Subgraphs keep their own checkpoints; parent graphs may not see their updates right away. Put cross-graph data in the Store.
  - On resume, the interrupted node restarts from its start. Make side effects idempotent or isolate them ([1graph.md](1graph.md)).
- **Time travel:** reload an earlier checkpoint to replay or fork a run; a debugging tool ([4observability.md](4observability.md)).
- 🗣 "Thread is the session, checkpoint is the save point, store is long-term memory."

---

## 3. LangChain agents and Deep Agents
`AI` ★★

- **`create_agent`:** a model-driven loop with tools, wrapped in middleware hooks. Built-in middleware includes human approval and, from background knowledge, summarization and PII handling*.
- **Persistence:** inherits LangGraph checkpointers and store.
- **Deep Agents:** a harness for longer tasks, with planning and sub-agents that run in their own context*; the sub-agent pattern in [1orchestration.md](1orchestration.md).
- **MCP and tools:** tool adapters and MCP adapters.
- **Guardrails:** middleware for PII detection and approval; custom hooks for more ([4guardrails.md](4guardrails.md)).
- **Choose between them**

| Need | Use |
|---|---|
| A standard tool-using agent fast | `create_agent` |
| Fixed stages, branching, pauses | LangGraph directly |
| Long open-ended tasks with delegation | Deep Agents |

---

## 4. LangSmith: tracing, evals, deployment
`software` ★★

| Function | What it gives |
|---|---|
| Tracing | per-run trees of model and tool calls; OpenTelemetry in and out |
| Evals | datasets and graders tied to traces ([4evals.md](4evals.md)) |
| Deployment | Agent Server that runs graphs and handles checkpointing and storage for you |
| Cost | commercial; self-hosting is an enterprise option |

- **Trade-off:** the managed server removes the database work and ties you to their hosting model. Without it, you operate Postgres and the service yourself.
- **Alternatives for tracing:** Langfuse or Phoenix via OpenTelemetry ([4observability.md](4observability.md)).

---

## 5. What you still own
`boundary` ★★

- The edge: BFF, SSE, auth ([0edge-com.md](0edge-com.md)).
- Postgres operation, migrations and checkpoint retention (unless using the managed server).
- Idempotency of nodes with side effects.
- Tenant isolation: the thread ID is not an access control; check user to thread ownership.
- Eval set and gate; cost budgets.
- Version pinning: the stack changes quickly.

---

## 6. System design view: choosing
`boundary` ★★★

| Decision | Options | How to decide |
|---|---|---|
| Entry point | `create_agent`, LangGraph, Deep Agents | by how fixed the flow is |
| Checkpointer | memory, SQLite, Postgres, managed | Postgres or managed in production |
| Hosting | your container, LangSmith Deployment | managed if you want less database work |
| Tracing | LangSmith, OTel to another backend | LangSmith if you're on this stack |
| Durability for days-long runs | checkpoints only, plus a workflow engine | checkpoints for pauses; add Temporal for heavy retry needs |

- **Choose it when:** the process has fixed stages, approvals and audits, you need resumable runs and time travel, and you're cloud-neutral.
- **Look elsewhere when:** a model-driven coding or file agent fits better (Claude Agent SDK), you're deep in a cloud's managed stack (AgentCore, Agent Runtime), or a graph is overkill.
- **Default:** LangGraph with Postgres checkpoints, a Store for user memory, interrupts for approvals, idempotent nodes, LangSmith or Langfuse for traces.

---

## 7. Failure modes
`boundary`

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Double side effect on resume | interrupted node restarts | duplicate payments or emails | idempotency keys; separate side-effect nodes |
| In-memory checkpointer in prod | default left on | state lost on restart | Postgres or managed |
| Checkpoint bloat | long threads, no pruning | storage growth, slow loads | retention and pruning |
| Subgraph state invisible | parent expects child updates | stale reads | Store for shared data |
| Thread access gap | thread ID guessed or shared | cross-user access in tests | ownership check on every call |
| Version churn | frequent releases | broken upgrades | pin; test migrations |

---

## Where this fits
- **Place:** L9 of [1a-bp.md](../1a-bp.md); the graph-runtime option with the most explicit control.
- **Time it deserves:** 30 minutes; §2, §3 and §6.
- **I should be able to…**
  - Define thread, checkpoint and store, and say which one is the session.
  - Explain why a resumed node must be idempotent.
  - Pick between `create_agent`, LangGraph and Deep Agents.
  - Say what LangSmith adds beyond tracing.

## References
1. [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence) — threads, checkpoints, store.
2. [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) — graph runtime.
3. [Choosing an agent framework in late 2026](https://www.developersdigest.tech/blog/choosing-an-agent-framework-late-2026) — versions, interrupts, middleware.
4. [LangChain Deep Agents — going to production](https://docs.langchain.com/oss/javascript/deepagents/going-to-production) — Deep Agents notes.
