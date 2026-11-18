# 5frameworks — Agent Frameworks And Ecosystems Compared

> What a framework manages for you and what you still own, framework by framework: sessions, state, memory, sub-agents, approvals, guardrails, tracing, deployment. Plus the cloud ecosystems around them.
> Group 5 (frameworks). One doc each: [5adk.md](5adk.md), [5aws.md](5aws.md), [5claude-sdk.md](5claude-sdk.md), [5openai-sdk.md](5openai-sdk.md), [5langchain.md](5langchain.md).
> Concept level, no code (AGENTS.md §8b). Last updated: 2026-11-16.
> **Reliability note:** versions and features are from late-2026 vendor docs and summaries. Cells marked `*` come from my background knowledge and were not re-checked this round. Verify before quoting in an interview.

## Index
- [0. One-minute version](#0-one-minute-version)
- [1. Concept: a framework is a prebuilt harness](#1-concept-a-framework-is-a-prebuilt-harness)
- [2. What a harness must manage: the checklist](#2-what-a-harness-must-manage-the-checklist)
- [3. Who manages what: the big tables](#3-who-manages-what-the-big-tables)
- [4. Sub-agents: how each framework does it](#4-sub-agents-how-each-framework-does-it)
- [5. External stores: what exists, what you write](#5-external-stores-what-exists-what-you-write)
- [6. The ecosystems](#6-the-ecosystems)
- [7. System design view: choosing](#7-system-design-view-choosing)
- [8. Failure modes](#8-failure-modes)
- [Where this fits](#where-this-fits)
- [References](#references)

---

## 0. One-minute version
- **What:** a framework packages part of a harness: the loop, tool calling, sessions, hooks and tracing. A cloud platform packages the hosting around it.
- **Why:** you don't rewrite the same plumbing. You still own what makes it a product: edge, auth, data, policy, evals, cost.
- **How:** pick the control style (model-driven loop or explicit graph), then check each concern in §3: does the framework do it, partly, or do I?
- **Catch:** "has sessions" can mean an in-memory list or a durable, shared, encrypted store. Read what's persisted, where, and who locks it.
- 🗣 "A framework is a harness I import. The question is never 'does it have memory' but 'where is it stored, who writes it, and what happens at 100k users'."

---

## 1. Concept: a framework is a prebuilt harness
`boundary` ★★★

- **Plain idea:** like web frameworks. Spring handles routing and request lifecycle; you still design the data and auth. Agent frameworks handle the loop and plumbing; you design the system.
- **Picture it:** the same support agent in two stacks.
  - Stack 1: Strands agent code on AWS AgentCore. The runtime isolates sessions, Memory stores history, Gateway exposes your APIs as tools.
  - Stack 2: LangGraph in your container with Postgres checkpoints and LangSmith traces. You operate the database and the service.
  - Same job. Different split of who runs what.
- **Four layers** (from [1architecture.md](1architecture.md) §3.4)
  1. Model API client.
  2. Model gateway.
  3. Agent framework (library): ADK, LangGraph, Strands, Claude Agent SDK, OpenAI Agents SDK.
  4. Managed agent runtime (hosted): AgentCore, Google's Agent Runtime, LangSmith Deployment.
- **The catch:** frameworks change fast; minor version bumps can break things. Pin versions.
- 🗣 "I choose the framework for the control flow I want and the platform for who operates it."

---

## 2. What a harness must manage: the checklist
`boundary` ★★★

| # | Concern | The question |
|---|---|---|
| 1 | Loop and control flow | who decides the next step? |
| 2 | Context building and compaction | what goes in the window, and how is it trimmed? |
| 3 | Session history | where does this conversation live? |
| 4 | Run state and checkpoints | can a run pause and resume on another server? |
| 5 | Long-term memory | what survives across sessions? |
| 6 | Tools and MCP | how are tools registered, called, shaped? |
| 7 | Sub-agents | how is work delegated and context isolated? |
| 8 | Human approval | how does a run pause for a person? |
| 9 | Guardrails and permissions | where do checks plug in? |
| 10 | Tracing | what is recorded, and where does it go? |
| 11 | Edge streaming | how do events reach the client? |
| 12 | Deployment and scaling | who hosts it, isolates sessions, scales it? |

- **Rule:** for each row, decide framework, platform, or you. Row 11 and parts of 3, 5 and 12 are almost always yours.

---

## 3. Who manages what: the big tables
`boundary` ★★★

- **Legend:** **Built-in** = the framework does it. **Partial** = hooks or a basic version. **You** = you build it, often on a store you run.

### 3.1 State and memory

| Concern | LangChain / LangGraph | Google ADK | Strands (AWS) | Claude Agent SDK | OpenAI Agents SDK |
|---|---|---|---|---|---|
| Session history | Built-in: state per `thread_id`, saved by a checkpointer (in-memory, SQLite, Postgres) | Built-in: Session service with events and state; in-memory, database*, or managed on Google's platform | Built-in: session managers (file, S3, custom repository, AgentCore Memory) | Built-in: transcripts saved locally; continue, resume, fork by ID; `SessionStore` mirrors to your backend | Built-in: session classes (SQLite, Redis, SQLAlchemy, MongoDB, Dapr, server-side Conversations) |
| Run state, checkpoints | Built-in: checkpoint every step; time travel; resume after interrupt | Partial: session events and state; long-running tools pause a run | Partial: persists agent and graph or swarm state through the session manager | Partial: transcript resume; file checkpointing is separate | Partial: serializable run state at interruptions |
| Long-term memory | Built-in: `Store` for cross-thread data | Built-in: Memory service (in-memory, Memory Bank, RAG-based) | Partial: via AgentCore Memory manager, or your own tool | Partial: `CLAUDE.md` and memory files; per-subagent memory option | You: sandbox memory files exist; otherwise your store |
| Context compaction | Partial: middleware, e.g. summarization* | Partial*: event compaction option | Built-in: conversation managers (sliding window, summarizing)* | Built-in: auto-compaction | Partial: a compaction wrapper for sessions |
| Storage you run | Postgres for production; or managed Agent Server | Database or Google's managed service | S3, file, or AgentCore | the host's disk, or your store via `SessionStore` | your Redis or SQL, or OpenAI-hosted conversations |

### 3.2 Control and operations

| Concern | LangChain / LangGraph | Google ADK | Strands (AWS) | Claude Agent SDK | OpenAI Agents SDK |
|---|---|---|---|---|---|
| Tools and MCP | Built-in: tools, MCP adapters | Built-in: function tools, MCP toolset, agent tools | Built-in: tools, MCP client | Built-in: in-process MCP tools, MCP servers, tool search | Built-in: function, hosted and MCP tools |
| Human approval | Built-in: `interrupt` and resume command; approval middleware | Built-in: tool confirmation, long-running tools | Partial*: interrupts; check docs | Built-in: permission modes, hooks, a permission callback | Built-in: tool approval flag; interruptions; resume from run state |
| Guardrails | Partial: middleware (PII, approval) | Partial: callbacks and plugins | Partial*: hooks; Bedrock Guardrails on the model | Partial: hooks that can deny or defer | Built-in: input, output and tool guardrails (with gaps; see [4guardrails.md](4guardrails.md)) |
| Tracing | Built-in via LangSmith; OTel supported | Partial: OTel and Cloud Trace* | Built-in: OTel; AgentCore Observability | Partial: telemetry and hooks | Built-in: traces dashboard on by default |
| Edge streaming | Built-in: stream modes; you build the SSE layer | Built-in: SSE run endpoint; you build the BFF | You | You | Built-in: stream events; you build SSE |
| Hosting | LangSmith Deployment (Agent Server), or your container | Cloud Run, GKE, Google's Agent Runtime | AgentCore Runtime, ECS, Lambda | your container, one process per session | your container; hosted sandbox providers |

- **What the tables hide:** "Built-in" still needs your database, keys, quotas and retention rules.
- **Always yours:** edge auth, tenant isolation, cost budgets, the policy store, evals, queues for long runs.

---

## 4. Sub-agents: how each framework does it
`AI` ★★★

| Framework | Mechanisms | Who decides | Context handling | Notes |
|---|---|---|---|---|
| LangGraph | subgraphs, supervisor graphs, nodes that are agents | code (edges) or a supervisor model | shared state with reducers, or separate subgraph state | most explicit control |
| LangChain Deep Agents | sub-agents spawned by the lead agent | the lead model | each sub-agent has its own context | a harness on top of LangGraph |
| Google ADK | `sub_agents` with transfer (handoff style); agent as a tool; workflow agents (sequential, parallel, loop); A2A (experimental in the summary I read) | model or workflow type | shared session; branch separates parallel histories | rich set, close to the model |
| Strands | agents as tools; swarm; graph; workflow | orchestrator model, the agents, or you | shared state or message passing | "if you can draw the steps, use a workflow or graph" |
| Claude Agent SDK | subagents defined in options, each with its own tools, model and budget; a workflow tool for large fan-out | the lead model | fresh context per subagent; summary returns | reported limits: nesting depth 3, concurrency 20 by default; a subagent can't escalate permissions |
| OpenAI Agents SDK | handoffs (the specialist takes over); agents as tools (the manager keeps control) | the model | handoffs can filter history passed on | server-managed conversations lack handoff input filters |
| Managed runtimes | host any of the above; AgentCore supports A2A on Runtime | n/a | n/a | the runtime doesn't choose the pattern |

- **Two patterns cover most of it:** handoff (give control away) and agent as tool (lend control). Patterns in [1orchestration.md](1orchestration.md).
- 🗣 "Every framework offers handoff and agent-as-tool. They differ in how much control flow they let you own."

---

## 5. External stores: what exists, what you write
`software` ★★★

- **Plain idea:** frameworks ship adapters for common stores. They don't design your keys, retention or locking.

| Store | Adapters that exist | What you still write |
|---|---|---|
| Redis | OpenAI Agents SDK `RedisSession`; LangGraph Redis checkpointer and store as a separate package*; Strands and Claude SDK via custom adapters | key design, TTL, serialization version, per-session lock, encryption, persistence mode |
| Postgres | LangGraph `PostgresSaver` (the production recommendation); OpenAI `SQLAlchemySession`; ADK database session service* | schema migrations, indexes, pooling, pruning of old checkpoints, backups |
| DynamoDB | AWS packages for LangGraph*; Strands via custom repository | table design, TTL, item size limits, throttling |
| S3 | Strands `S3SessionManager` | prefixes per tenant, lifecycle rules, locking (session managers are not thread-safe) |
| Vector store | LangGraph store with an index*; ADK RAG memory service | what to extract, namespaces per user, deletion on request, PII handling |
| Managed memory | AgentCore Memory; Google's Memory Bank | namespace design, what gets generated, TTL, cost |

- **Three jobs no adapter does**
  1. **Locking:** one writer per session. Strands says its session managers are not thread-safe; the same holds elsewhere.
  2. **Retention and privacy:** TTLs, deletion on request, encryption. The Claude SDK says retention in your store is your job.
  3. **Schema versions:** a framework upgrade may change the saved format; plan migrations.
- 🗣 "The adapter gives me a table. Keys, locks, TTLs and deletes are still my design."

---

## 6. The ecosystems
`boundary` ★★

| Ecosystem | Pieces | How they fit | Detail |
|---|---|---|---|
| AWS | Bedrock (models, Guardrails, Knowledge Bases), AgentCore (Runtime, Memory, Identity, Gateway, Code Interpreter, Browser, Observability, Policy, Evaluations, Registry, managed Harness), Strands (framework), Step Functions | Strands code runs on AgentCore Runtime; Memory, Gateway and Identity plug in; Bedrock supplies models and guardrails | [5aws.md](5aws.md) |
| Google | Gemini models, ADK (framework), the agent platform (managed Agent Runtime, Sessions, Memory Bank), Model Armor, Cloud Trace; A2A protocol | ADK agents deploy to the managed runtime, which supplies sessions and memory | [5adk.md](5adk.md) |
| LangChain | LangChain (`create_agent`), LangGraph (runtime), Deep Agents, LangSmith (tracing, evals, deployment) | LangChain agents run on LangGraph; LangSmith watches and hosts them | [5langchain.md](5langchain.md) |
| Anthropic | Claude models, Claude Agent SDK, MCP | the SDK runs the Claude Code loop; you host it | [5claude-sdk.md](5claude-sdk.md) |
| OpenAI | Agents SDK, Responses and Conversations APIs, hosted tools, sandbox agents, traces | the SDK runs the loop; sessions and traces can be OpenAI-hosted or yours | [5openai-sdk.md](5openai-sdk.md) |
| Others | Microsoft Agent Framework, CrewAI, Mastra, Pydantic AI, LlamaIndex, Vercel AI SDK | similar splits, each with its own state and approval model | out of scope here |

- **Product names move.** Google's docs now use "Gemini Enterprise Agent Platform" and "Agent Runtime"; the older names were Vertex AI Agent Builder and Agent Engine. Check current names.

---

## 7. System design view: choosing
`boundary` ★★★

### 7.1 Deciding variables
1. **Control style:** explicit graph (LangGraph, ADK workflows) vs model-driven loop (Claude SDK, OpenAI SDK, Strands).
2. **Cloud:** AWS leans Strands plus AgentCore; Google leans ADK plus Agent Runtime; neutral leans LangGraph or an SDK in your container.
3. **Durability needs:** days-long pauses and audits favor graph checkpoints or a workflow engine.
4. **Team language:** Python and TypeScript are covered by all; ADK also has Go, Java and Kotlin per the summary I read.
5. **Who operates it:** managed runtime vs your containers.
6. **Lock-in tolerance:** managed memory and runtimes are convenient and sticky.

### 7.2 Common combinations

| Stack | Parts | Good at | Weak at |
|---|---|---|---|
| AWS-native | Strands, AgentCore (Runtime, Memory, Gateway, Identity), Bedrock | little to operate; policy and evals included | AWS lock-in |
| Google-native | ADK, Agent Runtime with Sessions and Memory Bank, Gemini | tight Gemini and Google Cloud fit | Google lock-in; naming churn |
| LangChain stack | LangGraph, Postgres, LangSmith | explicit control, strong tracing and evals | more to operate unless you use their hosting |
| Claude-centric | Claude Agent SDK, your container, Langfuse | strong coding and file agents; your own control | you build hosting, state, isolation |
| OpenAI-centric | Agents SDK, Redis or SQL sessions, OpenAI traces | quick start; handoffs; hosted tools | tracing off under zero data retention; fewer graph features |

- **Pick:** if the process is a known business flow with approvals, use a graph runtime (LangGraph or ADK workflows). If it's open-ended work, use a model-driven SDK. Then choose hosting by your cloud.
- **Deciding variable:** how much control flow you hand to the model, then who runs the servers.
- **Default for an AWS shop:** Strands plus AgentCore. **For a Google shop:** ADK plus Agent Runtime. **Cloud-neutral with approvals:** LangGraph plus Postgres plus Langfuse or LangSmith.

---

## 8. Failure modes
`boundary`

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| In-memory sessions in production | default session store left on | history lost on deploy | external store before launch |
| Concurrent writers | two requests on one session | corrupt or lost history | per-session lock or queue |
| Resume re-runs side effects | graph resumes from node start | duplicate payments or emails | idempotency keys; side effects in their own node |
| Framework upgrade breaks state | saved format changes | old sessions fail to load | pin versions; migration tests |
| Guardrail gap | a code path bypasses the framework's checks | audit finds unchecked tool calls | map every path; add checks in your own hook |
| Tracing data leaves your boundary | default hosted tracing | compliance review | choose backend deliberately; redact |
| Lock-in surprise | managed memory shapes the data model | migration estimate | keep a thin interface over memory |

---

## Where this fits
- **Place:** L9 of [1a-bp.md](../1a-bp.md). It ties groups 1–4 to concrete products.
- **Time it deserves:** 30 minutes; §3, §4 and §5. Then one framework doc, the one for the target employer's stack.
- **I should be able to…**
  - Say, for any framework, where sessions, checkpoints and long-term memory live.
  - Compare handoff and agent-as-tool in two frameworks.
  - Name the three things no storage adapter does for me.
  - Pick a stack from the deciding variables.

## References
1. [Choosing an agent framework in late 2026](https://www.developersdigest.tech/blog/choosing-an-agent-framework-late-2026) — versions and capability summary used for the tables.
2. [Strands — session management](https://strandsagents.com/docs/user-guide/concepts/agents/session-management/) — managers and limits.
3. [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence) — threads, checkpoints, store.
4. [ADK — sessions and memory](https://adk.dev/sessions/memory/) — session and memory services.
5. [OpenAI Agents SDK in late 2026](https://www.developersdigest.tech/blog/openai-agents-sdk-whats-new-2026) — sessions, approvals, handoffs, guardrails.
6. [Claude Agent SDK in late 2026](https://www.developersdigest.tech/blog/claude-agent-sdk-whats-new-2026) — sessions, subagents, hooks, permissions.
