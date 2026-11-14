"""Bedrock-branch state suite (langgraph:memory): checkpointer-backed conversation, store-backed
long-term memory, compaction, node cache, crash recovery, time travel, fork, durability, and the
AWS checkpointers (ElastiCache Valkey on a real redis-server, DynamoDB on moto)."""

import os
import uuid
from contextlib import ExitStack

import pytest
from fastapi.testclient import TestClient

from app.adapters.langgraph.adapter import LangGraphAdapter
from app.main import create_app
from tests.fakes.langchain import Scripts, call, say


@pytest.fixture
def lg(container):
    stack = ExitStack()

    def make(scripts: Scripts) -> TestClient:
        container.registry.register(LangGraphAdapter(container.settings, model_factory=scripts))
        return stack.enter_context(TestClient(create_app(container)))

    yield make
    stack.close()


@pytest.fixture
def user() -> str:
    return f"u-{uuid.uuid4().hex[:6]}"  # the in-memory store is process-wide; isolate per test


def run(client, message="", ok=True, provider="raw", **kw):
    body = {
        "framework": "langgraph",
        "pattern": "memory",
        "provider": provider,
        "message": message,
        **kw,
    }
    r = client.post("/v1/runs", json=body)
    assert r.status_code == 200, r.text
    data = r.json()
    if ok:
        assert not [e for e in data["events"] if e["type"] == "error"], data["events"]
    return data


def of(data, type_):
    return [e for e in data["events"] if e["type"] == type_]


def test_conversation_and_long_term_memory(lg, user):
    scripts = Scripts(agent=[say("Hi Ada."), say("us-east-1."), say("You deploy to us-east-1.")])
    client = lg(scripts)
    first = run(client, "I'm Ada and my primary AWS region is us-east-1.", user_id=user)
    run(client, "What is my region?", user_id=user, session_id=first["session_id"])
    assert "my primary AWS region is us-east-1" in scripts["agent"].all_text(1)  # same thread

    run(client, "Which AWS region do I deploy to?", user_id=user)  # new thread
    system = scripts["agent"].system_text(2)
    assert "Known about this user" in system and "us-east-1" in system  # recall node + store


def test_node_cache_skips_recall_for_same_user_and_question(lg, user):
    client = lg(Scripts(agent=[say("a"), say("b"), say("c")]))
    q = "What did I say about Valkey?"
    first = run(client, q, user_id=user)
    second = run(client, q, user_id=user)  # new thread, same user + question -> cached recall
    other = run(client, q, user_id=user + "-other")
    assert not [e for e in of(first, "state") if e["data"].get("cached")]
    assert [e for e in of(second, "state") if e["data"].get("cached") and e["agent"] == "recall"]
    assert not [e for e in of(other, "state") if e["data"].get("cached")]  # key includes user


def test_compaction_shrinks_state_but_time_travel_keeps_old_messages(lg, user):
    scripts = Scripts(
        agent=[say("one"), say("two"), say("three")], summarizer=[say("Ada asked twice.")]
    )
    client = lg(scripts)
    opts = {"summarize_after": 4, "keep_recent": 2}
    sid = run(client, "first", user_id=user, options=opts)["session_id"]
    run(client, "second", user_id=user, session_id=sid, options=opts)
    run(client, "third", user_id=user, session_id=sid, options=opts)  # 5 messages > 4 -> compact
    history = client.get(f"/v1/sessions/{sid}/history").json()
    assert history[0] == {"role": "summary", "text": "Ada asked twice."}
    assert [h["text"] for h in history[1:]] == ["third", "three"]
    assert "Ada asked twice." in scripts["agent"].system_text(2)
    checkpoints = client.get(f"/v1/sessions/{sid}/checkpoints").json()
    assert max(c["messages"] for c in checkpoints) >= 5  # earlier checkpoints still hold them


