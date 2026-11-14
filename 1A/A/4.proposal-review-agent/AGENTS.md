# AGENTS.md: 4.proposal-review-agent

Project rules. Repo-wide rules are in `../AGENTS.md`. Design lives in `docs/design/`; update it in the same change when behaviour changes.

## Invariants (do not break)

1. **Verdicts are aggregated in code.** `app/domain/verdicts.py::aggregate` decides the verdict from findings. Never let a prompt, a tool, or the agent's prose override it. Severity always comes from the database (`validate_findings`).
2. **Roles are server-side.** Role comes from `ADMIN_USERS` via `Identity` (API) and `before_agent_callback` (agent). Never accept a role from the client or from model output.
3. **Admin tools stay gated in three layers.** `RoleGatedToolset` hides them, `before_tool_callback` denies them, and REST uses `require_admin`. A test proves ADK still resolves hidden tools by name, so layer 2 is required.
4. **Conversations and memories are per user.** Every session and memory query is scoped to `identity.user_id`.
5. **Extracted rules are proposals.** Nothing writes a rule without an explicit admin action.
6. **The MCP server is read-only and HTTP-only.** It never touches a database. The backend maps its token to role `user`.
7. **`app_name` equals the ADK agent directory name** (`compliance_agent`), so the dev UI and portal share sessions.

## Map

- Composition root: `app/container.py`. Add an adapter here: a Protocol implementation, a branch in the matching `_x()` factory, a setting in `config.py`, and a line in `.env.example`. Mark it `ILLUSTRATION` or `PRODUCTION`.
- Agent: `app/agents/builder.py` (LlmAgent + App + plugins), `tools.py` (closures over the container), `toolsets.py`, `callbacks.py`, `prompts.py`. ADK entry point: `app/adk_apps/compliance_agent/agent.py`.
- Verdict pipeline: `app/services/assessment.py` + `app/domain/verdicts.py`.
- Ingestion: `app/services/ingestion.py` + `app/rag/*`. Add a format by adding a parser to `PARSERS` in `app/rag/parsers.py`, plus a test in `tests/test_parsing.py`.
- Chat wire format: `app/services/chat.py::translate_event` and `frontend/src/app/core/models.ts`. Change both together.

## Adding a tool

1. Write an async function in `app/agents/tools.py` with a docstring and an `Args:` section. Take `tool_context: ToolContext` if you need the user or session.
2. Put it in `user_tools` or `admin_tools`.
3. Add it to `tests/test_agent.py` (visibility for the role) and, if it writes, add an authz test.

## Tests

- No test may call a real model. Use `FakeLLM` (structured calls) and `ScriptedModel` (the ADK agent loop) from `tests/conftest.py`.
- Real stores: `TEST_PG_URL` and `TEST_MONGO_URL` enable the `integration` tests. CI provides both.
- Real-model evals: `python -m app.evals.run`, or `pytest -m eval`.

## Verify

```bash
cd backend && uv run ruff check . && uv run ruff format --check . && uv run pytest -q
cd mcp-server && uv run ruff check . && uv run pytest -q
cd frontend && npm test && npm run build
cd infra/terraform && terraform fmt -check -recursive && terraform validate
```
