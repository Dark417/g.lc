"""strands:memory: agent.state, summarising conversation manager, session managers (File and S3)."""

from contextlib import ExitStack

import pytest
from fastapi.testclient import TestClient

from app.adapters.strands.adapter import StrandsAdapter
from app.main import create_app
from tests.fakes.strands import Scripts, call, say


@pytest.fixture
def sa(container):
    stack = ExitStack()

    def make(scripts: Scripts) -> TestClient:
        container.registry.register(StrandsAdapter(container.settings, model_factory=scripts))
        return stack.enter_context(TestClient(create_app(container)))

    yield make
    stack.close()


def run(client, message, provider="raw", **kw):
    body = {
        "framework": "strands",
        "pattern": "memory",
        "provider": provider,
        "message": message,
        **kw,
    }
    r = client.post("/v1/runs", json=body)
    assert r.status_code == 200, r.text
    data = r.json()
    assert not [e for e in data["events"] if e["type"] == "error"], data["events"]
    return data


def test_agent_state_is_persisted_but_not_in_context(sa):
    scripts = Scripts(
        memory_assistant=[
            call("set_preference", key="region", value="us-east-1"),
            say("Saved."),
            call("get_preferences"),
            say("You prefer us-east-1."),
        ]
    )
    client = sa(scripts)
    sid = run(client, "I prefer us-east-1.")["session_id"]
    second = run(client, "What do I prefer?", session_id=sid)  # a brand-new Agent object
    prefs = [e["result"] for e in second["events"] if e["type"] == "tool_result"][0]
    assert prefs == {"preferences": {"region": "us-east-1"}}  # restored from the session manager
    assert "us-east-1" not in str(
        scripts["memory_assistant"].requests[2]["system"]
    )  # never in context
    history = client.get(f"/v1/sessions/{sid}/history").json()
    assert history[-1]["state"]["preferences"] == {"region": "us-east-1"}
    assert [h["text"] for h in history if "text" in h][:2] == ["I prefer us-east-1.", "Saved."]


def test_summarizing_conversation_manager(sa):
    scripts = Scripts(
        memory_assistant=[say(f"answer {i}") for i in range(4)],
        summarizer=[say("Earlier: four questions.")],
    )
    client = sa(scripts)
    opts = {"max_messages": 4, "keep_recent": 2}
    sid = run(client, "q0", options=opts)["session_id"]
    for i in range(1, 4):
        run(client, f"q{i}", session_id=sid, options=opts)
    assert len(scripts["summarizer"].requests) >= 1
    sent = str(scripts["memory_assistant"].requests[-1]["messages"])
    assert "Earlier: four questions." in sent and "q0" not in sent  # summarised, not dropped


def test_bedrock_s3_session_manager(sa, settings, monkeypatch):
    import boto3
    from moto import mock_aws

    for k, v in {
        "AWS_ACCESS_KEY_ID": "x",
        "AWS_SECRET_ACCESS_KEY": "x",
        "AWS_DEFAULT_REGION": "us-east-1",
    }.items():
        monkeypatch.setenv(k, v)
    settings.strands_s3_session_bucket = "ai-sdk-sessions"
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="ai-sdk-sessions")
        client = sa(Scripts(memory_assistant=[say("Stored in S3."), say("Still here.")]))
        sid = run(client, "hello", provider="bedrock")["session_id"]
        run(client, "again", provider="bedrock", session_id=sid)
        keys = [o["Key"] for o in s3.list_objects_v2(Bucket="ai-sdk-sessions")["Contents"]]
        assert any(sid in k and "messages" in k for k in keys)
        texts = [h["text"] for h in client.get(f"/v1/sessions/{sid}/history").json() if "text" in h]
        assert texts == ["hello", "Stored in S3.", "again", "Still here."]
