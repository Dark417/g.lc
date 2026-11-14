# 1.chatbot-nextjs

Minimum multi-turn chatbot. **FastAPI + Google ADK** backend, **Next.js** frontend. Small code, full deployable structure.

## What you'll learn

- How ADK's `Agent` → `Runner` → `SessionService` fit together (`backend/app/services/chat_service.py`).
- Keeping the agent runtime behind a service boundary so the API is testable without a model.
- A monorepo slice where backend and frontend are separate deployables with their own Dockerfile, k8s manifests, and CI.

## Layout

```
backend/    FastAPI + ADK      (uv, pyproject, Dockerfile, tests)
frontend/   Next.js            (npm, Dockerfile)
deploy/     docker-compose + k8s (kustomize)
docs/       DESIGN.md, DEPLOY.md
```

## Quickstart

```bash
cp backend/.env.example backend/.env       # put GOOGLE_API_KEY in
docker compose -f deploy/docker-compose.yaml up --build
open http://localhost:3000                 # backend docs: http://localhost:8000/docs
```

Without Docker: see `docs/DEPLOY.md` section 1.

## API

`POST /api/v1/chat`

```json
{ "message": "hi", "session_id": null }
```
→
```json
{ "session_id": "6b1e...", "reply": "Hello! How can I help?" }
```

Send `session_id` back on the next turn to continue the conversation.

## Tests

```bash
cd backend && uv sync && uv run pytest -q
```

No API key needed. The HTTP tests use a fake service; `test_adk_service.py` runs the real ADK Runner with a stub agent.

## Next

`../1.chatbot-angular` is the same backend with an Angular frontend. `../2.angular-full` adds tools, RAG, MCP, streaming, and evals.

## References

1. [google/adk-python](https://github.com/google/adk-python), [adk-samples](https://github.com/google/adk-samples)
2. [ADK: Runner and Sessions](https://google.github.io/adk-docs/sessions/)
3. [FastAPI lifespan events](https://fastapi.tiangolo.com/advanced/events/)
4. [Next.js standalone output](https://nextjs.org/docs/app/api-reference/config/next-config-js/output)
