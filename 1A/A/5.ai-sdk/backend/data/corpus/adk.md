# Google Agent Development Kit (ADK)

ADK is Google's open-source, code-first framework for building agents in Python (also Java, Go, TypeScript). It is model-agnostic but optimised for Gemini and Vertex AI.

## Agent types

- LlmAgent (alias Agent): an LLM with instructions, tools, and optional sub_agents. Its output can be saved to session state with output_key.
- Workflow agents run sub-agents in a fixed order without an LLM deciding:
  - SequentialAgent runs sub-agents one after another, sharing session state.
  - ParallelAgent runs sub-agents concurrently on branches of the same invocation; each should write a different state key.
  - LoopAgent repeats its sub-agents until max_iterations or until an agent escalates (tool_context.actions.escalate = True, e.g. via the built-in exit_loop tool).
- Custom agents subclass BaseAgent and implement _run_async_impl to orchestrate sub-agents with arbitrary Python logic.
- ADK 2 adds a graph Workflow API (google.adk.workflow): nodes (functions, agents, tools) connected by edges with optional routes, with retries, timeouts, joins, and resumability.

## Multi-agent delegation

- Transfer: an LlmAgent with sub_agents can hand control to a sub-agent (the model calls transfer_to_agent). The sub-agent then answers the user directly.
- AgentTool: wraps an agent so another agent calls it like a function and keeps control of the conversation.

## Tools

- FunctionTool wraps a Python function; the signature and docstring become the schema.
- McpToolset connects to an MCP server (stdio, SSE, or streamable HTTP) and exposes its tools.
- Built-ins include google_search, load_memory, preload_memory, VertexAiSearchTool, VertexAiRagRetrieval, and code executors.

## Sessions, state, and memory

- A Runner executes an agent with a SessionService (InMemory, Database via SQLAlchemy, or VertexAiSessionService on Agent Engine).
- Session state keys can be scoped: no prefix (session), user: (all sessions of a user), app: (all users), temp: (one invocation).
- A MemoryService stores knowledge across sessions: InMemoryMemoryService, VertexAiMemoryBankService (Agent Engine Memory Bank), or VertexAiRagMemoryService.
- Custom backends implement BaseSessionService or BaseMemoryService (add_session_to_memory, search_memory).

## Callbacks and plugins

- Agent callbacks: before/after_agent, before/after_model, before/after_tool. Returning a value from a before_* callback short-circuits the step (e.g. block a tool call).
- Plugins (BasePlugin) register the same hooks once on the Runner/App and apply to every agent, for logging, policy, or caching.

## Deployment and evaluation

- Deploy targets: Vertex AI Agent Engine (AdkApp), Cloud Run, or GKE. `adk web` provides a developer UI.
- AgentEvaluator scores eval sets (.evalset.json) on tool trajectory and response match; `adk eval` runs them from the CLI.
- ADK emits OpenTelemetry spans (invoke_agent, call_llm, execute_tool) to the global tracer provider.
