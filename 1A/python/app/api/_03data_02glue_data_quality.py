"""REST adapter mounted at /glue_dq."""

from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, Header

from app.service import _03data_02glue_data_quality as service
from app.domain._03data_02glue_data_quality import build_ruleset, default_rules
from app.infra._03data_02glue_data_quality import list_results

router = APIRouter()


@router.get("/ruleset")
def ruleset() -> dict[str, str]:
    return {"dqdl": build_ruleset(default_rules())}


@router.post("/gate")
def gate(idempotency_key: str = Header(alias="Idempotency-Key", min_length=1)) -> dict[str, Any]:
    return asdict(service.evaluate_gate(idempotency_key))


@router.get("/results")
def results(limit: int = 20) -> list[dict[str, Any]]:
    return list_results(limit)
