from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    backend_url: str = "http://localhost:8000"
    service_token: str = "local-mcp-token"  # must be in the backend's SERVICE_TOKENS
    transport: Literal["stdio", "http"] = "stdio"
    host: str = "0.0.0.0"
    port: int = 8001  # Cloud Run sets PORT; see __main__
    timeout_s: float = 120.0  # assessments call the model


@lru_cache
def get_settings() -> Settings:
    return Settings()
