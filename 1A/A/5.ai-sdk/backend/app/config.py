"""All configuration in one place. Nothing else reads os.environ.

Three provider branches (docs/design/03-cloud-branches.md):
  raw      direct model APIs, state on local disk
  bedrock  AWS: Bedrock models, AgentCore Memory/Browser/Code Interpreter, Bedrock KB, Guardrails
  vertex   GCP: Vertex models, Agent Engine Sessions/Memory Bank, RAG Engine, Model Armor
Managed services are optional per branch: unset ids fall back to the local implementation.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent

Vendor = Literal["anthropic", "gemini"]


def _csv(value: str) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "ai-sdk"
    log_level: str = "INFO"
    cors_origins: str = "*"
    data_dir: str = "./data/generated"
    corpus_dir: str = "./data/corpus"

    # --- raw: direct APIs ---
    anthropic_api_key: str = ""
    google_api_key: str = ""
    raw_vendor: Vendor = "anthropic"  # default model vendor for adk / langgraph / strands on raw
    anthropic_model: str = "claude-opus-5"
    gemini_model: str = "gemini-2.5-flash"

    # --- bedrock: AWS ---
    aws_region: str = ""
    # Converse API model id or inference profile (adk via LiteLLM, langgraph, strands).
    bedrock_model_id: str = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    # Claude in Amazon Bedrock, Messages API shape ("Mantle"); ids carry an `anthropic.` prefix.
    bedrock_anthropic_model: str = "anthropic.claude-opus-5"
    # Optional ANTHROPIC_MODEL for the Claude Agent SDK on Bedrock; empty = the CLI's default.
    bedrock_claude_code_model: str = ""
    agentcore_memory_id: str = ""
    bedrock_kb_id: str = ""
    bedrock_guardrail_id: str = ""
    bedrock_guardrail_version: str = "DRAFT"
    agentcore_browser: bool = False
    agentcore_code_interpreter: bool = False

    # --- vertex: GCP ---
    google_cloud_project: str = ""
    google_cloud_location: str = "us-central1"
    vertex_vendor: Vendor = "gemini"
    vertex_gemini_model: str = "gemini-2.5-flash"
    vertex_claude_model: str = "claude-opus-5"
    vertex_claude_region: str = "global"
    agent_engine_id: str = ""  # Agent Engine resource id: Sessions + Memory Bank
    vertex_rag_corpus: str = ""  # projects/.../locations/.../ragCorpora/...
    model_armor_template: str = ""  # projects/.../locations/.../templates/...

    # --- tools ---
    playwright_chromium_path: str = ""  # e.g. /opt/pw-browsers/chromium; empty = Playwright default
    browser_allowed_hosts: str = ""  # comma-separated; empty = any public host
    playwright_mcp_enabled: bool = False  # external MCP server via `npx @playwright/mcp`
    cli_timeout_s: float = 10.0

    # --- state / cache server (docs/design/07-state-and-memory.md) ---
    # redis://, rediss:// (TLS: ElastiCache in-transit encryption), Valkey, Memorystore. Empty = the
    # in-process session registry and lock (one replica only).
    redis_url: str = ""
    session_lock_ttl_s: int = 300
    llm_cache_ttl_s: int = 3600
    # langgraph:memory checkpointer on bedrock: agentcore | dynamodb | valkey | sqlite
    langgraph_checkpointer: str = "agentcore"
    dynamodb_checkpoint_table: str = "ai-sdk-checkpoints"
    s3_checkpoint_bucket: str = ""  # DynamoDBSaver offloads large checkpoints here
    valkey_url: str = ""  # ElastiCache for Valkey endpoint for ValkeySaver; defaults to REDIS_URL
    strands_s3_session_bucket: str = ""  # strands on bedrock: S3SessionManager

    # --- runs ---
    max_llm_calls: int = 20
    guardrails_enabled: bool = True
    judge_model: str = "claude-opus-5"

    # --- observability ---
    otel_exporter: Literal["none", "console", "otlp", "gcp"] = "none"
    otel_exporter_otlp_endpoint: str = "http://localhost:4318"
    otel_service_name: str = "ai-sdk-backend"
    otel_capture_content: bool = False

    # ------------------------------------------------------------------ helpers

    @property
    def data_path(self) -> Path:
        p = Path(self.data_dir)
        p = p if p.is_absolute() else BACKEND_DIR / p
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def corpus_path(self) -> Path:
        p = Path(self.corpus_dir)
        return p if p.is_absolute() else BACKEND_DIR / p

    @property
    def allowed_hosts(self) -> list[str]:
        return [h.lower() for h in _csv(self.browser_allowed_hosts)]

    @property
    def cors_origin_list(self) -> list[str]:
        return _csv(self.cors_origins)

    @property
    def agent_engine_name(self) -> str:
        """Full resource name; accepts a bare id or a full name."""
        if self.agent_engine_id.startswith("projects/"):
            return self.agent_engine_id
        return (
            f"projects/{self.google_cloud_project}/locations/{self.google_cloud_location}"
            f"/reasoningEngines/{self.agent_engine_id}"
        )

    def provider_missing(self, provider: str) -> list[str]:
        """Env vars a provider branch needs before it can run anything."""
        if provider == "raw":
            return (
                []
                if (self.anthropic_api_key or self.google_api_key)
                else ["ANTHROPIC_API_KEY or GOOGLE_API_KEY"]
            )
        if provider == "bedrock":
            return [] if self.aws_region else ["AWS_REGION (+ AWS credentials)"]
        if provider == "vertex":
            return [] if self.google_cloud_project else ["GOOGLE_CLOUD_PROJECT (+ ADC)"]
        return [f"unknown provider {provider!r}"]

    def subprocess_env(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        """Environment for child processes (MCP servers, the Claude Code CLI).

        MCP stdio clients pass only a minimal env by default, so we hand over PATH/HOME plus our
        settings explicitly. Secrets are added by the caller only when the child needs them.
        """
        env = {k: v for k, v in os.environ.items() if k in _CHILD_ENV_KEYS}
        env["DATA_DIR"] = str(self.data_path)
        env["CORPUS_DIR"] = str(self.corpus_path)
        env.update(extra or {})
        return env


_CHILD_ENV_KEYS = {
    "PATH", "HOME", "LANG", "LC_ALL", "TMPDIR", "USER",
    "HTTPS_PROXY", "HTTP_PROXY", "NO_PROXY", "SSL_CERT_FILE", "REQUESTS_CA_BUNDLE",
    "NODE_EXTRA_CA_CERTS", "PLAYWRIGHT_BROWSERS_PATH",
    "AWS_PROFILE", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN",
    "GOOGLE_APPLICATION_CREDENTIALS", "CLOUDSDK_CONFIG",
}  # fmt: skip


@lru_cache
def get_settings() -> Settings:
    return Settings()
