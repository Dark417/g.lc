"""Every ADK pattern through the real ADK Runner, with scripted models per agent role."""

import pytest
from fastapi.testclient import TestClient

from app.adapters.adk.adapter import AdkAdapter
from app.main import create_app
from tests.fakes.adk import Scripts, call, say


@pytest.fixture
def adk(container):
    def make(scripts: Scripts) -> TestClient:
        container.registry.register(AdkAdapter(container.settings, model_factory=scripts))
        return TestClient(create_app(container))

    return make


def run(client, pattern, message, **kw):
    body = {"framework": "adk", "pattern": pattern, "provider": "raw", "message": message, **kw}
    r = client.post("/v1/runs", json=body)
    assert r.status_code == 200, r.text
    data = r.json()
    errors = [e for e in data["events"] if e["type"] == "error"]
    assert not errors, errors
    return data


def of(data, type_):
    return [e for e in data["events"] if e["type"] == type_]


def test_single_uses_local_and_mcp_tools_callbacks_and_memory(adk):
    scripts = Scripts(
        assistant=[
            call("calculator", expression="0.17 * 2340"),
            call("create_ticket", title="Evaluate AgentCore Memory", body="from chat"),
            say("17% of 2340 is 397.8. I filed a ticket to evaluate AgentCore Memory."),
            say("You asked me to file a ticket about AgentCore Memory."),
        ]
    )
    client = adk(scripts)
    data = run(
        client, "single", "What is 17% of 2340? Then file a ticket to evaluate AgentCore Memory."
    )
    results = {e["name"]: e["result"] for e in of(data, "tool_result")}
    assert results["calculator"]["result"] == 397.8
    assert "Evaluate AgentCore Memory" in str(results["create_ticket"])  # MCP over stdio
    assert data["output"].startswith("17% of 2340 is 397.8")
    model = scripts["assistant"]
    assert "User id: demo-user" in model.system(0)  # before_model_callback injected context
    offered = set(model.requests[0].tools_dict)
    assert {"calculator", "search_docs", "browse", "run_cli", "create_ticket"} <= offered
    assert "run_code" not in offered  # no sandbox on raw

    # New session, same user: PreloadMemoryTool injects the earlier conversation.
    run(client, "single", "Remind me about the AgentCore ticket.")
    past = model.contents_text(3)
    assert "<PAST_CONVERSATIONS>" in past and "397.8" in past


def test_tool_policy_denies_by_name(adk):
    scripts = Scripts(assistant=[call("run_cli", command="date"), say("Not allowed.")])
    data = run(
        adk(scripts), "single", "Run date", options={"deny_tools": ["run_cli"], "mcp": False}
    )
    assert of(data, "tool_result")[0]["result"]["status"] == "denied"


def test_sequential_passes_state(adk):
    scripts = Scripts(
        researcher=[
            call("search_docs", query="AgentCore Memory"),
            say("- events + strategies (agentcore.md)"),
        ],
        writer=[say("AgentCore Memory stores events and extracted records [agentcore.md].")],
    )
    data = run(adk(scripts), "sequential", "What does AgentCore Memory store?")
    assert [e["agent"] for e in of(data, "agent")] == ["researcher", "writer"]
    assert "events + strategies" in scripts["writer"].system(0)  # {notes} templated from state
    assert data["output"].startswith("AgentCore Memory stores")
    assert any("notes" in e["data"] for e in of(data, "state"))


def test_parallel_fans_out_and_in(adk):
    scripts = Scripts(
        docs_researcher=[call("search_docs", query="LoopAgent"), say("docs: LoopAgent repeats")],
        web_researcher=[say("no web findings")],
        synthesizer=[say("Merged answer.")],
    )
    data = run(adk(scripts), "parallel", "Explain LoopAgent")
    agents = {e["agent"] for e in of(data, "agent")}
    assert {"docs_researcher", "web_researcher", "synthesizer"} <= agents
    system = scripts["synthesizer"].system(0)
    assert "docs: LoopAgent repeats" in system and "no web findings" in system
    assert data["output"] == "Merged answer."


