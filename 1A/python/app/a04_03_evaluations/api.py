"""Thin REST adapter, mounted at /evals by app.main when "evals" is in A_ENABLED.

- Job ARNs contain ':' and '/', so they travel as a query parameter (?arn=...), not a path segment.
- Store and service are built lazily on first request: importing this module makes no AWS call.
"""

from dataclasses import asdict
from functools import lru_cache
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.a04_03_evaluations import infra, metrics, service
from app.a04_03_evaluations.domain import EvalCase, EvalJob, GuardrailCase, RagCase

router = APIRouter()


@lru_cache
def get_store() -> infra.InMemoryEvalResultStore:
    return infra.InMemoryEvalResultStore()


@lru_cache
def get_service() -> service.EvalService:
    return service.EvalService(get_store())


Service = Annotated[service.EvalService, Depends(get_service)]


class ModelCaseIn(BaseModel):
    prompt: str = Field(min_length=1)
    reference: str = ""
    category: str = ""


class RagCaseIn(BaseModel):
    prompt: str = Field(min_length=1)
    references: list[str] = []


class ModelEvalRequest(BaseModel):
    dataset_name: str = Field(pattern=r"^[a-z0-9-]{1,48}$")
    judge: bool = True
    cases: list[ModelCaseIn] = Field(min_length=1)


class RagEvalRequest(BaseModel):
    dataset_name: str = Field(pattern=r"^[a-z0-9-]{1,48}$")
    retrieve_only: bool = False
    cases: list[RagCaseIn] = Field(min_length=1)


class GuardrailCaseIn(BaseModel):
    text: str
    source: str = Field(default="INPUT", pattern="^(INPUT|OUTPUT)$")
    expected_blocked: bool
    policy: str = "benign"


class GuardrailEvalRequest(BaseModel):
    run_id: str = Field(min_length=1)
    version: str | None = None  # default A_EVALS_GUARDRAIL_VERSION (DRAFT)
    min_recall: float = Field(default=0.9, ge=0, le=1)
    max_fpr: float = Field(default=0.05, ge=0, le=1)
    cases: list[GuardrailCaseIn] = []  # empty = built-in starter set


class RougeRequest(BaseModel):
    candidate: str
    reference: str


def _job_json(job: EvalJob) -> dict[str, Any]:
    return asdict(job)


@router.post("/jobs/model")
def start_model_eval(body: ModelEvalRequest, svc: Service) -> dict[str, Any]:
    cases = [EvalCase(c.prompt, c.reference, c.category) for c in body.cases]
    return _job_json(svc.start_model_eval(cases, body.dataset_name, body.judge))


@router.post("/jobs/rag")
def start_rag_eval(body: RagEvalRequest, svc: Service) -> dict[str, Any]:
    cases = [RagCase(c.prompt, tuple(c.references)) for c in body.cases]
    return _job_json(svc.start_rag_eval(cases, body.dataset_name, body.retrieve_only))


@router.get("/jobs")
def list_jobs(status: str | None = None) -> list[dict[str, Any]]:
    return infra.list_jobs(status=status)


@router.get("/job")
def job(svc: Service, arn: Annotated[str, Query(min_length=20)]) -> dict[str, Any]:
    return _job_json(svc.refresh(arn))


@router.post("/job/stop")
def stop(arn: Annotated[str, Query(min_length=20)]) -> dict[str, str]:
    infra.stop_job(arn)
    return {"status": "Stopping"}


@router.post("/guardrail")
def guardrail_eval(body: GuardrailEvalRequest, svc: Service) -> dict[str, Any]:
    cases = [GuardrailCase(c.text, c.source, c.expected_blocked, c.policy) for c in body.cases]
    passed, report = svc.guardrail_gate(
        body.run_id, cases or service.DEFAULT_GUARDRAIL_CASES, body.version, body.min_recall, body.max_fpr
    )
    return {
        "passed": passed,
        "version": report.guardrail_version,
        "overall": report.overall.as_dict(),
        "per_policy": {p: m.as_dict() for p, m in report.per_policy.items()},
        "misclassified": report.misclassified,
        "total_units": report.total_units,
        "p95_latency_ms": report.p95_latency_ms(),
    }


@router.get("/guardrail/{run_id}")
def guardrail_report(run_id: str) -> dict[str, Any]:
    report = get_store().get_guardrail_report(run_id)
    if report is None:
        raise HTTPException(status_code=404, detail="unknown run_id")
    return {"overall": report.overall.as_dict(), "per_policy": {p: m.as_dict() for p, m in report.per_policy.items()}}


@router.post("/rouge")
def rouge(body: RougeRequest) -> dict[str, Any]:
    """Local metric mechanics; no AWS call."""
    return {"rouge1": asdict(metrics.rouge_n(body.candidate, body.reference, 1)),
            "rouge2": asdict(metrics.rouge_n(body.candidate, body.reference, 2)),
            "rougeL": asdict(metrics.rouge_l(body.candidate, body.reference))}
