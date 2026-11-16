# embeddings.06quantization Quantization

> Store fewer bits per dimension, accept some recall loss, and recover it by rescoring.

## Index

- [1. Schemes](#1-schemes)
- [2. Memory Math](#2-memory-math)
- [3. Binary Quantization](#3-binary-quantization)
- [4. Product Quantization](#4-product-quantization)
- [5. Limit](#5-limit)

## 1. Schemes

Each scheme shrinks the vector by a fixed factor at a recall cost.

| Scheme | Bytes / 1024-dim | Shrink | Recall cost | Where |
|---|---|---|---|---|
| float32 | 4,096 | 1x | none | default |
| float16 (scalar) | 2,048 | 2x | negligible (order of magnitude) | faiss `sq fp16` |
| int8 / byte (scalar) | 1,024 | 4x | small | lucene Scalar Quantization (SQ), faiss `sq`, Cohere int8 |
| binary (1 bit / dim) | 128 | 32x | large unless rescored | OpenSearch `on_disk` 32x, Titan V2 `binary` |
| Product Quantization (PQ) (m=64 codes) | 64 | 64x | medium–large, data dependent | faiss `pq`, Inverted File Index (IVF)-PQ |

```python
# app/domain/_02rag_01embeddings.py
class QuantScheme(StrEnum):
    FLOAT32 = "float32"  # 4 B / dim
    FLOAT16 = "float16"  # 2 B / dim (scalar quantization, near-lossless)
    INT8 = "int8"  # 1 B / dim (scalar / byte quantization)
    BINARY = "binary"  # 1 bit / dim (sign), needs rescoring for good recall
    PQ = "pq"  # product quantization: m sub-vectors x 1 B code each
```

## 2. Memory Math

Size the store before picking a tier (1M vectors × 1024 dims, order of magnitude).

- float32 ≈ 4 gigabytes (GB)
- Hierarchical Navigable Small World (HNSW) total ≈ 4.6 GB
- binary ≈ 128 megabytes (MB) ⇒ fits in a small node's Random-Access Memory (RAM)

```python
# app/service/_02rag_01embeddings/similarity.py
def vector_memory_bytes(n_vectors: int, dims: int, scheme: QuantScheme, pq_m: int = 64) -> int:
    """Raw vector bytes only (no graph)."""
    per_vector = {
        QuantScheme.FLOAT32: 4 * dims,
        QuantScheme.FLOAT16: 2 * dims,
        QuantScheme.INT8: dims,
        QuantScheme.BINARY: math.ceil(dims / 8),
        QuantScheme.PQ: pq_m,  # one 8-bit code per sub-vector
    }[scheme]
    return n_vectors * per_vector
```

## 3. Binary Quantization

Keep one sign bit per dimension and compare with Hamming distance.

→ keep the sign bit of each dimension  
→ distance = Hamming = popcount(a Exclusive OR (XOR) b)  
→ shortlist k × oversample candidates  
→ rescore the shortlist with full-precision vectors (kept on disk)

- **Oversample** is the recall knob (2–10x typical, order of magnitude)
- **Production forms**
  - OpenSearch `on_disk` mode ([opensearch.04knn-plugin](opensearch.04knn-plugin.md))
  - Titan V2 `embeddingTypes=["binary"]` + float

```python
# app/service/_02rag_01embeddings/similarity.py
def binary_quantize(vector: Vector) -> int:
    """Sign bit per dimension packed into one int: 1024 floats (4 KiB) -> 128 B = 32x smaller."""
    bits = 0
    for i, x in enumerate(vector):
        if x > 0:
            bits |= 1 << i
    return bits


def hamming(a: int, b: int) -> int:
    """Differing bits: XOR + popcount, one CPU instruction per 64 dims."""
    return (a ^ b).bit_count()


def binary_search_with_rescore(records, query: Vector, k: int, oversample: int = 4) -> list[SearchHit]:
    q_bits = binary_quantize(query)
    codes = [(r, binary_quantize(r.vector)) for r in records]  # a real index stores codes
    codes.sort(key=lambda rc: hamming(q_bits, rc[1]))
    shortlist = [r for r, _ in codes[: k * oversample]]  # phase 1: Hamming shortlist
    hits = [SearchHit(id=r.id, score=cosine(query, r.vector), text=r.text) for r in shortlist]
    hits.sort(key=lambda h: h.score, reverse=True)  # phase 2: exact cosine rescoring
    return hits[:k]
```

- **Catch**: binary throws away magnitude
  - Recall drops, so production systems rescore the top candidates

## 4. Product Quantization

PQ compresses each sub-vector to one centroid id.

→ split the vector into m sub-vectors  
→ k-means each sub-space into 256 centroids  
→ store one byte (centroid id) per sub-vector

- Repo code covers only PQ memory math (`QuantScheme.PQ`), not the encoding

## 5. Limit

Quantization is a recall-for-memory trade.

- Measure recall@k after every change ([04 Exact vs Approximate Nearest Neighbor (ANN)](embeddings.04exact-vs-ann.md))
