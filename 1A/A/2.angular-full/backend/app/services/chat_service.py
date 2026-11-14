"""Use case: run one user turn through the agent, surface every step, stream if asked.

This is the only module that touches the ADK Runner. It translates ADK Events into a small
wire-format (see app/schemas.py) that both the JSON endpoint and the SSE endpoint use.
"""

import logging
from collections.abc import AsyncIterator
from typing import Any, Protocol

from google.adk.agents import BaseAgent
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.sessions import BaseSessionService, InMemorySessionService
from google.genai import types

from app.schemas import ChatResponse, TraceEvent

log = logging.getLogger(__name__)

_MAX_RESULT_CHARS = 1500


class ChatService(Protocol):
    async def chat(self, *, user_id: str, session_id: str | None, message: str) -> ChatResponse: ...

    def stream(
        self, *, user_id: str, session_id: str | None, message: str
    ) -> AsyncIterator[dict[str, Any]]: ...


def _truncate(value: Any) -> Any:
    s = str(value)
    return value if len(s) <= _MAX_RESULT_CHARS else s[:_MAX_RESULT_CHARS] + "…"


def translate_event(event: Event, root_name: str) -> list[dict[str, Any]]:
    """ADK Event -> zero or more wire events. Pure function, unit-tested."""
    out: list[dict[str, Any]] = []
    for fc in event.get_function_calls():
        out.append({"type": "tool_call", "author": event.author, "name": fc.name, "args": fc.args})
    for fr in event.get_function_responses():
        out.append(
            {
                "type": "tool_result",
                "author": event.author,
                "name": fr.name,
                "result": _truncate(fr.response),
            }
        )
    text = "".join(p.text for p in (event.content.parts if event.content else []) if p.text)
    if not text:
        return out
    if event.author == root_name:
        # SSE streaming: partial chunks first, then one non-partial event with the full text.
        out.append({"type": "delta" if event.partial else "final_text", "text": text})
    elif not event.partial:
        # A specialist "thinking out loud" (its answer also comes back as a tool_result).
        out.append({"type": "agent_text", "author": event.author, "text": text})
    return out


class AdkChatService:
    def __init__(
        self,
        *,
        app_name: str,
        agent: BaseAgent,
        session_service: BaseSessionService | None = None,
    ) -> None:
        self._app_name = app_name
        self._root_name = agent.name
        self._sessions = session_service or InMemorySessionService()
        self._runner = Runner(app_name=app_name, agent=agent, session_service=self._sessions)

    async def _ensure_session(self, user_id: str, session_id: str | None):
        session = None
        if session_id:
            session = await self._sessions.get_session(
                app_name=self._app_name, user_id=user_id, session_id=session_id
            )
        if session is None:
            session = await self._sessions.create_session(
                app_name=self._app_name, user_id=user_id, session_id=session_id
            )
        return session

    async def _run(
        self, *, user_id: str, session_id: str | None, message: str, streaming: bool
    ) -> AsyncIterator[dict[str, Any]]:
        session = await self._ensure_session(user_id, session_id)
        yield {"type": "session", "session_id": session.id}
        run_config = RunConfig(
            streaming_mode=StreamingMode.SSE if streaming else StreamingMode.NONE
        )
        async for event in self._runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=types.Content(role="user", parts=[types.Part(text=message)]),
            run_config=run_config,
        ):
            for wire in translate_event(event, self._root_name):
                yield wire

    async def chat(self, *, user_id: str, session_id: str | None, message: str) -> ChatResponse:
        sid, texts, events = "", [], []
        async for ev in self._run(
            user_id=user_id, session_id=session_id, message=message, streaming=False
        ):
            if ev["type"] == "session":
                sid = ev["session_id"]
            elif ev["type"] == "final_text":
                texts.append(ev["text"])
            elif ev["type"] in ("tool_call", "tool_result", "agent_text"):
                events.append(TraceEvent(**ev))
        return ChatResponse(session_id=sid, reply="\n\n".join(texts).strip(), events=events)

    async def stream(
        self, *, user_id: str, session_id: str | None, message: str
    ) -> AsyncIterator[dict[str, Any]]:
        sid, texts = "", []
        try:
            async for ev in self._run(
                user_id=user_id, session_id=session_id, message=message, streaming=True
            ):
                if ev["type"] == "session":
                    sid = ev["session_id"]
                elif ev["type"] == "final_text":
                    texts.append(ev["text"])  # authoritative; deltas were already streamed
                else:
                    yield ev
        except Exception as e:  # surface as a wire event, don't cut the stream silently
            log.exception("stream failed")
            yield {"type": "error", "message": str(e)}
            return
        yield {"type": "done", "session_id": sid, "reply": "\n\n".join(texts).strip()}
