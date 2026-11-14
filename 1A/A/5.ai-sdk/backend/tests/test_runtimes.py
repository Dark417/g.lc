"""AgentCore Runtime entrypoint: /invocations streams RunService events."""

import json

from starlette.testclient import TestClient

from tests.conftest import EchoAdapter


def test_agentcore_invocations_streams_events(container, monkeypatch):
    import app.runtimes.agentcore_app as runtime

    container.registry.register(EchoAdapter())
    monkeypatch.setattr(runtime, "_container", container)
    client = TestClient(runtime.app)
    assert client.get("/ping").status_code == 200
    r = client.post(
        "/invocations", json={"framework": "echo", "pattern": "single", "message": "hi"}
    )
    assert r.status_code == 200
    events = [json.loads(ln[6:]) for ln in r.text.splitlines() if ln.startswith("data: ")]
    assert events[0]["type"] == "session" and events[0]["data"]["provider"] == "bedrock"
    assert events[-1] == {"type": "done", "output": "echo[bedrock]: hi"}
