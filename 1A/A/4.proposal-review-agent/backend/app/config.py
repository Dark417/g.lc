"""All configuration in one place. Nothing else reads or writes os.environ.

Every swappable component is selected here by a string and resolved once in app/container.py.
See docs/design/02-data-model.md for what each option means.
"""

import os
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


def _csv(value: str) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Must equal the ADK agent directory name (app/adk_apps/compliance_agent) so the dev UI and
    # the portal read and write the same sessions.
    app_name: str = "compliance_agent"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:4200"
    enable_adk_web: bool = True  # mounts ADK's dev UI at /dev-ui. No auth: keep off in prod.

    # --- models (Gemini API key locally, Vertex AI on GCP) ---
    model: str = "gemini-2.5-flash"
    embedding_model: str = "gemini-embedding-001"
    embedding_dim: int = 768
    google_api_key: str = ""
    google_genai_use_vertexai: bool = False
    google_cloud_project: str = ""
    google_cloud_location: str = "us-central1"

    # --- relational: rules, assessments, sessions, memories, chunks ---
    database_url: str = "sqlite+aiosqlite:///./data/generated/app.db"
    vector_store: Literal["sql", "pgvector", "vertex"] = "sql"
    embedder: Literal["hashing", "gemini"] = "hashing"

    # --- document store ---
    doc_store: Literal["file", "mongo"] = "file"
    doc_store_path: str = "./data/generated/documents.json"
    mongo_url: str = "mongodb://localhost:27017"
    mongo_db: str = "compliance"

    # --- blobs + ADK artifacts ---
    blob_store: Literal["local", "gcs"] = "local"
    blob_dir: str = "./data/generated/blobs"
    gcs_bucket: str = ""
    artifact_dir: str = "./data/generated/artifacts"

    # --- long-term memory ---
    memory_backend: Literal["sql", "vertex"] = "sql"
    agent_engine_id: str = ""  # for MEMORY_BACKEND=vertex (Agent Engine Memory Bank)
    memory_min_score: float = 0.2

    # --- auth ---
    auth_mode: Literal["dev", "iap"] = "dev"
    dev_default_user: str = "user@example.com"
    admin_users: str = "admin@example.com"  # comma-separated emails
    service_tokens: str = ""  # comma-separated; X-Service-Token for the MCP server
    iap_audience: str = ""

    # --- assessment / ingestion tuning ---
    assess_inline_rule_limit: int = 40
    assess_top_k_rules: int = 15
    assess_top_k_passages: int = 6
    sync_ingest_max_mb: int = 10

    @property
    def admins(self) -> set[str]:
        return {a.lower() for a in _csv(self.admin_users)}

    @property
    def service_token_set(self) -> set[str]:
        return set(_csv(self.service_tokens))

    @property
    def cors_list(self) -> list[str]:
        return _csv(self.cors_origins)

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    def export_model_env(self) -> None:
        """ADK's Gemini model and google-genai read credentials from the process environment.

        pydantic-settings reads `.env` but does not export it, so a bare `uvicorn` run would
        not see GOOGLE_API_KEY. Export once at startup. Real env vars always win.
        """
        pairs = {"GOOGLE_API_KEY": self.google_api_key}
        if self.google_genai_use_vertexai:
            pairs |= {
                "GOOGLE_GENAI_USE_VERTEXAI": "TRUE",
                "GOOGLE_CLOUD_PROJECT": self.google_cloud_project,
                "GOOGLE_CLOUD_LOCATION": self.google_cloud_location,
            }
        for key, value in pairs.items():
            if value:
                os.environ.setdefault(key, value)


@lru_cache
def get_settings() -> Settings:
    return Settings()
