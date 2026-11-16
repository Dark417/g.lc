# RAG Reference Handbook — Production & Interview Prep (L4/L5)

> Scope: RAG as a **retrieval tool inside an agent harness**, not a standalone chatbot pattern. Anchored to your stack: fastembed / bge-small, Delta Lake, LangGraph, Qdrant or pgvector. Opinionated; recommendations are called out.

---

## 0. The one-paragraph mental model

RAG = **build a search engine, then let the model read the top results before answering.** Every hard problem in RAG is a search-engine problem (chunking, indexing, ranking, freshness, evaluation), not an LLM problem. The model is the last 5%. Interviewers who've shipped RAG are testing whether you know that.

Two pipelines, two cadences:

```
OFFLINE / INGEST (batch or CDC, minutes–hours)         ONLINE / QUERY (per request, <1s)
──────────────────────────────────────────────         ──────────────────────────────────────
source docs ──► parse ──► chunk ──► embed ──► index    query ──► rewrite ──► hybrid search ──►
   │                                   │                      rerank ──► assemble context ──►
   └── change detection ───────────────┘                      generate (w/ citations) ──► eval log
```

Where it sits in your dependency tree: **retrieval is a tool** (node 3). An agent decides *whether* and *what* to retrieve; RAG is what happens when it does. Context engineering (node 5) decides *how much* of the retrieved material survives into the window.

---

## 1. Ingest pipeline — decisions that matter

### 1.1 Parse
Boring but where most quality is lost. PDFs → tables, headers, footers, multi-column. Options: `unstructured`, `docling` (IBM, best layout fidelity in 2025), `pymupdf4llm`, LlamaParse (hosted). For structured sources (Delta tables, DBs, APIs) skip parsing — you already have fields; treat each row/record as a document with metadata.

**Rule:** preserve structure as metadata (`section_title`, `page`, `source_uri`, `doc_version`). You will need it for filtering, citations, and deletion.

### 1.2 Chunk

| Strategy | How | Use when | Deciding tradeoff |
|---|---|---|---|
| Fixed-size w/ overlap | N tokens, 10–20% overlap | Default, unknown structure | Simple; splits mid-thought |
| Recursive character | Split on `\n\n` → `\n` → `.` → ` ` until under size | Prose | LangChain default; good enough 80% of the time |
| Structure-aware | Split by headings / markdown / HTML sections | Docs, wikis, filings | Best precision when structure exists |
| Semantic | Embed sentences, split at similarity drops | Long unstructured prose | Expensive at ingest; marginal gains |
| Parent-child (small-to-big) | Index small chunks, return the parent chunk/window | Almost always | Retrieval precision of small chunks + context of large ones. **Recommended.** |
| Late chunking / contextual retrieval | Prepend doc-level summary to each chunk before embedding (Anthropic's "contextual retrieval") | Chunks lose meaning without doc context (e.g., "the company" in a 10-K) | Extra LLM call per chunk at ingest; big retrieval gains (~35–50% fewer failures in Anthropic's writeup) |

**Sizes:** 256–512 tokens for retrieval unit; 1–2k for the returned parent. Tune with eval, not vibes.

**Recommendation:** structure-aware split → parent-child → contextual prefix for any corpus where chunks are ambiguous out of context (SEC filings absolutely qualify).

### 1.3 Embed

- **Model choice:** `bge-small-en-v1.5` (384d, fast, fine for English), `bge-m3` (multilingual + produces dense **and** sparse), `nomic-embed-text`, `text-embedding-3-small/large`, Cohere embed-v3/v4, Voyage. Check MTEB retrieval subset, not the overall leaderboard.
- **Asymmetric models** need query/doc prefixes (`query: ` / `passage: `). Forgetting this silently degrades recall — a classic interview gotcha.
- **Dims vs cost:** 384d vs 1536d is 4x storage and memory in HNSW. Matryoshka models (OpenAI v3, nomic) let you truncate dims.
- **Normalize** vectors and use cosine/dot; store which model + version produced the vector (`embed_model="bge-small-en-v1.5"`) — you'll need it for migrations (§5.4).

### 1.4 Index

| Index | Recall | Build | Memory | Use |
|---|---|---|---|---|
| Flat (brute force) | 100% | none | N×d | <100k vectors, or as ground truth for recall tests |
| HNSW | ~95–99% | slow-ish | high (graph + vectors) | Default everywhere. Tune `M`, `ef_construction`, `ef_search` |
| IVF(+PQ) | tunable | fast | low (compressed) | 10M+ vectors, cost-sensitive |
| DiskANN | high | slow | disk-resident | Billions, one box |

