"""Base settings from environment variables (pydantic-settings).

- Every slice is off unless listed in A_ENABLED (comma list), e.g. A_ENABLED=converse,guardrails.
- Shared names match Terraform outputs in 1A/terraform (prefix "a").
- Slice-specific settings live in the slice's own config.py (env prefix A_<SLICE>_), so slices never edit this file.
- No secrets: AWS uses the default credential chain.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_", env_file=".env", extra="ignore")

    enabled: str = ""
    aws_region: str = "us-east-1"
    prefix: str = "a"
    data_bucket: str = "a-ai-data-ACCOUNT_ID"  # terraform output data_bucket (00.05)

    # Default models. Cross-region inference profile IDs ("us." prefix) route across regions for capacity.
    text_model_id: str = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    fast_model_id: str = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
    embed_model_id: str = "amazon.titan-embed-text-v2:0"

    def enabled_slices(self) -> set[str]:
        return {s.strip() for s in self.enabled.split(",") if s.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
