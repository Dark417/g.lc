# 0edge-com — Edge Communication (Client To Agent Backend)

> How a client talks to an agent backend: streams, sessions, runs, reconnects, cancels, and approvals.
> Group 0 (foundations). Used by: [1architecture.md](1architecture.md), [1harness.md](1harness.md). Component-to-component wires: [1aa-msg.md](1aa-msg.md).
> Concept level, no code (AGENTS.md §8b). Last updated: 2026-11-16.
> **Term:** "edge" = the client-facing boundary (UI, API gateway, BFF). In [1aa-msg.md](1aa-msg.md), connections between components are called "wires".

## Index
- [0. One-minute version](#0-one-minute-version)
- [1. Concept](#1-concept)
- [2. Client types: same parts, different placement](#2-client-types-same-parts-different-placement)
- [3. Transport options](#3-transport-options)
- [4. Session, run, stream: the three IDs](#4-session-run-stream-the-three-ids)
- [5. What flows on the stream](#5-what-flows-on-the-stream)
- [6. The approval round trip](#6-the-approval-round-trip)
- [7. Scaling the edge](#7-scaling-the-edge)
- [8. System design view: choosing](#8-system-design-view-choosing)
- [9. Failure modes](#9-failure-modes)
- [Where this fits](#where-this-fits)
- [References](#references)

---

## 0. One-minute version
- **What:** the edge is where a user's message enters and where tokens, progress and approval requests go back out.
- **Why:** an agent run takes seconds to minutes. A plain request and response can't carry that.
- **How:** the client sends a message with a session ID. The backend starts a run and streams typed events back, usually over SSE.
- **Catch:** a connection is not a run. The client can drop and the run must survive; the client reconnects and catches up.
- 🗣 "The stream is a view of the run, not the run itself. If the connection dies, the run keeps going and the client replays what it missed."

---

## 1. Concept
`boundary` ★★★

- **Plain idea:** like ordering at a restaurant counter with a buzzer. You place the order (message), you get a ticket (run ID), and updates reach you while the kitchen (harness) works.
- **Picture it:** a support chat in a browser.
  1. The user types a question. The browser sends it with the session ID.
  2. The backend authenticates, starts a run, and opens a stream.
  3. Tokens arrive as the model writes. A "searching orders…" status appears during a tool call.
  4. The agent wants to issue a refund. The stream sends an approval request; the UI shows two buttons.
  5. The user clicks Approve. The run continues and the stream ends with "done".
- **How it works**
  1. Request in: message, session ID, auth token.
  2. The edge checks identity and rate limits.
  3. The harness runs; each step emits an event.
  4. Events go out on the stream, each with an ID.
  5. The client renders them and can reconnect, cancel or answer an approval.
- **The catch**
  - Proxies and load balancers buffer or time out long connections.
  - A browser tab can close mid-run. Who owns the run then?
- 🗣 "Design the edge around three things the client must be able to do: follow, cancel, and answer."

---

## 2. Client types: same parts, different placement
`boundary` ★★★

- **Plain idea:** a web chat and a coding agent have the same parts. What differs is where the harness and tools run.

| Client | Where the harness runs | Where tools run | Edge protocol | State lives |
|---|---|---|---|---|
| Web chat (claude.ai style) | provider or product servers | server side | HTTPS + SSE | server database |
| Mobile app | same as web | server side | SSE plus push notification for long runs | server database |
| CLI or IDE coding agent | a local process on the developer's machine | local files and shell | no server edge; the terminal is the edge. Only model calls go out | local transcript files |
| Cloud background agent | a cloud sandbox per task | inside the sandbox | webhook or notification when done; log stream to watch | task store |
| Chat platform bot (Slack) | your server | server side | inbound webhook; reply by API, editing a message | your store |
| Voice | server | server side | WebSocket or WebRTC | server database |
| Your product's embedded agent | your backend | server side | your BFF's API | your store |

- **Why it matters**
  - Local harness: permission prompts are local and tools touch the user's own machine. Risk is the user's machine.
  - Server harness: the multi-tenant problems appear (isolation, quotas, scale, who sees what).
- 🗣 "Same architecture, different placement. A coding CLI is the harness running on the user's laptop; a web chat is the harness running on mine."

---

## 3. Transport options
`software` ★★★

| Option | Direction | How it works | Good at | Bad at | Choose when |
|---|---|---|---|---|---|
| Request / response | client asks, server answers | one HTTP call | short, single-step answers | anything over a few seconds | no streaming needed |
| SSE (Server-Sent Events) ★★★ | server to client | one long HTTP response of small text events | tokens and progress; auto-reconnect with `Last-Event-ID` | one-way; proxies may buffer | default for agent UIs |
| WebSocket ★★ | both ways | upgraded persistent connection | live voice, barge-in, collaboration | stateful; harder through some proxies and load balancers | client must talk mid-stream |
| Long polling ★ | client pulls | request held open until data | works through anything | wasteful, higher latency | fallback only |
| Webhook / push notification ★★ | server to a URL or device | server calls out when done | hour-long runs, bots, mobile | client must host an endpoint; replay risk | run outlives the session |
| gRPC streaming ★★ | both ways | protobuf over HTTP/2 | internal hops, typed contracts | not browser-native | BFF to harness service |

- **Browser to BFF:** SSE for output; a normal POST for input, cancel and approvals. Two simple channels beat one clever one.
- **BFF to harness service:** gRPC server streaming, or HTTP with SSE. The BFF translates internal events to UI events.
- **Pick:** SSE plus POST by default. WebSocket only for voice or interruption mid-stream.
- 🗣 "SSE for the way out, POST for the way in. WebSocket only when the client needs to interrupt."

---

## 4. Session, run, stream: the three IDs
`boundary` ★★★

- **Plain idea:** three different things, three different IDs.

| ID | What it names | Lifetime | Used for |
|---|---|---|---|
| Session ID | one conversation or workspace | hours to months | loading history; continuity |
| Run ID | one execution, triggered by one message | seconds to hours | status, cancel, resume, billing |
| Event ID | one event on the stream | within a run | resume after a dropped connection |

- **Why separate them**
  - A session holds many runs. A run holds many steps.
  - Follow-up messages while a run is active need a rule: queue them, or interrupt the run.
  - Only one run per session should write state at a time. Use a per-session lock or queue.
- **Decouple the run from the connection**
  - The run executes in the harness (or a worker). The stream only reads its event log.
  - Events are written to a short-lived log (a Redis stream or a table) with increasing IDs.
  - On reconnect the client sends the last event ID it saw; the edge replays from there.
- **Disconnect is not cancel**
  - Closing the tab shouldn't kill a refund mid-way. Cancel is an explicit action: a separate call with the run ID.
  - Idle runs with no reader for N minutes can still be paused or stopped by policy.
- **Resume after approval or input**
  - A paused run waits in a store. A new call carrying the run ID and the decision resumes it, even on another server.
- 🗣 "Session is the thread, run is one turn of work, event ID is the bookmark."

---

## 5. What flows on the stream
`software` ★★

- **Plain idea:** the stream carries typed events, not just text. The UI can then draw tool cards, progress and approval buttons.

| Event type | Meaning | UI does |
|---|---|---|
| Message start / end | an answer begins or finishes | open or close a bubble |
| Text delta | a few tokens | append text |
| Tool call start / end | the agent is acting | show "checking order…" with the tool name |
| Status / progress | step N of M, sub-agent started | progress line |
| Artifact | a file or structured result, by reference | show a download or card |
| Approval request | the run is paused for a decision | show options |
| Error | a recoverable or fatal problem | show a message, offer retry |
| Run done | final state and reason | stop the spinner |

- **Standards exist:** AG-UI (CopilotKit's event protocol for agent-to-UI), and the Vercel AI SDK's stream format. Pick one or define your own small schema.
- **Keep an internal event schema.** Frameworks emit their own event shapes (ADK events, LangGraph stream modes, SDK message streams). The BFF maps them to one UI schema, so the UI doesn't change when the framework does.
- **Don't stream everything.** Hide raw reasoning and internal tool arguments unless the product shows them on purpose.
- **Coalesce tiny deltas** (for example every ~50 ms) to cut event volume without hurting perceived speed.
- 🗣 "I keep one UI event schema and map each framework's events into it."

---

## 6. The approval round trip
`boundary` ★★★

- **Plain idea:** human approval is a pause with a question. The question is a structured interaction, and the answer routes the run down one branch.
- **How it works**
  1. The harness reaches a risky step (for example "issue refund of $240").
  2. It saves the run's state and marks the run "paused: waiting for approval".
  3. It emits an approval request event: what, why, the options, and an expiry.
  4. The edge shows buttons. The user may also type "yes, but make it $200".
  5. The answer goes back by POST with the run ID: a structured decision, or free text.
  6. Free text goes through a small parsing step (code or a model) to become approve, reject or edit.
  7. The harness loads the saved state, applies the decision, and continues down that branch.
- **Properties to design in**
  - No thread is blocked while waiting; the state is in a store.
  - The request has an expiry and an owner. Who may approve? Check this on the answer, not just the request.
  - The decision is logged with who, when and what they saw.
  - A stale approval (state changed since) is rejected or re-asked.
- **Channels:** the same request can go to the UI, Slack or email. The answer comes back by the same POST or a webhook.
- 🗣 "Approval is a paused run plus a structured question. The answer is data that picks the next branch."

---

## 7. Scaling the edge
`software` ★★

- **The edge is mostly idle connections.** Most of a run's life is waiting for the model, so each stream holds a connection with little traffic.
- **What limits scale**
  - Open connections per instance and per load balancer.
  - Load balancer idle timeouts (often around 60 seconds by default): send a heartbeat comment on the stream every 15–30 seconds.
  - Proxy buffering: the stream arrives all at once at the end unless buffering is turned off for that route.
  - Token expiry during long streams: authenticate at the start; re-check on resume.
- **Pattern for large user counts**
  - Stateless edge instances behind a load balancer; no sticky sessions needed because replay comes from the shared event log.
  - Autoscale on open connections and active runs, not CPU.
  - Per-user and per-tenant concurrency limits to protect model quotas.
  - Backpressure: if the queue is long, answer "queued, position N" instead of holding connections.
- **Order of magnitude:** an async server can hold thousands of idle streams per instance. The first real limits are model rate limits and cost, not connections.
- 🗣 "Connections are cheap, tokens aren't. I scale the edge on open streams and cap per-tenant concurrency."

---

## 8. System design view: choosing
`boundary` ★★★

| Decision | Options | How to decide |
|---|---|---|
| Output channel | SSE, WebSocket, polling, push | SSE unless the user interrupts mid-stream |
| Run ownership | tied to connection vs independent run | independent for anything with side effects |
| Replay | none vs event log with IDs | event log if users reconnect or switch devices |
| Concurrent messages | queue vs interrupt vs reject | queue by default; interrupt for chat-like feel |
| Long runs | keep streaming vs return run ID and notify | run ID plus notification beyond ~30–60 seconds |
| UI event format | own schema vs AG-UI vs SDK format | own schema if you have several frameworks |
| Approval channel | in-app only vs multi-channel | in-app first; add Slack or email for async approval |

| Tool | Role |
|---|---|
| API gateway / ALB / Envoy | auth, rate limits, timeouts, SSE routes |
| Redis Streams, Pub/Sub, a table | event log and fan-out for replay |
| AG-UI, Vercel AI SDK | ready-made event formats and client libraries |
| WebSocket services (API Gateway WebSocket, managed pub/sub) | when a persistent two-way channel is needed |

- **Default:** SSE out, POST in, event log with IDs for replay, run independent of the connection, run ID plus notification for long work.

---

## 9. Failure modes
`boundary`

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Stream shows nothing, then everything | proxy buffering | time to first token equals total time | disable buffering on the route; heartbeats |
| Dropped connection loses output | no replay | users report missing text | event IDs and replay log |
| Run dies with the tab | run tied to connection | runs end when users close pages | run in worker; explicit cancel only |
| Duplicate run | client retries the POST | two runs for one message | idempotency key on the message |
| Orphan approvals | approver never answers | runs pending past deadline | expiry, reminder, escalation |
| Wrong approver | answer not checked | audit shows unexpected approver | verify identity and role on the answer |

---

## Where this fits
- **Place:** the front of every agent system; supports L8–L9 in [1a-bp.md](../1a-bp.md).
- **Time it deserves:** 20 minutes; §2, §4 and §6.
- **I should be able to…**
  - Say how a coding CLI and a web chat differ in where the harness runs.
  - Explain session ID, run ID and event ID, and why disconnect isn't cancel.
  - Walk the approval round trip in seven steps.
  - Name what breaks SSE in production and the fix for each.

## References
1. [WHATWG — Server-Sent Events](https://html.spec.whatwg.org/multipage/server-sent-events.html) — event stream format, `Last-Event-ID`.
2. [AG-UI protocol](https://docs.ag-ui.com/) — typed agent-to-UI events.
3. [A2A protocol](https://a2a-protocol.org/) — task states including input-required, push notifications.
4. [MCP — Streamable HTTP transport](https://modelcontextprotocol.io/specification) — streaming over HTTP for tool servers.
