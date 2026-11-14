"""All configuration in one place. Nothing else reads os.environ.

Every swappable component (sessions, embedder, vector store, MCP transport) is selected here
by a string, and resolved once in a factory. See docs/CONVENTIONS.md "Illustration vs production".
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "angular-full"
    google_api_key: str = ""
    model: str = "gemini-2.5-flash"
    cors_origins: list[str] = ["http://localhost:4200"]
    log_level: str = "INFO"

    # --- sessions (conversation memory) ---
    session_backend: Literal["memory", "sqlite"] = "memory"
    session_db_url: str = "sqlite+aiosqlite:///./data/generated/sessions.db"

    # --- app database the agent can query ---
    db_path: str = "./data/generated/app.db"

    # --- RAG ---
    knowledge_dir: str = "./data/knowledge"
    embedder: Literal["hashing", "gemini"] = "hashing"
    vector_store: Literal["memory", "chroma"] = "memory"
    chroma_path: str = "./data/generated/chroma"
    rag_top_k: int = 3

    # --- MCP ---
    # stdio: spawn app/mcp/server.py as a subprocess (illustration).
    # http:  connect to an already-running MCP server at mcp_url (production shape).
    # off:   don't attach MCP tools (used by tests).
    mcp_transport: Literal["stdio", "http", "off"] = "stdio"
    mcp_url: str = "http://localhost:8001/mcp"


@lru_cache
def get_settings() -> Settings:
    return Settings()