def test_loop_until_critic_escalates(adk):
    scripts = Scripts(
        drafter=[say("draft v1"), say("draft v2 [adk.md]")],
        critic=[say("Cite a source."), call("exit_loop")],
    )
    data = run(adk(scripts), "loop", "What is a LoopAgent?")
    assert [e["agent"] for e in of(data, "agent")] == ["drafter", "critic", "drafter", "critic"]
    assert "Cite a source." in scripts["drafter"].system(1)  # critique fed back via {critique?}
    assert data["output"] == "draft v2 [adk.md]"


def test_coordinator_agent_tool_and_transfer(adk):
    scripts = Scripts(
        coordinator=[
            call("math_agent", request="17% of 2340"),
            call("transfer_to_agent", agent_name="researcher"),
        ],
        math_agent=[call("calculator", expression="0.17*2340"), say("397.8")],
        researcher=[
            call("search_docs", query="AgentTool"),
            say("AgentTool keeps control [adk.md]."),
        ],
    )
    data = run(
        adk(scripts), "coordinator", "17% of 2340, and what is AgentTool?", options={"mcp": False}
    )
    names = [e["name"] for e in of(data, "tool_call")]
    # AgentTool: call and return. The inner agent runs in its own runner, so its calculator call
    # is not in the parent's event stream; only the AgentTool call and its result are.
    assert names == ["math_agent", "transfer_to_agent", "search_docs"]
    assert "397.8" in str(of(data, "tool_result")[0]["result"])
    assert len(scripts["math_agent"].requests) == 2  # it did call the calculator internally
    # transfer: control moved to researcher, who produced the final answer
    assert data["output"] == "AgentTool keeps control [adk.md]."


@pytest.mark.parametrize(
    ("message", "route", "role", "script"),
    [
        (
            "what is 2 + 2",
            "math_agent",
            "math_agent",
            [call("calculator", expression="2+2"), say("4")],
        ),
        (
            "what time is it",
            "ops_agent",
            "ops_agent",
            [call("current_time", timezone="UTC"), say("noon")],
        ),
        ("what is AgentCore", "researcher", "researcher", [say("A set of services.")]),
    ],
)
def test_custom_router_is_deterministic(adk, message, route, role, script):
    data = run(adk(Scripts(**{role: script})), "custom", message)
    assert {"route": route} in [e["data"] for e in of(data, "state")]
    assert of(data, "agent")[-1]["agent"] == role


def test_workflow_graph_routes_and_formats(adk):
    scripts = Scripts(
        math_agent=[call("calculator", expression="0.17*2340"), say("0.17*2340 = 397.8")]
    )
    data = run(adk(scripts), "workflow", "What is 17% of 2340?")
    assert {"route": "math"} in [e["data"] for e in of(data, "state")]
    assert data["output"] == "0.17*2340 = 397.8\n\n— via ADK Workflow"


def test_workflow_ops_branch_uses_mcp(adk):
    scripts = Scripts(
        ops_agent=[call("create_ticket", title="Try Workflow", body="x"), say("Ticket 1 created")]
    )
    data = run(adk(scripts), "workflow", "Please open a ticket to try Workflow")
    assert of(data, "tool_result")[0]["name"] == "create_ticket"
    assert data["output"].startswith("Ticket 1 created")


def test_session_continues_with_history(adk):
    scripts = Scripts(assistant=[say("Hi Ada."), say("Your name is Ada.")])
    client = adk(scripts)
    sid = run(client, "single", "I am Ada", options={"mcp": False})["session_id"]
    run(client, "single", "What is my name?", session_id=sid, options={"mcp": False})
    assert "I am Ada" in scripts["assistant"].contents_text(1)  # DatabaseSessionService history


def test_llm_call_cap(adk, container):
    container.settings.max_llm_calls = 2
    scripts = Scripts(assistant=[call("current_time", timezone="UTC")] * 5)
    client = adk(scripts)
    body = {"framework": "adk", "pattern": "single", "message": "loop", "options": {"mcp": False}}
    events = client.post("/v1/runs", json=body).json()["events"]
    assert events[-1]["type"] == "error"
