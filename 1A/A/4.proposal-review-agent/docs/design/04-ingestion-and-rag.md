# 04 · Ingestion and RAG

## Pipeline

```
bytes + filename
  ─▶ sha256 (idempotency: same hash ⇒ return existing record)
  ─▶ blob store: documents/{id}/{filename}
  ─▶ parse (by extension / mime) ─▶ ParsedDocument{sections[{heading, text, page}]}
  ─▶ blob store: documents/{id}/extracted.txt
  ─▶ chunk (heading-aware, overlap) ─▶ embed ─▶ vector store (kind='doc', ref_id=doc id)
  ─▶ summarize (Gemini, structured: summary, key_points, category guess)
  ─▶ document record (status=ready, outline, chunk_count, summary)
```

- Triggered by: `POST /api/v1/documents`, the `ingest_attachment` chat tool, and `python -m app.cli ingest <dir|gs://prefix>`.
- One `IngestionService`, three entry points.

## Parsers (`app/rag/parsers.py`)

| Format | Parser | Sections from |
|---|---|---|
| `.md` | stdlib | `#` headings |
| `.txt` | stdlib | blank-line paragraphs; numbered/UPPERCASE lines as headings |
| `.html` / `.htm` | stdlib `html.parser` | `<h1>`–`<h4>`; drops `<script>`/`<style>` |
| `.pdf` | `pypdf` | one section per page (`page` set) |
| `.docx` | `python-docx` | `Heading N` paragraph styles |
| `.csv` / `.json` rules files | `rule_import.py` | Not documents: parsed as rule rows (see below) |

- **PRODUCTION**: Document AI Layout Parser for scanned PDFs, tables, and multi-column layouts. It plugs in as another parser keyed by format.
- Unknown formats fail fast with a clear error; the record gets `status=failed`.

## Chunking

- Section-aware: never merge text across top-level headings.
- ~1,200 characters per chunk, 150-character overlap.
- Each chunk's metadata carries `document_id`, `title`, `heading`, `page`, so citations read "Data Privacy Standard §2 Lawful basis".
- **PRODUCTION**: token-based sizing with the model tokenizer.

## Embeddings

| `EMBEDDER` | Class | Use |
|---|---|---|
| `hashing` | `HashingEmbedder` | ILLUSTRATION: offline, deterministic, tests and no-key runs. Lexical only. |
| `gemini` | `GeminiEmbedder` | `gemini-embedding-001` via `google-genai`. Works with an API key or Vertex AI. 768 dimensions. |

- Rules are embedded too (`kind='rule'`, text = code + title + statement) so `search_rules` and assessment retrieval work at scale.
- `EMBEDDING_DIM` must match the pgvector column. Changing embedders means re-indexing: `python -m app.cli reindex`.

## Vector stores

| `VECTOR_STORE` | Class | Notes |
|---|---|---|
| `sql` | `SqlVectorStore` | ILLUSTRATION: embeddings as JSON, brute-force cosine in Python. Works on SQLite and Postgres. |
| `pgvector` | `PgVectorStore` | PRODUCTION: `vector(768)` column + HNSW `vector_cosine_ops`. Cloud SQL supports the extension. |
| `vertex` | `VertexVectorSearchStore` | PRODUCTION alternative (dummy body): Vertex AI Vector Search for 10M+ chunks. |

## Retrieval

- `search_documents(query)`: embed query → top-k `kind='doc'` → passages with source labels.
- `search_rules(query)`: embed → top-k `kind='rule'` → join back to the rules table (only `active`).
- Assessment uses both (see `03-agent-and-verdicts.md`).
- **Next step if recall is weak**: hybrid search (Postgres full-text `tsvector` + vector, reciprocal rank fusion). Compliance text has exact terms ("DPIA", "COPPA") where keyword search wins.

## Summaries

- One Gemini call per document on the first ~30k characters: `summary`, `key_points[]`, `suggested_category`.
- Stored on the document record; `get_document_summary` returns them without touching the model again.

## Rules from documents

Two paths:

1. **Structured files** (`.csv`, `.json`): deterministic import. Columns: `code, title, statement, severity, category, rationale, exception_process`.
2. **Prose documents**: `propose_rules(text)` → Gemini with `response_schema=list[ProposedRule]`.
   - Returns proposals; never writes.
   - An admin approves (portal checkboxes or "add 1 and 3" in chat).
   - Proposed codes are suggestions; `RuleService` guarantees uniqueness (`PRIV-004` → `PRIV-005` if taken).

Why human-in-the-loop here: a wrongly extracted **hard** rule blocks real work. Extraction is cheap; review is the control.

## Scale notes ("tons of documents")

- The API ingests synchronously for files under `SYNC_INGEST_MAX_MB` (10 MB). Above that it returns `202` with a `processing` record and runs in a background task.
- Bulk loads use the Cloud Run job. It parallelises with `--concurrency`, and re-runs are idempotent by hash.
- **PRODUCTION**: GCS finalize event → Eventarc → Cloud Run job, so dropping a file into `inbox/` is the whole workflow.
