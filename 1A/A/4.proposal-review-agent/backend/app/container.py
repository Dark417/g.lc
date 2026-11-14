"""Composition root: settings -> every adapter and service, built once.

ADK's dev UI builds its services from URIs. We register a `container://` scheme with ADK's
service registry so the dev UI and our API share the *same* session, memory, and artifact
service instances. See docs/design/01-architecture.md.
"""

import logging
from dataclasses import dataclass

from google.adk.artifacts import BaseArtifactService
from google.adk.memory import BaseMemoryService
from google.adk.sessions import BaseSessionService, DatabaseSessionService
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from app.config import Settings, get_settings
from app.llm.gemini import LLM, GeminiLLM
from app.rag.embedder import Embedder, GeminiEmbedder, HashingEmbedder
from app.rag.retriever import Retriever
from app.rag.vector_store import PgVectorStore, SqlVectorStore, VectorStore, VertexVectorSearchStore
from app.services.assessment import AssessmentService
from app.services.ingestion import IngestionService
from app.services.memory import SqlMemoryService
from app.services.rules import RuleService
from app.storage.assessments_repo import SqlAssessmentRepository
from app.storage.blobs import BlobStore, GcsBlobStore, LocalBlobStore
from app.storage.documents_repo import (
    DocumentRepository,
    JsonFileDocumentRepository,
    MongoDocumentRepository,
)
from app.storage.rules_repo import SqlRuleRepository
from app.storage.sql import init_schema, make_engine, make_sessionmaker, ping

log = logging.getLogger(__name__)


@dataclass
class Container:
    settings: Settings
    engine: AsyncEngine
    sessionmaker: async_sessionmaker
    rules: SqlRuleRepository
    assessments: SqlAssessmentRepository
    docs: DocumentRepository
    blobs: BlobStore
    embedder: Embedder
    vectors: VectorStore
    retriever: Retriever
    llm: LLM
    rule_service: RuleService
    ingestion: IngestionService
    assessment: AssessmentService
    sessions: BaseSessionService
    memory: BaseMemoryService
    artifacts: BaseArtifactService

    async def init(self) -> None:
        await init_schema(self.engine)
        await self.vectors.init()
        await self.docs.init()

    async def ready(self) -> None:
        await ping(self.engine)

    async def close(self) -> None:
        await self.docs.close()
        await self.engine.dispose()


def _embedder(s: Settings) -> Embedder:
    if s.embedder == "gemini":
        return GeminiEmbedder(s.embedding_model, s.embedding_dim)
    return HashingEmbedder(s.embedding_dim)


def _vectors(s: Settings, engine, sm) -> VectorStore:
    if s.vector_store == "pgvector":
        return PgVectorStore(engine, s.embedding_dim)
    if s.vector_store == "vertex":
        return VertexVectorSearchStore()
    return SqlVectorStore(sm)


def _docs(s: Settings) -> DocumentRepository:
    if s.doc_store == "mongo":
        return MongoDocumentRepository(s.mongo_url, s.mongo_db)
    return JsonFileDocumentRepository(s.doc_store_path)


def _blobs(s: Settings) -> BlobStore:
    if s.blob_store == "gcs":
        return GcsBlobStore(s.gcs_bucket)
    return LocalBlobStore(s.blob_dir)


def _artifacts(s: Settings) -> BaseArtifactService:
    if s.blob_store == "gcs":
        from google.adk.artifacts.gcs_artifact_service import GcsArtifactService

        return GcsArtifactService(bucket_name=s.gcs_bucket)
    from google.adk.artifacts.file_artifact_service import FileArtifactService

    return FileArtifactService(root_dir=s.artifact_dir)


def _memory(s: Settings, sm, embedder) -> BaseMemoryService:
    if s.memory_backend == "vertex":
        from google.adk.memory.vertex_ai_memory_bank_service import VertexAiMemoryBankService

        return VertexAiMemoryBankService(
            project=s.google_cloud_project,
            location=s.google_cloud_location,
            agent_engine_id=s.agent_engine_id,
        )
    return SqlMemoryService(sm, embedder, min_score=s.memory_min_score)


def build_container(
    settings: Settings, *, llm: LLM | None = None, embedder: Embedder | None = None
) -> Container:
    engine = make_engine(settings.database_url)
    sm = make_sessionmaker(engine)
    embedder = embedder or _embedder(settings)
    vectors = _vectors(settings, engine, sm)
    retriever = Retriever(embedder, vectors)
    llm = llm or GeminiLLM(settings.model)
    rules = SqlRuleRepository(sm)
    assessments = SqlAssessmentRepository(sm)
    docs = _docs(settings)
    blobs = _blobs(settings)
    session_kwargs = {"connect_args": {"timeout": 30}} if settings.is_sqlite else {}
    return Container(
        settings=settings,
        engine=engine,
        sessionmaker=sm,
        rules=rules,
        assessments=assessments,
        docs=docs,
        blobs=blobs,
        embedder=embedder,
        vectors=vectors,
        retriever=retriever,
        llm=llm,
        rule_service=RuleService(rules, retriever),
        ingestion=IngestionService(docs, blobs, retriever, llm),
        assessment=AssessmentService(
            rules=rules, retriever=retriever, llm=llm, assessments=assessments, settings=settings
        ),
        sessions=DatabaseSessionService(db_url=settings.database_url, **session_kwargs),
        memory=_memory(settings, sm, embedder),
        artifacts=_artifacts(settings),
    )


_container: Container | None = None


def get_container() -> Container:
    """Process-wide container. ADK's agent loader imports the agent module, which calls this."""
    global _container
    if _container is None:
        settings = get_settings()
        settings.export_model_env()
        _container = build_container(settings)
    return _container


def set_container(c: Container) -> None:
    global _container
    _container = c


def register_adk_services(c: Container) -> None:
    from google.adk.cli.service_registry import get_service_registry

    reg = get_service_registry()
    reg.register_session_service("container", lambda uri, **kw: c.sessions)
    reg.register_memory_service("container", lambda uri, **kw: c.memory)
    reg.register_artifact_service("container", lambda uri, **kw: c.artifacts)