**Filtering interaction:** pre-filter (apply metadata filter, then ANN) vs post-filter (ANN top-k, then filter — can return <k). Qdrant/Weaviate do filtered HNSW natively; pgvector does post-filter unless you partition/partial-index. Ask about this in any vector DB choice.

---

## 2. Query pipeline

### 2.1 Query transformation (pick 0–2, eval each)
- **Rewrite / decontextualize:** turn "what about last year?" into a standalone query using chat history. Nearly always worth it in multi-turn.
- **Multi-query:** generate 3–5 paraphrases, union results. Cheap recall boost.
- **HyDE:** generate a hypothetical answer, embed *that*. Helps when queries are short and docs are long. Hurts on factual lookups where the model hallucinates the wrong entity.
- **Step-back / decomposition:** break a complex question into sub-questions. This is where agentic RAG starts (§7).
- **Metadata extraction:** "Apple 10-K 2023 risk factors" → `filters={ticker:"AAPL", form:"10-K", fy:2023, section:"1A"}` + semantic query. Self-query retriever pattern. For structured corpora this single step outperforms every embedding trick.

### 2.2 Hybrid search
Dense embeddings miss exact tokens (IDs, product codes, names, acronyms); BM25 misses paraphrase. Run both, fuse with **Reciprocal Rank Fusion**:

```
RRF(d) = Σ_r 1 / (k + rank_r(d)),   k = 60
```

Fuse *ranks*, not scores — scores aren't comparable across systems. Weighted variants exist; RRF is the boring default.

### 2.3 Rerank
Retrieve top-50 to top-100 with cheap bi-encoders, rerank to top-5 to top-10 with a **cross-encoder** (`bge-reranker-v2-m3`, Cohere Rerank, `mxbai-rerank`). Cross-encoders see query and doc together, so they're far more precise but O(k) forward passes — hence two-stage. This is the single highest-ROI addition to a naive pipeline.

### 2.4 Assemble context
- Dedupe by parent; collapse child hits into their parent window.
- Order: relevance-ordered is fine; for very long contexts put the most relevant at the beginning *and* end ("lost in the middle").
- Attach citation handles: `[doc_id:chunk_id]` so the model can cite and you can verify.
- Budget: fixed token budget for retrieved context; drop tail, don't truncate mid-chunk.

### 2.5 Generate
- System prompt: answer only from context; if not in context, say so; cite by handle.
- Post-check: every cited handle exists in the provided set (mechanical gate — your style). Optionally an NLI/LLM faithfulness check on high-stakes paths.

---

## 3. Frameworks

| Framework | What it actually is | Strength | Weakness | Verdict |
|---|---|---|---|---|
| **LangChain** (`langchain-core` + `langchain-community`) | Interfaces (`Embeddings`, `VectorStore`, `BaseRetriever`) + integrations | Ubiquitous, every DB has a loader/store; pairs with LangGraph | Abstractions leak; retrievers hide the query you actually ran | Use the **interfaces and integrations**, write your own pipeline logic |
| **LlamaIndex** | Data framework: ingestion pipeline, node parsers, indices, query engines | Best ingestion/chunking tooling; `IngestionPipeline` has built-in docstore-based dedup/upsert | Second framework to learn; agent story weaker than LangGraph | Steal its ingestion ideas; use if RAG *is* the product |
| **Haystack** (deepset) | Pipeline DAG of components | Clean, explicit, production-minded | Smaller ecosystem | Solid; rarely the JD keyword |
| **Vector DB native** (Qdrant, Weaviate, Databricks Vector Search) | DB does hybrid + rerank + sometimes embedding | Fewest moving parts | Lock-in | Great for the ingest+search layer |
| **DIY** (fastembed + client + ~200 lines) | You own everything | Transparent, testable, no magic | You write the plumbing | **Recommended for your profile** — it's what you'd want to own as a lead anyway |

**Recommendation for interviews:** say "LangChain interfaces for pluggability, LangGraph for orchestration, but the retrieval pipeline itself is explicit code I can eval and trace." That's the L5 answer — framework-fluent, not framework-dependent.

---

## 4. Vector databases

