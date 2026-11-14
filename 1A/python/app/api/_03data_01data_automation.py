"""REST adapter mounted at /bda."""

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.service import _03data_01data_automation as service

router = APIRouter()


class ExtractRequest(BaseModel):
    key: str = Field(min_length=1, description="object key under bda/input/")
    run_id: str | None = Field(default=None, description="idempotency token; same id, same job")


@router.post("/extract")
def extract(body: ExtractRequest) -> dict[str, Any]:
    return service.extract_invoice(body.key, body.run_id)
