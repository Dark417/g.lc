"""Runs the real AdkChatService + Runner with scripted agents (no model, no network).

This is the most useful test in the project: it pins down how ADK events become trace events.
"""

from google.adk.agents import BaseAgent
from google.adk.events import Event
from google.genai import types

from app.services.chat_service import AdkChatService, translate_event


def _ev(author, *parts, partial=False, ctx=None):
    return Event(
        author=author,
        invocation_id=ctx.invocation_id if ctx else "inv",
        partial=partial,
        content=types.Content(role="model", parts=list(parts)),
    )


class ToolUsingAgent(BaseAgent):
    """Pretends to call `calculate`, then answers. Mirrors a real LlmAgent's event sequence."""

    async def _run_async_impl(self, ctx):
        yield _ev(
            self.name,
            types.Part(
                function_call=types.FunctionCall(name="calculate", args={"expression": "6*7"})
            ),
            ctx=ctx,
        )
        yield _ev(
            self.name,
            types.Part(
                function_response=types.FunctionResponse(name="calculate", response={"result": 42})
            ),
            ctx=ctx,
        )
        yield _ev(self.name, types.Part(text="It's 42."), ctx=ctx)


class StreamingAgent(BaseAgent):
    async def _run_async_impl(self, ctx):
        yield _ev(self.name, types.Part(text="Hel"), partial=True, ctx=ctx)
        yield _ev(self.name, types.Part(text="lo"), partial=True, ctx=ctx)
        yield _ev(self.name, types.Part(text="Hello"), ctx=ctx)


async def test_chat_collects_trace_and_reply():
    svc = AdkChatService(app_name="t", agent=ToolUsingAgent(name="orchestrator"))
    res = await svc.chat(user_id="u", session_id=None, message="6*7?")
    assert res.reply == "It's 42."
    assert [e.type for e in res.events] == ["tool_call", "tool_result"]
    assert res.events[0].name == "calculate" and res.events[0].args == {"expression": "6*7"}
    assert res.events[1].result == {"result": 42}


async def test_stream_yields_deltas_then_done():
    svc = AdkChatService(app_name="t", agent=StreamingAgent(name="orchestrator"))
    out = [ev async for ev in svc.stream(user_id="u", session_id=None, message="hi")]
    assert [e["type"] for e in out] == ["delta", "delta", "done"]
    assert "".join(e["text"] for e in out[:2]) == "Hello"
    assert out[-1]["reply"] == "Hello" and out[-1]["session_id"]


def test_specialist_text_is_agent_text_not_reply():
    ev = _ev("data_agent", types.Part(text="Ada has 3 orders."))
    assert translate_event(ev, root_name="orchestrator") == [
        {"type": "agent_text", "author": "data_agent", "text": "Ada has 3 orders."}
    ]
