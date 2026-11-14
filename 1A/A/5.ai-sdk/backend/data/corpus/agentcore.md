# Amazon Bedrock AgentCore

AgentCore is a set of managed services for running agents built with any framework (Strands, LangGraph, ADK, CrewAI, ...) and any model. Each service can be used on its own.

## Runtime

- Serverless hosting for agents and MCP servers with session isolation (one microVM per session), long-running sessions, and streaming.
- The Python SDK's BedrockAgentCoreApp wraps an entrypoint function; the service calls POST /invocations and GET /ping on port 8080.

## Memory

- Short-term memory stores raw conversation events per actor and session (create_event, list_events, get_last_k_turns).
- Long-term memory is extracted asynchronously from events by strategies: semantic (facts), summary (per session), and user preference. Records live under namespaces such as /users/{actorId}/facts and are queried with retrieve_memories (semantic search).
- Integrations: AgentCoreMemorySessionManager for Strands; AgentCoreMemorySaver and AgentCoreMemoryStore for LangGraph.

## Gateway and Identity

- Gateway turns APIs, Lambda functions, and existing MCP servers into one MCP endpoint with auth and semantic tool search.
- Identity manages inbound auth (who may call the agent) and outbound credentials (OAuth tokens and API keys the agent uses for third-party services).

## Built-in tools

- Browser: a managed, isolated Chromium. Start a session, then drive it with Playwright or other CDP clients over a signed WebSocket; a live view URL lets humans watch or take control.
- Code Interpreter: sandboxed Python, JavaScript, and TypeScript execution with file upload/download.

## Observability, evaluation, policy

- Observability: OpenTelemetry-compatible traces, metrics, and logs in CloudWatch (GenAI observability dashboards); AWS Distro for OpenTelemetry (ADOT) instruments agents.
- Evaluations: built-in and custom evaluators (e.g. correctness, helpfulness, tool selection accuracy) scored on agent traces, online or on demand.
- Policy: deterministic rules (Cedar) that allow or deny tool calls through the Gateway.
