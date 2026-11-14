# Strands Agents

Strands Agents is an open-source SDK from AWS for model-driven agents: the model plans and calls tools in a loop, with little scaffolding.

## Core

- Agent(model=..., tools=[...], system_prompt=...) runs the agent loop. Calling agent("question") returns an AgentResult; invoke_async and stream_async are the async forms.
- Model providers: BedrockModel (default; Converse API), AnthropicModel, GeminiModel, OpenAIModel, LiteLLMModel, Ollama, and others.
- Tools: the @tool decorator turns a function into a tool from its signature and docstring. strands-agents-tools ships ready tools such as calculator, current_time, http_request, shell, retrieve (Bedrock Knowledge Bases), browser and code_interpreter (AgentCore), and use_aws.
- MCP: MCPClient wraps an MCP transport (stdio, SSE, streamable HTTP); its tools are passed to the agent like any others.
- Structured output: pass a Pydantic model (structured_output_model) to get a validated object back.

## Multi-agent patterns

- Agents as tools: wrap a specialist Agent in a @tool function; an orchestrator agent calls it.
- Swarm: a team of agents that hand off to each other autonomously with a handoff_to_agent tool and shared context, bounded by max_handoffs and timeouts.
- Graph: GraphBuilder builds a deterministic DAG of agents (or nested swarms/graphs) with conditional edges; outputs of dependencies flow into each node.
- Workflow: a task-dependency workflow tool for parallel task execution.

## State

- Conversation managers keep context in budget: SlidingWindowConversationManager (drop oldest), SummarizingConversationManager, or NullConversationManager.
- Session managers persist agent state and messages: FileSessionManager, S3SessionManager, and AgentCoreMemorySessionManager (from the bedrock-agentcore package) for short- and long-term memory.
- agent.state is a key-value store that is persisted with the session but not sent to the model.

## Hooks and observability

- HookProvider registers callbacks on typed events: BeforeInvocationEvent, BeforeModelCallEvent, BeforeToolCallEvent, AfterToolCallEvent, MessageAddedEvent, and more. Hooks can modify or cancel tool calls.
- Strands emits OpenTelemetry traces and metrics with GenAI semantic conventions; StrandsTelemetry sets up OTLP or console exporters.
- Deployment: AWS Lambda, Fargate, EKS, or Bedrock AgentCore Runtime.
