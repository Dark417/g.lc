"""Thin REST adapter, mounted at /converse by app.main when "converse" is in A_ENABLED.

- POST /stream returns Server-Sent Events (text/event-stream): one event per text delta, then stop + usage.
- The showcase is built lazily on first request: importing this module makes no AWS call.
"""

import base64
import json
from collections.abc import Iterator
from dataclasses import asdict
from functools import lru_cache
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.a01_01_converse.domain import ConverseError, ConverseResult
from app.a01_01_converse.infra import ConverseShowcase, InMemoryConversationStore
from app.a01_01_converse.service import DEMO_TOOLS, ChatService

router = APIRouter()


@lru_cache
def get_showcase() -> ConverseShowcase:
    return ConverseShowcase()


@lru_cache
def get_chat() -> ChatService:
    return ChatService(get_showcase(), InMemoryConversationStore())


Showcase = Annotated[ConverseShowcase, Depends(get_showcase)]
Chat = Annotated[ChatService, Depends(get_chat)]


class PromptRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=20_000)
    system: str = "You are a concise assistant for backend engineers."
    max_tokens: int | None = Field(default=None, gt=0, le=8192)
    stop_sequences: list[str] | None = Field(default=None, max_length=4)


class MediaRequest(BaseModel):
    """JSON upload (base64) keeps the slice free of a multipart dependency; boto3 gets raw bytes."""

    question: str = Field(min_length=1)
    format: str = Field(description="image: png|jpeg|gif|webp; document: pdf|csv|doc|docx|xls|xlsx|html|txt|md")
    content_b64: str = Field(min_length=1)
    filename: str | None = None


class ToolsRequest(BaseModel):
    prompt: str = Field(min_length=1)
    tool_choice: str = Field(default="auto", pattern="^(auto|any)$")
    forced_tool: str | None = None


def _json(result: ConverseResult) -> dict[str, Any]:
    return {
        "text": result.text,
        "stop_reason": result.stop_reason,
        "usage": asdict(result.usage),
        "latency_ms": result.latency_ms,
        "tool_calls": result.tool_calls,
        "rounds": result.rounds,
    }


@router.get("/models")
def list_models(showcase: Showcase, provider: str | None = None, output_modality: str | None = None) -> list[dict[str, Any]]:
    return [asdict(m) for m in showcase.list_foundation_models(provider=provider, output_modality=output_modality)]


@router.get("/inference-profiles")
def list_profiles(showcase: Showcase) -> list[dict[str, str]]:
    return showcase.list_inference_profiles()


@router.post("/chat")
def chat(body: PromptRequest, showcase: Showcase) -> dict[str, Any]:
    return _json(showcase.converse_basic(body.prompt, body.system, max_tokens=body.max_tokens, stop_sequences=body.stop_sequences))


@router.post("/chat/retry")
def chat_with_retry(body: PromptRequest, showcase: Showcase) -> dict[str, Any]:
    try:
        return _json(showcase.converse_with_retry(body.prompt))
    except ConverseError as e:  # ValidationException / AccessDenied: the request is wrong, not the service
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/conversations/{conversation_id}/messages")
def send_message(conversation_id: str, body: PromptRequest, chat_service: Chat) -> dict[str, Any]:
    return _json(chat_service.send(conversation_id, body.prompt))


@router.post("/stream")
def stream(body: PromptRequest, showcase: Showcase) -> StreamingResponse:
    def sse() -> Iterator[str]:
        for event in showcase.converse_stream(body.prompt, body.system):
            payload = {k: v for k, v in asdict(event).items() if v not in ("", None, 0)}
            yield f"event: {event.kind}\ndata: {json.dumps(payload)}\n\n"

    return StreamingResponse(sse(), media_type="text/event-stream")


@router.post("/tools")
def tools(body: ToolsRequest, showcase: Showcase) -> dict[str, Any]:
    try:
        return _json(showcase.converse_with_tools(body.prompt, DEMO_TOOLS, body.tool_choice, body.forced_tool))
    except ConverseError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@router.post("/image")
def image(body: MediaRequest, showcase: Showcase) -> dict[str, Any]:
    try:
        return _json(showcase.converse_image(base64.b64decode(body.content_b64), body.format, body.question))
    except ConverseError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/document")
def document(body: MediaRequest, showcase: Showcase) -> dict[str, Any]:
    raw = base64.b64decode(body.content_b64)
    return _json(showcase.converse_document(raw, body.format, body.filename or "document", body.question))


@router.post("/invoke-model")
def invoke_model(body: PromptRequest, showcase: Showcase) -> dict[str, Any]:
    return showcase.invoke_model_anthropic(body.prompt, body.system)
