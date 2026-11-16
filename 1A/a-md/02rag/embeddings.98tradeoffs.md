# embeddings.98tradeoffs Tradeoffs

> When to use vector search, which knobs to turn, which store to pick, and how it fails.

## Index

- [1. When To Use Or Not](#1-when-to-use-or-not)
- [2. Knobs](#2-knobs)
- [3. Best Practices](#3-best-practices)
- [4. Store Comparison](#4-store-comparison)
- [5. Failure Modes](#5-failure-modes)

## 1. When To Use Or Not

Vector search fits natural-language questions over private, changing text.

- **Use vector search / Retrieval-Augmented Generation (RAG) when**
  - Answers must come from private, changing, or citable sources
  - Queries are natural language and paraphrase the docs
- **Use hybrid when**
  - Users search with codes, names, versions, error strings
- **Don't use when**
  - The data is structured and the question is a query
    - ⇒ text-to-SQL ([knowledge-bases.05stores-sql](knowledge-bases.05stores-sql.md))
  - The corpus fits in the context window and changes rarely
    - ⇒ prompt caching may be simpler
  - You need exact lookups by key
    - ⇒ a database, not similarity
  - Facts must be learned as behaviour (format, tone)
    - ⇒ prompting or fine-tuning ([customization](../01bedrock/customization.00index.md))

## 2. Knobs

Model and index knobs trade recall against storage, latency, and build time.

**Model and metric**

| Knob | Values | Trades | Change when |
|---|---|---|---|
| Embedding model | Titan V2, Cohere v3/v4, multimodal | quality per domain vs price | eval set shows low recall |
| `dimensions` | 256 / 512 / 1024 | recall vs storage + latency | memory-bound, recall loss acceptable |
| `normalize` | true (default) | – | keep true unless the model card says otherwise |
| Metric | cosine / dot / l2 | none on unit vectors | match the model card |

**Index and query**

| Knob | Values | Trades | Change when |
|---|---|---|---|
| Index | Hierarchical Navigable Small World (HNSW) / Inverted File Index (IVF) / flat | latency vs memory vs build time | N > ~100M or memory bound ⇒ IVF/Product Quantization (PQ) |
| `m`, `ef_construction` | 16 / 100 default | recall vs build time + memory | recall plateau below target |
| `ef_search`, `n_probe` | per query | recall vs latency | tune last, per workload |
| Quantization | fp16 / int8 / binary / PQ | memory vs recall | memory cost dominates |
| k (top-k) | 3–10 to Large Language Model (LLM), 20–100 to reranker | context tokens vs recall | answers miss facts ⇒ raise k + rerank |
| Hybrid weights | e.g. 0.3 lexical / 0.7 vector | exact-term vs paraphrase recall | identifier-heavy queries |

## 3. Best Practices

Each rule prevents a specific failure.

- Pin model id + dims + normalize in config, and store them with the index
  - ⇒ prevents mixing vectors from two models
- Cache embeddings by `sha256(model | dims | normalize | text)`
  - ⇒ re-ingest only re-embeds changed chunks
  - ⇒ a model change invalidates every key
- Keep the original text and metadata next to the vector
  - ⇒ enables re-embedding, citations, and filters
- Measure recall@k on a labeled query set before and after every knob change
- Filter inside the Approximate Nearest Neighbor (ANN) search (efficient filtering), not after
  - ⇒ post-filtering can return fewer than k results

## 4. Store Comparison

The deciding variable is steady query rate vs idle cost.

**Managed Amazon Web Services (AWS) stores**

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| OpenSearch Serverless (vector) | Managed OpenSearch, OCU-billed, HNSW/faiss | Knowledge Base (KB) quick-create default; hybrid + filters; no cluster ops | Min OpenSearch Compute Units (OCUs) billed idle (pricing page); fewer index knobs | Default for Bedrock KB; need hybrid |
| OpenSearch Service (domain) | Your cluster with the k-Nearest Neighbors (k-NN) plugin | Full control: shards, engines, on_disk, IVF, Index State Management (ISM) | You size and operate nodes, Java Virtual Machine (JVM), shards | Very large or tuned workloads |
| Aurora PostgreSQL + pgvector | Postgres extension, HNSW / IVFFlat | Vectors next to relational data; Structured Query Language (SQL) joins; transactions | Index must fit memory; behind dedicated engines at large N | Postgres already holds the data |
| Simple Storage Service (S3) Vectors | S3 vector buckets + indexes | Lowest storage cost; no cluster; KB-supported | Higher latency; no Best Matching 25 (BM25) hybrid; check quotas | Large, rarely queried corpora |

**Specialized and external**

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| Pinecone | Software as a Service (SaaS) vector Database (DB) (serverless) | Mature Application Programming Interface (API), namespaces, hybrid sparse-dense | Data leaves AWS account boundary; separate vendor | Multi-cloud teams already on Pinecone |
| Neptune Analytics | In-memory graph + vector search | GraphRAG: entities + relations + vectors | Graph modeling effort; memory-priced | Multi-hop questions over linked entities |
| MemoryDB (Valkey/Redis) | In-memory DB with vector search | Single-digit ms latency, high Queries Per Second (QPS) | All in Random-Access Memory (RAM) ⇒ most expensive per gigabyte (GB) | Semantic cache, real-time recs |
| Facebook Artificial Intelligence Similarity Search (FAISS) in process | Library, no server | Free, fastest on a single node | No durability, replication, filters, auth | Prototypes, offline batch, edge |

- **Default**: OpenSearch Serverless behind a Bedrock Knowledge Base, unless
  - the data already lives in Postgres and the corpus is modest ⇒ pgvector
  - the corpus is large and queried rarely ⇒ S3 Vectors
  - latency must be single-digit ms ⇒ MemoryDB
- **Deciding variable**: steady query rate vs idle cost
  - Low, spiky traffic ⇒ idle OCU floor dominates ⇒ S3 Vectors or pgvector
  - High traffic + hybrid ⇒ OpenSearch

Pick: OpenSearch Serverless, unless traffic is low and spiky.

## 5. Failure Modes

Most failures are silent quality drops, not errors.

**Quality failures**

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Garbage similarity | Index and query use different model / dims / input_type | Scores near random; recall collapses after deploy | Pin model config; store with index; re-embed on change |
| Exact terms missed | Pure vector search on Identifiers (IDs), codes, names | Eval set: identifier queries fail | Hybrid BM25 + vector; metadata fields |
| Fewer than k results | Post-filter after ANN with selective filter | Result count < k | In-graph filtering; exact search on small sets |
| Recall drop at scale | `ef_search` / `n_probe` tuned on small index | recall@k on golden set falls as N grows | Re-sweep; raise `ef_search`; rebuild with higher `m` |

**Operational failures**

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Out Of Memory (OOM) / circuit breaker | HNSW graph exceeds native memory | k-NN breaker trips, indexing rejected | Quantize, fewer dims, on_disk, bigger nodes |
| Stale answers | Source changed, index not resynced | Citations point to old versions | Event or scheduled sync ([knowledge-bases](knowledge-bases.06freshness.md)) |
| Silent truncation | Chunk longer than model input limit | Token counts at limit; tail facts never retrieved | Chunk below limit; `truncate=NONE` |
| Throttling on ingest | Parallel embed calls exceed quota | `ThrottlingException` spikes | Adaptive retries, bounded workers, batch inference |
