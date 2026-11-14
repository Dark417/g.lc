"""Use case: send a message to the agent inside a session, get the final reply.

This is the only place that touches the ADK Runner. The API layer depends on the
`ChatService` protocol, not on ADK, so tests can substitute a fake.
"""

from typing import Protocol

from google.adk.agents import BaseAgent
from google.adk.runners import Runner
from google.adk.sessions import BaseSessionService, InMemorySessionService
from google.genai import types

from app.schemas import ChatResponse


class ChatService(Protocol):
    async def chat(self, *, user_id: str, session_id: str | None, message: str) -> ChatResponse: ...


class AdkChatService:
    def __init__(
        self,
        *,
        app_name: str,
        agent: BaseAgent,
        session_service: BaseSessionService | None = None,
    ) -> None:
        self._app_name = app_name
        # ILLUSTRATION: in-memory sessions vanish on restart and don't scale past one pod.
        # PRODUCTION: DatabaseSessionService("postgresql://...") or VertexAiSessionService.
        self._sessions = session_service or InMemorySessionService()
        self._runner = Runner(app_name=app_name, agent=agent, session_service=self._sessions)

    async def chat(self, *, user_id: str, session_id: str | None, message: str) -> ChatResponse:
        session = None
        if session_id:
            session = await self._sessions.get_session(
                app_name=self._app_name, user_id=user_id, session_id=session_id
            )
        if session is None:
            session = await self._sessions.create_session(
                app_name=self._app_name, user_id=user_id, session_id=session_id
            )

        content = types.Content(role="user", parts=[types.Part(text=message)])
        reply_parts: list[str] = []

        # The Runner drives the agent loop: model call -> (tool calls) -> model call -> final.
        # Each step is yielded as an Event; we only keep the final text here.
        async for event in self._runner.run_async(
            user_id=user_id, session_id=session.id, new_message=content
        ):
            if event.is_final_response() and event.content and event.content.parts:
                reply_parts.extend(p.text for p in event.content.parts if p.text)

        return ChatResponse(session_id=session.id, reply="".join(reply_parts).strip())