| DB | Model | Hybrid | Filtered ANN | Deletes/updates | Ops | Pick when |
|---|---|---|---|---|---|---|
| **pgvector** (+ `pg_search`/`pg_bm25`, or `tsvector`) | Postgres extension | Yes, via SQL | Post-filter (partial indexes help) | Native SQL, transactional | You already run Postgres | <5–10M vectors, you want one DB, ACID with your metadata. **Default.** |
| **Qdrant** | Rust, standalone/cloud | Native dense+sparse, RRF fusion | Native filtered HNSW (excellent) | Upsert by id, payload filters for delete | Simple binary/Docker | Standalone vector service, >10M, heavy filtering. **Default when pgvector isn't enough.** |
| **Weaviate** | Go, standalone/cloud | Native BM25+dense | Native | Upsert by uuid | Moderate | Multi-tenant, built-in vectorizers |
| **Milvus / Zilliz** | Distributed | Yes | Yes | Yes, with compaction | Heavy (etcd, MinIO, Pulsar) | Billions of vectors, real scale team |
| **Pinecone** | Managed | Sparse-dense | Namespaces + metadata | Upsert/delete by id | Zero | You want zero ops and accept cost/lock-in |
| **OpenSearch / Elasticsearch** | Search engine w/ kNN | Best-in-class BM25 + kNN | Yes | Yes | Heavy | You already run it; text-search-heavy |
| **Databricks Vector Search** | Managed, indexes a Delta table | Hybrid | Yes | **Delta Sync** — auto-syncs from source Delta table via CDF | Zero if on Databricks | **Your edgar-mcp corpus is already in Delta. Strongest story for you.** |
| **LanceDB / Chroma** | Embedded | Lance: yes; Chroma: dense | Basic | Yes | None | Local dev, notebooks, edge |

**Interview positioning:** "pgvector until it hurts; Qdrant when it does; Databricks Vector Search when the source of truth is already Delta. Never a distributed vector DB for a corpus that fits in one Postgres."

---

## 5. Dynamic content — the section interviewers actually probe

Naive RAG assumes a static corpus. Real corpora change constantly. Design for it from day one.

### 5.1 Identity and idempotency
Every chunk gets a deterministic id:

```
doc_id     = stable source key (URL, file path, table PK)
doc_hash   = sha256(canonical content)
chunk_id   = f"{doc_id}#{chunk_index}"      # position-based
chunk_hash = sha256(chunk_text)             # content-based
```

Store `doc_id`, `doc_hash`, `chunk_hash`, `embed_model`, `ingested_at`, `source_version` as payload/metadata. This makes every ingest run **idempotent** — rerunning is safe, which is what lets you build the rest.

### 5.2 Change detection → three cases
Maintain a **manifest** (`doc_id → doc_hash, chunk_ids[]`) in Postgres/Delta:

| Case | Detect | Action |
|---|---|---|
| New doc | `doc_id` not in manifest | chunk → embed → upsert all |
| Changed doc | `doc_hash` differs | diff chunk hashes: upsert changed/new chunks, **delete** orphaned chunk_ids |
| Deleted doc | in manifest, not in source | delete all its chunk_ids, remove from manifest |

Chunk-level hashing means editing one paragraph re-embeds one chunk, not the whole doc. This is what LlamaIndex's `IngestionPipeline(docstore=...)` does under the hood.

### 5.3 Getting the changes
- **Batch diff:** full scan, compare hashes. Fine for <100k docs nightly.
- **CDC:** Delta Lake **Change Data Feed** (`readChangeFeed`, `_change_type ∈ {insert, update_postimage, delete}`), Postgres logical replication/Debezium, S3 event notifications. Stream changes → embed → upsert. This is what Databricks Delta Sync automates.
- **Event-driven:** app emits `DocumentUpdated(doc_id)` → queue → worker. Latency = seconds.

State the target: **freshness SLO** ("changes visible in retrieval within 5 minutes") drives the mechanism.

### 5.4 Model migrations (re-embedding everything)
You *will* change embedding models. Vectors from different models are incomparable — you cannot mix them in one index.

**Blue/green index:**
1. Create `chunks_v2` with new model.
2. Backfill from the manifest (not from the old index — re-read source text).
3. Dual-write during backfill.
4. Shadow-query both; compare recall on golden set.
5. Flip alias `chunks_current → chunks_v2`. Keep v1 for rollback window, then drop.

Qdrant: collection aliases. Postgres: view or table swap in a transaction. Pinecone: namespaces.

### 5.5 Freshness at query time
- **Metadata filter:** `published_at >= now - 30d` when recency matters.
- **Time decay in ranking:** `score * exp(-λ · age_days)` as a final re-score (Elastic-style `gauss` decay). Don't bake time into the embedding.
- **Versioned docs:** store `is_latest` flag; default filter to latest; keep history for point-in-time queries ("what did the policy say in Q2?").
- **Soft-delete first:** flag `deleted=true`, filter it out immediately, physically delete in the nightly compaction. Instant correctness, deferred cost.

