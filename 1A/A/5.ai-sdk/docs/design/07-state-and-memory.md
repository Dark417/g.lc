# 07 · State, memory, checkpoints, context, history, and caching

This doc covers everything an agent *remembers* and how it *recovers*:

- in-flight loop state and checkpoints;
- conversation (short-term) memory, and what of it reaches the model (context);
- long-term memory across sessions;
- history (listing and reading past conversations);
- the cache servers that make all of this fast and multi-replica safe.

## Challenge to the brief

- **"Every framework on every branch" would be 12 near-identical memory stacks.**
  - Most of the 12 cells duplicate each other: a checkpoint is a checkpoint.
  - So we build **one complete suite per branch**, in the framework that shows that branch best.
  - For the other frameworks we add **only what is unique** to them.

| Branch | Suite | Why this framework |
|---|---|---|
| `raw` | **`diy:loop`**: our own agent loop, no framework | "Raw" means *you* own the state. Building the loop by hand shows exactly what frameworks do for you. |
| `bedrock` | **`langgraph:memory`** | LangGraph has the most explicit state model (checkpoints, time travel, stores, node cache). `langgraph-checkpoint-aws` maps every piece onto AWS: AgentCore Memory, DynamoDB + S3, ElastiCache Valkey. |
| `vertex` | **`adk:memory`** | ADK's state model *is* Vertex AI Agent Engine: Sessions, Memory Bank, state scopes, resumability, compaction, Gemini context caching. |

- Each suite runs on any provider's *model*.
  - Its state backends are the managed ones on its home branch.
  - On other branches it falls back to local stores, the same rule as everywhere else in this project.

## Vocabulary (one meaning per word)

| Term | Lifetime | Source of truth | Example |
|---|---|---|---|
| **Run state** | one turn, in flight | checkpoint | step number, pending tool calls, status |
| **Checkpoint** | snapshot after each step | durable store | LangGraph checkpoint, DIY step snapshot, ADK resumable invocation |
| **Conversation** (short-term memory) | one session | durable store | the message list |
| **Session state** | one session | durable store | key-value scratch: ADK `state`, Strands `agent.state`, LangGraph channels |
| **Context** | one model call | computed | the trimmed / summarised / memory-augmented subset sent to the model |
| **Long-term memory** | across sessions, per user | memory store | "user deploys to us-east-1" |
| **History** | product feature | durable store | "list my conversations", "show this transcript" |
| **Cache** | seconds to hours | **never** | session lock, hot checkpoint copy, LLM response cache, prompt cache |

- Rule 1: a cache is never the source of truth. Losing Redis loses speed, not data.
  - The one exception is the lock. It is *coordination*, so it fails **closed**: no lock → 503, never two loops on one session.
- Rule 2: conversation ≠ context.
  - We persist the whole conversation.
  - We *send* a window, summary, or compacted version of it.
  - Mixing the two is how agents silently lose history.

## The loop: framework vs build-your-own

| Concern | Framework loop (ADK / LangGraph / Strands / Claude SDK) | DIY loop (`app/adapters/diy`) |
|---|---|---|
| Who decides the next step | runtime (graph edges, LLM transfer, agent loop) | our `while` loop over a tiny state machine |
| Where state lives | framework session / checkpointer / session manager | our `LoopState`, serialised by our `CheckpointStore` |
| When state is saved | framework-defined (after each node / event) | after **every** step, before side effects are acknowledged |
| Recovery after a crash | resume API (`invoke(None)`, `invocation_id`, `resume=`) | `resume: {"recover": true}` reloads the last checkpoint; finished tool calls are not re-run |
| Context management | middleware / compaction / conversation managers | our strategies: `window`, `token_budget`, `summary`, `server` (Anthropic compaction) |
| Cost | less code, framework conventions | ~400 lines, total control, nothing hidden |

- **DIY state machine**:

