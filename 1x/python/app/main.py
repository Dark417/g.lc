"""FastAPI entry point for every 1x slice.

- A slice router is imported and mounted only when its name is in X_ENABLED.
- With X_ENABLED empty the app starts with no cloud access and no slice imports.
- Each slice module exposes `router` in app/<package>/api.py.
"""

import importlib

from fastapi import FastAPI

from app.shared.config import get_settings

# slice name (used in X_ENABLED) -> package under app/
SLICES: dict[str, str] = {
    "principles": "x02_01_principles",
    "aurora": "x03_01_aurora",
    "dynamodb": "x03_02_dynamodb",
    "s3": "x03_03_s3",
    "athena": "x04_01_athena",
    "redshift": "x04_02_redshift",
    "kinesis": "x05_01_kinesis",
    "kafka": "x05_02_kafka",
}


def create_app() -> FastAPI:
    app = FastAPI(title="x", version="0.1.0")
    enabled = get_settings().enabled_slices()
    unknown = enabled - SLICES.keys()
    if unknown:
        raise ValueError(f"Unknown slices in X_ENABLED: {sorted(unknown)}")
    for name in sorted(enabled):
        module = importlib.import_module(f"app.{SLICES[name]}.api")
        app.include_router(module.router, prefix=f"/{name}", tags=[name])

    @app.get("/health")
    def health() -> dict[str, object]:
        return {"status": "ok", "slices": sorted(enabled)}

    return app


app = create_app()
