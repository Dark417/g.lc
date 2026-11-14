from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    session_id: str | None = Field(default=None, description="Omit to start a new conversation")
    user_id: str = "anonymous"


class TraceEvent(BaseModel):
    """One step of the agent loop, surfaced to the UI so you can see the wiring."""

    type: Literal["tool_call", "tool_result", "agent_text"]
    author: str
    name: str | None = None
    args: dict[str, Any] | None = None
    result: Any = None
    text: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    events: list[TraceEvent] = []


# Streaming wire format (one JSON object per SSE `data:` line):
#   {"type": "delta", "text": "..."}                  partial model output
#   {"type": "tool_call" | "tool_result" | "agent_text", ...}   same shape as TraceEvent
#   {"type": "done", "session_id": "...", "reply": "..."}
#   {"type": "error", "message": "..."}
class StreamDone(BaseModel):
    type: Literal["done"] = "done"
    session_id: str
    reply: str
