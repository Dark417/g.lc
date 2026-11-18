# 5openai-sdk — OpenAI Agents SDK

> The OpenAI Agents SDK as a harness: agents, handoffs, guardrails, sessions, human approval and tracing, and where it leaves work to you.
> Group 5 (frameworks). Overview and comparison: [5frameworks.md](5frameworks.md).
> Concept level, no code (AGENTS.md §8b). Last updated: 2026-11-16.
> **Source note:** details come from a third-party summary of the SDK's 2026 releases (Python 0.24, JS 0.22 at the time). Minor versions can break things; check current docs.

## Index
- [0. One-minute version](#0-one-minute-version)
- [1. Concept](#1-concept)
- [2. How the SDK manages the harness concerns](#2-how-the-sdk-manages-the-harness-concerns)
- [3. Handoffs vs agents as tools](#3-handoffs-vs-agents-as-tools)
- [4. Guardrails and their gaps](#4-guardrails-and-their-gaps)
- [5. Sessions, approvals and run state](#5-sessions-approvals-and-run-state)
- [6. What you still own](#6-what-you-still-own)
- [7. System design view: choosing](#7-system-design-view-choosing)
- [8. Failure modes](#8-failure-modes)
- [Where this fits](#where-this-fits)
- [References](#references)

---

## 0. One-minute version
- **What:** a lightweight framework: agents with instructions and tools, a runner loop, handoffs between agents, guardrails, sessions and built-in tracing.
- **Why:** few concepts, fast to start, good multi-agent routing, and approvals that pause and resume.
- **How:** define agents; the runner loops until a final output; sessions store history; approvals surface as interruptions you resolve and resume.
- **Catch:** fewer durability features than a graph runtime. Tracing defaults to OpenAI's dashboard.
- 🗣 "Small surface: agent, tool, handoff, guardrail, session. Durable multi-day workflows need more than the SDK."

---

## 1. Concept
`AI` ★★★

- **Plain idea:** a runner calls the model with an agent's instructions and tools, executes tool calls, and repeats until the agent gives a final output or hands off to another agent.
- **Picture it:** a customer-service router.
  1. A triage agent reads the message.
  2. It hands off to the billing agent, which takes over the conversation.
  3. Billing calls a refund tool; the tool needs approval, so the run pauses.
  4. After approval, the run resumes and returns the final answer.
- **How it works**
  1. Run the starting agent with the input (and a session, if any).
  2. The model returns text, a tool call, or a handoff.
  3. Guardrails run at their checkpoints.
  4. Tools execute; results go back; the loop continues.
  5. Tracing records the run.
- **The catch:** guardrail and session features have rules about where they run. Read them ([§4](#4-guardrails-and-their-gaps)).
- 🗣 "Run, tool or handoff, repeat. Approvals pause the run and hand me its state."

---

## 2. How the SDK manages the harness concerns
`boundary` ★★★

| Concern | How it's handled |
|---|---|
| Loop | the runner; turn limits |
| Context | session history plus per-run input; a compaction wrapper shortens stored history after each turn |
| Session history | session classes: SQLite, Redis, SQLAlchemy, MongoDB, Dapr, or OpenAI's server-side conversations; TypeScript has fewer built-ins and a small interface to implement |
| Run state | a serializable run state when a run is interrupted |
| Long-term memory | sandbox agents have a memory feature that writes lessons to files; otherwise your own store |
| Tools | function tools, hosted tools, shell and patch tools, MCP servers, agents as tools, and a way for the model to run a short program that calls allowed tools |
| Human approval | an approval flag on tools; pending approvals appear as interruptions |
| Guardrails | input, output and tool guardrails |
| Tracing | on by default to OpenAI's traces dashboard; task and turn spans; export to other backends |
| Edge | stream events; you build SSE; realtime and voice agents exist (WebSocket, WebRTC in JS) |
| Hosting | your server; sandbox agents run code in local, Docker or hosted sandboxes (E2B, Modal, Daytona, Cloudflare, Vercel and others) |

- **Limits to know:** sessions can't be combined with server-side conversation IDs in the same run. Server-managed conversations don't support handoff input filters.
- **Sandbox agents:** an agent plus a workspace manifest and a sandbox client. The local Python client has no OS-level confinement on Linux, so use Docker or a hosted sandbox for untrusted input.

---

## 3. Handoffs vs agents as tools
`AI` ★★★

| | Handoff | Agent as tool |
|---|---|---|
| Control | the specialist takes over the rest of the turn | the manager keeps control and writes the final answer |
| How the model sees it | a transfer function per target agent | an ordinary tool |
| History passed | can be filtered (for example strip earlier tool calls) | only the tool input |
| Good at | triage and routing to owners | focused lookups under one coordinator |
| Risk | context loss or bloat at the handoff | the specialist can't ask the user |

- They can be combined: a triage handoff, then agents-as-tools inside the specialist.
- Patterns in general: [1orchestration.md](1orchestration.md).
- 🗣 "Handoff gives away control. Agent-as-tool lends it."

---

## 4. Guardrails and their gaps
`boundary` ★★★

| Guardrail | Runs | Notes |
|---|---|---|
| Input | only for the first agent in a chain | runs in parallel with the model by default; a blocking mode waits for the check |
| Output | only for the agent that produces the final output | |
| Tool | on guarded function-tool calls, including local MCP tools when configured | handoff calls and hosted or built-in tools skip this path |

- **What this means:** a multi-agent flow can pass through agents whose inputs were never checked. Add your own checks at handoffs and on hosted tools.
- **Redaction:** blocked terminal tool output can be replaced with a configurable message.
- General design: [4guardrails.md](4guardrails.md).
- 🗣 "SDK guardrails are per-checkpoint, not global. I map every path to a check."

---

## 5. Sessions, approvals and run state
`software` ★★★

- **Sessions:** pick a store by durability need. In-memory only for development; SQL or Redis for production. Wrappers add encryption with a TTL (Python) or history compaction.
- **Approvals**
  1. A tool marked as needing approval is requested by the model.
  2. The run stops; pending approvals are returned as interruptions.
  3. You show them to a person. Decisions can be "always" or "never" for the rest of the run.
  4. You resume from the saved run state with the decisions.
- **Security note:** the run state loaded from text is not authenticated. Store it server side. Don't round-trip it through the browser.
- **Resume anywhere:** because run state is serializable, another server can continue the run, if you stored it.
- Edge mechanics: [0edge-com.md](0edge-com.md) §6.

---

## 6. What you still own
`boundary` ★★

- Durable storage choice, locking and retention for sessions.
- Where run state is stored between approval and resume.
- The BFF and SSE layer; auth; per-tenant limits.
- Guardrails on paths the SDK skips.
- Tracing destination: the default sends data to OpenAI's dashboard, and can't be disabled under zero data retention.
- Evals, cost budgets and the eval gate.
- Long-running durable workflows: use a workflow engine around it.

---

## 7. System design view: choosing
`boundary` ★★★

| Decision | Options | How to decide |
|---|---|---|
| Session store | SQL, Redis, OpenAI-hosted conversations | SQL or Redis for control and portability; hosted for least work |
| Multi-agent | handoffs, agents as tools, both | handoffs for routing to owners; tools for coordination |
| Tracing | default dashboard, export to your backend | your backend for data-control needs |
| Sandbox | local, Docker, hosted | Docker or hosted for untrusted code |
| Durability | SDK only, plus a workflow engine | add Temporal or Step Functions for hours-long runs |

- **Choose it when:** you use OpenAI models, want quick routing and approvals, and runs are short to medium.
- **Look elsewhere when:** you need graph checkpoints with time travel, a Google or AWS managed runtime, or the deepest file and coding tools.
- **Default:** Agents SDK with SQL or Redis sessions, handoffs for routing, approvals for risky tools, your own checks at handoffs, traces exported to your backend, a workflow engine for long runs.

---

## 8. Failure modes
`boundary`

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Unchecked agent in a chain | input guardrails only on the first agent | audit finds unchecked inputs | checks at handoffs |
| Tool guardrail skipped | hosted tool or handoff call | missing checks in traces | wrap or restrict those tools |
| Tampered run state | state sent through the client | audit mismatch | server-side storage; expiry |
| Trace data leaves the boundary | default dashboard tracing | compliance review | export to your backend; redact |
| Session conflict | two writers to one session | corrupted history | lock or queue per session |
| Version break | minor bump changes behavior | failing tests after upgrade | pin exact versions |

---

## Where this fits
- **Place:** L9 of [1a-bp.md](../1a-bp.md); the lightweight handoff-oriented SDK.
- **Time it deserves:** 25 minutes; §3, §4 and §5.
- **I should be able to…**
  - Compare handoff and agent-as-tool.
  - Name the session stores and say which are for production.
  - Walk the approval and resume flow, and the security rule for run state.
  - State where the guardrails don't run.

## References
1. [OpenAI Agents SDK in late 2026](https://www.developersdigest.tech/blog/openai-agents-sdk-whats-new-2026) — sessions, sandbox, approvals, handoffs, guardrails, tracing (third-party summary).
2. [OpenAI Agents SDK — Python docs](https://openai.github.io/openai-agents-python/) — official docs.
3. [OpenAI Agents SDK — sessions (JS)](https://openai.github.io/openai-agents-js/guides/sessions) — session interface.
