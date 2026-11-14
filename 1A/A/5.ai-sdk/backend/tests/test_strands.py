"""Every Strands pattern through the real Strands event loop, with scripted models per role."""

import pytest
from fastapi.testclient import TestClient

from app.adapters.strands.adapter import StrandsAdapter
from app.adapters.strands.models import default_strands_model
from app.main import create_app
from app.providers import build_profiles
from tests.fakes.strands import Scripts, call, say


@pytest.fixture
def sa(container):
    def make(scripts: Scripts) -> TestClient:
        container.registry.register(StrandsAdapter(container.settings, model_factory=scripts))
        return TestClient(create_app(container))

    return make


def run(client, pattern, message, **kw):
    body = {"framework": "strands", "pattern": pattern, "message": message, **kw}
    r = client.post("/v1/runs", json=body)
    assert r.status_code == 200, r.text
    data = r.json()
    errors = [e for e in data["events"] if e["type"] == "error"]
    assert not errors, errors
    return data


def of(data, type_):
    return [e for e in data["events"] if e["type"] == type_]


def test_single_tools_mcp_hooks_and_file_session(sa, settings):
    scripts = Scripts(
        assistant=[
            call("calculator", expression="0.17*2340"),
            call("create_ticket", title="Evaluate Strands", body="x"),
            say("397.8; ticket filed."),
            say("Your earlier question was about 17% of 2340."),
        ]
    )
    client = sa(scripts)
    data = run(client, "single", "What is 17% of 2340? File a ticket to evaluate Strands.")
    results = {e["name"]: e["result"] for e in of(data, "tool_result")}
    assert results["calculator"]["result"] == 397.8
    assert "Evaluate Strands" in str(results["create_ticket"])  # MCPClient over stdio
    assert data["output"] == "397.8; ticket filed."
    assert data["events"][-1].get("data", {}).get("usage")

    # A new Agent object on the next request restores the conversation from the session manager.
    run(
        client,
        "single",
        "What did I ask before?",
        session_id=data["session_id"],
        options={"mcp": False},
    )
    restored = scripts["assistant"].requests[3]["messages"]
    assert "17% of 2340" in str(restored[0])
    assert (settings.data_path / "strands_sessions").exists()


def test_hook_cancels_denied_tool(sa):
    scripts = Scripts(assistant=[call("run_cli", command="date"), say("Not permitted.")])
    data = run(sa(scripts), "single", "run date", options={"mcp": False, "deny_tools": ["run_cli"]})
    result = of(data, "tool_result")[0]["result"]
    assert result["status"] == "error" and "disabled by policy" in str(result["error"])
    assert data["output"] == "Not permitted."


def test_agents_as_tools(sa):
    scripts = Scripts(
        orchestrator=[call("math_assistant", problem="17% of 2340"), say("It is 397.8.")],
        math_assistant=[call("calculator", expression="0.17*2340"), say("397.8")],
    )
    data = run(sa(scripts), "agents_as_tools", "What is 17% of 2340?")
    assert of(data, "tool_result")[0]["name"] == "math_assistant"
    assert "397.8" in str(of(data, "tool_result")[0]["result"])
    assert len(scripts["math_assistant"].requests) == 2  # the specialist ran its own loop
    assert data["output"] == "It is 397.8."


def test_swarm_handoffs(sa):
    scripts = Scripts(
        researcher=[
            call("search_docs", query="Swarm"),
            call("handoff_to_agent", agent_name="writer", message="notes: swarm hands off"),
            say("handed off"),
        ],
        writer=[
            call("handoff_to_agent", agent_name="reviewer", message="draft ready"),
            say("handed off"),
        ],
        reviewer=[say("A Swarm lets agents hand off to each other [strands.md].")],
    )
    data = run(sa(scripts), "swarm", "What is a Strands Swarm?")
    assert [e["agent"] for e in of(data, "agent")] == ["researcher", "writer", "reviewer"]
    assert "handoff_to_agent" in [e["name"] for e in of(data, "tool_call")]
    assert data["output"] == "A Swarm lets agents hand off to each other [strands.md]."


@pytest.mark.parametrize(
    ("message", "calc_runs"),
    [("What is 17% of 2340 in Strands terms?", True), ("What is a Strands Graph?", False)],
)
def test_graph_conditional_edge(sa, message, calc_runs):
    scripts = Scripts(
        research=[say("notes")],
        calculate=[call("calculator", expression="0.17*2340"), say("397.8")],
        report=[say("Final report.")],
    )
    data = run(sa(scripts), "graph", message)
    agents = [e["agent"] for e in of(data, "agent")]
    assert agents[0] == "research" and agents[-1] == "report"
    assert ("calculate" in agents) is calc_runs
    assert data["output"] == "Final report."


def test_structured_output(sa):
    brief = {
        "topic": "AgentCore Memory",
        "summary": "Managed memory for agents.",
        "key_points": ["events", "strategies", "namespaces"],
        "sources": ["agentcore.md"],
    }
    scripts = Scripts(
        brief_writer=[call("search_docs", query="AgentCore Memory"), call("ResearchBrief", **brief)]
    )
    data = run(sa(scripts), "structured", "Brief me on AgentCore Memory")
    assert data["output"] == brief
    assert "ResearchBrief" in scripts["brief_writer"].requests[0]["tools"]


def test_model_class_per_branch(settings):
    p = build_profiles(settings)
    assert type(default_strands_model(p["raw"], "anthropic", "a")).__name__ == "AnthropicModel"
    assert type(default_strands_model(p["raw"], "gemini", "a")).__name__ == "GeminiModel"
    settings.bedrock_guardrail_id = "gr-1"
    bedrock = default_strands_model(p["bedrock"], None, "a")
    assert (
        type(bedrock).__name__ == "BedrockModel" and bedrock.get_config()["guardrail_id"] == "gr-1"
    )
    vertex_claude = default_strands_model(p["vertex"], "anthropic", "a")
    assert type(vertex_claude.client).__name__ == "AsyncAnthropicVertex"


def test_session_manager_falls_back_to_file(settings):
    """bedrock without AGENTCORE_MEMORY_ID degrades to the local file session manager."""
    from app.adapters.strands.state import session_manager

    assert type(session_manager("raw", settings, "s1", "u1")).__name__ == "FileSessionManager"
    assert type(session_manager("bedrock", settings, "s2", "u1")).__name__ == "FileSessionManager"
