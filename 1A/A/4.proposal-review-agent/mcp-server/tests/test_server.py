"""The MCP tools against a fake backend (httpx MockTransport), through a real MCP client session."""

import json

import httpx
import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from app.client import BackendClient, BackendError
from app.config import Settings
from app.server import build_server

RULE = {
    "code": "PRIV-003",
    "title": "Parental consent",
    "statement": "Must obtain consent.",
    "severity": "hard",
    "category": "privacy",
    "rationale": "COPPA",
    "exception_process": "",
    "id": "x",
    "version": 2,
}
VERDICT = {
    "verdict": "NON_COMPLIANT",
    "blocking": ["PRIV-003: Parental consent"],
    "findings": [
        {"rule_code": "PRIV-003", "status": "violated"},
        {"rule_code": "FIN-001", "status": "not_applicable"},
    ],
}


def handler(seen: list):
    def handle(req: httpx.Request) -> httpx.Response:
        seen.append(req)
        path = req.url.path
        if path == "/api/v1/assess":
            return httpx.Response(200, json=VERDICT)
        if path == "/api/v1/search/rules":
            return httpx.Response(200, json=[RULE | {"score": 0.9}])
        if path == "/api/v1/rules/PRIV-003":
            return httpx.Response(200, json=RULE)
        if path.startswith("/api/v1/rules/"):
            return httpx.Response(404, json={"detail": "nope"})
        if path == "/api/v1/rules":
            return httpx.Response(200, json=[RULE])
        if path == "/api/v1/documents":
            return httpx.Response(
                200,
                json=[
                    {
                        "id": "doc_1",
                        "title": "Privacy",
                        "category": "privacy",
                        "format": "html",
                        "status": "ready",
                        "summary": "s",
                    }
                ],
            )
        if path == "/api/v1/documents/doc_1":
            return httpx.Response(
                200,
                json={
                    "id": "doc_1",
                    "title": "Privacy",
                    "category": "privacy",
                    "summary": "s",
                    "key_points": [],
                    "outline": [],
                    "extracted_rule_codes": [],
                },
            )
        if path == "/api/v1/search/documents":
            return httpx.Response(
                200,
                json=[{"document_id": "doc_1", "source": "Privacy §3", "score": 0.8, "text": "t"}],
            )
        return httpx.Response(500, text="boom")

    return handle


@pytest.fixture
def backend():
    seen: list[httpx.Request] = []
    client = BackendClient(
        Settings(backend_url="http://backend", service_token="tok"),
        httpx.MockTransport(handler(seen)),
    )
    client.seen = seen
    return client


async def _call(session, name, **args):
    res = await session.call_tool(name, args)
    assert not res.isError, res.content
    if res.structuredContent is not None:
        data = res.structuredContent
        return data.get("result", data)
    return json.loads(res.content[0].text)


async def test_tools_over_a_real_mcp_session(backend):
    server = build_server(backend)
    async with create_connected_server_and_client_session(server._mcp_server) as session:
        names = {t.name for t in (await session.list_tools()).tools}
        assert names == {
            "check_proposal",
            "search_rules",
            "get_rule",
            "list_rules",
            "list_documents",
            "get_document_summary",
            "search_documents",
        }

        v = await _call(session, "check_proposal", proposal="kids emails")
        assert v["verdict"] == "NON_COMPLIANT" and [f["rule_code"] for f in v["findings"]] == [
            "PRIV-003"
        ]

        [r] = await _call(session, "search_rules", query="children")
        assert r == {
            k: RULE[k]
            for k in (
                "code",
                "title",
                "statement",
                "severity",
                "category",
                "rationale",
                "exception_process",
            )
        }
        assert (await _call(session, "get_rule", code="NOPE-1"))["status"] == "not_found"
        assert (await _call(session, "list_rules", severity="hard"))[0]["code"] == "PRIV-003"
        assert (await _call(session, "list_documents"))[0]["id"] == "doc_1"
        assert (await _call(session, "get_document_summary", document_id="doc_1"))["summary"] == "s"
        assert (await _call(session, "search_documents", query="consent"))[0][
            "source"
        ] == "Privacy §3"

    assert all(req.headers["x-service-token"] == "tok" for req in backend.seen)
    list_req = next(r for r in backend.seen if r.url.path == "/api/v1/rules")
    assert list_req.url.params.get("severity") == "hard" and "category" not in list_req.url.params


async def test_backend_errors_surface():
    c = BackendClient(
        Settings(backend_url="http://b"),
        httpx.MockTransport(lambda r: httpx.Response(503, text="down")),
    )
    with pytest.raises(BackendError, match="503"):
        await c.list_rules()
