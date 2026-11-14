"""The raw-branch state suite: a hand-written loop with checkpoints, recovery, fork, context
strategies, long-term memory, and Redis caches. The real Anthropic SDK talks to a scripted
transport; tools, stores, and Redis are real."""

from contextlib import ExitStack

import pytest
from fastapi.testclient import TestClient

from app.adapters.diy.adapter import DiyAdapter
from app.adapters.diy.context import build_context, safe_cut
from app.adapters.diy.state import LoopState
from app.main import create_app
from tests.fakes.claude import api_message, api_text, api_tool_use, routed_messages_client


@pytest.fixture
def diy(container):
    stack = ExitStack()

    def make(main, summarize=(), extract=()):
        factory, captured = routed_messages_client(main, summarize, extract)
        adapter = DiyAdapter(container.settings, client_factory=factory)
        container.registry.register(adapter)
        # `with`: one event loop for the client's lifetime, as in a real server (Redis pools bind to it)
        return stack.enter_context(TestClient(create_app(container))), captured, adapter

    yield make
    stack.close()


def run(client, message="", ok=True, **kw):
    r = client.post(
        "/v1/runs", json={"framework": "diy", "pattern": "loop", "message": message, **kw}
    )
    assert r.status_code == 200, r.text
    data = r.json()
    if ok:
        assert not [e for e in data["events"] if e["type"] == "error"], data["events"]
    return data


def of(data, type_):
    return [e for e in data["events"] if e["type"] == type_]


def state_data(data, key):
    return [e["data"][key] for e in of(data, "state") if key in e["data"]]


def test_conversation_memory_long_term_memory_and_consolidation(diy):
    client, captured, _ = diy(
        main=[api_message(api_text("Noted, Ada.")), api_message(api_text("us-east-1.")),
              api_message(api_text("You use us-east-1.")), api_message(api_text("Updated."))],
        extract=['{"facts": ["User\'s name is Ada", "User\'s primary AWS region is us-east-1"]}', '{"facts": []}',
                 '{"facts": []}', '{"facts": ["User\'s primary AWS region is eu-west-1"]}'],
    )  # fmt: skip
    first = run(client, "I'm Ada and I deploy everything to us-east-1.")
    assert [m["op"] for m in state_data(first, "memory")[0]] == ["insert", "insert"]

    # Same session: short-term (conversation) memory = the stored messages are sent again.
    run(client, "Which region do I use?", session_id=first["session_id"])
    sent = captured["main"][1]["messages"]
    assert sent[0]["content"] == "I'm Ada and I deploy everything to us-east-1." and len(sent) == 3

    # New session: long-term memory = extracted facts are recalled and injected.
    run(client, "What is my primary AWS region?")
    system = " ".join(b["text"] for b in captured["main"][2]["system"])
    assert "Known about this user" in system and "us-east-1" in system

    # Consolidation: a contradicting fact replaces the old one instead of piling up.
    moved = run(client, "We moved: my primary AWS region is now eu-west-1.")
    op = state_data(moved, "memory")[0][0]
    assert op["op"] == "update" and "us-east-1" in op["replaced"]
    facts = [m["text"] for m in client.get("/v1/users/demo-user/memories?framework=diy").json()]
    assert sorted(facts) == ["User's name is Ada", "User's primary AWS region is eu-west-1"]


def test_crash_then_recover_does_not_rerun_finished_tools(diy):
    client, captured, _ = diy(
        main=[
            api_message(api_tool_use("t1", "calculator", expression="0.17*2340"),
                        api_tool_use("t2", "current_time", timezone="UTC"), stop="tool_use"),
            api_message(api_text("397.8, and the time is noted.")),
        ]
    )  # fmt: skip
    # checkpoints: 1 user, 2 model, 3 tool:calculator -> crash
    crashed = run(
        client, "17% of 2340, and the UTC time?", ok=False, options={"crash_after_step": 3}
    )
    assert (
        crashed["events"][-1]["type"] == "error"
        and "simulated crash" in crashed["events"][-1]["message"]
    )
    assert [e["name"] for e in of(crashed, "tool_result")] == ["calculator"]
    sid = crashed["session_id"]

    blocked = run(client, "new question", session_id=sid, ok=False)
    assert "unfinished turn" in blocked["events"][-1]["message"]

    recovered = run(client, session_id=sid, resume={"recover": True})
    assert state_data(recovered, "recovered_from")
    assert [e["name"] for e in of(recovered, "tool_result")] == [
        "current_time"
    ]  # calculator not re-run
    assert recovered["output"] == "397.8, and the time is noted."
    final_request = captured["main"][-1]["messages"]
    results = [b["tool_use_id"] for b in final_request[-1]["content"]]
    assert results == ["t1", "t2"]  # both results reached the model, in order

    labels = [c["label"] for c in client.get(f"/v1/sessions/{sid}/checkpoints").json()]
    assert labels[::-1][:4] == ["user", "model", "tool:calculator", "tool:current_time"]


