# Deploy

## Options at a glance

| Target | What runs there | When |
|---|---|---|
| Docker Compose | backend + OTel collector + Jaeger | local demo with traces |
| Kubernetes (`deploy/k8s`) | backend (1 replica) | any cluster (EKS, GKE, kind) |
| Cloud Run | backend | GCP, simplest managed hosting of the whole service |
| AgentCore Runtime | backend via `app/runtimes/agentcore_app.py` | AWS, managed per-session isolation for all four frameworks |
| Vertex AI Agent Engine | the ADK `single` agent via `AdkApp` | GCP, managed ADK hosting (one agent, not the API) |

## 1. Image

```bash
docker build -t ai-sdk-backend:latest 5.ai-sdk/backend
```

- The image bundles:
  - Chromium, for the `browse` tool;
  - the Claude Code CLI, which ships inside the `claude-agent-sdk` wheel.
- Node.js is not included, so the Playwright MCP server (`npx @playwright/mcp`) is off.
  - To enable it, add Node to the image and set `PLAYWRIGHT_MCP_ENABLED=true`.

## 2. Docker Compose

```bash
cp 5.ai-sdk/backend/.env.example 5.ai-sdk/backend/.env    # add keys
docker compose -f 5.ai-sdk/deploy/docker-compose.yaml up --build
```

- Playground: <http://localhost:8000>.
- Jaeger: <http://localhost:16686>. Search service `ai-sdk-backend`, plus `ai-sdk-backend-claude-cli` for Claude Agent SDK runs.

## 3. Kubernetes

```bash
kubectl apply -f 5.ai-sdk/deploy/k8s/namespace.yaml
cp 5.ai-sdk/deploy/k8s/secret.example.yaml 5.ai-sdk/deploy/k8s/secret.yaml   # git-ignored; fill in
kubectl apply -f 5.ai-sdk/deploy/k8s/
```

- **One replica**, on purpose:
  - the session lock, the SQLite stores, and the Claude CLI's session files are process-local;
  - scaling out needs the PRODUCTION swaps in `docs/design/04-tools-mcp-rag-state.md`.
- Cloud credentials: bind the `backend` ServiceAccount to an IAM role (EKS IRSA / Pod Identity) or a GCP service account (GKE Workload Identity). Don't use static keys.
- Point `OTEL_EXPORTER_OTLP_ENDPOINT` at your collector.

## 4. AWS: AgentCore Runtime

- See `infra/aws/README.md`, section 5.
- The runtime calls `POST /invocations` with a `RunRequest` JSON. `provider` defaults to `bedrock`.

## 5. GCP: Cloud Run or Agent Engine

- See `infra/gcp/README.md`, section 3.

## 6. CI

- `.github/workflows/5-ai-sdk.yml`:
  - ruff;
  - keyless pytest, including real Chromium;
  - image build;
  - compose validation.
- Deploy steps depend on your registry and cluster. Add them after the `image` job.
- Real-model evals are a commented, scheduled job (cost and nondeterminism keep them out of PRs).
