# AGENTS.md: 2.angular-full

Project-specific rules. Repo-wide rules are in `../AGENTS.md`.

## Intent

Show every component of an applied-AI backend wired together, each in its smallest honest form. Keep components small; keep the seams obvious.

## Map

- `backend/app/main.py`: startup order (DB → RAG → MCP → agents → sessions → service). The only place infrastructure is assembled for the API.
- `backend/app/agents/agent.py`: same assembly for ADK's CLI (`adk web`, `adk eval`). Keep it in sync with `main.py`.
- `backend/app/agents/factory.py`: builds the tree. `orchestrator.py` (root, AgentTools), `data_agent.py`, `knowledge_agent.py`, `writer_pipeline.py` (Sequential + Loop).
- `backend/app/services/chat_service.py`: Runner + `translate_event`. Wire format lives in `schemas.py`.
- `backend/app/tools/`: `local_tools.py` (plain), `db_tools.py` (factory over db path), `rag_tools.py` (factory over retriever), `mcp_tools.py` (client config).
- `backend/app/rag/`: `embedder.py`, `vector_store.py`, `chunker.py`, `retriever.py`, `factory.py`. Two implementations per Protocol.
- `backend/app/mcp/server.py`: the MCP server. `Dockerfile.mcp` ships it standalone.
- `backend/evals/`: eval sets, one folder per criteria set. `evals/README.md`.
- `frontend/src/app/chat/`: `chat.service.ts` (JSON + SSE parsing), `chat.component.*` (messages + trace panel).

## Rules

- **Tests need no API key.** Anything touching a model is `@pytest.mark.eval`. Fake at the `ChatService` seam (HTTP tests) or with a scripted `BaseAgent` (service tests).
- **Adding a tool:** write the function with a docstring (`Args:` section), add it to the right agent in `factory.py`, add a case to `tests/test_agent_wiring.py`, and consider an eval case.
- **Adding a swappable implementation:** implement the Protocol, add a branch in the matching `factory.py`, add the env option in `config.py` and `.env.example`. Mark it `ILLUSTRATION` or `PRODUCTION`.
- **Changing the wire format:** `schemas.py`, `translate_event`, `chat.service.ts`, and the tests for both, in one commit.
- `run_sql_query` must stay SELECT-only. Don't loosen the guard for convenience.
- Don't build agents at import time anywhere except `app/agents/agent.py`.

## Verify

```bash
cd backend && uv run ruff check . && uv run ruff format --check . && uv run pytest -q
cd frontend && npm test && npm run build
# with a key:
cd backend && uv run adk web app/agents         # click through the tree
uv sync --extra eval && uv run pytest -m eval -s
```
