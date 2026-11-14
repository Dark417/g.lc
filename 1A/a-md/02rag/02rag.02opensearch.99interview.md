# 02rag.02opensearch.99interview Interview Questions

> Level 4 (L4) baseline and Level 5 (L5) extensions for OpenSearch as a vector store.

## Index

- [1. Core Questions](#1-core-questions)
  - [Q1 Serverless Or Domain](#q1-serverless-or-domain)
  - [Q2 Three Dedicated Masters](#q2-three-dedicated-masters)
  - [Q3 Shard Sizing](#q3-shard-sizing)
  - [Q4 The Three Serverless Policies](#q4-the-three-serverless-policies)
  - [Q5 Efficient Filtering](#q5-efficient-filtering)
  - [Q6 Hybrid Search](#q6-hybrid-search)
  - [Q7 Bulk Returns 200 But Docs Missing](#q7-bulk-returns-200-but-docs-missing)
- [2. L5-Only Questions](#2-l5-only-questions)
  - [Q8 Morning Latency Spikes](#q8-morning-latency-spikes)
  - [Q9 Move 100M Vectors To A Domain](#q9-move-100m-vectors-to-a-domain)
  - [Q10 Tenant Isolation](#q10-tenant-isolation)

## 1. Core Questions

Each question has an L4 answer and an L5 extension.

### Q1 Serverless Or Domain

**Q:** Serverless collection or managed domain for a Bedrock Knowledge Base (KB)?

**L4 answer**

- Serverless: no nodes or shards, KB quick-create, scales in OpenSearch Compute Units (OCUs)
- Domain: more control, more ops

**L5 extra**

- Serverless bills a minimum OCU floor while idle
  - ⇒ wrong for tiny, spiky workloads
- Domain unlocks Inverted File Index (IVF), on_disk compression, Index State Management (ISM), and shard layout for large corpora
- Decide by traffic shape and team
  - Steady traffic + no ops team ⇒ Serverless

### Q2 Three Dedicated Masters

**Q:** Why three dedicated master nodes?

**L4 answer**

- Masters manage cluster state; three give a quorum of two
- One master = single point of failure
- Two cannot elect after one fails

**L5 extra**

- Dedicated masters keep cluster-state work off busy data nodes
  - ⇒ fewer timeouts under load
- Size masters by shard count, not data volume
- Multi-AZ with standby places masters across three Availability Zones (AZs)

### Q3 Shard Sizing

**Q:** How do you size shards for a domain?

**L4 answer**

- 10–30 gibibytes (GiB) per shard for search, 30–50 GiB for logs (Amazon Web Services (AWS) guidance)
- Primary count fixed at creation

**L5 extra**

- Too many shards ⇒ heap and cluster-state overhead
- Too few ⇒ slow recovery and hotspots
- For vectors, memory per node (graphs off-heap) binds before shard size
- Use rollover + ISM for growing indexes instead of oversizing up front

### Q4 The Three Serverless Policies

**Q:** What are the three Serverless policies and what does each gate?

**L4 answer**

- Encryption: which key encrypts the collection
- Network: from where the endpoint is reachable
- Data access: which principals can do what on indexes and the collection

**L5 extra**

- Encryption must exist before the collection, and the key is fixed
- Identity and Access Management (IAM) `aoss:APIAccessAll` AND a data-access rule are both required
- Private collections reach Bedrock through `SourceServices: bedrock.amazonaws.com`

### Q5 Efficient Filtering

**Q:** Explain efficient filtering in k-Nearest Neighbors (k-NN).

**L4 answer**

- Put the filter inside the `knn` clause
- Avoids post-filtering, which can return fewer than k

**L5 extra**

- The engine switches per query
  - Selective filter ⇒ exact search over matching docs
  - Loose filter ⇒ filtered Hierarchical Navigable Small World (HNSW)
- faiss 2.9+ and lucene support it
- For tenant isolation at scale, also consider index-per-tenant to avoid noisy neighbours

### Q6 Hybrid Search

**Q:** How do you run hybrid search in OpenSearch?

**L4 answer**

- `hybrid` query with a `match` and a `knn` sub-query
- A search pipeline normalizes and combines scores

**L5 extra**

- Best Matching 25 (BM25) is unbounded, k-NN scores bounded
  - ⇒ min-max normalization before the weighted mean
- Weights follow sub-query order; tune on a golden set
- Reciprocal Rank Fusion (RRF) (2.19+) avoids weights
- Reranking on top of either improves precision

### Q7 Bulk Returns 200 But Docs Missing

**Q:** Bulk indexing returns 200 but documents are missing. Why?

**L4 answer**

- `_bulk` reports failures per item
- Check `errors` and each item's status

**L5 extra**

- Retry only 429 / 5xx with backoff
  - 4xx (mapping, dims) never succeeds on retry
- On Serverless, writes are not instantly searchable
  - ⇒ do not "read your write" right after bulk
- Keep ids stable so retries are upserts, not duplicates

## 2. L5-Only Questions

Depth, scale, and design ownership.

### Q8 Morning Latency Spikes

**Q:** Your KB retrieval latency spikes every morning. Diagnose.

**L5 answer**

- Serverless: search OCUs scaling from the floor
  - ⇒ check OCU metrics against traffic
- Domain: graphs evicted from native memory ⇒ cold loads
  - Use warmup, more Random-Access Memory (RAM)
- Segment count high after nightly ingestion
  - ⇒ force_merge in a maintenance window
- Measure p99 per stage: embedding, OpenSearch, rerank, Large Language Model (LLM)

### Q9 Move 100M Vectors To A Domain

**Q:** Move a 100M-vector index from Serverless to a domain to cut cost. Plan it.

**L5 answer**

- Size: 100M × (1.1 × (4·1024 + 8·16)) ≈ 465 gigabytes (GB) native graph memory float32
  - ⇒ use on_disk 32x or fp16
- Build the new index in parallel (blue/green)
  - Re-ingest from the source of truth, not by copying graphs
- Dual-read a sample, compare recall@k and p99
  - Then switch the KB (new data source / KB) or the app alias
- Keep Serverless until the rollback window closes

### Q10 Tenant Isolation

**Q:** Design tenant isolation for a multi-tenant Retrieval-Augmented Generation (RAG) store.

**L5 answer**

- Small tenants: shared index + mandatory tenant filter inside `knn`
  - Plus data-access per role where possible
- Large tenants: index or collection per tenant
  - ⇒ isolation, separate deletion, noisy-neighbour control
- Enforce the tenant filter server-side (never trust client filters)
  - KB metadata filters do the same at retrieval
- Trade-off: per-tenant indexes multiply shards/OCUs
