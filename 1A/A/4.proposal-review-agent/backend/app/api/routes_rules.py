from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.deps import AdminDep, ContainerDep, IdentityDep
from app.domain.models import Rule, RuleIn, RuleUpdate
from app.services.rule_extraction import parse_rules_file
from app.storage.rules_repo import RuleConflict

router = APIRouter(prefix="/api/v1/rules", tags=["rules"])


@router.get("", response_model=list[Rule])
async def list_rules(
    _: IdentityDep,
    c: ContainerDep,
    category: str | None = None,
    severity: str | None = None,
    status: str | None = "active",
    q: str | None = None,
) -> list[Rule]:
    return await c.rules.list(category=category, severity=severity, status=status or None, q=q)


@router.get("/{code}", response_model=Rule)
async def get_rule(code: str, _: IdentityDep, c: ContainerDep) -> Rule:
    if rule := await c.rules.get(code):
        return rule
    raise HTTPException(404, f"rule {code} not found")


@router.get("/{code}/versions")
async def rule_versions(code: str, _: IdentityDep, c: ContainerDep) -> list[dict]:
    return await c.rules.versions(code)


@router.post("", response_model=Rule, status_code=201)
async def create_rule(body: RuleIn, admin: AdminDep, c: ContainerDep) -> Rule:
    try:
        return await c.rule_service.create(body, admin.user_id)
    except RuleConflict as e:
        raise HTTPException(409, str(e)) from e


@router.post("/bulk", response_model=list[Rule], status_code=201)
async def create_rules(body: list[RuleIn], admin: AdminDep, c: ContainerDep) -> list[Rule]:
    """Used to approve proposed rules. Colliding codes are renumbered, never overwritten."""
    rules = await c.rule_service.create_many(body, admin.user_id)
    for r in rules:  # link back to the source document
        if r.source_document_id and (doc := await c.docs.get(r.source_document_id)):
            doc.extracted_rule_codes = sorted({*doc.extracted_rule_codes, r.code})
            await c.docs.upsert(doc)
    return rules


@router.post("/import", response_model=list[Rule], status_code=201)
async def import_rules(
    admin: AdminDep, c: ContainerDep, file: UploadFile = File(...)
) -> list[Rule]:
    """Import a .csv or .json rule table (columns: code,title,statement,severity,category,...)."""
    try:
        items = parse_rules_file(await file.read(), file.filename or "rules.csv")
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    return await c.rule_service.create_many(items, admin.user_id)


@router.patch("/{code}", response_model=Rule)
async def update_rule(code: str, body: RuleUpdate, admin: AdminDep, c: ContainerDep) -> Rule:
    if rule := await c.rule_service.update(code, body, admin.user_id):
        return rule
    raise HTTPException(404, f"rule {code} not found")


@router.delete("/{code}", response_model=Rule)
async def retire_rule(code: str, admin: AdminDep, c: ContainerDep, reason: str = "") -> Rule:
    """Soft delete: status -> retired, embedding removed, history kept."""
    if rule := await c.rule_service.retire(code, admin.user_id, reason):
        return rule
    raise HTTPException(404, f"rule {code} not found")
