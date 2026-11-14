# 02rag.01embeddings.03similarity-metrics Similarity Metrics

> Cosine, dot product, and L2, and why normalizing once makes them rank identically.

## Index

- [1. The Three Metrics](#1-the-three-metrics)
- [2. Why Normalize](#2-why-normalize)
- [3. Engine Names And Choosing](#3-engine-names-and-choosing)

## 1. The Three Metrics

Each metric compares two vectors; they differ in whether magnitude counts.

| Metric | Formula | Range | Note |
|---|---|---|---|
| Cosine | a·b / (‖a‖‖b‖) | [-1, 1] | angle only; magnitude ignored |
| Dot (inner product) | a·b | unbounded | = cosine on unit vectors; cheapest |
| L2 (Euclidean) | ‖a − b‖ | [0, ∞), smaller = closer | unit vectors: d² = 2 − 2·cos ⇒ cosine ranking |

```python
# app/service/_02rag_01embeddings/similarity.py
def dot(a: Vector, b: Vector) -> float:
    """Cheapest metric. Equals cosine only when both vectors are unit length."""
    if len(a) != len(b):
        raise ValueError(f"dimension mismatch: {len(a)} vs {len(b)}")
    return sum(x * y for x, y in zip(a, b))


def cosine(a: Vector, b: Vector) -> float:
    # needs two norms per pair unless pre-normalized
    return dot(a, b) / (norm(a) * norm(b))


def l2_distance(a: Vector, b: Vector) -> float:
    # On unit vectors: d^2 = 2 - 2*cos, so the ranking equals cosine ranking.
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
```

## 2. Why Normalize

Unit vectors remove magnitude from the comparison.

- Unit vectors make all three metrics rank identically
- Then the store can use dot product (no norms at query time)
- Unnormalized + dot ⇒ long vectors win regardless of meaning

```python
# app/service/_02rag_01embeddings/similarity.py
def normalize(a: Vector) -> Vector:
    """Scale to unit length. Do it once at write time so query-time scoring can use plain dot."""
    n = norm(a)
    if n == 0.0:
        raise ValueError("cannot normalize a zero vector")
    return [x / n for x in a]
```

## 3. Engine Names And Choosing

Stores name the metrics differently and transform scores differently.

- **OpenSearch names**: `cosinesimil`, `innerproduct`, `l2` ([02rag.02opensearch.04knn-plugin](02rag.02opensearch.04knn-plugin.md))
- **Score transforms differ**: `1/(1+d)` for L2
- **Rule**: use the metric the model was trained for (model card)
  - For Titan V2 normalized, any of the three works

```python
# app/domain/_02rag_01embeddings.py
class Metric(StrEnum):
    COSINE = "cosine"  # angle only; magnitude ignored
    DOT = "dot"  # angle x magnitudes; == cosine when vectors are unit length
    L2 = "l2"  # Euclidean distance; smaller = closer; same ranking as cosine on unit vectors
```

```python
# app/service/_02rag_01embeddings/similarity.py
def score(metric: Metric, a: Vector, b: Vector) -> float:
    """Unified 'higher is better' score."""
    if metric is Metric.COSINE:
        return cosine(a, b)
    if metric is Metric.DOT:
        return dot(a, b)
    return 1.0 / (1.0 + l2_distance(a, b))  # same transform OpenSearch k-NN uses
```

- **Catch**: a dimension mismatch raises in the repo code
  - Real stores may reject or silently misbehave ⇒ pin model + dims with the index