```
          ┌──────────── model returns tool_use ─────────────┐
          ▼                                                  │
 READY ─▶ CALL_MODEL ─▶ (end_turn) ─▶ DONE                   │
                │                                            │
                └──────▶ RUN_TOOLS ── each result checkpointed ──┘
 any exception ─▶ FAILED   (the last checkpoint is the recovery point)
```

## Per-branch ownership (the three suites)

| Layer | `raw` · `diy:loop` | `bedrock` · `langgraph:memory` | `vertex` · `adk:memory` |
|---|---|---|---|
| Loop | hand-written state machine | `StateGraph` (agent ⇄ tools + memory nodes) | ADK `Runner` + `LlmAgent` |
| Checkpoint per step | `CheckpointStore`: SQLite (durable) + Redis write-through | `AgentCoreMemorySaver`, `DynamoDBSaver` (+ S3 offload), or `ValkeySaver` (ElastiCache), chosen by `LANGGRAPH_CHECKPOINTER` | resumable invocations (`ResumabilityConfig`) over session events |
| Crash recovery | reload last checkpoint, skip completed tool calls | `astream(None, config)` resumes; pending writes skip finished nodes | `run_async(invocation_id=…)` resumes the invocation |
| Time travel / fork | list checkpoints → fork into a new session | `aget_state_history` → fork from `checkpoint_id` | `rewind_async(before invocation)` |
| Conversation | `LoopState.messages` | `messages` channel (`add_messages` reducer) | `session.events` |
| Session KV state | `LoopState.vars` | extra graph channels | `state` with scopes: session, `user:`, `app:`, `temp:` |
| Context management | `window` · `token_budget` · `summary` · `server` | `trim_messages` + a rolling-summary node | `EventsCompactionConfig` (LLM summarises old events) |
| Long-term write | LLM extraction → **our** consolidation (update-or-insert by similarity) | `AgentCoreMemoryStore.put` → AgentCore strategies extract and consolidate | `add_session_to_memory` → Memory Bank generates and consolidates |
| Long-term read | similarity search, injected as a system block | `store.search(("facts", user))` in a pre-model node | `PreloadMemoryTool` (every turn) + `load_memory` (on demand) |
| History | SQL over our sessions table | checkpointer `alist` per thread | `list_sessions` / `get_session` |
| Cache server | Redis: lock, hot checkpoint, LLM response cache, Anthropic prompt caching | ElastiCache Valkey: `ValkeySaver`; LangGraph node cache (`CachePolicy`) | Memorystore: lock; Gemini **context caching** (`ContextCacheConfig`) |

## Unique parts in the other frameworks (and nothing else)

| Framework | Unique state feature | Where |
|---|---|---|
| Strands | `SummarizingConversationManager` (summarise instead of drop), triggered by a `reduce_context` hook; `agent.state` (persisted, never sent to the model); `S3SessionManager` on bedrock (`STRANDS_S3_SESSION_BUCKET`) | `strands:memory` |
| Claude Agent SDK | `SessionStore` protocol: we implement `RedisSessionStore`, so CLI sessions survive replicas (closes the gap in `03-cloud-branches.md`); `fork_session` (every message uuid is a fork point); `get_session_messages` for history; `PreCompact` hook on auto-compaction | every `claude` Agent SDK pattern when `REDIS_URL` is set (`app/adapters/claude/session_store.py`) |
| Claude Messages API | server-side context management: compaction (`compact_20260112`) and context editing (`clear_tool_uses_20250919`); prompt caching (`cache_control`) | the `server` strategy and prompt caching inside `diy:loop` |
| ADK, LangGraph | covered by their suites | — |

## Cache servers

- One protocol (RESP), many products. The client is `redis.asyncio`. Only `REDIS_URL` changes.

| Where | Product | `REDIS_URL` |
|---|---|---|
| local / compose | Redis OSS or Valkey | `redis://localhost:6379/0` |
| AWS | ElastiCache (Valkey or Redis OSS); MemoryDB if you need durability | `rediss://<cluster>.cache.amazonaws.com:6379` |
| GCP | Memorystore for Valkey / Redis | `redis://10.x.x.x:6379` (VPC) |
| tests | a real `redis-server` started on a free port | set by the fixture |

