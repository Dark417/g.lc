"""HTTP surface: authn, authz, rules, documents, assess, chat, conversations. Real app + lifespan."""

import json

import pytest
from fastapi.testclient import TestClient

from app.container import build_container
from app.main import create_app
from tests.conftest import (
    ADMIN,
    ALICE,
    BOB,
    HARD_OK,
    SAMPLES,
    ScriptedModel,
    call,
    findings_from,
    say,
)

DOCS = SAMPLES / "documents"
RULES = SAMPLES / "rules"


@pytest.fixture
def api(settings, fake_llm):
    model = ScriptedModel()
    app = create_app(container=build_container(settings, llm=fake_llm), agent_model=model)
    with TestClient(app) as tc:
        tc.model, tc.llm = model, fake_llm
        yield tc


def seed(api):
    with open(RULES / "seed-rules.json", "rb") as f:
        r = api.post("/api/v1/rules/import", headers=ADMIN, files={"file": ("seed-rules.json", f)})
    assert r.status_code == 201, r.text


def test_health_and_identity(api):
    assert api.get("/healthz").json() == {"status": "ok"}
    assert api.get("/readyz").json() == {"status": "ready"}
    assert api.get("/api/v1/me").json()["user_id"] == "user@example.com"  # dev default
    me = api.get("/api/v1/me", headers=ADMIN).json()
    assert me["role"] == "admin" and me["adk_web"] is False and me["auth_mode"] == "dev"
    svc = api.get("/api/v1/me", headers={"X-Service-Token": "svc-token"}).json()
    assert svc["user_id"] == "svc:mcp" and svc["role"] == "user" and svc["kind"] == "service"
    assert api.get("/api/v1/me", headers={"X-Service-Token": "wrong"}).status_code == 401


def test_rules_crud_and_authz(api):
    body = {
        "title": "Badges on site",
        "statement": "Staff must wear badges.",
        "severity": "hard",
        "category": "security",
    }
    assert api.post("/api/v1/rules", json=body, headers=ALICE).status_code == 403
    r = api.post("/api/v1/rules", json=body | {"code": "SEC-100"}, headers=ADMIN)
    assert r.status_code == 201 and r.json()["code"] == "SEC-100"
    assert (
        api.post("/api/v1/rules", json=body | {"code": "SEC-100"}, headers=ADMIN).status_code == 409
    )

    assert api.get("/api/v1/rules/sec-100", headers=ALICE).json()["title"] == "Badges on site"
    assert (
        api.patch("/api/v1/rules/SEC-100", json={"severity": "flexible"}, headers=ALICE).status_code
        == 403
    )
    patched = api.patch(
        "/api/v1/rules/SEC-100",
        json={"severity": "flexible", "change_note": "relaxed"},
        headers=ADMIN,
    ).json()
    assert patched["version"] == 2 and patched["severity"] == "flexible"
    assert [
        v["change_note"] for v in api.get("/api/v1/rules/SEC-100/versions", headers=ALICE).json()
    ] == ["created", "relaxed"]

    assert api.delete("/api/v1/rules/SEC-100", headers=ADMIN).json()["status"] == "retired"
    assert api.get("/api/v1/rules", headers=ALICE).json() == []
    assert len(api.get("/api/v1/rules?status=", headers=ALICE).json()) == 1
    assert api.get("/api/v1/rules/NOPE-1", headers=ALICE).status_code == 404


def test_rule_import_and_bulk_approve(api):
    seed(api)
    with open(RULES / "regional-rules.csv", "rb") as f:
        r = api.post(
            "/api/v1/rules/import", headers=ADMIN, files={"file": ("regional-rules.csv", f)}
        )
    assert [x["code"] for x in r.json()] == ["REG-001", "REG-002", "REG-003"]
    assert len(api.get("/api/v1/rules", headers=ALICE).json()) == 17
    assert (
        len(api.get("/api/v1/rules?severity=flexible&category=marketing", headers=ALICE).json())
        == 2
    )

    proposed = [
        {
            "code": "PRIV-001",
            "title": "Duplicate code gets renumbered",
            "statement": "Must be unique.",
            "severity": "hard",
            "category": "privacy",
        }
    ]
    [created] = api.post("/api/v1/rules/bulk", json=proposed, headers=ADMIN).json()
    assert created["code"] == "PRIV-005"  # PRIV-001..004 exist


def test_documents_lifecycle(api):
    with open(DOCS / "ai-usage-policy.docx", "rb") as f:
        assert (
            api.post("/api/v1/documents", headers=ALICE, files={"file": ("a.docx", f)}).status_code
            == 403
        )
    with open(DOCS / "ai-usage-policy.docx", "rb") as f:
        r = api.post(
            "/api/v1/documents",
            headers=ADMIN,
            files={"file": ("ai-usage-policy.docx", f)},
            data={"category": "ai", "tags": "ml, genai"},
        )
    assert r.status_code == 201, r.text
    doc = r.json()
    assert (
        doc["status"] == "ready"
        and doc["title"] == "AI Usage Policy"
        and doc["tags"] == ["ml", "genai"]
    )
    assert (
        api.post("/api/v1/documents", headers=ADMIN, files={"file": ("x.xlsx", b"x")}).status_code
        == 415
    )

    [listed] = api.get("/api/v1/documents", headers=ALICE).json()
    assert listed["id"] == doc["id"] and listed["summary"] == "Test summary."
    assert "Training data" in api.get(f"/api/v1/documents/{doc['id']}/text", headers=ALICE).text
    dl = api.get(f"/api/v1/documents/{doc['id']}/download", headers=ALICE)
    assert dl.content == (DOCS / "ai-usage-policy.docx").read_bytes()

    assert (
        api.post(f"/api/v1/documents/{doc['id']}/propose-rules", headers=ALICE).status_code == 403
    )
    [proposal] = api.post(f"/api/v1/documents/{doc['id']}/propose-rules", headers=ADMIN).json()
    approved = api.post(
        "/api/v1/rules/bulk", json=[proposal | {"source_document_id": doc["id"]}], headers=ADMIN
    ).json()
    assert api.get(f"/api/v1/documents/{doc['id']}", headers=ALICE).json()[
        "extracted_rule_codes"
    ] == [approved[0]["code"]]

    assert api.delete(f"/api/v1/documents/{doc['id']}", headers=ADMIN).status_code == 204
    assert api.get(f"/api/v1/documents/{doc['id']}", headers=ALICE).status_code == 404


