# 02rag.01embeddings.04exact-vs-ann Exact k-Nearest Neighbors (kNN) vs Approximate Nearest Neighbor (ANN)

> Brute-force search is perfect but O(N·d); Approximate Nearest Neighbor (ANN) skips most vectors and trades recall for speed.

## Index

- [1. Exact k-Nearest Neighbors (kNN)](#1-exact-k-nearest-neighbors-knn)
- [2. ANN](#2-ann)
- [3. The Trade Triangle](#3-the-trade-triangle)
- [4. Measure Recall](#4-measure-recall)

## 1. Exact k-Nearest Neighbors (kNN)

Brute force compares the query with every vector and keeps the top k.

- **Recall** = 1.0 by definition
- **Cost** O(N·d)
  - 1M × 1024 ≈ 1G multiply-adds per query (order of magnitude)
- **Fine when**
  - Below ~10k–100k vectors
  - After a selective filter
    - OpenSearch switches to exact when few docs match
- **Other use**: ground truth when measuring an ANN index's recall

```python
# app/service/_02rag_01embeddings/similarity.py
class ExactVectorStore:
    def __init__(self, metric: Metric = Metric.COSINE) -> None:
        self.metric = metric
        self._rows: dict[str, VectorRecord] = {}

    def upsert(self, records: list[VectorRecord]) -> int:
        dims = {len(r.vector) for r in records} | {len(r.vector) for r in list(self._rows.values())[:1]}
        if len(dims) > 1:
            # Mixing models or dimensions in one index silently ruins similarity: fail loudly.
            raise ValueError(f"mixed dimensions in one store: {sorted(dims)}")
        for r in records:
            self._rows[r.id] = r
        return len(records)

    def query(self, vector: Vector, k: int, filter: MetadataFilter | None = None) -> list[SearchHit]:
        # Pre-filter then score: never returns fewer than k when k matches exist.
        scored = [
            SearchHit(id=r.id, score=score(self.metric, vector, r.vector), text=r.text, metadata=r.metadata)
            for r in self._rows.values()
            if _matches(r.metadata, filter)
        ]
        scored.sort(key=lambda h: h.score, reverse=True)
        return scored[:k]
```

```python
# app/domain/_02rag_01embeddings.py
class VectorStore(Protocol):  # every store adapter implements it (exact here, OpenSearch in 02rag.02)
    def upsert(self, records: list[VectorRecord]) -> int: ...

    def query(self, vector: Vector, k: int, filter: MetadataFilter | None = None) -> list[SearchHit]: ...

    def delete(self, ids: list[str]) -> int: ...
```

## 2. ANN

Approximate nearest neighbour builds a structure that skips most vectors.

- **Recall@k < 1.0**, tuned by search-time knobs
- **Definition**: recall@k = |ANN top-k ∩ exact top-k| / k
- **Families**: graph (Hierarchical Navigable Small World (HNSW)) and inverted file (IVF); see [05 HNSW and IVF](02rag.01embeddings.05hnsw-ivf.md)

```python
# app/service/_02rag_01embeddings/similarity.py
def recall_at_k(approx_ids: list[str], exact_ids: list[str]) -> float:
    """|approx top-k ∩ exact top-k| / k. The metric every ANN knob is tuned against."""
    if not exact_ids:
        return 1.0
    return len(set(approx_ids) & set(exact_ids)) / len(exact_ids)
```

## 3. The Trade Triangle

Recall, latency, and memory pull against each other.

- Recall ↔ latency ↔ memory
- Any knob that raises one lowers at least one other

## 4. Measure Recall

Tune ANN knobs on your own data, not by guessing.

→ sample real queries  
→ compute exact top-k as ground truth  
→ sweep `ef_search` / `n_probe`  
→ pick the cheapest setting that meets the recall target (often 0.95; order of magnitude)

```python
# app/service/_02rag_01embeddings/similarity.py
def recall_experiment(records, queries, k=10, n_lists=16, n_probes=None) -> list[RecallPoint]:
    exact = ExactVectorStore(Metric.COSINE)  # ground truth
    exact.upsert(records)
    ivf = IvfIndex(n_lists=n_lists)
    ivf.train([r.vector for r in records])
    ivf.add(records)
    points: list[RecallPoint] = []
    for n_probe in n_probes or [1, 2, 4, 8, n_lists]:
        recalls, scanned = [], 0
        for q in queries:
            truth = [h.id for h in exact.query(q, k)]
            hits, n_scanned = ivf.query(q, k, n_probe)
            recalls.append(recall_at_k([h.id for h in hits], truth))
            scanned += n_scanned
        points.append(RecallPoint(
            n_probe=n_probe,
            recall_at_k=sum(recalls) / len(recalls),
            fraction_scanned=scanned / (len(queries) * len(records)),  # latency / cost proxy
        ))
    return points
```

- **Catch**: recall depends on data distribution
  - Random uniform vectors (`random_unit_vectors`) are a pessimistic case
  - Run the sweep on your own data, not a benchmark
