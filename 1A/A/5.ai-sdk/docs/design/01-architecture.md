# 01 · Architecture

## One entrance, many runtimes

```
                         ┌──────────────────────────── FastAPI (app.main:app) ─────────────────────────────┐
 client ── POST /v1/runs │ RunService                                                                      │
 (curl, playground,      │  1. resolve target   (framework, pattern, provider)  ── AdapterRegistry         │
  evals, MCP clients)    │  2. session lock     per session_id, 409 if busy      ── SessionRegistry         │
                         │  3. guardrail(in)    local regex │ Bedrock Guardrails │ Model Armor              │
                         │  4. RunScope         contextvar: user, session, retriever, memory, browser, ...  │
                         │  5. adapter.run() ─────────────────────────────────────┐                         │
                         │  6. guardrail(out), persist turn, close span           │                         │
                         └────────────────────────────────────────────────────────┼─────────────────────────┘
                                                                                  ▼
             ┌───────────────┬──────────────────┬─────────────────┬────────────────────────────────┐
             │ AdkAdapter    │ LangGraphAdapter │ StrandsAdapter  │ ClaudeAdapter                  │
             │ 7 patterns    │ 6 patterns       │ 5 patterns      │ 4 patterns                     │
             └──────┬────────┴────────┬─────────┴───────┬─────────┴──────────────┬─────────────────┘
                    │ each adapter asks the ProviderProfile for its native pieces │
                    ▼                                                             ▼
   ProviderProfile(raw | bedrock | vertex)
     model factory per framework · session/checkpoint backend · memory · RAG retriever · browser · code sandbox · guardrail
                    │
                    ▼
   Neutral toolkit (app/tools): calculator, current_time, search_docs, remember, recall, run_cli, browse, run_code
   MCP: own "workbench" server (stdio) · external Playwright MCP (npx, optional)
```

## Key decisions

| Decision | Choice | Why | Tradeoff |
|---|---|---|---|
| Entrance | One `POST /v1/runs` (+ `/stream` SSE) | Clients and evals never care which framework ran | Framework-specific features (e.g. LangGraph resume) need a generic `resume` field |
| Adapter boundary | `AgentAdapter` protocol yielding neutral `Event`s | Same as project 4's SSE contract; one UI and one eval for all | Each adapter owns a translation layer from its native events |
| Provider injection | `ProviderProfile` object, resolved once per request | Patterns stay provider-agnostic | Profile grows one method per capability |
| Tool sharing | Plain typed Python functions + per-framework wrappers | Shows how each framework turns a function into a tool | Framework-only tools (e.g. ADK `exit_loop`) live in the adapter |
| Per-run context for tools | `contextvars.ContextVar[RunScope]` | Works in all four frameworks without threading their context objects through | Must be set before the framework spawns tasks (it is) |
| Session lock | In-process `asyncio.Lock` per session, 409 on contention | The pattern from `0.learn/fastapi-bedrock-asyncSessionMemory.py` | ILLUSTRATION: one replica only. PRODUCTION: Redis `SET NX PX` or DynamoDB conditional write |
| Framework-native state | Each adapter keeps its own (ADK SessionService, LangGraph checkpointer, Strands SessionManager, Claude CLI session) | That *is* the lesson | Our `SessionRegistry` only maps ids and holds the lock |

## Adapter contract

```python
class AgentAdapter(Protocol):
    name: str                                   # "adk" | "langgraph" | "strands" | "claude"
    def patterns(self) -> list[PatternInfo]: ...  # name, description, components shown
    def providers(self) -> list[str]: ...         # which branches it supports
    def run(self, ctx: RunContext) -> AsyncIterator[Event]: ...
```

- `RunContext` carries:
  - the request: `message`, `user_id`, `session_id`, `pattern`, `resume`, `options`;
  - the `ProviderProfile`;
  - the `SessionRecord` (our id ↔ native ids);
  - `settings`.
- Adapters are **lazy-imported**. Importing `app.main` does not import all four frameworks. Startup stays fast, and a missing optional dependency only disables one adapter.

## Event model (wire contract)

