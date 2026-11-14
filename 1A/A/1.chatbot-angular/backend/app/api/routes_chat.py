from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_chat_service
from app.schemas import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest, service: Annotated[ChatService, Depends(get_chat_service)]
) -> ChatResponse:
    return await service.chat(
        user_id=body.user_id, session_id=body.session_id, message=body.message
    )
