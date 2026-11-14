"""All configuration in one place. Nothing else reads os.environ."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "chatbot"
    # ADK reads GOOGLE_API_KEY from the environment itself; we declare it here so
    # startup fails loudly if it is missing instead of failing on the first request.
    google_api_key: str = ""
    model: str = "gemini-2.5-flash"
    cors_origins: list[str] = ["http://localhost:3000"]
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
