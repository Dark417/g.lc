"""REST adapter mounted at /comprehend."""

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.a03_04_comprehend import infra, service

router = APIRouter()


class TextRequest(BaseModel):
    text: str = Field(min_length=1)


class BatchRequest(BaseModel):
    texts: list[str] = Field(min_length=1)


@router.post("/analyze")
def analyze(body: TextRequest) -> dict[str, Any]:
    sig = service.gather_signals(body.text)
    return {"language": sig.language, "sentiment": sig.sentiment, "key_phrases": sig.key_phrases,
            "entities": infra.detect_entities(body.text, sig.language)}


@router.post("/entities/batch")
def entities_batch(body: BatchRequest) -> dict[str, Any]:
    r = infra.batch_detect_entities(body.texts)
    return {"ok": r.ok, "failed": r.failed}


@router.post("/route")
def route(body: TextRequest) -> dict[str, Any]:
    return service.route_and_answer(body.text)
