# 02 · Data model (polyglot persistence)

## What goes where

| Data | Shape | Store (local) | Store (GCP) | Why this store |
|---|---|---|---|---|
| Rules, rule versions | Relational, versioned, filtered by severity/category/status | Postgres (compose) or SQLite (lite) | **Cloud SQL Postgres** ("RDS") | Constraints, unique codes, audit history, joins |
| Assessments (every verdict) | Relational + JSON findings | same | Cloud SQL | Audit trail, per-user history, analytics |
| Chunks + embeddings | Vector rows | Postgres + **pgvector** / SQLite brute force | Cloud SQL + pgvector | Co-located with rules; HNSW index; one less service |
| ADK sessions (conversations) | ADK-managed tables | same | Cloud SQL | `DatabaseSessionService`, list per user |
| Long-term memories | Rows + embedding | same | Cloud SQL, or **Vertex AI Memory Bank** | Keyword/vector recall per user |
| Document records | Heterogeneous metadata, summaries, outlines | **MongoDB** (compose) or JSON file (lite) | **Firestore with MongoDB compatibility** ("DocumentDB") | Schema varies per format; document-shaped |
| Raw files, extracted text | Blobs | local dir | **GCS** | Cheap, large, immutable |
| Chat attachments | ADK artifacts | local dir (`FileArtifactService`) | GCS (`GcsArtifactService`) | ADK-native |

Selection is by env var, resolved once in `app/container.py`:

```
DATABASE_URL   = sqlite+aiosqlite:///… | postgresql+asyncpg://…
VECTOR_STORE   = sql | pgvector | vertex(dummy)
DOC_STORE      = file | mongo
BLOB_STORE     = local | gcs
EMBEDDER       = hashing | gemini
MEMORY_BACKEND = sql | vertex
```

## Relational schema (Postgres)

```sql
rules (
  id               uuid pk,
  code             text unique not null,      -- e.g. PRIV-003, human-readable, cited in verdicts
  title            text not null,
  statement        text not null,             -- the rule itself
  severity         text not null check (severity in ('hard','flexible')),
  category         text not null,             -- privacy, marketing, product-launch, security, finance…
  rationale        text,
  exception_process text,                     -- flexible rules: who can approve a deviation
  source_document_id text,                    -- Mongo document id, if extracted from a doc
  source_ref       text,                      -- section / page
  status           text not null default 'active' check (status in ('draft','active','retired')),
  version          int  not null default 1,
  created_by       text not null,
  created_at       timestamptz, updated_at timestamptz
)

rule_versions (                               -- append-only audit: every change snapshots the row
  id uuid pk, rule_code text, version int, snapshot jsonb, changed_by text, change_note text, changed_at timestamptz
)

assessments (
  id uuid pk, user_id text, session_id text,
  proposal text, verdict text, summary text,
  findings jsonb,                             -- [{rule_code, severity, status, reasoning, evidence[], remediation}]
  rule_versions jsonb,                        -- {code: version} used, so old verdicts are reproducible
  model text, created_at timestamptz
)

chunk_embeddings (                            -- pgvector store
  id text pk,                                 -- "{kind}:{ref_id}:{n}"
  kind text,                                  -- 'doc' | 'rule'
  ref_id text,                                -- document id or rule code
  text text, metadata jsonb,
  embedding vector(768)
)  + HNSW index (vector_cosine_ops)

memories (
  id text pk (event id), app_name text, user_id text, session_id text,
  author text, text text, embedding jsonb, created_at timestamptz
)
-- ADK's DatabaseSessionService creates its own tables (sessions, events, app_states, user_states).
```

Notes:

- `code` is the human key. Verdicts cite codes, not uuids.
- A rule edit bumps `version` and writes a `rule_versions` row in the same transaction.
- Retiring sets `status='retired'` and removes its embedding; history stays.
- Schema is created with `metadata.create_all` at startup. **PRODUCTION**: Alembic migrations.

## Document record (Mongo / Firestore)

```json
{
  "_id": "doc_7f3a…",
  "title": "Data Privacy Standard",
  "filename": "data-privacy-standard.html",
  "format": "html",                      // pdf | docx | md | html | txt | csv | json
  "mime_type": "text/html",
  "size_bytes": 18233,
  "sha256": "…",                         // idempotency key for bulk ingest
  "category": "privacy",
  "tags": ["gdpr", "retention"],
  "status": "ready",                     // pending | processing | ready | failed
  "error": null,
  "summary": "Defines how personal data…",
  "key_points": ["…", "…"],
  "outline": ["1. Scope", "2. Lawful basis", "…"],
  "page_count": null,
  "chunk_count": 14,
  "blob_uri": "gs://bucket/documents/doc_7f3a/data-privacy-standard.html",
  "text_uri": "gs://bucket/documents/doc_7f3a/extracted.txt",
  "extracted_rule_codes": ["PRIV-001", "PRIV-002"],
  "uploaded_by": "admin@acme.com",
  "created_at": "…", "updated_at": "…"
}
```

- Full text is **not** stored in the record (Firestore 1 MiB document limit). It lives at `text_uri`.
- Format-specific fields (e.g. `page_count` for PDF) are simply present or absent. That is the reason for a document store.

## Blob layout (GCS / local)

```
documents/{doc_id}/{original filename}
documents/{doc_id}/extracted.txt
inbox/…                                   # bulk-ingest drop zone
artifacts/…                               # ADK GcsArtifactService (chat attachments)
```

## Consistency

- Ingestion order: blob → chunks → record(status=ready). A crash leaves a `processing` record with no `ready`; the next run retries it by `sha256`.
- Deleting a document: record → chunks → blobs. Rules extracted from it keep `source_document_id` (dangling is acceptable; the rule stands on its own).
- No cross-store transactions. Every step is idempotent instead.
