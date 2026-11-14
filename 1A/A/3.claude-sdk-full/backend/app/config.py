"""All configuration in one place. Nothing else reads os.environ."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "claude-sdk-full"
    anthropic_api_key: str = ""
    # Orchestrator model. Subagents inherit unless AgentDefinition.model overrides.
    model: str = "claude-opus-5"
    # Single-shot calls made directly through the Messages API (writer loop, eval judge).
    judge_model: str = "claude-opus-5"
    effort: Literal["low", "medium", "high", "xhigh", "max"] = "medium"
    max_turns: int = 20
    cors_origins: list[str] = ["http://localhost:4200"]
    log_level: str = "INFO"

    # --- agent runtime scratch space: the SDK stores session transcripts under here ---
    workdir: str = "./data/generated/agent"

    # --- app database the agent can query ---
    db_path: str = "./data/generated/app.db"

    # --- RAG ---
    knowledge_dir: str = "./data/knowledge"
    embedder: Literal["hashing", "voyage"] = "hashing"
    vector_store: Literal["memory", "chroma"] = "memory"
    chroma_path: str = "./data/generated/chroma"
    rag_top_k: int = 3

    # --- external MCP server (weather / tickets) ---
    # stdio: the SDK spawns app/mcp/server.py (illustration).
    # http:  connect to an already-running server at mcp_url (production shape).
    # off:   don't attach it (tests).
    mcp_transport: Literal["stdio", "http", "off"] = "stdio"
    mcp_url: str = "http://localhost:8001/mcp"


@lru_cache
def get_settings() -> Settings:
    return Settings()
