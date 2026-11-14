"""Every LangGraph pattern compiled and streamed for real, with scripted chat models."""

import pytest
from fastapi.testclient import TestClient

from app.adapters.langgraph.adapter import LangGraphAdapter
from app.adapters.langgraph.models import default_chat_model
from app.main import create_app
from app.providers import build_profiles
from tests.fakes.langchain import Scripts, call, say


@pytest.fixture
def lg(container):
    def make(scripts: Scripts) -> TestClient:
        container.registry.register(LangGraphAdapter(container.settings, model_factory=scripts))
        return TestClient(create_app(container))

    return make


def run(client, pattern, message="", ok=True, **kw):
    body = {"framework": "langgraph", "pattern": pattern, "message": message, **kw}
    r = client.post("/v1/runs", json=body)
    assert r.status_code == 200, r.text
    data = r.json()
    if ok:
        errors = [e for e in data["events"] if e["type"] == "error"]
        assert not errors, errors
    return data


def of(data, type_):
    return [e for e in data["events"] if e["type"] == type_]


def test_react_tools_mcp_checkpointer_and_store(lg):
    scripts = Scripts(
        agent=[
            call("calculator", expression="0.17*2340"),
            call("create_ticket", title="Evaluate LangGraph", body="x"),
            say("397.8, and ticket filed."),
            say("You filed a ticket about LangGraph."),
            say("New thread: I recall you asked about LangGraph tickets."),
        ]
    )
    client = lg(scripts)
    data = run(client, "react", "What is 17% of 2340? File a ticket to evaluate LangGraph.")
    results = {e["name"]: e["result"] for e in of(data, "tool_result")}
    assert results["calculator"]["result"] == 397.8
    assert "Evaluate LangGraph" in str(results["create_ticket"])  # MCP via langchain-mcp-adapters
    assert data["output"] == "397.8, and ticket filed."

    # Same thread: the checkpointer restores history.
    run(client, "react", "What did I ask?", session_id=data["session_id"])
    assert "17% of 2340" in scripts["agent"].all_text(3)

    # New thread, same user: pre_model_hook pulls long-term memories from the Store.
    run(client, "react", "Anything about LangGraph tickets?")
    assert "Facts from earlier conversations" in scripts["agent"].system_text(4)


def test_graph_retrieve_node_then_tool_loop(lg):
    scripts = Scripts(
        agent=[
            call("current_time", timezone="UTC"),
            say("AgentCore Memory stores events [agentcore.md]."),
        ]
    )
    data = run(lg(scripts), "graph", "What does AgentCore Memory store?", options={"mcp": False})
    nodes = [e["agent"] for e in of(data, "agent")]
    assert nodes[:3] == ["retrieve", "agent", "tools"]
    state = of(data, "state")[0]["data"]
    assert state["retrieval_backend"] == "local" and "agentcore.md" in state["context"]
    assert "Retrieved context" in scripts["agent"].system_text(0)
    assert data["output"].startswith("AgentCore Memory stores")


def test_middleware_pii_policy_and_dynamic_prompt(lg):
    scripts = Scripts(agent=[call("run_cli", command="date"), say("Done.")])
    data = run(
        lg(scripts),
        "middleware",
        "My email is ada@example.com, run date",
        options={"mcp": False, "deny_tools": ["run_cli"]},
    )
    first = scripts["agent"].requests[0]
    assert "ada@example.com" not in " ".join(
        str(m.content) for m in first
    )  # PIIMiddleware redacted
    assert "The user id is demo-user" in scripts["agent"].system_text(0)  # @dynamic_prompt
    assert of(data, "tool_result")[0]["result"]["status"] == "denied"  # @wrap_tool_call policy
    assert data["output"] == "Done."


def test_supervisor_routes_to_subgraph_workers(lg):
    scripts = Scripts(
        supervisor=[
            call("Route", next="calculator"),
            call("Route", next="researcher"),
            call("Route", next="FINISH"),
        ],
        calculator=[call("calculator", expression="2+2"), say("4")],
        researcher=[
            call("search_docs", query="Send API"),
            say("Send creates parallel branches [langgraph.md]."),
        ],
    )
    data = run(lg(scripts), "supervisor", "What is 2+2, and what is Send?")
    agents = [e["agent"] for e in of(data, "agent")]
    assert "calculator" in agents and "researcher" in agents
    tool_calls = [e["name"] for e in of(data, "tool_call")]
    assert "calculator" in tool_calls and "search_docs" in tool_calls  # streamed from subgraphs
    assert [e["data"]["next"] for e in of(data, "state") if "next" in e["data"]] == [
        "calculator",
        "researcher",
        "FINISH",
    ]
    assert data["output"] == "Send creates parallel branches [langgraph.md]."


