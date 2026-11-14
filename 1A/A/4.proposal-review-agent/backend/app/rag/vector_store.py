"""Vector stores for document chunks (kind='doc') and rules (kind='rule').

- SqlVectorStore: ILLUSTRATION. JSON embeddings, brute-force cosine in Python. SQLite or Postgres.
- PgVectorStore: PRODUCTION. pgvector `vector(N)` column + HNSW index. Cloud SQL supports it.
- VertexVectorSearchStore: PRODUCTION alternative for 10M+ chunks (dummy body).
"""

import json
from dataclasses import dataclass, field
from typing import Any, Protocol

from sqlalchemy import delete, func, select, text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from app.rag.embedder import Vector
from app.storage.sql import ChunkRow


@dataclass
class VectorRecord:
    id: str
    kind: str
    ref_id: str
    text: str
    embedding: Vector
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Hit:
    id: str
    kind: str
    ref_id: str
    text: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


class VectorStore(Protocol):
    async def init(self) -> None: ...
    async def upsert(self, records: list[VectorRecord]) -> None: ...
    async def delete_ref(self, kind: str, ref_id: str) -> None: ...
    async def search(self, vector: Vector, *, kind: str, k: int) -> list[Hit]: ...
    async def count(self, kind: str) -> int: ...


class SqlVectorStore:
    def __init__(self, sessionmaker: async_sessionmaker) -> None:
        self._sm = sessionmaker

    async def init(self) -> None:
        return None  # table is part of the ORM schema

    async def upsert(self, records: list[VectorRecord]) -> None:
        async with self._sm() as s, s.begin():
            for r in records:
                await s.merge(
                    ChunkRow(
                        id=r.id,
                        kind=r.kind,
                        ref_id=r.ref_id,
                        text=r.text,
                        meta=r.metadata,
                        embedding=r.embedding,
                    )
                )

    async def delete_ref(self, kind: str, ref_id: str) -> None:
        async with self._sm() as s, s.begin():
            await s.execute(
                delete(ChunkRow).where(ChunkRow.kind == kind, ChunkRow.ref_id == ref_id)
            )

    async def search(self, vector: Vector, *, kind: str, k: int) -> list[Hit]:
        async with self._sm() as s:
            rows = (await s.scalars(select(ChunkRow).where(ChunkRow.kind == kind))).all()
        hits = [
            Hit(
                r.id,
                r.kind,
                r.ref_id,
                r.text,
                sum(a * b for a, b in zip(vector, r.embedding, strict=False)),
                r.meta,
            )
            for r in rows
        ]
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:k]

    async def count(self, kind: str) -> int:
        async with self._sm() as s:
            return await s.scalar(select(func.count()).where(ChunkRow.kind == kind)) or 0


def _vec(v: Vector) -> str:
    return "[" + ",".join(f"{x:.7f}" for x in v) + "]"


class PgVectorStore:
    TABLE = "chunk_embeddings"

    def __init__(self, engine: AsyncEngine, dim: int) -> None:
        self._engine, self._dim = engine, dim

    async def init(self) -> None:
        stmts = [
            "CREATE EXTENSION IF NOT EXISTS vector",
            f"""CREATE TABLE IF NOT EXISTS {self.TABLE} (
                  id text PRIMARY KEY, kind text NOT NULL, ref_id text NOT NULL,
                  text text NOT NULL, metadata jsonb NOT NULL DEFAULT '{{}}',
                  embedding vector({self._dim}) NOT NULL)""",
            f"CREATE INDEX IF NOT EXISTS {self.TABLE}_ref ON {self.TABLE} (kind, ref_id)",
            f"""CREATE INDEX IF NOT EXISTS {self.TABLE}_hnsw ON {self.TABLE}
                  USING hnsw (embedding vector_cosine_ops)""",
        ]
        async with self._engine.begin() as conn:
            for stmt in stmts:
                await conn.execute(text(stmt))

    async def upsert(self, records: list[VectorRecord]) -> None:
        if not records:
            return
        sql = text(
            f"""INSERT INTO {self.TABLE} (id, kind, ref_id, text, metadata, embedding)
                VALUES (:id, :kind, :ref_id, :text, CAST(:metadata AS jsonb), CAST(:embedding AS vector))
                ON CONFLICT (id) DO UPDATE SET kind = EXCLUDED.kind, ref_id = EXCLUDED.ref_id,
                  text = EXCLUDED.text, metadata = EXCLUDED.metadata, embedding = EXCLUDED.embedding"""
        )
        params = [
            {
                "id": r.id,
                "kind": r.kind,
                "ref_id": r.ref_id,
                "text": r.text,
                "metadata": json.dumps(r.metadata),
                "embedding": _vec(r.embedding),
            }
            for r in records
        ]
        async with self._engine.begin() as conn:
            await conn.execute(sql, params)

    async def delete_ref(self, kind: str, ref_id: str) -> None:
        async with self._engine.begin() as conn:
            await conn.execute(
                text(f"DELETE FROM {self.TABLE} WHERE kind = :k AND ref_id = :r"),
                {"k": kind, "r": ref_id},
            )

    async def search(self, vector: Vector, *, kind: str, k: int) -> list[Hit]:
        sql = text(
            f"""SELECT id, kind, ref_id, text, metadata,
                       1 - (embedding <=> CAST(:q AS vector)) AS score
                FROM {self.TABLE} WHERE kind = :kind
                ORDER BY embedding <=> CAST(:q AS vector) LIMIT :k"""
        )
        async with self._engine.connect() as conn:
            rows = (await conn.execute(sql, {"q": _vec(vector), "kind": kind, "k": k})).all()
        return [
            Hit(
                r.id,
                r.kind,
                r.ref_id,
                r.text,
                float(r.score),
                json.loads(r.metadata) if isinstance(r.metadata, str) else r.metadata,
            )
            for r in rows
        ]

    async def count(self, kind: str) -> int:
        async with self._engine.connect() as conn:
            res = await conn.execute(
                text(f"SELECT count(*) FROM {self.TABLE} WHERE kind = :k"), {"k": kind}
            )
            return res.scalar_one()


class VertexVectorSearchStore:
    """PRODUCTION alternative (dummy): Vertex AI Vector Search.

    Real wiring, roughly:
        from google.cloud import aiplatform
        index = aiplatform.MatchingEngineIndex(index_name=INDEX_ID)
        index.upsert_datapoints(datapoints=[IndexDatapoint(datapoint_id=r.id,
            feature_vector=r.embedding, restricts=[Namespace("kind", [r.kind])])])
        endpoint = aiplatform.MatchingEngineIndexEndpoint(ENDPOINT_ID)
        endpoint.find_neighbors(deployed_index_id=DEPLOYED_ID, queries=[vector], num_neighbors=k)
    Chunk text and metadata stay in Postgres; Vector Search stores only ids + vectors.
    """

    def __init__(self, *_, **__) -> None:
        raise NotImplementedError("VertexVectorSearchStore is a production placeholder")
