"""Vertex AI Agent Engine Memory Bank as long-term memory.

Memory Bank stores facts scoped by a dict (we use {"user_id": ...}). Facts arrive two ways:
  create(fact=...)            a fact written directly (our `remember` tool)
  generate(vertex_session_source=...)  extracted by Gemini from an Agent Engine session
                              (what ADK's VertexAiMemoryBankService does on add_session_to_memory)
`retrieve` does similarity search within the scope.
"""

import asyncio

from app.memory.base import MemoryRecord


class VertexMemoryBank:
    name = "vertex_memory_bank"

    def __init__(self, engine_name: str, project: str, location: str, client=None):
        self.engine_name = engine_name
        self.project = project
        self.location = location
        self._client = client

    @property
    def client(self):
        if self._client is None:
            import vertexai

            self._client = vertexai.Client(project=self.project, location=self.location)
        return self._client

    async def add(self, user_id: str, text: str, session_id: str) -> str:
        op = await asyncio.to_thread(
            self.client.agent_engines.memories.create,
            name=self.engine_name,
            fact=text,
            scope={"user_id": user_id},
        )
        return getattr(op, "name", "") or ""

    async def search(self, user_id: str, query: str, k: int = 5) -> list[MemoryRecord]:
        def _retrieve():
            return list(
                self.client.agent_engines.memories.retrieve(
                    name=self.engine_name,
                    scope={"user_id": user_id},
                    similarity_search_params={"search_query": query, "top_k": k},
                )
            )

        results = await asyncio.to_thread(_retrieve)
        return [
            MemoryRecord(
                text=r.memory.fact,
                score=1.0 - float(getattr(r, "distance", 0.0) or 0.0),
                source="vertex:memory-bank",
            )
            for r in results
        ]
