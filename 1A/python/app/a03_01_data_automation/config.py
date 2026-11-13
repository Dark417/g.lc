"""Slice settings, env prefix A_BDA_. Defaults mirror terraform/03.01.data-automation.tf names."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class BdaSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_BDA_", env_file=".env", extra="ignore")

    project_name: str = "a-docs"
    blueprint_name: str = "a-invoice"
    project_arn: str = ""  # terraform output bda_project_arn
    blueprint_arn: str = ""  # terraform output bda_blueprint_arn
    # Cross-region inference profile BDA requires. Verify the exact id/Region for your account.
    profile_arn: str = ""  # arn:aws:bedrock:<region>:<account>:data-automation-profile/us.data-automation-v1
    input_prefix: str = "bda/input/"
    output_prefix: str = "bda/output/"
    stage: str = "LIVE"  # LIVE | DEVELOPMENT: which project stage to run
    poll_deadline_s: float = 600.0


@lru_cache
def get_bda_settings() -> BdaSettings:
    return BdaSettings()
