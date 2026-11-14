"""Chat use case: run a turn through the ADK Runner, stream it, and manage conversation history.

The only module that touches the Runner. It translates ADK events into a small wire format the
portal renders. `assess_proposal` results become `verdict` events (rendered as verdict cards).
"""

import base64
import logging
from collections.abc import AsyncIterator
from typing import Any

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.sessions import BaseSessionService
from google.genai import types
from pydantic import BaseModel, Field

log = logging.getLogger(__name__)

MAX_RESULT_CHARS = 1500
# Hard cap on model calls per user turn (ADK's default is 500). Stops runaway tool loops.
MAX_LLM_CALLS = 25
VERDICT_TOOL = "assess_proposal"


class Attachment(BaseModel):
    filename: str = Field(min_length=1, max_length=200)
    mime_type: str = "application/octet-stream"
    data_base64: str


class ConversationNotFound(LookupError):
    pass


def _text(event: Event) -> str:
    if not event.content or not event.content.parts:
        return ""
    return "".join(p.text for p in event.content.parts if p.text and not p.thought)


def _truncate(value: Any) -> Any:
    s = str(value)
    return value if len(s) <= MAX_RESULT_CHARS else s[:MAX_RESULT_CHARS] + "…"


def translate_event(event: Event, root_name: str) -> list[dict[str, Any]]:
    """ADK Event -> wire events. Pure; unit-tested."""
    out: list[dict[str, Any]] = []
    for fc in event.get_function_calls():
        out.append({"type": "tool_call", "author": event.author, "name": fc.name, "args": fc.args})
    for fr in event.get_function_responses():
        resp = fr.response or {}
        if fr.name == VERDICT_TOOL and isinstance(resp, dict) and "verdict" in resp:
            out.append({"type": "verdict", "verdict": resp})
        out.append(
            {
                "type": "tool_result",
                "author": event.author,
                "name": fr.name,
                "result": _truncate(resp),
            }
        )
    text = _text(event)
    if text and event.author == root_name:
        out.append({"type": "delta" if event.partial else "final_text", "text": text})
    return out


def events_to_messages(events: list[Event]) -> list[dict[str, Any]]:
    """Rebuild a readable transcript (user / assistant + verdict cards) from session events."""
    messages: list[dict[str, Any]] = []
    pending: list[dict] = []
    for e in events:
        if e.partial:
            continue
        if e.author == "user":
            if text := _text(e).strip():
                messages.append({"role": "user", "text": text, "verdicts": []})
            continue
        for fr in e.get_function_responses():
            if (
                fr.name == VERDICT_TOOL
                and isinstance(fr.response, dict)
                and "verdict" in fr.response
            ):
                pending.append(fr.response)
        if text := _text(e).strip():
            messages.append({"role": "assistant", "text": text, "verdicts": pending})
            pending = []
    if pending:
        messages.append({"role": "assistant", "text": "", "verdicts": pending})
    return messages


