"""Slice settings for 01.03 (env prefix A_PROMPTS_).

- prompt_id / prompt_arn = terraform outputs prompt_id / prompt_arn (a-prompt).
- prompt_version_arn = what production calls: "<prompt_arn>:<n>" after CreatePromptVersion. Never DRAFT.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.shared.config import get_settings


class PromptsSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_PROMPTS_", env_file=".env", extra="ignore")

    prompt_name: str = "a-prompt"
    prompt_id: str = "PROMPT_ID"  # terraform output prompt_id
    prompt_version_arn: str = ""  # e.g. arn:aws:bedrock:us-east-1:111122223333:prompt/PROMPT_ID:1
    kms_key_arn: str = ""  # terraform output kms_key_arn; empty -> AWS-owned key for prompts created in code
    model_id: str = ""  # empty -> shared fast_model_id (variants created by create_prompt)

    def model(self) -> str:
        return self.model_id or get_settings().fast_model_id


@lru_cache
def get_prompts_settings() -> PromptsSettings:
    return PromptsSettings()
