# Tool Calling — Single-Instance vs Pooled (and what the video gets wrong)

> The video frames it as a framework switch. The real question is: **is the tool stateless or stateful, and where is the bottleneck?**

---

## 0. Concepts — 中 / EN

| 中文 | English | What it really is |
|---|---|---|
| 两个工具调用算不算冲突 | do two tool calls conflict | do they touch the same *stateful* resource |
| 一个工具对应一个调用 | one tool = one call | naive mental model |
| 工具的状态管理模式 | tool state-management mode | stateless function vs stateful instance |
| 工具执行器 | tool executor | harness dispatcher |
| 工具状态表 | tool state table | instance registry / connection pool bookkeeping |
| 工具实例被占用 | tool instance occupied | a session/connection/process is busy |
| 排队或者报错 | queue or error | serialize or reject |
| 实例复用 | instance reuse | keep-alive; don't recreate per call |
| 工具池化 | tool pooling | pool of N instances + scheduler |
| 负载规则分发 | dispatch by load rule | round-robin / least-busy |
| 池化标志 | pooling flag | pool size config |
| 单实例模式 | single-instance mode | pool size = 1 |

---

## 1. What "single-instance tool calling" actually means

- **Stateless tool** = a pure function over its args: `get_weather(city)`, `search_docs(q)`, a REST GET.
  - Two agents calling it at once: no conflict. Concurrency is limited only by the backend (rate limit, DB connections).
  - There is no "instance" to occupy. Most tools in ADK / LangGraph / Claude SDK are this kind.
- **Stateful tool** = wraps a live resource that can serve one caller at a time:
  - MCP server over **stdio**: one subprocess, one session, one JSON-RPC stream → serial.
  - Browser page (Playwright): one page, one DOM state.
  - Sandbox / shell session: one cwd, one env.
  - DB connection (not pool): one transaction at a time.
  - Legacy SDK client that isn't thread-safe.
- **Single-instance tool calling** = the tool holds exactly one such resource. Second concurrent call must **wait** (queue / mutex) or **fail** (busy error). That's the whole concept.
- **Pooled tool calling** = the tool holds N resources; dispatcher hands each call a free one; call N+1 waits.
- So "can two agents call the same tool concurrently?" → *"Is it stateless? Yes, freely. Stateful? Only if pooled, and then up to pool size."*

---

## 2. How real frameworks behave (not how the video describes)

- **ADK**
  - `FunctionTool` is just an async function; ADK runs multiple function calls from one model turn **concurrently** (`asyncio.gather`) and `ParallelAgent` branches concurrently.
  - No "tool state table", no "pooling flag". If your function isn't safe to call concurrently, that's your problem.
  - `MCPToolset` opens one MCP session per toolset instance. stdio server = one process → effectively serial per session. Concurrency = create N toolsets/sessions or use a streamable-HTTP MCP server that handles concurrency itself.
- **Claude Agent SDK / Claude Code**
  - Model may emit several `tool_use` blocks in one turn; the harness executes them concurrently when they're marked safe, serially otherwise (e.g. file edits).
- **LangGraph**
  - `ToolNode` executes parallel tool calls concurrently; same story — no built-in instance management.
- **MCP protocol**
  - Session-oriented. A client-server session processes requests; stdio transport is inherently one stream. Streamable HTTP servers can be stateless and horizontally scaled.
- **Where "instance reuse / pooling" is real**
  - DB drivers: `asyncpg.create_pool(min_size, max_size)`.
  - HTTP: one shared `httpx.AsyncClient` (connection reuse) — reuse, not exclusivity.
  - Browsers: a Playwright context pool.
  - Sandboxes: warm pool of containers (E2B, Modal).
  - These are **resource** pools that a tool wraps, not framework-level "tool pooling".

---

## 2b. Tool integration in the three SDKs

- Same shape everywhere: **define → register on agent → harness dispatches by name → result appended as tool message**.
- Differences are in *how* you define and *what* the SDK gives you for free.

