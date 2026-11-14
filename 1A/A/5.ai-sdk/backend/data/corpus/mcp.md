# Model Context Protocol (MCP)

MCP is an open protocol for connecting AI applications (clients) to tools and data (servers).

## Concepts

- Servers expose tools (functions the model can call), resources (readable data), and prompts (templates).
- Transports: stdio (the client spawns the server as a subprocess) and streamable HTTP (a remote server at a URL). SSE is the older HTTP transport.
- The Python SDK's FastMCP builds a server from decorated functions (@mcp.tool()).

## Clients in each framework

- ADK: McpToolset(connection_params=StdioConnectionParams(...) or StreamableHTTPConnectionParams(...)).
- LangGraph / LangChain: langchain-mcp-adapters MultiServerMCPClient converts MCP tools to LangChain tools.
- Strands: MCPClient(lambda: stdio_client(...)) used as a context manager; list_tools_sync() returns agent tools.
- Claude Agent SDK: mcp_servers option (stdio, sse, http, or in-process sdk servers); tool names are mcp__server__tool.
- Anthropic SDK: anthropic.lib.tools.mcp converts MCP tools for the tool runner.

## Hosting

- Remote MCP servers run behind auth: Amazon Bedrock AgentCore Gateway or Runtime on AWS; Cloud Run on GCP.
- Playwright MCP (@playwright/mcp) is a popular server that lets an agent drive a browser through accessibility snapshots.
