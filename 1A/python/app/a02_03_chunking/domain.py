"""Chunk model, strategies, and the Embedder port (semantic chunking needs embeddings; tests inject a fake)."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol

Vector = list[float]


class ChunkingStrategy(StrEnum):
    # Bedrock KB chunkingStrategy values (bedrock-agent CreateDataSource)
    FIXED_SIZE = "FIXED_SIZE"
    HIERARCHICAL = "HIERARCHICAL"
    SEMANTIC = "SEMANTIC"
    NONE = "NONE"  # one chunk per file (or pre-chunked files / custom Lambda chunking)


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    start_word: int  # offsets in words into the source: lets you cite and re-chunk deterministically
    end_word: int
    level: str = "leaf"  # "parent" | "child" | "leaf"
    parent_id: str | None = None  # hierarchical: child -> parent link
    metadata: dict[str, object] = field(default_factory=dict)


class Embedder(Protocol):
    def embed(self, text: str) -> Vector: ...