def test_fork_from_checkpoint_leaves_original_untouched(diy):
    client, _, _ = diy(
        main=[api_message(api_text("Hi Ada.")), api_message(api_text("Rust is fine.")),
              api_message(api_text("In this branch: Go."))],
    )  # fmt: skip
    first = run(client, "I'm Ada.")
    sid = first["session_id"]
    run(client, "Should I use Rust?", session_id=sid)
    ckpts = client.get(f"/v1/sessions/{sid}/checkpoints").json()
    after_turn_1 = next(c for c in ckpts if c["label"] == "done" and c["turn"] == 1)

    fork = client.post(
        f"/v1/sessions/{sid}/fork", json={"checkpoint_id": after_turn_1["checkpoint_id"]}
    ).json()
    assert [h["text"] for h in client.get(f"/v1/sessions/{fork['session_id']}/history").json()] == [
        "I'm Ada.",
        "Hi Ada.",
    ]
    run(client, "Should I use Go?", session_id=fork["session_id"])

    original = [h["text"] for h in client.get(f"/v1/sessions/{sid}/history").json()]
    forked = [h["text"] for h in client.get(f"/v1/sessions/{fork['session_id']}/history").json()]
    assert original == ["I'm Ada.", "Hi Ada.", "Should I use Rust?", "Rust is fine."]
    assert forked == ["I'm Ada.", "Hi Ada.", "Should I use Go?", "In this branch: Go."]


def test_redis_caches_llm_response_and_checkpoint(diy, settings, redis_url, container):
    import asyncio

    from app.state.cache import redis_client

    asyncio.run(redis_client(redis_url).flushdb())
    settings.redis_url = redis_url
    client, captured, adapter = diy(
        main=[api_message(api_text("397.8")), api_message(api_text("again"))]
    )
    a = run(client, "What is 17% of 2340?", options={"long_term": False})
    b = run(
        client, "What is 17% of 2340?", options={"long_term": False}
    )  # new session, same prompt
    assert state_data(a, "context")[0]["llm_cache"] == "miss"
    assert state_data(b, "context")[0]["llm_cache"] == "hit" and b["output"] == "397.8"
    assert len(captured["main"]) == 1  # the second answer never reached the model

    run(
        client,
        "And now?",
        session_id=a["session_id"],
        options={"long_term": False, "llm_cache": False},
    )
    assert adapter.store.name == "sqlite+redis" and adapter.store.hits >= 1  # latest() from Redis
    assert captured["main"][0]["system"][0]["cache_control"] == {
        "type": "ephemeral"
    }  # prompt caching


def _conversation(turns: int) -> LoopState:
    st = LoopState(session_id="s", user_id="u")
    for i in range(turns):
        st.messages += [
            {"role": "user", "content": f"question {i}"},
            {
                "role": "assistant",
                "content": [{"type": "tool_use", "id": f"t{i}", "name": "calculator", "input": {}}],
            },
            {
                "role": "user",
                "content": [{"type": "tool_result", "tool_use_id": f"t{i}", "content": "x" * 400}],
            },
            {"role": "assistant", "content": [{"type": "text", "text": f"answer {i}"}]},
        ]
    return st


async def _no_summary(prev, msgs):
    raise AssertionError("should not summarise")


async def test_context_strategies_keep_storage_complete():
    st = _conversation(5)  # 20 messages
    window = await build_context(st, {"context": "window", "window": 6}, _no_summary)
    assert window.messages[0] == {
        "role": "user",
        "content": "question 4",
    }  # never starts at a tool_result
    assert safe_cut(st.messages, 18) == 19  # index 18 is a tool_result -> moved forward

    budget = await build_context(st, {"context": "token_budget", "token_budget": 300}, _no_summary)
    assert budget.info["approx_tokens"] < 500 and budget.messages[0]["content"] == "question 4"

    calls = []

    async def summarize(prev, msgs):
        calls.append(len(msgs))
        return f"summary of {len(msgs)} messages"

    summary = await build_context(
        st, {"context": "summary", "keep_recent": 4, "summarize_after": 10}, summarize
    )
    assert calls == [16] and st.summarized_upto == 16 and st.summary == "summary of 16 messages"
    assert summary.system_extra == ["Summary of the earlier conversation:\nsummary of 16 messages"]
    assert len(summary.messages) == 4

    server = await build_context(st, {"context": "server"}, _no_summary)
    assert len(server.messages) == 20
    assert {e["type"] for e in server.request_extra["context_management"]["edits"]} == {
        "clear_tool_uses_20250919",
        "compact_20260112",
    }
    assert len(st.messages) == 20  # no strategy ever changes the stored conversation
