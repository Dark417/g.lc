"""Vector math and search mechanics, pure Python (no numpy: the point is to read the mechanism).

Order follows docs/02.01.embeddings-vector-search.md:
  similarity metrics -> exact kNN store -> ANN (IVF) + recall@k -> binary quantization -> memory math.
Real stores do the same work in C++ / SIMD; these functions are for small tests and for intuition.
"""

import math
import random

from app.a02_01_embeddings.domain import (
    MetadataFilter,
    Metric,
    QuantScheme,
    RecallPoint,
    SearchHit,
    Vector,
    VectorRecord,
)

# ================================================================ similarity metrics


def dot(a: Vector, b: Vector) -> float:
    """Dot product: cheapest metric. Equals cosine only when both vectors are unit length."""
    if len(a) != len(b):
        raise ValueError(f"dimension mismatch: {len(a)} vs {len(b)}")
    return sum(x * y for x, y in zip(a, b))


def norm(a: Vector) -> float:
    return math.sqrt(dot(a, a))


def normalize(a: Vector) -> Vector:
    """Scale to unit length. Do it once at write time so query-time scoring can use plain dot."""
    n = norm(a)
    if n == 0.0:
        raise ValueError("cannot normalize a zero vector")
    return [x / n for x in a]


def cosine(a: Vector, b: Vector) -> float:
    """Cosine similarity in [-1, 1]: angle only. Catch: needs two norms per pair unless pre-normalized."""
    return dot(a, b) / (norm(a) * norm(b))


def l2_distance(a: Vector, b: Vector) -> float:
    """Euclidean distance. On unit vectors: d^2 = 2 - 2*cos, so the ranking equals cosine ranking."""
    if len(a) != len(b):
        raise ValueError(f"dimension mismatch: {len(a)} vs {len(b)}")
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def score(metric: Metric, a: Vector, b: Vector) -> float:
    """Unified 'higher is better' score. L2 uses 1 / (1 + d), the same transform OpenSearch k-NN uses."""
    if metric is Metric.COSINE:
        return cosine(a, b)
    if metric is Metric.DOT:
        return dot(a, b)
    return 1.0 / (1.0 + l2_distance(a, b))


# ================================================================ exact kNN store (VectorStore adapter)


def _matches(metadata: dict[str, object], flt: MetadataFilter | None) -> bool:
    return flt is None or all(metadata.get(k) == v for k, v in flt.items())


class ExactVectorStore:
    """Brute-force VectorStore: compares the query with every vector, so recall is 1.0 by definition.

    When to use: tests, < ~10k vectors, and as the ground truth when measuring an ANN index's recall.
    Catch: O(N * d) per query; at 1M x 1024 dims that is ~1G multiply-adds per query (order of magnitude).
    """

    def __init__(self, metric: Metric = Metric.COSINE) -> None:
        self.metric = metric
        self._rows: dict[str, VectorRecord] = {}

    def upsert(self, records: list[VectorRecord]) -> int:
        dims = {len(r.vector) for r in records} | {len(r.vector) for r in list(self._rows.values())[:1]}
        if len(dims) > 1:
            # Mixing models or dimensions in one index silently ruins similarity: fail loudly instead.
            raise ValueError(f"mixed dimensions in one store: {sorted(dims)}")
        for r in records:
            self._rows[r.id] = r
        return len(records)

    def query(self, vector: Vector, k: int, filter: MetadataFilter | None = None) -> list[SearchHit]:
        # Pre-filter then score: exact filtering never returns fewer than k when k matches exist.
        scored = [
            SearchHit(id=r.id, score=score(self.metric, vector, r.vector), text=r.text, metadata=r.metadata)
            for r in self._rows.values()
            if _matches(r.metadata, filter)
        ]
        scored.sort(key=lambda h: h.score, reverse=True)
        return scored[:k]

    def delete(self, ids: list[str]) -> int:
        return sum(1 for i in ids if self._rows.pop(i, None) is not None)

    def __len__(self) -> int:
        return len(self._rows)


# ================================================================ ANN: IVF (inverted file) + recall@k


class IvfIndex:
    """Minimal IVF: k-means partitions the space into n_lists cells; a query scans only n_probe cells.

    Shows the ANN trade-off: fewer probed cells = less work = lower recall.
    Catch: needs a training pass on representative data; centroids drift as data changes (retrain / reindex).
    HNSW (graph) is the other family; it is what Bedrock KB indexes use by default (see 02.02).
    """

    def __init__(self, n_lists: int, metric: Metric = Metric.COSINE, iterations: int = 8, seed: int = 7) -> None:
        self.n_lists = n_lists
        self.metric = metric
        self.iterations = iterations
        self._rng = random.Random(seed)
        self.centroids: list[Vector] = []
        self.lists: list[list[VectorRecord]] = []

    def _nearest_centroids(self, v: Vector, n: int) -> list[int]:
        ranked = sorted(range(len(self.centroids)), key=lambda i: score(self.metric, v, self.centroids[i]), reverse=True)
        return ranked[:n]

    def train(self, sample: list[Vector]) -> None:
        """Lloyd's k-means on a sample. Real IVF trains on ~30-256 points per list (order of magnitude)."""
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
        """Returns (hits, vectors_scanned). n_probe = n_lists degenerates to exact search."""
        candidates = [r for i in self._nearest_centroids(vector, n_probe) for r in self.lists[i]]
        hits = [SearchHit(id=r.id, score=score(self.metric, vector, r.vector), text=r.text) for r in candidates]
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:k], len(candidates)


