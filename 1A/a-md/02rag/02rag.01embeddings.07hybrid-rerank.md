# 02rag.01embeddings.07hybrid-rerank Hybrid Search and Reranking

> Fuse lexical and vector retrieval, then sharpen the top results with a cross-encoder.

## Index

- [1. Hybrid Search](#1-hybrid-search)
- [2. Reranking](#2-reranking)
- [3. Default](#3-default)

## 1. Hybrid Search

Hybrid = lexical (Best Matching 25 (BM25)) + vector, fused into one ranking.

- **Why both**
  - BM25 catches exact tokens
  - Vectors catch paraphrase
- **Fusion options**
  - Score normalization (min-max or L2) + weighted arithmetic mean
    - OpenSearch normalization processor
  - **Reciprocal Rank Fusion (RRF)** (reciprocal rank fusion): score = Σ 1 / (60 + rank)
    - Rank-based, no score scaling
- **Bedrock Knowledge Base (KB)**: `overrideSearchType = HYBRID`
  - Store support varies ([02rag.04knowledge-bases.03retrieve](02rag.04knowledge-bases.03retrieve.md))

The repo's hybrid call lives in OpenSearch ([02rag.02opensearch.06filtering-hybrid](02rag.02opensearch.06filtering-hybrid.md)).

```python
# app/infra/_02rag_02opensearch.py
body = {
    "size": k,
    # sub-query order = weight order in the normalization pipeline (lexical first)
    "query": {"hybrid": {"queries": [lexical, {"knn": {c.vector_field: knn}}]}},
    "_source": {"excludes": [c.vector_field]},
}
```

```python
# illustrative: RRF over two ranked id lists
def rrf(rankings: list[list[str]], rank_constant: int = 60) -> list[str]:
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (rank_constant + rank)
    return sorted(scores, key=scores.get, reverse=True)
```

- **Catch**: BM25 scores are unbounded; cosine is bounded
  - ⇒ normalize before a weighted mean, or use rank-based RRF

## 2. Reranking

A second stage that scores each (query, chunk) pair jointly.

→ retrieve a wide candidate set (e.g. 50)  
→ a cross-encoder scores each (query, chunk) pair jointly  
→ keep the top few (e.g. 5)

- **Bedrock**: Rerank Application Programming Interface (API) or KB `rerankingConfiguration`
  - Models: `amazon.rerank-v1:0`, `cohere.rerank-v3-5:0`
- **Cost**: one model call per candidate batch
  - +latency, hundreds of ms (order of magnitude)

```python
# app/infra/_02rag_04knowledge_bases.py
if rerank:
    vsc["numberOfResults"] = min(100, n * 5)  # wide candidate set for the reranker
    vsc["rerankingConfiguration"] = {
        "type": "BEDROCK_RERANKING_MODEL",
        "bedrockRerankingConfiguration": {
            "modelConfiguration": {"modelArn": s.rerank_model_arn},
            "numberOfRerankedResults": n,  # keep the top n after rescoring
            "metadataConfiguration": {"selectionMode": "ALL"},
        },
    }
```

## 3. Default

Hybrid + rerank is the production default for mixed content.

- **Default**: hybrid + rerank for production Question and Answer (Q&A) over mixed prose and identifiers
- **Unless** the latency budget is tight
