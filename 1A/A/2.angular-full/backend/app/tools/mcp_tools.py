"""Client side of MCP: plug an MCP server's tools into an ADK agent as a toolset."""

import sys

from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StdioConnectionParams,
    StreamableHTTPConnectionParams,
)
from mcp import StdioServerParameters

from app.config import Settings


def build_mcp_toolset(settings: Settings) -> McpToolset | None:
    if settings.mcp_transport == "off":
        return None
    if settings.mcp_transport == "http":
        # PRODUCTION: the MCP server is its own deployment; we only know its URL.
        # Add auth via `header_provider=` or `auth_credential=` here.
        return McpToolset(
            connection_params=StreamableHTTPConnectionParams(url=settings.mcp_url, timeout=30),
        )
    # ILLUSTRATION: spawn the server as a child process and talk over stdin/stdout.
    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=sys.executable, args=["-m", "app.mcp.server"]
            ),
            timeout=30,
        ),
        # Expose only what this agent needs; a toolset can be filtered by name.
        tool_filter=["get_weather", "lookup_ticket", "create_ticket"],
    )