### 5.6 Index maintenance gotchas
- **HNSW deletes are tombstones.** The graph isn't repaired; recall degrades and memory doesn't shrink until you rebuild/optimize (`VACUUM`/`REINDEX` in pgvector, Qdrant's optimizer, Milvus compaction). Schedule it.
- **pgvector:** HNSW build is memory-hungry; bulk load *then* build the index. Updates are cheap; index rebuild is not.
- **Caches:** query-embedding cache and semantic answer cache must be invalidated on upsert for affected `doc_id`s — or keyed with the index version.

### 5.7 Consistency
Ingest is not transactional across "source updated" and "vector updated." Accept eventual consistency and **make it observable**: `max(ingested_at)` lag metric, count of pending changes, per-run upsert/delete counts. If you need read-your-writes (user uploads a doc and asks about it immediately), do a synchronous ingest path for that doc scoped to the user's session.

---

## 6. Optimization — quality, latency, cost

### 6.1 Quality (in ROI order)
1. Build a **golden set** (50–200 query → relevant chunk_ids). Nothing else is meaningful without it.
2. Add **reranking**.
3. Add **hybrid** (BM25 + dense).
4. Fix **chunking** (structure-aware + parent-child + contextual prefix).
5. Add **metadata filters / self-query**.
6. Query rewriting for multi-turn.
7. Only then: bigger embedding model, fine-tuned embeddings.

### 6.2 Latency budget (typical, p50)
| Stage | Target | Levers |
|---|---|---|
| Query embed | 5–20ms | Small model, ONNX/fastembed, cache repeated queries |
| ANN search | 5–50ms | `ef_search` down, quantization, pre-filter, fewer dims |
| BM25 | 5–30ms | Postgres GIN / OpenSearch |
| Rerank top-50 | 50–200ms | Batch, GPU, or rerank top-20 only; small reranker |
| LLM generate | 500ms–5s | Dominant cost; stream tokens; smaller model for simple queries |

Run embed + BM25 in parallel. Rerank is the knob: rerank fewer candidates before you shrink the ANN.

### 6.3 Cost
- **Quantization:** scalar int8 (~4x memory, ~0 recall loss), binary (~32x, needs rescoring with full vectors). Qdrant/pgvector 0.7+ support both.
- **Fewer dims** (Matryoshka truncation).
- **Cache:** embedding cache keyed on text hash (ingest and query); semantic cache for answers with a similarity threshold and index-version key.
- **Tiered:** hot index in memory, cold in disk-based IVF.
- **Batch embedding at ingest** (fastembed handles batches; GPU if volume warrants).

### 6.4 Don't over-engineer
- Corpus < ~50k tokens and static? **Stuff it in context**, no RAG.
- Corpus is a few thousand docs with rich metadata? Postgres full-text + filters may beat vector search. Run the eval.
- Fine-tuning does **not** replace RAG for knowledge; it changes behavior/style. RAG for facts, fine-tune for form.

---

## 7. Agentic RAG

Single-shot retrieve-then-read fails when the question needs multiple hops, or when the first retrieval is off. Agentic patterns:

- **Retrieve → grade → rewrite loop** (Corrective RAG / Self-RAG): model grades relevance of retrieved chunks; if low, rewrite query or fall back to web search. Cap iterations.
- **Decompose → retrieve per sub-question → synthesize.**
- **Router:** decide between vector store, SQL/structured tool, web, or "no retrieval needed."
- **Supervisor with retrieval as one tool** — your `analyst-graph` design. RAG becomes `search_filings(query, filters)` alongside `get_financials(ticker)`.

Guardrails: iteration cap, token budget, deterministic grading where possible (metadata mismatch → reject without an LLM call). Your multi-agent skepticism applies: most "agentic RAG" needs one retry loop, not five agents.

---

## 8. Evaluation

**Retrieval metrics** (need golden set of query → relevant chunk ids):
- `recall@k` — fraction of relevant chunks in top-k. Primary metric for the retriever.
- `precision@k`, `MRR`, `nDCG@k` — when ordering matters.
- Test hybrid vs dense vs +rerank as separate configs; report the table.

**Generation metrics** (RAGAS-style, LLM-as-judge):
- **Faithfulness** — claims in answer supported by context? (hallucination detector)
- **Answer relevance** — answers the question?
- **Context precision/recall** — retrieved context was needed / sufficient?

Validate judge against ~100 human labels with Cohen's κ (you've done this — say so). Run evals in CI on every chunking/model/prompt change. Log query, retrieved ids, scores, final answer to Langfuse; sample for human review; mine failures into the golden set.

---

## 9. Code

All snippets Python 3.11+. `pip install fastembed qdrant-client psycopg[binary] pgvector rank-bm25`.

