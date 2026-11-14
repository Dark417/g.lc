import json
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.deps import get_chat_service
from app.schemas import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest, service: Annotated[ChatService, Depends(get_chat_service)]
) -> ChatResponse:
    """One turn, full trace, JSON reply."""
    return await service.chat(
        user_id=body.user_id, session_id=body.session_id, message=body.message
    )


@router.post("/chat/stream")
async def chat_stream(
    body: ChatRequest, service: Annotated[ChatService, Depends(get_chat_service)]
) -> StreamingResponse:
    """Same turn as Server-Sent Events: `data: <json>\\n\\n` per event, ending with type=done."""

    async def sse():
        async for ev in service.stream(
            user_id=body.user_id, session_id=body.session_id, message=body.message
        ):
            yield f"data: {json.dumps(ev)}\n\n"

    return StreamingResponse(
        sse(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
