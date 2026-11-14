"""Tests never call a real model. We swap the service at the dependency boundary."""

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_chat_service
from app.config import Settings
from app.main import create_app
from app.schemas import ChatResponse


class FakeChatService:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def chat(self, *, user_id: str, session_id: str | None, message: str) -> ChatResponse:
        self.calls.append({"user_id": user_id, "session_id": session_id, "message": message})
        return ChatResponse(session_id=session_id or "new-session", reply=f"echo: {message}")


@pytest.fixture
def fake_service() -> FakeChatService:
    return FakeChatService()


@pytest.fixture
def client(fake_service: FakeChatService) -> TestClient:
    app = create_app(Settings(google_api_key="test", cors_origins=["*"]))
    app.dependency_overrides[get_chat_service] = lambda: fake_service
    # Don't run lifespan (which would build the real ADK service).
    return TestClient(app)
