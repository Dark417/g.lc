"""Slice settings, env prefix A_OPENSEARCH_. Defaults mirror terraform/02.02.opensearch-serverless.tf.

The index contract (name + field names + dimensions) is shared with terraform/02.04.knowledge-bases.tf
field_mapping: change one, change both.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenSearchSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_OPENSEARCH_", env_file=".env", extra="ignore")

    collection_name: str = "a-vectors"
    # terraform output aoss_collection_endpoint, host part only (no https://)
    collection_endpoint: str = "COLLECTION_ID.us-east-1.aoss.amazonaws.com"
    port: int = 443
    service: str = "aoss"  # "aoss" = Serverless, "es" = managed OpenSearch Service domain (SigV4 service name)

    # Index contract shared with the Bedrock KB (02.04 storage_configuration.field_mapping)
    index_name: str = "a-kb-index"
    vector_field: str = "embedding"
    text_field: str = "text"
    metadata_field: str = "metadata"
    dimensions: int = 1024  # must equal the KB embedding model dimensions (Titan V2 1024)

    search_pipeline: str = "a-hybrid-pipeline"
    bulk_chunk: int = 500  # docs per _bulk request; keep requests ~5–15 MB (order of magnitude)
    bulk_max_attempts: int = 4  # retries for 429 / 5xx items only
    timeout_s: int = 30


@lru_cache
def get_opensearch_settings() -> OpenSearchSettings:
    return OpenSearchSettings()