### ADK (Python)

```python
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool, AgentTool, ToolContext
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
from google.adk.tools.openapi_tool import OpenAPIToolset

def get_order(order_id: str, tool_context: ToolContext) -> dict:
    """Fetch one order by id. Returns status and line items."""   # docstring = description shown to model
    tool_context.state["temp:last_order"] = order_id              # optional state access
    return {"status": "ok", "order": db.get(order_id)}

agent = LlmAgent(
    name="support", model="gemini-2.5-flash",
    tools=[
        get_order,                                                # plain function → FunctionTool
        MCPToolset(connection_params=StreamableHTTPConnectionParams(url="https://mcp.internal/crm"),
                   tool_filter=["search_customer", "get_ticket"]),
        OpenAPIToolset(spec_str=open("billing.yaml").read(), spec_str_type="yaml"),
        AgentTool(agent=research_agent),                          # agent as a tool
    ],
    before_tool_callback=policy_check,                            # return dict → skip tool
    after_tool_callback=redact_pii,
)
```

- Schema from type hints + docstring. Return a `dict`; never raise.
- `LongRunningFunctionTool` → pause for human approval, resume later.
- Parallel function calls in one turn run concurrently.
- Built-ins: `google_search`, `VertexAiSearchTool`, `BuiltInCodeExecutor`.

### Claude Agent SDK (Python) — "ccsdk"

```python
from claude_agent_sdk import query, ClaudeAgentOptions, tool, create_sdk_mcp_server

@tool("get_order", "Fetch one order by id", {"order_id": str})
async def get_order(args):
    return {"content": [{"type": "text", "text": json.dumps(db.get(args["order_id"]))}]}

server = create_sdk_mcp_server(name="orders", version="1.0", tools=[get_order])   # in-process MCP

opts = ClaudeAgentOptions(
    mcp_servers={
        "orders": server,                                                     # in-process
        "crm": {"type": "http", "url": "https://mcp.internal/crm"},           # remote MCP
    },
    allowed_tools=["Read", "Grep", "mcp__orders__get_order", "mcp__crm__search_customer"],
    permission_mode="acceptEdits",
    hooks={"PreToolUse": [policy_hook], "PostToolUse": [audit_hook]},
)
async for msg in query(prompt="Why is order 123 late?", options=opts):
    ...
```

- **Every custom tool is an MCP tool**, even in-process. No plain-function path.
- Built-ins come with the harness: `Read`, `Write`, `Edit`, `Bash`, `Grep`, `Glob`, `WebFetch`, `WebSearch`, `Task` (subagents).
- Allow/deny by name; `can_use_tool` callback for dynamic permission; hooks are the deterministic gate.
- Multiple `tool_use` blocks in one turn: run concurrently when independent.

### OpenAI Agents SDK (Python) — "oasdk"

```python
from agents import Agent, Runner, function_tool, WebSearchTool, HostedMCPTool
from agents.mcp import MCPServerStreamableHttp

@function_tool
def get_order(order_id: str) -> dict:
    """Fetch one order by id."""
    return db.get(order_id)

crm = MCPServerStreamableHttp(params={"url": "https://mcp.internal/crm"})

agent = Agent(
    name="support", model="gpt-4.1",
    tools=[get_order, WebSearchTool(), research_agent.as_tool("research", "Deep-dive a topic")],
    mcp_servers=[crm],                  # SDK is the MCP client
    handoffs=[billing_agent],           # conversational transfer, like ADK sub_agents
)
result = await Runner.run(agent, "Why is order 123 late?")
```

- Schema from signature via Pydantic; docstring → description.
- `HostedMCPTool` → OpenAI's servers act as MCP client (no local process, remote URL only).
- Hosted tools: web search, file search (their vector store), code interpreter, computer use.
- `@input_guardrail` / `@output_guardrail` run in parallel with the agent; tripwire aborts.
- `failure_error_function` on a tool → error text sent to model instead of raising.

