# MCP — The Full Picture (Oct 2026, spec 2026-07-28)

## Index
- [0. One-minute version](#0-one-minute-version)
- [1. Is the Wiz diagram right?](#1-is-the-wiz-diagram-right)
- [2. Concept](#2-concept)
- [3. The roles: host, client, server, gateway, registry](#3-the-roles-host-client-server-gateway-registry)
- [4. The call loop, step by step](#4-the-call-loop-step-by-step)
- [5. Consuming MCP from your code](#5-consuming-mcp-from-your-code)
- [6. MCP vs direct API vs CLI](#6-mcp-vs-direct-api-vs-cli)
- [7. Building MCP for existing services](#7-building-mcp-for-existing-services)
- [8. Context and memory optimization](#8-context-and-memory-optimization)
- [9. Security](#9-security)
- [10. Failure modes](#10-failure-modes)
- [11. Interview questions](#11-interview-questions)
- [12. Deeper](#12-deeper)
- [Where this fits](#where-this-fits)
- [Further reading](#further-reading)

---

## 0. One-minute version
- **What**: a standard plug between an AI app and outside capabilities.
  - It works like USB for tools, so one server serves every compatible agent.
- **Why**: without it there are N agents × M services, and each pair needs custom glue.
  - With it, it's N + M.
- **How**: the host's client calls the server over JSON-RPC.
  - The host turns the tool list into ordinary function-calling schemas for the LLM.
  - **The LLM never speaks MCP.**
- **Catch**: naive hosts dump every schema into context.
  - Big results also land in context.
  - Fixes: filter tools, tool search, code mode.
- 🗣 *"MCP is a host-to-tool protocol, not a model protocol. The model sees normal function schemas. MCP standardizes discovery, auth, and invocation so a tool is built once and reused by every agent."*

---

## 1. Is the Wiz diagram right?
`boundary`

| Element in the picture | Verdict | Nuance |
|---|---|---|
| Host contains the Agent | ✅ | The host is the app running the agent loop |
| MCP Client inside the host | ✅ | One client per upstream connection |
| MCP Server outside the host | ✅ | It can be local (stdio) or remote (HTTP) |
| Gateway inside the host | ⚠️ Possible, not typical | Enterprises usually run it as a **separate shared proxy** |
| Shield: Agent ↔ Gateway | ✅ | **Tool-call policy**: allowlist, human approval, argument checks |
| Shield: Client ↔ Server | ✅ | **Transport trust**: OAuth token, TLS, origin checks |
| LLM | Missing | It sits outside the host; the agent calls it via the provider API |

- The two common gateway placements:
  - **Embedded** (Wiz's picture): a policy library inside your agent process.
    - Simple, but every host repeats the config.
  - **Network gateway**: hosts connect to one URL, and the gateway fans out to N servers.
    - Central auth, audit, allowlists, and tool search.
    - Examples: AWS Bedrock AgentCore Gateway, Docker MCP Gateway, Kong, Cloudflare.
- 🗣 *"A gateway is to MCP what an API gateway is to REST: one front door for auth, routing, and audit."*

---

## 2. Concept
`AI` ★★★

- **Plain idea**: a menu plus a waiter for tools.
  - The menu is `tools/list`; the order is `tools/call`.
- **Picture it**: your Spring service has a REST controller for humans.
  - MCP is **another inbound adapter**, written for an LLM caller instead.
  - It calls the same application services underneath.
- **How it works**
  1. The server publishes tools: name, description, and JSON Schema inputs and outputs.
  2. The host fetches the list and translates it into the LLM's tool format.
  3. The LLM picks a tool and arguments; the host calls the server.
  4. The result goes back into the conversation; the loop repeats until the LLM answers in text.
- **The catch**
  - Every visible tool costs prompt tokens on **every** turn.
  - Every result stays in history.
  - This cost is what drove the "CLI over MCP" backlash.
- 🗣 *"MCP's value is interoperability and governance. Its cost is context. Good hosts load tools lazily."*

What a server can expose:

| Primitive | Who controls it | Example | Status (2026-07-28) |
|---|---|---|---|
| **Tools** | The model decides to call | `get_order_summary` | Core ★★★ |
| **Resources** | The app decides to attach | `filing://AAPL/10-K/2025` | Core ★★ |
| **Prompts** | The user picks | "/summarize-incident" template | Core ★ |
| **Elicitation** | The server asks the user mid-call | "Confirm refund $420?" | Core, via multi-round-trip results |
| **Sampling** | The server asks the host's LLM | The server wants a summary | **Deprecated** |
| **Roots / Logging** | — | — | **Deprecated** |

---

## 3. The roles: host, client, server, gateway, registry
`boundary` ★★★

```
Host (your agent process)
  Agent loop  <---->  LLM API (Gemini / Claude / GPT)
    |
  Policy layer (allowlist, approval, arg checks)
    |
  MCP client A ---stdio---> Server A (local subprocess)
  MCP client B ---HTTPS---> Gateway ---> Server B, C, D
```

| Role | What it is | Concrete examples | Common confusion |
|---|---|---|---|
| **Host** | The app that owns the LLM loop and the user | Claude Desktop, Cursor, your ADK agent | People call the server "host". Wrong |
| **Client** | A connector object inside the host; holds one upstream connection | `McpToolset` in ADK, `mcp.Client` in the Python SDK | Some articles skip it because SDKs hide it |
| **Server** | The process that exposes tools and resources | Your edgar-mcp, GitHub MCP, Vercel MCP | It can run on your laptop; "server" ≠ remote |
| **Gateway** | A proxy that is a server to hosts and a client to upstreams | AgentCore Gateway, Docker MCP Gateway | It's optional; skip it for one server |
| **Registry** | A catalog of servers with metadata (`server.json`) | Official MCP Registry, internal catalogs | Discovery of *servers*, not tools |

- Why tutorials disagree:
  - **"No host"**: they're writing a server, so the host is someone else's app.
  - **"No client"**: the SDK creates clients for you inside the host.
  - **"Gateway"**: they're writing for enterprise deployments with many servers.
- 🗣 *"Host runs the loop, client holds the connection, server exposes capabilities. A gateway is a server facing up and a client facing down."*

---

## 4. The call loop, step by step
`boundary` ★★★

- **Plain idea**: one HTTP POST per action, with no handshake or session.
  - The 2026-07-28 spec made every request self-describing.
- **What changed in 2026-07-28** (versus 2025 tutorials)
  - No `initialize` handshake, no `Mcp-Session-Id`, and no resumable streams.
  - Each request carries its protocol version and client capabilities in `_meta`.
  - Servers must implement `server/discover` (optional for clients, and cacheable).
  - Headers mirror the body (`Mcp-Method`, `Mcp-Name`), so gateways can route without parsing JSON.
  - List results carry `ttlMs` and `cacheScope` cache hints.
  - Older clients still work against "dual-era" servers during a 12-month window.

The loop (your agent calls an orders server):

| # | Who | Does what | Waits on | If it fails |
|---|---|---|---|---|
| 1 | Host | Optionally calls `server/discover`, then `tools/list` and caches it per TTL | Server | Unsupported version → retry with an advertised one |
| 2 | Host | Translates MCP schemas into the provider's tool format | — | Bad schema → drop the tool, log it |
| 3 | Host → LLM | Sends system prompt, tool schemas, and the user message | LLM API | 429 → backoff |
| 4 | LLM | Returns a tool call (name + JSON args) or final text | — | Hallucinated tool name → host rejects and tells the LLM |
| 5 | Host | Policy check, then `tools/call` via the right client | Server | Policy deny → tell the LLM "not permitted" |
| 6 | Server | Validates args, calls the backend, shapes the result | Backend | Error → `isError: true` with an actionable message |
| 6b | Server | Needs user input → returns `input_required` and a signed `requestState` | User via host | Host retries the same call with the user's answer |
| 7 | Host | Appends the `tool_result` and goes back to step 3 | — | Loop guard: max N iterations |

- The catch in step 6b: the retry gets a fresh request ID, not a fresh operation.
  - Keep the first round side-effect free, or use an operation ID for idempotency.
- 🗣 *"Modern MCP is stateless request-response. Cross-call state moves into explicit handles the model passes back as arguments."*

---

## 5. Consuming MCP from your code
`boundary` ★★★

### 5.1 What you set up (concepts, no code)

| Concern | Decision | Default |
|---|---|---|
| **Transport** | stdio (local subprocess) or Streamable HTTP (remote) | stdio for dev; HTTP for anything shared |
| **Topology** | Direct to each server, or through a gateway | Direct for 1–3 servers; gateway beyond that |
| **Auth** | Whose identity reaches the backend | User OAuth token for user data; client credentials for M2M |
| **Tool exposure** | Which tools the LLM sees, and when (§5.2) | Allowlist per agent |
| **Policy** | Which calls need human approval | Anything marked `destructiveHint` |
| **Result handling** | Truncate, summarize, or store results | Cap size, keep a reference to the full data |
| **Caching** | `tools/list` cache plus prompt cache | Honor `ttlMs`; stable tool order |
| **Observability** | Trace every call | OpenTelemetry spans, or Langfuse for agent traces |

In ADK, the default framework (class names per current ADK docs; check your version):

```python
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

orders = McpToolset(
    connection_params=StreamableHTTPConnectionParams(url="https://mcp-gw.internal/mcp"),
    tool_filter=["get_order_summary", "refund_order"],  # static allowlist
)
agent = LlmAgent(model="gemini-2.5-flash", name="support", tools=[orders])
```

### 5.2 "Send all schemas" vs "select": the five strategies

- **Plain idea**: the LLM can only pick tools it can see.
  - Every visible tool costs tokens on every turn.
  - So you control who sees what, and when.

| Strategy | What it is | Good at | Bad at | Choose when |
|---|---|---|---|---|
| **Load all** | Every tool from every server goes into every prompt | Zero setup; best tool-selection recall | Token cost and selection errors grow with count | ≤ ~20–30 tools total |
| **Static allowlist** | Per-agent filter (`tool_filter`, gateway policy) | Cheap, predictable, auditable | You must know the task shape ahead of time | Fixed-purpose agents ★ the usual default |
| **Subagent split** | Each subagent gets a narrow toolset | Keeps contexts small and focused | Handoff overhead and lost context between agents | Clearly separable domains |
| **Tool search / deferred loading** | The LLM sees a `search_tools` meta-tool; full schemas load on demand | Scales to hundreds of tools | Extra round trip; search can miss | 30+ tools or a dynamic catalog |
| **Code mode** | Tools appear as a typed SDK; the LLM writes code that calls them | Results get filtered in the sandbox, not in context | Needs a secure sandbox; harder to audit | Data-heavy, multi-step pipelines |

- Where tool search lives today:
  - **Provider side**: Anthropic's tool search tool (`defer_loading` on tool definitions).
  - **Gateway side**: semantic tool search in AgentCore Gateway; `search_tools` / `call_tool` meta-tools in custom gateways.
- Scale of the problem:
  - GitHub's MCP server once exposed 93 tools at about 55K tokens of schema.
  - That's roughly 600 tokens per tool (Kaxil, cited below).
  - Treat 100–1,000 tokens per tool as the order of magnitude.

### 5.3 Common production combinations

| Situation | Combination |
|---|---|
| Solo dev agent in a sandbox | Shell/CLI + a skills doc; MCP only for SaaS that needs OAuth |
| Internal enterprise agent, 3–10 services | Gateway + per-agent allowlist + prompt caching |
| Platform serving many agents and teams | Gateway + registry + tool search + per-user OAuth + audit |
| Analytics / heavy data agent | Code mode over MCP tools; intermediate data stays in the sandbox |

- Default: **gateway + static allowlist**, unless the catalog exceeds ~30 tools.
  - Then add tool search.
- 🗣 *"I don't send every schema. I allowlist per agent, and past roughly 30 tools I switch to deferred loading behind a search tool."*

---

## 6. MCP vs direct API vs CLI
`boundary` ★★★

- **Plain idea**: MCP pays off when the *consumer* is someone else.
  - Another team, another host, or another user's identity.

| Option | What it is | Good at | Bad at | Choose when |
|---|---|---|---|---|
| **Direct function tool** | Agent code calls your SDK or REST (ADK `FunctionTool`, `OpenAPIToolset`) | Lowest latency, simplest, fully typed | No reuse across hosts; you own the glue | One agent, same team owns both sides |
| **MCP server** | A standard server any host can discover and call | Reuse, per-user OAuth, central governance | Protocol overhead and schema tokens | ≥2 consumers, cross-team, or third-party hosts |
| **CLI in a shell** | The agent runs `gh`, `aws`, `kubectl` | Models already know them; piping filters output | Inherits ambient creds; no per-user scoping | A dev agent already has a sandboxed shell |
| **Browser / computer use** | The agent drives a UI | Works when no API exists | Slow, brittle, costly | Last resort for legacy UIs |

- Decision rule
  - **Who owns the consumer?** You → direct. Others → MCP.
  - **Whose identity?** Yours → CLI or direct. End users → MCP with OAuth.
  - **How many hosts?** One → direct. Claude, Cursor, and your agents → MCP.
- A common evolution path:
  - Start with `OpenAPIToolset` (direct, auto-generated from your spec).
  - Promote to MCP when a second team asks for it.
- 🗣 *"I expose MCP when the consumer isn't me. For my own agent calling my own service, a direct function tool is cheaper and simpler."*

---

## 7. Building MCP for existing services
`software` + `boundary` ★★★

### 7.1 Where it sits: hexagonal view

```
            +-- REST controller --+
Clients --> |                     | --> Application services --> Ports --> DB / SQS / APIs
LLM hosts ->+-- MCP adapter ------+
```

- MCP is **another inbound (driving) adapter**, a sibling of your REST controller.
- It reuses the same use cases, validation, and authorization.
- **Never** let the MCP layer bypass domain rules to call the DB directly.
- Two deployment shapes:
  - **In-process**: the MCP endpoint lives inside the Spring service. Simplest, but couples releases.
  - **Facade service**: a separate MCP service calls existing REST or gRPC. Best for wrapping many services.

### 7.2 Components to build

| Component | Job | Failure it prevents |
|---|---|---|
| **Tool layer** | Task-shaped tools with good descriptions and schemas | The LLM picks the wrong tool or passes bad args |
| **Adapter / anti-corruption layer** | Maps tool args to backend calls; hides internal models | Internal schema churn breaking every agent |
| **Result shaper** | Projects fields, caps size, paginates | 30K-token payloads flooding context |
| **AuthN/AuthZ** | Validates OAuth tokens, exchanges for downstream tokens, checks scopes | Confused deputy: the agent acting with more power than the user |
| **Handle store** | Durable state for multi-step work (export IDs, cursors) | Lost state when a request lands on another instance |
| **Policy hints** | `readOnlyHint`, `destructiveHint`, `idempotentHint` | Hosts auto-running dangerous writes |
| **Observability** | One span per call: tool, latency, result size, `isError` rate | Silent misuse; bad descriptions go unnoticed |
| **Rate limits + quotas** | Per user and per tool | One looping agent DoS-ing the backend |

### 7.3 Turning REST / GraphQL / gRPC into MCP

- **Plain idea**: redesign for the caller.
  - The REST API was designed for programmers who read docs once.
  - The LLM rereads your docs (descriptions) on every turn and can't see your Swagger UI.
  - So don't mirror endpoints 1:1.

| REST concept | MCP translation | Why |
|---|---|---|
| Many fine-grained endpoints | Fewer **task-level** tools (combine read calls) | Fewer schema tokens, fewer wrong picks |
| Path + query + body + headers | One **flat** JSON Schema object | The LLM fills one object reliably |
| Free-text params | `enum`, `default`, `format`, examples in the description | Cuts argument errors |
| Pagination tokens and links | `limit` + `cursor` args; return `next_cursor` | Bounded result size |
| Full response DTO | Projected fields + `structuredContent` with `outputSchema` | Less context; the host can parse it |
| 404 / 409 / 422 | `isError: true` + a fix hint ("order not found; use search_orders") | The LLM self-corrects |
| 401 / 403 | Auth error; with step-up, request the extra scope | No retry storms |
| 429 / 5xx | Transient error + retry hint; idempotent writes | Safe retries |
| POST / PUT / DELETE | `idempotency_key` arg + `destructiveHint` + confirmation via elicitation | Duplicate charges, accidental deletes |
| Async jobs (202 + poll) | `start_x` returns a handle, plus a `get_x_status` tool (or the Tasks extension) | Streams can't resume in 2026-07-28 |

- **GraphQL**: three options. Pick by consumer trust.
  - **Persisted queries as tools** (★ default): each vetted query becomes a named tool. Safe and cheap.
  - **One generic `graphql_query` tool** with the schema as a resource. Flexible, but the LLM writes queries and the server must enforce depth and cost limits.
  - **Code mode**: the LLM writes code against a typed client. Best for complex analysis.
- **gRPC**: proto messages → JSON Schema.
  - Hide streaming RPCs behind handles.
  - Map status codes like the HTTP rows above.
- **Auto-generation** (gateways that ingest OpenAPI):
  - Fine as a **starting point**.
  - Then curate: rename tools, merge them, rewrite descriptions, drop admin endpoints.
- Worked example (orders service, 14 REST endpoints → 5 tools):
  - `search_orders(customer_email?, status?, limit=10, cursor?)`
  - `get_order_summary(order_id)` merges order + items + shipment + refund eligibility (4 GETs).
  - `refund_order(order_id, amount, reason, idempotency_key)` is destructive and needs confirmation.
  - `start_order_export(filter)` → handle; `get_export_status(handle)`.
  - Admin endpoints (reindex, purge) are **not exposed**.

Server sketch (Python SDK v2; v1's `FastMCP` import path was removed):

```python
from mcp.server import MCPServer
mcp = MCPServer("orders", version="1.0.0")

@mcp.tool()
def get_order_summary(order_id: str) -> OrderSummary:
    """Status, items, shipment, refund eligibility for ONE order.
    Use search_orders first if you only have an email."""
    return order_service.summary(order_id)  # same use case the REST controller calls
```

### 7.4 Design paradigms to name in interviews

| Paradigm | Rule | Failure it prevents |
|---|---|---|
| **Design for the model as caller** | Descriptions say when to use, when not to, and what a good arg looks like | Wrong tool choice |
| **Workflow over CRUD** | One tool per user intent | 5-call chains that fail halfway |
| **Context budget per tool** | Every tool has a max output size | Context exhaustion |
| **Stateless server, explicit handles** | State lives in durable storage, keyed by handle | Instance affinity; lost work on scale-out |
| **Least privilege, user-delegated** | Token exchange to the user's scope; no god service account | Confused deputy, data leaks |
| **Deterministic tool list** | Stable order and names; semver on breaking changes | Prompt-cache misses; broken agents |
| **Errors as instructions** | Every error says what to do next | Retry loops |

- 🗣 *"An MCP server over an existing service is an inbound adapter. It redesigns the surface for an LLM caller: fewer task-shaped tools, bounded outputs, actionable errors, and user-delegated auth."*

---

## 8. Context and memory optimization
`AI` ★★★

- **Plain idea**: context is RAM. Schemas and tool results are what fill it.
  - You save tokens in three places: what you advertise, what you return, and what you keep.

| Lever | Where | What to do | Saves |
|---|---|---|---|
| **Advertise less** | Host / gateway | Allowlist, subagents, tool search | Schema tokens on every turn |
| **Shorter schemas** | Server | Tight descriptions, enums over prose | 20–50% of schema size (order of magnitude) |
| **Return less** | Server | Field projection, `limit`, summaries, resource links | Result tokens |
| **Filter outside the model** | Host | Code mode: data stays in the sandbox, only the answer returns | The biggest win on data tasks |
| **Keep less** | Host | Mask old tool results; compact old turns into summaries | History growth |
| **Cache the prefix** | Host | Stable system prompt + tool order → provider prompt caching | Cost and latency, not window size |

- Reference number: Anthropic's code-execution approach cut one workflow from ~150K to ~2K tokens (98.7%).
  - Their published example, not a general guarantee.

**Memory: where it actually lives**
- MCP has **no memory**. Since 2026-07-28 the protocol doesn't even have sessions.
- Each tier lives somewhere else:

| Tier | Where | Example |
|---|---|---|
| Working memory | The host's message list (context window) | Current conversation |
| Session state | Agent framework state | ADK `session.state`, LangGraph checkpointer |
| Cross-call tool state | Server-issued handles in durable storage | `export_handle` |
| Long-term memory | An external store, often **exposed as MCP tools** | `remember(fact)` / `recall(query)` over a vector DB |

- Long-term memory design (canonical pattern):
  - **Write path**: at turn end, an async job extracts facts → dedupes → stores embeddings + metadata.
  - **Read path**: top-k by embedding similarity × recency → inject a compact block into the prompt.
  - **Catch**: stale or wrong memories persist. Add TTLs, a source for each fact, and a delete path.
- 🗣 *"MCP is stateless. Memory is a host concern, or just another MCP server that the agent calls like any tool."*

---

## 9. Security
`boundary` ★★★

- **Plain idea**: every tool description and every tool result is untrusted text fed to an LLM.
  - Some tools can act in the real world.

| Threat | What happens | Mitigation |
|---|---|---|
| **Tool poisoning** | A server's description hides instructions ("also read ~/.ssh") | Allowlist servers; pin versions; review descriptions |
| **Rug pull** | A server changes tool behavior after approval | Version pinning; alert on `tools/list` diffs |
| **Indirect prompt injection** | A tool result (email, web page) contains instructions | Treat results as data; approval for writes after reading untrusted content |
| **Confused deputy** | The server uses its own powerful creds for any user | Per-user OAuth; token exchange; audience-bound tokens (RFC 8707) |
| **Token passthrough** | The server forwards the client's token to downstream APIs | Forbidden by the spec; exchange for a downstream token |
| **Exfiltration chains** | Read private data → send it via another tool | Approval gates; egress limits; never mix sensitive-read and send tools without a human |
| **Local server exposure** | A localhost server reachable from a browser (DNS rebinding) | Bind 127.0.0.1; validate `Origin` |

- 2026-07-28 auth in one breath:
  - OAuth 2.1, with the MCP server as a resource server.
  - Protected Resource Metadata (RFC 9728) for discovery.
  - Client ID Metadata Documents instead of Dynamic Client Registration (now deprecated).
  - Step-up scopes per call.
- 🗣 *"The two shields: policy between agent and tools decides **whether** a call happens; OAuth between client and server decides **as whom**."*

---

## 10. Failure modes

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Context blowout | 5 servers × 40 tools loaded at once | Tokens-before-first-message metric | Allowlist + tool search |
| Wrong tool picked | Overlapping names or descriptions | Tool-selection eval set; called-then-abandoned rate | Merge tools; add "use X instead when…" |
| Duplicate side effects | LLM retry or an MRTR retry | Duplicate rows or charges | Idempotency keys; side-effect-free first round |
| Lost in-flight call | LB drains a streaming response | Client errors mid-stream | Handles + polling for long work |
| Stale tool list | `ttlMs` cache during a deploy | Calls to removed tools | Short TTL during rollout; `tools/list_changed` notification |
| Prompt-cache misses | Non-deterministic tool order | Cache-hit ratio drops | Sort `tools/list` |
| Header mismatch (400 / -32020) | Middleware rewrites the body only | Spike in 400s | Rewrite header and body together, or neither |
| Agent loop runaway | A tool error the LLM can't fix | Iterations per task | Max-iterations guard + actionable error text |

---

## 11. Interview questions

**Q:** Walk me through what happens when a user message triggers an MCP tool.
**L4:**
- The host sends the prompt and tool schemas (translated from `tools/list`) to the LLM.
- The LLM returns a tool call; the host checks policy and sends `tools/call` via the right client.
- The server validates, executes, and returns `content` / `structuredContent` / `isError`.
- The result goes back as a tool_result; the loop runs until the LLM answers in text.
**L5 adds:**
- The LLM never sees MCP; translation to provider formats is the host's job.
- Since 2026-07-28, each request is self-describing (`_meta`, no sessions), so servers scale behind round-robin LBs.
- Mid-call user input uses an `input_required` result plus a retry; the first round must be side-effect free.
🗣 *"Host translates, LLM decides, client calls, server executes. Stateless per request."*

**Q:** Your agent connects to 8 MCP servers with 200 tools. What breaks, and what do you do?
**L4:**
- Schema tokens eat the window; tool-selection accuracy drops.
- Allowlist tools per agent; split into subagents by domain.
- Shorten descriptions.
**L5 adds:**
- Deferred loading behind a search tool (provider tool search or a gateway meta-tool) trades one round trip for O(k) schemas instead of O(n).
- For data-heavy tasks, code mode keeps intermediate results in the sandbox.
- Measure it: a tool-selection eval set before and after, not just token counts.
🗣 *"Allowlist first, tool search past ~30 tools, code mode when the data is big."*

**Q:** You have 40 REST endpoints in an order service. How do you expose them over MCP?
**L4:**
- Don't mirror 1:1; group by user task into ~5–8 tools.
- Flat schemas with enums and defaults; paginate; project fields.
- Map HTTP errors to `isError` with a fix hint.
- Mark writes destructive; add idempotency keys.
**L5 adds:**
- Build it as an inbound adapter over the same application services, so auth and domain rules can't be bypassed.
- Use user-delegated auth via token exchange; a shared service account creates a confused deputy.
- Version tools semantically and keep `tools/list` deterministic for prompt caching.
🗣 *"MCP is a new front door, not a new backdoor: same use cases, redesigned surface."*

**Q:** When would you not use MCP?
**L4:**
- A single agent calling your own service → direct function tool.
- A dev agent with a sandboxed shell → CLI plus a skills doc.
- No API at all → browser automation.
**L5 adds:**
- The deciding variable is *whose identity and how many consumers*.
- The CLI's cheapness comes from ambient credentials, which is exactly what multi-tenant products can't allow.
🗣 *"MCP pays off when the consumer isn't you or acts for someone else."*

**Q:** How do you handle a multi-step, long-running operation over MCP?
**L4:**
- A `start_x` tool returns a handle; a `get_x_status` tool polls it.
- State goes in durable storage keyed by the handle, with an expiry.
- An expired handle returns a tool error the model can act on.
**L5 adds:**
- Streams don't resume under 2026-07-28, so holding a response open for minutes is fragile behind LBs.
- The Tasks extension standardizes this, but SDK support varies. Verify before depending on it.
🗣 *"State moves out of the transport and into handles the model can see."*

**Q (L5 only):** Design an enterprise MCP gateway for 50 internal services and 20 agent teams.
**L5:**
- Gateway = server to hosts, client to upstreams.
  - It routes on `Mcp-Name` headers without parsing bodies.
  - It validates that headers match bodies.
- Identity: the user's OAuth token at the edge, token exchange per upstream.
  - Per-team allowlists; approval policy keyed on `destructiveHint`.
- Catalog: a registry for servers, semantic tool search for tools.
  - Cache `tools/list` per `ttlMs` with `cacheScope: private` for identity-filtered lists.
- Ops: per-user and per-tool rate limits, OpenTelemetry traces, `tools/list` diff alerts (rug-pull detection).
🗣 *"It's an API gateway plus a tool catalog plus a policy engine, with identity propagated, never pooled."*

**Q (L5 only):** A tool reads emails, another sends Slack messages. What's the risk, and how do you contain it?
**L5:**
- Lethal trifecta: private data + untrusted content + an exfiltration channel in one agent.
- Treat tool results as data, but the model can't reliably separate data from instructions.
- Containment:
  - Require approval for any send after untrusted content enters context.
  - Split the reader and sender agents.
  - Use egress allowlists.
🗣 *"Prompt injection isn't solved by prompting. It's solved by capability boundaries."*

---

## 12. Deeper
`boundary` ★

- **Era compatibility**
  - Modern client ↔ legacy server fails unless the client is dual-era.
  - The Python SDK client auto-probes with `server/discover`; the TypeScript client defaults to the legacy handshake unless configured.
  - Check your SDK's defaults.
- **Deprecated in 2026-07-28** (12-month minimum window):
  - Roots, Sampling, Logging, and Dynamic Client Registration.
  - Don't adopt them in new code.
- **Extensions** (versioned separately; check maturity):
  - Tasks, MCP Apps (UI), OAuth Client Credentials, Enterprise-Managed Authorization, Skills.
- **Notification fan-out**
  - `subscriptions/listen` is still a long-lived SSE stream.
  - Multi-instance servers need pub/sub to deliver list-changed events.
- **Caching hints**
  - Never mark a principal-specific result `cacheScope: public`; a shared cache could leak it across users.
- **What L5 adds overall**
  - Treat MCP as a distributed-systems surface: idempotency, statelessness, caching, identity propagation, and evals for tool selection.
  - Not just as a "plugin format".

---

## Where this fits
- This is core to the applied-AI / agent role target.
  - Worth 2–3 focused sessions: §3–5 first, then §7, then §11 out loud.
- Learning objectives:
  - I should be able to **explain** host / client / server / gateway and the stateless loop without notes.
  - I should be able to **decide** between direct tool, MCP, and CLI by naming the deciding variable.
  - I should be able to **redesign** a 40-endpoint REST service into 5–8 MCP tools on a whiteboard.
  - I should be able to **build**: upgrade edgar-mcp to SDK v2 with handles, bounded outputs, and annotations.

## Further reading
1. [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk) — the v2 `MCPServer` and `mcp.Client` APIs
2. [MCP specification 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/changelog) — the changelog is the source of truth on what changed
3. [MCP blog: the 2026-07-28 release](https://blog.modelcontextprotocol.io/posts/2026-07-28/) — the maintainers' rationale for going stateless
4. [ADK — MCP tools](https://google.github.io/adk-docs/tools/mcp-tools/) — `McpToolset`, `tool_filter`, connection params
5. [Anthropic — Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) — tools as code APIs; the 98.7% example
6. [Cloudflare — Code Mode](https://blog.cloudflare.com/code-mode/) — collapsing many tools into a code interface
7. [MCP in 2026: what changed (dev.to, Sep 2026)](https://dev.to/jarvisbitztech/mcp-in-2026-what-changed-in-the-2026-07-28-specification-and-how-to-design-production-integrations-16c4) — a migration-focused walkthrough of the new spec
8. [Scalekit — MCP vs CLI benchmark](https://www.scalekit.com/blog/mcp-vs-cli-use) — cost and reliability numbers; the governance framing
9. [Kaxil — "MCP sucks (until it doesn't)"](https://kaxil.substack.com/p/mcp-vs-cli-vs-rest) — the schema-tax numbers for GitHub MCP
