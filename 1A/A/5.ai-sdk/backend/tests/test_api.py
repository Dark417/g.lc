"""The entrance contract, with a framework-free adapter."""

import asyncio
import json

import httpx

from app.main import create_app
from tests.conftest import EchoAdapter


def run(client, **kw):
    body = {"framework": "echo", "pattern": "single", "provider": "raw", "message": "hi", **kw}
    return client.post("/v1/runs", json=body)


def test_run_returns_events_and_output(client):
    r = run(client)
    assert r.status_code == 200, r.text
    body = r.json()
    types = [e["type"] for e in body["events"]]
    assert types == ["session", "agent", "tool_call", "tool_result", "message", "done"]
    assert body["output"] == "echo[raw]: hi"
    assert body["events"][3]["result"]["result"] == 5  # the neutral calculator ran in scope


def test_session_reuse_counts_turns(client):
    sid = run(client).json()["session_id"]
    assert run(client, session_id=sid).json()["session_id"] == sid
    info = client.get(f"/v1/sessions/{sid}").json()
    assert info["turns"] == 2 and info["target"] == "echo:single:raw"


def test_session_bound_to_target(client):
    sid = run(client).json()["session_id"]
    r = run(client, session_id=sid, provider="bedrock")
    assert r.status_code == 409 and "bound to" in r.json()["detail"]


def test_session_belongs_to_user(client):
    sid = run(client).json()["session_id"]
    assert run(client, session_id=sid, user_id="mallory").status_code == 409


async def test_concurrent_requests_on_one_session_get_409(container):
    container.registry.register(EchoAdapter(delay=0.3))
    app = create_app(container)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://t") as c:
        first = await c.post(
            "/v1/runs", json={"framework": "echo", "pattern": "single", "message": "a"}
        )
        sid = first.json()["session_id"]
        body = {"framework": "echo", "pattern": "single", "message": "b", "session_id": sid}
        r1, r2 = await asyncio.gather(c.post("/v1/runs", json=body), c.post("/v1/runs", json=body))
    codes = sorted([r1.status_code, r2.status_code])
    # one wins; the loser is rejected up front (409) or, if it lost the race inside the stream,
    # gets an error event. Never two loops interleaved on one session.
    loser = r2 if r1.status_code == 200 and "done" in r1.text else r1
    assert codes[0] == 200
    assert loser.status_code == 409 or '"error"' in loser.text


def test_unknown_framework_and_pattern(client):
    assert run(client, framework="nope").status_code == 404
    assert run(client, pattern="nope").status_code == 404


def test_unconfigured_provider_is_400(client, container):
    container.settings.google_cloud_project = ""
    r = run(client, provider="vertex")
    assert r.status_code == 400 and "GOOGLE_CLOUD_PROJECT" in r.json()["detail"]


def test_input_guardrail_blocks_secret(client):
    r = run(client, message="my key is AKIAABCDEFGHIJKLMNOP")
    events = r.json()["events"]
    assert events[-1]["type"] == "error" and "secret:aws_access_key" in events[-1]["message"]


def test_output_guardrail_masks_pii(client):
    body = run(client, message="mail bob@example.com").json()
    assert body["output"] == "echo[raw]: mail [EMAIL]"


def test_stream_is_sse(client):
    body = {"framework": "echo", "pattern": "single", "message": "hi"}
    with client.stream("POST", "/v1/runs/stream", json=body) as r:
        lines = [ln for ln in r.iter_lines() if ln.startswith("data: ")]
    events = [json.loads(ln[6:]) for ln in lines]
    assert events[0]["type"] == "session" and events[-1]["type"] == "done"


def test_catalog(client):
    cat = client.get("/v1/catalog").json()
    assert [f["name"] for f in cat["frameworks"]] == ["echo"]
    providers = {p["name"]: p for p in cat["providers"]}
    assert providers["raw"]["services"]["rag"] == "local"
    assert providers["bedrock"]["services"]["memory"] == "local"  # no AGENTCORE_MEMORY_ID: fallback
    assert {t["name"] for t in cat["tools"]} >= {"calculator", "browse", "run_cli", "search_docs"}
    assert cat["mcp_servers"] == ["workbench"]


def test_catalog_reports_broken_adapter(container):
    from app.core.registry import AdapterRegistry

    container.registry = AdapterRegistry(container.settings, {"ghost": "app.nope:build"})
    from fastapi.testclient import TestClient

    with TestClient(create_app(container)) as c:
        fw = c.get("/v1/catalog").json()["frameworks"][0]
    assert fw["available"] is False and "ModuleNotFoundError" in fw["error"]


def test_playground_and_health(client):
    assert client.get("/healthz").json() == {"status": "ok"}
    assert "Agent playground" in client.get("/").text
