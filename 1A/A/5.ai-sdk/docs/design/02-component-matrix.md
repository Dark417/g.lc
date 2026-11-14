# 02 · Component matrix

How to read this file:

- **Pattern** = the demo that shows the component (`POST /v1/runs {"framework", "pattern", ...}`).
- **raw / bedrock / vertex**: which native class or service fills that slot on each branch.
- `—` = a documented gap, with the reason.
- `GET /v1/catalog` returns the same data as JSON.

## Shared demo domain

- An **engineering research assistant**. It answers questions about agent frameworks and cloud agent services.
- Its RAG corpus is `backend/data/corpus/*.md`: short notes on ADK, LangGraph, Strands, the Claude Agent SDK, AgentCore, and Agent Engine.
- So "search the docs" returns real, checkable content.
- Typical prompts:
  - "What is AgentCore Memory? Cite the docs, then file a ticket to evaluate it."
  - "Compare ADK LoopAgent and LangGraph cycles."
  - "Open https://example.com and tell me its title."
  - "What is 17% of 2340?"

## Google ADK (`framework=adk`)

| Pattern | Components shown | How they work together |
|---|---|---|
| `single` | `LlmAgent`, `FunctionTool`, `McpToolset`, `PreloadMemoryTool`, `before_model_callback`, `before_tool_callback`, `BasePlugin`, `output_key` | One agent with every tool type. Callbacks guard inputs and tools. A plugin logs every model and tool call app-wide. |
| `sequential` | `SequentialAgent`, `output_key`, `{state}` templating | researcher writes `state["notes"]` → writer reads `{notes}`. State is the bus. |
| `parallel` | `ParallelAgent` inside a `SequentialAgent` | docs_researcher ∥ web_researcher write separate keys → synthesizer merges them. Fan-out/fan-in. |
| `loop` | `LoopAgent`, `max_iterations`, `exit_loop` tool (`tool_context.actions.escalate`) | writer drafts → critic approves or not. Escalate ends the loop. |
| `coordinator` | `sub_agents` (LLM-driven transfer), `AgentTool` (agent as a tool) | The coordinator transfers control to `researcher`. It calls `math_agent` as a tool and keeps control. Both delegation styles appear side by side. |
| `custom` | `BaseAgent._run_async_impl`, `ctx.session.state`, deterministic routing | Code decides which sub-agent runs (keyword → route), as in `0.learn`'s code-first orchestrator. No LLM call for routing. |
| `workflow` | ADK 2 `Workflow` graph: `FunctionNode`, agent nodes, routed `Edge`s, `START` | classify (function) → route edge → `researcher` or `calculator` agent → format (function). Explicit graph, not LLM transfer. |
| `memory` | state scopes (`user:`/`app:`/`temp:`), `ToolContext.state`, `EventsCompactionConfig`, `ResumabilityConfig`, `rewind_async`, `ContextCacheConfig`, Memory Bank | The vertex-branch state suite. See `07-state-and-memory.md`. |

| Slot | raw | bedrock | vertex |
|---|---|---|---|
| Model | `Gemini` (API key) or `AnthropicLlm` (Claude API) | `LiteLlm("bedrock/converse/<id>")` | `Gemini` on Vertex, or `Claude` (Claude on Vertex) |
| Session | `DatabaseSessionService` (SQLite) | `DatabaseSessionService` (any SQL, e.g. RDS) | `VertexAiSessionService` (Agent Engine Sessions) |
| Memory | `InMemoryMemoryService` | `AgentCoreMemoryService`: our `BaseMemoryService` over AgentCore Memory | `VertexAiMemoryBankService` (Memory Bank) |
| RAG | `search_docs` (local) | `search_docs` → Bedrock KB | `VertexAiRagRetrieval` (native) + `search_docs` → RAG Engine |
| Hosting | Docker / k8s | AgentCore Runtime (`runtimes/agentcore_app.py`) | Agent Engine `AdkApp` (`runtimes/agent_engine_app.py`) |
| Tracing | native OTel spans → OTLP | → ADOT → X-Ray | → Cloud Trace |

## LangGraph (`framework=langgraph`)

