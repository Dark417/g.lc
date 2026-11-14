"""Exercises the real AdkChatService with a stub agent (no model, no network).

Shows how the Runner/session plumbing works without needing an API key.
"""

from google.adk.agents import BaseAgent
from google.adk.events import Event
from google.genai import types

from app.services.chat_service import AdkChatService


class EchoAgent(BaseAgent):
    """A BaseAgent that replies with the last user message. Stands in for an LlmAgent."""

    async def _run_async_impl(self, ctx):
        last = ctx.user_content.parts[0].text if ctx.user_content else ""
        yield Event(
            author=self.name,
            invocation_id=ctx.invocation_id,
            content=types.Content(role="model", parts=[types.Part(text=f"echo: {last}")]),
        )


async def test_service_creates_and_reuses_session():
    svc = AdkChatService(app_name="t", agent=EchoAgent(name="echo"))

    first = await svc.chat(user_id="u", session_id=None, message="one")
    assert first.reply == "echo: one"
    assert first.session_id

    second = await svc.chat(user_id="u", session_id=first.session_id, message="two")
    assert second.session_id == first.session_id
    assert second.reply == "echo: two"
