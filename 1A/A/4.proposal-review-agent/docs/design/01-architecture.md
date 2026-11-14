# 01 · Architecture

## Sub-projects (each independently deployable)

| Dir | What | Runtime | Deploys to |
|---|---|---|---|
| `backend/` | Agent service: FastAPI + Google ADK agent + REST API + ingestion pipeline + ADK dev UI | Python 3.11, uv | Cloud Run service `backend` |
| `backend/` (job entrypoint) | Bulk ingestion: `python -m app.cli ingest gs://…` | same image, different command | Cloud Run job `ingest` |
| `frontend/` | Angular portal: chat, conversations, documents, rules | nginx serving static + proxying `/api` | Cloud Run service `frontend` (IAP) |
| `mcp-server/` | MCP facade over the backend REST API, so other agents (Claude Code, Gemini CLI, other ADK agents) can query the compliance KB | Python, MCP streamable-http or stdio | Cloud Run service `mcp-server` (IAM auth) |
| `infra/terraform/` | All GCP resources | Terraform | `terraform apply` |
| `deploy/` | Local docker-compose: Postgres+pgvector, MongoDB, backend, frontend, mcp-server | Docker | your laptop |

Rules:

- Sub-projects talk over HTTP only. The MCP server never touches a database.
- The ingest job reuses the backend image on purpose: one ingestion code path, two triggers (API upload and bulk job).

## Runtime components

```
                         ┌──────────────────────── Browser ───────────────────────┐
                         │  Angular portal (chat · conversations · docs · rules)  │
                         └───────────────┬────────────────────────────────────────┘
                                         │ HTTPS (IAP in GCP; X-User-Email header locally)
                          ┌──────────────▼──────────────┐
                          │ frontend (nginx)            │  /api/* ──proxy──┐
                          └─────────────────────────────┘                  │
 Claude Code / Gemini CLI ──MCP──▶ mcp-server ──REST + service token──┐    │
                                                                      ▼    ▼
┌───────────────────────────────────── backend (FastAPI) ──────────────────────────────────────┐
│  auth: DevHeaderAuth | IapAuth | ServiceTokenAuth  →  Identity(user_id, role)                 │
│                                                                                               │
│  /api/v1/chat[/stream] ─▶ ChatService ─▶ ADK Runner(App: compliance_agent + plugins)          │
│  /dev-ui (ADK web, optional) ────────────▶ same App, same session/memory/artifact services    │
│                                                                                               │
│  compliance_agent (LlmAgent, Gemini on Vertex)                                                │
│    tools (all):   list_rules · search_rules · get_rule · list_documents · get_document_summary │
│                   search_documents · assess_proposal · preload_memory                          │
│    tools (admin): add_rule · update_rule · retire_rule · ingest_attachment                     │
│                   propose_rules_from_attachment · propose_rules_from_document                  │
│    callbacks:     before_agent → resolve role · before_tool → deny admin tools · after_agent → │
│                   save session to memory                                                       │
│                                                                                               │
│  services: AssessmentService · IngestionService · RuleService · ChatService · SqlMemoryService │
│                                                                                               │
│  /api/v1/rules · /documents · /assess · /conversations · /assessments · /me                   │
└───────┬────────────────────┬────────────────────┬────────────────────┬────────────────────────┘
        │                    │                    │                    │
  Postgres (Cloud SQL)   MongoDB API          Object store         Vertex AI
  rules, rule_versions,  (Firestore Mongo-    (GCS / local dir)    Gemini (chat, assess,
  assessments, chunks    compat / local       raw files, text,     summarize, extract)
  + pgvector, ADK        mongo): document     ADK artifacts        gemini-embedding-001
  sessions, memories     records
```

## Key flows

### A. "Can I launch a product that…?" (user)

1. Portal `POST /api/v1/chat/stream` with message.
2. Backend authenticates → `Identity(user_id="alice@acme.com", role="user")`.
3. ChatService runs the ADK Runner with `user_id=alice@acme.com`.
4. `before_agent_callback` sets `user:role` in session state from the server-side admin list.
5. `PreloadMemoryTool` injects relevant memories from Alice's past chats.
6. Model calls `assess_proposal(proposal=…)`.
7. AssessmentService:
   1. retrieves candidate rules (all active rules if few, else vector top-K)
   2. retrieves document passages as evidence
   3. asks Gemini for a finding per rule (structured JSON)
   4. **aggregates the verdict in code** (hard violated ⇒ `NON_COMPLIANT`)
   5. persists the assessment row
8. Tool result streams as a `verdict` event → portal renders a verdict card with citations.
9. Model explains the verdict in prose.
10. `after_agent_callback` adds the session's new events to long-term memory.

### B. Admin uploads a document (portal)

1. `POST /api/v1/documents` (multipart) → `require_admin`.
2. IngestionService: store raw file (GCS) → parse by format → store extracted text (GCS) → chunk → embed → upsert chunks (pgvector) → summarize (Gemini) → save document record (Mongo).
3. Optional `extract_rules=true` → returns proposed rules; admin reviews in the portal → `POST /api/v1/rules/bulk`.

### C. Admin uploads in chat

1. Portal sends the file inline with the message (or drag-and-drop in ADK dev UI).
2. ADK's `SaveFilesAsArtifactsPlugin` saves it as a session artifact and replaces it with a placeholder.
3. Model calls `ingest_attachment(filename)` → same IngestionService.
4. "Extract the rules from it" → `propose_rules_from_attachment` → model shows proposals → admin says "add 1, 3, 4" → `add_rule` × 3.
5. Non-admins never see these tools (role-gated toolset) and are denied if they try (callback).

### D. Bulk load "tons of documents"

1. `gsutil cp -r ./policies gs://BUCKET/inbox/`
2. `gcloud run jobs execute ingest` → `python -m app.cli ingest gs://BUCKET/inbox`
3. Idempotent: documents are keyed by content hash; re-running skips unchanged files.

## Why this shape

- **ADK owns the agent loop, sessions, memory, artifacts.** We own storage, retrieval, and the verdict logic.
- **The assessment is a tool, not the whole agent.** The model decides *when* to assess and how to explain; the pipeline decides *what* the verdict is. That split is what makes "hard rules" actually hard.
- **One composition root** (`app/container.py`) builds every adapter from settings. ADK's web server and our API get the *same* service instances via custom URI schemes registered with ADK's service registry.
