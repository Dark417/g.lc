"""App factory. `uvicorn app.main:app`.

Startup order is explicit here: DB -> RAG index -> agent options (tools server, MCP config,
subagents) -> service. Nothing is built at import time. The SDK spawns the Claude Code CLI per
request (or per ClaudeSDKClient connection), so there is nothing to close on shutdown.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_chat, routes_debug, routes_health
from app.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    logging.basicConfig(level=settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        from app.agents.factory import build_options
        from app.db.database import init_db
        from app.rag.factory import build_retriever
        from app.services.chat_service import ClaudeChatService

        if not settings.anthropic_api_key:
            logging.warning("ANTHROPIC_API_KEY is empty; chat requests will fail.")

        Path(settings.workdir).mkdir(parents=True, exist_ok=True)
        init_db(settings.db_path)
        retriever = build_retriever(settings)
        options = build_options(settings, retriever=retriever)

        app.state.retriever = retriever
        app.state.chat_service = ClaudeChatService(options=options)
        yield

    app = FastAPI(title="claude-sdk-full-backend", version="0.1.0", lifespan=lifespan)
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


app = create_app()
