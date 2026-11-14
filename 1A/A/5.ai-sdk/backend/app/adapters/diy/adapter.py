"""DIY adapter: the `raw` branch's state suite. No agent framework, every piece of state ours.

Pattern `loop` options (RunRequest.options):
  context            full | window | token_budget | summary | server     (default window)
  window, token_budget, keep_recent, summarize_after                    strategy knobs
  long_term          extract + consolidate + recall facts (default true)
  llm_cache          exact-match response cache in Redis (default true when REDIS_URL is set)
  crash_after_step   simulate a crash after the Nth checkpoint of this run (recovery demo)
Recover a crashed turn with  {"resume": {"recover": true}}.
"""

from collections.abc import AsyncIterator

from app.adapters.claude.messages_api import ClientFactory, default_client, model_for
from app.adapters.claude.tools import as_beta_tool
from app.adapters.diy.longterm import FactStore
from app.adapters.diy.loop import AgentLoop
from app.adapters.diy.state import (
    CachedCheckpointStore,
    Checkpoint,
    CheckpointStore,
    SqliteCheckpointStore,
)
from app.config import Settings
from app.core.adapter import AdapterError, PatternInfo, RunContext
from app.core.sessions import SessionRecord
from app.providers.profile import ProviderProfile
from app.schemas import Event
from app.state.cache import LlmResponseCache, redis_client
from app.tools import tools_for

PATTERN = PatternInfo(
    "loop",
    "A hand-written agent loop: explicit state machine, a checkpoint per step, crash recovery, "
    "fork, four context strategies, long-term memory with consolidation, Redis caches.",
    (
        "LoopState + state machine", "checkpoint per step (SQLite)", "Redis write-through checkpoint cache",
        "recover after crash", "fork from checkpoint", "context: window / token_budget / summary / server",
        "Anthropic compaction + context editing (server)", "long-term: extract -> consolidate -> recall",
        "LLM response cache (Redis)", "prompt caching (cache_control)",
    ),
)  # fmt: skip


class DiyAdapter:
    name = "diy"
    description = "No framework: an agent loop and all of its state management, built by hand."

    def __init__(self, settings: Settings, client_factory: ClientFactory = default_client):
        self.settings = settings
        self.client_factory = client_factory
        self._store: CheckpointStore | None = None
        self._cache: LlmResponseCache | None = None
        self.facts = FactStore(settings.data_path / "diy_facts.db")

    def patterns(self) -> list[PatternInfo]:
        return [PATTERN]

    def providers(self) -> list[str]:
        return ["raw", "bedrock", "vertex"]  # the model can be anywhere; the state is always ours

    @property
    def store(self) -> CheckpointStore:
        if self._store is None:
            durable = SqliteCheckpointStore(self.settings.data_path / "diy_checkpoints.db")
            if self.settings.redis_url:
                redis = redis_client(self.settings.redis_url)
                self._store = CachedCheckpointStore(durable, redis)
                self._cache = LlmResponseCache(redis, self.settings.llm_cache_ttl_s)
            else:
                self._store = durable
        return self._store

    def _loop(self, profile: ProviderProfile, opts: dict) -> AgentLoop:
        store = self.store
        tools = tools_for(
            profile,
            [
                "calculator",
                "current_time",
                "search_docs",
                "remember",
                "recall",
                "run_cli",
                "run_code",
            ],
        )
        return AgentLoop(
            client=self.client_factory(profile),
            model=model_for(profile),
            store=store,
            facts=self.facts,
            tools=tools,
            tool_defs=[as_beta_tool(f).to_dict() for f in tools],
            opts=opts,
            llm_cache=self._cache,
            max_model_calls=self.settings.max_llm_calls,
        )

    async def run(self, ctx: RunContext) -> AsyncIterator[Event]:
        req = ctx.request
        recover = bool((req.resume or {}).get("recover"))
        if req.resume is not None and not recover:
            raise AdapterError('the diy loop resumes with {"recover": true}')
        loop = self._loop(ctx.provider, req.options)
        async for event in loop.run_turn(
            session_id=ctx.session.id, user_id=req.user_id, message=req.message, recover=recover
        ):
            yield event
        ctx.session.native["diy_checkpoint"] = loop.last_checkpoint

    # ------------------------------------------------------------------ StateOps

    async def history(self, rec: SessionRecord, profile: ProviderProfile) -> list[dict]:
        latest = await self.store.latest(rec.id)
        out = []
        for m in latest.state.messages if latest else []:
            if isinstance(m["content"], str):
                out.append({"role": m["role"], "text": m["content"]})
                continue
            for b in m["content"]:
                if b.get("type") == "text":
                    out.append({"role": m["role"], "text": b["text"]})
                elif b.get("type") == "tool_use":
                    out.append(
                        {"role": "assistant", "tool_call": b["name"], "args": b.get("input")}
                    )
                elif b.get("type") == "tool_result":
                    out.append(
                        {
                            "role": "tool",
                            "tool_use_id": b["tool_use_id"],
                            "result": b.get("content"),
                        }
                    )
        return out

    async def checkpoints(self, rec: SessionRecord, profile: ProviderProfile) -> list[dict]:
        return [c.meta() for c in await self.store.list(rec.id)]

    async def fork(
        self, rec: SessionRecord, profile: ProviderProfile, checkpoint_id: str, new: SessionRecord
    ) -> None:
        src = await self.store.get(rec.id, checkpoint_id)
        if src is None:
            raise AdapterError(f"checkpoint {checkpoint_id!r} not found")
        state = src.state
        state.session_id = new.id
        await self.store.put(Checkpoint.of(state, "fork", parent_id=f"{rec.id}/{checkpoint_id}"))

    async def memories(self, user_id: str, profile: ProviderProfile, query: str) -> list[dict]:
        return await self.facts.search(user_id, query, k=20)

    async def forget(self, rec: SessionRecord, profile: ProviderProfile) -> None:
        await self.store.delete(rec.id)


def build(settings: Settings) -> DiyAdapter:
    return DiyAdapter(settings)