| `type` | Fields | Emitted when |
|---|---|---|
| `session` | `session_id`, `framework`, `pattern`, `provider` | First event of every run |
| `agent` | `agent` | Control moves to a named agent or node (transfer, handoff, graph node) |
| `tool_call` | `agent`, `name`, `args`, `id` | A model asks for a tool (local, MCP, or built-in) |
| `tool_result` | `name`, `result`, `id` | The tool returned |
| `delta` | `text`, `agent` | Streaming text chunk |
| `message` | `text`, `agent` | A complete assistant message from one agent |
| `state` | `data` | Framework state worth showing (ADK `state_delta`, LangGraph channel update) |
| `interrupt` | `data` | The run paused for a human (LangGraph `interrupt`) |
| `done` | `output`, `usage` | Final answer |
| `error` | `message` | Anything failed; the run ends |

- `POST /v1/runs` collects the events and returns `{session_id, output, events}`.
- `POST /v1/runs/stream` sends the same events as SSE `data:` lines.

## Request flow (one turn)

1. `RunService.run(req)` validates the target against the registry.
   - Unknown framework or pattern → 404.
   - Provider not configured → 400, with the missing env vars named.
2. `SessionRegistry.acquire(session_id)` creates the session if new and takes the lock.
   - A session is **bound** to `(framework, pattern, provider)` at creation.
   - Re-using it with a different target → 409. A LangGraph checkpoint cannot be resumed by Strands.
3. Input guardrail. A block → `error` event, no model call.
4. A span named `agent.run` opens, with attributes `gen_ai.system`, `agent.framework`, `agent.pattern`, `agent.provider`, `session.id`.
5. `RunScope` is set in a contextvar. Tools read the retriever, memory, and browser for this provider from it.
6. The adapter streams native events and translates them to neutral `Event`s.
7. Output guardrail on the final text. On a block, the final text is replaced and an `error` event is added.
8. Lock released in `finally`, always.

## Code layout

```
5.ai-sdk/
  backend/
    app/
      main.py                 FastAPI app factory (+ playground at /)
      config.py               Settings (pydantic-settings). Only place that reads env.
      container.py            Composition root: providers, registry, sessions, RunService
      schemas.py              RunRequest, Event, RunResponse, catalog models
      api/                    routes_runs.py (the entrance), routes_catalog.py (catalog, sessions)
      core/
        adapter.py            AgentAdapter protocol, PatternInfo, RunContext
        registry.py           AdapterRegistry (lazy imports)
        sessions.py           SessionRegistry + per-session lock
        scope.py              RunScope contextvar (+ default scope for single-agent hosts)
      providers/              ProviderProfile + build_profiles() for raw / bedrock / vertex
      tools/                  neutral tools: basic.py, knowledge.py, cli.py, browser.py, code.py
      mcp/                    server.py (workbench MCP server), clients.py (server specs)
      rag/                    LocalRetriever, BedrockKbRetriever, VertexRagRetriever
      memory/                 SqliteMemory, AgentCoreMemory, VertexMemoryBank
      guardrails/             LocalGuardrail, BedrockGuardrail, ModelArmorGuardrail
      telemetry.py            TracerProvider + MeterProvider + instrumentors + Claude CLI env
      services/run_service.py The single use case
      adapters/
        adk/                  patterns.py, models.py, services.py, callbacks.py, translate.py
        langgraph/            patterns.py, models.py, persistence.py, translate.py
        strands/              patterns.py, models.py, state.py (sessions + hooks), translate.py
        claude/               agent_sdk.py, messages_api.py, tools.py
      adk_eval_agent/         `root_agent` module for ADK tooling (adk eval / AgentEvaluator)
      runtimes/               agentcore_app.py (AgentCore Runtime), agent_engine_app.py (Agent Engine)
      evals/                  harness.py, scorers.py, run.py (CLI), vertex_eval.py
    data/corpus/              markdown docs the RAG indexes (about these frameworks)
    evals/                    cases.yaml, adk/ evalset
    tests/                    keyless tests; tests/fakes/ = scripted models per framework
  deploy/                     docker-compose (backend + otel-collector + jaeger), k8s/
  infra/                      aws/ and gcp/ provisioning scripts + steps
  docs/                       design/, DEPLOY.md
```

## Why no separate `frontend/`

- The repo convention has a `frontend/`. Here the deliverable is the **API contract** across frameworks.
- A static playground page (`/`) served by the backend covers manual exploration. It is one HTML file with no build.
- It keeps "one entrance" literal: one container, one port.
- Adding a real frontend later is cheap. The event contract is the same as projects 2–4.
