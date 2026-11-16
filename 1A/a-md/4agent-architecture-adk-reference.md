# Agent Architecture — ADK-Centered Reference

> Merged from every thread in this chat: harness anatomy, Claude Code as worked example, context, tools, MCP, multi-agent consistency, the full-stack chat system, and the study plan.
> Framework of record: **Google ADK**. Other SDKs appear only in comparison tables.
> Legend: 🗣 = quotable interview one-liner.

---

## Index

1. [The harness](#1-the-harness)
   1.1 Mental model · 1.2 Loop anatomy · 1.3 Central controller · 1.4 Agent- vs orchestrator-driven · 1.5 Parsing tool calls · 1.6 "Done" · 1.7 Guardrails · 1.8 Nested loops, skills, subagents · 1.9 Sandboxes
2. [Context](#2-context)
   2.1 What it physically is · 2.2 Structured or not · 2.3 How ADK builds the request · 2.4 What belongs in context · 2.5 Design & implement · 2.6 Memory taxonomy
3. [Tools](#3-tools)
   3.1 Mechanics · 3.2 Stateless vs stateful · 3.3 Framework behavior · 3.4 SDK integration · 3.5 Designing concurrency · 3.6 Video verdict
4. [MCP](#4-mcp)
5. [Multi-agent coordination & consistency](#5-multi-agent-coordination--consistency)
6. [Full system — the seven layers](#6-full-system--the-seven-layers)
7. [Study plan & summary table](#7-study-plan--summary-table)
8. [Interview one-liners](#8-interview-one-liners)
9. [References](#9-references)

---

## 1. The harness

### 1.1 Mental model

```
UI ──► HARNESS (the agent) ──► LLM (stateless callee)
          │  assemble context
          │  dispatch tools  ──► DB / APIs / MCP / sandbox
          │  stop / budget / guardrails
          └─ persist session, state, artifacts
```

- The LLM is stateless. It sees only the token array sent in one call.
- Therefore *something* assembles that array every turn. That something is the harness. The harness **is** the agent; the model is one adapter.
- Common diagram confusion: labeling the LLM oval "Agent" and drawing "Working Memory" before it. Working memory = the assembled prompt; it must precede the call. The UI never hits the LLM; it hits the harness.
- Hexagonal mapping:
  - UI / chat / queue = inbound adapter
  - harness loop = application service
  - LLM = outbound port (swap Gemini ↔ Claude here)
  - vector store, SQL, files = outbound ports for memory
- 🗣 "A harness is a loop that assembles context, calls a stateless model, dispatches tool calls, and decides when to stop; memory, planning, subagents and guardrails are either code around that loop or text inside the context."

### 1.2 Loop anatomy (Claude Code → ADK mapping)

| Step | Claude Code | ADK |
|---|---|---|
| Entry | REPL hands string to in-process `runTurn()` | `Runner.run_async(user_id, session_id, new_message)` |
| Context build | system prompt + CLAUDE.md + tools + history + @files | request processors → `LlmRequest` |
| Model call | Messages API | `LlmAgent` → Gemini |
| Dispatch | switch on `tool_use.name` → handler | `functionCall` → `FunctionTool` / `MCPToolset` |
| Commit | append `tool_result` | `Event` with `state_delta`, applied by Runner |
| Stop | `stop_reason == end_turn` | final response / no transfer / `end_invocation` |

- ADK vocabulary: **invocation** (user msg → final response) ⊃ **agent call** ⊃ **step** (one LLM call + its tool calls).
- Runner guarantee: `state_delta` applied **before** the event is forwarded. No transaction across events.

### 1.3 Central controller / dispatcher

- The controller is the loop function, never the model. ADK: `Runner` + agent's `run_async` generator. CC: internal query loop. LangGraph: compiled graph executor.
- Duties in order: assemble → call → read stop reason → execute tools → continue/stop.
- The model returns "I suggest calling X(args)". The controller decides whether it happens (permissions, budget, allowlist).
- "Dispatcher" narrowly = the switch-on-tool-name that maps `functionCall.name` → handler. Nothing smarter.

### 1.4 Agent-driven vs orchestrator-driven

- Question: who decides control flow — code or model.

| | Orchestrator-driven | Agent-driven |
|---|---|---|
| Who decides | code | model, step by step |
| ADK | `SequentialAgent` / `ParallelAgent` / `LoopAgent` | `LlmAgent` with tools / `sub_agents` |
| Retrieval | harness runs RAG before every call | `search_docs` is a tool |
| Properties | deterministic, testable, cheaper | flexible, non-deterministic, more tokens |
| Choose when | sequence known at design time | branching can't be enumerated |

- Production = hybrid: cheap always-on context by code; conditional lookups as tools.
- 🗣 "Show me two inputs where the correct sequence differs; if nobody can, it's a `SequentialAgent`."

### 1.5 How the harness finds the command in the response

- No prose parsing. Providers return structured blocks:
  - Gemini: `parts: [{functionCall: {name, args}}]` → ADK `Event` with `function_call`
  - Anthropic: `content: [{type:"tool_use", id, name, input}]`, `stop_reason: "tool_use"`
- Underneath: tool JSON schemas were sent; model emits special delimiter tokens around a JSON object; the provider's API layer parses them into the block.
- Harness code, literally:
  - `for part in response.parts: if part.function_call:`
  - `fn = registry[part.function_call.name]`
  - validate args against schema → `fn(**args)` → append `functionResponse` → call model again
- Unknown name / bad args → return a structured error as the tool result; never crash. Cap retries in code.
- 2023 ReAct (`Action: tool_name` regex) is dead; mention only as history.

### 1.6 "Done" and goal translation

- No explicit target extraction. Done = model returns a response with zero tool calls.
- Goal-shaped behavior is prompting: "keep working until complete"; a todo/plan scratchpad tool.
- Hard termination lives in code: `max_iterations`, step cap, cost cap, timeout, `end_invocation`. Soft termination lives in the prompt.
- 🗣 "Hard stops in code, soft stops in the prompt. Never rely on the model to stop itself."

### 1.7 Guardrails — who decides

| Layer | Owner | Mechanism | Strength |
|---|---|---|---|
| Harness code | you | permission modes, allow/deny per tool, `before_tool_callback`, plugins, iteration caps | deterministic |
| User config | user | settings, per-tool approvals, HITL | deterministic |
| Prompt | model | "don't commit unless asked" | advisory, bypassable |

- Input guardrails (injection, PII, size) belong before the first call, not only on output.
- Tracing should wrap the whole run including tool calls, not sit after the reply.

### 1.8 Nested loops, skills, subagents

- Ordinary tools (Read, Bash, DB query) are single deterministic calls. Only a tool that wraps another model call is a nested loop.
- ADK: `AgentTool` = new invocation, own context, returns a value. `sub_agents` = transfer, shared context, control moves. `ParallelAgent` branches share one state map.
- Subagent purpose = **context isolation**, not parallelism. Return summaries, not transcripts.
- Claude Code discovery: finds `.claude/agents/*.md`, `.claude/skills/*/SKILL.md`, `CLAUDE.md`, MCP servers at startup; picks by description text. It does **not** invent new skill/agent files mid-task.
- "Don't create agents/skills" advice = built-ins + a good `CLAUDE.md` cover most work; custom subagents earn their place only for context isolation or a restricted tool set. Premature agents fragment context and add routing errors (see "the seventh agent", §5).

### 1.9 Sandboxes

- CC local: no sandbox by default; permission prompts + hooks are the gate. Optional OS-level sandbox (macOS seatbelt / Linux bubblewrap; `sandbox-runtime`).
- Cloud agents (CC on web, Codex, Devin): one container/microVM per task, repo cloned in, network off or allowlisted, destroyed after.
- Isolation ladder: process sandbox (seccomp/bwrap) → container (Docker, gVisor) → microVM (Firecracker). Untrusted user code → microVM.
- Build it:
  - warm pool of pre-baked images (start < 1 s)
  - per-session instance; mount a copy of the workspace
  - CPU / memory / wall-clock / disk limits; kill on idle
  - egress via allowlist proxy; no raw internet
  - no secrets inside; credentialed tools go through a gateway outside
  - snapshot/restore; ship logs out
- Buy first: E2B, Modal, Daytona, Vercel Sandbox, Bedrock AgentCore Code Interpreter. ADK: `BuiltInCodeExecutor` (Gemini-side) or Vertex code execution.

---

## 2. Context

### 2.1 What it physically is

- At call time: one HTTPS request body
  - `system_instruction` — text
  - `contents[]` — `{role: user|model, parts:[...]}`
  - parts: `{text}` | `{functionCall}` | `{functionResponse}` | `{inlineData: mime+base64}`
  - `tools[]` — JSON schemas · `generation_config`
- Provider tokenizes to an integer array. That array is the context. Nothing else.
- Lifetime: milliseconds in process RAM while built, then gone. Provider KV cache enables prefix caching; you don't own it.
- Between calls context doesn't exist. What persists is the **raw material**:
  - `SessionService` → events + state (in-memory / Postgres / Vertex)
  - `ArtifactService` → blobs
  - `MemoryService` → cross-session index
- RAM for the assembled request; DB for sources. Redis optional (hot-session cache, semantic cache), not required.

### 2.2 Structured or not

- Envelope: structured JSON. Inside: `text` parts unstructured; `functionCall/Response` structured JSON; `inlineData` bytes.
- No numerics as numerics. `balance: 1250` in state → characters → tokens. Keep math in tools.
- `session.state` = JSON-serializable dict, **not** auto-injected. Reaches the model only via `{key}` templating in `instruction` or a tool reading it.

### 2.3 How ADK builds the request

- `LlmAgent` → `BaseLlmFlow` → request processors mutating one `LlmRequest`:
  - `basic` — model id, generation config
  - `instructions` — `global_instruction` + `instruction`, `{state_key}` interpolated
  - `identity` — agent name/description
  - `contents` — `session.events` → `contents[]`; filtered by `branch`; `include_contents='none'` drops history
  - `agent_transfer` — adds `transfer_to_agent` + sub-agent descriptions
  - tool declarations from `tools=[...]`
- `before_model_callback(callback_context, llm_request)` — last hook; rewrite anything; return `LlmResponse` to skip the call (cache).
- Compaction: not automatic in older versions; recent `App`-level events-compaction config exists — verify against pinned version.

### 2.4 What belongs in context

| Layer | Content | Source | Budget (assume) |
|---|---|---|---|
| System | role, rules, output format, tool policy | versioned prompt file | ~1–2k |
| Dynamic facts | user id, tenant, date/time, locale, profile summary | `user:` / `app:` state via templating | ≤500 |
| Tools | ≤10 declarations | `tools=[]` | ~1.5k |
| History | last N turns; older summarized | session events | ≤15k |
| Retrieved knowledge | top-k chunks with ids | RAG tool or `before_model` injection | ≤6k |
| Working state | task, plan, prior step outputs | state via `{key}` / `output_key` | ≤2k |
| This turn's tool results | truncated, structured | dispatcher | ≤4k |
| Attachments | the file under discussion | artifact → `inlineData` | as needed |

- Not in context: secrets, full documents, whole memory store, other users' rows, raw stack traces.
- 1M windows don't change the budget — cost, latency, attention quality degrade with length.

### 2.5 Design & implement in ADK

- Rule: assembly is a pure function `sources → LlmRequest` with a budget per layer.
- Three decisions per item: always-on (templated) vs on-demand (tool) vs never (DB only) · who writes it and under which prefix · how it's bounded.

```python
from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest
from google.genai import types

def instruction(ctx: ReadonlyContext) -> str:
    s = ctx.state
    return f"""You are a support agent for tenant {s.get('app:tenant')}.
User: {s.get('user:name')} ({s.get('user:tier')}). Today: {s.get('temp:today')}.
Current task: {s.get('task', 'none')}.
Rules: cite doc ids; call tools for any number; never invent order data."""

async def shape_context(cb: CallbackContext, req: LlmRequest) -> None:
    req.contents = req.contents[-12:]                                   # history budget
    q = next((p.text for p in reversed(req.contents[-1].parts) if p.text), "")
    hits = await vector_search(q, tenant=cb.state["app:tenant"], k=5)  # orchestrator-driven RAG
    docs = "\n".join(f"[{h.id}] {h.text[:800]}" for h in hits)
    req.contents.insert(-1, types.Content(role="user", parts=[types.Part(text=f"<docs>\n{docs}\n</docs>")]))
    cb.state["temp:ctx_chars"] = sum(len(p.text or "") for c in req.contents for p in c.parts)
    return None

agent = LlmAgent(
    name="support", model="gemini-2.5-flash",
    instruction=instruction,
    tools=[get_order, search_docs],
    before_model_callback=shape_context,
    output_key="last_answer",
)
```

- State discipline: Pydantic model per key, validated in `before_agent_callback`; `temp:` intra-invocation; session for conversation; `user:` durable profile; `app:` tenant config; blobs → artifacts.
- Compaction: summarize events older than N turns with a cheap model into `state["history_summary"]`, template it, keep raw events in DB for audit.
- Observe chars/tokens per layer per call. Context bloat is the most common silent cost/latency regression.

### 2.6 Memory taxonomy & retrieval patterns

- CoALA taxonomy (legit, not invented): **procedural** (how to act — skills, instruction files), **semantic** (durable facts — vector store, profile), **episodic** (dated events — past chats, SQL).
- Consolidation: summarizer agent distills episodes into facts after N chats; cheaper model.
- Retrieval ownership (see 1.4): always-on cheap context by code; expensive/conditional lookups as tools. Start orchestrator-driven; add memory-as-tool only when evals show the model needs to pull things it isn't getting.
- ADK pieces: `MemoryService` (`add_session_to_memory`, `search_memory`), `load_memory` / `preload_memory` tools, Vertex Memory Bank.

---

## 3. Tools

### 3.1 Mechanics

- Two halves: **model side** (schema in, `functionCall` out) and **execution side** (who runs it, where). The model never executes anything.
- Define → register on agent → dispatcher matches by name → validate → run → append result → next step.
- Tool wrapper owns: timeout, retry of transient errors, structured `{error, retryable}`, idempotency key, result truncation.
- 🗣 "Model-level retry is the most expensive retry in the system — handle transient errors inside the tool."

### 3.2 Stateless vs stateful — single-instance vs pooled

| 中文 | English | Reality |
|---|---|---|
| 一个工具对应一个调用 | one tool = one call | naive model |
| 工具的状态管理模式 | tool state-management mode | stateless function vs stateful instance |
| 工具实例被占用 / 排队或报错 | instance occupied / queue or error | session/connection/process busy |
| 实例复用 | instance reuse | keep-alive, don't recreate per call |
| 工具池化 / 负载分发 | tool pooling / load dispatch | pool of N + round-robin / least-busy |
| 单实例模式 | single-instance mode | pool size = 1 |

- **Stateless tool** = pure function over args (`get_weather`, `search_docs`, REST GET). Concurrent calls never conflict; bound only by backend rate limits.
- **Stateful tool** = wraps a live resource serving one caller at a time: stdio MCP server (one process, one stream), browser page, shell/sandbox session, single DB connection, non-thread-safe SDK client.
- **Single-instance tool calling** = one such resource; second concurrent call waits (mutex/queue) or fails (busy).
- **Pooled** = N resources; dispatcher leases a free one; N+1 waits.
- 🗣 "Can two agents call the same tool concurrently? Stateless: yes, freely. Stateful: only up to pool size."
- Third axis the video misses: **shared data**. Two pooled instances writing the same row still conflict → serialize by key or CAS.

### 3.3 Framework behavior (not the video's version)

- ADK: `FunctionTool` is an async function; multiple function calls in one turn run concurrently; `ParallelAgent` branches run concurrently. No "tool state table", no "pooling flag". `MCPToolset` = one MCP session per toolset; stdio server effectively serial per session → multiple sessions or streamable-HTTP server for concurrency.
- Claude Agent SDK / CC: multiple `tool_use` blocks run concurrently when independent, serially otherwise (file edits).
- LangGraph `ToolNode`: concurrent parallel tool calls, no instance management.
- Where pooling is real: `asyncpg.create_pool`, shared `httpx.AsyncClient`, Playwright context pool, warm sandbox pools (E2B, Modal). Resource pools a tool wraps, not framework "tool pooling".

### 3.4 SDK integration

#### ADK (primary)

```python
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool, AgentTool, ToolContext
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
from google.adk.tools.openapi_tool import OpenAPIToolset

def get_order(order_id: str, tool_context: ToolContext) -> dict:
    """Fetch one order by id. Returns status and line items."""   # docstring = model-facing description
    tool_context.state["temp:last_order"] = order_id
    return {"status": "ok", "order": db.get(order_id)}

agent = LlmAgent(
    name="support", model="gemini-2.5-flash",
    tools=[
        get_order,                                                # → FunctionTool
        MCPToolset(connection_params=StreamableHTTPConnectionParams(url="https://mcp.internal/crm"),
                   tool_filter=["search_customer", "get_ticket"]),
        OpenAPIToolset(spec_str=open("billing.yaml").read(), spec_str_type="yaml"),
        AgentTool(agent=research_agent),
    ],
    before_tool_callback=policy_check,                            # return dict → skip tool
    after_tool_callback=redact_pii,
)
```

- Schema from type hints + docstring. Return `dict`; never raise.
- `LongRunningFunctionTool` → pause for human approval, resume.
- Built-ins: `google_search`, `VertexAiSearchTool`, `BuiltInCodeExecutor`.

#### Claude Agent SDK — for comparison

```python
from claude_agent_sdk import query, ClaudeAgentOptions, tool, create_sdk_mcp_server

@tool("get_order", "Fetch one order by id", {"order_id": str})
async def get_order(args):
    return {"content": [{"type": "text", "text": json.dumps(db.get(args["order_id"]))}]}

server = create_sdk_mcp_server(name="orders", version="1.0", tools=[get_order])   # in-process MCP
opts = ClaudeAgentOptions(
    mcp_servers={"orders": server, "crm": {"type": "http", "url": "https://mcp.internal/crm"}},
    allowed_tools=["Read", "Grep", "mcp__orders__get_order", "mcp__crm__search_customer"],
    permission_mode="acceptEdits",
    hooks={"PreToolUse": [policy_hook], "PostToolUse": [audit_hook]},
)
```

- Every custom tool is an MCP tool, even in-process. Built-ins: Read/Write/Edit/Bash/Grep/Glob/WebFetch/WebSearch/Task.

#### OpenAI Agents SDK — for comparison

```python
from agents import Agent, Runner, function_tool, WebSearchTool
from agents.mcp import MCPServerStreamableHttp

@function_tool
def get_order(order_id: str) -> dict:
    """Fetch one order by id."""
    return db.get(order_id)

agent = Agent(name="support", model="gpt-4.1",
              tools=[get_order, WebSearchTool(), research_agent.as_tool("research", "Deep-dive a topic")],
              mcp_servers=[MCPServerStreamableHttp(params={"url": "https://mcp.internal/crm"})],
              handoffs=[billing_agent])
```

#### Side by side

| | ADK | Claude Agent SDK | OpenAI Agents SDK |
|---|---|---|---|
| Define a tool | Python func → `FunctionTool` | `@tool` → in-process MCP server | `@function_tool` |
| Schema source | type hints + docstring | explicit dict / JSON schema | Pydantic from signature |
| MCP client | `MCPToolset` (stdio/SSE/HTTP) | `mcp_servers` config | `MCPServer*` or `HostedMCPTool` |
| Agent as tool | `AgentTool` | `Task` subagents | `agent.as_tool()` |
| Handoff | `sub_agents` + `transfer_to_agent` | — | `handoffs` |
| Interception | `before/after_tool_callback`, plugins | `PreToolUse/PostToolUse`, `can_use_tool` | guardrails, `RunHooks` |
| HITL | `LongRunningFunctionTool` | permission prompts | `needs_approval` |
| Parallel tool calls | yes | yes (independent) | yes |
| Sweet spot | Gemini + GCP, workflow agents | coding / filesystem agents | OpenAI models |

- Tool wrappers (idempotency, pooling, errors) are identical code in all three.

### 3.5 Designing tool concurrency

- Step 1 — classify each tool stateless / stateful; write it in the docstring.
- Step 2 — stateless: semaphore sized to backend rate limit.

```python
_sem = asyncio.Semaphore(20)
async def search_docs(q: str) -> dict:
    async with _sem:
        return await client.search(q)
```

- Step 3 — stateful: pool with lease/release; reset state on return.

```python
class BrowserPool:
    def __init__(self, n): self._q = asyncio.Queue(); self.n = n
    async def start(self):
        for _ in range(self.n): await self._q.put(await new_page())
    @asynccontextmanager
    async def lease(self, timeout=30):
        page = await asyncio.wait_for(self._q.get(), timeout)
        try: yield page
        finally: await page.reset(); await self._q.put(page)

pool = BrowserPool(4)
async def fetch_rendered(url: str) -> dict:
    async with pool.lease() as page:
        await page.goto(url); return {"html": await page.content()}
```

- Step 4 — per-agent affinity when state must persist across steps (shell, browser): pin instance id in `temp:` state; pool per invocation, not shared. Sharing a stateful instance across agents is a bug.
- Step 5 — wait-with-timeout → `{error:"busy", retryable:true}` default; fail-fast when the model has an alternative.
- Step 6 — data conflicts: same key write+write → `asyncio.Lock` per key or DB row lock / CAS. Read-only + different keys → always parallel.
- Step 7 — observe pool utilization, wait p99, busy-timeout rate. Exhaustion shows as latency, not errors.

### 3.6 Verdict on the tool-calling video

| Claim | Verdict | Correction |
|---|---|---|
| 是否冲突取决于状态管理模式和并发配置 | Valid | stateless vs stateful decides it |
| 框架维护工具状态表记录实例占用 | Not accurate | no such table in ADK / LangGraph / Claude SDK; bookkeeping lives in resource pools you write |
| 默认单实例，已占用则排队或报错 | Valid for stateful only | stateless tools run concurrently by default |
| 实例复用开关 | real concept, wrong label | keep-alive / connection reuse; not a framework switch |
| 工具池化开关 + 调度器负载均衡 | real concept, wrong label | pattern per tool, not a flag |
| 统一工具池多实例共享 | Valid pattern | browsers, sandboxes, DB connections; meaningless for stateless tools |
| 没池化并发 → 全部阻塞 | Valid for stateful only | not for REST tools |
| 冲突 = 实例数 + 调度策略 + 池化标志 | Half right | add shared-data conflicts |

---

## 4. MCP

### 4.1 Relation to tool calling

```
model ──functionCall──► harness (MCP client) ──tools/call──► MCP server (adapter)
                                                                 │ auth, authz, validate, shape
                                                                 ▼
                                                           existing service layer ──► DB / APIs
```

- Tool calling has two halves; MCP standardizes only the **execution half**: `tools/list`, `tools/call`, plus `resources`, `prompts`.
- The model never speaks MCP. Harness = MCP client (ADK `MCPToolset`); your server = tool provider. Harness converts `tools/list` into the schemas the model sees.
- Without MCP: custom glue per harness per tool set. With MCP: write once, any client uses it (ADK, Claude, Cursor).

### 4.2 "Just a protocol translator" — yes, plus two things

- Correct: an MCP server holds no data. Facade over your DB / APIs / files.
- It is also the **security boundary**: auth, per-user authz, allow-listed operations, PII redaction.
- It is also **capability curation**: the 8 tasks the model may do, not the 80 endpoints that exist.
- 🗣 "MCP server = adapter + policy + curated surface. Thin, stateless, no data."

### 4.3 Cost

- Protocol: free. Server: a process — stdio = zero infra; streamable HTTP = normal microservice hosting.
- Real cost = **tokens**: every tool definition ships on every call (40 tools × ~150 tokens ≈ 6k/turn before the user speaks); results are tokens too.
- Mitigate: `tool_filter` to ≤10 tools per agent; paginate/truncate results (~2–4k tokens cap); prompt caching on the static prefix.
- Backend cost unchanged — your query still runs.

### 4.4 Design over existing systems (hexagonal)

- MCP server = new inbound adapter beside REST controllers; domain services unchanged; outbound adapters reused. No business logic in the MCP layer.
- Build flow:
  1. List 5–10 *tasks* in the user's words, not endpoints.
  2. Per tool: `verb_noun` name; description with when-to-use / when-not; typed params with enums; small typed result.
  3. Thin calls into the service layer; propagate user identity.
  4. Mark reads vs writes; writes take `idempotency_key`; HITL on high-blast-radius writes.
  5. Structured JSON + short summary; paginate; cap size.
  6. Errors: `isError: true` + actionable message; never a stack trace.
  7. Transport: stdio local; streamable HTTP, stateless, behind gateway for deploy; OAuth 2.1 on remote.
  8. Test: MCP Inspector; unit per tool; tool-*selection* eval (30 prompts → expected tool).
  9. Observe: latency, error rate, tokens returned per tool, calls per session.
  10. Version; deprecate with a window; clients pin by `tool_filter`.
- Patterns to name: facade / anti-corruption layer; coarse task-shaped tools over CRUD; read/write split; identity propagation (no god credential); least privilege per agent; stateless server.
- Pre-build questions: caller identity and auth path? task list and max tool count? which tools mutate, blast radius, HITL where? result size budget, PII redaction? latency budget, timeouts/retries inside the tool? multi-tenant row filtering server-side? deploy, ownership, versioning? build vs buy (Bedrock AgentCore Gateway / Apigee expose REST as MCP with no code)?
- Frameworks: Python `mcp` SDK / `fastmcp`; Java Spring AI MCP starter (natural for Spring Boot); TS `@modelcontextprotocol/sdk`.

---

## 5. Multi-agent coordination & consistency

### 5.1 Concepts — 中 / EN / DS name

| 中文 | English | Standard DS name |
|---|---|---|
| 多 Agent 协作一致性 | multi-agent collaboration consistency | distributed workflow consistency |
| 任务拆分粒度不当 → 语义重叠 | wrong granularity → semantic overlap | overlapping partitions |
| 失败重试产生脏数据 | retry creates dirty data | non-idempotent retry |
| 通信延迟 → 读写竞态 → 覆盖 | latency → race → lost update | lost update / write skew |
| 调度中心宕机 → 重发 / 漏发 | scheduler crash → resend / miss | coordinator failure; at-least-once vs at-most-once |
| 异构 Agent 协议不统一 | heterogeneous agents, no common protocol | adapter / anti-corruption layer |
| 全局任务状态机 | global task state machine | workflow state machine |
| 子任务幂等 | sub-task idempotency | idempotency key |
| 最终一致性补偿 | eventual-consistency compensation | Saga with compensating transactions |
| 语义指纹 (semantic_hash) | semantic fingerprint | normalized dedup key |
| 共享资源乐观锁 / 影响行数为零 | optimistic lock / affected 0 rows | OCC version column / CAS |
| 数据库唯一约束 | DB unique constraint | uniqueness as dedup gate |
| 降级为单 Agent 串行 + 人工对账 | degrade to serial + manual reconciliation | degraded mode + reconciliation |

- 🗣 "Nothing here is an AI problem. It's Saga + idempotency + OCC + durable state + leases, with one twist: the decomposer is non-deterministic."

### 5.2 Ground truth (pure distributed systems)

- Exactly-once delivery is impossible; at-least-once + idempotent effects = effectively-once.
- Atomicity exists only inside one DB transaction; anything across a network hop is a Saga.
- Promise: **the ledger is always correct; the world catches up to it.**
- Coordinator stateless; state durable; any replica resumes.

### 5.3 Schema everything hangs off

```sql
CREATE TABLE job  (job_id uuid PRIMARY KEY, status text, version int DEFAULT 0, input jsonb, result jsonb);
CREATE TABLE step (
  job_id uuid REFERENCES job, step_id text,          -- deterministic from inputs
  dedup_key text NOT NULL, status text, version int DEFAULT 0, attempt int DEFAULT 0,
  lease_owner text, lease_until timestamptz,
  idem_key text NOT NULL, result jsonb, error jsonb,
  PRIMARY KEY (job_id, step_id), UNIQUE (dedup_key));
CREATE TABLE outbox (id bigserial PRIMARY KEY, job_id uuid, step_id text, idem_key text, payload jsonb, status text);
```

- `UNIQUE(dedup_key)` = dedup gate · `version` = optimistic lock · `lease_*` = dead-worker detection · `idem_key` = third-party dedup.
- The video's table lacks `version`, `attempt`, `lease_*`, `idem_key` — without leases you can't detect a dead worker; without version the OCC they describe has nothing to compare.

### 5.4 Answers by question — DS answer → agent-specific addition

| Question | Distributed-systems answer | Agent-specific addition (ADK) |
|---|---|---|
| Decompose without overlap | partition by data key in code; deterministic `step_id`; coverage + disjointness check; unique constraint | move decomposition out of the model when input is enumerable; else structured output + code validation; dedup on business keys, never prose hash |
| Assign | workers **pull** with lease: `FOR UPDATE SKIP LOCKED` or queue visibility timeout; route by `required_capability` | one step = one invocation; deterministic routing on op type; `sub_agents` routing only if not enumerable, then eval it |
| Partial failure / retry | classify retryable vs terminal; retry failed steps only; retry budget; DLQ | transient errors retried inside the tool; model never sees them; `max_iterations` |
| Dual write / third party | idempotency key **to the third party**; query-before-write; outbox + reconciler | `idem_key = hash(tool, canonical(args))` in the tool wrapper so a different tool path on retry still dedups; ledger check before call |
| Compensation | Saga: compensating action per step, reverse order, idempotent | code-driven; one `compensate_*` tool per effect; never "undo yourself" |
| Race / stale state | CAS with version; fencing token for external writes; partition to avoid contention; no lock across a network call | write tools require `expected_version`; disjoint `output_key` per `ParallelAgent` branch; `temp:` collisions |
| Coordinator loss | stateless coordinator; on restart scan PENDING/LEASED; reaper re-leases expired; multiple coordinators fine (atomic claim) | ADK session store ≠ job ledger (no tx across events); keep ledger outside; replay steps, not reasoning |
| Async / heterogeneous | adapter; long lease; idempotent callback (`UPDATE … WHERE status='LEASED'`); poll on silence; schema-validate output | A2A task lifecycle; remote agent returns, adapter writes ledger |
| Aggregate | counter → AGGREGATING; read from ledger not messages; aggregation is a retryable step; validate invariants | structured outputs only; LLM aggregator cites `step_id`; conflicts → FAILED + human |
| Consistency model | ledger strong; effects effectively-once; Saga eventual; stateless coordinator | plus: decomposition in code, idempotency in tools, schema at every boundary |

- Buy before build: Temporal / Step Functions / Cloud Workflows implement the ledger + retries + compensation + timers.

```python
async def refund(order_id: str, amount: int, tool_context: ToolContext) -> dict:
    key = f"{tool_context.state['step_id']}:refund:{order_id}:{amount}"
    if (prior := await ledger.get(key)):
        return prior                                           # replay, no second charge
    res = await stripe.refund(order_id, amount, idempotency_key=key)
    await ledger.put(key, res)
    return {"ok": True, "refund_id": res.id, "retryable": False}
```

### 5.5 Verdict on the consistency video

| Claim | Verdict | Correction |
|---|---|---|
| 一致性定义 + 五个失效场景 | Valid | add zombie worker (expired lease still writing) → fencing token |
| 基线 = 状态机 + 幂等 + 补偿 | Valid | name it: Saga + durable state |
| agent_collab_task 表 | Mostly valid | missing `version`, `attempt`, `lease_*`, `idem_key` |
| 语义指纹去重 + 唯一约束 | Partly valid | unique constraint correct; hashing prose doesn't catch paraphrase; use business keys |
| 乐观锁，第二条影响行数为零 | Valid | textbook CAS |
| 子任务全部幂等 | Valid but incomplete | only stops double charge if key reaches the third party or query-before-write |
| 中心化调度只分发，一致性靠分布式状态机 | Valid | phrase it "no *stateful* scheduler", not "no scheduler" |
| 协议适配层 | Valid | add output schema validation; adapter writes ledger |
| 同一事务写状态 + 记录 | Valid | covers ledger, not external effects → outbox |
| 7 天归档 | Valid, minor | archive terminal states only; no retry window problem |
| 监控四指标 | Valid | add steps/job p99, lease-expiry rate, DLQ depth, reconciliation diff |
| 降级串行 + 人工对账 | Valid | good degraded mode |

- Overall: competent Saga explanation relabeled for agents. Gaps: no leases/fencing; semantic dedup hand-waved; "no central scheduler" misleading.

### 5.6 ADK multi-agent primitives (where the above lands)

| Primitive | Semantics | Use when | Hazard |
|---|---|---|---|
| `SequentialAgent` | code-ordered steps, shared state via `output_key` | order known | none; preferred |
| `ParallelAgent` | concurrent branches, shared state map | independent reads | same-key writes race → disjoint keys |
| `LoopAgent` | repeat until `escalate` or `max_iterations` | critic/refine | runaway without cap |
| `LlmAgent` + `sub_agents` | model transfers control | genuine branching | routing by description → eval set |
| `AgentTool` | invoke agent, get value back | context isolation | returns summary only |
| A2A | remote agent task lifecycle | foreign framework | adapter + schema validation |

---

## 6. Full system — the seven layers

```
[UI]  React chat ──SSE──►  [API]  FastAPI ──►  [HARNESS]  ADK Runner + LlmAgent
                                                   ├── context assembly
                                                   ├── model gateway ──► Gemini / Claude via LiteLlm
                                                   ├── tool dispatcher ──► DB, HTTP, MCP, sandbox
                                                   └── stop / budget / guardrail
   [RETRIEVAL] pgvector   [MEMORY] SessionService   [TOOLS]   [EVAL] adk eval + judge   [OBS] OTEL → Langfuse
   ──────────────── [INFRA] Docker → Cloud Run / GKE / Agent Engine, CI gate, secrets, IAM ────────────────
```

- Inseparable core (MVP0): UI ↔ API ↔ Harness ↔ Model. First useful additions: tools, retrieval. Production: eval, guardrails, observability, persistence.

| Layer | Purpose | Inseparable parts | Boring default | Watch for |
|---|---|---|---|---|
| Frontend | stream, stay responsive, upload, render | message model, SSE reader, abort, presigned upload, sanitized markdown | `fetch`+`ReadableStream`, `react-markdown`+sanitize | XSS from model HTML; bytes through chat call |
| API | edge: auth, sessions, streaming, limits | `/chat` SSE, `/upload`, session CRUD, auth mw, async I/O | FastAPI + uvicorn; ADK `get_fast_api_app` for MVP0 | one blocking call serializes server |
| Harness | the loop | `Runner`, `LlmAgent`, workflow agents, `SessionService`, state scopes, callbacks | `SequentialAgent` when order known | untyped state; runaway loops; misrouting |
| Tools | typed, bounded actions | schema, dispatcher, validation, structured errors, allowlist, idempotency | `FunctionTool`; `MCPToolset` for shared; typed DB tools before text-to-SQL | hallucinated args on prod DB |
| Retrieval | right facts in context | chunk, embed, store+ACL, top-k, rerank, freshness | pgvector; hybrid BM25+vector | wrong doc with confidence; tenant leak |
| Memory/state | history + user facts | events, compaction, `user:` scope, artifacts | ADK state first; memory service later | session bloat = latency growth |
| Eval | detect regressions first | golden set, judge + kappa ≥ 0.6, CI gate, online signals | `adk eval` + Langfuse datasets | judge never validated; no gate |
| Guardrails | bound read/say/do | input+output filters, allowlist, HITL, injection-as-data | ADK plugins; mechanical gates first | confused deputy; RAG injection |
| Observability | why wrong/slow/costly | trace/spans, event stream, p99 distributions, versions on spans | OTEL → Langfuse | means hide tail; no prompt version |
| Model layer | pick, route, version | gateway, retries on 429/5xx only, fallback, small→large routing, caching | Gemini on Vertex; `LiteLlm` for others | provider outage = outage |
| Infra / MLOps | run, roll out, roll back | Docker, Cloud Run/GKE/Agent Engine, secrets, IAM, CI gate, canary | Cloud Run + Cloud SQL + GitHub Actions | prompts not versioned |

- LangGraph with ADK: **no**. Same layer, two harnesses. Only if durable pause/resume graphs are the core requirement.
- AWS mapping: Cloud Run ≈ Fargate/App Runner; Agent Engine ≈ Bedrock AgentCore; Vertex ≈ Bedrock; Pub/Sub ≈ SQS/SNS; Cloud SQL ≈ RDS.
- ML vocab, one sentence each: attention cost grows with context; embeddings = cosine ≈ similarity; pretrain → SFT → RLHF; LoRA = adapter matrices; GAN / VAE / diffusion one-liners; you consume models, don't train.

---

## 7. Study plan & summary table

### 7.1 Six-week MVP ladder

| Week | Build | Exit criterion |
|---|---|---|
| 1 MVP0 | FastAPI `/chat` SSE ← `LlmAgent` (Gemini), zero tools; React streaming page; Docker | tokens stream in a container |
| 2 MVP1 | `DatabaseSessionService`; two `FunctionTool`s; tool events in UI; `max_iterations` | multi-turn survives restart; tool errors don't crash |
| 3 MVP2 | ingest → pgvector; `search_docs` with citations; `/upload` → GCS → artifact | upload PDF, get cited answer |
| 4 Prod layers | plugins: OTEL→Langfuse, PII redaction, allowlist; `adk eval` 30 cases + judge; CI gate | bad prompt change fails CI |
| 5 Orchestration + deploy | one flow as `SequentialAgent`; Cloud Run + Cloud SQL + Secret Manager; canary prompt flag | deployed URL; rollback shown |
| 6 Polish | system design answer for this product; drill table; ML vocab; GCP↔AWS mapping aloud | — |

### 7.2 Master summary

| Topic | Core mechanism | ADK name | Decider | Failure prevented |
|---|---|---|---|---|
| Harness | loop: assemble → call → dispatch → stop | `Runner` + `run_async` | — | model treated as the agent |
| Control flow | code vs model decides | workflow agents vs `LlmAgent` | can the sequence be enumerated? | non-deterministic routing |
| Parsing | structured `functionCall` parts | `Event.function_call` | — | prose regex brittleness |
| Done | zero tool calls + hard caps in code | `max_iterations`, `end_invocation` | — | runaway loop |
| Guardrails | code > config > prompt | callbacks, plugins | blast radius | confused deputy |
| Context | request body → tokens; sources persist, context doesn't | `LlmRequest`, `SessionService` | always-on vs on-demand | bloat, leaks |
| State | JSON dict, not auto-injected, prefixed scopes | `session.state`, `{key}` templating | lifetime | untyped contract breaks |
| Tools | schema in, call out; wrapper owns reliability | `FunctionTool`, `MCPToolset` | stateless vs stateful | hallucinated args; expensive retries |
| Concurrency | stateless free; stateful pooled; data-level CAS | `ParallelAgent`, your pool | pool size; shared keys | blocking; lost update |
| MCP | standard execution half; adapter + policy | `MCPToolset` | tokens per tool | glue per harness |
| Multi-agent | Saga + idempotency + OCC + leases | `SequentialAgent` + external ledger | enumerable decomposition? | duplicates, dual writes |
| Sandbox | per-task isolated runtime | code executors / E2B | trust level | host compromise |
| Eval | golden set + validated judge + CI gate | `adk eval` | kappa | silent regression |

---

## 8. Interview one-liners

- 🗣 Harness: "A loop that assembles context, calls a stateless model, dispatches tools, and decides when to stop."
- 🗣 Orchestrator vs agent: "Show me two inputs where the sequence differs; otherwise it's a `SequentialAgent`."
- 🗣 Done: "Hard stops in code, soft stops in the prompt."
- 🗣 Context: "Context exists for milliseconds as a request body; what persists is the raw material to rebuild it."
- 🗣 Tools: "Model-level retry is the most expensive retry in the system."
- 🗣 Concurrency: "Stateless tools run freely; stateful ones up to pool size; shared rows still need CAS."
- 🗣 MCP: "Adapter + policy + curated surface. Thin, stateless, no data; the cost is tokens."
- 🗣 Multi-agent: "Agents are unreliable workers with non-deterministic control flow; the machinery is a microservice Saga, and the agent-specific work is pushing decomposition, idempotency and compensation into code and tools."
- 🗣 Subagents: "Context isolation, not parallelism."
- 🗣 LangGraph with ADK: "Same layer, pick one."

---

## 9. References

1. https://github.com/google/adk-python — `runners.py`, `flows/llm_flows/contents.py`, `instructions.py`, `functions.py`, `agents/parallel_agent.py`, `tools/mcp_tool/`, `cli/fast_api.py`
2. https://adk.dev/ — `/sessions/state/`, `/callbacks/`, `/tools/`, `/streaming/`, `/evaluate/`, `/deploy/`
3. https://github.com/google/adk-samples — end-to-end streaming + deployment
4. https://github.com/anthropics/claude-agent-sdk-python — the same loop as a library; tool-dispatch path
5. https://github.com/anthropic-experimental/sandbox-runtime — OS-level sandbox, readable in one sitting
6. https://www.anthropic.com/research/building-effective-agents — workflow vs agent, canonical statement
7. https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents — budgeting, compaction, subagents
8. https://arxiv.org/abs/2309.02427 — CoALA memory taxonomy
9. https://github.com/temporalio/samples-python — Saga, retries, idempotent activities
10. https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html — fencing tokens
11. https://microservices.io/patterns/data/saga.html · https://microservices.io/patterns/data/transactional-outbox.html
12. https://modelcontextprotocol.io/specification/2025-06-18/basic/transports — stdio vs streamable HTTP
13. https://github.com/jlowin/fastmcp · Spring AI MCP examples: https://github.com/spring-projects/spring-ai-examples/tree/main/model-context-protocol
14. https://a2a-protocol.org/ — async / heterogeneous agent lifecycle
15. https://github.com/pgvector/pgvector · https://github.com/assistant-ui/assistant-ui