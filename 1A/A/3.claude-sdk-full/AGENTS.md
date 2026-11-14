# AGENTS.md: 3.claude-sdk-full

Project-specific rules. Repo-wide rules are in `../AGENTS.md`.

## Intent

Project 2 rebuilt on the Claude Agent SDK. Same frontend, same wire format, same tools, same data. Differences are confined to `backend/app/agents/`, `backend/app/services/chat_service.py`, and `backend/app/evals/`.

## Map

- `backend/app/agents/orchestrator.py`: `ClaudeAgentOptions` (system prompt, subagents as `AgentDefinition`, MCP servers, `allowed_tools`, permission mode). The tree lives here.
- `backend/app/agents/tools_server.py`: `as_sdk_tool` adapter + in-process MCP server. Tool ids are `mcp__local__<fn>`.
- `backend/app/agents/writer_loop.py`: the hand-rolled draft/critique loop, exposed as `write_polished_text`.
- `backend/app/agents/llm.py`: single-shot Messages API calls (`ClaudeText`, `parse_structured`). Inject fakes here in tests.
- `backend/app/agents/factory.py`: settings + retriever + llm -> options. `main.py` is the only caller.
- `backend/app/services/chat_service.py`: `query()` + `translate_message`. Wire format is in `schemas.py` and must stay identical to project 2.
- `backend/app/evals/harness.py`: eval harness (trajectory + LLM judge). `evals/cases.json` holds cases. `app/evals/run.py` is the entry point.
- `backend/app/mcp/server.py`: external support MCP server; imports FastMCP or MCPServer depending on the mcp major version.
- Everything under `backend/app/{tools,rag,db,api}` is identical to project 2. If you fix something there, fix it in both.

## Rules

- **Tests need no API key and never spawn the CLI.** `translate_message`, the tools adapter, the writer loop, the harness, and options wiring are all tested with fakes. Anything that runs `query()` is `@pytest.mark.eval`.
- **Adding a tool:** write the function in `app/tools/`, add it to `factory.build_options`, add its name to the right list in `orchestrator.py` (`LOCAL_TOOLS` / `DB_TOOLS` / ...), and extend `tests/test_options_wiring.py`. If it isn't in `allowed_tools` the model can't call it.
- **Adding a subagent:** an `AgentDefinition` in `orchestrator.py` with an explicit `tools=` list; mention it in `ORCHESTRATOR_PROMPT`.
- Keep `tools=["Task"]`; never enable the coding tools (Read/Write/Bash) in this service.
- `run_sql_query` must stay SELECT-only.
- Don't build options at import time anywhere.

## Verify

```bash
cd backend && uv run ruff check . && uv run ruff format --check . && uv run pytest -q   # 29 passed
cd frontend && npm test && npm run build
# with a key:
cd backend && uv run python -m app.evals.run
```