def test_crash_then_recover_resumes_at_the_failed_node(lg, user):
    scripts = Scripts(agent=[call("calculator", expression="0.17*2340"), say("397.8")])
    client = lg(scripts)
    crashed = run(
        client, "17% of 2340?", ok=False, user_id=user, options={"crash_on_model_call": 2}
    )
    assert "simulated model outage" in crashed["events"][-1]["message"]
    assert [e["name"] for e in of(crashed, "tool_result")] == ["calculator"]

    recovered = run(
        client, user_id=user, session_id=crashed["session_id"], resume={"recover": True}
    )
    assert {"recovering": ["agent"]} in [e["data"] for e in of(recovered, "state")]
    assert not of(recovered, "tool_result")  # the calculator is not run again
    assert recovered["output"] == "397.8"
    assert len(scripts["agent"].requests) == 2  # one call before the crash, one after


def test_fork_and_time_travel(lg, user):
    client = lg(Scripts(agent=[say("Hi Ada."), say("Rust."), say("Go, in the fork.")]))
    sid = run(client, "I'm Ada.", user_id=user)["session_id"]
    run(client, "Rust or Go?", user_id=user, session_id=sid)
    checkpoints = client.get(f"/v1/sessions/{sid}/checkpoints").json()
    end_of_turn_1 = next(c for c in checkpoints if c["messages"] == 2 and c["next"] == [])
    fork = client.post(
        f"/v1/sessions/{sid}/fork", json={"checkpoint_id": end_of_turn_1["checkpoint_id"]}
    )
    fid = fork.json()["session_id"]
    run(client, "Rust or Go, again?", user_id=user, session_id=fid)
    assert [h["text"] for h in client.get(f"/v1/sessions/{sid}/history").json()] == [
        "I'm Ada.",
        "Hi Ada.",
        "Rust or Go?",
        "Rust.",
    ]
    assert [h["text"] for h in client.get(f"/v1/sessions/{fid}/history").json()] == [
        "I'm Ada.",
        "Hi Ada.",
        "Rust or Go, again?",
        "Go, in the fork.",
    ]


def test_durability_exit_writes_fewer_checkpoints(lg, user):
    client = lg(Scripts(agent=[say("a"), say("b")]))
    s1 = run(client, "hi", user_id=user, options={"durability": "sync"})["session_id"]
    s2 = run(client, "hi", user_id=user, options={"durability": "exit"})["session_id"]
    n_sync = len(client.get(f"/v1/sessions/{s1}/checkpoints").json())
    n_exit = len(client.get(f"/v1/sessions/{s2}/checkpoints").json())
    assert n_exit < n_sync


def test_bedrock_on_elasticache_valkey(lg, user, settings, redis_url):
    settings.langgraph_checkpointer = "valkey"
    settings.redis_url = redis_url
    client = lg(Scripts(agent=[say("Hi."), say("You said hi.")]))
    sid = run(client, "hi", provider="bedrock", user_id=user)["session_id"]
    run(client, "what did I say?", provider="bedrock", user_id=user, session_id=sid)
    assert [h["text"] for h in client.get(f"/v1/sessions/{sid}/history").json()] == [
        "hi",
        "Hi.",
        "what did I say?",
        "You said hi.",
    ]
    import valkey

    keys = valkey.Valkey.from_url(redis_url.replace("redis://", "valkey://")).keys("*")
    assert any(b"checkpoint" in k for k in keys)  # the checkpoints live in the cache server


def test_bedrock_on_dynamodb(lg, user, settings, monkeypatch):
    import boto3
    from moto import mock_aws

    for k, v in {
        "AWS_ACCESS_KEY_ID": "x",
        "AWS_SECRET_ACCESS_KEY": "x",
        "AWS_DEFAULT_REGION": "us-east-1",
    }.items():
        monkeypatch.setenv(k, v)
    settings.langgraph_checkpointer = "dynamodb"
    with mock_aws():
        boto3.client("dynamodb", region_name="us-east-1").create_table(
            TableName=settings.dynamodb_checkpoint_table,
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        client = lg(Scripts(agent=[say("Stored in DynamoDB.")]))
        sid = run(client, "hi", provider="bedrock", user_id=user)["session_id"]
        assert len(client.get(f"/v1/sessions/{sid}/checkpoints").json()) >= 5
        assert client.delete(f"/v1/sessions/{sid}").status_code == 204
    assert os.environ["AWS_DEFAULT_REGION"] == "us-east-1"
