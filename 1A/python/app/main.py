"""FastAPI entry point for every 1A slice.

- A slice router is imported and mounted only when its name is in A_ENABLED.
- With A_ENABLED empty the app starts with no cloud access and no slice imports.
- Each slice module exposes `router` in app/api/<component>.py.
"""

import importlib

from fastapi import FastAPI

from app.shared.config import get_settings

# slice name (used in A_ENABLED) -> component module name under app/api/
SLICES: dict[str, str] = {
    "converse": "_01bedrock_01converse",
    "customization": "_01bedrock_02customization",
    "prompts": "_01bedrock_03prompt_management",
    "flows": "_01bedrock_04prompt_flows",
    "prompting": "_01bedrock_05prompt_engineering",
    "embeddings": "_02rag_01embeddings",
    "opensearch": "_02rag_02opensearch",
    "chunking": "_02rag_03chunking",
    "kb": "_02rag_04knowledge_bases",
    "bda": "_03data_01data_automation",
    "glue_dq": "_03data_02glue_data_quality",
    "transcribe": "_03data_03transcribe",
    "comprehend": "_03data_04comprehend",
    "guardrails": "_04safety_01guardrails",
    "pii": "_04safety_02pii_redaction",
    "evals": "_04safety_03evaluations",
    "observability": "_05ops_01observability",
}


def create_app() -> FastAPI:
    app = FastAPI(title="a", version="0.1.0")
    enabled = get_settings().enabled_slices()
    unknown = enabled - SLICES.keys()
    if unknown:
        raise ValueError(f"Unknown slices in A_ENABLED: {sorted(unknown)}")
    for name in sorted(enabled):
        module = importlib.import_module(f"app.api.{SLICES[name]}")
        app.include_router(module.router, prefix=f"/{name}", tags=[name])

    @app.get("/health")
    def health() -> dict[str, object]:
        return {"status": "ok", "slices": sorted(enabled)}

    return app


app = create_app()