def recall_at_k(approx_ids: list[str], exact_ids: list[str]) -> float:
    """recall@k = |approx top-k ∩ exact top-k| / k. The metric every ANN knob is tuned against."""
    if not exact_ids:
        return 1.0
    return len(set(approx_ids) & set(exact_ids)) / len(exact_ids)


def recall_experiment(
    records: list[VectorRecord],
    queries: list[Vector],
    k: int = 10,
    n_lists: int = 16,
    n_probes: list[int] | None = None,
) -> list[RecallPoint]:
    """Sweep n_probe and report recall@k vs work done, with ExactVectorStore as ground truth.

    When to use: before choosing ANN knobs (n_probe / ef_search); run it on your own data, not a benchmark.
    Catch: recall depends on data distribution; random uniform vectors are a pessimistic case.
    """
    exact = ExactVectorStore(Metric.COSINE)
    exact.upsert(records)
    ivf = IvfIndex(n_lists=n_lists)
    ivf.train([r.vector for r in records])
    ivf.add(records)
    points: list[RecallPoint] = []
    for n_probe in n_probes or [1, 2, 4, 8, n_lists]:
        recalls: list[float] = []
        scanned = 0
        for q in queries:
            truth = [h.id for h in exact.query(q, k)]
            hits, n_scanned = ivf.query(q, k, n_probe)
            recalls.append(recall_at_k([h.id for h in hits], truth))
            scanned += n_scanned
        points.append(
            RecallPoint(
                n_probe=n_probe,
                recall_at_k=sum(recalls) / len(recalls),
                fraction_scanned=scanned / (len(queries) * len(records)),
            )
        )
    return points


def random_unit_vectors(n: int, dims: int, seed: int = 1) -> list[Vector]:
    """Synthetic data for demos and tests (no AWS)."""
    rng = random.Random(seed)
    return [normalize([rng.gauss(0.0, 1.0) for _ in range(dims)]) for _ in range(n)]


# ================================================================ binary quantization


def binary_quantize(vector: Vector) -> int:
    """Sign bit per dimension packed into one int: 1024 floats (4 KiB) -> 1024 bits (128 B) = 32x smaller.

    Catch: throws away magnitude; recall drops, so production systems rescore the top candidates
    with full-precision vectors (OpenSearch on_disk mode, Titan V2 embeddingTypes=["binary"] + float).
    """
    bits = 0
    for i, x in enumerate(vector):
        if x > 0:
            bits |= 1 << i
    return bits


def hamming(a: int, b: int) -> int:
    """Number of differing bits: XOR + popcount, one CPU instruction per 64 dims."""
    return (a ^ b).bit_count()


def binary_search_with_rescore(
    records: list[VectorRecord], query: Vector, k: int, oversample: int = 4
) -> list[SearchHit]:
    """Two-phase search: Hamming over bits for k*oversample candidates, then exact cosine rescoring.

    When to use: memory-bound indexes; oversample is the recall knob (2-10x typical, order of magnitude).
    """
    q_bits = binary_quantize(query)
    codes = [(r, binary_quantize(r.vector)) for r in records]  # a real index stores codes, not recomputes
    codes.sort(key=lambda rc: hamming(q_bits, rc[1]))
    shortlist = [r for r, _ in codes[: k * oversample]]
    hits = [SearchHit(id=r.id, score=cosine(query, r.vector), text=r.text) for r in shortlist]
    hits.sort(key=lambda h: h.score, reverse=True)
    return hits[:k]


# ================================================================ memory math


def vector_memory_bytes(n_vectors: int, dims: int, scheme: QuantScheme, pq_m: int = 64) -> int:
    """Raw vector bytes only (no graph). Use for order-of-magnitude sizing before picking a store tier."""
    per_vector = {
        QuantScheme.FLOAT32: 4 * dims,
        QuantScheme.FLOAT16: 2 * dims,
        QuantScheme.INT8: dims,
        QuantScheme.BINARY: math.ceil(dims / 8),
        QuantScheme.PQ: pq_m,  # one 8-bit code per sub-vector
    }[scheme]
    return n_vectors * per_vector


def hnsw_memory_bytes(n_vectors: int, dims: int, m: int = 16) -> int:
    """OpenSearch k-NN sizing rule for faiss HNSW float32: 1.1 * (4*d + 8*m) bytes per vector.

    Example: 1M x 1024 dims, m=16 -> ~4.6 GB of native (off-heap) memory.
    """
    return int(1.1 * (4 * dims + 8 * m) * n_vectors)
