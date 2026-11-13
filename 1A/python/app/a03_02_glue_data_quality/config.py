"""Slice settings, env prefix A_GLUE_DQ_. Defaults mirror terraform/03.02.glue-data-quality.tf."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class GlueDqSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_GLUE_DQ_", env_file=".env", extra="ignore")

    database: str = "a_ai_data"
    table: str = "docs_metadata"
    ruleset_name: str = "a-docs-metadata-dq"
    role_arn: str = ""  # terraform output glue_dq_role_arn
    number_of_workers: int = 2  # Glue default is 5; fewer workers = cheaper, slower (check the minimum in the API reference)
    timeout_minutes: int = 30  # Glue default 2880 (48 h); cap it, a stuck run keeps billing
    results_s3_prefix: str = ""  # e.g. s3://<bucket>/glue/dq-results/ ; empty = no S3 copy
    gate_min_score: float = 0.95  # fraction of rules that must pass for the gate
    poll_deadline_s: float = 1800.0


@lru_cache
def get_glue_dq_settings() -> GlueDqSettings:
    return GlueDqSettings()
