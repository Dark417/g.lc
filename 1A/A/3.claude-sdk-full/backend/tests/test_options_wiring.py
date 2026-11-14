"""Builds the real ClaudeAgentOptions (no CLI spawned) and asserts the wiring."""

from app.agents.factory import build_options
from app.db.database import init_db
from app.rag.factory import build_retriever


async def _noop_llm(*, system: str, prompt: str) -> str:
    return "x"


def test_options_shape(settings):
    init_db(settings.db_path)
    opts = build_options(settings, retriever=build_retriever(settings), llm=_noop_llm)

    assert opts.model == "claude-opus-5" and opts.permission_mode == "dontAsk"
    assert opts.tools == ["Task"] and opts.setting_sources == []
    assert set(opts.mcp_servers) == {"local"}  # support MCP is off in tests
    assert opts.mcp_servers["local"]["type"] == "sdk"

    assert set(opts.agents) == {"data_agent", "knowledge_agent"}
    assert opts.agents["data_agent"].tools == [
        "mcp__local__describe_schema",
        "mcp__local__list_customers",
        "mcp__local__get_customer_orders",
        "mcp__local__run_sql_query",
    ]
    assert opts.agents["knowledge_agent"].tools == ["mcp__local__search_knowledge_base"]

    assert "mcp__local__write_polished_text" in opts.allowed_tools
    assert "mcp__local__calculate" in opts.allowed_tools
    assert opts.env == {"ANTHROPIC_API_KEY": "test"}


def test_support_mcp_transports(settings):
    from app.agents.orchestrator import build_support_mcp

    assert build_support_mcp(settings) is None
    stdio = build_support_mcp(settings.model_copy(update={"mcp_transport": "stdio"}))
    assert stdio["type"] == "stdio" and stdio["args"] == ["-m", "app.mcp.server"]
    http = build_support_mcp(settings.model_copy(update={"mcp_transport": "http"}))
    assert http == {"type": "http", "url": settings.mcp_url}
