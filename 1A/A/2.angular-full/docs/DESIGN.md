# Design: 2.angular-full

## Problem

Project 1 is a chat window in front of a model. Real assistants need to *do* things: look up data, read documents, call external systems, iterate on their own output, and be measured. This project adds every one of those components in its smallest honest form and shows how they wire together.

## Who it's for

Me. The goal is to see each component's seam, not to ship a product.

## Success metric

- Every component (local tools, SQLite tools, RAG, MCP, orchestrator, loop, streaming, evals) is exercised by a test that runs without an API key.
- With a key: `docker compose up`, ask "How many orders does Ada have and what's your return window?", and watch the trace panel show `data_agent` and `knowledge_agent` both being called.
- `pytest -m eval` produces a pass/fail number.

## Non-goals

- Production RAG quality (hashing embedder is lexical only).
- Auth, multi-tenancy, rate limits.
- A durable MCP server (its tickets live in memory).

## The system

```
Angular ──POST /api/v1/chat[/stream]──▶ FastAPI ──▶ AdkChatService ──▶ Runner
                                                                         │
      ┌──────────────────────────── orchestrator (LlmAgent) ◀────────────┘
      │  tools: calculate, get_current_time
      │  AgentTool ─▶ data_agent ──────▶ describe_schema / list_customers / get_customer_orders / run_sql_query ──▶ SQLite
      │  AgentTool ─▶ knowledge_agent ─▶ search_knowledge_base ──▶ Retriever(embedder, vector store) ◀── data/knowledge/*.md
      │                               └▶ McpToolset ──stdio/http──▶ app/mcp/server.py (get_weather, lookup_ticket, create_ticket)
      │  AgentTool ─▶ writer (Sequential) ─▶ revision_loop (Loop: drafter ⇄ critic, exit via approve_draft) ─▶ finalizer
      ▼
   Events ──translate_event()──▶ tool_call / tool_result / agent_text / delta / final_text ──▶ JSON or SSE
```

## Component by component

| Component | Where | Illustration choice | Production swap |
|---|---|---|---|
| Agent loop | ADK `Runner` (in `services/chat_service.py`) | n/a: this *is* the loop (model → tool → model …) | same |
| Orchestrator | `agents/orchestrator.py` | `AgentTool` per specialist; parent keeps control | `sub_agents` transfer for persona routing; A2A for remote agents |
| Iteration | `agents/writer_pipeline.py` | `LoopAgent` + `escalate` from a tool, wrapped in `SequentialAgent` | same; add `output_schema` on the critic for structured verdicts |
| Local tools | `tools/local_tools.py` | plain functions; AST-walked calculator | same |
| DB tools | `tools/db_tools.py` + `db/` | stdlib sqlite3, seeded mock data, SELECT-only guard + `query_only` pragma | Postgres, read-only role, statement timeout |
| RAG | `rag/` | `HashingEmbedder` + `InMemoryVectorStore`, re-indexed at startup | `GeminiEmbedder` (real) + `ChromaVectorStore` (real, optional dep); separate ingest job |
| MCP | `mcp/server.py`, `tools/mcp_tools.py` | FastMCP server spawned over stdio by the backend | same server as its own Deployment over streamable-http (`Dockerfile.mcp`, k8s `25-mcp-server.yaml`) |
| Sessions | `main.py::_session_service` | in-memory | `DatabaseSessionService` (sqlite in compose; Postgres URL in prod) |
| Streaming | `chat_service.py::stream` + `routes_chat.py` | ADK `StreamingMode.SSE` → Server-Sent Events | same; consider WebSocket/BIDI for voice |
| Trace | `schemas.py::TraceEvent` | every function call/response shown in the UI | ship the same events to OpenTelemetry (ADK has built-in tracing) |
| Evals | `evals/`, `tests/test_evals.py` | ADK evalsets: trajectory match + ROUGE | LLM-judge criteria, scheduled CI, persisted results |

## Key decisions

- **AgentTool over sub_agents.** With `AgentTool` the orchestrator receives the specialist's answer as a tool result and can combine several. With `sub_agents` the conversation is handed off. For a "front door" assistant, combining wins.
- **Factories, not globals.** `build_db_tools(db_path)`, `build_rag_tool(retriever)`, `build_root_agent(settings, ...)`. Tests inject temp paths and fakes; `app/agents/agent.py` builds the same tree for `adk web`/`adk eval`.
- **One wire format for JSON and SSE.** `translate_event` is a pure function tested in isolation; both endpoints consume it. The frontend has one `TraceEvent` type.
- **Root-only text is the reply.** Specialists' prose becomes `agent_text` trace events, so the user sees only the orchestrator's answer and the trace shows the reasoning.
- **Evals split by folder.** Trajectory matching is exact on name+args, so it only fits tools with deterministic args (calculator). Free-form tools (search queries) are judged on response text only.

## Build-vs-buy

| Choice | Why |
|---|---|
| ADK `McpToolset` vs hand-rolled MCP client | It handles session lifecycle, tool schema conversion, filtering. Hand-rolling teaches nothing useful. |
| FastMCP vs raw MCP server API | Decorator API is what every MCP tutorial uses; same wire protocol. |
| Own RAG code vs LangChain/LlamaIndex | Three small classes make the seams visible. Adopt a framework when you need loaders, rerankers, hybrid search. |
| ADK evals vs custom harness | Free trajectory + response metrics and `adk web` case authoring. Project 3 hand-rolls a harness so you see what's inside. |

## MVP ladder (how this was built)

1. MVP0: project 1 backend + trace events in the JSON reply.
2. MVP1: local tools + SQLite tools + `data_agent`.
3. MVP2: RAG + `knowledge_agent`; debug endpoint.
4. MVP3: MCP server + toolset on `knowledge_agent`.
5. MVP4: orchestrator with `AgentTool`s; writer loop.
6. MVP5: SSE streaming + Angular trace panel.
7. MVP6: eval sets + config + pytest marker.

## Failure modes to know

- MCP over stdio: the child process is spawned by the backend at first use and killed on shutdown (`toolset.close()`). If the backend crashes hard, orphaned children are possible; the HTTP shape avoids this.
- `run_sql_query` guard is a regex plus `PRAGMA query_only`. Good for a demo. In production give the agent a DB role that physically cannot write.
- Hashing embeddings will miss synonyms ("refund" vs "money back"). That is the point of the swap.
- SSE through proxies: nginx and the Ingress must disable buffering (both configured).
- LoopAgent with `max_iterations=3` and a critic that never approves costs 6 model calls plus the finalizer. Budget it.