| Pattern | Components shown | How they work together |
|---|---|---|
| `react` | `create_react_agent` (prebuilt), checkpointer, `BaseStore` via `pre_model_hook` / `post_model_hook` + `get_store()`, MCP tools | Fastest path: model + tools + memory. The thread id comes from our session id. The hooks read and write long-term memory around each model call. |
| `graph` | `StateGraph`, `TypedDict` state with an `add_messages` reducer, `ToolNode`, `tools_condition`, conditional edges | retrieve (RAG node) → agent ⇄ tools loop → END. Everything the prebuilt hides, written out. |
| `middleware` | `langchain.agents.create_agent` + `PIIMiddleware`, `SummarizationMiddleware`, `ModelCallLimitMiddleware`, `ToolCallLimitMiddleware`, `ToolRetryMiddleware`, custom `@before_model`, `@wrap_tool_call`, `@dynamic_prompt` | Cross-cutting concerns as composable middleware around one agent loop. |
| `supervisor` | Subgraphs (agents as nodes), `Command(goto=…)` handoff, structured routing output | The supervisor picks `researcher` / `calculator` / `FINISH`. Each worker is its own compiled graph. |
| `map_reduce` | `Send` API, `Annotated[list, operator.add]` reducer | plan sub-questions → `Send` one branch per question in parallel → reduce into an answer. |
| `hitl` | `interrupt()`, `Command(resume=…)`, checkpointer-backed pause | Before `run_cli` executes, the graph pauses and returns an `interrupt` event. The next request with `resume: {"approve": true}` continues it. |
| `memory` | AWS checkpointers (AgentCore / DynamoDB+S3 / Valkey), `AgentCoreMemoryStore`, `RemoveMessage` compaction, `trim_messages`, `CachePolicy` + `ValkeyCache`, `RetryPolicy`, durability, `aget_state_history`, `aupdate_state` | The bedrock-branch state suite. See `07-state-and-memory.md`. |

| Slot | raw | bedrock | vertex |
|---|---|---|---|
| Model | `ChatAnthropic` or `ChatGoogleGenerativeAI` | `ChatBedrockConverse` | `ChatVertexAI` (Gemini) or `ChatAnthropicVertex` |
| Checkpointer (short-term) | `AsyncSqliteSaver` | `AgentCoreMemorySaver` (AgentCore Memory events) | `AsyncSqliteSaver`; PRODUCTION: Postgres saver on Cloud SQL, or deploy via the Agent Engine `LanggraphAgent` template |
| Store (long-term) | `InMemoryStore` | `AgentCoreMemoryStore` | `InMemoryStore` + `recall` tool → Memory Bank |
| RAG | `search_docs` (local) | `AmazonKnowledgeBasesRetriever` (native) | `search_docs` → RAG Engine |
| Tracing | OpenInference LangChain instrumentor → OTel | same | same |

- **Gap — vertex checkpointer**:
  - No first-party GCP LangGraph checkpointer ships in `langchain-google-*`.
  - The managed path is Agent Engine, which hosts the graph and its checkpointer (Cloud SQL or AlloyDB).

## Strands (`framework=strands`)

| Pattern | Components shown | How they work together |
|---|---|---|
| `single` | `Agent`, `@tool`, `MCPClient`, `HookProvider` (Before/AfterToolCall, BeforeModelCall), `SlidingWindowConversationManager`, session manager, `strands_tools` AgentCore Browser / Code Interpreter (bedrock) | Model-driven loop. Hooks audit and guard tools. The conversation manager trims context. The session manager persists it. |
| `agents_as_tools` | Specialist `Agent`s wrapped in `@tool` functions | An orchestrator calls `research_assistant` / `math_assistant` like any tool. |
| `swarm` | `Swarm`, `handoff_to_agent` (auto-injected), `max_handoffs` | researcher → writer → reviewer hand off to each other autonomously, with shared context. |
| `graph` | `GraphBuilder`, `add_node`, `add_edge(condition=…)`, entry point | A deterministic DAG: research → calculate (only if the task has arithmetic) → report. |
| `structured` | `structured_output_model=<Pydantic>` | Returns a typed `ResearchBrief`, which `done.output` carries as JSON. |
| `memory` | `agent.state`, `SummarizingConversationManager`, `reduce_context` hook, `S3SessionManager` | Only the Strands-specific state features. See `07-state-and-memory.md`. |

| Slot | raw | bedrock | vertex |
|---|---|---|---|
| Model | `AnthropicModel` or `GeminiModel` | `BedrockModel` (Converse, optional `guardrail_id`) | `GeminiModel(client=genai.Client(vertexai=True))` |
| Session | `FileSessionManager` | `AgentCoreMemorySessionManager` (short- and long-term) | `FileSessionManager`; PRODUCTION: `RepositorySessionManager` over Firestore/GCS |
| Native cloud tools | — | `strands_tools.browser` (AgentCore Browser), `code_interpreter` (AgentCore), `retrieve` (Bedrock KB) | — |
| Tracing | native OTel (`StrandsTelemetry` optional) | same | same |

