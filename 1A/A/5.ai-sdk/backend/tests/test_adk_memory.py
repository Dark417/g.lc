"""Vertex-branch state suite (adk:memory) on local services: state scopes, Memory Bank-style
recall, events compaction, resumable invocations, rewind, fork. The same code uses
VertexAiSessionService / VertexAiMemoryBankService when AGENT_ENGINE_ID is set."""

import uuid
from contextlib import ExitStack

import pytest
from fastapi.testclient import TestClient

from app.adapters.adk.adapter import AdkAdapter
from app.main import create_app
from tests.fakes.adk import Scripts, call, say


@pytest.fixture
def adk(container):
    stack = ExitStack()

    def make(scripts: Scripts) -> TestClient:
        container.registry.register(AdkAdapter(container.settings, model_factory=scripts))
        return stack.enter_context(TestClient(create_app(container)))

    yield make
    stack.close()


@pytest.fixture
def user() -> str:
    return f"u-{uuid.uuid4().hex[:6]}"


def run(client, message="", ok=True, **kw):
    body = {"framework": "adk", "pattern": "memory", "provider": "raw", "message": message, **kw}
    r = client.post("/v1/runs", json=body)
    assert r.status_code == 200, r.text
    data = r.json()
    if ok:
        assert not [e for e in data["events"] if e["type"] == "error"], data["events"]
    return data


def of(data, type_):
    return [e for e in data["events"] if e["type"] == type_]


def state_of(client, sid):
    return client.get(f"/v1/sessions/{sid}/history").json()[-1]["state"]


def test_state_scopes(adk, user):
    scripts = Scripts(
        assistant=[
            call("save_preference", key="region", value="us-east-1"),
            call("add_note", text="compare ADK and Strands"),
            say("Saved."),
            say("You prefer us-east-1."),
        ]
    )
    client = adk(scripts)
    s1 = run(client, "Remember I prefer us-east-1; note: compare ADK and Strands.", user_id=user)[
        "session_id"
    ]
    state = state_of(client, s1)
    assert state["user:preferences"] == {"region": "us-east-1"}  # user scope
    assert state["notes"] == ["compare ADK and Strands"]  # session scope
    assert state["turns"] == 1 and state["last_answer"] == "Saved."  # callback + output_key
    assert "temp:last_tool" not in state  # temp scope is never persisted
    assert state["app:preferences_saved"] >= 1  # app scope

    s2 = run(client, "Which region do I prefer?", user_id=user)["session_id"]  # new session
    system = scripts["assistant"].system(3)
    assert "'region': 'us-east-1'" in system  # {user:preferences?} followed the user
    assert "compare ADK and Strands" not in system  # {notes?} did not: session scope
    assert "notes" not in state_of(client, s2)


def test_long_term_memory_across_sessions(adk, user):
    scripts = Scripts(assistant=[say("Noted, you deploy with Terraform."), say("With Terraform.")])
    client = adk(scripts)
    run(client, "I deploy everything with Terraform.", user_id=user)
    run(client, "How do I deploy everything?", user_id=user)
    assert "<PAST_CONVERSATIONS>" in scripts["assistant"].contents_text(1)  # PreloadMemoryTool
    mems = client.get(f"/v1/users/{user}/memories?framework=adk&query=deploy").json()
    assert any("Terraform" in m["text"] for m in mems)


def test_events_compaction(adk, user):
    scripts = Scripts(
        assistant=[say("one"), say("two"), say("three")],
        summarizer=[say("User asked three things.")] * 3,
    )
    client = adk(scripts)
    opts = {"compaction_interval": 2, "overlap_size": 0}
    sid = run(client, "first", user_id=user, options=opts)["session_id"]
    run(client, "second", user_id=user, session_id=sid, options=opts)
    run(client, "third", user_id=user, session_id=sid, options=opts)
    history = client.get(f"/v1/sessions/{sid}/history").json()
    assert {"compaction"} <= {h["role"] for h in history}
    assert "User asked three things." in scripts["assistant"].contents_text(
        2
    )  # summary replaced old events


def test_crash_then_resume_invocation(adk, user):
    scripts = Scripts(assistant=[call("calculator", expression="2+3"), say("It is 5.")])
    client = adk(scripts)
    crashed = run(client, "2+3?", ok=False, user_id=user, options={"crash_on_model_call": 2})
    assert "simulated model outage" in crashed["events"][-1]["message"]
    assert [e["name"] for e in of(crashed, "tool_result")] == ["calculator"]
    resumed = run(client, user_id=user, session_id=crashed["session_id"], resume={"recover": True})
    assert [e for e in of(resumed, "state") if "resuming_invocation" in e["data"]]
    assert not of(resumed, "tool_result")  # the calculator is not run again
    assert resumed["output"] == "It is 5."


def test_rewind_and_fork(adk, user):
    scripts = Scripts(
        assistant=[say("Hi Ada."), say("Use Rust."), say("Rewound: what else?"), say("Forked: Go.")]
    )
    client = adk(scripts)
    sid = run(client, "I'm Ada.", user_id=user)["session_id"]
    run(client, "Rust or Go?", user_id=user, session_id=sid)
    invocations = client.get(f"/v1/sessions/{sid}/checkpoints").json()
    assert [i["user"] for i in invocations] == ["Rust or Go?", "I'm Ada."]

    fork = client.post(
        f"/v1/sessions/{sid}/fork", json={"checkpoint_id": invocations[1]["checkpoint_id"]}
    ).json()
    r = client.post(
        f"/v1/sessions/{sid}/rewind", json={"checkpoint_id": invocations[0]["checkpoint_id"]}
    )
    assert r.status_code == 200
    run(client, "Anything else?", user_id=user, session_id=sid)
    context = scripts["assistant"].contents_text(2)
    assert "I'm Ada." in context and "Rust or Go?" not in context  # turn 2 rewound away
    assert "rewind" in {h["role"] for h in client.get(f"/v1/sessions/{sid}/history").json()}

    run(client, "Which language?", user_id=user, session_id=fork["session_id"])
    fork_context = scripts["assistant"].contents_text(3)
    assert "I'm Ada." in fork_context and "Rust or Go?" not in fork_context


def test_recover_requires_resumable_pattern(adk, user):
    client = adk(Scripts(assistant=[say("hi")]))
    body = {
        "framework": "adk",
        "pattern": "single",
        "message": "hi",
        "user_id": user,
        "options": {"mcp": False},
    }
    sid = client.post("/v1/runs", json=body).json()["session_id"]
    body = {**body, "message": "", "session_id": sid, "resume": {"recover": True}}
    assert "not resumable" in client.post("/v1/runs", json=body).json()["events"][-1]["message"]
