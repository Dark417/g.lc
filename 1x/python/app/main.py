"""FastAPI entry point for every 1x slice.

- A slice router is imported and mounted only when its name is in X_ENABLED.
- With X_ENABLED empty the app starts with no cloud access and no slice imports.
- Each slice module exposes `router` in app/api/<module>.py.
"""

import importlib

from fastapi import FastAPI

from app.shared.config import get_settings

# slice name (used in X_ENABLED) -> module under app/api/
SLICES: dict[str, str] = {
    "principles": "_01core_01principles",
    "aurora": "_03db_01aurora",
    "dynamodb": "_03db_02dynamodb",
    "s3": "_03db_03s3",
    "mongodb": "_03db_04mongodb",
    "athena": "_05analytics_01athena",
    "redshift": "_05analytics_02redshift",
    "kinesis": "_02messaging_01kinesis",
    "kafka": "_02messaging_02kafka",
}


def create_app() -> FastAPI:
    app = FastAPI(title="x", version="0.1.0")
    enabled = get_settings().enabled_slices()
    unknown = enabled - SLICES.keys()
    if unknown:
        raise ValueError(f"Unknown slices in X_ENABLED: {sorted(unknown)}")
    for name in sorted(enabled):
        module = importlib.import_module(f"app.api.{SLICES[name]}")
        app.include_router(module.router, prefix=f"/{name}", tags=[name])

    @app.get("/health")
    def health() -> dict[str, object]:
        return {"status": "ok", "slices": sorted(enabled)}

    return app


app = create_app()
