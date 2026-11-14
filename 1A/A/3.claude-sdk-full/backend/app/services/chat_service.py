"""Use case: run one user turn through the Claude Agent SDK, surface every step, stream if asked.

This is the only module that touches the SDK's `query()`. It translates SDK messages into the
same wire format project 2 uses (see app/schemas.py), so the Angular frontend is unchanged.
"""

import logging
import uuid
from collections.abc import AsyncIterator
from dataclasses import replace
from typing import Any, Protocol

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    StreamEvent,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
    query,
)

from app.schemas import ChatResponse, TraceEvent

log = logging.getLogger(__name__)

_MAX_RESULT_CHARS = 1500
ROOT = "orchestrator"


class ChatService(Protocol):
    async def chat(self, *, user_id: str, session_id: str | None, message: str) -> ChatResponse: ...

    def stream(
        self, *, user_id: str, session_id: str | None, message: str
    ) -> AsyncIterator[dict[str, Any]]: ...


def _truncate(value: Any) -> Any:
    s = str(value)
    return value if len(s) <= _MAX_RESULT_CHARS else s[:_MAX_RESULT_CHARS] + "…"


def _result_text(content: str | list[dict] | None) -> Any:
    if isinstance(content, list):
        return "\n".join(c.get("text", "") for c in content if isinstance(c, dict))
    return content


def translate_message(msg: Any) -> list[dict[str, Any]]:
    """SDK message -> zero or more wire events. Pure function, unit-tested."""
    out: list[dict[str, Any]] = []
    if isinstance(msg, AssistantMessage):
        author = ROOT if msg.parent_tool_use_id is None else "subagent"
        for block in msg.content:
            if isinstance(block, ToolUseBlock):
                out.append(
                    {"type": "tool_call", "author": author, "name": block.name, "args": block.input}
                )
            elif isinstance(block, TextBlock) and block.text.strip():
                if author == ROOT:
                    out.append({"type": "final_text", "text": block.text})
                else:
                    out.append({"type": "agent_text", "author": author, "text": block.text})
    elif isinstance(msg, UserMessage) and isinstance(msg.content, list):
        author = ROOT if msg.parent_tool_use_id is None else "subagent"
        for block in msg.content:
            if isinstance(block, ToolResultBlock):
                out.append(
                    {
                        "type": "tool_result",
                        "author": author,
                        "name": block.tool_use_id,
                        "result": _truncate(_result_text(block.content)),
                    }
                )
    elif isinstance(msg, StreamEvent) and msg.parent_tool_use_id is None:
        ev = msg.event
        if (
            ev.get("type") == "content_block_delta"
            and ev.get("delta", {}).get("type") == "text_delta"
        ):
            out.append({"type": "delta", "text": ev["delta"]["text"]})
    elif isinstance(msg, ResultMessage):
        out.append(
            {
                "type": "session",
                "session_id": msg.session_id,
                "cost_usd": msg.total_cost_usd,
                "is_error": msg.is_error,
            }
        )
    return out


class ClaudeChatService:
    def __init__(self, *, options: ClaudeAgentOptions) -> None:
        self._options = options
        self._tool_names: dict[str, str] = {}  # tool_use_id -> tool name, for tool_result rows

    def _run(
        self, *, session_id: str | None, message: str, streaming: bool
    ) -> AsyncIterator[dict[str, Any]]:
        # Sessions: the SDK persists transcripts under `cwd`. `resume` continues one;
        # `session_id` names a new one so we can hand the id to the client up front.
        # PRODUCTION: ClaudeAgentOptions.session_store (SessionStore protocol) -> your DB.
        if session_id:
            options = replace(self._options, resume=session_id)
        else:
            session_id = str(uuid.uuid4())
            options = replace(self._options, session_id=session_id)
        options = replace(options, include_partial_messages=streaming)
        return self._events(session_id, message, options)

    async def _events(self, session_id: str, message: str, options: ClaudeAgentOptions):
        yield {"type": "session", "session_id": session_id}
        async for msg in query(prompt=message, options=options):
            for wire in translate_message(msg):
                if wire["type"] == "tool_call":
                    # remember ids so tool_result rows can show the tool name instead of the id
                    for b in getattr(msg, "content", []):
                        if isinstance(b, ToolUseBlock):
                            self._tool_names[b.id] = b.name
                elif wire["type"] == "tool_result":
                    wire["name"] = self._tool_names.pop(wire["name"], wire["name"])
                yield wire

    async def chat(self, *, user_id: str, session_id: str | None, message: str) -> ChatResponse:
        sid, texts, events = "", [], []
        async for ev in self._run(session_id=session_id, message=message, streaming=False):
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
            async for ev in self._run(session_id=session_id, message=message, streaming=True):
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
