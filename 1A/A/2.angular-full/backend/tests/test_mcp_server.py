"""Talks to app/mcp/server.py over stdio with the plain MCP client, exactly as ADK does."""

import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mcp_server_lists_and_calls_tools():
    params = StdioServerParameters(command=sys.executable, args=["-m", "app.mcp.server"])
    async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
        await session.initialize()
        names = {t.name for t in (await session.list_tools()).tools}
        assert names == {"get_weather", "lookup_ticket", "create_ticket"}

        res = await session.call_tool("get_weather", {"city": "Berlin"})
        payload = json.loads(res.content[0].text)
        assert payload["temp_c"] == 14

        res = await session.call_tool("lookup_ticket", {"ticket_id": "t-1001"})
        assert json.loads(res.content[0].text)["ticket"]["status"] == "open"
