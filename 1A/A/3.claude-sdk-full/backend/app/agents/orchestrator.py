"""The agent tree, expressed as Claude Agent SDK options.

Mapping from project 2 (ADK) to here:
- LlmAgent orchestrator            -> ClaudeAgentOptions.system_prompt + the SDK's own loop
- AgentTool(data_agent) etc.       -> `agents={...: AgentDefinition}` + the built-in `Task` tool
- FunctionTool(calculate) etc.     -> in-process SDK MCP server (`mcp__local__*`)
- McpToolset(stdio/http)           -> `mcp_servers={"support": {"type": "stdio"|"http", ...}}`
- LoopAgent writer                 -> hand-rolled loop behind the `write_polished_text` tool
- Runner + SessionService          -> `query(prompt, options)` with `session_id` / `resume`
"""

import sys

from claude_agent_sdk import AgentDefinition, ClaudeAgentOptions
from claude_agent_sdk.types import McpSdkServerConfig, McpServerConfig

from app.agents.tools_server import tool_id
from app.config import Settings

SUBAGENT_TOOL = "Task"  # the built-in tool that spawns a subagent from `agents`

LOCAL_TOOLS = ["calculate", "get_current_time"]
DB_TOOLS = ["describe_schema", "list_customers", "get_customer_orders", "run_sql_query"]
RAG_TOOLS = ["search_knowledge_base"]
WRITER_TOOLS = ["write_polished_text"]
SUPPORT_TOOLS = ["get_weather", "lookup_ticket", "create_ticket"]

ORCHESTRATOR_PROMPT = """You are the assistant for Acme Outdoor, an outdoor-gear store.
Route work to your tools and subagents:
- data_agent (via Task): anything about customers, orders, revenue, tiers.
- knowledge_agent (via Task): policies (returns, shipping, warranty, product care), weather,
  support tickets.
- write_polished_text: when the user wants a polished piece of text written.
- calculate / get_current_time: math and dates; never do arithmetic in your head.
You may use several tools for one question and combine their answers. Be concise, and say so
when something is unknown. Never invent customer data or policies."""


def build_support_mcp(settings: Settings) -> McpServerConfig | None:
    if settings.mcp_transport == "off":
        return None
    if settings.mcp_transport == "http":
        # PRODUCTION: the MCP server is its own deployment; we only know its URL.
        return {"type": "http", "url": settings.mcp_url}
    # ILLUSTRATION: the SDK spawns the server as a child process over stdio.
    return {"type": "stdio", "command": sys.executable, "args": ["-m", "app.mcp.server"]}


def build_agent_options(
    settings: Settings,
    *,
    tools_server: McpSdkServerConfig,
    support_mcp: McpServerConfig | None,
) -> ClaudeAgentOptions:
    local = [tool_id(n) for n in LOCAL_TOOLS + WRITER_TOOLS]
    db = [tool_id(n) for n in DB_TOOLS]
    rag = [tool_id(n) for n in RAG_TOOLS]
    support = [tool_id(n, "support") for n in SUPPORT_TOOLS] if support_mcp else []

    mcp_servers: dict[str, McpServerConfig] = {"local": tools_server}
    if support_mcp:
        mcp_servers["support"] = support_mcp

    agents = {
        "data_agent": AgentDefinition(
            description=(
                "Answers questions about customers, orders, revenue and subscription tiers "
                "by querying the company database."
            ),
            prompt=(
                "You answer questions about customers and orders using your tools. Prefer "
                "list_customers and get_customer_orders. For aggregates or anything else, call "
                "describe_schema then run_sql_query with a single SELECT. Reply with the facts "
                "you found, compactly. Never invent data; if a tool returns not_found or error, "
                "say so."
            ),
            tools=db,
        ),
        "knowledge_agent": AgentDefinition(
            description=(
                "Answers questions about store policies (returns, shipping, warranty, product "
                "care) from the knowledge base, checks weather, and looks up or creates support "
                "tickets."
            ),
            prompt=(
                "Always call search_knowledge_base before answering policy or product-care "
                "questions and ground your answer in the returned passages, citing the source "
                "file name. Use get_weather, lookup_ticket and create_ticket for weather or "
                "support tickets. If the knowledge base has nothing relevant, say you don't know."
            ),
            tools=rag + support,
        ),
    }

    return ClaudeAgentOptions(
        model=settings.model,
        effort=settings.effort,
        system_prompt=ORCHESTRATOR_PROMPT,
        mcp_servers=mcp_servers,
        agents=agents,
        # Only the built-in Task tool; no file/bash tools, this isn't a coding agent.
        tools=[SUBAGENT_TOOL],
        allowed_tools=[SUBAGENT_TOOL, *local, *db, *rag, *support],
        permission_mode="dontAsk",  # non-interactive: anything not allowed above is denied
        setting_sources=[],  # ignore ~/.claude settings on the server
        max_turns=settings.max_turns,
        cwd=settings.workdir,
        env={"ANTHROPIC_API_KEY": settings.anthropic_api_key},
        forward_subagent_text=True,  # subagent prose becomes agent_text trace events
    )