| Role | Key pattern | TTL | On cache outage |
|---|---|---|---|
| Distributed session lock | `lock:session:{id}` = owner token (`SET NX PX`, Lua compare-and-delete release) | lease 300 s | **fail closed** (503) |
| Session registry (bindings, native ids) | `session:{id}` JSON | 30 d | durable-by-Redis: use MemoryDB or persistence (AOF) in prod |
| Hot checkpoint (DIY) | `diy:ckpt:{session}` latest checkpoint JSON | 1 h | fail open → read SQLite |
| LLM response cache (DIY) | `llmcache:{sha256(model, system, messages, tools)}` | 1 h | fail open → call the model |
| LangGraph checkpoints (bedrock) | `ValkeySaver` keys | configurable | it *is* the store: use MemoryDB / AOF |
| Server-side prompt / context cache | Anthropic `cache_control`, Gemini `ContextCacheConfig` | provider-managed | n/a |

- Without `REDIS_URL`, the in-process lock and registry stay (ILLUSTRATION, one replica).
- With `REDIS_URL`, every framework gets the distributed lock. `deploy/k8s` can then run more than one replica.

## State API

Generic endpoints. Adapters opt in by implementing `StateOps`. Unsupported operations return `501`.

| Endpoint | Does |
|---|---|
| `GET /v1/sessions/{id}/history` | transcript as `[{role, text, ...}]` from the framework's own store |
| `GET /v1/sessions/{id}/checkpoints` | checkpoints / invocations, newest first |
| `POST /v1/sessions/{id}/fork` `{"checkpoint_id"}` | new session that continues from that checkpoint |
| `POST /v1/sessions/{id}/rewind` `{"checkpoint_id"}` | roll back in place to before that checkpoint (ADK `rewind_async`) |
| `GET /v1/users/{user_id}/memories?framework=&provider=&query=` | long-term memories as the framework sees them |
| `DELETE /v1/sessions/{id}` | forget: the durable store, caches, and the registry |
| `POST /v1/runs` with `resume: {"recover": true}` | continue a run that crashed mid-turn |

## Where it lives

| Suite / part | Code | Tests |
|---|---|---|
| cache server, lock, registry, LLM cache, state API | `app/core/sessions.py`, `app/state/cache.py`, `app/api/routes_state.py` | `tests/test_state_cache.py` |
| `diy:loop` (raw) | `app/adapters/diy/` (`state.py`, `context.py`, `longterm.py`, `loop.py`) | `tests/test_diy.py` |
| `langgraph:memory` (bedrock) | `app/adapters/langgraph/memory.py`, `persistence.py` | `tests/test_langgraph_memory.py` (Valkey on redis-server, DynamoDB on moto) |
| `adk:memory` (vertex) | `app/adapters/adk/memory.py`, `adapter.py` (StateOps) | `tests/test_adk_memory.py` |
| `strands:memory` | `app/adapters/strands/memory.py`, `state.py` | `tests/test_strands_memory.py` (S3 on moto) |
| Claude `RedisSessionStore` | `app/adapters/claude/session_store.py` | `tests/test_claude.py` |

## Demo script (what the tests prove)

1. Tell the agent a fact. Ask about it in the **same** session (conversation memory) and in a **new** session (long-term memory).
2. Run a turn with `options.crash_after_step=2`. The run fails. Recover it: the tools that already ran are not called again.
3. List checkpoints. Fork from an earlier one. The fork has the old state, and the original is untouched.
4. Send a long conversation. The context sent to the model stays under budget while the stored conversation stays complete.
5. Send the same question twice. The second answer comes from the LLM cache.
6. Two concurrent requests on one session across two "replicas" (two registries, one Redis): one gets `409`.
