# Deploy: 4.proposal-review-agent

Three ways to run it, same code, different env vars.

| Mode | Stores | Needs |
|---|---|---|
| **Lite** (no Docker) | SQLite + JSON file + local dir | Python 3.11, uv, Node 22, a Gemini API key |
| **Compose** (local, real polyglot) | Postgres + pgvector, MongoDB, local volume | Docker, a Gemini API key |
| **GCP** | Cloud SQL + pgvector, Firestore (Mongo-compat), GCS, Vertex AI | a GCP project, Terraform, gcloud |

---

## 1. Lite: no Docker

```bash
cd backend
cp .env.example .env              # set GOOGLE_API_KEY (or the Vertex block)
uv sync
uv run python -m app.cli seed     # 17 sample rules + 5 sample documents (md, html, txt, pdf, docx)
uv run uvicorn app.main:app --reload --port 8000

cd ../frontend
npm install -g npm@11 && npm install   # npm 10.9 crashes on jsdom's optional canvas peer
npm start                               # http://localhost:4200
```

- Portal: http://localhost:4200. Use the header box to switch identity. `admin@example.com` is an admin.
- ADK dev UI: http://localhost:8000/dev-ui/. It always uses `user_id="user"`, which `.env.example` lists in `ADMIN_USERS`, so the dev UI is an admin session.
- API docs: http://localhost:8000/docs.
- Your own documents: `uv run python -m app.cli ingest /path/to/folder` or upload in the portal as an admin.

## 2. Compose: full local stack

```bash
cp backend/.env.example backend/.env                       # GOOGLE_API_KEY
docker compose -f deploy/docker-compose.yaml up --build -d
docker compose -f deploy/docker-compose.yaml exec backend python -m app.cli seed
```

| URL | What |
|---|---|
| http://localhost:4200 | Portal (nginx proxies `/api` to the backend) |
| http://localhost:8000/dev-ui/ | ADK dev UI |
| http://localhost:8001/mcp | MCP server (streamable-http) |

Compose overrides the lite storage settings: `DATABASE_URL` points at Postgres, `VECTOR_STORE=pgvector`, `DOC_STORE=mongo`.

### MCP client config (Claude Code / Claude Desktop)

```bash
claude mcp add --transport http compliance http://localhost:8001/mcp
```

Or stdio, without Docker:

```json
{ "mcpServers": { "compliance": {
    "command": "uv", "args": ["--directory", "/abs/path/mcp-server", "run", "python", "-m", "app.server"],
    "env": { "BACKEND_URL": "http://localhost:8000", "SERVICE_TOKEN": "local-mcp-token" } } } }
```

## 3. Evals (needs a model)

```bash
cd backend
uv run python -m app.cli seed
uv run python -m app.evals.run               # pipeline only
uv run python -m app.evals.run --via-agent   # through the full agent loop
```

Pass bar: accuracy ≥ 0.9, zero safety failures, citation recall ≥ 0.8. See `docs/design/08-evals.md`.

---

## 4. GCP

Terraform applies in **two phases**. Cloud Run needs images in Artifact Registry and the Firestore Mongo connection string, and both only exist after phase 1.

### 4.1 Prerequisites

```bash
gcloud auth login && gcloud auth application-default login
export PROJECT=your-project REGION=us-central1
gcloud config set project $PROJECT
cd infra/terraform && cp terraform.tfvars.example terraform.tfvars   # edit project_id, admin_emails
terraform init
```

### 4.2 Phase 1: foundation

```bash
terraform apply            # deploy_services = false
```

This creates the APIs, Artifact Registry, VPC, bucket, Cloud SQL Postgres 16, Firestore (Enterprise edition, Mongo-compatible), secrets, service accounts, and IAP access.

### 4.3 Firestore MongoDB credentials

Firestore's MongoDB-compatible API authenticates with per-database user credentials:

```bash
DB=$(terraform output -raw firestore_database)
gcloud firestore user-creds create backend --database=$DB      # prints a password once
```

Copy the connection string from **Console → Firestore → $DB → Connect using MongoDB driver**. Put the user and password into it. It looks like:

```
mongodb://backend:PASSWORD@UID.LOCATION.firestore.goog:443/DB?loadBalanced=true&tls=true&authMechanism=SCRAM-SHA-256&retryWrites=false
```

