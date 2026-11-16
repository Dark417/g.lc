# opensearch.06filtering-hybrid Filtering and Hybrid Queries

> Put filters inside the knn clause, and fuse Best Matching 25 (BM25) with k-Nearest Neighbors (k-NN) through a normalization pipeline.

## Index

- [1. Post-Filtering](#1-post-filtering)
- [2. Efficient Filtering](#2-efficient-filtering)
- [3. Hybrid Query](#3-hybrid-query)
  - [3.1 Pipeline](#31-pipeline)
  - [3.2 Query](#32-query)
- [4. VectorStore Adapter](#4-vectorstore-adapter)

## 1. Post-Filtering

A filter outside the knn clause runs after Approximate Nearest Neighbor (ANN).

- Shape: `bool { must: knn, filter: … }`
- ANN returns k, then the filter drops some
  - ⇒ fewer than k results, sometimes zero

## 2. Efficient Filtering

Put the filter inside the `knn` clause and let the engine choose per query.

- Few matches ⇒ exact search over them
- Many matches ⇒ filtered graph traversal
- Supported by faiss (2.9+) and lucene (2.4+)

```python
# app/infra/_02rag_02opensearch.py
def metadata_filter_clause(flt: MetadataFilter) -> dict[str, Any]:
    """{"dept": "hr", "year": 2025, "tags": ["a", "b"]} → bool filter."""
    terms: list[dict[str, Any]] = []
    for k, v in flt.items():
        if isinstance(v, list):
            field = f"{k}.keyword" if v and isinstance(v[0], str) else k
            terms.append({"terms": {field: v}})
        else:
            # strings match the .keyword sub-field created by dynamic mapping
            terms.append({"term": {f"{k}.keyword" if isinstance(v, str) else k: v}})
    return {"bool": {"filter": terms}}


def filtered_knn_query(vector: Vector, flt: MetadataFilter, k: int = 5) -> list[SearchHit]:
    c = contract()
    body = {
        "size": k,
        # filter INSIDE knn = efficient filtering; outside would be post-filtering
        "query": {"knn": {c.vector_field: {"vector": vector, "k": k, "filter": metadata_filter_clause(flt)}}},
        "_source": {"excludes": [c.vector_field]},  # never return ~4 KB of floats per hit
    }
    return _hits(opensearch_client().search(index=c.index_name, body=body))
```

- **Catch**: for tenant isolation at scale, also consider index-per-tenant
  - Avoids noisy neighbours

## 3. Hybrid Query

Lexical match + k-NN in one request, fused by a search pipeline.

→ `hybrid.queries = [match(text), knn(embedding)]`  
→ search pipeline `normalization-processor`: `min_max` (or `l2`) normalization  
→ combination `arithmetic_mean` with weights in sub-query order (e.g. 0.3 lexical, 0.7 vector)

- **Reciprocal Rank Fusion (RRF) alternative**: `score-ranker-processor` (2.19+)
  - Rank-based, no weights
- **Support**: managed domains support search pipelines (2.10+)
  - Serverless: verify on your collection
- Fusion math: [embeddings.07hybrid-rerank](embeddings.07hybrid-rerank.md)

### 3.1 Pipeline

The pipeline puts BM25 (unbounded) and k-NN scores on one scale.

```python
# app/infra/_02rag_02opensearch.py
def create_hybrid_pipeline(lexical_weight: float = 0.3, vector_weight: float = 0.7) -> dict[str, Any]:
    body = {
        "description": "BM25 + k-NN hybrid for the KB index",
        "phase_results_processors": [{
            "normalization-processor": {
                "normalization": {"technique": "min_max"},  # min_max (default) | l2
                "combination": {
                    "technique": "arithmetic_mean",  # | geometric_mean | harmonic_mean
                    "parameters": {"weights": [lexical_weight, vector_weight]},  # sub-query order
                },
            }
        }],
    }
    # Alternative (2.19+): "score-ranker-processor" with
    # {"combination": {"technique": "rrf", "rank_constant": 60}}
    return opensearch_client().search_pipeline.put(id=get_opensearch_settings().search_pipeline, body=body)
```

### 3.2 Query

Use hybrid when queries mix identifiers (Stock Keeping Units (SKUs), error codes) and natural language.

```python
# app/infra/_02rag_02opensearch.py
def hybrid_query(text: str, vector: Vector, k: int = 5, flt: MetadataFilter | None = None) -> list[SearchHit]:
    c = contract()
    knn: dict[str, Any] = {"vector": vector, "k": k}
    lexical: dict[str, Any] = {"match": {c.text_field: {"query": text}}}
    if flt:  # same filter on both sub-queries
        knn["filter"] = metadata_filter_clause(flt)
        lexical = {"bool": {"must": [lexical], "filter": metadata_filter_clause(flt)["bool"]["filter"]}}
    body = {
        "size": k,
        "query": {"hybrid": {"queries": [lexical, {"knn": {c.vector_field: knn}}]}},
        "_source": {"excludes": [c.vector_field]},
    }
    resp = opensearch_client().search(
        index=c.index_name, body=body,
        params={"search_pipeline": get_opensearch_settings().search_pipeline},  # required
    )
    return _hits(resp)
```

- **Catch**: without `?search_pipeline`, the hybrid query errors or returns un-normalized scores
  - ⇒ BM25 dominates the ranking

## 4. VectorStore Adapter

The same port as the exact store, so callers can swap stores.

```python
# app/infra/_02rag_02opensearch.py
class OpenSearchVectorStore:
    def query(self, vector: Vector, k: int, filter: MetadataFilter | None = None) -> list[SearchHit]:
        return filtered_knn_query(vector, filter, k) if filter else knn_query(vector, k)

    def delete(self, ids: list[str]) -> int:
        return bulk_delete(ids)
```

- Port definition: [embeddings.04exact-vs-ann](embeddings.04exact-vs-ann.md)
  - Defined again locally in `app/domain/_02rag_02opensearch.py` so components stay independent
