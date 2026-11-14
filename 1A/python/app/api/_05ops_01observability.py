"""REST adapter mounted at /observability."""

from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.infra import _05ops_01observability as infra
from app.service import _05ops_01observability as service
from app.shared.config import get_settings

router = APIRouter()


class AskRequest(BaseModel):
    prompt: str = Field(min_length=1)


@router.post("/ask")
def ask(body: AskRequest) -> dict[str, Any]:
    return service.ask(body.prompt)


@router.get("/usage")
def usage(hours: int = Query(24, ge=1, le=336), model_id: str | None = None) -> list[dict[str, Any]]:
    points = infra.token_usage_over_time(model_id or get_settings().fast_model_id, hours)
    return [{"timestamp": p.timestamp.isoformat(), "input": p.input_tokens, "output": p.output_tokens} for p in points]


@router.get("/insights/tokens")
def insights(hours: int = Query(24, ge=1, le=168)) -> list[dict[str, str]]:
    return infra.logs_insights(hours=hours)
