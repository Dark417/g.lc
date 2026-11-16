# RAG in Production — The Short Version

> Companion to `rag-reference-handbook.md`. High-level: the process, the real production problems, and how to pick `k`. No framework code; see the handbook for that.

---

## 1. The process in one screen

```
OFFLINE (ingest)                              ONLINE (query)
source ─► parse ─► chunk ─► embed ─► index    query ─► rewrite ─► search ─► rerank ─► context ─► LLM
             │                         ▲                  (dense + BM25)   (cross-enc)  (budget)   (cite)
             └── change detection ─────┘
```

- **Ingest** turns documents into searchable units.
  - Parse: keep structure (title, section, page, version) as metadata.
  - Chunk: small unit for retrieval (~300 tokens), larger parent for reading (~1–2k). Prepend doc context to each chunk.
  - Embed: one model, one version, recorded on every vector.
  - Index: HNSW by default; store metadata beside the vector for filtering.
- **Query** turns a question into the best 5–10 passages.
  - Rewrite: make the query standalone; extract filters (ticker, year, doc type).
  - Search: dense + keyword in parallel, fuse by rank (RRF).
  - Rerank: cross-encoder over top 30–50 → keep top 5–10.
  - Context: collapse to parents, fixed token budget, citation handles.
  - Generate: answer only from context; verify citations mechanically.
- **Eval** sits under both: golden set → recall@k for retrieval, faithfulness for generation, both in CI.

**Mental model:** RAG is a search engine with an LLM reader bolted on. Quality problems are search problems.

---

## 2. The real production problems

### 2.1 New data streaming in
- Problem: users expect today's document to be findable today.
- Fix: event or CDC-driven ingest, not nightly batch.
  - Source emits change → queue → worker → chunk/embed/upsert.
  - Delta Lake: Change Data Feed. Postgres: logical replication. Files: bucket events.
- Set a **freshness SLO** ("visible in retrieval within 5 min") and measure ingest lag.
- Ingest must be **idempotent**: deterministic chunk ids, upsert not insert, so replays and retries are safe.

### 2.2 Updated data
- Problem: an edited doc leaves stale chunks behind; two versions compete at query time.
- Fix: manifest + hashes.
  - `doc_hash` unchanged → skip.
  - Changed → diff chunk hashes; re-embed only changed chunks; delete orphaned chunk ids.
  - Deleted from source → delete all chunks, drop from manifest.
- Versioned corpora: keep `is_latest` flag, filter to it by default, keep history for point-in-time questions.
- **Soft-delete first** (flag + filter, instant), hard-delete in nightly compaction.
- Invalidate caches (query embeddings, semantic answer cache) by `doc_id` or index version.

### 2.3 Re-chunking
- Triggers: chunk size change, new parser, adding contextual prefixes, structure-aware split.
- Chunk ids change → this is a **full rebuild**, not an incremental update.
- Do it as **blue/green**: build `index_v2` from source text, dual-write, compare on golden set, flip alias, keep v1 for rollback.
- Same procedure for **embedding model upgrades** — vectors from different models cannot share an index.

### 2.4 Re-prioritizing (ranking drifts over time)
- Problem: old-but-popular docs dominate; new policy loses to old policy; some sources are more trusted.
- Levers, applied at re-score time, not baked into embeddings:
  - **Recency decay:** `score × exp(−λ · age_days)` — tune λ per corpus.
  - **Source boost:** multiply by a trust weight per source/collection.
  - **Metadata filters first:** filter to latest/relevant scope, *then* rank.
  - **Feedback loop:** clicks/thumbs → boost or demote specific chunks; feed failures into the golden set.
- Re-evaluate on the golden set after every ranking change; ranking tweaks silently regress recall.

### 2.5 Index degradation
- HNSW deletes are tombstones; recall drops and memory doesn't shrink over months of churn.
- Schedule optimize / reindex / compaction. Monitor recall against a brute-force sample of queries.

### 2.6 Consistency and observability
- Source and index are never transactionally consistent; accept eventual consistency, make it visible:
  - ingest lag, pending changes, upsert/delete counts per run, index version served.
- Trace every query: query text, filters, retrieved ids + scores, rerank scores, final context, answer.
- Need read-your-writes (user uploads then asks)? Synchronous ingest for that doc, scoped to the session.

---

## 3. Choosing `k`

There are three different `k`s. Interviewers conflate them; don't.

| `k` | What it is | Typical | How to choose |
|---|---|---|---|
| `k_search` | candidates from each search arm (dense, BM25) | 30–100 | Large enough that recall@k_search ≈ 0.95 on golden set. Cheap to raise. |
| `k_rerank` | candidates fed to cross-encoder | 20–50 | Latency-bound: rerank cost is linear in this. Usually the bottleneck knob. |
| `k_final` | passages given to the LLM | 3–10 | Token budget ÷ parent size; plus faithfulness drops when context is long or noisy. |

- Method:
  1. Plot recall@k on the golden set for `k_search` — pick the knee.
  2. Pick `k_rerank` from the latency budget (~2–5 ms per pair on CPU, less on GPU).
  3. Pick `k_final` from context budget, then verify faithfulness didn't drop vs a smaller `k_final`.
- Make `k_final` **adaptive**: cut off when rerank score drops below a threshold or the gap to the top score is large. Fewer, better passages beat a fixed 10.
- Refuse or say "not found" when the top rerank score is below a floor — this is your hallucination guard.
- Parent-child changes the math: `k_final` counts unique parents, not chunks.

---

## 4. Optimization order (do these in sequence, measure each)

1. Golden set + recall@k in CI.
2. Reranker.
3. Hybrid (BM25 + dense).
4. Chunking: structure-aware, parent-child, contextual prefix.
5. Metadata extraction + filters.
6. Query rewriting for multi-turn.
7. Only then: bigger embedding model.

Skip RAG entirely when: corpus fits in context and is static; question is structured (use SQL/tool); you need behavior change (fine-tune).

---

## 5. Interview one-liners

- "RAG is a search engine; the LLM is the reader. I tune search first."
- "Freshness is CDC + idempotent upsert + a freshness SLO I measure."
- "Updates are a hash diff against a manifest; only changed chunks re-embed."
- "Re-chunking and model upgrades are blue/green index rebuilds, never in-place."
- "Ranking priority is a re-score step — recency decay, source weight — not something I bake into embeddings."
- "Three k's: search k for recall, rerank k for latency, final k for the context budget — each chosen from a different measurement."

---

## References
1. https://www.anthropic.com/news/contextual-retrieval — chunking + hybrid + rerank with numbers.
2. https://docs.databricks.com/aws/en/generative-ai/vector-search — Delta Sync as the managed answer to §2.1–2.2.
3. https://github.com/pgvector/pgvector — HNSW tuning, deletes, filtering caveats.
4. https://qdrant.tech/documentation/concepts/hybrid-queries/ — prefetch + RRF fusion.
