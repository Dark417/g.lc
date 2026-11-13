"""REST adapter mounted at /opensearch. Thin: maps HTTP to infra; every call needs the collection to exist."""

from dataclasses import asdict
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.a02_02_opensearch import infra
from app.a02_02_opensearch.domain import VectorRecord

router = APIRouter()


class RecordIn(BaseModel):
    id: str = Field(min_length=1)
    vector: list[float]
    text: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnnRequest(BaseModel):
    vector: list[float]
    k: int = Field(default=5, ge=1, le=100)
    filter: dict[str, Any] | None = None
    ef_search: int | None = Field(default=None, ge=1)


class HybridRequest(BaseModel):
    text: str = Field(min_length=1)
    vector: list[float]
    k: int = Field(default=5, ge=1, le=100)
    filter: dict[str, Any] | None = None


class PipelineRequest(BaseModel):
    lexical_weight: float = Field(default=0.3, ge=0, le=1)
    vector_weight: float = Field(default=0.7, ge=0, le=1)


@router.post("/index")
def create_index(recreate: bool = False) -> dict[str, Any]:
    return infra.create_kb_index(recreate)


@router.delete("/index")
def delete_index() -> dict[str, bool]:
    return {"deleted": infra.delete_index()}


@router.post("/documents")
def bulk(records: list[RecordIn]) -> dict[str, Any]:
    result = infra.bulk_index([VectorRecord(r.id, r.vector, r.text, r.metadata) for r in records])
    return asdict(result)


@router.post("/knn")
def knn(body: KnnRequest) -> list[dict[str, Any]]:
    hits = infra.filtered_knn_query(body.vector, body.filter, body.k) if body.filter else infra.knn_query(body.vector, body.k, body.ef_search)
    return [asdict(h) for h in hits]


@router.post("/pipeline")
def pipeline(body: PipelineRequest) -> dict[str, Any]:
    return infra.create_hybrid_pipeline(body.lexical_weight, body.vector_weight)


@router.post("/hybrid")
def hybrid(body: HybridRequest) -> list[dict[str, Any]]:
    return [asdict(h) for h in infra.hybrid_query(body.text, body.vector, body.k, body.filter)]
