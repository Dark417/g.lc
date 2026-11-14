"""Wire settings + infrastructure into agent options. One function, one place."""

from claude_agent_sdk import ClaudeAgentOptions

from app.agents.llm import ClaudeText, TextLLM
from app.agents.orchestrator import build_agent_options, build_support_mcp
from app.agents.tools_server import build_tools_server
from app.agents.writer_loop import build_writer_tool
from app.config import Settings
from app.rag.retriever import Retriever
from app.tools.db_tools import build_db_tools
from app.tools.local_tools import calculate, get_current_time
from app.tools.rag_tools import build_rag_tool


def build_options(
    settings: Settings, *, retriever: Retriever, llm: TextLLM | None = None
) -> ClaudeAgentOptions:
    llm = llm or ClaudeText(settings.judge_model, settings.anthropic_api_key)
    functions = [
        calculate,
        get_current_time,
        *build_db_tools(settings.db_path),
        build_rag_tool(retriever, settings.rag_top_k),
        build_writer_tool(llm),
    ]
    return build_agent_options(
        settings,
        tools_server=build_tools_server(functions),
        support_mcp=build_support_mcp(settings),
    )
