# 2.angular-full

Project 1's chatbot, grown into a small but complete assistant. **FastAPI + Google ADK** backend, **Angular** frontend with a live trace panel.

Every component is present and wired, deliberately small:

| Component | Implementation | Swap for production |
|---|---|---|
| Agent loop + orchestrator | ADK `Runner`; root `LlmAgent` calling specialists via `AgentTool` | same |
| Iterative refinement | `LoopAgent` (drafter ⇄ critic, exits via `escalate`) inside a `SequentialAgent` | same |
| Local tools | `calculate`, `get_current_time` | same |
| Database tools | SQLite + mock data; `list_customers`, `get_customer_orders`, `run_sql_query` (SELECT-only) | Postgres, read-only role |
| RAG | `HashingEmbedder` + `InMemoryVectorStore` over `data/knowledge/*.md` | `GeminiEmbedder` + `ChromaVectorStore` (already written) |
| MCP | FastMCP server (`get_weather`, `lookup_ticket`, `create_ticket`) spawned over stdio | same server as its own service over HTTP (`Dockerfile.mcp`) |
| Sessions | in-memory | `DatabaseSessionService` (sqlite in compose, Postgres in prod) |
| Streaming | SSE (`/api/v1/chat/stream`) with tool events interleaved | same |
| Evals | ADK evalsets: tool trajectory + response match | LLM-judge criteria, scheduled CI |

## Quickstart

```bash
cp backend/.env.example backend/.env       # put GOOGLE_API_KEY in
docker compose -f deploy/docker-compose.yaml up --build
open http://localhost:4200
```

Ask things like:

- "How many orders does Ada have?" → `data_agent` → `get_customer_orders`
- "Total revenue from pro customers?" → `data_agent` → `describe_schema` + `run_sql_query`
- "Can I dry clean my sleeping bag?" → `knowledge_agent` → `search_knowledge_base`
- "What's the weather in Berlin?" → `knowledge_agent` → MCP `get_weather`
- "Write a short email announcing free express shipping" → `writer` → loop
- "What is 12 * 7?" → `calculate`

The trace panel under each answer shows exactly which agent called which tool with what.

## Layout

```
backend/
  app/agents/     orchestrator, data_agent, knowledge_agent, writer_pipeline, factory, agent (for adk cli)
  app/tools/      local_tools, db_tools, rag_tools, mcp_tools
  app/rag/        chunker, embedder, vector_store, retriever, factory
  app/db/         schema.sql, seed.py, database.py
  app/mcp/        server.py (FastMCP)
  app/services/   chat_service.py (Runner + event translation + streaming)
  app/api/        routes_chat (json + sse), routes_debug (rag search), routes_health
  data/knowledge/ three markdown docs
  evals/          tools/ and knowledge/ eval sets + criteria
  tests/          20 tests, no API key needed
frontend/         Angular 21; chat.service.ts parses SSE; trace panel
deploy/           compose (stdio MCP) and k8s (separate MCP service, PVC)
docs/             DESIGN.md (the why), DEPLOY.md (the how)
```

## Tests and evals

```bash
cd backend && uv sync && uv run pytest -q                 # 20 passed, no key
cd frontend && npm test                                   # 3 passed

# real-model evals
cd backend && uv sync --extra eval
GOOGLE_API_KEY=... uv run pytest -m eval -s
# or
uv run adk eval app/agents evals/tools/local_tools.evalset.json --config_file_path evals/tools/test_config.json
```

## Debugging with ADK's UI

```bash
cd backend && uv run adk web app/agents --port 8080
```

Same agent tree, with ADK's event inspector, session state viewer, and an Eval tab that can save a conversation as an eval case.

## Next

`../3.claude-sdk-full` rebuilds this with the Claude Agent SDK as the runtime.

## References

1. [google/adk-python](https://github.com/google/adk-python) and [google/adk-samples](https://github.com/google/adk-samples) (see `python/agents/` for MCP, RAG, and workflow examples)
2. [ADK docs: Multi-agent systems](https://google.github.io/adk-docs/agents/multi-agents/), [MCP tools](https://google.github.io/adk-docs/tools/mcp-tools/), [Evaluate](https://google.github.io/adk-docs/evaluate/), [Streaming](https://google.github.io/adk-docs/streaming/)
3. [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk) (FastMCP)
4. [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) (the orchestrator / evaluator-optimizer patterns used here)
