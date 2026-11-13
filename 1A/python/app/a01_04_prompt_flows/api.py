"""Thin REST adapter, mounted at /flows by app.main when "flows" is in A_ENABLED.

- POST /invoke runs the configured alias (A_FLOWS_FLOW_ALIAS_ID); deploy endpoints mirror the lifecycle.
- The showcase is built lazily on first request: importing this module makes no AWS call.
"""

from dataclasses import asdict
from functools import lru_cache
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.a01_04_prompt_flows.domain import build_summary_flow
from app.a01_04_prompt_flows.infra import FlowError, FlowsShowcase

router = APIRouter()


@lru_cache
def get_showcase() -> FlowsShowcase:
    return FlowsShowcase()


Showcase = Annotated[FlowsShowcase, Depends(get_showcase)]


class InvokeRequest(BaseModel):
    document: str = Field(min_length=1, max_length=50_000)
    alias_id: str | None = None


class CreateRequest(BaseModel):
    name: str = Field(pattern=r"^([0-9a-zA-Z][_-]?){1,100}$")


class ReleaseRequest(BaseModel):
    release_id: str = Field(min_length=1)
    alias_id: str | None = None  # move this alias to the new version; None -> create alias "live"


@router.get("/definition")
def definition(showcase: Showcase) -> dict[str, Any]:
    return build_summary_flow(showcase.settings.model())  # pure: no AWS call


@router.post("/validate")
def validate(showcase: Showcase) -> list[dict[str, Any]]:
    return showcase.validate_definition()


@router.post("")
def create(body: CreateRequest, showcase: Showcase) -> dict[str, str]:
    return showcase.create_flow(body.name)


@router.post("/{flow_id}/release")
def release(flow_id: str, body: ReleaseRequest, showcase: Showcase) -> dict[str, str]:
    """prepare -> version -> alias (create or move): one deploy."""
    try:
        showcase.prepare_flow(flow_id)
    except FlowError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    version = showcase.create_flow_version(flow_id, body.release_id)
    if body.alias_id:
        showcase.point_alias(body.alias_id, version, flow_id=flow_id)
        return {"version": version, "alias_id": body.alias_id}
    return {"version": version, **showcase.create_flow_alias(version, flow_id=flow_id)}


@router.get("/{flow_id}/versions")
def versions(flow_id: str, showcase: Showcase) -> list[dict[str, str]]:
    return showcase.list_flow_versions(flow_id)


@router.post("/invoke")
def invoke(body: InvokeRequest, showcase: Showcase) -> dict[str, Any]:
    try:
        return asdict(showcase.invoke_flow(body.document, body.alias_id))
    except FlowError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
