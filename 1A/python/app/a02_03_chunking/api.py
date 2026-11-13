"""REST adapter mounted at /chunking. Pure logic: no AWS call (semantic chunking uses the hashing fake)."""

from dataclasses import asdict
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.a02_03_chunking import bedrock_config, chunkers
from app.a02_03_chunking.config import get_chunking_settings
from app.a02_03_chunking.domain import ChunkingStrategy

router = APIRouter()


class ChunkRequest(BaseModel):
    text: str = Field(min_length=1)
    strategy: ChunkingStrategy = ChunkingStrategy.FIXED_SIZE


@router.post("/chunk")
def chunk(body: ChunkRequest) -> dict[str, Any]:
    s = get_chunking_settings()
    if body.strategy is ChunkingStrategy.FIXED_SIZE:
        out = {"chunks": chunkers.fixed_size_chunks(body.text, s.max_tokens, s.overlap_percentage)}
    elif body.strategy is ChunkingStrategy.HIERARCHICAL:
        parents, children = chunkers.hierarchical_chunks(body.text, s.parent_max_tokens, s.child_max_tokens, s.overlap_tokens)
        out = {"parents": parents, "children": children}
    elif body.strategy is ChunkingStrategy.SEMANTIC:
        out = {
            "chunks": chunkers.semantic_chunks(
                body.text, chunkers.HashingEmbedder(), s.buffer_size, s.breakpoint_percentile_threshold, s.semantic_max_tokens
            )
        }
    else:
        out = {"chunks": chunkers.no_chunking(body.text)}
    return {k: [asdict(c) for c in v] for k, v in out.items()}


@router.post("/recursive")
def recursive(body: ChunkRequest) -> list[str]:
    return chunkers.recursive_split(body.text, get_chunking_settings().max_tokens)


@router.get("/bedrock-config/{strategy}")
def bedrock(strategy: ChunkingStrategy) -> dict[str, Any]:
    return bedrock_config.config_for(strategy)
