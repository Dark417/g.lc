import json


def test_chat_returns_reply_and_trace(client, fake_service):
    r = client.post("/api/v1/chat", json={"message": "hi"})
    assert r.status_code == 200
    body = r.json()
    assert body["reply"] == "echo: hi"
    assert body["events"][0]["type"] == "tool_call"
    assert fake_service.calls[0]["session_id"] is None


def test_chat_stream_is_sse(client):
    with client.stream("POST", "/api/v1/chat/stream", json={"message": "hi"}) as r:
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("text/event-stream")
        lines = [ln for ln in r.iter_lines() if ln.startswith("data: ")]
    events = [json.loads(ln[len("data: ") :]) for ln in lines]
    assert [e["type"] for e in events] == ["tool_call", "delta", "delta", "done"]
    assert events[-1]["reply"] == "echo"


def test_health(client):
    assert client.get("/healthz").json() == {"status": "ok"}
