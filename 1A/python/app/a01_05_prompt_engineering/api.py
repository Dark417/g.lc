"""Thin REST adapter, mounted at /prompting by app.main when "prompting" is in A_ENABLED.

- /render, /scan, /schema are pure logic (no AWS call): handy to inspect prompts before spending tokens.
- Model-backed endpoints build the showcase lazily on first request.
"""

from functools import lru_cache
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.a01_05_prompt_engineering.domain import (
    InjectionDetector,
    Invoice,
    TemplateError,
    fence_untrusted,
    render_template,
)
from app.a01_05_prompt_engineering.infra import PromptingShowcase, StructuredOutputError, schema_of

router = APIRouter()


@lru_cache
def get_showcase() -> PromptingShowcase:
    return PromptingShowcase()


Showcase = Annotated[PromptingShowcase, Depends(get_showcase)]


class RenderRequest(BaseModel):
    template: str = Field(min_length=1)
    variables: dict[str, str] = Field(default_factory=dict)


class TextRequest(BaseModel):
    text: str = Field(min_length=1, max_length=50_000)


class ExtractRequest(TextRequest):
    method: str = Field(default="tool", pattern="^(tool|native|repair|prefill)$")


class Doc(BaseModel):
    source: str
    text: str


class RagRequest(BaseModel):
    question: str = Field(min_length=1)
    documents: list[Doc] = Field(min_length=1, max_length=20)


# ---------------------------------------------------------------- pure logic


@router.post("/render")
def render(body: RenderRequest) -> dict[str, str]:
    try:
        return {"prompt": render_template(body.template, body.variables)}
    except TemplateError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@router.post("/scan")
def scan(body: TextRequest) -> dict[str, Any]:
    report = InjectionDetector().scan(body.text)
    return {"score": report.score, "suspicious": report.suspicious, "matches": report.matches}


@router.post("/fence")
def fence(body: RagRequest) -> dict[str, str]:
    fenced, boundary = fence_untrusted([(d.source, d.text) for d in body.documents])
    return {"boundary": boundary, "fenced": fenced}


@router.get("/schema")
def schema() -> dict[str, Any]:
    return schema_of(Invoice)


# ---------------------------------------------------------------- model-backed


@router.post("/classify")
def classify(body: TextRequest, showcase: Showcase, mode: str = "few-shot") -> dict[str, str]:
    label = showcase.classify_zero_shot(body.text) if mode == "zero-shot" else showcase.classify_few_shot(body.text)
    return {"mode": mode, "label": label}


@router.post("/cot")
def cot(body: TextRequest, showcase: Showcase) -> dict[str, str | None]:
    return showcase.chain_of_thought(body.text)


@router.post("/temperatures")
def temperatures(body: TextRequest, showcase: Showcase) -> dict[str, str]:
    return showcase.sample_at_temperatures(body.text, [0.0, 0.5, 1.0])


@router.post("/extract")
def extract(body: ExtractRequest, showcase: Showcase) -> dict[str, Any]:
    method = {
        "tool": showcase.extract_with_tool,
        "native": showcase.extract_with_native_schema,
        "repair": showcase.extract_with_repair,
        "prefill": showcase.extract_with_prefill,
    }[body.method]
    try:
        return {"method": body.method, "invoice": method(body.text).model_dump(mode="json")}
    except StructuredOutputError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@router.post("/rag-answer")
def rag_answer(body: RagRequest, showcase: Showcase) -> dict[str, Any]:
    return showcase.answer_from_documents(body.question, [(d.source, d.text) for d in body.documents])
