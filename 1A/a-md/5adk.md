# 5adk — Google ADK And Google's Agent Platform (Vertex AI)

> Google's Agent Development Kit (ADK) as a harness, and the Google Cloud platform around it: managed runtime, sessions, memory, safety and tracing.
> Group 5 (frameworks). Overview and comparison: [5frameworks.md](5frameworks.md). Older reference: [4agent-architecture-adk-reference.md](4agent-architecture-adk-reference.md).
> Concept level, no code (AGENTS.md §8b). Last updated: 2026-11-16. Cells marked `*` come from background knowledge and were not re-checked.

## Index
- [0. One-minute version](#0-one-minute-version)
- [1. Concept](#1-concept)
- [2. How ADK manages the harness concerns](#2-how-adk-manages-the-harness-concerns)
- [3. Agents and sub-agents](#3-agents-and-sub-agents)
- [4. Google's platform around ADK (Vertex AI)](#4-googles-platform-around-adk-vertex-ai)
- [5. What you still own](#5-what-you-still-own)
- [6. System design view: choosing](#6-system-design-view-choosing)
- [7. Failure modes](#7-failure-modes)
- [Where this fits](#where-this-fits)
- [References](#references)

---

## 0. One-minute version
- **What:** ADK is an open-source agent framework. It gives you agent types, a runner (the loop), sessions, memory services, callbacks, tools and evals.
- **Why:** it covers the full harness in one design, and it's the default for this project's discussions.
- **How:** you define agents and tools; a Runner executes them, emitting events; services store sessions and memory; you deploy to Cloud Run, GKE or Google's managed Agent Runtime.
- **Catch:** it is deepest on Google Cloud. The platform names and managed features have changed several times.
- 🗣 "ADK is the harness. The Runner is the loop engine, sessions hold history, the memory service holds long-term facts, and Agent Runtime is where it can be hosted."

---

## 1. Concept
`AI` ★★★

- **Plain idea:** every step an agent takes becomes an event written to a session. The Runner replays the session into context for the next step.
- **Picture it:** a support agent with a "billing" sub-agent.
  1. A user message arrives with a session ID.
  2. The Runner loads the session (past events and state).
  3. The root agent runs; it may transfer to the billing agent or call it as a tool.
  4. Each model reply, tool call and tool result is an event, appended to the session.
  5. State changes ride on events, so saving the event log saves the state.
- **How it works (the parts)**
  - **Agent:** an LLM agent (instructions, model, tools) or a workflow agent (sequential, parallel, loop). Newer 2.x releases add graph-style workflows (per a late-2026 summary).
  - **Runner:** executes an agent against a session, streaming events.
  - **Session and state:** one conversation's events plus a key-value state.
  - **Memory service:** long-term, searchable knowledge across sessions.
  - **Artifact service*:** versioned files and blobs.
  - **Callbacks:** code before and after agent, model and tool steps.
- **The catch:** the event log is the source of truth. Anything not in events or state doesn't survive a restart.
- 🗣 "In ADK everything is an event. Session equals the event log plus state."

---

## 2. How ADK manages the harness concerns
`boundary` ★★★

| Concern | How ADK handles it |
|---|---|
| Loop | Runner runs the agent loop; workflow agents fix the order |
| Context | built from session events and state; instructions can read state values |
| Session history | session service: in-memory (default), database*, or managed (Google platform) |
| State scopes* | prefixes separate state: session-level (no prefix), per user (`user:`), app-wide (`app:`), temporary (`temp:`) |
| Run state | events and state deltas; long-running tools pause a run until an outside result returns |
| Long-term memory | memory service: in-memory (keyword matching, prototyping), Memory Bank (managed, model-extracted, semantic search), or a RAG-based service |
| Memory retrieval | a tool the agent calls on demand, or a preload tool that fetches each turn |
| Saving to memory | usually an after-agent callback that adds the finished session |
| Tools | function tools, MCP toolset, agent-as-tool, long-running tools; a confirmation flag asks a human first |
| Guardrails | callbacks and plugins around model and tool calls |
| Tracing | OpenTelemetry-based; Cloud Trace on Google* |
| Edge | a built-in dev server streams events over SSE; production needs your own BFF |
| Evals | built-in eval runner for test cases ([4evals.md](4evals.md)) |

- **Limits to know:** ADK documents restrictions on mixing certain built-in tools with function tools and with structured output; check the limitations page before designing around them.
- **Memory vs session in one line:** a session is one conversation; memory is what you search across conversations.

---

## 3. Agents and sub-agents
`AI` ★★★

| Mechanism | Control | Use |
|---|---|---|
| Sub-agents with transfer | the model hands the conversation to another agent (handoff) | triage and specialists |
| Agent as a tool | the parent calls the child and keeps control | focused lookups, parallel reads |
| Sequential workflow agent | fixed order | pipelines |
| Parallel workflow agent | concurrent branches | independent subtasks |
| Loop workflow agent | repeat until a condition or cap | review and revise |
| A2A (remote agents) | a call to an agent on another service; marked experimental in the summary I read | cross-team agents |

- **Parallel branches** keep separate histories so they don't interleave.
- **Pick:** workflow agents when the shape is fixed; transfer for routing; agent-as-tool when the parent must reason over results ([1orchestration.md](1orchestration.md)).

---

## 4. Google's platform around ADK (Vertex AI)
`software` ★★

- **Naming:** Google's docs now say "Gemini Enterprise Agent Platform" with "Agent Runtime" as the managed deployment service. The older names were Vertex AI Agent Builder and Vertex AI Agent Engine. Check which names your docs use.

| Piece | What it does | Maps to |
|---|---|---|
| Gemini and Model Garden | first- and third-party models behind one platform | model layer (and gateway-like access) |
| Agent Runtime (formerly Agent Engine) | managed hosting and scaling for agents; runs ADK, and other frameworks* | managed runtime ([1architecture.md](1architecture.md) §6) |
| Sessions | managed session storage | ADK session service in production |
| Memory Bank | managed long-term memory: generates, consolidates and retrieves memories; IAM conditions control access | ADK memory service |
| Model Armor* | screens prompts and responses for injection and sensitive data | guardrail checkpoint 1 and 5 ([4guardrails.md](4guardrails.md)) |
| Cloud Trace and Logging | traces and logs | observability ([4observability.md](4observability.md)) |
| Evaluation services* | scoring agent outputs | evals |
| Vector search and RAG engines | retrieval backends | RAG |

- **How they fit:** write the agent in ADK; deploy it to Agent Runtime; sessions and memory become managed services; Model Armor guards the edges; Cloud Trace shows runs.
- **Trade-off:** the managed pieces remove ops work and tie your data model to Google's service shapes.

---

## 5. What you still own
`boundary` ★★

- The edge: auth, SSE to the client, BFF, rate limits ([0edge-com.md](0edge-com.md)).
- Tenant isolation: user and tenant come from the token, not from the model.
- Policy store, rules in callbacks, approval UX.
- Eval set, gate in CI, production sampling.
- Cost budgets and quotas per user.
- Retention, deletion on request, and encryption for sessions and memory.
- Queues for runs longer than your request timeout.

---

## 6. System design view: choosing
`boundary` ★★★

| Decision | Options | How to decide |
|---|---|---|
| Hosting | Cloud Run or GKE vs Agent Runtime | Agent Runtime if you want managed sessions and memory; containers for control |
| Session store | in-memory (never in prod), database, managed | managed or database; always external in production |
| Memory | in-memory, Memory Bank, RAG, your own | Memory Bank for personalization on Google; your own if you need portability |
| Control style | LLM agents with transfer vs workflow agents | workflow agents for known processes |
| Languages | Python, TypeScript, Go, Java, Kotlin | team language; Python is most complete per the summaries |

- **Choose ADK when:** you're on Google Cloud, want one framework from prototype to managed hosting, and use Gemini.
- **Look elsewhere when:** you need explicit graph checkpoints with time travel (LangGraph), or you're deep in AWS (Strands plus AgentCore).
- **Default:** ADK workflow agents for fixed stages with LLM agents inside them, Agent Runtime sessions and Memory Bank, callbacks for checks, OpenTelemetry to Cloud Trace.

---

## 7. Failure modes
`boundary`

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| In-memory session service shipped | default left in place | history disappears on deploy | database or managed sessions |
| Memory writes forgotten | no callback saves sessions to memory | the agent can't recall earlier chats | add the after-agent save step |
| Stale memory | facts never consolidated or expired | wrong personalization | TTL and consolidation; user-visible memory |
| Tool-combination limits | mixing unsupported built-in and function tools | errors at startup | check the limitations page; split agents |
| Name drift | docs and consoles use new names | confusion in design reviews | note both names in the design doc |

---

## Where this fits
- **Place:** L9 of [1a-bp.md](../1a-bp.md); the default framework for this project.
- **Time it deserves:** 30 minutes; §1, §2 and §4.
- **I should be able to…**
  - Say what a session, state and memory service are, and what each stores.
  - Compare transfer, agent-as-tool and workflow agents.
  - Map Vertex AI pieces to harness concerns.

## References
1. [ADK documentation](https://adk.dev/) — agents, sessions, memory, tools.
2. [ADK — sessions and memory](https://adk.dev/sessions/memory/) — session and memory services.
3. [Memory Bank overview](https://docs.cloud.google.com/agent-builder/agent-engine/memory-bank/overview) — managed long-term memory.
4. [A2A protocol](https://a2a-protocol.org/) — agent-to-agent.
5. [Choosing an agent framework in late 2026](https://www.developersdigest.tech/blog/choosing-an-agent-framework-late-2026) — ADK 2.x state.
