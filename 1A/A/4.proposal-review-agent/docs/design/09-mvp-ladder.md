# 09 · MVP ladder

Each rung is a vertical slice you can demo end to end. Build in this order.

| Rung | Demo | Adds | Why this order |
|---|---|---|---|
| **MVP0** | In ADK dev UI: "Can I email kids without parental consent?" → `NON_COMPLIANT`, cites `PRIV-003` | Rules table + seed JSON, `assess_proposal` with deterministic aggregation, agent with read tools | The verdict pipeline is the product and the riskiest part. Prove it first. |
| **MVP1** | Upload a PDF in the portal; its summary shows; verdicts quote it | Parsers, chunking, embeddings, vector store, document store, blob store, summaries, Documents page | Evidence quality is the next biggest driver of trust. |
| **MVP2** | Admin chats "add a rule…", drops a DOCX in chat, "extract rules" → approve → verdicts change | Roles, `RoleGatedToolset`, admin tools, chat attachments via artifacts, Rules page | Content management through chat is the second headline feature. It needs roles first. |
| **MVP3** | Close the tab, reopen: previous conversations listed; agent remembers "the EU launch" | `DatabaseSessionService`, conversation API + sidebar, `SqlMemoryService` + `PreloadMemoryTool` | Needs stable identities (MVP2) to scope history per user. |
| **MVP4** | Claude Code asks the KB via MCP; eval suite prints accuracy | MCP server sub-project, golden verdict set + runner | Integration and measurement once behaviour is stable. |
| **MVP5** | Same demo on a `*.run.app` URL behind Google login | Terraform, Cloud SQL + pgvector, Firestore Mongo-compat, GCS, Vertex, IAP, Cloud Build, CI deploy | Cloud last: every earlier rung runs locally with the same code and different env vars. |

## What each rung changes in code

- MVP0: `app/domain/verdicts.py`, `app/storage/rules_repo.py`, `app/services/assessment.py`, `app/agents/`
- MVP1: `app/rag/*`, `app/storage/{documents_repo,blobs}.py`, `app/services/ingestion.py`, `frontend/…/documents`
- MVP2: `app/auth/*`, `app/agents/{toolsets,callbacks}.py`, `app/services/rule_extraction.py`, `frontend/…/rules`
- MVP3: `app/services/{chat,memory}.py`, `frontend/…/chat` sidebar
- MVP4: `mcp-server/`, `backend/evals/`, `app/evals/`
- MVP5: `infra/terraform/`, `cloudbuild.yaml`, `.github/workflows/4-proposal-review-agent.yml`

## Explicitly deferred

- Hybrid (keyword + vector) retrieval: add when evals show recall misses on exact terms.
- Exception-approval workflow: surface the approver today; integrate a ticketing system later.
- Alembic migrations: `create_all` until the first schema change after launch.
- Per-document ACLs.
