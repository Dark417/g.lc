"""REST adapter mounted at /embeddings.

- /embed calls Bedrock (needs AWS); the other endpoints are pure math on synthetic data (no AWS).
"""

from dataclasses import asdict
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.a02_01_embeddings import infra, similarity
from app.a02_01_embeddings.domain import Metric, QuantScheme, VectorRecord

router = APIRouter()


class EmbedRequest(BaseModel):
    text: str = Field(min_length=1)
    dimensions: int = Field(default=1024, description="256 | 512 | 1024")
    binary: bool = False


class SimilarityRequest(BaseModel):
    a: list[float] = Field(min_length=1)
    b: list[float] = Field(min_length=1)


class RecallRequest(BaseModel):
    n_vectors: int = Field(default=2000, ge=100, le=20000)
    dims: int = Field(default=32, ge=4, le=256)
    n_queries: int = Field(default=20, ge=1, le=200)
    k: int = Field(default=10, ge=1, le=100)
    n_lists: int = Field(default=16, ge=2, le=256)


class MemoryRequest(BaseModel):
    n_vectors: int = Field(default=1_000_000, ge=1)
    dims: int = Field(default=1024, ge=1)
    m: int = Field(default=16, ge=2, description="HNSW neighbours per node")


@router.post("/embed")
def embed(body: EmbedRequest) -> dict[str, Any]:
    e = infra.embed_text(body.text, dimensions=body.dimensions, binary=body.binary)
    return {"model_id": e.model_id, "dimensions": e.dimensions, "input_tokens": e.input_tokens, "head": e.vector[:8]}


@router.post("/similarity")
def compare(body: SimilarityRequest) -> dict[str, float]:
    return {m.value: similarity.score(m, body.a, body.b) for m in Metric} | {"l2_distance": similarity.l2_distance(body.a, body.b)}


@router.post("/recall-demo")
def recall_demo(body: RecallRequest) -> list[dict[str, Any]]:
    vectors = similarity.random_unit_vectors(body.n_vectors, body.dims, seed=1)
    records = [VectorRecord(id=str(i), vector=v) for i, v in enumerate(vectors)]
    queries = similarity.random_unit_vectors(body.n_queries, body.dims, seed=2)
    return [asdict(p) for p in similarity.recall_experiment(records, queries, body.k, body.n_lists)]


@router.post("/memory-estimate")
def memory_estimate(body: MemoryRequest) -> dict[str, int]:
    raw = {s.value: similarity.vector_memory_bytes(body.n_vectors, body.dims, s) for s in QuantScheme}
    return raw | {"hnsw_float32_total": similarity.hnsw_memory_bytes(body.n_vectors, body.dims, body.m)}
