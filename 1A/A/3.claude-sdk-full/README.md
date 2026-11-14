# 3.claude-sdk-full

`2.angular-full` with the agent runtime swapped: **Claude Agent SDK** instead of Google ADK. Same Angular frontend, same wire format, same tools, same data, same deploy shape. Diff the two `backend/app/agents/` directories and you have the whole lesson.

| Component | Project 2 (ADK) | Here (Claude Agent SDK) |
|---|---|---|
| Loop + orchestrator | `Runner` + `LlmAgent` | `query()` + `ClaudeAgentOptions.system_prompt` |
| Specialists | `AgentTool(LlmAgent)` | `agents={...: AgentDefinition}` + built-in `Task` tool |
| Our tools | functions passed straight to ADK | same functions, wrapped by `as_sdk_tool` into an in-process MCP server (`mcp__local__*`) |
| External MCP | `McpToolset` | `mcp_servers={"support": {"type": "stdio"|"http"}}` |
| Refinement loop | `LoopAgent` + `escalate` | hand-written `for` loop in `writer_loop.py` behind a tool |
| Sessions | `SessionService` | CLI transcripts + `session_id` / `resume` (`SessionStore` for prod) |
| Streaming | `StreamingMode.SSE` | `include_partial_messages=True` |
| Evals | `AgentEvaluator` + evalset JSON | hand-written harness: trajectory check + structured-output LLM judge |
| RAG / SQLite / local tools / frontend / deploy | unchanged | unchanged (embedder swap example is Voyage instead of Gemini) |

## Quickstart

```bash
cp backend/.env.example backend/.env       # put ANTHROPIC_API_KEY in
docker compose -f deploy/docker-compose.yaml up --build
open http://localhost:4200
```

Same prompts as project 2 work. In the trace panel you'll see `Task` calls (subagents) and `mcp__local__*` / `mcp__support__*` tool names.

## Layout

```
backend/
  app/agents/     orchestrator (options), tools_server (adapter), writer_loop, llm, factory
  app/evals/      harness.py, run.py          <- hand-rolled evals
  evals/          cases.json + README
  app/services/   chat_service.py (query() + translate_message + streaming)
  app/{tools,rag,db,mcp,api}/   as in project 2
  tests/          29 tests, no API key, no CLI spawned
frontend/         unchanged Angular app
deploy/           compose (stdio MCP) and k8s (separate MCP service, PVC)
docs/             DESIGN.md (mapping table, decisions), DEPLOY.md
```

## Tests and evals

```bash
cd backend && uv sync && uv run pytest -q                 # 29 passed
cd frontend && npm test                                   # 3 passed

ANTHROPIC_API_KEY=... uv run python -m app.evals.run      # 5 cases, prints a table
```

## Notes on the SDK

- `claude-agent-sdk` bundles the Claude Code CLI binary; no Node in the image.
- Built-in coding tools are disabled (`tools=["Task"]`); the model only sees our MCP tools and subagents.
- `permission_mode="dontAsk"`: non-interactive, deny by default, allow by list.
- The writer loop and the eval judge call the Messages API directly (`anthropic` SDK), because a single prompt does not need an agent loop.

## References

1. [anthropics/claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python) (see `examples/` for subagents, MCP, streaming, hooks)
2. [Claude Agent SDK docs](https://code.claude.com/docs/en/agent-sdk), [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) (structured outputs via `messages.parse`)
3. [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) and [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
4. [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk) (v2 migration: FastMCP -> MCPServer)
