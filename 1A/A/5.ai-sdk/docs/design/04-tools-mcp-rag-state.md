# 04 · Tools, MCP, RAG, state

## Neutral tools, four wrappers

- A tool is written **once** as a typed Python function with a docstring (`app/tools/*.py`).
- Each framework turns it into its own tool type. Seeing the four wrappers side by side is part of the lesson.

| Framework | Wrapper | Schema from |
|---|---|---|
| ADK | `FunctionTool(fn)` (or just pass `fn`) | signature + docstring |
| LangGraph / LangChain | `StructuredTool.from_function(coroutine=fn)` | signature + docstring |
| Strands | `strands.tool(fn)` | signature + docstring |
| Claude Agent SDK | `@claude_agent_sdk.tool(name, desc, schema)` + `create_sdk_mcp_server` | explicit JSON schema (we derive it with Pydantic) |
| Anthropic Messages API | `beta_async_tool(fn)` | signature + docstring |

| Tool | Kind | Backend by provider |
|---|---|---|
| `calculator(expression)` | local, pure | safe AST evaluator (no `eval`) |
| `current_time(timezone)` | local, pure | `zoneinfo` |
| `search_docs(query, k)` | RAG | local / Bedrock KB / Vertex RAG Engine |
| `remember(fact)` / `recall(query)` | long-term memory | SQLite / AgentCore Memory / Memory Bank |
| `run_cli(command)` | CLI | allowlisted `subprocess`, no shell |
| `browse(url)` | Playwright | local Chromium / AgentCore Browser (CDP) |
| `run_code(code)` | sandbox | AgentCore Code Interpreter (bedrock only) |

- Tools need per-request context: who the user is, and which retriever or memory to use.
  - They read it from `RunScope`, a `ContextVar` set by `RunService`.
  - No framework's context object is threaded through. So the same function works in all four frameworks.

## CLI tool safety (`run_cli`)

- `shlex.split`, then `subprocess.run(argv, shell=False, timeout=10)` in a worker thread.
- **Allowlist by program**, each with an argument validator: `date` (never `-s`), `uname`, `whoami`, `pwd`, `echo`, `ls`, `cat`, `head`, `wc` (file arguments must resolve inside `data/corpus`), `python --version`.
- Rejected: pipes, redirects, `;`, `&&`, backticks, `$(`. These are rejected *before* splitting, so there is no shell to interpret them anyway. Defense in depth.
- Output is truncated to 4 KB.
- On top of this, LangGraph `hitl` asks a human before running it. Claude `agent_sdk` gates it in `can_use_tool`.

## Browser tool (`browse`)

- Returns `{url, title, text[:4000], links[:20]}`.
- Two backends, one code path:
  - **local**: `async_playwright().chromium.launch(executable_path=PLAYWRIGHT_CHROMIUM_PATH)`.
  - **AgentCore Browser**: `BrowserClient(region).start()` → `generate_ws_headers()` → `chromium.connect_over_cdp(ws_url, headers=...)`.
    - It is the same Playwright API on a managed, isolated browser.
    - The live-view URL is logged.
- **SSRF guard**: only `http(s)`. Hosts that resolve to private, loopback, or link-local addresses are refused. An optional allowlist is `BROWSER_ALLOWED_HOSTS`.
- **Playwright MCP** (`@playwright/mcp`) is the *external MCP* alternative: the agent drives the browser step by step (click, type, snapshot) instead of one fetch. It is enabled with `PLAYWRIGHT_MCP_ENABLED=true` (needs `npx`).

## MCP

- **Our server**: `app/mcp/server.py`, FastMCP, name `workbench`.
  - Tools: `create_ticket`, `list_tickets`, `get_ticket` (SQLite), `word_count`.
  - Transports: stdio (spawned by the agent) and streamable HTTP (`python -m app.mcp.server --http`) for remote use.
- **Each framework's MCP client**:

| Framework | Client |
|---|---|
| ADK | `McpToolset(connection_params=StdioConnectionParams(...))` |
| LangGraph | `langchain_mcp_adapters.client.MultiServerMCPClient` → LangChain tools |
| Strands | `MCPClient(lambda: stdio_client(params))`; `start()` / `stop()` on a worker thread; tools come from `list_tools_sync()` |
| Claude Agent SDK | `mcp_servers={"workbench": {"command": ..., "args": [...]}}` (CLI-managed) |
| Messages API | `mcp` `ClientSession` + `anthropic.lib.tools.mcp.async_mcp_tool` |

- **Cloud**: the same server deploys behind AgentCore Gateway or on Cloud Run. Clients switch from stdio to streamable HTTP with a URL.

## RAG

- `Retriever` protocol: `async search(query, k) -> list[Passage(source, text, score)]`.

| Impl | Index | Notes |
|---|---|---|
| `LocalRetriever` | `data/corpus/*.md`, split by heading, hashing embedder, cosine | `# ILLUSTRATION:` deterministic, no network |
| `BedrockKbRetriever` | Bedrock Knowledge Base (`bedrock-agent-runtime.retrieve`) | Ingest the corpus to S3 → KB sync (`infra/aws`) |
| `VertexRagRetriever` | Vertex RAG Engine corpus (`vertexai.rag.retrieval_query`) | `infra/gcp/setup_vertex.py` imports the corpus |

- **Native retrievers** where the framework has them:
  - LangGraph `AmazonKnowledgeBasesRetriever` (bedrock);
  - ADK `VertexAiRagRetrieval` (vertex);
  - Strands `strands_tools.retrieve` (bedrock).
- The neutral `search_docs` tool always exists, so behaviour stays comparable.

## State: three layers, kept apart on purpose

| Layer | Owner | Lifetime | Example |
|---|---|---|---|
| **Run lock + id mapping** | our `SessionRegistry` | process (PRODUCTION: Redis/DynamoDB) | "session `s1` is bound to `langgraph/hitl/bedrock` and is busy" |
| **Conversation state** (short-term) | the framework | per session | ADK `Session.events` + `state`; LangGraph checkpoint; Strands messages; Claude CLI JSONL |
| **Long-term memory** | provider memory service | per user, across sessions | AgentCore memory records; Memory Bank memories; local SQLite facts |

- Why three layers:
  - The lock and the mapping are framework-agnostic.
  - Conversation state **must** stay native. Only LangGraph can resume a LangGraph checkpoint.
  - Long-term memory is the one layer frameworks *can* share. The `recall` tool shows it: a fact remembered in an ADK session can be recalled in a Strands session for the same user.
- The session lock follows `0.learn/fastapi-bedrock-asyncSessionMemory.py`. A second concurrent request on the same session returns `409`. It never interleaves two agent loops on one history.

## Guardrails

- `Guardrail` protocol: `async check(text, source="INPUT"|"OUTPUT") -> GuardrailResult(allowed, text, reasons)`.
  - `LocalGuardrail`: regex for emails, card numbers, and AWS keys. Masks on output, blocks secrets on input.
  - `BedrockGuardrail`: `bedrock-runtime.apply_guardrail(guardrailIdentifier, guardrailVersion, source, content)`.
  - `ModelArmorGuardrail`: `modelarmor` `sanitize_user_prompt` / `sanitize_model_response`.
- **Native equivalents** shown inside frameworks:
  - ADK `before_model_callback`;
  - LangGraph `PIIMiddleware`;
  - Strands `BedrockModel(guardrail_id=...)`;
  - Claude `PreToolUse` hook (policy) and `UserPromptSubmit` hook (context).
