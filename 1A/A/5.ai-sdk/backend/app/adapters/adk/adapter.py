"""Google ADK adapter: Runner + App + plugin + provider-specific session and memory services.

resume {"recover": true} continues a failed invocation (patterns whose App is resumable).
StateOps read the ADK session/memory services: history (events), checkpoints (invocations),
rewind (Runner.rewind_async), fork (copy events into a new session), memories, forget.
"""

from collections.abc import AsyncIterator

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.apps import App
from google.adk.runners import Runner
from google.genai import types

from app.adapters.adk.callbacks import AuditPlugin
from app.adapters.adk.models import ModelFactory, default_model_factory
from app.adapters.adk.patterns import PATTERNS, AdkKit
from app.adapters.adk.services import memory_service, session_service
from app.adapters.adk.translate import TranslateState, translate
from app.config import Settings
from app.core.adapter import AdapterError, PatternInfo, RunContext
from app.schemas import Event

# One ADK app name for every pattern, so long-term memory (keyed by app + user) is shared.
APP_NAME = "ai_sdk"


class AdkAdapter:
    name = "adk"
    description = (
        "Google Agent Development Kit: workflow agents, graph Workflow, services, callbacks."
    )

    def __init__(self, settings: Settings, model_factory: ModelFactory | None = None):
        self.settings = settings
        self.model_factory = model_factory or default_model_factory

    def patterns(self) -> list[PatternInfo]:
        return [p.info for p in PATTERNS.values()]

    def providers(self) -> list[str]:
        return ["raw", "bedrock", "vertex"]

    async def run(self, ctx: RunContext) -> AsyncIterator[Event]:
        req, profile = ctx.request, ctx.provider
        pattern = PATTERNS[req.pattern]
        kit = AdkKit(
            profile=profile,
            settings=self.settings,
            options=req.options,
            model_for=lambda role: self.model_factory(profile, req.vendor, role),
        )
        sessions = session_service(profile.name, self.settings)
        memory = memory_service(profile.name, self.settings, profile.memory)
        plugin = AuditPlugin()
        recover = bool((req.resume or {}).get("recover"))
        try:
            root = pattern.build(kit)
            app_config = pattern.app_config(kit) if pattern.app_config else {}
            if recover and not app_config.get("resumability_config"):
                raise AdapterError(f"adk:{req.pattern} is not resumable; use adk:memory")
            runner = Runner(
                app=App(name=APP_NAME, root_agent=root, plugins=[plugin], **app_config),
                session_service=sessions,
                memory_service=memory,
            )
            session_id = await self._ensure_session(sessions, ctx)
            if recover:
                # The failed invocation is the last one in the session; resume it by id.
                current = await sessions.get_session(
                    app_name=APP_NAME, user_id=req.user_id, session_id=session_id
                )
                invocation_id = current.events[-1].invocation_id if current.events else None
                if invocation_id is None:
                    raise AdapterError("nothing to recover")
                yield Event(type="state", data={"resuming_invocation": invocation_id})
                run_args = {"invocation_id": invocation_id}
            else:
                run_args = {
                    "new_message": types.Content(role="user", parts=[types.Part(text=req.message)])
                }
            st = TranslateState()
            async for adk_event in runner.run_async(
                user_id=req.user_id,
                session_id=session_id,
                run_config=RunConfig(
                    streaming_mode=StreamingMode.SSE, max_llm_calls=self.settings.max_llm_calls
                ),
                **run_args,
            ):
                for event in translate(adk_event, st):
                    yield event

            session = await sessions.get_session(
                app_name=APP_NAME, user_id=req.user_id, session_id=session_id
            )
            # Long-term memory: hand the finished conversation to the memory service
            # (Memory Bank / AgentCore extract facts from it; InMemory indexes it).
            await memory.add_session_to_memory(session)
            output = st.last_text
            if pattern.output_key and session.state.get(pattern.output_key):
                output = session.state[pattern.output_key]
            elif st.workflow_output is not None:
                output = st.workflow_output
            usage = next(iter(plugin.usage.values()), None)
            yield Event(type="done", output=output, data={"usage": usage} if usage else None)
        finally:
            for toolset in kit.toolsets:
                await toolset.close()

    # ------------------------------------------------------------------ StateOps

    def _services(self, profile):
        return session_service(profile.name, self.settings), memory_service(
            profile.name, self.settings, profile.memory
        )

    async def _session(self, rec, profile):
        sessions, _ = self._services(profile)
        sid = rec.native.get("adk_session_id")
        session = sid and await sessions.get_session(
            app_name=APP_NAME, user_id=rec.user_id, session_id=sid
        )
        if not session:
            raise AdapterError("no ADK session for this session yet")
        return sessions, session

    async def history(self, rec, profile) -> list[dict]:
        _, session = await self._session(rec, profile)
        out = []
        for e in session.events:
            entry: dict = {"role": e.author, "invocation_id": e.invocation_id}
            if e.actions and e.actions.compaction:
                parts = e.actions.compaction.compacted_content.parts or []
                out.append(
                    {**entry, "role": "compaction", "text": "".join(p.text or "" for p in parts)}
                )
                continue
            if e.actions and e.actions.rewind_before_invocation_id:
                out.append(
                    {
                        **entry,
                        "role": "rewind",
                        "text": f"rewound before {e.actions.rewind_before_invocation_id}",
                    }
                )
                continue
            for p in e.content.parts if e.content and e.content.parts else []:
                if p.text and not p.thought:
                    out.append({**entry, "text": p.text})
                elif p.function_call:
                    out.append({**entry, "tool_call": p.function_call.name})
        return out + [{"role": "state", "state": dict(session.state)}]

    async def checkpoints(self, rec, profile) -> list[dict]:
        """ADK's unit of recovery and rewind is the invocation (one user turn)."""
        _, session = await self._session(rec, profile)
        seen: dict[str, dict] = {}
        for e in session.events:
            if not e.invocation_id:
                continue
            item = seen.setdefault(
                e.invocation_id,
                {
                    "checkpoint_id": e.invocation_id,
                    "events": 0,
                    "created_at": e.timestamp,
                    "user": None,
                },
            )
            item["events"] += 1
            if e.author == "user" and e.content and e.content.parts:
                item["user"] = e.content.parts[0].text
        return list(reversed(seen.values()))

    async def rewind(self, rec, profile, checkpoint_id: str) -> None:
        sessions, session = await self._session(rec, profile)
        runner = Runner(
            app=App(
                name=APP_NAME, root_agent=PATTERNS[rec.pattern].build(self._kit_for_state(profile))
            ),
            session_service=sessions,
        )
        await runner.rewind_async(
            user_id=rec.user_id, session_id=session.id, rewind_before_invocation_id=checkpoint_id
        )

    async def fork(self, rec, profile, checkpoint_id: str, new) -> None:
        """ADK has no fork; build one on the session service: a new session that replays the
        events up to and including `checkpoint_id` (their state deltas rebuild session state)."""
        sessions, session = await self._session(rec, profile)
        ids = [e.invocation_id for e in session.events]
        if checkpoint_id not in ids:
            raise AdapterError(f"invocation {checkpoint_id!r} not found")
        last = max(i for i, inv in enumerate(ids) if inv == checkpoint_id)
        requested = None if profile.name == "vertex" and self.settings.agent_engine_id else new.id
        forked = await sessions.create_session(
            app_name=APP_NAME, user_id=rec.user_id, session_id=requested
        )
        for event in session.events[: last + 1]:
            await sessions.append_event(forked, event.model_copy(deep=True))
        new.native["adk_session_id"] = forked.id

    async def memories(self, user_id: str, profile, query: str) -> list[dict]:
        _, memory = self._services(profile)
        found = await memory.search_memory(app_name=APP_NAME, user_id=user_id, query=query)
        return [
            {"text": "".join(p.text or "" for p in (m.content.parts or [])), "author": m.author}
            for m in found.memories
        ]

    async def forget(self, rec, profile) -> None:
        sessions, session = await self._session(rec, profile)
        await sessions.delete_session(app_name=APP_NAME, user_id=rec.user_id, session_id=session.id)

    def _kit_for_state(self, profile) -> AdkKit:
        return AdkKit(profile=profile, settings=self.settings, options={"mcp": False},
                      model_for=lambda role: self.model_factory(profile, None, role))  # fmt: skip

    async def _ensure_session(self, sessions, ctx: RunContext) -> str:
        """Our session id -> ADK session id. Agent Engine assigns its own ids, so we map."""
        rec, user_id = ctx.session, ctx.request.user_id
        sid = rec.native.get("adk_session_id")
        if sid and await sessions.get_session(app_name=APP_NAME, user_id=user_id, session_id=sid):
            return sid
        requested = (
            None if ctx.provider.name == "vertex" and self.settings.agent_engine_id else rec.id
        )
        session = await sessions.create_session(
            app_name=APP_NAME, user_id=user_id, session_id=requested
        )
        rec.native["adk_session_id"] = session.id
        return session.id


def build(settings: Settings) -> AdkAdapter:
    return AdkAdapter(settings)
