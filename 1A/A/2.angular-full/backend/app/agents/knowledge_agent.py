"""Specialist: policies/products via RAG, plus external support tools via MCP."""

from collections.abc import Callable

from google.adk.agents import LlmAgent
from google.adk.tools.base_toolset import BaseToolset


def build_knowledge_agent(
    model: str, rag_tool: Callable, mcp_toolset: BaseToolset | None
) -> LlmAgent:
    tools: list = [rag_tool]
    if mcp_toolset is not None:
        tools.append(mcp_toolset)  # a toolset expands to its tools at runtime
    return LlmAgent(
        name="knowledge_agent",
        model=model,
        description=(
            "Answers questions about store policies (returns, shipping, warranty, product care) "
            "from the knowledge base, checks weather, and looks up or creates support tickets."
        ),
        instruction=(
            "Always call search_knowledge_base before answering policy or product-care questions "
            "and ground your answer in the returned passages, citing the source file name. "
            "Use get_weather, lookup_ticket and create_ticket when the user asks about weather or "
            "support tickets. If the knowledge base has nothing relevant, say you don't know."
        ),
        tools=tools,
    )
