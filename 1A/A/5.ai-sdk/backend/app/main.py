"""App factory. `uvicorn app.main:app`.

One FastAPI app, one entrance (POST /v1/runs). Framework adapters load lazily on first use.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api import routes_catalog, routes_runs, routes_state
from app.container import Container, build_container
from app.telemetry import instrument_app, setup_telemetry

STATIC = Path(__file__).parent / "static"


def create_app(container: Container | None = None) -> FastAPI:
    container = container or build_container()
    settings = container.settings
    logging.basicConfig(level=settings.log_level)
    setup_telemetry(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.container = container
        yield

    app = FastAPI(
        title="ai-sdk: one entrance for ADK, LangGraph, Strands, Claude",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.container = container
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(routes_runs.router)
    app.include_router(routes_catalog.router)
    app.include_router(routes_state.router)

    @app.get("/healthz", tags=["ops"])
    async def healthz() -> dict:
        return {"status": "ok"}

    @app.get("/", include_in_schema=False)
    async def playground() -> FileResponse:
        return FileResponse(STATIC / "index.html")

    instrument_app(app, settings)
    return app


app = create_app()
