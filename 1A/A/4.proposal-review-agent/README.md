# 4.proposal-review-agent

A compliance **proposal review agent**. Employees ask "can I do X?" and get a verdict grounded in the company's rules and policy documents. Admins maintain the rules and documents from a portal or by chatting with the agent.

Built on **Google ADK** with **Gemini on Vertex AI**. Deploys to **GCP** (Cloud Run, Cloud SQL + pgvector, Firestore with MongoDB compatibility, GCS). Runs fully locally with one API key.

> Design first: read [`docs/design/`](docs/design/00-overview.md). Deploy: [`docs/DEPLOY.md`](docs/DEPLOY.md).

## What it does

- **Verdicts, not vibes.** `COMPLIANT`, `CONDITIONALLY_COMPLIANT`, `NON_COMPLIANT`, or `NEEDS_MORE_INFO`, with per-rule findings, quoted evidence, and conditions.
- **Hard rules are hard in code.** The model assesses each rule; a deterministic function turns findings into the verdict. A violated hard rule is always `NON_COMPLIANT`.
- **Flexible rules carry conditions.** Each lists the remediation and who can approve an exception.
- **Knowledge base from many formats.** PDF, DOCX, Markdown, HTML, TXT documents; CSV/JSON rule tables; rule extraction from prose with admin approval.
- **Roles.** Admins add, edit, and retire rules and ingest documents, including from chat with attachments. Users read, search, get summaries, and ask.
- **Memory.** Every conversation is kept per user and can be reopened. The agent also recalls relevant facts from earlier conversations.
- **Two UIs.** The Angular portal for everyone, and ADK's own dev UI mounted in the same backend for developers.
- **MCP.** Claude Code, Gemini CLI, or other agents can query the knowledge base and check proposals.

## Sub-projects

| Dir | What | Deploys as |
|---|---|---|
| [`backend/`](backend) | FastAPI + ADK agent, REST API, ingestion/RAG, storage adapters, ADK dev UI | Cloud Run service `backend` + Cloud Run job `ingest` |
| [`frontend/`](frontend) | Angular portal: chat with history and verdict cards, documents, rules | Cloud Run service `frontend` behind IAP |
| [`mcp-server/`](mcp-server) | MCP facade over the backend REST API (read-only) | Cloud Run service `mcp-server` (IAM auth) |
| [`infra/terraform/`](infra/terraform) | All GCP resources | `terraform apply` |
| [`deploy/`](deploy) | docker-compose for the full local stack | your laptop |

## Storage (polyglot, each behind a protocol)

| Data | Local lite | Local compose | GCP |
|---|---|---|---|
| Rules, versions, assessments, sessions, memories | SQLite | Postgres | Cloud SQL Postgres |
| Vectors (chunks + rules) | SQL brute force | pgvector | pgvector on Cloud SQL |
| Document records | JSON file | MongoDB | Firestore (MongoDB compatibility) |
| Files, chat attachments | local dir | volume | GCS |
| Model + embeddings | Gemini API key | Gemini API key | Vertex AI (service account) |

## Quickstart

```bash
cp backend/.env.example backend/.env                   # paste your GOOGLE_API_KEY
docker compose -f deploy/docker-compose.yaml up --build -d
docker compose -f deploy/docker-compose.yaml exec backend python -m app.cli seed
open http://localhost:4200                             # portal; switch identity to admin@example.com
open http://localhost:8000/dev-ui/                     # ADK dev UI
```

No Docker? See [`docs/DEPLOY.md` §1](docs/DEPLOY.md). It uses the same code with SQLite and files.

Try:

- "Can we launch a mobile game for 10-year-olds that collects email addresses at sign-up?" (hard rule, `NON_COMPLIANT`)
- "Can we run an ad saying we're twice as fast as Acme Backup?" (flexible rule, conditions)
- As admin: attach a PDF and say "ingest this, then extract the rules from it"

## Tests

```bash
cd backend && uv sync && uv run pytest -q          # no API key; real ADK loop via a scripted model
TEST_PG_URL=postgresql+asyncpg://... TEST_MONGO_URL=mongodb://... uv run pytest -q   # + real stores
cd mcp-server && uv sync && uv run pytest -q
cd frontend && npm test
```

## Layout (backend)

```
app/
  main.py                 app factory: ADK get_fast_api_app (dev UI) + our /api/v1 routers
  container.py            composition root: settings -> every adapter; shares services with ADK
  config.py               all settings
  adk_apps/compliance_agent/agent.py   ADK entry point (`app` = ADK App with plugins)
  agents/                 builder, tools, RoleGatedToolset, callbacks, prompts
  domain/                 rules/documents models; verdicts.py (validate + aggregate)
  services/               assessment, ingestion, rules, rule_extraction, chat, memory
  rag/                    parsers (md/txt/html/pdf/docx), chunker, embedder, vector_store, retriever
  storage/                sql (schema), rules_repo, assessments_repo, documents_repo, blobs
  auth/identity.py        dev header / IAP JWT / service token -> Identity(role)
  api/                    routes: rules, documents, chat, conversations, assess, search, me
  cli.py                  seed | ingest <dir|gs://> | import-rules | reindex
  evals/run.py            golden verdict suite
data/samples/             seed rules (json, csv) + policy documents (md, html, txt, pdf, docx)
evals/verdicts.json       golden proposals with expected verdicts
```

## References

1. [google/adk-python](https://github.com/google/adk-python), [google/adk-samples](https://github.com/google/adk-samples)
2. ADK docs: [Sessions & Memory](https://google.github.io/adk-docs/sessions/), [Artifacts](https://google.github.io/adk-docs/artifacts/), [Callbacks](https://google.github.io/adk-docs/callbacks/), [Deploy to Cloud Run](https://google.github.io/adk-docs/deploy/cloud-run/)
3. [pgvector](https://github.com/pgvector/pgvector) and [Cloud SQL pgvector](https://cloud.google.com/sql/docs/postgres/generative-ai/work-with-embeddings), [Firestore with MongoDB compatibility](https://cloud.google.com/firestore/mongodb-compatibility/docs/overview)
4. [Cloud Run IAP](https://cloud.google.com/run/docs/securing/identity-aware-proxy-cloud-run), [Direct VPC egress](https://cloud.google.com/run/docs/configuring/vpc-direct-vpc)
