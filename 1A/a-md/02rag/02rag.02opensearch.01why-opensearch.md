# 02rag.02opensearch.01why-opensearch Why OpenSearch for Vectors

> One engine holds inverted indexes and k-Nearest Neighbors (k-NN) graphs, so keyword and vector search share a write path.

## Index

- [1. The Pain And Prior Art](#1-the-pain-and-prior-art)
- [2. How OpenSearch Helps](#2-how-opensearch-helps)
- [3. Picture](#3-picture)
  - [3.1 Serverless Collection](#31-serverless-collection)
  - [3.2 Managed Domain](#32-managed-domain)
- [4. Write And Read Paths](#4-write-and-read-paths)
- [5. Use Cases And Limits](#5-use-cases-and-limits)

## 1. The Pain And Prior Art

Two engines mean two writes and fusion in application code.

- **The pain**
  - Separate keyword engine + vector Database (DB)
    - ⇒ two writes, two consistency stories, fusion in app code
- **Prior art**
  - Elasticsearch (2010) for full text
    - Forked as OpenSearch in 2021 (Apache 2.0)
  - Dedicated vector DBs (Milvus, Pinecone) without strong lexical search

## 2. How OpenSearch Helps

Lucene segments hold both index kinds; one request can search both.

- Lucene segments hold both inverted indexes and k-NN graph files
- The k-NN plugin loads native graphs (faiss) per segment into off-heap memory
- Hybrid query runs Best Matching 25 (BM25) and k-NN in one request
  - A search pipeline fuses scores ([06 Filtering and hybrid](02rag.02opensearch.06filtering-hybrid.md))

```python
# app/infra/_02rag_02opensearch.py
"settings": {
    "index": {
        "knn": True,  # turns on native k-NN structures for knn_vector fields
        "knn.algo_param.ef_search": ef_search,
    }
},
"mappings": {
    "properties": {
        c.vector_field: {"type": "knn_vector", "dimension": c.dimensions, "method": {...}},
        c.text_field: {"type": "text"},  # BM25-searchable chunk text, same document
    }
},
```

## 3. Picture

Two deployment forms wrap the same engine.

### 3.1 Serverless Collection

Amazon Web Services (AWS) runs separate indexing and search OpenSearch Compute Units (OCUs) over Simple Storage Service (S3)-backed storage.

```text
          ┌─ Serverless collection a-vectors (VECTORSEARCH) ─┐
app ─────►│ VPC endpoint ─► indexing OCUs ─► S3 storage      │◄─ KB
SigV4 aoss│                 search OCUs ◄─── S3 storage      │
via VPCE  │ encryption (CMK) · network · data-access policy  │
          └──────────────────────────────────────────────────┘
```

Notice that the app enters via the Virtual Private Cloud (VPC) endpoint, while Bedrock Knowledge Base (KB) enters via `SourceServices: bedrock`.

### 3.2 Managed Domain

You run masters and data nodes; each shard is a Lucene index.

```text
          ┌─ Managed domain ─────────────────────────────────┐
app ─────►│ 3 dedicated masters (cluster state, quorum)      │
SigV4 es  │ data nodes: primary + replica shards             │
          │   per segment: inverted index + k-NN graph (RAM) │
          │ UltraWarm (S3, read-only) · cold (detached)      │
          └──────────────────────────────────────────────────┘
```

Notice that the k-NN graph sits per segment, so merges rebuild graphs.

## 4. Write And Read Paths

A domain write becomes searchable only after a refresh.

**Write path (domain)**

→ coordinator routes doc to a primary shard by `_id` hash  
→ primary writes translog + in-memory buffer, replicates to replicas  
→ refresh (default 1 s) creates a searchable segment; k-NN graph built for it  
→ merges combine segments and rebuild graphs

**Read path**

→ query fans out to one copy of every shard  
→ each returns top k  
→ coordinator merges

```python
# app/infra/_02rag_02opensearch.py
def knn_query(vector: Vector, k: int = 5, ef_search: int | None = None) -> list[SearchHit]:
    c = contract()
    knn: dict[str, Any] = {"vector": vector, "k": k}  # k = neighbours per segment/shard
    if ef_search:
        knn["method_parameters"] = {"ef_search": ef_search}
    body = {"size": k,  # size = hits returned after the coordinator merge
            "query": {"knn": {c.vector_field: knn}},
            "_source": {"excludes": [c.vector_field]}}
    return _hits(opensearch_client().search(index=c.index_name, body=body))
```

## 5. Use Cases And Limits

OpenSearch fits Retrieval-Augmented Generation (RAG), product search, and log analytics.

- **Common use cases**
  - RAG store behind Bedrock KB
  - Semantic + keyword product search
  - Log analytics (the original workload), now with semantic search on top
- **Limits**
  - Segment-level graphs ⇒ heavy updates/deletes need merges, cost Central Processing Unit (CPU)
  - Billion-scale low-latency needs careful memory planning
    - Quantization, on_disk ([04 k-NN plugin](02rag.02opensearch.04knn-plugin.md))
