"""Tests never call a real model. The service is swapped at the dependency seam."""

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_chat_service
from app.config import Settings
from app.main import create_app
from app.schemas import ChatResponse, TraceEvent


class FakeChatService:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def chat(self, *, user_id: str, session_id: str | None, message: str) -> ChatResponse:
        self.calls.append({"user_id": user_id, "session_id": session_id, "message": message})
        return ChatResponse(
            session_id=session_id or "new-session",
            reply=f"echo: {message}",
            events=[
                TraceEvent(
                    type="tool_call", author="orchestrator", name="mcp__local__calculate", args={}
                )
            ],
        )

    async def stream(self, *, user_id: str, session_id: str | None, message: str):
        yield {
            "type": "tool_call",
            "author": "orchestrator",
            "name": "mcp__local__calculate",
            "args": {},
        }
        yield {"type": "delta", "text": "ec"}
        yield {"type": "delta", "text": "ho"}
        yield {"type": "done", "session_id": session_id or "new-session", "reply": "echo"}


@pytest.fixture
def settings(tmp_path) -> Settings:
    return Settings(
        anthropic_api_key="test",
        cors_origins=["*"],
        db_path=str(tmp_path / "app.db"),
        workdir=str(tmp_path / "agent"),
        knowledge_dir="data/knowledge",
        mcp_transport="off",
        _env_file=None,
    )


@pytest.fixture
def fake_service() -> FakeChatService:
    return FakeChatService()


@pytest.fixture
def client(settings, fake_service) -> TestClient:
    app = create_app(settings)
    app.dependency_overrides[get_chat_service] = lambda: fake_service
    return TestClient(app)  # no lifespan: the real agent options are never built here
