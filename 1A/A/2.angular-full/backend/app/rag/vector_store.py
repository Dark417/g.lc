"""Vector store: add vectors with payloads, query by similarity.

Two implementations behind one Protocol. Selected by Settings.vector_store in app/rag/factory.py.
"""

from dataclasses import dataclass, field
from typing import Any, Protocol

from app.rag.embedder import Vector


@dataclass
class Hit:
    id: str
    text: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


class VectorStore(Protocol):
    def add(
        self, ids: list[str], vectors: list[Vector], texts: list[str], metadatas: list[dict]
    ) -> None: ...

    def search(self, vector: Vector, k: int) -> list[Hit]: ...

    def count(self) -> int: ...


class InMemoryVectorStore:
    """ILLUSTRATION: brute-force cosine similarity over Python lists.

    O(n) per query, lost on restart. Fine for a few hundred chunks. The point is to show the
    interface, not to be fast.
    """

    def __init__(self) -> None:
        self._rows: list[tuple[str, Vector, str, dict]] = []

    def add(
        self, ids: list[str], vectors: list[Vector], texts: list[str], metadatas: list[dict]
    ) -> None:
        self._rows.extend(zip(ids, vectors, texts, metadatas, strict=True))

    def search(self, vector: Vector, k: int) -> list[Hit]:
        # vectors are unit-normalised by the embedder, so dot product == cosine similarity
        scored = [
            Hit(id=i, text=t, score=sum(a * b for a, b in zip(vector, v, strict=True)), metadata=m)
            for i, v, t, m in self._rows
        ]
        scored.sort(key=lambda h: h.score, reverse=True)
        return scored[:k]

    def count(self) -> int:
        return len(self._rows)


class ChromaVectorStore:
    """PRODUCTION (dummy, but real API calls): persistent Chroma collection.

    `uv sync --extra chroma` then VECTOR_STORE=chroma. For scale, swap for pgvector, Qdrant,
    or Vertex AI Vector Search; the interface stays the same.
    """

    def __init__(self, path: str, collection: str = "knowledge") -> None:
        import chromadb  # optional dependency

        self._col = chromadb.PersistentClient(path=path).get_or_create_collection(
            collection, metadata={"hnsw:space": "cosine"}
        )

    def add(
        self, ids: list[str], vectors: list[Vector], texts: list[str], metadatas: list[dict]
    ) -> None:
        self._col.upsert(ids=ids, embeddings=vectors, documents=texts, metadatas=metadatas)

    def search(self, vector: Vector, k: int) -> list[Hit]:
        res = self._col.query(query_embeddings=[vector], n_results=k)
        return [
            Hit(id=i, text=d, score=1.0 - dist, metadata=m or {})
            for i, d, dist, m in zip(
                res["ids"][0],
                res["documents"][0],
                res["distances"][0],
                res["metadatas"][0],
                strict=True,
            )
        ]

    def count(self) -> int:
        return self._col.count()
