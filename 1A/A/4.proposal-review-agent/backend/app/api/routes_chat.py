import json

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.api.deps import IdentityDep
from app.services.chat import Attachment, ChatService, ConversationNotFound

router = APIRouter(prefix="/api/v1", tags=["chat"])

MAX_ATTACHMENTS = 5


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=20_000)
    session_id: str | None = None
    attachments: list[Attachment] = Field(default=[], max_length=MAX_ATTACHMENTS)


def _chat(request: Request) -> ChatService:
    return request.app.state.chat


@router.post("/chat")
async def chat(body: ChatRequest, identity: IdentityDep, request: Request) -> dict:
    try:
        return await _chat(request).chat(
            user_id=identity.user_id,
            session_id=body.session_id,
            message=body.message,
            attachments=body.attachments,
        )
    except ConversationNotFound as e:
        raise HTTPException(404, "conversation not found") from e


@router.post("/chat/stream")
async def chat_stream(
    body: ChatRequest, identity: IdentityDep, request: Request
) -> StreamingResponse:
    """Server-Sent Events: `data: <json>` per event.
    Types: session, tool_call, tool_result, verdict, delta, done, error."""
    service = _chat(request)

    async def sse():
        async for ev in service.stream(
            user_id=identity.user_id,
            session_id=body.session_id,
            message=body.message,
            attachments=body.attachments,
        ):
            yield f"data: {json.dumps(ev, default=str)}\n\n"

    return StreamingResponse(
        sse(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/conversations")
async def conversations(identity: IdentityDep, request: Request) -> list[dict]:
    return await _chat(request).list_conversations(identity.user_id)


@router.get("/conversations/{session_id}")
async def conversation(session_id: str, identity: IdentityDep, request: Request) -> dict:
    try:
        return await _chat(request).get_conversation(identity.user_id, session_id)
    except ConversationNotFound as e:
        raise HTTPException(404, "conversation not found") from e


@router.delete("/conversations/{session_id}", status_code=204)
async def delete_conversation(session_id: str, identity: IdentityDep, request: Request) -> None:
    try:
        await _chat(request).delete_conversation(identity.user_id, session_id)
    except ConversationNotFound as e:
        raise HTTPException(404, "conversation not found") from e
