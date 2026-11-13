"""Slice settings for 01.01 (env prefix A_CONVERSE_).

- Model IDs default to the shared ones (app.shared.config); override per slice only to experiment.
- app_profile_arn = terraform output converse_app_profile_arn (application inference profile a-app-profile).
- Every value is config, never code: switching models is an env change, not a redeploy.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.shared.config import get_settings


class ConverseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_CONVERSE_", env_file=".env", extra="ignore")

    model_id: str = ""  # empty -> shared text_model_id (us. cross-Region inference profile)
    fast_model_id: str = ""  # empty -> shared fast_model_id
    app_profile_arn: str = ""  # terraform output converse_app_profile_arn; empty -> skip that demo

    # inferenceConfig defaults. maxTokens also reserves tokens-per-minute quota on some models: keep it tight.
    max_tokens: int = 1024
    temperature: float = 0.2  # 0..1; low for extraction/tools, higher for creative text
    top_p: float = 0.9  # nucleus sampling; tune temperature OR top_p, not both
    send_sampling: bool = True  # False for models that reject temperature/topP (some newer Claude models)

    max_tool_rounds: int = 5  # hard cap on the tool-use loop
    history_max_messages: int = 20  # sliding window for multi-turn (kept even so roles stay paired)
    app_retry_attempts: int = 3  # app-level retries on top of the SDK's adaptive retries

    def text_model(self) -> str:
        return self.model_id or get_settings().text_model_id

    def fast_model(self) -> str:
        return self.fast_model_id or get_settings().fast_model_id


@lru_cache
def get_converse_settings() -> ConverseSettings:
    return ConverseSettings()
