"""Models and the VectorStore port for the OpenSearch slice. No SDK imports.

- The port is defined locally (same shape as 02.01's) so slices stay independent.
- KbIndexContract is the single place that names the fields the Bedrock KB writes and reads.
"""

from dataclasses import dataclass, field
from typing import Protocol

Vector = list[float]
MetadataFilter = dict[str, object]  # field -> value (scalar = term, list = terms)


@dataclass(frozen=True)
class KbIndexContract:
    index_name: str
    vector_field: str
    text_field: str
    metadata_field: str
    dimensions: int


@dataclass(frozen=True)
class VectorRecord:
    id: str
    vector: Vector
    text: str = ""
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class SearchHit:
    id: str
    score: float
    text: str = ""
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class BulkItemError:
    id: str
    status: int
    error_type: str
    reason: str


@dataclass
class BulkResult:
    succeeded: int = 0
    failed: list[BulkItemError] = field(default_factory=list)  # non-retryable or out of attempts
    attempts: int = 0


class VectorStore(Protocol):
    def upsert(self, records: list[VectorRecord]) -> int: ...

    def query(self, vector: Vector, k: int, filter: MetadataFilter | None = None) -> list[SearchHit]: ...

    def delete(self, ids: list[str]) -> int: ...
