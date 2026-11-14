# Deploy: 3.claude-sdk-full

Same shape as `../../2.angular-full/docs/DEPLOY.md`; differences are called out.

## 1. Local, no Docker

```bash
cd backend && cp .env.example .env && uv sync          # set ANTHROPIC_API_KEY
uv run uvicorn app.main:app --reload --port 8000        # the SDK spawns the bundled Claude CLI per request

cd ../frontend && npm install && npm start              # http://localhost:4200
```

Useful while developing:

```bash
curl 'localhost:8000/api/v1/debug/rag/search?q=express%20shipping'
curl -N localhost:8000/api/v1/chat/stream -H 'content-type: application/json' -d '{"message":"what is 12*7?"}'
uv run python -m app.mcp.server --http                  # standalone support MCP server on :8001, then MCP_TRANSPORT=http
uv run python -m app.evals.run                          # eval suite, prints a table
```

No Node is required: `claude-agent-sdk` bundles the CLI binary. If you already have Claude Code installed, the SDK prefers its bundled copy anyway.

## 2. Local, Docker Compose

```bash
cp backend/.env.example backend/.env
docker compose -f deploy/docker-compose.yaml up --build
open http://localhost:4200
```

The `backend-data` volume holds the app DB and the agent's session transcripts (`WORKDIR`).

## 3. Build and push images

```bash
REG=ghcr.io/<you>; TAG=$(git rev-parse --short HEAD)
docker build -t $REG/claude-sdk-full-backend:$TAG backend
docker build -t $REG/claude-sdk-full-mcp:$TAG -f backend/Dockerfile.mcp backend
docker build -t $REG/claude-sdk-full-frontend:$TAG frontend
for i in backend mcp frontend; do docker push $REG/claude-sdk-full-$i:$TAG; done
```

## 4. Kubernetes

```bash
kubectl apply -f deploy/k8s/00-namespace.yaml
kubectl -n claude-sdk-full create secret generic backend-secrets --from-literal=ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
cd deploy/k8s
kustomize edit set image REGISTRY/claude-sdk-full-backend=$REG/claude-sdk-full-backend:$TAG \
                         REGISTRY/claude-sdk-full-mcp=$REG/claude-sdk-full-mcp:$TAG \
                         REGISTRY/claude-sdk-full-frontend=$REG/claude-sdk-full-frontend:$TAG
kubectl apply -k .
kubectl -n claude-sdk-full rollout status deploy/backend deploy/mcp-server deploy/frontend
```

Backend is `replicas: 1` with a PVC: the SDK's session transcripts live on disk under `WORKDIR`. To scale out, implement `claude_agent_sdk.SessionStore` against Postgres/Redis and pass it as `ClaudeAgentOptions.session_store`, then drop the PVC.

## 5. CI/CD

`.github/workflows/3-claude-sdk-full.yml`: backend lint+tests, frontend tests+build, three image builds. Evals are a commented-out scheduled job.

## Runbook

- `CLINotFoundError` at first chat: the bundled binary is missing or not executable in the image. `docker run --rm <backend> python -c "import claude_agent_sdk,os;print(os.listdir(os.path.dirname(claude_agent_sdk.__file__)+'/_bundled'))"`.
- Chat hangs then errors with a permission message: a tool isn't in `allowed_tools`. Compare the trace's tool name with `app/agents/orchestrator.py`.
- `EACCES` / cannot write transcript: `HOME` or `WORKDIR` not writable. Both are set in the Dockerfile; check the PVC mount.
- Cost creeping: every `session` event carries `cost_usd`; log it. Lower `EFFORT` or `MAX_TURNS` before switching models.
