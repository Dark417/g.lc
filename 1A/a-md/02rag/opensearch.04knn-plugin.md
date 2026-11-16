# opensearch.04knn-plugin k-Nearest Neighbors (k-NN) Plugin

> Engines, methods, space types, Hierarchical Navigable Small World (HNSW) and Inverted File Index (IVF) parameters, disk-based vectors, and memory sizing.

## Index

- [1. Engines](#1-engines)
- [2. Space Types And Method Parameters](#2-space-types-and-method-parameters)
- [3. Disk-Based Vectors](#3-disk-based-vectors)
- [4. Memory Sizing](#4-memory-sizing)

## 1. Engines

The engine decides which methods and encoders are available.

| Engine | Methods | Strength | Note |
|---|---|---|---|
| faiss | hnsw, ivf | Large scale, fp16 / Product Quantization (PQ) encoders, efficient filtering (2.9+) | Required by Bedrock Knowledge Base (KB) on Serverless |
| lucene | hnsw | Smaller indexes, efficient filtering, byte vectors | Up to tens of millions of vectors (order of magnitude) |
| nmslib | hnsw | Historical default | Deprecated; blocked for new indexes in OpenSearch 3.0 |

Pick: faiss, unless the index is small and lucene's byte vectors suffice.

## 2. Space Types And Method Parameters

The vector field declares the metric and the Approximate Nearest Neighbor (ANN) method.

- **`space_type`**: `l2`, `innerproduct`, `cosinesimil`, `l1`, `linf`, `hamming` (binary vectors)
  - Titan V2 output is normalized ⇒ `l2` and `innerproduct` rank identically
- **HNSW parameters**
  - `m` (default 16): links per node
  - `ef_construction` (default 100): build beam
  - `ef_search` (index setting default 100): query beam
    - Per query via `method_parameters` (2.16+)
- **IVF parameters**: `nlist`, `nprobes`
  - Needs the train Application Programming Interface (API) and a stored model (faiss only, managed domains)
- Mechanism of both: [embeddings.05hnsw-ivf](embeddings.05hnsw-ivf.md)

```python
# app/infra/_02rag_02opensearch.py
def kb_index_body(ef_search: int = 512, m: int = 16, ef_construction: int = 512) -> dict[str, Any]:
    c = contract()
    return {
        "settings": {"index": {"knn": True, "knn.algo_param.ef_search": ef_search}},
        "mappings": {"properties": {
            c.vector_field: {
                "type": "knn_vector",
                "dimension": c.dimensions,
                "method": {
                    "name": "hnsw",  # ivf: faiss only, needs a train step + model
                    "engine": "faiss",  # KB requirement on AOSS
                    "space_type": "l2",  # normalized Titan V2: same ranking as innerproduct
                    "parameters": {"m": m, "ef_construction": ef_construction},
                },
            },
            ...
        }},
    }
```

- **Binary embeddings**: KB `embedding_data_type BINARY`
  - ⇒ `"data_type": "binary"` + `space_type` `hamming`

## 3. Disk-Based Vectors

Managed domains (2.17+) can keep quantized vectors in Random-Access Memory (RAM) and full ones on disk.

- `mode: on_disk` + `compression_level`
  - `1x` | `2x` (fp16) | `4x` (byte) | `8x` | `16x` | `32x` (binary)
  - on_disk defaults to 32x
- Quantized vectors in RAM for the first pass
- Full precision on disk for rescoring
- **Trade**: ~32x less RAM for extra latency
  - Order of magnitude: tens of ms more
- Mechanism: [embeddings.06quantization](embeddings.06quantization.md)

```python
# app/infra/_02rag_02opensearch.py
def on_disk_vector_field(dimensions: int, compression: str = "32x") -> dict[str, Any]:
    """Managed domains, OpenSearch 2.17+. Check AOSS support before using."""
    return {
        "type": "knn_vector",
        "dimension": dimensions,
        "space_type": "innerproduct",
        "mode": "on_disk",  # quantized in memory, full precision on disk for rescoring
        "compression_level": compression,
    }
```

## 4. Memory Sizing

Graph memory, not disk, sizes a k-Nearest Neighbors (k-NN) cluster.

- faiss HNSW: 1.1 × (4·d + 8·m) bytes per vector (k-NN docs)
  - ⇒ 1M × 1024 dims ≈ 4.6 gigabytes (GB)
- Code: `hnsw_memory_bytes` in [embeddings.05hnsw-ivf](embeddings.05hnsw-ivf.md)
- **Catch**: graphs exceeding native memory trip the k-NN circuit breaker
  - See [02 Managed domains](opensearch.02managed-domains.md)
