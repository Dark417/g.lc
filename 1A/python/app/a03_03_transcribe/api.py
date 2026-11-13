"""REST adapter mounted at /transcribe."""

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.a03_03_transcribe import service

router = APIRouter()


class TranscribeRequest(BaseModel):
    key: str = Field(min_length=1, description="object key under transcribe/in/")
    diarize: bool = True
    redact: bool = True


@router.post("/summarize")
def summarize_call(body: TranscribeRequest) -> dict[str, Any]:
    return service.transcribe_and_summarize(body.key, body.diarize, body.redact)
