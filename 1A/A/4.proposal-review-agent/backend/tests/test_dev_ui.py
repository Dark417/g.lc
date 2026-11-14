"""ADK's dev UI mounted in the same process, sharing our container's services."""

from fastapi.testclient import TestClient

from app.container import build_container
from app.main import create_app
from tests.conftest import ALICE, ScriptedModel, say


def test_adk_dev_ui_shares_sessions_with_the_api(settings, fake_llm):
    settings.enable_adk_web = True
    model = ScriptedModel(script=[say("hello from the portal")])
    app = create_app(container=build_container(settings, llm=fake_llm), agent_model=model)
    with TestClient(app) as tc:
        assert tc.get("/list-apps").json() == ["compliance_agent"]
        assert tc.get("/dev-ui/").status_code == 200
        assert tc.get("/api/v1/me", headers=ALICE).json()["adk_web"] is True

        # a conversation started through our API is visible through ADK's own endpoints
        sid = tc.post("/api/v1/chat", json={"message": "hi"}, headers=ALICE).json()["session_id"]
        adk_sessions = tc.get("/apps/compliance_agent/users/alice@example.com/sessions").json()
        assert sid in {s["id"] for s in adk_sessions}
