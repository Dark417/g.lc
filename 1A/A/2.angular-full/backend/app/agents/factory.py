"""Wire settings + infrastructure into the agent tree. One function, one place."""

from google.adk.agents import LlmAgent
from google.adk.tools.base_toolset import BaseToolset

from app.agents.data_agent import build_data_agent
from app.agents.knowledge_agent import build_knowledge_agent
from app.agents.orchestrator import build_orchestrator
from app.agents.writer_pipeline import build_writer_pipeline
from app.config import Settings
from app.rag.retriever import Retriever
from app.tools.db_tools import build_db_tools
from app.tools.rag_tools import build_rag_tool


def build_root_agent(
    settings: Settings, *, retriever: Retriever, mcp_toolset: BaseToolset | None
) -> LlmAgent:
    data_agent = build_data_agent(settings.model, build_db_tools(settings.db_path))
    knowledge_agent = build_knowledge_agent(
        settings.model, build_rag_tool(retriever, settings.rag_top_k), mcp_toolset
    )
    writer = build_writer_pipeline(settings.model)
    return build_orchestrator(settings.model, [data_agent, knowledge_agent, writer])
