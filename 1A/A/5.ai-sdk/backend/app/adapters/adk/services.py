"""ADK session and memory services per provider branch.

             SessionService (conversation)             MemoryService (long-term)
  raw        DatabaseSessionService (SQLite)           InMemoryMemoryService
  bedrock    DatabaseSessionService (point at RDS)     AgentCoreMemoryService (ours, below)
  vertex     VertexAiSessionService (Agent Engine)     VertexAiMemoryBankService (Memory Bank)

ADK's service interfaces are its cloud extension point: AgentCoreMemoryService is ~40 lines and
makes AgentCore Memory a first-class ADK memory (load_memory / PreloadMemoryTool just work).
"""

from functools import cache

from google.adk.memory import InMemoryMemoryService
from google.adk.memory.base_memory_service import BaseMemoryService, SearchMemoryResponse
from google.adk.memory.memory_entry import MemoryEntry
from google.adk.sessions import BaseSessionService, DatabaseSessionService
from google.genai import types

from app.config import Settings


class AgentCoreMemoryService(BaseMemoryService):
    """ADK BaseMemoryService backed by Amazon Bedrock AgentCore Memory."""

    def __init__(self, memory):  # app.memory.agentcore.AgentCoreMemory
        self.memory = memory

    async def add_session_to_memory(self, session) -> None:
        turns: list[tuple[str, str]] = []
        for event in session.events:
            text = "".join(p.text or "" for p in (event.content.parts if event.content else []))
            if text.strip():
                turns.append((text, "USER" if event.author == "user" else "ASSISTANT"))
        if turns:
            await self.memory.add_turns(session.user_id, session.id, turns[-20:])

    async def search_memory(
        self, *, app_name: str, user_id: str, query: str
    ) -> SearchMemoryResponse:
        records = await self.memory.search(user_id, query, k=5)
        return SearchMemoryResponse(
            memories=[
                MemoryEntry(
                    content=types.Content(role="user", parts=[types.Part(text=r.text)]),
                    author="agentcore-memory",
                )
                for r in records
            ]
        )


@cache
def _db_sessions(url: str) -> DatabaseSessionService:
    return DatabaseSessionService(db_url=url)


def session_service(provider: str, s: Settings) -> BaseSessionService:
    if provider == "vertex" and s.agent_engine_id:
        from google.adk.sessions import VertexAiSessionService

        return VertexAiSessionService(
            project=s.google_cloud_project,
            location=s.google_cloud_location,
            agent_engine_id=s.agent_engine_id,
        )
    # PRODUCTION (bedrock): DATABASE_URL on RDS/Aurora Postgres; ADK has no AgentCore session service.
    return _db_sessions(f"sqlite+aiosqlite:///{s.data_path / 'adk_sessions.db'}")


_in_memory = InMemoryMemoryService()


def memory_service(provider: str, s: Settings, profile_memory) -> BaseMemoryService:
    if provider == "vertex" and s.agent_engine_id:
        from google.adk.memory import VertexAiMemoryBankService

        return VertexAiMemoryBankService(
            project=s.google_cloud_project,
            location=s.google_cloud_location,
            agent_engine_id=s.agent_engine_id,
        )
    if provider == "bedrock" and s.agentcore_memory_id:
        return AgentCoreMemoryService(profile_memory)
    # ILLUSTRATION: process memory, lost on restart. PRODUCTION: the managed services above.
    return _in_memory
