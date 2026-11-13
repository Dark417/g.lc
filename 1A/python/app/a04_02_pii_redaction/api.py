"""Thin REST adapter, mounted at /pii by app.main when "pii" is in A_ENABLED.

- Detection responses return types, scores, offsets: never the matched values.
- Vault and policy are built lazily on first request: importing this module makes no AWS call.
"""

from dataclasses import asdict
from functools import lru_cache
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.a04_02_pii_redaction import infra, service
from app.a04_02_pii_redaction.config import get_pii_settings
from app.a04_02_pii_redaction.domain import RedactionPolicy, default_policy
from app.shared.config import get_settings

router = APIRouter()


@lru_cache
def get_policy() -> RedactionPolicy:
    return default_policy(get_pii_settings().min_score)


@lru_cache
def get_vault() -> infra.InMemoryPseudonymVault:
    return infra.vault_from_settings()


Policy = Annotated[RedactionPolicy, Depends(get_policy)]
Vault = Annotated[infra.InMemoryPseudonymVault, Depends(get_vault)]


class TextRequest(BaseModel):
    text: str = Field(min_length=1)


class StreamRequest(BaseModel):
    chunks: list[str] = Field(min_length=1)  # simulates model stream deltas


class JobRequest(BaseModel):
    input_key: str = Field(default="", description="key under comprehend/input/; empty = whole prefix")
    mode: str = Field(default="ONLY_REDACTION", pattern="^(ONLY_REDACTION|ONLY_OFFSETS)$")
    mask_mode: str = Field(default="REPLACE_WITH_PII_ENTITY_TYPE", pattern="^(MASK|REPLACE_WITH_PII_ENTITY_TYPE)$")
    client_token: str | None = Field(default=None, max_length=64)


@router.post("/detect")
def detect(body: TextRequest) -> list[dict[str, Any]]:
    return [asdict(e) for e in infra.detect_pii(body.text)]


@router.post("/contains")
def contains(body: TextRequest) -> dict[str, float]:
    return infra.contains_pii(body.text)


@router.post("/redact")
def redact(body: TextRequest, policy: Policy, vault: Vault) -> dict[str, Any]:
    r = infra.redact(body.text, policy, vault)
    if r.blocked:
        raise HTTPException(status_code=422, detail={"blocked_types": list(r.blocked_types)})
    return {"text": r.text, "pii": r.summary(), "skipped_low_score": r.skipped_low_score}


@router.post("/stream")
def stream(body: StreamRequest, policy: Policy, vault: Vault) -> dict[str, Any]:
    redactor = infra.StreamingRedactor(policy, vault)
    emitted = [redactor.feed(c) for c in body.chunks]
    emitted.append(redactor.flush())
    return {"emitted": [e for e in emitted if e], "blocked_types": sorted(redactor.blocked_types)}


@router.post("/jobs")
def start_job(body: JobRequest, policy: Policy) -> dict[str, str]:
    s, base = get_pii_settings(), get_settings()
    in_uri = f"s3://{base.data_bucket}/{s.input_prefix}{body.input_key}"
    out_uri = f"s3://{base.data_bucket}/{s.output_prefix}"
    job_id = infra.start_redaction_job(
        in_uri, out_uri, policy, mode=body.mode, mask_mode=body.mask_mode, client_token=body.client_token
    )
    return {"job_id": job_id}


@router.get("/jobs/{job_id}")
def job(job_id: str) -> dict[str, Any]:
    return infra.describe_job(job_id)


@router.post("/pipeline")
def pipeline(body: TextRequest, policy: Policy, vault: Vault) -> dict[str, Any]:
    return asdict(service.redact_converse_guard(body.text, policy, vault))
