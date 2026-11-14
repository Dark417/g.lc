# AGENTS.md: 1.chatbot-angular

Project-specific rules. Repo-wide rules are in `../AGENTS.md`.

## Intent

Same minimum chatbot as `../1.chatbot-nextjs`, Angular frontend. **Do not add features here**; they belong in `../2.angular-full`.

## Map

- `backend/`: identical to `1.chatbot-nextjs/backend` except package name and default CORS port (4200). Keep them in sync; if you fix a bug in one, fix it in the other.
- `frontend/src/app/chat/chat.service.ts`: the only file that knows the backend URL and wire format.
- `frontend/src/app/chat/chat.component.*`: the UI. Signals for state, `FormsModule` for the input.
- `frontend/src/environments/`: `apiUrl` per environment. Production is `''` (same-origin).
- `frontend/nginx.conf`: SPA fallback + `/api/` proxy. `BACKEND_URL` is env-substituted at container start.
- `deploy/`: compose maps 4200→8080; k8s Ingress sends everything to the frontend pod and nginx forwards `/api`.

## Rules

- Frontend tests use `HttpTestingController`; never hit a real backend in `npm test`.
- Keep the nginx `proxy_pass` prefix-preserving (`/api/` → `${BACKEND_URL}/api/`); the backend routes are mounted at `/api/v1`.
- If you change `schemas.py`, change `chat.service.ts` in the same commit.

## Verify

```bash
cd backend && uv run ruff check . && uv run ruff format --check . && uv run pytest -q
cd frontend && npm test && npm run build
```
