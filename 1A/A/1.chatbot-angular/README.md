# 1.chatbot-angular

Minimum multi-turn chatbot. **FastAPI + Google ADK** backend (identical to `1.chatbot-nextjs`), **Angular** frontend served by nginx.

## What you'll learn

- Same backend lessons as `../1.chatbot-nextjs` (ADK `Agent` → `Runner` → `SessionService`, service boundary, tests without a model).
- Angular standalone components + signals + `HttpClient`, with one `ChatService` owning the backend contract.
- The nginx-sidecar deployment pattern for SPAs: static files + `/api` reverse proxy in one image, so the browser is same-origin and no build-time URL baking is needed.

## Layout

```
backend/    FastAPI + ADK      (uv, pyproject, Dockerfile, tests)
frontend/   Angular 21         (npm, nginx Dockerfile, vitest)
deploy/     docker-compose + k8s (kustomize)
docs/       DESIGN.md, DEPLOY.md
```

## Quickstart

```bash
cp backend/.env.example backend/.env       # put GOOGLE_API_KEY in
docker compose -f deploy/docker-compose.yaml up --build
open http://localhost:4200
```

Without Docker:

```bash
cd backend && cp .env.example .env && uv sync && uv run uvicorn app.main:app --reload --port 8000
cd frontend && npm install && npm start    # http://localhost:4200, calls http://localhost:8000 directly
```

## API

`POST /api/v1/chat` `{ "message": "hi", "session_id": null }` → `{ "session_id": "...", "reply": "..." }`. See `../1.chatbot-nextjs/README.md`.

## Tests

```bash
cd backend && uv run pytest -q             # 6 tests, no API key
cd frontend && npm test                    # vitest + HttpTestingController
```

## Next.js vs Angular: what actually differs

| Concern | Next.js | Angular |
|---|---|---|
| Backend URL | `NEXT_PUBLIC_API_URL`, baked at build time | `environment.ts` (dev) / `''` same-origin (prod) |
| Serving in prod | Node server (`output: standalone`) | nginx static + `/api` proxy |
| HTTP | `fetch` | `HttpClient` (interceptors, testing controller) |
| State | `useState` | signals |

## References

1. [angular/angular](https://github.com/angular/angular): [Signals](https://angular.dev/guide/signals), [HttpClient](https://angular.dev/guide/http)
2. [nginx-unprivileged image](https://github.com/nginx/docker-nginx-unprivileged) and [nginx env templates](https://hub.docker.com/_/nginx) ("Using environment variables in nginx configuration")
3. [google/adk-python](https://github.com/google/adk-python)