class ChatService:
    def __init__(self, *, runner: Runner, sessions: BaseSessionService, app_name: str, memory=None):
        self._runner = runner
        self._sessions = sessions
        self._app = app_name
        self._memory = memory
        self._root = runner.agent.name if runner.agent else app_name

    @staticmethod
    def build_content(message: str, attachments: list[Attachment]) -> types.Content:
        # Text first: ADK's PreloadMemoryTool searches memory with parts[0].text.
        parts = [types.Part(text=message)]
        for raw in attachments:
            a = raw if isinstance(raw, Attachment) else Attachment.model_validate(raw)
            parts.append(
                types.Part(
                    inline_data=types.Blob(
                        data=base64.b64decode(a.data_base64),
                        mime_type=a.mime_type,
                        display_name=a.filename,
                    )
                )
            )
        return types.Content(role="user", parts=parts)

    async def _session(self, user_id: str, session_id: str | None, message: str):
        if session_id:
            s = await self._sessions.get_session(
                app_name=self._app, user_id=user_id, session_id=session_id
            )
            if s is None:
                raise ConversationNotFound(session_id)
            return s, None
        s = await self._sessions.create_session(app_name=self._app, user_id=user_id)
        return s, {"title": message.strip().splitlines()[0][:60]}

    async def _run(
        self,
        *,
        user_id: str,
        session_id: str | None,
        message: str,
        attachments: list[Attachment],
        streaming: bool,
    ) -> AsyncIterator[dict[str, Any]]:
        session, state_delta = await self._session(user_id, session_id, message)
        yield {"type": "session", "session_id": session.id}
        async for event in self._runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=self.build_content(message, attachments),
            state_delta=state_delta,
            run_config=RunConfig(
                streaming_mode=StreamingMode.SSE if streaming else StreamingMode.NONE,
                max_llm_calls=MAX_LLM_CALLS,
            ),
        ):
            for wire in translate_event(event, self._root):
                yield wire

    async def chat(
        self,
        *,
        user_id: str,
        session_id: str | None,
        message: str,
        attachments: list[Attachment] = (),
    ) -> dict[str, Any]:
        sid, texts, events, verdicts = "", [], [], []
        async for ev in self._run(
            user_id=user_id,
            session_id=session_id,
            message=message,
            attachments=list(attachments),
            streaming=False,
        ):
            match ev["type"]:
                case "session":
                    sid = ev["session_id"]
                case "final_text":
                    texts.append(ev["text"])
                case "verdict":
                    verdicts.append(ev["verdict"])
                case _:
                    events.append(ev)
        return {
            "session_id": sid,
            "reply": "\n\n".join(texts).strip(),
            "verdicts": verdicts,
            "events": events,
        }

    async def stream(
        self,
        *,
        user_id: str,
        session_id: str | None,
        message: str,
        attachments: list[Attachment] = (),
    ) -> AsyncIterator[dict[str, Any]]:
        sid, texts = "", []
        try:
            async for ev in self._run(
                user_id=user_id,
                session_id=session_id,
                message=message,
                attachments=list(attachments),
                streaming=True,
            ):
                if ev["type"] == "final_text":
                    texts.append(ev["text"])
                    continue
                if ev["type"] == "session":
                    sid = ev["session_id"]
                yield ev
        except ConversationNotFound:
            yield {"type": "error", "message": "conversation not found"}
            return
        except Exception as e:  # surface as a wire event instead of cutting the stream
            log.exception("chat stream failed")
            yield {"type": "error", "message": str(e)}
            return
        yield {"type": "done", "session_id": sid, "reply": "\n\n".join(texts).strip()}

    # --- conversation history (always scoped to the caller's user_id) ---
    async def list_conversations(self, user_id: str) -> list[dict[str, Any]]:
        res = await self._sessions.list_sessions(app_name=self._app, user_id=user_id)
        items = [
            {
                "id": s.id,
                "title": s.state.get("title") or "Untitled conversation",
                "updated_at": s.last_update_time,
            }
            for s in res.sessions
        ]
        return sorted(items, key=lambda i: i["updated_at"], reverse=True)

    async def get_conversation(self, user_id: str, session_id: str) -> dict[str, Any]:
        s = await self._sessions.get_session(
            app_name=self._app, user_id=user_id, session_id=session_id
        )
        if s is None:
            raise ConversationNotFound(session_id)
        return {
            "id": s.id,
            "title": s.state.get("title") or "Untitled conversation",
            "updated_at": s.last_update_time,
            "messages": events_to_messages(s.events),
        }

    async def delete_conversation(self, user_id: str, session_id: str) -> None:
        s = await self._sessions.get_session(
            app_name=self._app, user_id=user_id, session_id=session_id
        )
        if s is None:
            raise ConversationNotFound(session_id)
        await self._sessions.delete_session(
            app_name=self._app, user_id=user_id, session_id=session_id
        )
        if self._memory is not None and hasattr(self._memory, "delete_session"):
            await self._memory.delete_session(
                app_name=self._app, user_id=user_id, session_id=session_id
            )
