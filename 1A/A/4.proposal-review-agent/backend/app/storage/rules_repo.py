"""Rules in the relational store. Every change is versioned in `rule_versions` (audit)."""

from __future__ import annotations

import re
import uuid
from typing import Literal

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.domain.models import Rule, RuleIn, RuleStatus, RuleUpdate, utcnow
from app.storage.sql import RuleRow, RuleVersionRow


class RuleConflict(ValueError):
    pass


def _to_rule(row: RuleRow) -> Rule:
    return Rule.model_validate(row, from_attributes=True)


def code_prefix(category: str) -> str:
    return re.sub(r"[^A-Z]", "", category.upper())[:6] or "GEN"


def normalize_code(code: str) -> str:
    return re.sub(r"\s+", "-", code.strip().upper())


class SqlRuleRepository:
    def __init__(self, sessionmaker: async_sessionmaker) -> None:
        self._sm = sessionmaker

    async def list(
        self,
        *,
        category: str | None = None,
        severity: str | None = None,
        status: str | None = RuleStatus.ACTIVE,
        q: str | None = None,
        limit: int = 500,
    ) -> list[Rule]:
        stmt = select(RuleRow).order_by(RuleRow.code).limit(limit)
        if category:
            stmt = stmt.where(func.lower(RuleRow.category) == category.lower())
        if severity:
            stmt = stmt.where(RuleRow.severity == severity.lower())
        if status:
            stmt = stmt.where(RuleRow.status == status)
        if q:
            like = f"%{q.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(RuleRow.title).like(like),
                    func.lower(RuleRow.statement).like(like),
                    func.lower(RuleRow.code).like(like),
                )
            )
        async with self._sm() as s:
            return [_to_rule(r) for r in (await s.scalars(stmt)).all()]

    async def get(self, code: str) -> Rule | None:
        async with self._sm() as s:
            row = await s.scalar(select(RuleRow).where(RuleRow.code == normalize_code(code)))
            return _to_rule(row) if row else None

    async def get_many(self, codes: list[str]) -> dict[str, Rule]:
        if not codes:
            return {}
        norm = [normalize_code(c) for c in codes]
        async with self._sm() as s:
            rows = (await s.scalars(select(RuleRow).where(RuleRow.code.in_(norm)))).all()
            return {r.code: _to_rule(r) for r in rows}

    async def count(self, status: str = RuleStatus.ACTIVE) -> int:
        async with self._sm() as s:
            return await s.scalar(select(func.count()).where(RuleRow.status == status)) or 0

    async def _next_code(self, s, prefix: str) -> str:
        codes = (
            await s.scalars(select(RuleRow.code).where(RuleRow.code.like(f"{prefix}-%")))
        ).all()
        nums = [int(m.group(1)) for c in codes if (m := re.fullmatch(rf"{prefix}-(\d+)", c))]
        return f"{prefix}-{(max(nums) + 1) if nums else 1:03d}"

    async def create(
        self, data: RuleIn, actor: str, *, on_conflict: Literal["error", "renumber"] = "error"
    ) -> Rule:
        async with self._sm() as s, s.begin():
            code = normalize_code(data.code) if data.code else ""
            if code and await s.scalar(select(RuleRow.id).where(RuleRow.code == code)):
                if on_conflict == "error":
                    raise RuleConflict(f"rule {code} already exists")
                code = await self._next_code(s, code.rsplit("-", 1)[0])
            if not code:
                code = await self._next_code(s, code_prefix(data.category))
            now = utcnow()
            row = RuleRow(
                id=str(uuid.uuid4()),
                **data.model_dump(exclude={"code"}),
                code=code,
                version=1,
                created_by=actor,
                created_at=now,
                updated_at=now,
            )
            s.add(row)
            await s.flush()
            rule = _to_rule(row)
            s.add(self._version_row(rule, actor, "created"))
            return rule

    async def update(self, code: str, patch: RuleUpdate, actor: str) -> Rule | None:
        async with self._sm() as s, s.begin():
            row = await s.scalar(select(RuleRow).where(RuleRow.code == normalize_code(code)))
            if row is None:
                return None
            changes = patch.model_dump(exclude_none=True, exclude={"change_note"})
            if not changes:
                return _to_rule(row)
            for field, value in changes.items():
                setattr(row, field, value)
            row.version += 1
            row.updated_at = utcnow()
            await s.flush()
            rule = _to_rule(row)
            s.add(self._version_row(rule, actor, patch.change_note or ", ".join(changes)))
            return rule

    async def versions(self, code: str) -> list[dict]:
        async with self._sm() as s:
            rows = (
                await s.scalars(
                    select(RuleVersionRow)
                    .where(RuleVersionRow.rule_code == normalize_code(code))
                    .order_by(RuleVersionRow.version)
                )
            ).all()
            return [
                {
                    "version": r.version,
                    "changed_by": r.changed_by,
                    "change_note": r.change_note,
                    "changed_at": r.changed_at,
                    "snapshot": r.snapshot,
                }
                for r in rows
            ]

    @staticmethod
    def _version_row(rule: Rule, actor: str, note: str) -> RuleVersionRow:
        return RuleVersionRow(
            rule_code=rule.code,
            version=rule.version,
            snapshot=rule.model_dump(mode="json"),
            changed_by=actor,
            change_note=note,
        )