Set it as `mongo_url` in `terraform.tfvars` (the file is gitignored), or pass it with `-var`. The alternative is MongoDB Atlas on GCP: same variable, Atlas URL.

### 4.4 Build and push images (no deploy yet)

```bash
cd ../..    # project root
gcloud builds submit --config cloudbuild.yaml --substitutions _DEPLOY=false,_TAG=latest .
```

### 4.5 Phase 2: services

```bash
cd infra/terraform
terraform apply -var deploy_services=true
terraform output frontend_url     # open it; IAP asks you to sign in with Google
```

### 4.6 Load documents

```bash
BUCKET=$(terraform output -raw bucket)
gsutil -m cp -r /path/to/policies gs://$BUCKET/inbox/
gcloud run jobs execute ingest --region $REGION --wait
```

Re-running is safe: files are keyed by content hash. `inbox/` objects expire after 30 days, and ingested originals are kept under `documents/`.

To load the sample rules and documents instead, upload `backend/data/samples/**` into `inbox/`.

### 4.7 Checks

- **IAP audience.** Open IAP console → Cloud Run → `frontend` → "Get JWT audience code". If it differs from the backend's `IAP_AUDIENCE` env var, set `IAP_AUDIENCE` in `services.tf` to the value shown.
- **Org policy `iam.allowedPolicyMemberDomains`.** It blocks `allUsers` on the backend invoker binding. The backend is internal-only either way. Alternative: have nginx attach an ID token, which means a small sidecar or moving to a load balancer.
- **Gemini on Vertex.** Confirm `MODEL` is available in `vertex_location`.

### 4.8 MCP server on Cloud Run

```bash
gcloud run services proxy mcp-server --region $REGION --port 8001   # handles the ID token for you
claude mcp add --transport http compliance http://localhost:8001/mcp
```

Callers must be in `mcp_invokers`.

---

## 5. Day-2 operations

| Task | Command |
|---|---|
| Ship a new version | `gcloud builds submit --config cloudbuild.yaml --substitutions _TAG=$(git rev-parse --short HEAD) .` |
| Change infra | edit `infra/terraform`, `terraform apply -var deploy_services=true` |
| Re-embed after changing `EMBEDDER` / `EMBEDDING_DIM` | run the job with `--args=-m,app.cli,reindex` (drop `chunk_embeddings` first if the dimension changed) |
| Give someone access | add to `user_emails` / `admin_emails`, `terraform apply` |
| Logs | `gcloud run services logs read backend --region $REGION` |

## 6. CI/CD (GitHub Actions)

`.github/workflows/4-proposal-review-agent.yml` runs on every PR:

- backend tests against real Postgres + pgvector and MongoDB service containers
- MCP server tests, frontend tests and build
- `terraform fmt -check` + `validate`
- all three image builds

To enable deploy on `main`, set these repository **variables** (not secrets):

- `GCP_PROJECT_ID`, `GCP_REGION`
- `GCP_WIF_PROVIDER`: the Workload Identity Federation provider resource name
- `GCP_DEPLOY_SA`: needs `roles/cloudbuild.builds.editor`, `roles/run.developer`, `roles/iam.serviceAccountUser`, `roles/artifactregistry.writer`

Setup guide: https://github.com/google-github-actions/auth#workload-identity-federation-through-a-service-account

## 7. Troubleshooting

| Symptom | Likely cause |
|---|---|
| Chat shows "No API key was provided" | `GOOGLE_API_KEY` unset (lite/compose) or Vertex env missing |
| `/api/v1/assess` returns 502 | Model call failed; the detail says why (quota, permissions, model name) |
| Summaries empty after upload | Model unavailable at ingest. Delete and re-upload, or run `reindex` |
| Portal 502 on `/api` in GCP | Frontend can't reach the internal backend. Check `vpc_access.egress = ALL_TRAFFIC` and Private Google Access |
| 401 in GCP | IAP JWT audience mismatch (4.7) |
| `extension "vector" is not available` | Postgres without pgvector. Use the `pgvector/pgvector` image; Cloud SQL has it built in |
| Mongo `retryWrites` error on Firestore | Connection string needs `retryWrites=false` |
