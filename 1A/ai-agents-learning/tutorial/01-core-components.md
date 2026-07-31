# 01 — Core Components of an AI-Agent Service

Before architecture, learn the **parts list**. Every agent service is some
subset of the components below. A toy demo uses 2–3; a production system
uses 8–12. Knowing the parts lets you reason about which to add when.

We group them into four layers: **Brain**, **Memory**, **Action**, **Ops**.

---

## Layer 1 — Brain (decides what to do)

### 1. LLM / Model
The reasoning engine. Frontier models (Claude, GPT, Gemini), open-weight
(Llama, Qwen, DeepSeek), or specialist (small task-tuned models).
- *Knobs:* temperature, max tokens, JSON / structured output, tool-use mode,
  reasoning / thinking budget, vision, streaming.

### 2. Controller / Orchestrator
The loop that drives the model. Sometimes called the "agent runtime."
Responsibilities:
- Build the prompt (system + history + retrieved context + tool results).
- Call the model.
- Parse the response (text vs tool calls).
- Execute tool calls and feed results back.
- Decide when to stop.

This is the analog of the "Claude Code harness" or the LangChain
`AgentExecutor` — it's the thing *around* the model.

### 3. Prompt / Instruction Layer
System prompt, role definitions, few-shot examples, output schemas. Often
stored as templates with variable interpolation. May be versioned, A/B-tested,
or hot-reloadable.

### 4. Planner (optional, higher-order)
For complex tasks: a component that produces a multi-step plan before
execution. Can be the same LLM in "planning mode" or a dedicated planner
model. Examples: ReAct's plan-act loop, Plan-and-Execute, Tree-of-Thoughts.

---

## Layer 2 — Memory (knows things)

### 5. Short-term context / Conversation state
The current chat history kept in the model's context window. Plus
summarization / compaction when it overflows.

### 6. Long-term memory store
Persists facts across sessions: user preferences, prior conversations,
extracted entities. Implementation ranges from a key-value store to a
"memory" microservice (e.g. Mem0, Letta/MemGPT).

### 7. Vector database / Semantic index
Stores embeddings for similarity search. Examples: Pinecone, Weaviate,
Qdrant, Milvus, pgvector, Chroma, LanceDB, FAISS (local). Pick on:
managed-vs-self-host, hybrid (BM25+vector) support, filtering, scale.

### 8. Embedding model
Turns text (or images, code) into vectors. OpenAI `text-embedding-3-*`,
Cohere, Voyage, Nomic, BGE, E5. Often a different vendor than the LLM.

### 9. Document store / Knowledge base
The *source of truth* the vector index points to: object storage (S3),
docs DB (Postgres, Mongo), CMS, wiki, code repo. Vectors are an index
*over* this — keep the originals so you can re-embed when the model changes.

### 10. RAG pipeline
Glues 7+8+9 together: chunking, embedding, retrieval, reranking,
context-window packing. Variants: naive RAG, hybrid (vector+keyword),
reranked (Cohere/Voyage reranker), HyDE, GraphRAG, agentic RAG (retrieval
as a tool the agent calls).

---

## Layer 3 — Action (does things)

### 11. Tools / Function calling
Named functions the model can invoke: `search_web`, `read_file`,
`send_email`, `run_sql`, `create_ticket`. Each tool has a JSON schema for
arguments and a handler that executes it.

### 12. MCP (Model Context Protocol) servers
A *standard* for exposing tools, resources, and prompts to any agent
client. Instead of hard-wiring a tool into your app, you run an MCP
server (stdio or HTTP) and the agent connects to it. Lets you swap
backends without code changes. See `07-mcp-and-config.md`.

### 13. Code interpreter / Sandbox
A controlled execution environment so the agent can run code, shell, or
SQL safely. E.g. E2B, Modal sandboxes, Docker, Firecracker microVMs,
Pyodide for browser.

### 14. Browser / Computer-use
Headless browser or full OS control (Playwright, Browserbase, Anthropic
computer-use, OpenAI Operator). Most powerful tool, biggest blast radius.

### 15. External APIs & connectors
Slack, GitHub, Stripe, Jira, Gmail, internal services. Wrapped as tools
or exposed via MCP.

---

## Layer 4 — Ops (keeps it running and safe)

### 16. Guardrails / Policy
Input/output filters, jailbreak detection, PII redaction, content
moderation, schema validation, rate limits per user/tool. Examples:
NeMo Guardrails, Guardrails AI, Llama Guard, OpenAI moderation.

### 17. Observability & tracing
Per-run traces of every model call, tool call, retrieval. Examples:
LangSmith, Langfuse, Arize Phoenix, Helicone, Weights & Biases Traces,
OpenTelemetry GenAI semantic conventions.

### 18. Evaluation
Offline and online evals: golden datasets, LLM-as-judge, A/B tests,
regression tests on prompt changes. Tools: Braintrust, Promptfoo,
DeepEval, Ragas (for RAG).

### 19. Caching
Prompt-prefix cache (provider-side, e.g. Anthropic prompt caching),
semantic cache (cache by embedding similarity), tool-result cache.

### 20. Cost / Rate control
Token budgets per session, model-tier routing (cheap model first,
escalate on uncertainty), concurrency caps.

### 21. Auth / Multi-tenancy
Per-user identity, scoped credentials passed into tools, data isolation
in the vector store (namespace/tenant filtering).

### 22. Queue / Async runtime
For long-running agents: task queue (Temporal, Inngest, BullMQ, Celery),
durable execution, retries, checkpointing.

---

## Priority: core → nice-to-have

A *minimum viable agent* is just three things:

> **LLM + Controller + Tools**

Add the rest as the problem demands. Here's a rough order of when you
typically need each:

| Tier | Add when… | Components |
|---|---|---|
| **Core (must)** | always | LLM, Controller, Prompt, Tools |
| **Memory (most apps)** | the agent answers questions about *your* data | Embedding, Vector DB, Doc store, RAG |
| **Stability (any real users)** | someone besides you uses it | Guardrails, Observability, Caching |
| **Scale** | >1 concurrent user or long tasks | Queue/Async, Rate control, Multi-tenancy |
| **Quality** | you ship updates and don't want regressions | Eval harness, Tracing-based debugging |
| **Power** | the agent needs to act on the world | Code sandbox, Browser, MCP connectors |
| **Sophistication** | single-shot prompts plateau | Planner, Long-term memory, Reranker, Hybrid retrieval |

Next: how these compose into **agent paradigms** → `02-agent-paradigms.md`.
