"""App factory. `uvicorn app.main:app`.

With ENABLE_ADK_WEB=true the app *is* ADK's FastAPI server (dev UI at /dev-ui plus ADK's own
/run, /run_sse, /apps/... routes) with our /api/v1 routers added on top. Both use the same
container-backed services. With it off, a plain FastAPI app with only our routes.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_chat, routes_documents, routes_misc, routes_rules
from app.config import Settings
from app.container import (
    Container,
    build_container,
    get_container,
    register_adk_services,
    set_container,
)

AGENTS_DIR = Path(__file__).parent / "adk_apps"


def create_app(
    settings: Settings | None = None, container: Container | None = None, *, agent_model=None
) -> FastAPI:
    """`agent_model` overrides the Gemini model (tests pass a scripted BaseLlm)."""
    if container is None:
        container = build_container(settings) if settings else get_container()
    settings = container.settings
    settings.export_model_env()
    set_container(container)  # the ADK agent module resolves the same instance
    logging.basicConfig(level=settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        from google.adk.runners import Runner

        from app.agents.builder import build_app
        from app.services.chat import ChatService

        await container.init()
        adk_app = build_app(container, model=agent_model)
        runner = Runner(
            app=adk_app,
            session_service=container.sessions,
            memory_service=container.memory,
            artifact_service=container.artifacts,
        )
        app.state.container = container
        app.state.chat = ChatService(
            runner=runner,
            sessions=container.sessions,
            app_name=settings.app_name,
            memory=container.memory,
        )
        try:
            yield
        finally:
            await container.close()

    if settings.enable_adk_web:
        from google.adk.cli.fast_api import get_fast_api_app

        register_adk_services(container)
        app = get_fast_api_app(
            agents_dir=str(AGENTS_DIR),
            session_service_uri="container://",
            memory_service_uri="container://",
            artifact_service_uri="container://",
            allow_origins=settings.cors_list,
            web=True,
            lifespan=lifespan,
        )
    else:
        app = FastAPI(title="proposal-review-backend", lifespan=lifespan)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_list,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.state.container = container
    app.include_router(routes_misc.router)
    app.include_router(routes_rules.router)
    app.include_router(routes_documents.router)
    app.include_router(routes_chat.router)
    return app


def __getattr__(name: str):
    # Lazy `app` so importing this module (e.g. in tests) doesn't build the default container.
    if name == "app":
        return create_app()
    raise AttributeError(name)
