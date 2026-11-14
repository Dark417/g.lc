# Design: 3.claude-sdk-full

## Problem

Project 2 wired every component with Google ADK. Frameworks hide different things. Rebuilding the same system on the **Claude Agent SDK** shows which parts were framework and which parts were yours, and forces you to write the two pieces ADK gave you for free: the refinement loop and the evaluator.

## Who it's for

Me. Same system, different runtime, same frontend. Diff the two projects to learn the seams.

## Success metric

- Same Angular frontend, unchanged, talks to this backend: the wire format is identical.
- Every component has a no-API-key test. `pytest -m eval` gives a pass/fail number with a key.
- The `docs/DESIGN.md` mapping table below is enough to port a third runtime.

## Non-goals

- Feature parity in every corner (e.g. ADK's eval UI).
- Using the SDK's built-in coding tools (Read/Write/Bash). This is not a coding agent; they are disabled.

## The system

```
Angular ──POST /api/v1/chat[/stream]──▶ FastAPI ──▶ ClaudeChatService ──▶ claude_agent_sdk.query()
                                                                                │  (spawns the bundled Claude Code CLI)
                              ┌────────────────── orchestrator (system_prompt) ◀┘
                              │  tools: mcp__local__calculate, mcp__local__get_current_time, mcp__local__write_polished_text
                              │  Task ─▶ data_agent (AgentDefinition) ─▶ mcp__local__{describe_schema,list_customers,get_customer_orders,run_sql_query} ─▶ SQLite
                              │  Task ─▶ knowledge_agent (AgentDefinition) ─▶ mcp__local__search_knowledge_base ─▶ Retriever ◀── data/knowledge/*.md
                              │                                             └▶ mcp__support__{get_weather,lookup_ticket,create_ticket} ──stdio/http──▶ app/mcp/server.py
                              │  write_polished_text ─▶ hand-rolled loop: Messages API drafter ⇄ critic (JSON verdict), max 3
                              ▼
   SDK messages ──translate_message()──▶ tool_call / tool_result / agent_text / delta / final_text ──▶ JSON or SSE
```

## ADK → Claude Agent SDK mapping

| Concern | 2.angular-full (ADK) | 3.claude-sdk-full (Claude Agent SDK) | What you now own |
|---|---|---|---|
| Agent loop | `Runner.run_async` yields `Event`s | `query(prompt, options)` yields `AssistantMessage` / `UserMessage` / `StreamEvent` / `ResultMessage` | nothing; both are the loop |
| Root agent | `LlmAgent(instruction, tools)` | `ClaudeAgentOptions(system_prompt, allowed_tools, ...)` | nothing |
| Specialists | `AgentTool(LlmAgent)` | `agents={name: AgentDefinition(prompt, tools)}` + built-in `Task` tool | nothing; the SDK spawns and returns |
| Function tools | pass the function; ADK reads signature + docstring | `@tool(name, desc, schema)` on an async handler returning MCP content | `as_sdk_tool` adapter (20 lines) so `app/tools/*` is unchanged |
| External MCP | `McpToolset(StdioConnectionParams / StreamableHTTPConnectionParams)` | `mcp_servers={"support": {"type": "stdio" \| "http", ...}}` | nothing |
| Iteration | `LoopAgent` + `escalate` | none | `writer_loop.py`: a `for` loop with an exit condition, exposed as a tool |
| Sessions | `SessionService` (memory / DB) | CLI transcripts under `cwd`; `session_id` / `resume` options; `session_store` protocol for a DB | the id hand-off; a `SessionStore` for prod |
| Streaming | `RunConfig(streaming_mode=SSE)`, `event.partial` | `include_partial_messages=True` → `StreamEvent` with raw API deltas | filtering deltas to the root thread |
| Trace | `event.get_function_calls()` | `ToolUseBlock` / `ToolResultBlock`; `parent_tool_use_id` marks subagent work | mapping tool_use ids back to names |
| Evals | `AgentEvaluator` + evalset JSON + `test_config.json` | none | `app/evals/harness.py`: trajectory check + structured-output LLM judge |
| Debug UI | `adk web` | none for this shape (Claude Code itself is the CLI) | the trace panel is your UI |

## Key decisions

- **In-process MCP server for our own tools** (`create_sdk_mcp_server`). No subprocess, no extra service, and the same `app/tools` functions as project 2. Tool ids become `mcp__local__<name>`; the trace shows them verbatim so the naming is not magic.
- **Subagents get an explicit `tools=` list.** `data_agent` cannot touch RAG or MCP; `knowledge_agent` cannot touch the DB. Least privilege is one list per agent.
- **`permission_mode="dontAsk"` + explicit `allowed_tools` + `tools=["Task"]`.** Non-interactive server: anything not allowed is denied, and the coding tools are simply not present.
- **`setting_sources=[]` and `env={ANTHROPIC_API_KEY}`.** The server never inherits the developer's `~/.claude` config, and the key comes from `Settings`, not ambient env.
- **The writer loop calls the Messages API directly**, not the agent runtime. Draft/critique is two single-shot prompts per iteration; an agent loop would be overkill. Critic output is JSON parsed defensively.
- **Judge uses structured outputs** (`messages.parse` → `Verdict`). Deterministic trajectory check first (free), LLM judge second (costs money), both injectable.
- **`Task` is what the root trace sees.** Tool calls *inside* a subagent are not visible to the parent's trace, so eval cases for DB/RAG assert `Task` and rely on the rubric for the rest. This is a real limitation to know about.

## Build-vs-buy

| Choice | Why |
|---|---|
| Claude Agent SDK vs Anthropic SDK tool runner | The Agent SDK gives subagents, MCP client, sessions, permissions and streaming for free. The tool runner (`client.beta.messages.tool_runner`) would be the leaner choice if you only needed the loop over your own tools and no subagents. |
| Hand-rolled loop vs a workflow library | 40 lines. Adding a library to avoid a `for` loop is the wrong trade. |
| Hand-rolled eval vs ADK's | Only because ADK's evaluator is coupled to ADK agents. The harness is 120 lines and now you know what "trajectory score" means. |

## Failure modes to know

- Each `query()` spawns the CLI (~1s). Fine for a tutorial; for throughput use `ClaudeSDKClient` (persistent connection) or pool workers.
- The CLI writes transcripts under `cwd`/`HOME`. In containers both must be writable (Dockerfile sets `HOME`; `WORKDIR` is on the volume). Two pods sharing the volume will race; keep `replicas: 1` or implement `SessionStore`.
- `resume` on an unknown session id errors. The API hands ids out; it never accepts client-invented ones.
- `dontAsk` denies silently from the model's view (it sees a permission error as a tool result). If a tool "never gets called", check `allowed_tools` first.
- `max_turns` caps runaway loops; `total_cost_usd` on `ResultMessage` is surfaced on the `session` event for budgeting.
