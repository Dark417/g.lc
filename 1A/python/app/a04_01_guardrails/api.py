"""Thin REST adapter, mounted at /guardrails by app.main when "guardrails" is in A_ENABLED.

- Responses never echo PolicyHit.match (the sensitive text itself); only policy, name, action.
- Services are built lazily on first request: importing this module makes no AWS call.
"""

import json
from collections.abc import Iterator
from dataclasses import asdict
from functools import lru_cache
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.a04_01_guardrails import infra, service
from app.a04_01_guardrails.config import get_guardrails_settings
from app.a04_01_guardrails.domain import GuardedReply, GuardrailVerdict, Source, TextBlock, Tier, default_spec

router = APIRouter()


@lru_cache
def get_chat_service() -> service.GuardedChatService:
    return service.GuardedChatService(infra.BedrockGuardrail(), infra.BedrockChatModel())


ChatService = Annotated[service.GuardedChatService, Depends(get_chat_service)]


class ApplyRequest(BaseModel):
    text: str = Field(min_length=1)
    source: Source = Source.INPUT
    version: str | None = None  # DRAFT or a number; default = configured version
    output_scope: str = Field(default="INTERVENTIONS", pattern="^(INTERVENTIONS|FULL)$")


class GroundingRequest(BaseModel):
    passages: list[str] = Field(min_length=1)
    query: str = Field(min_length=1)
    answer: str = Field(min_length=1)


class ChatRequest(BaseModel):
    text: str = Field(min_length=1)
    context: list[str] = []


class StreamRequest(BaseModel):
    text: str = Field(min_length=1)
    mode: str = Field(default="sync", pattern="^(sync|async)$")


class PromoteRequest(BaseModel):
    release_id: str = Field(min_length=1, max_length=256)  # used as clientRequestToken
    description: str = "promoted from DRAFT"


def _verdict_json(v: GuardrailVerdict | None) -> dict[str, Any] | None:
    if v is None:
        return None
    data = asdict(v)
    data["hits"] = [{"policy": h.policy, "name": h.name, "action": h.action, "detected": h.detected} for h in v.hits]
    return data


def _reply_json(r: GuardedReply) -> dict[str, Any]:
    return {
        "text": r.text,
        "stop_reason": r.stop_reason,
        "intervened": r.intervened,
        "input": _verdict_json(r.input_verdict),
        "output": _verdict_json(r.output_verdict),
    }


@router.post("/apply")
def apply(body: ApplyRequest) -> dict[str, Any] | None:
    v = infra.apply_guardrail([TextBlock(body.text)], body.source, body.version, body.output_scope)
    return _verdict_json(v)


@router.post("/grounding")
def grounding(body: GroundingRequest) -> dict[str, Any] | None:
    return _verdict_json(infra.check_grounding(body.passages, body.query, body.answer))


@router.post("/chat")
def chat(body: ChatRequest, svc: ChatService) -> dict[str, Any]:
    """ApplyGuardrail sandwich: works the same for a non-Bedrock model behind ChatModelPort."""
    return _reply_json(svc.chat(body.text, body.context))


@router.post("/converse")
def converse(body: ChatRequest) -> dict[str, Any]:
    """Converse + guardrailConfig, guarding only the tagged user text (+ grounding when context is given)."""
    return _reply_json(infra.converse_guard_user_text_only(body.text, body.context or None))


@router.post("/converse/stream")
def converse_stream(body: StreamRequest) -> StreamingResponse:
    def ndjson() -> Iterator[str]:
        for event in infra.converse_stream_guarded(body.text, body.mode):
            yield json.dumps(event) + "\n"

    return StreamingResponse(ndjson(), media_type="application/x-ndjson")


@router.post("/checks")
def checks(body: ChatRequest) -> dict[str, Any]:
    return infra.invoke_guardrail_checks(body.text)


@router.get("/config")
def config(version: str | None = None) -> dict[str, Any]:
    return infra.get_guardrail(get_guardrails_settings().guardrail_id, version)


@router.get("/list")
def list_all() -> list[dict[str, Any]]:
    return infra.list_guardrails()


@router.get("/versions")
def versions() -> list[str]:
    return infra.list_versions(get_guardrails_settings().guardrail_id)


@router.post("/admin/sdk-guardrail")
def provision() -> dict[str, str]:
    """Create-or-update a-guardrail-sdk from default_spec (same policies as Terraform)."""
    s = get_guardrails_settings()
    spec = default_spec(
        s.sdk_guardrail_name,
        tier=Tier(s.tier),
        guardrail_profile_id=s.guardrail_profile_id,
        kms_key_id=s.kms_key_id,
        ar_policy_arns=(s.ar_policy_arn,) if s.ar_policy_arn else (),
    )
    guardrail_id, version = service.provision_sdk_guardrail(spec)
    return {"guardrail_id": guardrail_id, "version": version}


@router.post("/admin/{guardrail_id}/versions")
def promote(guardrail_id: str, body: PromoteRequest) -> dict[str, str]:
    try:
        version = service.promote_draft(guardrail_id, service.DEFAULT_SMOKE_CASES, body.description, body.release_id)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    return {"guardrail_id": guardrail_id, "version": version}
