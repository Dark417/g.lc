"""Vertex AI RAG Engine retriever (GCP-managed RAG).

Index: a RAG corpus created and filled by infra/gcp/setup_vertex.py.
API: `vertexai.rag.retrieval_query` -> contexts with source URI and distance.
Native framework equivalent: ADK `VertexAiRagRetrieval` tool (used in the ADK adapter on vertex).
"""

import asyncio

from app.rag.base import Passage


class VertexRagRetriever:
    name = "vertex_rag"

    def __init__(self, corpus: str, project: str, location: str):
        self.corpus = corpus
        self.project = project
        self.location = location
        self._ready = False

    def _query(self, query: str, k: int):
        import vertexai
        from vertexai import rag

        if not self._ready:
            vertexai.init(project=self.project, location=self.location)
            self._ready = True
        return rag.retrieval_query(
            rag_resources=[rag.RagResource(rag_corpus=self.corpus)],
            text=query,
            rag_retrieval_config=rag.RagRetrievalConfig(top_k=k),
        )

    async def search(self, query: str, k: int = 4) -> list[Passage]:
        resp = await asyncio.to_thread(self._query, query, k)
        out = []
        for c in resp.contexts.contexts:
            # RAG Engine reports a distance (lower is closer); flip it so higher is better.
            score = 1.0 - float(getattr(c, "distance", 0.0) or getattr(c, "score", 0.0) or 0.0)
            out.append(Passage(source=c.source_uri.rsplit("/", 1)[-1], text=c.text, score=score))
        return out
