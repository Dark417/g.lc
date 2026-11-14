# 00 · Overview

## Problem

- A company has a large, growing body of compliance material:
  - policy documents in mixed formats (PDF, DOCX, Markdown, HTML, TXT)
  - explicit rules written by people (some **hard**, some **flexible**)
- Employees constantly ask "can I do X?" before launching a product, running a campaign, or changing a process.
- Today the answer takes days, depends on who you ask, and rarely cites the rule it rests on.

## What we build

- A **proposal review agent** that answers "can I do X?" with:
  - a verdict: `COMPLIANT`, `CONDITIONALLY_COMPLIANT`, `NON_COMPLIANT`, `NEEDS_MORE_INFO`
  - per-rule findings with reasoning
  - evidence quotes from rules and documents
  - conditions or remediations for flexible rules
- A **knowledge base** of rules and documents that admins maintain:
  - through a web portal (upload, create, edit, retire)
  - or by chatting with the agent ("add a rule that…", "ingest this PDF", "extract rules from this doc")
- **Memory**:
  - every user sees their own past conversations and can continue them
  - the agent recalls relevant facts from a user's earlier conversations

## Users

| Role | Can do |
|---|---|
| `user` | Chat, ask "can I…?", list rules and documents, read document summaries, see own conversations and assessments |
| `admin` | Everything a user can, plus add/edit/retire rules, upload documents, extract rules from documents, via portal or chat |
| `service` | Machine callers (the MCP server). Read-only, same as `user` |

## Success metrics

- **Verdict accuracy**: ≥ 90% agreement with a golden set of reviewed proposals (`backend/evals/verdicts.json`).
- **Hard-rule safety**: 0 cases where a hard-rule violation produces anything other than `NON_COMPLIANT`.
  - Enforced in code, not by the model (see `03-agent-and-verdicts.md`).
- **Grounding**: every finding cites a rule code; ≥ 80% of findings carry at least one evidence quote.
- **Time to answer**: p50 < 15 s for a chat assessment.
- **Local-first**: `docker compose up` + one API key + upload docs → working system in < 10 minutes.

## Non-goals

- Legal advice. The agent is decision support; the verdict says so.
- Multi-tenant SaaS (one company per deployment).
- Fine-grained per-document ACLs (all authenticated users can read all documents).
- A workflow engine for exception approvals (we surface who approves; we don't route tickets).
- OCR for scanned PDFs (noted as a production swap: Document AI).

## Build vs buy

| Option | Verdict | Why |
|---|---|---|
| Vertex AI Search / RAG Engine as the whole retrieval layer | **Not now**, swap-ready | Great ingestion at scale, but we need rule-level structure (hard vs flexible, versions, codes) and exact citations. Our `VectorStore` protocol lets us swap later. |
| Vertex AI Agent Engine for hosting | **Not now** | Cloud Run gives us one deploy model for backend, frontend, MCP server, and the ingest job. Agent Engine is a good option once we only host the agent. |
| Vertex AI Memory Bank | **Production option** | Selected via `MEMORY_BACKEND=vertex`. Default is our SQL memory service so local works offline. |
| Document AI for parsing | **Production option** | Needed for scanned PDFs and complex tables. Local parsers handle text PDFs, DOCX, HTML, MD, TXT. |
| Build our own assessment pipeline | **Build** | This is the product. Deterministic hard-rule aggregation is the core differentiator. |

## Challenge to the brief (read this)

- **"Store in different DBs (RDS, DocumentDB, NoSQL)."**
  - Polyglot persistence has a real cost: two backups, two consistency stories, two sets of credentials.
  - Postgres alone (tables + JSONB + pgvector) could hold everything here.
  - We implement polyglot because it was asked and because each store fits its data. Rules are relational and versioned. Documents are heterogeneous metadata. Files are blobs.
  - Each store sits behind a protocol, so collapsing to Postgres later is a config change plus one adapter.
- **"Use the ADK UI."**
  - ADK's web UI is a **developer** UI. It has no auth and lets you pick any user id.
  - We mount it at `/dev-ui` for local use and admins-only debugging. It is **off** in production by default.
  - The product UI is the Angular portal, which talks to the same sessions, so conversations started in either show up in both locally.

## Documents in this folder

| File | Covers |
|---|---|
| `01-architecture.md` | Sub-projects, runtime components, request flows |
| `02-data-model.md` | What lives in which store, schemas |
| `03-agent-and-verdicts.md` | Agent, tools, role gating, assessment pipeline, verdict rules |
| `04-ingestion-and-rag.md` | Parsing, chunking, embeddings, retrieval, summaries, rule extraction |
| `05-memory-and-conversations.md` | Sessions, conversation history, long-term memory |
| `06-security.md` | AuthN, AuthZ, prompt injection, audit |
| `07-gcp-deployment.md` | Cloud Run, Cloud SQL, Firestore, GCS, Vertex, IAP, Terraform |
| `08-evals.md` | Golden verdict set, what we measure |
| `09-mvp-ladder.md` | Build order and why |
