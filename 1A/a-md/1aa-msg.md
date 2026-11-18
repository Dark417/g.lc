# 1aa-msg — How Agent System Components Communicate (Lean)

> Every component, every pair that talks, the protocol on each wire, and what each message must carry. Concepts only.
> Group 1 (agent core). Field-level detail with code: [1aa-msg-c.md](1aa-msg-c.md). Client side: [0edge-com.md](0edge-com.md). Hub: [1harness.md](1harness.md).
> Concept level, no code (AGENTS.md §8b). Last updated: 2026-11-16.
> **Term:** a "wire" is a connection between two components. "Edge" means the client-facing boundary ([0edge-com.md](0edge-com.md)).
> **Version note:** the detailed doc pins MCP revision 2025-06-18, A2A 0.3.x, and OpenTelemetry GenAI conventions at "Development". AWS release notes mention a newer MCP revision (2026-07-28). Check current specs before quoting.

## Index
- [0. One-minute version](#0-one-minute-version)
- [1. Concept: hub and spokes](#1-concept-hub-and-spokes)
- [2. Components, by zone](#2-components-by-zone)
- [3. The wire map](#3-the-wire-map)
- [4. Protocols and framing](#4-protocols-and-framing)
- [5. Contracts: what every message carries](#5-contracts-what-every-message-carries)
- [6. Data load: how big and why it grows](#6-data-load-how-big-and-why-it-grows)
- [7. Each wire in one paragraph](#7-each-wire-in-one-paragraph)
- [8. System design view: choosing wires](#8-system-design-view-choosing-wires)
- [9. Failure modes](#9-failure-modes)
- [Where this fits](#where-this-fits)
- [References](#references)

---

## 0. One-minute version
- **What:** about 20 components in six zones. The harness is the hub; almost every message passes through it.
- **Why:** most agent bugs are contract bugs on a wire: a tool call with no result, context lost in a handoff, a result too big for the window.
- **How:** five wire families cover nearly everything.
  - Model APIs: HTTPS, JSON, streamed over SSE.
  - Tools: MCP, which is JSON-RPC over stdio or streamable HTTP.
  - Agents: A2A, JSON-RPC over HTTPS built around a task.
  - UI: SSE or WebSocket, optionally AG-UI events.
  - Telemetry: OTLP spans with W3C trace context.
- **Catch:** the model is a pure function of the request body. What isn't in the payload doesn't exist for it.
- 🗣 "The model never opens a connection. It emits a structured intent, the harness executes it, and every wire carries who, which call, which conversation, which trace, and which version."

---

## 1. Concept: hub and spokes
`boundary` ★★★

- **Plain idea:** an air-traffic tower. Planes (model, tools, agents) never talk to each other; every instruction goes through the tower (harness).
- **The pain before standard wires (2022–2023)**

| Pain | Fix | Who and when |
|---|---|---|
| tool calls parsed from prose | native function calling: structured call blocks | model providers, mid-2023 |
| N apps times M tools of custom adapters | MCP: one tool server, any client | Anthropic, Nov 2024 |
| no agent-to-agent standard | A2A: agent card plus task lifecycle | Google Apr 2025; Linux Foundation Jun 2025 |
| no agent-to-UI stream standard | AG-UI typed events | CopilotKit, 2025 |
| no trace shape for model and tool steps | OpenTelemetry GenAI conventions | OpenTelemetry, 2024 onward |

- **How the hub works**
  1. The harness builds one request from many sources.
  2. The model returns text or a structured tool call.
  3. The harness checks policy, then runs the call on the right spoke.
  4. It appends the result and calls the model again.
- **Why the shape wins:** one place for policy, budgets, approval, tracing and caching; any spoke can be swapped.
- **The catch:** the hub is a bottleneck and single point of failure. Keep it stateless and state durable.
- **Two sanctioned exceptions to "the model never calls out"**
  - Server-side tools the provider runs (web search, code execution).
  - MCP sampling: a tool server asks the client's model, still through the client.
- 🗣 "Harness is the hub: the model proposes, the harness disposes."

---

## 2. Components, by zone
`boundary` ★★★

| Zone | Components | Examples |
|---|---|---|
| Edge and identity | client UI; API gateway or BFF; identity provider | React chat, CLI, Slack bot; FastAPI, Spring Boot; Okta, Cognito, Entra |
| Core | harness; model gateway; LLM inference | ADK Runner, LangGraph, Claude Agent SDK; LiteLLM, Portkey; Claude, GPT, Gemini, vLLM |
| Tools | in-process tools; MCP servers; sandbox; external systems | typed functions; GitHub or your own MCP server; E2B, Modal; REST, Postgres, Stripe |
| Agents | sub-agent (same runtime); remote agent | ADK agent tool, Claude subagent; any A2A server |
| Data | session store; memory store; retrieval stack; artifact store | ADK sessions, LangGraph checkpointer; Memory Bank, Mem0; pgvector, Pinecone; S3 |
| Control and ops | guardrail or policy engine; human approver; queue or workflow engine; observability and evals | Bedrock Guardrails, OPA; Slack or UI card; SQS, Temporal; Langfuse, Phoenix |

- **State:** only the data zone, the queue, the sandbox and external systems hold state. The harness, gateway and tools should not.

---

## 3. The wire map
`boundary` ★★★

```
 client --SSE/WS--> BFF --call/stream--> HARNESS --HTTPS--> model gateway --> LLM
 client --OIDC--> identity              |--> in-process tools
                                        |--JSON-RPC--> MCP server --> business systems
                                        |--A2A--> remote agent
                                        |--> stores, retrieval, sandbox, guardrail, human, queue
 every component --OTLP--> observability
```

| Wire | Pair | Protocol | Carries |
|---|---|---|---|
| W1 | client to BFF | HTTPS plus SSE or WebSocket | user turn in; event stream out |
| W2 | client to identity | OIDC authorization code with PKCE | tokens |
| W3 | client to object store | presigned upload | file bytes |
| W4 | BFF to harness | in-process, or internal HTTP or gRPC | session, user, message; events back |
| W5 | harness to model | provider chat API over HTTPS, SSE streaming | full context in; text or tool call out |
| W6 | harness to in-process tool | function call | arguments in; result out |
| W7 | harness to MCP server | MCP over stdio or streamable HTTP | tool list, tool calls, resources, prompts |
| W8 | MCP server to harness | MCP sampling, elicitation, roots | server asks for a model call or user input |
| W9 | harness to identity | OAuth with audience-bound tokens | a token for one MCP server |
| W10 | tool to business system | native: REST, SQL, gRPC | business request |
| W11 | harness to sub-agent | framework-internal | task in; summary out |
| W12 | harness to remote agent | A2A over HTTPS with SSE and webhooks | message, task, artifacts |
| W13 | harness to stores | SQL, Redis, vendor API | events, state deltas, facts |
| W14 | harness to retrieval | HTTPS or SQL | query in; chunks out |
| W15 | harness to sandbox | session API | code in; output out |
| W16 | harness to guardrail | HTTPS or in-process | content in; verdict out |
| W17 | harness to human approver | event out; POST back, or webhook | proposed action; decision |
| W18 | harness to queue or workflow | SQS, Pub/Sub, workflow engine API | job envelope with idempotency key |
| W19 | everything to observability | OTLP | spans, metrics, logs |

### Pairs that must not talk directly
| Forbidden | Why | Correct path |
|---|---|---|
| client to model | leaks keys; bypasses policy and budget | client to BFF to harness to model |
| model to tool | the model only emits tokens | model emits a call; harness executes |
| MCP server to model | server would need keys; user loses consent | sampling request to the client |
| remote agent to your database | foreign code writing your data | remote agent returns an artifact; your adapter writes |
| tool to tool | hidden coupling, untraceable | compose in the harness or inside one server |
| sub-agent to user | breaks single conversation owner | sub-agent returns to parent; parent speaks |

---

## 4. Protocols and framing
`software` ★★★

- **Each wire is a four-layer stack:** transport (TCP+TLS, stdio), framing (HTTP, SSE, WebSocket), message (REST JSON, JSON-RPC, gRPC), semantics (chat schema, MCP, A2A, AG-UI, OTLP).
- **MCP and A2A both use JSON-RPC 2.0.** They differ in methods and objects, not framing.

| Protocol | What it is | Good at | Weak at | Choose when |
|---|---|---|---|---|
| Provider function calling | tool schemas in the model request; structured call out | native; no extra infra | you build the execution side per app | always (the model side) |
| MCP | standard tool execution side: discover, call | write once, any client uses it | session handling; token cost of tool lists | tools shared across agents or teams |
| A2A | tasks between agents with a lifecycle | long-running, opaque peers, discovery | heavier; young ecosystem | calling an agent you don't own |
| AG-UI | typed agent-to-UI events | frontend decoupled from framework | a mapping layer | rich UI with tool and state events |
| REST or OpenAPI | plain HTTP | universal, cacheable | no model-facing discovery | backend behind a tool |
| gRPC | typed binary RPC over HTTP/2 | fast, typed, streaming | not browser-native | internal hops, BFF to harness |

- **Framing**

| Option | Direction | Choose when |
|---|---|---|
| SSE | server to client | default for tokens and events |
| WebSocket | both | voice, barge-in, live collaboration |
| stdio | both, local | local MCP servers |
| Webhook | server to your URL | hours-long tasks, async approvals |
| Polling | client pulls | fallback |

- **Pick:** function calling plus MCP for tools; A2A only across ownership boundaries.
- **Deciding variable:** do you own both sides? Yes: in-process tool or sub-agent. No, and it's a tool: MCP. No, and it's an autonomous agent with long tasks: A2A.
- 🗣 "I own both sides, in-process. A shared tool, MCP. Someone else's agent, A2A."

---

## 5. Contracts: what every message carries
`boundary` ★★★

### 5.1 The six envelope classes
| Class | Question | Typical carrier | Breaks if missing |
|---|---|---|---|
| Auth | who, with what rights? | bearer token or API key | anyone calls anything |
| Correlation | which call is this the answer to? | JSON-RPC ID, tool-use ID | results attach to the wrong call |
| Context | which conversation or task? | session ID, context ID | turns mix across users |
| Trace | which end-to-end run? | W3C `traceparent` | can't debug across hops |
| Idempotency | is this a retry? | idempotency key | double charge |
| Version | which schema? | version header or field | silent misparse after an upgrade |

- 🗣 "Every hop answers six questions: who, which call, which conversation, which trace, is it a retry, which version."

### 5.2 One model, many dialects
- Every chat message is a role plus an ordered list of typed parts: text, media, tool call, tool result, reasoning, citations.
- **Providers differ in field names, not in concept.** Tool definition, tool call, tool result and stop reason exist in all of them.
- **Traps**
  - OpenAI tool arguments arrive as a JSON string that can be invalid. Parse defensively.
  - Reasoning blocks may be signed. Pass them back unchanged or the provider rejects the request.
  - Every tool call needs a matching result before the next request.
- **Canonical internal model:** most mature stacks define their own message, part and event schema and keep provider types at the boundary.

### 5.3 Tool contract
- A tool = name, description, and an argument schema. The description is a prompt; the schema is a validator.
- **Best practices**
  - Enums over free strings prevent invented values.
  - Rejecting unknown fields stops invented arguments reaching production.
  - Patterns on IDs let the model fix validation errors.
  - Write tools take an idempotency key.
  - Output schemas (MCP) or strict mode (OpenAI) make results parseable.

### 5.4 Run-state contracts
- **Framework events:** ADK records every model output, tool call, tool result and state change as an event with an author, a branch for parallel sub-agents, and state changes attached.
- **A2A task states:** submitted, working, completed; failed, canceled, rejected; and two pause states, input-required and auth-required. Input-required is how a remote agent asks a question back.

### 5.5 Versioning
- Pin every version explicitly. Treat a spec or provider bump as a deploy.
- Carriers: provider version header, MCP protocol version at initialize, A2A version in the agent card, OTel schema URL.

---

## 6. Data load: how big and why it grows
`software` ★★

- **Anatomy of one model request:** a stable prefix (system prompt, tool schemas, memory facts) then a volatile tail (history, retrieved chunks, tool call and result pairs, current message). Keep the stable part first so the provider's prefix cache hits.
- **Order-of-magnitude sizes**

| Message | Typical size | Grows with | Bound it with |
|---|---|---|---|
| Request, step 1 | 3–6k tokens | system plus tools | lean prompt, tool filter |
| Request, step N | 10–60k tokens | history plus tool results | compaction, result caps |
| Response | 50–1k tokens | tool arguments or answer | max tokens |
| MCP tool list | ~100–300 tokens per tool | tool count | tool filter; about ten tools per agent |
| Tool result | unbounded | rows returned | paginate; cap about 2–4k tokens |

- **Why loop cost is quadratic:** each step resends history. If each step adds about 2k tokens, ten steps total roughly 140k input tokens, not 50k. Cost grows about with the square of steps.
- **Levers:** prompt caching, compaction, pruning old tool results to pointers, server-side state (less upload, same tokens billed).
- **Streaming:** one answer is hundreds of small events. Tool-call arguments stream as fragments and parse only after the block ends. BFFs either forward deltas or coalesce them (about every 50 ms).
- 🗣 "Each step resends the history, so cost grows with the square of steps. Caching and compaction are the levers."

---

## 7. Each wire in one paragraph
`boundary` ★★

- **W1 client to BFF:** POST for input, SSE for output, event IDs for replay ([0edge-com.md](0edge-com.md)).
- **W5 harness to model:** one request body per step; stream out; branch on the stop reason; handle truncation.
- **W7 harness to MCP:** initialize, list tools, call tools. Remote servers use streamable HTTP; local ones use stdio and must log to stderr only.
- **W9 authorization:** OAuth with tokens bound to one server; never forward the user's token to another service ([4access.md](4access.md)).
- **W11 sub-agent:** task in, structured summary out; the parent speaks to the user.
- **W12 remote agent:** read the agent card, send a message, follow task states over SSE, poll, or webhook.
- **W13 stores:** read at the start of a run, write deltas per step; one writer per session.
- **W15 sandbox:** session-scoped; code in, output and artifacts out; no secrets inside.
- **W16 guardrail:** content and source in; verdict out ([4guardrails.md](4guardrails.md)).
- **W17 human approver:** paused run, structured request, decision back ([0edge-com.md](0edge-com.md) §6).
- **W18 queue:** job envelope with an idempotency key; the trace context in message attributes.
- **W19 telemetry:** spans per model and tool call; the trace ID survives every hop ([4observability.md](4observability.md)).

---

## 8. System design view: choosing wires
`boundary` ★★★

| Decision | Options | How to decide |
|---|---|---|
| Tool wire | in-process, MCP, REST behind a tool | MCP when shared; in-process when owned |
| Agent wire | in-process sub-agent, gRPC service, A2A | ownership and team boundaries |
| UI wire | SSE, WebSocket, AG-UI on top | SSE unless the client interrupts |
| Internal model schema | provider types vs your own | your own, mapped at the edge of the system |
| Trace propagation | headers only vs headers plus queue attributes | both; async hops break traces |
| Payload budgets | none vs per-layer token budgets | budgets per layer, alerted like latency |

- **Default:** SSE plus POST to clients; gRPC between your services; function calling plus MCP for tools; A2A across ownership boundaries; one internal event schema; OTLP everywhere; versions pinned.
- **Zero trust between agents:** treat every A2A and MCP peer as a third party: authenticate it, scope it, validate what it returns.

---

## 9. Failure modes
`boundary`

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Orphan tool call | harness crashed between call and result | provider rejects the next request | validate pairing; synthesize an error result on resume |
| Invalid tool arguments | bad JSON or types | schema validator errors | return the error to the model; strict mode |
| Context blow-up | huge tool result | tokens per turn spike | cap, paginate, store by pointer |
| Reasoning block rejected | edited or dropped signed block | provider error | pass back unchanged |
| Silent truncation | max-tokens stop ignored | answers end mid-sentence | branch on stop reason |
| Corrupted stdio stream | server logs to stdout | parse errors | logs to stderr only |
| Session expired | server restart | not-found with session ID | re-initialize; stateless tools |
| Confused deputy | token forwarded upstream | audit shows reuse | audience checks; no passthrough |
| Lossy handoff | sub-agent returns free text | parent invents details | structured return with evidence |
| Stuck remote task | task stays working | task age over SLA | timeout, cancel, push config |
| Indirect injection | instructions in a tool result or document | unexpected write calls | treat as data; gate writes |
| Double side effect | retry without idempotency key | duplicate charges | key from business arguments |
| Stream never arrives | proxy buffers SSE | first token time equals total time | disable buffering |
| Broken trace | async hop drops trace context | orphan spans | trace context in queue attributes |
| Schema drift | provider or MCP version bump | parse failures after deploy | pin versions; contract tests |

---

## Where this fits
- **Place:** L8 of [1a-bp.md](../1a-bp.md). The "wires" view of [1architecture.md](1architecture.md).
- **Time it deserves:** 30 minutes; §1, §3, §4 and §5.1. Open the code version only when building.
- **I should be able to…**
  - Name the five wire families and what each carries.
  - List the six envelope classes and what breaks without each.
  - Explain why the model never opens a connection, and the two exceptions.
  - Say when to use in-process, MCP, gRPC or A2A.

## References
1. [Model Context Protocol specification](https://modelcontextprotocol.io/specification) — lifecycle, transports, authorization.
2. [A2A protocol](https://a2a-protocol.org/latest/specification/) — agent card, task states, streaming, push.
3. [AG-UI protocol](https://docs.ag-ui.com/) — agent-to-UI events.
4. [OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — span and attribute names.
5. [W3C Trace Context](https://www.w3.org/TR/trace-context/) — `traceparent`.
