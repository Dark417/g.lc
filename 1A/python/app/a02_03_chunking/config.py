"""Slice settings, env prefix A_CHUNKING_. Defaults mirror the Bedrock KB defaults (console, read 2026-11).

No Terraform here: the chunking config lives on the KB data source in terraform/02.04.knowledge-bases.tf.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class ChunkingSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_CHUNKING_", env_file=".env", extra="ignore")

    # FIXED_SIZE
    max_tokens: int = 300
    overlap_percentage: int = 20
    # HIERARCHICAL
    parent_max_tokens: int = 1500
    child_max_tokens: int = 300
    overlap_tokens: int = 60
    # SEMANTIC
    semantic_max_tokens: int = 300
    buffer_size: int = 0  # Bedrock allows 0 or 1 surrounding sentences
    breakpoint_percentile_threshold: int = 95  # 50–99: higher = fewer, larger chunks
    # Local approximation: English averages ~0.75 words per token, i.e. ~1.3 tokens per word (order of magnitude).
    tokens_per_word: float = 1.3


@lru_cache
def get_chunking_settings() -> ChunkingSettings:
    return ChunkingSettings()
