"""Our MCP server over real stdio, with the official MCP client."""

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from app.mcp.clients import server_specs


async def test_workbench_over_stdio(settings):
    spec = server_specs(settings)[0]
    params = StdioServerParameters(command=spec.command, args=spec.args, env=spec.env, cwd=spec.cwd)
    async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
        await session.initialize()
        names = {t.name for t in (await session.list_tools()).tools}
        assert names == {"create_ticket", "list_tickets", "get_ticket", "word_count"}
        created = await session.call_tool(
            "create_ticket", {"title": "Evaluate AgentCore", "body": "memory"}
        )
        assert '"status": "open"' in created.content[0].text
        listed = await session.call_tool("list_tickets", {"status": "open"})
        assert "Evaluate AgentCore" in listed.content[0].text
    assert (settings.data_path / "tickets.db").exists()  # DATA_DIR reached the subprocess


def test_playwright_mcp_is_opt_in(settings):
    assert [s.name for s in server_specs(settings)] == ["workbench"]
    settings.playwright_mcp_enabled = True
    pw = server_specs(settings)[1]
    assert pw.command == "npx" and "@playwright/mcp@latest" in pw.args
