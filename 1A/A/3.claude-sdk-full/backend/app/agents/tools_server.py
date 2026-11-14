"""Turn plain Python tool functions into an in-process MCP server the Claude Agent SDK can use.

ADK reads a function's signature + docstring and makes it a tool. The Claude Agent SDK wants
`@tool(name, description, schema)` around an async handler that returns MCP content blocks.
`as_sdk_tool` bridges the two so app/tools/* stays framework-agnostic (same code as project 2).

Tool names on the wire become `mcp__<server>__<tool>`, e.g. `mcp__local__calculate`.
"""

import inspect
import json
from collections.abc import Callable

from claude_agent_sdk import SdkMcpTool, create_sdk_mcp_server, tool
from claude_agent_sdk.types import McpSdkServerConfig

SERVER_NAME = "local"


def as_sdk_tool(fn: Callable) -> SdkMcpTool:
    """Wrap `fn(a: str, b: int) -> dict` as an SDK MCP tool. Works for sync and async fns."""
    sig = inspect.signature(fn)
    schema = {name: p.annotation for name, p in sig.parameters.items()}
    description = inspect.getdoc(fn) or fn.__name__

    @tool(fn.__name__, description, schema)
    async def handler(args: dict) -> dict:
        result = fn(**args)
        if inspect.isawaitable(result):
            result = await result
        return {"content": [{"type": "text", "text": json.dumps(result, default=str)}]}

    return handler


def build_tools_server(functions: list[Callable]) -> McpSdkServerConfig:
    return create_sdk_mcp_server(
        name=SERVER_NAME, version="0.1.0", tools=[as_sdk_tool(f) for f in functions]
    )


def tool_id(fn_name: str, server: str = SERVER_NAME) -> str:
    """The name Claude uses to call an MCP tool."""
    return f"mcp__{server}__{fn_name}"
