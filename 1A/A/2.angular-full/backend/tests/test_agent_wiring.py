"""Builds the real agent tree (no model calls) and asserts the wiring is what the docs claim."""

from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent
from google.adk.tools import AgentTool, FunctionTool

from app.agents.factory import build_root_agent
from app.db.database import init_db
from app.rag.factory import build_retriever


def test_tree_shape(settings):
    init_db(settings.db_path)
    settings = settings.model_copy(update={"knowledge_dir": "data/knowledge"})
    root = build_root_agent(settings, retriever=build_retriever(settings), mcp_toolset=None)

    assert isinstance(root, LlmAgent) and root.name == "orchestrator"
    local = {t.__name__ for t in root.tools if callable(t) and not isinstance(t, AgentTool)}
    assert local == {"calculate", "get_current_time"}

    specialists = {t.agent.name: t.agent for t in root.tools if isinstance(t, AgentTool)}
    assert set(specialists) == {"data_agent", "knowledge_agent", "writer"}

    data_tools = {t.__name__ for t in specialists["data_agent"].tools}
    assert data_tools == {
        "describe_schema",
        "list_customers",
        "get_customer_orders",
        "run_sql_query",
    }
    assert [t.__name__ for t in specialists["knowledge_agent"].tools] == ["search_knowledge_base"]

    writer = specialists["writer"]
    assert isinstance(writer, SequentialAgent)
    loop, finalizer = writer.sub_agents
    assert isinstance(loop, LoopAgent) and loop.max_iterations == 3
    assert [a.name for a in loop.sub_agents] == ["drafter", "critic"]
    assert finalizer.name == "finalizer"


def test_function_tools_have_docs_and_schemas(settings):
    from app.tools.db_tools import build_db_tools

    init_db(settings.db_path)
    for fn in build_db_tools(settings.db_path):
        decl = FunctionTool(fn)._get_declaration()
        assert decl.description, fn.__name__
