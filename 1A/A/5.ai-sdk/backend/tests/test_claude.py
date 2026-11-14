"""Claude adapter: Agent SDK wiring (CLI replaced by a fake) and the real Messages API tool runner."""

import uuid
from contextlib import ExitStack

import pytest
from fastapi.testclient import TestClient

from app.adapters.claude.adapter import ClaudeAdapter
from app.adapters.claude.agent_sdk import make_can_use_tool, make_hooks, provider_env
from app.adapters.claude.tools import as_sdk_tool
from app.main import create_app
from app.providers import build_profiles
from app.tools import calculator
from tests.fakes.claude import (
    CliScript,
    api_message,
    api_text,
    api_tool_use,
    messages_client,
    result,
    text,
    tool_result,
    tool_use,
)


@pytest.fixture
def cl(container):
    stack = ExitStack()

    def make(script: CliScript | None = None, messages=None) -> TestClient:
        script = script or CliScript()
        container.registry.register(
            ClaudeAdapter(
                container.settings,
                client_cls=lambda options: script.client_cls(options),
                query_fn=script.query_fn,
                messages_client=messages or (lambda p: None),
            )
        )
        return stack.enter_context(TestClient(create_app(container)))  # one event loop

    yield make
    stack.close()


def run(client, pattern, message="", provider="raw", ok=True, **kw):
    body = {
        "framework": "claude",
        "pattern": pattern,
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


def test_agent_sdk_options_events_and_session_resume(cl):
    script = CliScript(
        [
            tool_use("t1", "mcp__tools__calculator", expression="0.17*2340"),
            tool_result("t1", {"status": "ok", "result": 397.8}),
            text("17% of 2340 is 397.8."),
            result("17% of 2340 is 397.8.", session_id="cli-1"),
        ],
        [
            text("You asked about 17% of 2340."),
            result("You asked about 17% of 2340.", session_id="cli-1"),
        ],
    )
    client = cl(script)
    data = run(client, "agent_sdk", "What is 17% of 2340?")
    assert [e["name"] for e in of(data, "tool_call")] == ["calculator"]  # mcp__tools__ stripped
    assert of(data, "tool_result")[0]["result"]["result"] == 397.8
    assert data["output"] == "17% of 2340 is 397.8."
    assert data["events"][-1]["data"]["cost_usd"] == 0.001

    opts = script.options[0]
    assert set(opts.mcp_servers) == {"tools"} and opts.mcp_servers["tools"]["type"] == "sdk"
    assert "mcp__tools__calculator" in opts.allowed_tools
    assert "mcp__tools__run_cli" not in opts.allowed_tools  # sensitive -> can_use_tool decides
    assert opts.tools == [] and opts.can_use_tool is not None
    assert set(opts.hooks) == {"UserPromptSubmit", "PreToolUse", "PostToolUse", "PreCompact"}
    assert opts.env["ANTHROPIC_API_KEY"] == "test-key" and opts.session_id == str(
        uuid.UUID(data["session_id"])
    )

    run(client, "agent_sdk", "What did I ask?", session_id=data["session_id"])
    assert script.options[1].resume == "cli-1" and script.options[1].session_id is None


def test_subagents_options_and_attribution(cl):
    script = CliScript(
        [
            tool_use("task1", "Task", subagent_type="calculator", prompt="17% of 2340"),
            tool_use("c1", "mcp__tools__calculator", parent="task1", expression="0.17*2340"),
            tool_result("c1", {"result": 397.8}, parent="task1"),
            text("397.8", parent="task1"),
            tool_result("task1", "397.8"),
            text("It is 397.8."),
            result("It is 397.8."),
        ]
    )
    data = run(cl(script), "subagents", "What is 17% of 2340?")
    assert [e["agent"] for e in of(data, "agent")] == ["main", "calculator", "main"]
    assert [e["name"] for e in of(data, "tool_call")] == ["Task", "calculator"]
    opts = script.options[0]
    assert set(opts.agents) == {"researcher", "calculator"}
    assert opts.agents["calculator"].tools == ["mcp__tools__calculator"]
    assert opts.tools == ["Task"] and opts.permission_mode == "dontAsk"


def test_external_mcp_servers(cl, container):
    container.settings.playwright_mcp_enabled = True
    script = CliScript([text("Ticket created."), result("Ticket created.")])
    run(cl(script), "external_mcp", "File a ticket")
    opts = script.options[0]
    assert set(opts.mcp_servers) == {"workbench", "playwright"}
    assert opts.mcp_servers["workbench"]["type"] == "stdio"
    assert opts.mcp_servers["playwright"]["command"] == "npx"
    assert set(opts.allowed_tools) == {"mcp__workbench__*", "mcp__playwright__*"}


def test_cli_error_result_becomes_error_event(cl):
    script = CliScript([result("boom", is_error=True)])
    data = run(cl(script), "subagents", "x", ok=False)
    assert data["events"][-1]["type"] == "error"


@pytest.mark.parametrize(
    ("provider", "expected"),
    [
        ("raw", {"ANTHROPIC_API_KEY": "test-key"}),
        ("bedrock", {"CLAUDE_CODE_USE_BEDROCK": "1", "AWS_REGION": "us-east-1"}),
        (
            "vertex",
            {
                "CLAUDE_CODE_USE_VERTEX": "1",
                "CLOUD_ML_REGION": "global",
                "ANTHROPIC_VERTEX_PROJECT_ID": "test-project",
            },
        ),
    ],
)
def test_provider_is_env(settings, provider, expected):
    assert provider_env(build_profiles(settings)[provider]) == expected


async def test_hooks_and_permissions():
    hooks = make_hooks({"browse"})
    policy = hooks["PreToolUse"][0].hooks[0]
    denied = await policy({"tool_name": "mcp__tools__browse"}, "t1", None)
    assert denied["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert await policy({"tool_name": "mcp__tools__calculator"}, "t2", None) == {}
    ctx = await hooks["UserPromptSubmit"][0].hooks[0]({}, None, None)
    assert "Current UTC time" in ctx["hookSpecificOutput"]["additionalContext"]

    can_use = make_can_use_tool({"approve_sensitive": False})
    assert type(await can_use("mcp__tools__run_cli", {}, None)).__name__ == "PermissionResultDeny"
    assert (
        type(await make_can_use_tool({})("mcp__tools__run_cli", {}, None)).__name__
        == "PermissionResultAllow"
    )


async def test_sdk_tool_runs_neutral_function(scope):
    out = await as_sdk_tool(calculator).handler({"expression": "2+3"})
    assert out["content"][0]["text"] == '{"status": "ok", "expression": "2+3", "result": 5}'


def test_messages_api_tool_runner_mcp_and_history(cl):
    factory, captured = messages_client(
        api_message(api_tool_use("tu1", "calculator", expression="0.17*2340"), stop="tool_use"),
        api_message(
            api_tool_use("tu2", "create_ticket", title="Try tool runner", body="x"), stop="tool_use"
        ),
        api_message(api_text("397.8, ticket filed.")),
        api_message(api_text("You asked for 17% of 2340.")),
    )
    client = cl(messages=factory)
    data = run(client, "messages_api", "What is 17% of 2340? File a ticket.")
    results = {e["name"]: e["result"] for e in of(data, "tool_result")}
    assert results["calculator"]["result"] == 397.8  # our function, run by the SDK's runner
    assert "Try tool runner" in str(results["create_ticket"])  # MCP via async_mcp_tool
    assert data["output"] == "397.8, ticket filed."
    assert {t["name"] for t in captured[0]["tools"]} >= {
        "calculator",
        "search_docs",
        "create_ticket",
    }
    assert captured[0]["model"] == "claude-opus-5"

    run(
        client,
        "messages_api",
        "What did I ask?",
        session_id=data["session_id"],
        options={"mcp": False},
    )
    history = captured[-1]["messages"]
    assert history[0]["content"] == "What is 17% of 2340? File a ticket."  # we own the history
    assert [m["role"] for m in history] == [
        "user",
        "assistant",
        "user",
        "assistant",
        "user",
        "assistant",
        "user",
    ]


def test_messages_api_client_per_provider(settings):
    from app.adapters.claude.messages_api import default_client, model_for

    p = build_profiles(settings)
    assert type(default_client(p["raw"])).__name__ == "AsyncAnthropic"
    assert type(default_client(p["bedrock"])).__name__ == "AsyncAnthropicBedrockMantle"
    assert model_for(p["bedrock"]) == "anthropic.claude-opus-5"
    assert type(default_client(p["vertex"])).__name__ == "AsyncAnthropicVertex"


async def test_redis_session_store_protocol(redis_url):
    from app.adapters.claude.session_store import RedisSessionStore
    from app.state.cache import redis_client

    redis = redis_client(redis_url)
    await redis.flushdb()
    store = RedisSessionStore(redis, ttl_s=60)
    key = {"project_key": "-data-claude_workdir", "session_id": "s1"}
    assert await store.load(key) is None
    await store.append(key, [{"type": "user", "uuid": "u1", "timestamp": "t1"}])
    await store.append(key, [{"type": "assistant", "uuid": "a1", "timestamp": "t2"}])
    await store.append(
        {**key, "subpath": "subagents/agent-1"}, [{"type": "user", "uuid": "x", "timestamp": "t"}]
    )
    assert [e["uuid"] for e in await store.load(key)] == ["u1", "a1"]  # append-only, ordered
    assert [s["session_id"] for s in await store.list_sessions("-data-claude_workdir")] == ["s1"]
    assert await store.list_subkeys(key) == ["subagents/agent-1"]
    assert 0 < await redis.ttl("claude:-data-claude_workdir/s1") <= 60  # retention is ours
    await store.delete(key)  # cascades to subagent transcripts
    assert await store.load(key) is None and await redis.keys("claude:*") == []
    await redis.aclose()


def test_session_store_wired_when_redis_configured(cl, container, redis_url):
    container.settings.redis_url = redis_url
    script = CliScript([text("ok"), result("ok")])
    run(cl(script), "agent_sdk", "hi")
    assert type(script.options[0].session_store).__name__ == "RedisSessionStore"


def _transcript(session_id: str, cwd: str) -> list[dict]:
    """Entries shaped like the real Claude Code CLI transcript (captured from a live run)."""
    turns = [
        ("user", "I'm Ada."),
        ("assistant", "Hi Ada."),
        ("user", "Rust or Go?"),
        ("assistant", "Rust."),
    ]
    out, parent = [], None
    for i, (role, said) in enumerate(turns):
        uuid_ = f"00000000-0000-4000-8000-00000000000{i}"
        content = said if role == "user" else [{"type": "text", "text": said}]
        out.append(
            {"type": role, "uuid": uuid_, "parentUuid": parent, "sessionId": session_id, "isSidechain": False,
             "timestamp": f"2026-10-04T08:00:0{i}.000Z", "cwd": cwd, "userType": "external",
             "message": {"role": role, "content": content}}
        )  # fmt: skip
        parent = uuid_
    return out


def test_history_checkpoints_and_fork_through_session_store(cl, container, redis_url):
    import asyncio

    from claude_agent_sdk._internal.session_mutations import project_key_for_directory

    from app.state.cache import redis_client

    container.settings.redis_url = redis_url
    sid = "11111111-1111-4111-8111-111111111111"
    client = cl(CliScript([text("Rust."), result("Rust.", session_id=sid)]))
    ours = run(client, "agent_sdk", "Rust or Go?")["session_id"]

    adapter = container.registry.get("claude")
    key = {"project_key": project_key_for_directory(adapter.workdir), "session_id": sid}

    async def seed():
        redis = redis_client(redis_url)
        from app.adapters.claude.session_store import RedisSessionStore

        await RedisSessionStore(redis).append(key, _transcript(sid, adapter.workdir))
        await redis.aclose()

    asyncio.run(seed())  # what the SDK mirrors during a real run

    history = client.get(f"/v1/sessions/{ours}/history").json()
    assert [(h["role"], h["text"]) for h in history] == [
        ("user", "I'm Ada."), ("assistant", "Hi Ada."), ("user", "Rust or Go?"), ("assistant", "Rust.")
    ]  # fmt: skip
    checkpoints = client.get(f"/v1/sessions/{ours}/checkpoints").json()
    assert checkpoints[0]["text"] == "Rust."  # newest first; every message uuid is a fork point
    after_hi = next(c for c in checkpoints if c["text"] == "Hi Ada.")
    fork = client.post(
        f"/v1/sessions/{ours}/fork", json={"checkpoint_id": after_hi["checkpoint_id"]}
    ).json()
    forked = client.get(f"/v1/sessions/{fork['session_id']}/history").json()
    assert [h["text"] for h in forked] == ["I'm Ada.", "Hi Ada."]  # fork_session_via_store