### 9.1 Chunking: structure-aware + parent-child

```python
import hashlib, re
from dataclasses import dataclass, field

@dataclass
class Chunk:
    doc_id: str
    chunk_id: str
    parent_id: str
    text: str            # small chunk, what gets embedded
    parent_text: str     # what gets returned to the LLM
    meta: dict = field(default_factory=dict)
    @property
    def chunk_hash(self) -> str:
        return hashlib.sha256(self.text.encode()).hexdigest()

def split_sections(md: str) -> list[tuple[str, str]]:
    """Split markdown on headings → [(section_title, body)]."""
    parts = re.split(r"\n(?=#{1,3} )", md)
    out = []
    for p in parts:
        title, _, body = p.partition("\n")
        out.append((title.strip("# ").strip(), body.strip()))
    return out

def window(text: str, size: int, overlap: int) -> list[str]:
    words = text.split()
    step = size - overlap
    return [" ".join(words[i:i+size]) for i in range(0, max(len(words), 1), step)]

def chunk_document(doc_id: str, md: str, meta: dict,
                   parent_words=800, child_words=200, overlap=40) -> list[Chunk]:
    chunks = []
    for s_idx, (title, body) in enumerate(split_sections(md)):
        for p_idx, parent in enumerate(window(body, parent_words, 0)):
            parent_id = f"{doc_id}#s{s_idx}p{p_idx}"
            for c_idx, child in enumerate(window(parent, child_words, overlap)):
                # contextual prefix: cheap version (title); expensive version = LLM summary
                text = f"{meta.get('title','')} > {title}\n{child}"
                chunks.append(Chunk(doc_id, f"{parent_id}c{c_idx}", parent_id,
                                    text, parent, {**meta, "section": title}))
    return chunks
```

### 9.2 Embedding with fastembed (dense + sparse)

```python
from fastembed import TextEmbedding, SparseTextEmbedding

dense = TextEmbedding("BAAI/bge-small-en-v1.5")      # 384d
sparse = SparseTextEmbedding("Qdrant/bm25")          # BM25 as sparse vectors

def embed_docs(texts: list[str]):
    d = list(dense.passage_embed(texts))              # note: passage_ vs query_ prefixing
    s = list(sparse.embed(texts))
    return d, s

def embed_query(q: str):
    return next(dense.query_embed(q)), next(sparse.query_embed(q))
```

### 9.3 Qdrant: idempotent upsert, hybrid query with RRF

```python
from qdrant_client import QdrantClient, models
import uuid

client = QdrantClient("http://localhost:6333")
COL = "filings_v1"

def ensure_collection():
    if not client.collection_exists(COL):
        client.create_collection(
            COL,
            vectors_config={"dense": models.VectorParams(size=384, distance=models.Distance.COSINE)},
            sparse_vectors_config={"bm25": models.SparseVectorParams(modifier=models.Modifier.IDF)},
        )
        for f in ("doc_id", "ticker", "form", "fy"):
            client.create_payload_index(COL, f, models.PayloadSchemaType.KEYWORD)

def point_id(chunk_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, chunk_id))   # deterministic → upsert idempotent

def upsert_chunks(chunks: list[Chunk]):
    d, s = embed_docs([c.text for c in chunks])
    client.upsert(COL, points=[
        models.PointStruct(
            id=point_id(c.chunk_id),
            vector={"dense": d[i].tolist(),
                    "bm25": models.SparseVector(indices=s[i].indices.tolist(), values=s[i].values.tolist())},
            payload={"doc_id": c.doc_id, "chunk_id": c.chunk_id, "parent_id": c.parent_id,
                     "chunk_hash": c.chunk_hash, "parent_text": c.parent_text,
                     "embed_model": "bge-small-en-v1.5", **c.meta},
        ) for i, c in enumerate(chunks)
    ])

def delete_doc(doc_id: str):
    client.delete(COL, points_selector=models.FilterSelector(filter=models.Filter(
        must=[models.FieldCondition(key="doc_id", match=models.MatchValue(value=doc_id))])))

def hybrid_search(q: str, filters: dict | None = None, k: int = 20):
    qd, qs = embed_query(q)
    flt = models.Filter(must=[models.FieldCondition(key=key, match=models.MatchValue(value=v))
                              for key, v in (filters or {}).items()]) if filters else None
    res = client.query_points(
        COL,
        prefetch=[
            models.Prefetch(query=qd.tolist(), using="dense", limit=k * 3, filter=flt),
            models.Prefetch(query=models.SparseVector(indices=qs.indices.tolist(), values=qs.values.tolist()),
                            using="bm25", limit=k * 3, filter=flt),
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        limit=k,
    )
    return res.points
```

