"""Slice settings, env prefix A_KB_. Defaults mirror terraform/02.04.knowledge-bases.tf."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class KbSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_KB_", env_file=".env", extra="ignore")

    knowledge_base_id: str = "KB_ID"  # terraform output kb_id
    data_source_id: str = "DS_ID"  # terraform output kb_data_source_id
    kb_docs_prefix: str = "kb-docs/"
    number_of_results: int = 5  # 1–100; hierarchical chunking may return fewer (children collapse into parents)
    search_type: str = "HYBRID"  # HYBRID | SEMANTIC; unset = Bedrock decides per store
    # Generator: empty = app.shared.config text_model_id (cross-region inference profile id is accepted)
    generator_model_id: str = ""
    rerank_model_arn: str = "arn:aws:bedrock:us-east-1::foundation-model/amazon.rerank-v1:0"
    guardrail_id: str = ""  # 04.01 output; empty = no guardrail on RetrieveAndGenerate
    guardrail_version: str = "1"  # a published version; DRAFT only for testing
    poll_interval_s: float = 10.0
    poll_deadline_s: float = 1800.0


@lru_cache
def get_kb_settings() -> KbSettings:
    return KbSettings()
