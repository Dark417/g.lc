"""Long-term memory: facts about a user that outlive one session.

This is the one state layer the four frameworks can share, so it sits behind the neutral
`remember` / `recall` tools. Short-term conversation state stays framework-native.
"""

from dataclasses import asdict, dataclass
from typing import Protocol


@dataclass
class MemoryRecord:
    text: str
    score: float
    source: str  # backend name, or session id the fact came from

    def as_dict(self) -> dict:
        return asdict(self)


class LongTermMemory(Protocol):
    name: str

    async def add(self, user_id: str, text: str, session_id: str) -> str: ...

    async def search(self, user_id: str, query: str, k: int = 5) -> list[MemoryRecord]: ...
