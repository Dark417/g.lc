"""REST adapter mounted at /kb. Thin mapping to infra / service; every call needs the KB from terraform/02.04."""

from dataclasses import asdict
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.a02_04_knowledge_bases import infra, service
from app.a02_04_knowledge_bases.domain import RetrievalFilter

router = APIRouter()


class RetrieveRequest(BaseModel):
    query: str = Field(min_length=1)
    k: int | None = Field(default=None, ge=1, le=100)
    search_type: str | None = Field(default=None, pattern="^(HYBRID|SEMANTIC)$")
    filter: RetrievalFilter | None = None
    rerank: bool = False


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    session_id: str | None = None
    filter: RetrievalFilter | None = None
    decompose: bool = False


class SidecarRequest(BaseModel):
    document_key: str = Field(min_length=1, description="kb-docs/... key of the document")
    attributes: dict[str, Any]


class DataSourceRequest(BaseModel):
    name: str = Field(min_length=1)
    strategy: str = Field(pattern="^(FIXED_SIZE|HIERARCHICAL|SEMANTIC|NONE)$")
    prefix: str | None = None


@router.post("/sync")
def sync(wait: bool = False) -> dict[str, Any]:
    job = infra.start_ingestion_job()
    return asdict(infra.wait_for_ingestion(job.job_id) if wait else job)


@router.get("/sync/{job_id}")
def sync_status(job_id: str) -> dict[str, Any]:
    return asdict(infra.get_ingestion_job(job_id))


@router.get("/sync")
def sync_history(status: str | None = None) -> list[dict[str, Any]]:
    return [asdict(j) for j in infra.list_ingestion_jobs(status)]


@router.post("/retrieve")
def retrieve(body: RetrieveRequest) -> list[dict[str, Any]]:
    return [asdict(c) for c in infra.retrieve(body.query, body.k, body.search_type, body.filter, body.rerank)]


@router.post("/ask")
def ask(body: AskRequest) -> dict[str, Any]:
    return asdict(infra.retrieve_and_generate(body.question, body.session_id, body.filter, decompose=body.decompose))


@router.post("/metadata")
def metadata(body: SidecarRequest) -> dict[str, str]:
    return {"key": infra.write_metadata_sidecar(body.document_key, body.attributes)}


@router.post("/data-sources")
def data_source(body: DataSourceRequest) -> dict[str, Any]:
    return infra.create_data_source(body.name, body.strategy, body.prefix)


@router.post("/s3-event")
def s3_event(event: dict[str, Any]) -> dict[str, Any]:
    return service.handle_s3_event(event)
