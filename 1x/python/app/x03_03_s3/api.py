"""Thin FastAPI adapter under /s3 (mounted by app.main when "s3" is in X_ENABLED)."""

from typing import Any

from fastapi import APIRouter, Body, HTTPException, Response
from fastapi.responses import JSONResponse

from app.x03_03_s3 import infra
from app.x03_03_s3.domain import ListingPage, ObjectInfo

router = APIRouter()


@router.get("/head")
def head(key: str) -> ObjectInfo:
    return infra.head(key)


@router.get("/list")
def list_folder(prefix: str = "") -> ListingPage:
    return infra.list_folder(prefix)


@router.get("/presign-get")
def presign_get(key: str, seconds: int = 300) -> dict[str, str]:
    if not 1 <= seconds <= 3600:
        raise HTTPException(status_code=422, detail="seconds must be 1..3600")
    return {"url": infra.presign_get(key, seconds)}


@router.put("/create-only")
def create_only(key: str, body: bytes = Body(...)) -> Response:
    # 201 when created, 409 when the key already exists (S3 answered 412).
    r = infra.put_if_absent(key, body)
    payload: dict[str, Any] = {"created": r.created, "etag": r.etag, "version_id": r.version_id}
    return JSONResponse(payload, status_code=201 if r.created else 409)
