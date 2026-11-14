"""Resolve Settings -> concrete RAG components. The only place that knows all implementations."""

import logging

from app.config import Settings
from app.rag.embedder import Embedder, GeminiEmbedder, HashingEmbedder
from app.rag.retriever import Retriever, load_markdown_dir
from app.rag.vector_store import ChromaVectorStore, InMemoryVectorStore, VectorStore

log = logging.getLogger(__name__)


def build_embedder(settings: Settings) -> Embedder:
    if settings.embedder == "gemini":
        return GeminiEmbedder()
    return HashingEmbedder()


def build_vector_store(settings: Settings) -> VectorStore:
    if settings.vector_store == "chroma":
        return ChromaVectorStore(path=settings.chroma_path)
    return InMemoryVectorStore()


def build_retriever(settings: Settings, ingest: bool = True) -> Retriever:
    retriever = Retriever(build_embedder(settings), build_vector_store(settings))
    if ingest:
        # ILLUSTRATION: (re)index on every startup. PRODUCTION: a separate ingest job/pipeline
        # writes to the persistent store; the API only reads.
        n = retriever.index(load_markdown_dir(settings.knowledge_dir))
        log.info("rag: indexed %d chunks from %s", n, settings.knowledge_dir)
    return retriever
