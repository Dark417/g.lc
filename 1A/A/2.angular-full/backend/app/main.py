"""App factory. `uvicorn app.main:app`.

Startup order matters and is explicit here: DB -> RAG index -> MCP toolset -> agent tree ->
session store -> service. Nothing is built at import time.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_chat, routes_debug, routes_health
from app.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    logging.basicConfig(level=settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        from app.agents.factory import build_root_agent
        from app.db.database import init_db
        from app.rag.factory import build_retriever
        from app.services.chat_service import AdkChatService
        from app.tools.mcp_tools import build_mcp_toolset

        if not settings.google_api_key:
            logging.warning("GOOGLE_API_KEY is empty; chat requests will fail.")

        init_db(settings.db_path)
        retriever = build_retriever(settings)
        mcp_toolset = build_mcp_toolset(settings)
        agent = build_root_agent(settings, retriever=retriever, mcp_toolset=mcp_toolset)

        app.state.retriever = retriever
        app.state.chat_service = AdkChatService(
            app_name=settings.app_name, agent=agent, session_service=_session_service(settings)
        )
        try:
            yield
        finally:
            if mcp_toolset is not None:
                await mcp_toolset.close()  # stops the stdio child process

    app = FastAPI(title="angular-full-backend", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(routes_health.router)
    app.include_router(routes_chat.router)
    app.include_router(routes_debug.router)
    return app


def _session_service(settings: Settings):
    if settings.session_backend == "sqlite":
        # Survives restarts. Same class works with Postgres: SESSION_DB_URL=postgresql+asyncpg://...
        from pathlib import Path

        from google.adk.sessions import DatabaseSessionService

        Path(settings.session_db_url.split("///")[-1]).parent.mkdir(parents=True, exist_ok=True)
        return DatabaseSessionService(db_url=settings.session_db_url)
    from google.adk.sessions import InMemorySessionService

    return InMemorySessionService()


app = create_app()
