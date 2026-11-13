"""Slice settings for 01.05 (env prefix A_PROMPTING_).

- No Terraform of its own: calls Converse with the 01.01 permissions on the app role.
- Per-model capability flags: newer models reject some knobs (sampling, prefill, forced toolChoice).
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.shared.config import get_settings


class PromptingSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_PROMPTING_", env_file=".env", extra="ignore")

    model_id: str = ""  # empty -> shared text_model_id
    max_tokens: int = 1024
    send_sampling: bool = True  # False for models that reject temperature/topP
    supports_forced_tool: bool = True  # False for models that only accept toolChoice=auto
    supports_native_schema: bool = False  # True where Converse outputConfig json_schema is supported
    max_repairs: int = 2  # validate-and-repair retries (each = one more model call)
    injection_block_score: int = 3  # heuristic detector score at which documents are dropped

    def model(self) -> str:
        return self.model_id or get_settings().text_model_id


@lru_cache
def get_prompting_settings() -> PromptingSettings:
    return PromptingSettings()
