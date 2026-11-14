# Deploy: 2.angular-full

## 1. Local, no Docker

```bash
cd backend && cp .env.example .env && uv sync          # set GOOGLE_API_KEY
uv run uvicorn app.main:app --reload --port 8000        # MCP server is spawned as a child (stdio)
# ADK debug UI on the same agent tree (traces, state, eval tab):
uv run adk web app/agents --port 8080

cd ../frontend && npm install && npm start              # http://localhost:4200
```

Useful while developing:

```bash
curl 'localhost:8000/api/v1/debug/rag/search?q=express%20shipping'
curl -N localhost:8000/api/v1/chat/stream -H 'content-type: application/json' -d '{"message":"what is 12*7?"}'
uv run python -m app.mcp.server --http                  # run MCP server standalone on :8001, then MCP_TRANSPORT=http
```

## 2. Local, Docker Compose

```bash
cp backend/.env.example backend/.env
docker compose -f deploy/docker-compose.yaml up --build
open http://localhost:4200
```

Sessions and the app DB live in the `backend-data` volume (`SESSION_BACKEND=sqlite`).

## 3. Build and push images

```bash
REG=ghcr.io/<you>; TAG=$(git rev-parse --short HEAD)
docker build -t $REG/angular-full-backend:$TAG backend
docker build -t $REG/angular-full-mcp:$TAG -f backend/Dockerfile.mcp backend
docker build -t $REG/angular-full-frontend:$TAG frontend
for i in backend mcp frontend; do docker push $REG/angular-full-$i:$TAG; done
```

## 4. Kubernetes

```bash
kubectl apply -f deploy/k8s/00-namespace.yaml
kubectl -n angular-full create secret generic backend-secrets --from-literal=GOOGLE_API_KEY=$GOOGLE_API_KEY
cd deploy/k8s
kustomize edit set image REGISTRY/angular-full-backend=$REG/angular-full-backend:$TAG \
                         REGISTRY/angular-full-mcp=$REG/angular-full-mcp:$TAG \
                         REGISTRY/angular-full-frontend=$REG/angular-full-frontend:$TAG
kubectl apply -k .
kubectl -n angular-full rollout status deploy/backend deploy/mcp-server deploy/frontend
```

In k8s the backend uses `MCP_TRANSPORT=http` and talks to the `mcp-server` Service. Generated data (sqlite sessions, app DB) sits on a 1Gi PVC; the backend is `replicas: 1` with `Recreate` for that reason.

### Scaling out later

1. Sessions: `SESSION_DB_URL=postgresql+asyncpg://...` (same `DatabaseSessionService`).
2. App DB: Postgres with a read-only role for the agent.
3. Vector store: `VECTOR_STORE=chroma` (+ `uv sync --extra chroma`) or pgvector, populated by an ingest Job rather than at startup.
4. Then drop the PVC and raise replicas.

## 5. CI/CD

`.github/workflows/2-angular-full.yml`: backend lint+tests, frontend tests+build, three image builds. Evals are a commented-out scheduled job; they need a secret and cost money.

## Runbook

- Backend logs `rag: indexed 0 chunks`: `KNOWLEDGE_DIR` wrong or the image is missing `data/knowledge`.
- MCP tools missing from the trace: check `MCP_TRANSPORT`; for `http`, `kubectl -n angular-full exec deploy/backend -- python -c "import urllib.request;print(urllib.request.urlopen('http://mcp-server:8001/mcp').status)"` (a 4xx still proves reachability).
- Stream stalls then dumps everything at once: a proxy is buffering. nginx (`proxy_buffering off`) and Ingress annotations are set; check anything else in the path.
- "database is locked": two backend pods share the sqlite PVC. Keep `replicas: 1` or move to Postgres.