### 9.4 Rerank + parent collapse

```python
from fastembed.rerank.cross_encoder import TextCrossEncoder

reranker = TextCrossEncoder("BAAI/bge-reranker-base")

def retrieve(q: str, filters=None, k_final=6):
    hits = hybrid_search(q, filters, k=30)
    docs = [h.payload["text"] if "text" in h.payload else h.payload["parent_text"] for h in hits]
    scores = list(reranker.rerank(q, docs))
    ranked = sorted(zip(scores, hits), key=lambda x: -x[0])
    seen, out = set(), []
    for score, h in ranked:                       # collapse children → unique parents
        pid = h.payload["parent_id"]
        if pid in seen: continue
        seen.add(pid); out.append((score, h))
        if len(out) == k_final: break
    return out

def build_context(results, budget_chars=12000):
    blocks, used = [], 0
    for score, h in results:
        block = f"[{h.payload['parent_id']}] ({h.payload.get('form')} {h.payload.get('fy')} §{h.payload.get('section')})\n{h.payload['parent_text']}\n"
        if used + len(block) > budget_chars: break
        blocks.append(block); used += len(block)
    return "\n".join(blocks)
```

### 9.5 Incremental sync with manifest (the "dynamic content" answer in code)

```python
import json, psycopg

MANIFEST_DDL = """
CREATE TABLE IF NOT EXISTS rag_manifest (
  doc_id TEXT PRIMARY KEY, doc_hash TEXT NOT NULL,
  chunk_hashes JSONB NOT NULL,          -- {chunk_id: chunk_hash}
  embed_model TEXT NOT NULL, updated_at TIMESTAMPTZ DEFAULT now());
"""

def sync_document(conn, doc_id: str, md: str, meta: dict, embed_model="bge-small-en-v1.5"):
    doc_hash = hashlib.sha256(md.encode()).hexdigest()
    with conn.cursor() as cur:
        cur.execute("SELECT doc_hash, chunk_hashes FROM rag_manifest WHERE doc_id=%s", (doc_id,))
        row = cur.fetchone()
    if row and row[0] == doc_hash:
        return {"status": "unchanged"}

    new_chunks = chunk_document(doc_id, md, meta)
    new_map = {c.chunk_id: c.chunk_hash for c in new_chunks}
    old_map = row[1] if row else {}

    to_upsert = [c for c in new_chunks if old_map.get(c.chunk_id) != c.chunk_hash]
    to_delete = [cid for cid in old_map if cid not in new_map]

    if to_upsert: upsert_chunks(to_upsert)
    if to_delete: client.delete(COL, points_selector=models.PointIdsList(points=[point_id(c) for c in to_delete]))

    with conn.cursor() as cur:
        cur.execute("""INSERT INTO rag_manifest (doc_id, doc_hash, chunk_hashes, embed_model)
                       VALUES (%s,%s,%s,%s) ON CONFLICT (doc_id) DO UPDATE
                       SET doc_hash=EXCLUDED.doc_hash, chunk_hashes=EXCLUDED.chunk_hashes,
                           embed_model=EXCLUDED.embed_model, updated_at=now()""",
                    (doc_id, doc_hash, json.dumps(new_map), embed_model))
    conn.commit()
    return {"status": "changed", "upserted": len(to_upsert), "deleted": len(to_delete)}

def remove_document(conn, doc_id: str):
    delete_doc(doc_id)
    with conn.cursor() as cur:
        cur.execute("DELETE FROM rag_manifest WHERE doc_id=%s", (doc_id,))
    conn.commit()
```

### 9.6 CDC from Delta Lake (your edgar-mcp tables)

```python
# Requires: ALTER TABLE filings SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
from pyspark.sql import functions as F

def sync_from_delta(spark, table: str, last_version: int) -> int:
    cdf = (spark.read.format("delta")
           .option("readChangeFeed", "true")
           .option("startingVersion", last_version + 1)
           .table(table))
    latest_version = spark.sql(f"DESCRIBE HISTORY {table}").agg(F.max("version")).first()[0]

    # keep only the final state per doc within this batch
    w = cdf.filter(F.col("_change_type") != "update_preimage")
    rows = w.orderBy("_commit_version", "_commit_timestamp").collect()
    final = {}
    for r in rows:
        final[r["doc_id"]] = r
    for doc_id, r in final.items():
        if r["_change_type"] == "delete":
            remove_document(conn, doc_id)
        else:  # insert | update_postimage
            sync_document(conn, doc_id, r["content_md"], {"ticker": r["ticker"], "form": r["form"], "fy": r["fy"]})
    return latest_version   # persist as watermark for next run
```

