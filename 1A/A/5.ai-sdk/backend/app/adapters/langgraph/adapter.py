"""LangGraph adapter: compile the pattern's graph with a provider-specific checkpointer and store,
stream updates (including subgraphs), and handle interrupt/resume.

resume shapes (RunRequest.resume):
  {"recover": true}   continue a run that crashed: astream(None) re-runs only unfinished nodes
  anything else       the answer to an interrupt(): Command(resume=...)   (hitl pattern)
options.durability: "sync" (checkpoint before the next step starts; safest), "async" (default;
overlaps the write with the next step), "exit" (only at the end; fastest, no mid-run recovery).
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from langgraph.types import Command

from app.adapters.langgraph.models import ChatModelFactory, default_chat_model
from app.adapters.langgraph.patterns import PATTERNS, LgKit, UserContext
from app.adapters.langgraph.persistence import (
    checkpointer,
    node_cache,
    search_memories,
    store,
)
from app.adapters.langgraph.translate import TranslateState, final_output, translate
from app.config import Settings
from app.core.adapter import AdapterError, PatternInfo, RunContext
from app.mcp.clients import server_specs
from app.schemas import Event


async def load_mcp_tools(settings: Settings) -> list:
    """MCP servers -> LangChain tools via langchain-mcp-adapters (a session per tool call)."""
    from langchain_mcp_adapters.client import MultiServerMCPClient

    client = MultiServerMCPClient(
        {
            spec.name: {
                "transport": "stdio",
                "command": spec.command,
                "args": spec.args,
                "env": spec.env,
                "cwd": spec.cwd,
            }
            for spec in server_specs(settings)
        }
    )
    return await client.get_tools()


class LangGraphAdapter:
    name = "langgraph"
    description = (
        "LangGraph graphs and LangChain v1 agents: state, reducers, checkpointers, interrupts."
    )

    def __init__(self, settings: Settings, model_factory: ChatModelFactory | None = None):
        self.settings = settings
        self.model_factory = model_factory or default_chat_model

    def patterns(self) -> list[PatternInfo]:
        return [p.info for p in PATTERNS.values()]

    def providers(self) -> list[str]:
        return ["raw", "bedrock", "vertex"]

    async def run(self, ctx: RunContext) -> AsyncIterator[Event]:
        req, profile, rec = ctx.request, ctx.provider, ctx.session
        pattern = PATTERNS[req.pattern]
        recover = bool((req.resume or {}).get("recover"))
        if req.resume is not None and not recover and not rec.native.get("pending_interrupt"):
            raise AdapterError("nothing to resume: this session is not paused")
        mcp_tools = (
            await load_mcp_tools(self.settings)
            if pattern.uses_mcp and req.options.get("mcp", True)
            else []
        )
        config = self._config(rec.id, req.user_id)
        async with self._graph(req.pattern, profile, req.options, req.vendor, mcp_tools) as graph:
            if recover:
                snapshot = await graph.aget_state(config)
                if not snapshot.next:
                    raise AdapterError("nothing to recover: the last run finished")
                yield Event(type="state", data={"recovering": list(snapshot.next)})
                graph_input = None
            elif req.resume is not None:
                graph_input = Command(resume=req.resume)
            else:
                graph_input = pattern.to_input(req.message, req.user_id)
            st = TranslateState()
            interrupted = False
            async for namespace, chunk in graph.astream(
                graph_input,
                config,
                stream_mode="updates",
                subgraphs=True,
                context=UserContext(user_id=req.user_id),
                durability=req.options.get("durability", "async"),
            ):
                for event in translate(namespace, chunk, st):
                    interrupted = interrupted or event.type == "interrupt"
                    yield event
            rec.native["pending_interrupt"] = interrupted
            if interrupted:
                return  # the run is paused; the client resumes with {"resume": {...}}
            snapshot = await graph.aget_state(config)
            yield Event(
                type="done",
                output=final_output(snapshot.values),
                data={"checkpoint_id": snapshot.config["configurable"].get("checkpoint_id")},
            )

    # ------------------------------------------------------------------ helpers

    def _config(self, thread_id: str, user_id: str) -> dict:
        # thread_id = our session id; actor_id is what AgentCoreMemorySaver keys on.
        return {
            "configurable": {"thread_id": thread_id, "user_id": user_id, "actor_id": user_id},
            "recursion_limit": 2 * self.settings.max_llm_calls + 5,
        }

    @asynccontextmanager
    async def _graph(self, pattern_name, profile, options, vendor=None, mcp_tools=()):
        async with checkpointer(profile.name, self.settings) as saver:
            kit = LgKit(
                profile=profile,
                settings=self.settings,
                options=options,
                model_for=lambda role: self.model_factory(profile, vendor, role),
                checkpointer=saver,
                store=store(profile.name, self.settings),
                mcp_tools=list(mcp_tools),
                cache=node_cache(profile.name, self.settings),
            )
            yield PATTERNS[pattern_name].build(kit)

    # ------------------------------------------------------------------ StateOps

    async def history(self, rec, profile) -> list[dict]:
        async with self._graph(rec.pattern, profile, {}) as graph:
            snapshot = await graph.aget_state(self._config(rec.id, rec.user_id))
        values = snapshot.values or {}
        out = [{"role": "summary", "text": values["summary"]}] if values.get("summary") else []
        for m in values.get("messages", []):
            entry = {"role": m.type, "text": m.text if isinstance(m.text, str) else str(m.content)}
            if getattr(m, "tool_calls", None):
                entry["tool_calls"] = [c["name"] for c in m.tool_calls]
            out.append(entry)
        return out

    async def checkpoints(self, rec, profile) -> list[dict]:
        out = []
        async with self._graph(rec.pattern, profile, {}) as graph:
            async for snap in graph.aget_state_history(self._config(rec.id, rec.user_id)):
                meta = snap.metadata or {}
                out.append(
                    {
                        "checkpoint_id": snap.config["configurable"]["checkpoint_id"],
                        "parent_id": (snap.parent_config or {})
                        .get("configurable", {})
                        .get("checkpoint_id"),
                        "step": meta.get("step"),
                        "source": meta.get("source"),  # input / loop / update / fork
                        "next": list(snap.next),
                        "messages": len((snap.values or {}).get("messages", [])),
                        "created_at": snap.created_at,
                    }
                )
        return out

    async def fork(self, rec, profile, checkpoint_id: str, new) -> None:
        """Copy the state at `checkpoint_id` into a new thread. (LangGraph can also branch *in
        place*: invoke with that checkpoint_id in the config and the thread forks from there.)"""
        as_node = PATTERNS[rec.pattern].fork_as_node
        if as_node is None:
            raise AdapterError(f"fork is implemented for the memory pattern, not {rec.pattern!r}")
        async with self._graph(rec.pattern, profile, {}) as graph:
            src = self._config(rec.id, rec.user_id)
            src["configurable"]["checkpoint_id"] = checkpoint_id
            snapshot = await graph.aget_state(src)
            if not snapshot.values:
                raise AdapterError(f"checkpoint {checkpoint_id!r} not found")
            await graph.aupdate_state(
                self._config(new.id, rec.user_id), snapshot.values, as_node=as_node
            )

    async def memories(self, user_id: str, profile, query: str) -> list[dict]:
        found = await search_memories(store(profile.name, self.settings), user_id, query, limit=20)
        return [{"text": t} for t in found]

    async def forget(self, rec, profile) -> None:
        async with checkpointer(profile.name, self.settings) as saver:
            await saver.adelete_thread(rec.id)


def build(settings: Settings) -> LangGraphAdapter:
    return LangGraphAdapter(settings)