- **Gap — vertex session**:
  - Strands ships File, S3, and AgentCore session managers.
  - For GCP you implement `SessionRepository` (about 10 methods). We note it and do not build it.

## Claude (`framework=claude`)

| Pattern | Components shown | How they work together |
|---|---|---|
| `agent_sdk` | `ClaudeSDKClient`, `create_sdk_mcp_server` + `@tool` (in-process MCP), `HookMatcher` (`PreToolUse` deny, `PostToolUse` audit, `UserPromptSubmit`), `can_use_tool`, `allowed_tools`, `resume` | The Claude Code agent loop runs our neutral tools in-process. Hooks and permission callbacks decide what runs. |
| `subagents` | `AgentDefinition` (researcher, reviewer), delegation through the `Task` tool, per-agent tool scoping | The main agent delegates. Each subagent has its own prompt, tools, and model. |
| `external_mcp` | stdio MCP servers: our `workbench` server + `@playwright/mcp` (optional) | The same MCP servers the other frameworks use, attached by config. Tool names are `mcp__<server>__<tool>`. |
| `messages_api` | `client.beta.messages.tool_runner` + `@beta_async_tool`, history kept by us | The bare API agent loop. The provider swaps the **client class**, not env vars. |

| Slot | raw | bedrock | vertex |
|---|---|---|---|
| Agent SDK model | `ANTHROPIC_API_KEY` | `CLAUDE_CODE_USE_BEDROCK=1` + AWS credentials | `CLAUDE_CODE_USE_VERTEX=1` + `CLOUD_ML_REGION` + `ANTHROPIC_VERTEX_PROJECT_ID` |
| Messages API client | `AsyncAnthropic` | `AsyncAnthropicBedrockMantle` (`anthropic.`-prefixed ids) | `AsyncAnthropicVertex` |
| Session | CLI JSONL session, resumed by id (`resume=`) | same (local to the container) | same |
| Memory | `remember` / `recall` tools → local | → AgentCore Memory | → Memory Bank |
| Tracing | `CLAUDE_CODE_ENABLE_TELEMETRY=1` + `OTEL_*` passed in `env` (the CLI exports its own OTLP) | same | same |

- **Gap — managed sessions**:
  - The Agent SDK keeps sessions on the local disk of the CLI.
  - Running more than one replica needs sticky routing, or copying `~/.claude/projects/...` to shared storage.

## No framework (`framework=diy`)

| Pattern | Components shown | How they work together |
|---|---|---|
| `loop` | hand-written state machine, checkpoint per step (SQLite + Redis write-through), recovery, fork, context strategies (`window` / `token_budget` / `summary` / `server`), long-term extraction + consolidation, Redis LLM cache, prompt caching | The raw-branch state suite: everything the frameworks do, written out. Runs on Claude via any branch's client. See `07-state-and-memory.md`. |

## Cross-cutting components (all frameworks)

| Component | Where | raw | bedrock | vertex |
|---|---|---|---|---|
| Session lock + registry | `core/sessions.py` | in-process; with `REDIS_URL` a leased Redis lock | ElastiCache (Valkey/Redis) via `REDIS_URL` | Memorystore via `REDIS_URL` |
| Long-term memory tools | `tools/memory_tools.py` | SQLite keyword store | AgentCore Memory (`create_event` / `retrieve_memories`) | Agent Engine Memory Bank |
| RAG tool `search_docs` | `rag/` | hashing-vector store over the corpus | Bedrock KB `Retrieve` | Vertex RAG Engine `retrieval_query` |
| Browser tool `browse` | `tools/browser.py` | local Playwright Chromium | AgentCore Browser over CDP (Playwright `connect_over_cdp`) | local Playwright |
| Code tool `run_code` | `tools/code.py` | disabled (no sandbox) | AgentCore Code Interpreter | disabled — see `03-cloud-branches.md` |
| CLI tool `run_cli` | `tools/cli.py` | allowlisted `subprocess` (no shell) | same | same |
| MCP server | `mcp/server.py` | stdio | same; PRODUCTION: AgentCore Gateway (MCP over HTTP) | same; PRODUCTION: Cloud Run (streamable HTTP) |
| Guardrails | `guardrails/` | regex PII and secrets | Bedrock `ApplyGuardrail` | Model Armor `sanitize_user_prompt` |
| Tracing | `telemetry.py` | OTLP → collector → Jaeger | OTLP → ADOT → X-Ray | Cloud Trace exporter |
| Evals | `evals/` | harness (trajectory, contains, judge) | + AgentCore Evaluations (documented) | + Vertex Gen AI eval `EvalTask` |
