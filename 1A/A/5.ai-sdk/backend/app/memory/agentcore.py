"""Amazon Bedrock AgentCore Memory as long-term memory.

AgentCore Memory has two halves:
  short-term  raw events per (actor, session)      -> create_event / list_events
  long-term   records extracted by *strategies*     -> retrieve_memories(namespace, query)
              (semantic facts, summaries, user preferences), asynchronously, ~a minute later.

`add` writes an event; the memory's semantic strategy (namespace /users/{actorId}/facts, created
by infra/aws/setup_agentcore.py) extracts facts from it. `search` reads the extracted records.
Extraction is asynchronous: a fact remembered seconds ago is not recallable yet. That delay is
the price of managed consolidation (dedup, merge, summarise) and is worth seeing in the demo.

Framework-native uses of the same memory resource:
  Strands    AgentCoreMemorySessionManager      (app/adapters/strands)
  LangGraph  AgentCoreMemorySaver / Store       (app/adapters/langgraph)
  ADK        AgentCoreMemoryService(BaseMemoryService) built on this class (app/adapters/adk)
"""

import asyncio

from app.memory.base import MemoryRecord


def facts_namespace(user_id: str) -> str:
    return f"/users/{user_id}/facts"


class AgentCoreMemory:
    name = "agentcore"

    def __init__(self, memory_id: str, region: str, client=None):
        from bedrock_agentcore.memory import MemoryClient

        self.memory_id = memory_id
        self.client = client or MemoryClient(region_name=region)

    async def add(self, user_id: str, text: str, session_id: str) -> str:
        event = await asyncio.to_thread(
            self.client.create_event,
            memory_id=self.memory_id,
            actor_id=user_id,
            session_id=session_id,
            messages=[(text, "USER")],
        )
        return str(event.get("eventId", ""))

    async def search(self, user_id: str, query: str, k: int = 5) -> list[MemoryRecord]:
        records = await asyncio.to_thread(
            self.client.retrieve_memories,
            memory_id=self.memory_id,
            namespace=facts_namespace(user_id),
            query=query,
            top_k=k,
        )
        out = [
            MemoryRecord(
                text=r.get("content", {}).get("text", ""),
                score=float(r.get("score", 0.0)),
                source="agentcore:long-term",
            )
            for r in records
        ]
        return out[:k]

    async def add_turns(self, user_id: str, session_id: str, turns: list[tuple[str, str]]) -> None:
        """Write a whole conversation turn (used by the ADK memory service)."""
        await asyncio.to_thread(
            self.client.create_event,
            memory_id=self.memory_id,
            actor_id=user_id,
            session_id=session_id,
            messages=turns,
        )
