"""Slice settings, env prefix A_COMPREHEND_."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class ComprehendSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_COMPREHEND_", env_file=".env", extra="ignore")

    default_language: str = "en"  # BCP-47-ish code; Detect* APIs support a limited language list
    max_text_bytes: int = 5000  # keep sync input small (documented limits differ per API: check the quota page)
    batch_size: int = 25  # BatchDetect* documents per call (documented maximum, check the quota page)
    min_entity_score: float = 0.8  # drop low-confidence entities
    negative_threshold: float = 0.7  # NEGATIVE score above this routes to the strong model


@lru_cache
def get_comprehend_settings() -> ComprehendSettings:
    return ComprehendSettings()
