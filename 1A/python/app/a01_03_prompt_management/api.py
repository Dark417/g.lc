"""Thin REST adapter, mounted at /prompts by app.main when "prompts" is in A_ENABLED.

- POST /run uses the configured version ARN (A_PROMPTS_PROMPT_VERSION_ARN): production path.
- POST /run-variant renders any variant locally (A/B path).
- The showcase is built lazily on first request: importing this module makes no AWS call.
"""

from dataclasses import asdict
from functools import lru_cache
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.a01_03_prompt_management.domain import MissingVariableError
from app.a01_03_prompt_management.infra import PromptManagementShowcase

router = APIRouter()


@lru_cache
def get_showcase() -> PromptManagementShowcase:
    return PromptManagementShowcase()


Showcase = Annotated[PromptManagementShowcase, Depends(get_showcase)]


class CreateRequest(BaseModel):
    name: str = Field(pattern=r"^([0-9a-zA-Z][_-]?){1,100}$")
    description: str = ""


class VersionRequest(BaseModel):
    description: str = ""
    release_id: str = Field(min_length=1, description="Idempotency: same release_id -> same version")


class RunRequest(BaseModel):
    variables: dict[str, str]
    prompt_version_arn: str | None = None  # default: A_PROMPTS_PROMPT_VERSION_ARN


class RunVariantRequest(BaseModel):
    variables: dict[str, str]
    version: str = "DRAFT"
    variant: str | None = None


@router.get("")
def list_prompts(showcase: Showcase) -> list[dict[str, str]]:
    return showcase.list_prompts()


@router.post("")
def create_prompt(body: CreateRequest, showcase: Showcase) -> dict[str, Any]:
    return asdict(showcase.create_prompt(body.name, body.description))


@router.get("/{prompt_id}")
def get_prompt(prompt_id: str, showcase: Showcase, version: str | None = None) -> dict[str, Any]:
    return asdict(showcase.get_prompt(prompt_id, version))


@router.get("/{prompt_id}/versions")
def list_versions(prompt_id: str, showcase: Showcase) -> list[dict[str, str]]:
    return showcase.list_versions(prompt_id)


@router.post("/{prompt_id}/versions")
def create_version(prompt_id: str, body: VersionRequest, showcase: Showcase) -> dict[str, Any]:
    return asdict(showcase.create_prompt_version(prompt_id, body.description, body.release_id))


@router.post("/run")
def run(body: RunRequest, showcase: Showcase) -> dict[str, Any]:
    arn = body.prompt_version_arn or showcase.settings.prompt_version_arn
    try:
        return showcase.converse_managed_prompt(arn, body.variables)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@router.post("/{prompt_id}/run-variant")
def run_variant(prompt_id: str, body: RunVariantRequest, showcase: Showcase) -> dict[str, Any]:
    version = None if body.version == "DRAFT" else body.version
    try:
        return showcase.converse_rendered_variant(prompt_id, version or "", body.variant or "", body.variables)
    except (MissingVariableError, KeyError) as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