### 9.7 pgvector variant (single-DB hybrid via SQL)

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE chunks (
  chunk_id TEXT PRIMARY KEY, doc_id TEXT, parent_id TEXT,
  text TEXT, parent_text TEXT, meta JSONB,
  embedding vector(384), tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', text)) STORED,
  embed_model TEXT, chunk_hash TEXT, updated_at TIMESTAMPTZ DEFAULT now());
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops) WITH (m=16, ef_construction=128);
CREATE INDEX ON chunks USING gin (tsv);
CREATE INDEX ON chunks ((meta->>'ticker'), (meta->>'fy'));

-- Hybrid with RRF, filter applied inside both arms (pre-filter)
WITH dense AS (
  SELECT chunk_id, row_number() OVER (ORDER BY embedding <=> $1) AS r
  FROM chunks WHERE meta->>'ticker' = $3 ORDER BY embedding <=> $1 LIMIT 60),
bm25 AS (
  SELECT chunk_id, row_number() OVER (ORDER BY ts_rank_cd(tsv, q) DESC) AS r
  FROM chunks, plainto_tsquery('english', $2) q
  WHERE tsv @@ q AND meta->>'ticker' = $3 LIMIT 60)
SELECT c.chunk_id, c.parent_id, c.parent_text,
       COALESCE(1.0/(60+d.r),0) + COALESCE(1.0/(60+b.r),0) AS rrf
FROM chunks c LEFT JOIN dense d USING (chunk_id) LEFT JOIN bm25 b USING (chunk_id)
WHERE d.r IS NOT NULL OR b.r IS NOT NULL
ORDER BY rrf DESC LIMIT 20;
```

Set `SET hnsw.ef_search = 100;` per session to trade latency for recall.

### 9.8 Retrieval eval harness

```python
import statistics

def recall_at_k(retrieved_ids: list[str], relevant: set[str], k: int) -> float:
    return len(set(retrieved_ids[:k]) & relevant) / max(len(relevant), 1)

def mrr(retrieved_ids, relevant):
    for i, cid in enumerate(retrieved_ids, 1):
        if cid in relevant: return 1 / i
    return 0.0

def evaluate(golden: list[dict], retriever, k=10):
    """golden = [{"query": str, "filters": dict, "relevant_parent_ids": [..]}]"""
    r, m = [], []
    for g in golden:
        hits = retriever(g["query"], g.get("filters"))
        ids = [h.payload["parent_id"] for _, h in hits]
        rel = set(g["relevant_parent_ids"])
        r.append(recall_at_k(ids, rel, k)); m.append(mrr(ids, rel))
    return {"recall@k": statistics.mean(r), "mrr": statistics.mean(m), "n": len(golden)}

# Run as a CI gate: assert evaluate(golden, retrieve)["recall@k"] >= 0.85
```

### 9.9 As a LangGraph tool (fits `analyst-graph`)

```python
from langchain_core.tools import tool

@tool
def search_filings(query: str, ticker: str | None = None, form: str | None = None, fy: int | None = None) -> str:
    """Semantic + keyword search over SEC filings. Returns cited passages."""
    filters = {k: v for k, v in {"ticker": ticker, "form": form, "fy": fy}.items() if v is not None}
    return build_context(retrieve(query, filters))
