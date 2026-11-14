# AGENTS.md — 5.ai-sdk

Repo-wide rules are in `../AGENTS.md`. This file adds what is specific to this project.

## Shape

- One deployable: `backend/` (FastAPI + four agent frameworks).
  - No `frontend/`: a static playground (`app/static/index.html`) is served by the backend. See `docs/design/01-architecture.md`, "Why no separate frontend".
- `infra/` holds provisioning *scripts* for AWS and GCP managed agent services, not Terraform. See `docs/design/06-mvp-ladder.md`.

## Invariants (don't break these)

- **One contract.** Adapters yield `app.schemas.Event`s only. Don't add framework-specific fields to the wire. Put extras in `data`.
- **Patterns never branch on the provider.**
  - Ask the `ProviderProfile` (vendor, model id, retriever, memory, browser, sandbox, guardrail).
  - Provider-specific *framework* classes (session services, checkpointers, session managers, model classes) live in each adapter's `models.py` / `services.py` / `persistence.py` / `state.py`.
- **Neutral tools stay neutral.**
  - `app/tools/*` are plain async functions with Google-style docstrings and no default arguments.
  - They read per-run context from `current_scope()`, never from a framework context object.
- **Managed services degrade to local.** An unset cloud id must fall back to the local implementation, not fail.
- **Adapters import lazily** (`app/core/registry.py`). Don't import framework packages from `app.main`, `app.core`, or `app.services`.
- **Sensitive tools** (`app.tools.SENSITIVE`: `run_cli`, `run_code`) need a gate in every framework:
  - ADK `before_tool_callback`;
  - LangGraph `hitl` interrupt / `@wrap_tool_call`;
  - Strands `BeforeToolCallEvent.cancel_tool`;
  - Claude `can_use_tool` / `PreToolUse` hook.

## Adding things

- **A pattern**:
  - Add a builder plus a `PatternInfo` to the adapter's `patterns.py` registry, listing the components it shows.
  - Add a keyless test with scripted models (`tests/fakes/<framework>.py`).
  - Add a row to `docs/design/02-component-matrix.md`.
- **A framework**:
  - New `app/adapters/<name>/adapter.py` exposing `build(settings)`.
  - Register it in `BUILTIN_ADAPTERS`.
  - Implement translation to neutral events.
  - Add a scripted-model fake.
- **A managed service**:
  - A class behind the matching protocol (`Retriever`, `LongTermMemory`, `Browser`, `CodeSandbox`, `Guardrail`).
  - Selected in `app/providers/__init__.py` when its setting is present.
  - A stubbed-client test in `tests/test_cloud_backends.py`.

## Testing

- `uv run pytest`: keyless. Every pattern of every framework runs end to end.
  - Real agent loops, real MCP subprocesses, scripted models per agent role.
- `-m browser` tests need Chromium (`PLAYWRIGHT_CHROMIUM_PATH`). They skip otherwise.
- `-m eval`: real models. Opt-in.
- Cloud SDK clients are stubbed (`botocore.Stubber`, fake `vertexai` clients). Tests never call AWS or GCP.

## State (docs/design/07-state-and-memory.md)

- Conversation ≠ context. Persist the whole conversation; send a view (window / summary / compaction).
- A cache is never the source of truth. Caches fail open; the session lock fails closed (503).
- A new state feature goes into the suite for its branch (`diy`, `langgraph:memory`, `adk:memory`). Add to other frameworks only what is unique to them.
- State routes are generic. Adapters opt in by implementing `StateOps` methods.

## Gotchas found while building

- ADK `AgentTool` runs the inner agent in its own runner. Its tool calls do not appear in the parent event stream.
- A Strands graph node runs once per satisfied incoming edge. Make alternative paths into one node mutually exclusive.
- `AgentCoreMemoryStore` stores *messages* (`{"message": BaseMessage}` under `(actor, session)`) and searches *extracted facts* under `("facts", actor)`. It is not a key-value store.
- `langchain-mcp-adapters` 0.3 needs `mcp<2`.
- `strands-agents[anthropic]` pins `anthropic<1`. We install `anthropic` directly instead.
- Gemini rejects built-in retrieval mixed with function tools in one request. `VertexAiRagRetrieval` sits in its own agent behind `AgentTool`.
- `redis.asyncio` pools bind to the event loop that first uses them.
  - In tests, use `with TestClient(...)`: one loop per client.
  - Never cache a client across loops.
- LangGraph reports node-cache hits as a `__metadata__: {"cached": true}` entry in the `updates` chunk.
- Strands proactive compression needs the model's token estimates (a scripted model has none). `strands:memory` triggers `reduce_context` from a hook.
- ADK `rewind_async` appends a rewind event; it does not delete history. ADK has no fork, so we replay events into a new session.
- `redis-py`'s `ConnectionError` is not the builtin one. Catch `app.state.cache.CACHE_ERRORS`.
