"""Health, identity, and direct assessment (used by the MCP server and the portal's quick check)."""

import logging

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.api.deps import ContainerDep, IdentityDep
from app.domain.verdicts import Verdict
from app.rag.retriever import source_label

router = APIRouter()
log = logging.getLogger(__name__)


@router.get("/healthz", tags=["health"])
async def healthz() -> dict:
    return {"status": "ok"}


@router.get("/readyz", tags=["health"])
async def readyz(c: ContainerDep) -> dict:
    try:
        await c.ready()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"database unavailable: {e}") from e
    return {"status": "ready"}


@router.get("/api/v1/me", tags=["auth"])
async def me(identity: IdentityDep, c: ContainerDep) -> dict:
    return {
        "user_id": identity.user_id,
        "role": identity.role,
        "kind": identity.kind,
        "adk_web": c.settings.enable_adk_web,
        "auth_mode": c.settings.auth_mode,
    }


class AssessRequest(BaseModel):
    proposal: str = Field(min_length=5, max_length=20_000)
    context: str = Field(default="", max_length=40_000)


@router.post("/api/v1/assess", response_model=Verdict, tags=["assess"])
async def assess(body: AssessRequest, identity: IdentityDep, c: ContainerDep) -> Verdict:
    try:
        return await c.assessment.assess(
            body.proposal, context=body.context, user_id=identity.user_id
        )
    except Exception as e:  # model/credential/quota errors: tell the caller, don't 500
        log.exception("assessment failed")
        raise HTTPException(502, f"assessment model unavailable: {e}") from e


@router.get("/api/v1/assessments", tags=["assess"])
async def assessments(
    identity: IdentityDep, c: ContainerDep, all: bool = False, limit: int = 50
) -> list[dict]:
    user = None if (all and identity.is_admin) else identity.user_id
    return await c.assessments.list(user_id=user, limit=min(limit, 500))


@router.get("/api/v1/search/rules", tags=["search"])
async def search_rules(
    _: IdentityDep, c: ContainerDep, q: str = Query(min_length=2), k: int = 8
) -> list[dict]:
    """Semantic search over active rules (used by the MCP server)."""
    hits = await c.retriever.search_rules(q, k=min(k, 50))
    found = await c.rules.get_many([h.ref_id for h in hits])
    return [
        {"score": round(h.score, 3), **found[h.ref_id].model_dump(mode="json")}
        for h in hits
        if h.ref_id in found and found[h.ref_id].status == "active"
    ]


@router.get("/api/v1/search/documents", tags=["search"])
async def search_documents(
    _: IdentityDep, c: ContainerDep, q: str = Query(min_length=2), k: int = 6
) -> list[dict]:
    """Semantic search over document passages, with citation labels."""
    hits = await c.retriever.search_documents(q, k=min(k, 50))
    return [
        {
            "document_id": h.ref_id,
            "source": source_label(h.metadata),
            "score": round(h.score, 3),
            "text": h.text,
        }
        for h in hits
    ]