```

---

## 10. Interview question bank

### L4 — can you build it correctly

**Q: Walk me through a RAG pipeline end to end.**
Two pipelines (offline ingest, online query). Ingest: parse → structure-aware chunk with parent-child → embed (dense + sparse) → upsert with deterministic ids and metadata. Query: rewrite → hybrid search with RRF → cross-encoder rerank → collapse to parents → budgeted context with citation handles → generate → verify citations. Then say: "and a golden set with recall@k in CI, because none of the tuning is meaningful without it."

**Q: Why hybrid search?** Dense misses exact tokens (tickers, part numbers, names); BM25 misses paraphrase. Fuse ranks with RRF because scores aren't comparable.

**Q: Chunk size?** Retrieval unit 256–512 tokens; return the parent (1–2k). Small chunks embed precisely; large ones give the model context. Tune with eval.

**Q: How do you pick a vector DB?** pgvector if you already run Postgres and are under ~10M vectors (transactions with your metadata, one system). Qdrant for standalone with heavy filtering. Managed (Databricks Vector Search / Pinecone) when the platform already hosts the data or you want zero ops. Ask about filtered ANN behavior and delete semantics before committing.

**Q: What's the reranker and why not just retrieve top-5?** Bi-encoders embed query and doc independently — fast but coarse. Cross-encoders score the pair jointly — precise but O(candidates). Two-stage gets both.

**Q: Asymmetric embeddings?** Some models (bge, e5) expect `query:`/`passage:` prefixes; omitting them quietly degrades recall.

**Q: How do you evaluate?** Retrieval: recall@k, MRR on a golden set. Generation: faithfulness + answer relevance via LLM-as-judge, validated with Cohen's κ against human labels. Both in CI.

### L5 — can you own it in production

**Q: The corpus changes hourly. How do you keep the index fresh?**
Deterministic chunk ids + content hashes + a manifest table. Change detection yields new/changed/deleted docs; chunk-level hash diff means only changed chunks re-embed; orphaned chunks are deleted. Source of changes: CDC (Delta Change Data Feed / Debezium) or events for low latency, batch diff for nightly. State a freshness SLO and measure ingest lag. Soft-delete for instant correctness, hard-delete in compaction. Caches keyed to index version.

**Q: How do you upgrade the embedding model without downtime?**
Blue/green index: build v2 from source text via manifest, dual-write, shadow-compare on golden set, flip alias, keep v1 for rollback. Never mix models in one index.

**Q: Deletes are slow / recall dropped after months of updates. Why?**
HNSW deletes are tombstones; graph isn't repaired. Schedule optimize/reindex; monitor recall vs a brute-force sample.

**Q: Latency is 3s p95. Where do you look?**
Instrument stages. Usually: reranking too many candidates, or ANN with a post-filter that returns few results and retries, or synchronous embedding of a slow model. Parallelize dense + BM25, rerank top-20 not 100, cache query embeddings, stream generation.

**Q: Retrieval is fine but the model still hallucinates.**
Check faithfulness metric first. Then: context too long (lost-in-middle) → tighter budget; conflicting versions of the same doc → `is_latest` filter; prompt doesn't forbid outside knowledge; add mechanical citation validation and refuse when top rerank score is below threshold.

**Q: When would you *not* use RAG?**
Corpus fits in context and is static → stuff it. Behavior/style change → fine-tune. Structured questions ("revenue in FY23") → text-to-SQL over the table, not vector search over prose. Router decides.

**Q: Multi-tenant RAG?**
Tenant id as mandatory filter enforced in the retrieval function (not the prompt); Qdrant/Weaviate multi-tenancy or Postgres RLS; separate collections only when isolation/compliance demands it. Test: a query for tenant A can never return tenant B's chunk — write the test.

**Q: Agentic RAG — when is it worth it?**
Multi-hop or ambiguous queries. Start with one retrieve → grade → rewrite loop with a cap. Most gains come from a router (vector vs SQL vs none) and metadata extraction, not from more agents.

**Q: How would you design this on Databricks given the data is already in Delta?**
Enable CDF on the source table, Databricks Vector Search Delta Sync index (managed embedding or self-managed bge), hybrid query, reranker in the serving layer, golden set evaluated via MLflow. You've replaced the entire §5 pipeline with configuration — say that, and say what you lose (control over chunking and embedding cadence).

### The "should not have been RAG" answer
Have one story where the right call was **not** vector search — e.g., a metadata filter + full-text search beat embeddings on a structured corpus, or a question was better served by a SQL tool. Interviewers weight this heavily; it signals you optimize for the outcome, not the technique.

---

## 11. References

**Repos**
1. https://github.com/qdrant/fastembed — dense, sparse, and reranker models you're already using; check `examples/`.
2. https://github.com/qdrant/qdrant-client — `query_points` with prefetch + RRF fusion; hybrid search examples.
3. https://github.com/pgvector/pgvector — README covers HNSW tuning, quantization, filtering caveats.
4. https://github.com/run-llama/llama_index — read `IngestionPipeline` + `docstore` for the canonical dedup/upsert implementation.
5. https://github.com/explodinggradients/ragas — faithfulness / context precision metrics.

**Docs**
6. https://docs.databricks.com/aws/en/generative-ai/vector-search — Delta Sync index; directly relevant to edgar-mcp.
7. https://docs.delta.io/latest/delta-change-data-feed.html — CDF for incremental sync.
8. https://qdrant.tech/documentation/concepts/hybrid-queries/ — prefetch/fusion semantics.

**Blogs**
9. https://www.anthropic.com/news/contextual-retrieval — contextual prefix + hybrid + rerank, with numbers.
10. https://arxiv.org/abs/2307.03172 — "Lost in the Middle" (context position effects).
11. https://www.pinecone.io/learn/series/rag/rerankers/ — clear two-stage retrieval explanation.