### Side by side

| | ADK | Claude Agent SDK | OpenAI Agents SDK |
|---|---|---|---|
| Define a tool | Python func → `FunctionTool` | `@tool` → in-process MCP server | `@function_tool` |
| Schema source | type hints + docstring | explicit dict / JSON schema | Pydantic from signature |
| MCP client | `MCPToolset` (stdio/SSE/HTTP) | `mcp_servers` config (stdio/HTTP, in-process) | `MCPServer*` classes or `HostedMCPTool` |
| Agent as tool | `AgentTool` | `Task` subagents (`agents` config) | `agent.as_tool()` |
| Handoff | `sub_agents` + `transfer_to_agent` | — | `handoffs` |
| Interception | `before/after_tool_callback`, plugins | `PreToolUse/PostToolUse` hooks, `can_use_tool` | guardrails, `RunHooks` |
| HITL | `LongRunningFunctionTool` | permission prompts / `can_use_tool` | `needs_approval` on tools |
| Parallel tool calls | yes | yes (when independent) | yes |
| Built-in tools | search, code exec | full coding toolset | hosted search/files/computer |
| Sweet spot | Gemini + GCP, workflow agents | coding / file-system agents | OpenAI models, quick start |

- Pick by model + platform, not by tool API. Tool wrappers (idempotency, pooling, errors) are identical code in all three.

---

## 3. How to design it yourself

- **Step 1 — classify each tool**: stateless / stateful. Write it in the tool's docstring.
- **Step 2 — stateless tools**: bound concurrency with a semaphore sized to the backend's rate limit. Nothing else.

```python
_sem = asyncio.Semaphore(20)          # backend allows ~20 concurrent
async def search_docs(q: str) -> dict:
    async with _sem:
        return await client.search(q)
```

- **Step 3 — stateful tools**: build a pool with lease/release.

```python
class BrowserPool:
    def __init__(self, n): self._q = asyncio.Queue(); self.n = n
    async def start(self):
        for _ in range(self.n): await self._q.put(await new_page())
    @asynccontextmanager
    async def lease(self, timeout=30):
        page = await asyncio.wait_for(self._q.get(), timeout)   # wait if all busy
        try: yield page
        finally: await page.reset(); await self._q.put(page)   # reset state before reuse

pool = BrowserPool(4)
async def fetch_rendered(url: str) -> dict:
    async with pool.lease() as page:
        await page.goto(url); return {"html": await page.content()}
```

- **Step 4 — per-agent affinity when state must persist across calls**
  - A shell session or browser that one agent drives over many steps → pin one instance to that invocation (`temp:` state holds the handle id). Pool is per-invocation, not shared.
  - Sharing a stateful instance across agents is a bug, not an optimization: agent A's `cd` breaks agent B.
- **Step 5 — decide wait vs fail**
  - Wait with timeout → default. Returns `{error:"busy", retryable:true}` on timeout so the harness backs off.
  - Fail-fast → when the model can choose an alternative tool.
