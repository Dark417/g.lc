"""App factory. `uvicorn app.main:app`."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_chat, routes_health
from app.config import Settings, get_settings
from app.services.chat_service import AdkChatService


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    logging.basicConfig(level=settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Import here so `create_app` (and the test suite) never triggers agent construction
        # unless a real service is wanted.
        from app.agent.agent import build_agent

        if not settings.google_api_key:
            logging.warning("GOOGLE_API_KEY is empty; chat requests will fail.")
        app.state.chat_service = AdkChatService(app_name=settings.app_name, agent=build_agent())
        yield

    app = FastAPI(title="chatbot-backend", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(routes_health.router)
    app.include_router(routes_chat.router)
    return app


app = create_app()