def test_map_reduce_with_send(lg):
    scripts = Scripts(
        planner=[call("Plan", sub_questions=["What is ADK LoopAgent?", "What is LangGraph Send?"])],
        worker=[say("repeats sub-agents"), say("parallel branches")],
        reducer=[say("Both enable iteration or parallelism.")],
    )
    data = run(lg(scripts), "map_reduce", "Compare ADK LoopAgent with LangGraph Send")
    branches = [e for e in of(data, "agent") if e["agent"] == "answer_one"]
    assert branches  # Send fanned out
    reducer_input = scripts["reducer"].all_text(0)
    assert "What is ADK LoopAgent?" in reducer_input and "What is LangGraph Send?" in reducer_input
    assert data["output"] == "Both enable iteration or parallelism."


def test_hitl_interrupt_then_resume(lg):
    scripts = Scripts(agent=[call("run_cli", command="uname -s"), say("The OS is Linux.")])
    client = lg(scripts)
    first = run(client, "hitl", "What OS is this? Use uname.", options={"mcp": False})
    intr = of(first, "interrupt")
    assert intr and intr[0]["data"]["tool_calls"][0]["name"] == "run_cli"
    assert not of(first, "done")  # paused, not finished

    resumed = run(
        client,
        "hitl",
        session_id=first["session_id"],
        resume={"approve": True},
        options={"mcp": False},
    )
    result = of(resumed, "tool_result")[0]["result"]
    assert result["status"] == "ok" and "Linux" in result["output"]
    assert resumed["output"] == "The OS is Linux."


def test_hitl_reject(lg):
    scripts = Scripts(
        agent=[call("run_cli", command="whoami"), say("I was not allowed to run that.")]
    )
    client = lg(scripts)
    first = run(client, "hitl", "Who am I?", options={"mcp": False})
    resumed = run(
        client,
        "hitl",
        session_id=first["session_id"],
        resume={"approve": False},
        options={"mcp": False},
    )
    # the tool never ran: the review node answered the call with a denial instead
    assert [e["result"] for e in of(resumed, "tool_result")] == [{"status": "denied by reviewer"}]
    assert resumed["output"] == "I was not allowed to run that."


def test_resume_without_pause_is_error(lg):
    client = lg(Scripts(agent=[say("hi")]))
    sid = run(client, "hitl", "hi", options={"mcp": False})["session_id"]
    data = run(client, "hitl", session_id=sid, resume={"approve": True}, ok=False)
    assert "nothing to resume" in data["events"][-1]["message"]


def test_model_class_per_branch(settings):
    p = build_profiles(settings)
    assert type(default_chat_model(p["raw"], "anthropic", "agent")).__name__ == "ChatAnthropic"
    assert (
        type(default_chat_model(p["raw"], "gemini", "agent")).__name__ == "ChatGoogleGenerativeAI"
    )
    assert type(default_chat_model(p["bedrock"], None, "agent")).__name__ == "ChatBedrockConverse"
    assert type(default_chat_model(p["vertex"], "gemini", "agent")).__name__ == "ChatVertexAI"
    assert (
        type(default_chat_model(p["vertex"], "anthropic", "agent")).__name__
        == "ChatAnthropicVertex"
    )


async def test_bedrock_persistence_uses_agentcore(settings):
    from app.adapters.langgraph.persistence import checkpointer, store

    async with checkpointer("raw", settings) as saver:
        assert type(saver).__name__ == "AsyncSqliteSaver"
    settings.agentcore_memory_id = "mem-1"
    async with checkpointer("bedrock", settings) as saver:
        assert type(saver).__name__ == "AgentCoreMemorySaver"
    assert type(store("bedrock", settings)).__name__ == "AgentCoreMemoryStore"
    assert type(store("vertex", settings)).__name__ == "InMemoryStore"
