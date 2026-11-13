"""FastAPI entry point for every 1A slice.

- A slice router is imported and mounted only when its name is in A_ENABLED.
- With A_ENABLED empty the app starts with no cloud access and no slice imports.
- Each slice module exposes `router` in app/<package>/api.py.
"""

import importlib

from fastapi import FastAPI

from app.shared.config import get_settings

# slice name (used in A_ENABLED) -> package under app/
SLICES: dict[str, str] = {
    "converse": "a01_01_converse",
    "customization": "a01_02_customization",
    "prompts": "a01_03_prompt_management",
    "flows": "a01_04_prompt_flows",
    "prompting": "a01_05_prompt_engineering",
    "embeddings": "a02_01_embeddings",
    "opensearch": "a02_02_opensearch",
    "chunking": "a02_03_chunking",
    "kb": "a02_04_knowledge_bases",
    "bda": "a03_01_data_automation",
    "glue_dq": "a03_02_glue_data_quality",
    "transcribe": "a03_03_transcribe",
    "comprehend": "a03_04_comprehend",
    "guardrails": "a04_01_guardrails",
    "pii": "a04_02_pii_redaction",
    "evals": "a04_03_evaluations",
    "observability": "a05_01_observability",
}


def create_app() -> FastAPI:
    app = FastAPI(title="a", version="0.1.0")
    enabled = get_settings().enabled_slices()
    unknown = enabled - SLICES.keys()
    if unknown:
        raise ValueError(f"Unknown slices in A_ENABLED: {sorted(unknown)}")
    for name in sorted(enabled):
        module = importlib.import_module(f"app.{SLICES[name]}.api")
        app.include_router(module.router, prefix=f"/{name}", tags=[name])

    @app.get("/health")
    def health() -> dict[str, object]:
        return {"status": "ok", "slices": sorted(enabled)}

    return app


app = create_app()
