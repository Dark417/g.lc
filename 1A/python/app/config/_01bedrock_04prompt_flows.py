"""Slice settings for 01.04 (env prefix A_FLOWS_).

- flow_id / execution_role_arn = terraform outputs flow_id / flow_role_arn.
- flow_alias_id = the alias created by create_flow_alias; invoke aliases, never the DRAFT.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.shared.config import get_settings


class FlowsSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_FLOWS_", env_file=".env", extra="ignore")

    flow_id: str = "FLOW_ID"  # terraform output flow_id (a-flow)
    flow_alias_id: str = "ALIAS_ID"  # from create_flow_alias ("live")
    execution_role_arn: str = "arn:aws:iam::ACCOUNT_ID:role/a-flow-role"  # terraform output flow_role_arn
    kms_key_arn: str = ""  # terraform output kms_key_arn; empty -> AWS-owned key for flows created in code
    model_id: str = ""  # empty -> shared fast_model_id
    prepare_timeout_s: int = 120
    enable_trace: bool = False  # traces show node inputs/outputs: great for debugging, may contain PII

    def model(self) -> str:
        return self.model_id or get_settings().fast_model_id


@lru_cache
def get_flows_settings() -> FlowsSettings:
    return FlowsSettings()
