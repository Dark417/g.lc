# embeddings.99interview Interview Questions

> Level 4 (L4) baseline and Level 5 (L5) extensions for embeddings, Approximate Nearest Neighbor (ANN), quantization, and hybrid search.

## Index

- [1. Core Questions](#1-core-questions)
  - [Q1 Retrieval-Augmented Generation (RAG) End To End](#q1-retrieval-augmented-generation-rag-end-to-end)
  - [Q2 Cosine Dot Or L2](#q2-cosine-dot-or-l2)
  - [Q3 Hierarchical Navigable Small World (HNSW) And Its Knobs](#q3-hierarchical-navigable-small-world-hnsw-and-its-knobs)
  - [Q4 HNSW vs Inverted File Index (IVF)](#q4-hnsw-vs-inverted-file-index-ivf)
  - [Q5 Index Exceeds Memory](#q5-index-exceeds-memory)
  - [Q6 Hybrid Search](#q6-hybrid-search)
  - [Q7 Embedding Model Upgrade](#q7-embedding-model-upgrade)
- [2. L5-Only Questions](#2-l5-only-questions)
  - [Q8 Recall Drops In Production](#q8-recall-drops-in-production)
  - [Q9 Store For 200M Chunks](#q9-store-for-200m-chunks)
  - [Q10 When RAG Is Wrong](#q10-when-rag-is-wrong)

## 1. Core Questions

Each question has an L4 answer and an L5 extension.

### Q1 Retrieval-Augmented Generation (RAG) End To End

**Q:** Walk through a RAG request end to end.

**L4 answer**

- Index time: parse → chunk → embed → store vector, text, metadata
- Query time
  - Embed the question with the same model
  - k-Nearest Neighbors (kNN) top k
  - Put chunks in the prompt
  - Generate with citations

**L5 extra**

- Index time is throughput-bound and priced per embedded token
- Query time is latency-bound and the Large Language Model (LLM) dominates
- Quality levers in order: chunking, hybrid retrieval, reranking, then prompt
- Evaluate retrieval (recall@k, context precision) separately from generation (faithfulness)
  - See [evaluations](../04safety/evaluations.00index.md)

### Q2 Cosine Dot Or L2

**Q:** Cosine, dot product, or L2: which, and why normalize?

**L4 answer**

- Cosine compares angle
- Dot also counts magnitude
- L2 is distance
- On unit vectors all three rank the same

**L5 extra**

- d² = 2 − 2·cos for unit vectors
  - So the choice is about compute and engine support
- Normalize at write time ⇒ dot product at query time, no norms
- Unnormalized dot lets long vectors dominate regardless of meaning

### Q3 Hierarchical Navigable Small World (HNSW) And Its Knobs

**Q:** Explain HNSW and its knobs.

**L4 answer**

- Layered proximity graph
- Greedy search from sparse top layer to dense bottom layer
- `m` = links per node
- `ef_construction` = build beam
- `ef_search` = query beam

**L5 extra**

- `ef_search` is the only query-time dial
  - Raise it until recall@k meets target, watch p99
- Memory ≈ 1.1 × (4·d + 8·m) bytes per vector (faiss, OpenSearch sizing)
  - ⇒ dims and m drive cost
- Deletes are tombstones until merge
  - Heavy churn degrades the graph ⇒ periodic reindex

### Q4 HNSW vs Inverted File Index (IVF)

**Q:** HNSW vs IVF?

**L4 answer**

- HNSW: graph, high recall, no training, more memory
- IVF: k-means cells, scan `nprobes` cells, needs training, less memory

**L5 extra**

- IVF pairs with Product Quantization (PQ) for billion-scale in Random-Access Memory (RAM) budgets
- HNSW is the default up to hundreds of millions
- IVF centroids drift with data ⇒ retrain
- HNSW handles incremental inserts natively
- Both expose one recall dial (`ef_search` vs `nprobes`)

### Q5 Index Exceeds Memory

**Q:** Your 1024-dim index doesn't fit the memory budget. Options?

**L4 answer**

- Fewer dims (Titan V2 512 or 256)
- Quantize: fp16, int8, binary
- Disk-based mode with rescoring

**L5 extra**

- Binary = 32x smaller
  - Recover recall by oversampling + float rescoring
- Measure recall@k for each option on a golden set
  - Pick the cheapest that meets target
- Or switch store tier: Simple Storage Service (S3) Vectors for cold, rarely queried corpora

### Q6 Hybrid Search

**Q:** Why hybrid search, and how are scores combined?

**L4 answer**

- Vectors miss exact tokens
- Best Matching 25 (BM25) misses paraphrase
- Run both and fuse

**L5 extra**

- BM25 scores are unbounded, cosine is bounded
  - ⇒ normalize (min-max) before a weighted mean
  - Or use Reciprocal Rank Fusion (RRF) on ranks
- Weights are a tuning knob per query mix
- RRF needs no tuning but ignores score gaps
- Add a reranker on the fused top 50 for the final top 5

### Q7 Embedding Model Upgrade

**Q:** You upgrade the embedding model. What happens?

**L4 answer**

- Old and new vectors are not comparable
- Re-embed the full corpus into a new index, then switch

**L5 extra**

- Blue/green index
  - Build new index in parallel
  - Dual-read for eval
  - Flip an alias
- Cache keys include model id ⇒ the upgrade invalidates the cache automatically
- Budget: full corpus tokens × new model price
  - Plus double storage during cutover

## 2. L5-Only Questions

Depth, scale, and design ownership.

### Q8 Recall Drops In Production

**Q:** Recall is fine in staging but drops in production. Diagnose.

**L5 answer**

- Check index size
  - Knobs tuned on 100k vectors under-search at 50M ⇒ re-sweep `ef_search`
- Check filters
  - Selective filters with post-filtering return fewer than k
- Check drift
  - New document types the embedding model clusters poorly
- Check query distribution
  - Production queries are shorter, more keyword-like ⇒ hybrid
- Build a golden set from production logs
  - Track recall@k as a metric, not a one-off test

### Q9 Store For 200M Chunks

**Q:** Pick a vector store for 200M chunks, 50 Queries Per Second (QPS), filters by tenant, cost-sensitive.

**L5 answer**

- Memory: 200M × 1024 float32 ≈ 800 gigabytes (GB) raw
  - ⇒ in-memory HNSW is expensive
- Options
  - OpenSearch managed with on_disk binary quantization + rescoring
  - S3 Vectors if latency of hundreds of ms is acceptable
  - Titan V2 at 512 dims halves everything
- Tenant filter
  - Efficient filtering
  - Or index-per-tenant for large tenants (noisy-neighbour isolation)
- Decide by measured recall@k and p99 at 50 QPS, then cost per month

### Q10 When RAG Is Wrong

**Q:** When is RAG the wrong answer?

**L5 answer**

- Structured questions over tables ⇒ text-to-Structured Query Language (SQL)
- Behaviour or format learning ⇒ fine-tuning
- Tiny static corpus ⇒ put it in the prompt with caching
- Multi-hop over relations ⇒ GraphRAG (Neptune Analytics)
