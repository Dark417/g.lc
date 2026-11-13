"""Thin REST adapter, mounted at /customization by app.main when "customization" is in A_ENABLED.

- Read-only and validate routes only: starting jobs or buying provisioned throughput costs money, so those
  calls stay in infra.py for deliberate, scripted use (never one HTTP click away).
- The showcase is built lazily on first request: importing this module makes no AWS call.
"""

from dataclasses import asdict
from functools import lru_cache
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.a01_02_customization.domain import DatasetFormat, TrainingExample, validate_jsonl, write_jsonl
from app.a01_02_customization.infra import CustomizationError, CustomizationShowcase

router = APIRouter()


@lru_cache
def get_showcase() -> CustomizationShowcase:
    return CustomizationShowcase()


Showcase = Annotated[CustomizationShowcase, Depends(get_showcase)]


class Example(BaseModel):
    prompt: str = Field(min_length=1)
    completion: str = Field(min_length=1)
    system: str = ""


class DatasetRequest(BaseModel):
    format: DatasetFormat = DatasetFormat.CONVERSATION
    examples: list[Example] = Field(min_length=1)


class PromptRequest(BaseModel):
    prompt: str = Field(min_length=1)


@router.post("/dataset/preview")
def dataset_preview(body: DatasetRequest, showcase: Showcase) -> dict[str, Any]:
    """Pure: render JSONL in the chosen format and validate it (no AWS call)."""
    data = write_jsonl((TrainingExample(e.prompt, e.completion, e.system) for e in body.examples), body.format)
    report = validate_jsonl(data, body.format, showcase.settings.max_record_chars)
    return {"jsonl": data.decode("utf-8"), "report": asdict(report), "ok": report.ok}


@router.get("/base-models")
def base_models(showcase: Showcase, customization: str = "FINE_TUNING") -> list[dict[str, Any]]:
    return showcase.list_customizable_models(customization)


@router.get("/custom-models")
def custom_models(showcase: Showcase) -> list[dict[str, str]]:
    return showcase.list_custom_models()


@router.post("/converse")
def converse(body: PromptRequest, showcase: Showcase) -> dict[str, Any]:
    try:
        return showcase.converse_custom(body.prompt)
    except CustomizationError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
