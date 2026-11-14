"""The adapter from plain functions to SDK MCP tools, exercised without the CLI."""

import json

from app.agents.tools_server import as_sdk_tool, build_tools_server, tool_id
from app.tools.local_tools import calculate


async def test_as_sdk_tool_wraps_signature_docstring_and_result():
    t = as_sdk_tool(calculate)
    assert t.name == "calculate"
    assert "arithmetic" in t.description.lower()
    assert t.input_schema == {"expression": str}
    out = await t.handler({"expression": "6*7"})
    assert json.loads(out["content"][0]["text"])["result"] == 42


async def test_async_functions_are_supported():
    async def ping(name: str) -> dict:
        """Ping."""
        return {"pong": name}

    out = await as_sdk_tool(ping).handler({"name": "x"})
    assert json.loads(out["content"][0]["text"]) == {"pong": "x"}


def test_server_config_and_tool_ids():
    cfg = build_tools_server([calculate])
    assert cfg["type"] == "sdk" and cfg["name"] == "local"
    assert tool_id("calculate") == "mcp__local__calculate"
    assert tool_id("get_weather", "support") == "mcp__support__get_weather"