def test_assess_endpoint_and_history(api):
    seed(api)
    api.llm.findings = findings_from({"MKT-002": "violated", "PRIV-001": "satisfied"})
    v = api.post(
        "/api/v1/assess",
        json={"proposal": "Ad claiming we are twice as fast as Acme"},
        headers=ALICE,
    ).json()
    assert v["verdict"] == "NEEDS_MORE_INFO"  # hard rules not assessed are 'unclear'
    api.llm.findings = findings_from(HARD_OK | {"MKT-002": "violated"})
    v = api.post(
        "/api/v1/assess",
        json={"proposal": "Ad claiming we are twice as fast as Acme"},
        headers=ALICE,
    ).json()
    assert v["verdict"] == "CONDITIONALLY_COMPLIANT" and v["conditions"][0].startswith("MKT-002")
    assert len(api.get("/api/v1/assessments", headers=ALICE).json()) == 2
    assert api.get("/api/v1/assessments", headers=BOB).json() == []
    assert api.get("/api/v1/assessments?all=true", headers=BOB).json() == []  # not admin
    assert len(api.get("/api/v1/assessments?all=true", headers=ADMIN).json()) == 2


def test_chat_stream_and_conversations(api):
    seed(api)
    api.llm.findings = findings_from({"PRIV-003": "violated"})
    api.model.script = [call("assess_proposal", proposal="kids emails"), say("**NON-COMPLIANT**")]
    with api.stream(
        "POST", "/api/v1/chat/stream", json={"message": "Kids emails ok?"}, headers=ALICE
    ) as r:
        events = [json.loads(line[6:]) for line in r.iter_lines() if line.startswith("data: ")]
    types_ = [e["type"] for e in events]
    assert types_[0] == "session" and "verdict" in types_ and types_[-1] == "done"
    sid = events[0]["session_id"]

    api.model.script = [say("Glad to help.")]
    r = api.post(
        "/api/v1/chat", json={"message": "thanks", "session_id": sid}, headers=ALICE
    ).json()
    assert r["reply"] == "Glad to help." and r["session_id"] == sid

    [conv] = api.get("/api/v1/conversations", headers=ALICE).json()
    assert conv["id"] == sid and conv["title"] == "Kids emails ok?"
    msgs = api.get(f"/api/v1/conversations/{sid}", headers=ALICE).json()["messages"]
    assert [m["role"] for m in msgs] == ["user", "assistant", "user", "assistant"]
    assert msgs[1]["verdicts"][0]["verdict"] == "NON_COMPLIANT"

    assert api.get(f"/api/v1/conversations/{sid}", headers=BOB).status_code == 404
    assert (
        api.post("/api/v1/chat", json={"message": "x", "session_id": sid}, headers=BOB).status_code
        == 404
    )
    assert api.delete(f"/api/v1/conversations/{sid}", headers=ALICE).status_code == 204
    assert api.get("/api/v1/conversations", headers=ALICE).json() == []


def test_iap_mode_uses_verified_token_not_headers(settings, fake_llm, monkeypatch):
    import app.auth.identity as ident

    settings.auth_mode, settings.iap_audience = "iap", "/projects/1/locations/r/services/frontend"
    seen = {}

    def fake_verify(assertion, audience):
        seen["aud"] = audience
        if assertion != "good.jwt":
            raise ident.AuthError("bad")
        return "Admin@Example.com"

    monkeypatch.setattr(ident, "verify_iap_jwt", fake_verify)
    with TestClient(create_app(container=build_container(settings, llm=fake_llm))) as tc:
        assert (
            tc.get("/api/v1/me", headers={"X-User-Email": "admin@example.com"}).status_code == 401
        )
        me = tc.get("/api/v1/me", headers={"X-Goog-IAP-JWT-Assertion": "good.jwt"}).json()
        assert me["user_id"] == "admin@example.com" and me["role"] == "admin"
        assert seen["aud"] == settings.iap_audience


def test_semantic_search_endpoints(api):
    seed(api)
    with open(DOCS / "data-privacy-standard.html", "rb") as f:
        api.post(
            "/api/v1/documents", headers=ADMIN, files={"file": ("data-privacy-standard.html", f)}
        )
    rules = api.get(
        "/api/v1/search/rules", params={"q": "parental consent for children"}, headers=ALICE
    ).json()
    assert rules[0]["code"] == "PRIV-003" and "score" in rules[0]
    passages = api.get(
        "/api/v1/search/documents", params={"q": "verifiable parental consent"}, headers=ALICE
    ).json()
    assert passages[0]["source"] == "Data Privacy Standard §3. Children"
    assert api.get("/api/v1/search/rules", params={"q": "x"}, headers=ALICE).status_code == 422


def test_assess_reports_model_failure_as_502(api):
    seed(api)

    def boom(prompt):
        raise RuntimeError("No API key was provided")

    api.llm.findings = boom
    r = api.post("/api/v1/assess", json={"proposal": "anything at all"}, headers=ALICE)
    assert r.status_code == 502 and "No API key" in r.json()["detail"]
