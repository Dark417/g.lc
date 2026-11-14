# 02rag.01embeddings.05hnsw-ivf Hierarchical Navigable Small World (HNSW) and Inverted File Index (IVF)

> The two Approximate Nearest Neighbor (ANN) families: a layered proximity graph (Hierarchical Navigable Small World (HNSW)) and k-means cells (Inverted File Index (IVF)).

## Index

- [1. HNSW](#1-hnsw)
  - [1.1 Mechanism](#11-mechanism)
  - [1.2 Knobs](#12-knobs)
  - [1.3 Strengths And Costs](#13-strengths-and-costs)
- [2. IVF](#2-ivf)
  - [2.1 Mechanism And Knobs](#21-mechanism-and-knobs)
  - [2.2 Strengths And Costs](#22-strengths-and-costs)
- [3. Default Choice](#3-default-choice)

## 1. HNSW

Hierarchical Navigable Small World graph (Malkov & Yashunin, 2016).

### 1.1 Mechanism

Every vector is a node linked to its nearest neighbours, in layers.

- Layer 0 holds all nodes
- Each higher layer holds an exponentially smaller random subset

**Search**

→ enter at the top layer, greedy walk toward the query  
→ drop one layer, continue from the best node  
→ at layer 0, run a beam search of width `ef_search`  
→ return the best k from the beam

### 1.2 Knobs

Three knobs: two at build time, one at query time.

- **`m`**: max links per node (layer 0 uses 2m)
  - Higher ⇒ better recall, more memory, slower build
  - OpenSearch default 16
- **`ef_construction`**: beam width while inserting
  - Higher ⇒ better graph, slower indexing
  - OpenSearch default 100
- **`ef_search`**: beam width at query time
  - Higher ⇒ higher recall, higher latency
  - Tunable per query (OpenSearch 2.16+ `method_parameters`)

The repo builds HNSW only through OpenSearch; see [02rag.02opensearch.04knn-plugin](02rag.02opensearch.04knn-plugin.md).

```python
# app/infra/_02rag_02opensearch.py
"method": {
    "name": "hnsw",
    "engine": "faiss",
    "space_type": "l2",
    "parameters": {"m": m, "ef_construction": ef_construction},  # build-time knobs
},
# index setting "knn.algo_param.ef_search": query beam (default 100)
```

### 1.3 Strengths And Costs

HNSW wins on recall and latency, and pays in memory.

- **Strengths**
  - High recall at low latency
  - No training step
  - Incremental inserts
- **Costs**
  - Graph lives in memory
    - faiss HNSW ≈ 1.1 × (4·d + 8·m) bytes per vector (OpenSearch k-Nearest Neighbors (k-NN) sizing doc)
  - Deletes leave tombstones until segments merge
  - Builds are Central Processing Unit (CPU)-heavy ⇒ bulk loads are slow

```python
# app/service/_02rag_01embeddings/similarity.py
def hnsw_memory_bytes(n_vectors: int, dims: int, m: int = 16) -> int:
    """OpenSearch k-NN sizing rule for faiss HNSW float32: 1.1 * (4*d + 8*m) bytes per vector.

    Example: 1M x 1024 dims, m=16 -> ~4.6 GB of native (off-heap) memory.
    """
    return int(1.1 * (4 * dims + 8 * m) * n_vectors)
```

## 2. IVF

Inverted File index (faiss): partition the space, scan only nearby cells.

### 2.1 Mechanism And Knobs

k-means centroids define the cells.

→ train k-means on a sample to get `nlist` centroids  
→ assign each vector to its nearest centroid's list  
→ at query time, scan only the `nprobes` closest lists

- **`nlist`**: more lists = smaller lists = faster scan
  - But more misses at the cell borders
- **`nprobes`**: more lists scanned = higher recall, higher latency
  - `n_probe = n_lists` degenerates to exact search

```python
# app/service/_02rag_01embeddings/similarity.py
class IvfIndex:
    def train(self, sample: list[Vector]) -> None:
        """Lloyd's k-means. Real IVF trains on ~30-256 points per list (order of magnitude)."""
        if len(sample) < self.n_lists:
            raise ValueError("need at least n_lists training vectors")
        self.centroids = [list(v) for v in self._rng.sample(sample, self.n_lists)]
        dims = len(sample[0])
        for _ in range(self.iterations):
            buckets: list[list[Vector]] = [[] for _ in range(self.n_lists)]
            for v in sample:
                buckets[self._nearest_centroids(v, 1)[0]].append(v)
            for i, members in enumerate(buckets):
                if members:  # empty cell keeps its old centroid
                    self.centroids[i] = [sum(m[d] for m in members) / len(members) for d in range(dims)]
        self.lists = [[] for _ in range(self.n_lists)]

    def add(self, records: list[VectorRecord]) -> None:
        if not self.centroids:
            raise RuntimeError("train() before add(): IVF needs centroids")
        for r in records:
            self.lists[self._nearest_centroids(r.vector, 1)[0]].append(r)

    def query(self, vector: Vector, k: int, n_probe: int) -> tuple[list[SearchHit], int]:
        """Returns (hits, vectors_scanned)."""
        candidates = [r for i in self._nearest_centroids(vector, n_probe) for r in self.lists[i]]
        hits = [SearchHit(id=r.id, score=score(self.metric, vector, r.vector), text=r.text) for r in candidates]
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:k], len(candidates)
```

### 2.2 Strengths And Costs

IVF saves memory and needs training.

- **Strengths**
  - Less memory than HNSW (no graph)
  - Pairs well with Product Quantization (PQ) (IVF-PQ) for billions of vectors
- **Costs**
  - Needs a training step on representative data
    - OpenSearch: a separate train Application Programming Interface (API) + model
  - Centroids drift when the data distribution changes
    - ⇒ retrain and reindex

## 3. Default Choice

Pick by the binding constraint.

- **Default**: HNSW
- **Unless** memory is the binding constraint at very large N
  - ⇒ IVF(-PQ) or disk-based modes ([06 Quantization](02rag.01embeddings.06quantization.md))
