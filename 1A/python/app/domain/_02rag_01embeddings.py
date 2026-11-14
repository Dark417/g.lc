"""Models and ports for embeddings and vector search. No SDK imports.

- VectorStore is the port every store adapter implements (exact in-memory here, OpenSearch in 02.02).
- Embedder and EmbeddingCache are ports so tests can inject fakes and the cache can move to Redis / DynamoDB.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol

Vector = list[float]
MetadataFilter = dict[str, object]  # field -> required value (equality only, enough to show pre-filtering)


class Metric(StrEnum):
    COSINE = "cosine"  # angle only; magnitude ignored
    DOT = "dot"  # angle x magnitudes; == cosine when vectors are unit length
    L2 = "l2"  # Euclidean distance; smaller = closer; same ranking as cosine on unit vectors


class InputType(StrEnum):
    # Asymmetric models (Cohere v3+) embed documents and queries differently; Titan V2 has no such flag.
    SEARCH_DOCUMENT = "search_document"
    SEARCH_QUERY = "search_query"


class QuantScheme(StrEnum):
    FLOAT32 = "float32"  # 4 B / dim
    FLOAT16 = "float16"  # 2 B / dim (scalar quantization, near-lossless)
    INT8 = "int8"  # 1 B / dim (scalar / byte quantization)
    BINARY = "binary"  # 1 bit / dim (sign), needs rescoring for good recall
    PQ = "pq"  # product quantization: m sub-vectors x 1 B code each


@dataclass(frozen=True)
class Embedding:
    vector: Vector
    model_id: str
    dimensions: int
    input_tokens: int = 0
    binary: list[int] | None = None  # Titan V2 embeddingTypes=["binary"]: one 0/1 per dimension


@dataclass(frozen=True)
class VectorRecord:
    id: str
    vector: Vector
    text: str = ""
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class SearchHit:
    id: str
    score: float  # higher = more similar (L2 is converted to 1 / (1 + d))
    text: str = ""
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class RecallPoint:
    n_probe: int
    recall_at_k: float
    fraction_scanned: float  # share of vectors compared: the latency / cost proxy


class VectorStore(Protocol):
    def upsert(self, records: list[VectorRecord]) -> int: ...

    def query(self, vector: Vector, k: int, filter: MetadataFilter | None = None) -> list[SearchHit]: ...

    def delete(self, ids: list[str]) -> int: ...


class Embedder(Protocol):
    def embed(self, text: str, input_type: InputType = InputType.SEARCH_DOCUMENT) -> Vector: ...


class EmbeddingCache(Protocol):
    def get(self, key: str) -> Vector | None: ...

    def put(self, key: str, vector: Vector) -> None: ...
