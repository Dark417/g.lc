"""Slice settings, env prefix A_EMBEDDINGS_. No Terraform of its own (InvokeModel grant belongs in terraform/01.01.bedrock-converse.tf)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class EmbeddingsSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_EMBEDDINGS_", env_file=".env", extra="ignore")

    # Titan Text Embeddings V2 (model id from app.shared.config: embed_model_id).
    dimensions: int = 1024  # 256 | 512 | 1024 (default 1024): smaller = less storage and faster search, lower recall
    normalize: bool = True  # unit-length output; required for dot product == cosine
    # Cohere on Bedrock, shown for contrast (asymmetric input_type).
    cohere_model_id: str = "cohere.embed-english-v3"
    batch_workers: int = 8  # parallel InvokeModel calls in embed_batch; bounded by the account's TPM/RPM quota


@lru_cache
def get_embeddings_settings() -> EmbeddingsSettings:
    return EmbeddingsSettings()
