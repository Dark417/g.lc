"""Long-term memory as an ADK MemoryService backed by our SQL database.

- add_session_to_memory: stores each user/assistant text event once (keyed by event id).
- search_memory: cosine over this user's rows only. Never crosses users.

ILLUSTRATION: raw turns + embeddings. PRODUCTION: MEMORY_BACKEND=vertex ->
VertexAiMemoryBankService, which extracts and consolidates facts with an LLM.
"""

from google.adk.memory import BaseMemoryService
from google.adk.memory.base_memory_service import SearchMemoryResponse
from google.adk.memory.memory_entry import MemoryEntry
from google.adk.sessions import Session
from google.genai import types
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.rag.embedder import Embedder
from app.storage.sql import MemoryRow

MAX_CHARS = 2000


def _event_text(event) -> str:
    if not event.content or not event.content.parts or event.partial:
        return ""
    return "".join(p.text for p in event.content.parts if p.text and not p.thought).strip()


class SqlMemoryService(BaseMemoryService):
    def __init__(
        self,
        sessionmaker: async_sessionmaker,
        embedder: Embedder,
        *,
        min_score: float = 0.2,
        top_k: int = 5,
    ) -> None:
        self._sm = sessionmaker
        self._embedder = embedder
        self._min_score = min_score
        self._top_k = top_k

    async def add_session_to_memory(self, session: Session) -> None:
        candidates = [(e, _event_text(e)) for e in session.events]
        candidates = [(e, t) for e, t in candidates if t and not t.startswith("[Uploaded Artifact")]
        if not candidates:
            return
        async with self._sm() as s:
            existing = set(
                (
                    await s.scalars(select(MemoryRow.id).where(MemoryRow.session_id == session.id))
                ).all()
            )
        new = [(e, t[:MAX_CHARS]) for e, t in candidates if e.id not in existing]
        if not new:
            return
        vectors = await self._embedder.embed([t for _, t in new])
        async with self._sm() as s, s.begin():
            for (e, t), v in zip(new, vectors, strict=True):
                s.add(
                    MemoryRow(
                        id=e.id,
                        app_name=session.app_name,
                        user_id=session.user_id,
                        session_id=session.id,
                        author=e.author,
                        text=t,
                        embedding=v,
                    )
                )

    async def search_memory(
        self, *, app_name: str, user_id: str, query: str
    ) -> SearchMemoryResponse:
        async with self._sm() as s:
            rows = (
                await s.scalars(
                    select(MemoryRow).where(
                        MemoryRow.app_name == app_name, MemoryRow.user_id == user_id
                    )
                )
            ).all()
        if not rows or not query.strip():
            return SearchMemoryResponse(memories=[])
        [q] = await self._embedder.embed([query], task="query")
        scored = sorted(
            ((sum(a * b for a, b in zip(q, r.embedding, strict=False)), r) for r in rows),
            key=lambda x: x[0],
            reverse=True,
        )
        return SearchMemoryResponse(
            memories=[
                MemoryEntry(
                    id=r.id,
                    author=r.author,
                    timestamp=r.created_at.isoformat() if r.created_at else None,
                    content=types.Content(role="user", parts=[types.Part(text=r.text)]),
                )
                for score, r in scored[: self._top_k]
                if score >= self._min_score
            ]
        )

    async def delete_session(self, *, app_name: str, user_id: str, session_id: str) -> None:
        async with self._sm() as s, s.begin():
            await s.execute(
                delete(MemoryRow).where(
                    MemoryRow.app_name == app_name,
                    MemoryRow.user_id == user_id,
                    MemoryRow.session_id == session_id,
                )
            )
