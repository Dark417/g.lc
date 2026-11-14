# AGENTS.md: 1.chatbot-nextjs

Project-specific rules. Repo-wide rules are in `../AGENTS.md`.

## Intent

Minimum viable chatbot. **Do not add features here.** Capabilities (tools, RAG, MCP, streaming, evals) belong in `2.angular-full`. Changes here should only fix bugs, improve structure, or update dependencies.

## Map

- `backend/app/main.py`: app factory + lifespan (builds the ADK service).
- `backend/app/agent/agent.py`: the ADK `Agent`. Exposes `root_agent` for `adk web`.
- `backend/app/services/chat_service.py`: the only file touching ADK `Runner`. Implements the `ChatService` Protocol.
- `backend/app/api/`: routers. `deps.py` is the DI seam tests override.
- `frontend/src/lib/api.ts`: the only file that knows the backend URL.
- `frontend/src/components/ChatWindow.tsx`: the UI.
- `deploy/`: compose + kustomize.

## Rules

- Keep `AdkChatService.chat` returning only the final text. Event handling for tool traces lives in project 2.
- Tests must pass with no `GOOGLE_API_KEY`. Use `FakeChatService` from `tests/conftest.py` or `EchoAgent` from `tests/test_adk_service.py`.
- If you change the wire format (`schemas.py`), change `frontend/src/lib/api.ts` in the same commit.

## Verify

```bash
cd backend && uv run ruff check . && uv run ruff format --check . && uv run pytest -q
cd frontend && npm run lint && npm run build
docker build backend && docker build frontend
```
