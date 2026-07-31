# 03 — Frameworks at Each Layer

For every component in `01`, there's a stack of frameworks. This doc maps
them so you know *what to reach for* — not so you adopt them all. The
single biggest mistake is gluing together five frameworks when one would
do.

> Rule of thumb: start with the **provider SDK** (Anthropic, OpenAI) +
> your own loop. Reach for a framework when you feel the same pain it
> solves twice.

---

## Orchestration / Agent runtime

| Framework | Shape | Strength | Watch out |
|---|---|---|---|
| **LangChain** | components + chains | huge ecosystem, every integration | heavy abstractions, churny APIs |
| **LangGraph** | stateful graphs | best for explicit workflows + agents, checkpointing | learning curve |
| **LlamaIndex** | data-centric | excellent for RAG / docs | less for general agents |
| **Haystack** | pipelines | production-y, mature | smaller community |
| **AutoGen** (Microsoft) | multi-agent | conversation between agents | can be chatty/expensive |
| **CrewAI** | role-based crews | very ergonomic for "team of agents" | opinionated |
| **OpenAI Agents SDK** / Swarm | handoffs | minimal, official | OpenAI-centric |
| **Anthropic Agent SDK** | claude-native agents + skills | tight Claude integration, Claude Code parity | Anthropic-centric |
| **Pydantic AI** | typed agents | strict types, FastAPI vibes | newer |
| **DSPy** | compile prompts | optimizes prompts/programs from examples | mental model is unusual |
| **Mastra**, **Inngest Agent Kit** | TS-first | nice DX for Node shops | newer |
| **Semantic Kernel** (Microsoft) | planners + plugins | enterprise / .NET friendly | heavier |
| **Letta** (ex-MemGPT) | memory-first agents | tiered memory baked in | niche |

**Default picks**: LangGraph (Python, complex workflow), Anthropic or
OpenAI SDK directly (simple), CrewAI/AutoGen (multi-agent), LlamaIndex
(doc-heavy RAG).

---

## Vector stores

| Tier | Options |
|---|---|
| **Managed** | Pinecone, Weaviate Cloud, Qdrant Cloud, Turbopuffer, MongoDB Atlas Vector, Vertex AI Vector Search |
| **Self-host** | Qdrant, Weaviate, Milvus, Vespa, OpenSearch (k-NN), Elasticsearch |
| **Postgres-native** | pgvector, ParadeDB, Supabase Vector |
| **Embedded / local** | Chroma, LanceDB, FAISS, sqlite-vec, DuckDB VSS |

If you already have Postgres, **start with pgvector**. Move when you
outgrow it (filtering at scale, billions of vectors).

---

## Embeddings

| Provider | Notes |
|---|---|
| OpenAI `text-embedding-3-small/large` | strong default, cheap |
| Voyage AI | top quality, especially `voyage-3` series; reranker too |
| Cohere `embed-v3` | multilingual, has reranker |
| Google `text-embedding-004` | solid, integrates w/ Vertex |
| Nomic `nomic-embed-text` | open weights, runnable locally |
| BGE / E5 / GTE | open, strong; M3 is multilingual |
| Jina embeddings | long-context variants |

For code: Voyage `voyage-code`, OpenAI embeddings, or `bge-code`.

---

## Rerankers (the cheap quality win)

Cohere Rerank, Voyage Rerank, BGE reranker, Jina reranker, ColBERT.
Always try one before you change anything else in your RAG pipeline.

---

## Document loading & chunking

LangChain loaders, LlamaIndex readers, Unstructured.io (PDF/HTML/Office),
Docling (IBM), Firecrawl / Jina Reader (web), Apache Tika.

Chunkers: recursive character (default), token-aware, semantic
(embeddings-based), structure-aware (headings, AST for code).

---

## Memory

Mem0, Letta (MemGPT), Zep, Cognee, MotorheadMemory, LangMem,
plain Postgres+pgvector with your own schema.

---

## Tools / MCP

- **Tool catalogs**: Composio, Arcade.dev, Toolhouse — give an agent
  hundreds of pre-built integrations.
- **MCP servers**: official servers (filesystem, git, github, slack,
  postgres, puppeteer, …) + a growing third-party ecosystem. See `07`.
- **Code sandboxes**: E2B, Modal, Daytona, Riza, Pyodide (browser).
- **Browser**: Playwright, Browserbase, Stagehand, Anthropic
  computer-use, Browser Use.

---

## Guardrails

NeMo Guardrails (NVIDIA), Guardrails AI, LlamaGuard / PromptGuard
(Meta), Lakera, Protect AI, OpenAI moderation, Anthropic constitutional
+ moderation tools.

---

## Observability / Tracing

LangSmith, Langfuse (OSS), Arize Phoenix (OSS), Helicone, Weights &
Biases Traces, Datadog LLM Observability, OpenTelemetry GenAI
conventions, OpenLLMetry.

Pick early. Debugging agents without traces is misery.

---

## Evals

Braintrust, Promptfoo, DeepEval, Ragas (RAG-specific), TruLens,
Inspect AI (UK AISI), Patronus, OpenAI Evals.

---

## Inference / Serving (if hosting your own model)

vLLM, TGI (HuggingFace), TensorRT-LLM, SGLang, LMDeploy, Ollama (local),
llama.cpp, MLX (Apple), Together / Fireworks / Groq / Cerebras /
DeepInfra (managed open-weight).

---

## Async / Durable execution

Temporal, Inngest, Trigger.dev, Restate, Hatchet, DBOS, Cloudflare
Workflows, AWS Step Functions, plain Celery / BullMQ.

---

## Quick "good defaults" stack

For a typical SaaS that needs an AI feature, in 2026:

```
LLM:           Claude Sonnet 4.6 (or Haiku for cheap paths)
Orchestrator:  Anthropic SDK or LangGraph
Embeddings:    Voyage or OpenAI text-embedding-3-large
Vector DB:     pgvector  (Postgres you already run)
Reranker:      Cohere or Voyage
Tools:         MCP servers + a few native tools
Guardrails:    schema validation + LlamaGuard for content
Tracing:       Langfuse or LangSmith
Evals:         Braintrust or Promptfoo
Async:         Inngest or Temporal (only if tasks > 30s)
```

Next: how to **combine** components from 1 up to 8+. → `04-architecture-combinations.md`
