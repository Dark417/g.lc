from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse, Response

from app.api.deps import AdminDep, ContainerDep, IdentityDep
from app.domain.models import DocumentRecord, ProposedRule
from app.rag.parsers import PARSERS, UnsupportedFormat, format_of

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.get("", response_model=list[DocumentRecord])
async def list_documents(
    _: IdentityDep, c: ContainerDep, category: str | None = None
) -> list[DocumentRecord]:
    return await c.docs.list(category=category)


@router.get("/{doc_id}", response_model=DocumentRecord)
async def get_document(doc_id: str, _: IdentityDep, c: ContainerDep) -> DocumentRecord:
    if doc := await c.docs.get(doc_id):
        return doc
    raise HTTPException(404, "document not found")


@router.get("/{doc_id}/text")
async def document_text(doc_id: str, _: IdentityDep, c: ContainerDep) -> Response:
    doc = await c.docs.get(doc_id)
    if doc is None or doc.status != "ready":
        raise HTTPException(404, "document not found or not ready")
    return Response(await c.ingestion.text_of(doc), media_type="text/plain; charset=utf-8")


@router.get("/{doc_id}/download")
async def download(doc_id: str, _: IdentityDep, c: ContainerDep) -> Response:
    doc = await c.docs.get(doc_id)
    if doc is None:
        raise HTTPException(404, "document not found")
    return Response(
        await c.ingestion.original_of(doc),
        media_type=doc.mime_type,
        headers={"Content-Disposition": f'attachment; filename="{doc.filename}"'},
    )


@router.post("", response_model=DocumentRecord, status_code=201)
async def upload(
    admin: AdminDep,
    c: ContainerDep,
    background: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(""),
    category: str = Form(""),
    tags: str = Form(""),
):
    filename = file.filename or "upload"
    if format_of(filename) not in PARSERS:
        raise HTTPException(415, f"unsupported format; supported: {', '.join(PARSERS)}")
    data = await file.read()
    kwargs = dict(
        actor=admin.user_id,
        title=title,
        category=category,
        tags=[t.strip() for t in tags.split(",") if t.strip()],
    )
    if len(data) > c.settings.sync_ingest_max_mb * 1024 * 1024:
        # Large file: accept now, process after the response. PRODUCTION: Cloud Run job / Pub/Sub.
        background.add_task(c.ingestion.ingest, data, filename, **kwargs)
        return JSONResponse({"status": "processing", "filename": filename}, status_code=202)
    try:
        return await c.ingestion.ingest(data, filename, **kwargs)
    except UnsupportedFormat as e:
        raise HTTPException(422, str(e)) from e


@router.delete("/{doc_id}", status_code=204)
async def delete_document(doc_id: str, _: AdminDep, c: ContainerDep) -> Response:
    if not await c.ingestion.delete(doc_id):
        raise HTTPException(404, "document not found")
    return Response(status_code=204)


@router.post("/{doc_id}/propose-rules", response_model=list[ProposedRule])
async def propose_rules(doc_id: str, _: AdminDep, c: ContainerDep) -> list[ProposedRule]:
    """Extract candidate rules. Nothing is saved; approve via POST /api/v1/rules/bulk."""
    doc = await c.docs.get(doc_id)
    if doc is None or doc.status != "ready":
        raise HTTPException(404, "document not found or not ready")
    return await c.ingestion.propose_rules(doc)