- **Step 6 — conflict rules beyond instances**
  - Two calls touching the same **data** (write + write, or write + read) → serialize by key, not by tool. `asyncio.Lock` per `order_id`, or DB row lock.
  - Ordering dependency (call B needs A's output) → the model already sequences them; don't parallelize across turns.
  - Read-only + different keys → always parallel.
- **Step 7 — observe**: pool utilization, wait time p99, busy-timeout rate. Pool exhaustion shows up as latency, not errors.

---

## 4. Where the video is right and wrong

| Claim | Verdict | Correction |
|---|---|---|
| 是否冲突取决于工具的状态管理模式和并发配置 | Valid | Right framing: stateless vs stateful decides it. |
| 框架维护工具状态表，记录实例占用和执行阶段 | Not accurate for mainstream frameworks | ADK / LangGraph / Claude SDK keep no such table. Tools are functions. Bookkeeping exists only inside resource pools you (or a driver) write. |
| 默认单实例：已占用则排队或报错 | Valid *for stateful tools only* | For stateless tools there is nothing to occupy; calls run concurrently by default. Presented as universal — it isn't. |
| 实例复用开关：释放后立即接收下一次调用 | Real concept, wrong label | This is keep-alive / connection reuse. Not a named framework switch; default in any pooled client. |
| 工具池化开关：多 Agent 真正同时调用同一工具，调度器负载均衡 | Real concept, wrong label | Pool of N resource instances + dispatcher. It's a pattern you implement per tool, not a flag you flip. |
| 多 Agent 系统搭建统一工具池，每个工具多实例共享 | Valid pattern | Correct for browsers, sandboxes, DB connections. Meaningless for stateless tools. |
| 没池化却并发多 Agent → 后面的请求全部阻塞排队 | Valid *for stateful tools* | True for a stdio MCP server or a single browser page. Not true for a REST tool. |
| 判断冲突 = 实例数量 + 调度策略 + 池化标志 | Half right | Add the missing axis: **shared data**. Two pooled instances writing the same row still conflict. Instance count solves resource contention, not data contention. |

- One-line verdict: the video describes real resource-pool behavior but presents it as a generic framework feature with switches. Interview answer should say *stateless vs stateful* first, *pool size* second, *data-level conflicts* third.

---

## 5. Interview answer, 30 seconds

- "Whether two tool calls conflict depends on whether the tool wraps a stateful resource."
- "Stateless tool — pure function over args — runs concurrently; I bound it with a semaphore to respect the backend rate limit."
- "Stateful tool — browser, shell, stdio MCP server, DB connection — is one instance by default, so concurrent calls queue. I pool N instances with lease/release, reset state on return, and pin an instance to an agent when it needs continuity across steps."
- "Separately from instances, two calls that write the same key conflict regardless of pooling; I serialize by key or use CAS."
- "None of this is a framework flag in ADK or LangGraph; it's the tool wrapper's job."

---

## 6. MCP — what it is, what it costs, how to build one over existing systems

### 6.1 Relation to tool calling

- Tool calling = model emits `{name, args}`; harness runs it. Two halves: **model side** (schema in, call out) and **execution side** (who runs it, where).
- MCP standardizes only the **execution side**: `tools/list` (discovery), `tools/call` (invoke), plus `resources` and `prompts`.
- The model never speaks MCP. Harness = MCP client; your server = tool provider. Harness converts `tools/list` into the JSON schemas the model sees.
- Without MCP: every harness needs custom glue per tool set. With MCP: write the tool once, any MCP-capable harness (ADK, Claude, OpenAI, Cursor) uses it.

### 6.2 "Just a protocol translator" — yes, with two additions

- Correct: an MCP server holds no data of its own. It's a facade over your DB / APIs / files. Request in → your existing code → response out.
- Addition 1: it is the **security boundary**. Auth, authz per user, allow-listed operations, PII redaction happen here. Not a passive translator.
- Addition 2: it is **capability curation**. You decide which 8 tasks the model can do, not which 80 endpoints exist.
- So: MCP server = adapter + policy + curated surface. Still thin. Still no data.

### 6.3 Does it cost money

- **Protocol**: free, open spec.
- **Running the server**: it's a process.
  - stdio: subprocess on the same box → zero extra infra.
  - Streamable HTTP: a microservice → normal hosting cost (Cloud Run / ECS), same as any API.
- **The real cost is tokens**:
  - Every tool definition is sent to the model on every call. 40 tools × ~150 tokens = 6k tokens per turn, before the user says anything.
  - Tool results are tokens too. A tool returning 200 rows costs more than the call.
  - Mitigation: `tool_filter` / allow-list to expose ≤ 10 tools per agent; paginate and truncate results; prompt caching so the static prefix is cheap.
- **Backend cost** unchanged: your DB query still runs.

### 6.4 Design pattern for wrapping your existing systems

- Hexagonal mapping (your stack):
  - MCP server = new **inbound (driving) adapter**, sits beside REST controllers.
  - Domain services = unchanged.
  - DB / third-party clients = existing outbound adapters.
  - Do not put business logic in the MCP layer.

```
model ──tool_use──► harness (MCP client) ──tools/call──► MCP server (adapter)
                                                            │ auth, authz, validate, shape
                                                            ▼
                                                      existing service layer ──► DB / APIs
```

- **Flow to build one**
  1. List the 5–10 *tasks* the agent must accomplish (not endpoints). "Find why an order is late" → `get_order`, `get_shipment_events`, `search_tickets`.
  2. Define each tool: name (verb_noun), one-paragraph description with when-to-use and when-not, typed params with enums, small typed result.
  3. Implement as thin calls into the service layer. Pass user identity through.
  4. Mark reads vs writes. Writes take an `idempotency_key`; consider `require_confirmation` / HITL.
  5. Return structured JSON + short human summary; paginate; cap size (~2–4k tokens).
  6. Errors: `isError: true` with an actionable message (`"order_id must be 8 digits"`), never a stack trace.
  7. Transport: stdio for local; streamable HTTP, stateless, behind your gateway for deploy.
  8. Test with MCP Inspector, unit-test each tool, then eval tool *selection* with 30 prompts → expected tool.
  9. Observe: latency, error rate, tokens returned per tool, calls per session.
  10. Version tools; deprecate with a window; clients pin by `tool_filter`.

- **Patterns to name in an interview**
  - Facade / anti-corruption layer: model-facing tools ≠ API endpoints.
  - Coarse-grained, task-shaped tools over fine-grained CRUD (fewer calls, fewer tokens, less error surface).
  - Read/write split with confirmation on writes.
  - Identity propagation: OAuth 2.1 on remote servers; server enforces the *user's* permissions — no god credential.
  - Least privilege per agent via allow-lists.
  - Stateless server; state lives in your DB or the harness session.

- **Questions to answer before writing code**
  - Who is the caller — the user's identity or a service account? How does it reach the server?
  - Which tasks, in the user's words? What's the max tool count per agent?
  - Which tools mutate? What's the blast radius of a wrong call? HITL where?
  - Result size budget per tool? PII in responses — redact where?
  - Latency budget per call? Timeouts and retries inside the tool?
  - Multi-tenant? Row-level filtering enforced server-side?
  - Where deployed, who owns it, how versioned?
  - Build vs buy: Bedrock AgentCore Gateway / Apigee can expose existing REST/Lambda as MCP with no server code — check before writing one.

- **Frameworks**
  - Python: `mcp` official SDK (includes FastMCP 1.x) or `fastmcp` 2.x (you already use it).
  - Java: Spring AI MCP server starter — natural for your Spring Boot services.
  - TypeScript: `@modelcontextprotocol/sdk`.
  - Hosted conversion: AWS Bedrock AgentCore Gateway.

---

## References

1. https://github.com/google/adk-python — `flows/llm_flows/functions.py` (parallel function-call execution) and `tools/mcp_tool/` (one session per toolset).
2. https://modelcontextprotocol.io/specification/2025-06-18/basic/transports — stdio vs streamable HTTP; why stdio servers are effectively serial.
3. https://magicstack.github.io/asyncpg/current/usage.html#connection-pools — the canonical resource-pool API to model tool pools on.
4. https://playwright.dev/python/docs/browser-contexts — contexts as the unit to pool for browser tools.
5. https://github.com/anthropics/claude-agent-sdk-python — `@tool` + `create_sdk_mcp_server`; custom tools are in-process MCP.
6. https://github.com/openai/openai-agents-python — `function_tool`, `agents/mcp/`, `as_tool`, guardrails.
7. https://github.com/jlowin/fastmcp — build the server; `docs/` covers auth and streamable HTTP deploy.
8. https://github.com/spring-projects/spring-ai-examples/tree/main/model-context-protocol — MCP server on Spring Boot for your Java services.