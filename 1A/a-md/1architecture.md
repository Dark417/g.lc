# 1architecture — Agentic System Architecture

> The whole system around an agent: components, one request end to end, what each kind of state means, how it's deployed, and how it scales.
> Group 1 (agent core). Core runtime: [1harness.md](1harness.md). Client side: [0edge-com.md](0edge-com.md). Wires: [1aa-msg.md](1aa-msg.md).
> Concept level, no code (AGENTS.md §8b). Last updated: 2026-11-16 (refreshed).

## Index
- [0. One-minute version](#0-one-minute-version)
- [1. Concept](#1-concept)
- [2. Components, by zone](#2-components-by-zone)
- [3. Four parts people confuse](#3-four-parts-people-confuse)
- [4. One request, end to end](#4-one-request-end-to-end)
- [5. State: what each word means](#5-state-what-each-word-means)
- [6. Deployment shapes](#6-deployment-shapes)
- [7. Scaling to 100k–1M users](#7-scaling-to-100k1m-users)
- [8. System design view: the big decisions](#8-system-design-view-the-big-decisions)
- [9. Failure modes](#9-failure-modes)
- [Where this fits](#where-this-fits)
- [References](#references)

---

## 0. One-minute version
- **What:** an agent product is a normal multi-user backend with one unusual dependency, a harness that calls a model.
- **Why:** the model is a small part. Identity, tools, data, state, safety, evals and operations are most of the system.
- **How:** edge (client, gateway, identity), harness, model gateway, tools, data stores, and a control plane for guardrails, approvals, tracing and evals.
- **Catch:** model calls are slow, metered and non-deterministic. The design is about bounding them.
- **Stateless means** the harness process keeps nothing between requests. The conversation continues because state is loaded by session ID.
- 🗣 "An agent system is a backend where one dependency is slow, expensive and sometimes wrong, so the design is about bounding it."

---

## 1. Concept
`boundary`

- **Plain idea:** design it like any service with a risky dependency, like a payment gateway that sometimes makes things up.
- **Picture it:** an internal support assistant.
  - A user asks in a web chat. The edge checks who they are.
  - The harness loads their session, pulls the relevant policy text, and calls the model.
  - The model asks for a "find ticket" tool; a guardrail checks the final answer.
  - A refund waits for human approval. Every step is traced; the answer streams back.
- **How it works**
  1. The edge authenticates and opens a stream.
  2. The harness loads session state and builds context.
  3. It calls the model through a gateway, runs tools through policy checks, and loops as needed.
  4. Results stream back; state and the trace are saved.
  5. Long or risky work moves to queues and human approval.
- **The catch**
  - Latency is seconds, not milliseconds. Cost depends on steps and tokens, not requests.
  - Correctness can't be unit-tested alone; it needs evals on real cases.
- 🗣 "I treat the model as an untrusted, slow, metered dependency behind a port."

---

## 2. Components, by zone
`boundary` ★★★

```
  [client] --stream--> [edge: gateway / BFF] --> [HARNESS] --> [model gateway] --> [LLM]
                          |                        |  \--> [tool registry] --> in-process tools
                       [identity]                  |                      \--> [MCP servers] --> [business systems]
                                                   |  \--> [sub-agents / remote agents (A2A)]
                                                   |--> [session store] [memory] [retrieval] [artifacts]
                                                   |--> [instruction + policy store] [guardrails] [approval]
                                                   |--> [queue / scheduler / workflow engine]
                     every component --> [tracing, metrics, logs]     offline --> [evals, feedback]
```

| Zone | Components | Job | Holds state? |
|---|---|---|---|
| Edge | client, API gateway / BFF, identity provider | auth, rate limits, streaming (see [0edge-com.md](0edge-com.md)) | request-scoped |
| Core | harness, model gateway, LLM | loop, context, routing, fallback | harness: none that matters |
| Config | instruction and prompt registry, policy store, feature flags, secrets | versioned rules and prompts, loaded by the harness | versioned config |
| Tools | tool registry, in-process tools, MCP servers, sandbox, business systems | act on the world | business data lives here |
| Agents | sub-agents, remote agents | delegated work | their own tasks |
| Data | session store, memory, retrieval index, artifact store | history, facts, knowledge, files | yes |
| Control | guardrails, permission checks, human approval, quotas, queue and scheduler | bound, pause, retry, trigger | policies, pending items |
| Ops | tracing, metrics, evals, feedback, cost tracking | see, measure, prove | traces, scores |

- **The harness touches almost every wire.** That's why rules, budgets and tracing belong there ([1aa-msg.md](1aa-msg.md)).
- **Triggers:** runs start from a user message, a schedule, a webhook or a queue message. The same harness serves all four.
- **Caches:** the provider's prompt cache (stable prefix) saves cost; an app cache can hold retrieval or tool results.
- 🗣 "The harness is the hub. Put the rules there, not in the prompt."

---

## 3. Four parts people confuse
`boundary` ★★★

### 3.1 "Policy documents": three different things
| Kind | Example | Where it's enforced | How the model sees it |
|---|---|---|---|
| Instructions | "You are a support agent; never promise refunds" | in the prompt | sent with every model call |
| Rules | rate limit, allowed tools per role, spend cap | in harness code or a policy engine | never; the model only sees the result ("denied") |
| Knowledge | refund policy text, runbooks | retrieved when relevant | pasted into context for that call |

- **Where they live:** a versioned store (Git, a config service such as etcd, AWS AppConfig or Parameter Store, or a database).
- **How the harness uses them:** load at start or session start, cache in memory with a refresh, and tag each trace with the version.
- **Each round trip:** instructions go with every model call, because the model is stateless. Rules run in code at each step. Knowledge is fetched per need.
- **Rule of thumb:** the prompt asks, the code enforces.

### 3.2 Tool vs MCP
- A tool is any capability shown to the model as name, description and argument schema.
- Where the code runs is a separate question: in the harness process, or behind an MCP server (a separate process or service).
- MCP is the standard interface, so many agents can share one tool server. It is not "external" by definition; a local MCP server over stdio runs on the same machine.
- "Ticketing tool" in earlier text was an example: a tool that calls Jira or ServiceNow to create or read a ticket. A write tool like that goes through permission checks and often approval.
- Detail: 3tools.md, 3mcp.md.

### 3.3 Model gateway: what, who, how
- **What:** a proxy in front of model providers. One API, plus routing, fallback, key custody, quotas, caching and cost logs.
- **Who provides it:** your platform team (internal), open-source you deploy (LiteLLM proxy, Portkey, Kong or Envoy AI gateways), or a hosted service (Cloudflare AI Gateway, Vercel AI Gateway, OpenRouter). Cloud model hubs (Bedrock, Google's platform) give many models behind one API and cover part of the job.
- **Model vendors** provide endpoints, not necessarily a gateway.
- **What the engineer does:** points the harness at the gateway's URL with a virtual key, uses model aliases ("fast", "strong"), and sets fallbacks and budgets in gateway config. Harness code barely changes.

### 3.4 Four layers that sound alike
| Layer | What it is | Examples | You |
|---|---|---|---|
| Model API client | calls one provider's API | provider SDKs | import it |
| Model gateway | network proxy for model calls | LiteLLM, Portkey | run or rent it |
| Agent SDK or framework | a prebuilt harness: loop, tools, sessions, hooks | ADK, Claude Agent SDK, OpenAI Agents SDK, Strands, LangGraph | import it, plug in a model |
| Managed agent runtime | hosted harness plus infrastructure | Bedrock AgentCore, Google's Agent Runtime | deploy to it |

- 🗣 "An agent SDK is a harness you import. A gateway is a proxy you route model calls through. They sit at different layers."

---

## 4. One request, end to end
`boundary` ★★★

1. **Edge:** the client sends the message and session ID; the gateway validates the token, applies rate limits, opens an SSE stream.
2. **Load:** the harness loads session state and relevant memory for this user.
3. **Config:** it loads the current instructions, tool list and policies (cached by version).
4. **Context:** it assembles instructions, tool definitions, history and retrieved documents the user may see.
5. **Input guardrail:** injection, PII and topic checks ([4guardrails.md](4guardrails.md)).
6. **Model call:** through the gateway, with timeout, fallback and token cap.
7. **Tool step:** the model returns a request to call a tool. The harness checks permission as this user, asks for approval if risky, runs it, shapes the result.
8. **Loop:** steps 6–7 repeat within step, token and time budgets.
9. **Output guardrail:** grounding, policy and PII checks before anything leaves.
10. **Respond and persist:** stream the answer with citations; save state, trace and cost; the feedback button carries the trace ID.

- **Everything the model gets is one request:** instructions, tool definitions, history, retrieved text and goals are all text in one payload, resent every call. Limits and permissions are not in it; they're code.
- **Long-running variant:** the API returns a run ID; a worker runs the agent from a queue; the client follows by stream or polling.
- 🗣 "Auth at the edge, permissions at every tool call, guardrails on the way in and out, one trace across all of it."

---

## 5. State: what each word means
`software` ★★★

- **Plain idea:** four layers of memory, from shortest to longest.

| State | What it is | Lifetime | Typical store |
|---|---|---|---|
| Run state | where one execution is now: step count, pending tool calls, plan, status | one run | memory, or saved if the run can pause |
| Checkpoint | a snapshot of run state at a step boundary, so the run can resume or replay | per step, kept for a while | framework checkpointer, workflow engine |
| Session | one conversation: its message history and thread-level data | hours to months | Postgres, Redis, DynamoDB, framework session service |
| Long-term memory | facts that outlive sessions: preferences, past outcomes | months and years | per-user DB or vector store |

- **Worked example:** a user chats about an order today and a return tomorrow.
  - Two sessions; the second can recall "prefers email" from long-term memory.
  - In session one, the message "refund order 42" starts a run of five steps and five checkpoints.
  - The run pauses for approval at step four and the server restarts.
  - Another server loads the latest checkpoint and continues from step four.
- **Checkpoints and graphs:** a graph framework writes a checkpoint after every node. Resume restarts from the last good node, so a node that already did a side effect may run again. Make those nodes idempotent ([1graph.md](1graph.md)).
- **Stateless harness, corrected:** it does not mean each question is independent. It means the process holds no state between requests. Each request loads the session by ID, so the conversation continues, and any instance can serve it.
- **Why that matters:** deploys, crashes and autoscaling don't lose work. The model itself is also stateless, so history is resent each call.
- **Rule:** nothing that matters lives in process memory. Details: 2memory-state.md.

---

## 6. Deployment shapes
`software` ★★★

- **Plain idea:** the harness is a module. The question is which process hosts it, and who owns its scaling.
- **Why "inside the API service" couples things:** a long-held model stream and a quick CRUD call then share instances, deploys and failure. The harness mostly waits; the API serves many small requests. They scale differently.

| Shape | How | Good at | Weak at | Choose when |
|---|---|---|---|---|
| A. Embedded in the product backend | harness is a library inside the BFF or API | simplest; no extra hop | coupled deploys and scaling | MVP, small team |
| B. Dedicated harness service ★★★ | BFF calls an agent service over gRPC or HTTP streaming | independent scaling, owners and releases | one more hop; contract to maintain | production default |
| C. Queue and workers | API enqueues; workers run agents; events flow back by pub/sub | long runs, retries, smooth load | async UX; more parts | runs over ~30 seconds, batch |
| D. Several agent services | one per domain (HR, IT, finance), plus a router or orchestrator | team ownership | routing quality; cross-service tracing | many domains and teams |
| E. Managed runtime | AWS Bedrock AgentCore Runtime; Google's Agent Runtime (formerly Vertex AI Agent Engine) | session isolation, scaling, built-in tracing | provider lock-in; less control | want less to operate on one cloud |
| F. Serverless functions | each step or tool in a function | pay per use | timeouts and cold starts | short, bursty tools |

### 6.1 BFF and the harness service
- **BFF owns** what the UI needs: auth, shaping data for screens, fan-out of the stream, rate limits.
- **Harness service owns** what the agent needs: loop, tools, state, policy.
- **The contract between them** (define it first, version it)
  - Run: session ID, user, message in; an event stream out.
  - Cancel: by run ID.
  - Resume: run ID plus an approval decision or input.
  - Get run: status and result.
- **Decoupling:** the BFF never imports the agent framework. It receives canonical events and maps them to UI events ([0edge-com.md](0edge-com.md)).

### 6.2 Several agent services and A2A
- **Inside your company:** gRPC between services. It gives typed contracts and streaming; it is still an API, just binary and typed.
  - Browsers get REST plus SSE; services get gRPC.
- **Across teams or vendors:** A2A. Each agent publishes an agent card (what it does, endpoint, auth). A caller sends a task and watches its state: working, input-required, completed.
- **Use A2A when:** you don't own the other agent, frameworks differ, tasks run long, and you want discovery.
- **Don't use A2A when:** you own both sides. Use an in-process sub-agent or gRPC.
- **Typical layout:** a router agent in front picks a domain agent service. Each domain service is deployed and scaled separately.

### 6.3 Cloud mapping
- **AWS:** API Gateway or ALB, ECS or Lambda, Bedrock (models), AgentCore (runtime, memory, identity, gateway, observability, policy, evaluations), DynamoDB or Aurora, SQS, CloudWatch.
- **Google Cloud:** Cloud Run, Gemini models, the agent platform's Agent Runtime, Sessions and Memory Bank, Cloud SQL or Firestore, Pub/Sub, Cloud Trace. Product names have been changing; check current docs ([5adk.md](5adk.md)).
- 🗣 "Inline for an MVP, a dedicated harness service for production, a queue once runs get long, a managed runtime when I want less to operate."

---

## 7. Scaling to 100k–1M users
`software` ★★★

- **Plain idea:** users aren't the load. Concurrent runs and tokens per minute are.
- **Worked example (order of magnitude; assumptions stated)**
  - 1M registered users; 10% active daily = 100k; 5 runs each = 500k runs/day.
  - Peak hour takes 15% = 75k runs/hour ≈ 21 runs/second.
  - Each run lasts ~20 seconds, so about 420 runs are in flight; allow 3× bursts, so ~1,200.
  - Each run: 4 model calls of ~8k tokens in = ~32k input tokens. That's ~2.4B tokens per peak hour, ~40M per minute.
- **What the numbers say**
  - Connections are easy: ~1,200 concurrent streams is a few instances.
  - Tokens are the limit: provider quotas and cost dominate. That's why prompt caching, smaller models for easy steps, and context trimming matter.
- **Scaling levers**
  - Stateless harness instances; autoscale on active runs.
  - One run at a time per session (lock or queue), many sessions in parallel.
  - Shared stores that scale horizontally: DynamoDB or sharded Postgres by session ID; Redis for event logs.
  - Model gateway with several providers and regions; per-tenant concurrency and token quotas.
  - Queue with backpressure; shed or defer low-priority work.
- **Per-user data access:** retrieval and tools filter by user or tenant in the query, not in the prompt.
- 🗣 "At scale the bottleneck is tokens per minute and cost, not connections. I design the quota and caching story first."

---

## 8. System design view: the big decisions
`boundary` ★★★

| Decision | Options | How to decide |
|---|---|---|
| Control shape | single call, workflow, loop, graph, multi-agent | is the path known? ([1harness.md](1harness.md)) |
| Sync vs async | stream in the request vs run ID and queue | run length and failure tolerance |
| Model access | direct SDK vs gateway | gateway once you have several models, keys or teams |
| Build vs adopt harness | own loop, agent SDK, managed runtime | team skills, control needs, cloud commitment |
| Hosting | embedded, dedicated service, managed runtime | ops capacity; need for independent scaling |
| Tool integration | in-process functions vs MCP servers | MCP when tools are shared across agents or teams |
| State | in-process vs external store | external for anything resumable or audited |
| Safety | prompt rules vs code checks | code for anything that matters ([4guardrails.md](4guardrails.md), [4access.md](4access.md)) |
| Quality | manual testing vs eval gate | eval gate before any prompt or model change ([4evals.md](4evals.md)) |

- **Default first production architecture**
  - A dedicated, stateless harness service behind the BFF, streaming events.
  - Gateway for models; typed tools, with MCP for shared ones.
  - Postgres or DynamoDB for sessions; vector index for knowledge; instructions in a versioned store.
  - Guardrails and approval in the harness; OpenTelemetry traces to one backend ([4observability.md](4observability.md)); eval gate in CI.
  - Queue and workers when runs pass ~30 seconds.

---

## 9. Failure modes
`boundary`

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Provider outage | model API down or rate-limited | error rate per provider | gateway fallback; degrade to a simpler path |
| Request timeouts | long runs inside a sync request | gateway or LB timeouts | run ID and queue; stream progress |
| State lost on deploy | state kept in process memory | runs vanish during rollouts | external session store and checkpoints |
| Tenant data leak | retrieval or tools not filtered by user | cross-tenant eval cases fail | filter in the query; per-user tool credentials |
| Cost spike | loops, retries, long contexts | cost per task over baseline | budgets per run; cost alerts |
| Blind debugging | no trace across components | "can't reproduce" on bad answers | one trace ID from client to tool calls |
| Config drift | prompt or policy changed without versioning | behavior changes with no deploy | version config; stamp traces with the version |

---

## Where this fits
- **Place:** L8 and L9 of [1a-bp.md](../1a-bp.md). The frame every other group-1 doc plugs into.
- **Time it deserves:** 30 minutes; §3, §5, §6 and §7. It opens any agentic design answer.
- **I should be able to…**
  - Draw the zones and name a component in each.
  - Explain run, checkpoint, session and long-term memory with one example.
  - Say why a dedicated harness service beats embedding it, and where A2A fits.
  - Do the back-of-envelope: users to runs to tokens per minute.

## References
1. [Anthropic — Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — building blocks.
2. [Amazon Bedrock AgentCore docs](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html) — managed runtime, memory, identity, gateway, observability, policy.
3. [A2A protocol](https://a2a-protocol.org/) — agent cards and task states.
4. [OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — tracing across model and tool calls.
