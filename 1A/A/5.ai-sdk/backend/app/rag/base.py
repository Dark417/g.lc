"""Retriever protocol shared by the local store, Bedrock Knowledge Bases, and Vertex RAG Engine."""

from dataclasses import asdict, dataclass
from typing import Protocol


@dataclass
class Passage:
    source: str  # file name or URI, so answers can cite it
    text: str
    score: float

    def as_dict(self) -> dict:
        return asdict(self)


class Retriever(Protocol):
    name: str

    async def search(self, query: str, k: int = 4) -> list[Passage]: ...
