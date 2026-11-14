"""Every verdict is persisted with the rule versions it used, so it can be reproduced later."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.domain.verdicts import Verdict
from app.storage.sql import AssessmentRow


class SqlAssessmentRepository:
    def __init__(self, sessionmaker: async_sessionmaker) -> None:
        self._sm = sessionmaker

    async def save(
        self,
        verdict: Verdict,
        *,
        proposal: str,
        user_id: str,
        session_id: str,
        rule_versions: dict[str, int],
        model: str,
    ) -> str:
        assessment_id = str(uuid.uuid4())
        async with self._sm() as s, s.begin():
            s.add(
                AssessmentRow(
                    id=assessment_id,
                    user_id=user_id,
                    session_id=session_id,
                    proposal=proposal,
                    verdict=verdict.verdict,
                    summary=verdict.summary,
                    findings=[f.model_dump(mode="json") for f in verdict.findings],
                    rule_versions=rule_versions,
                    model=model,
                )
            )
        return assessment_id

    async def list(self, *, user_id: str | None, limit: int = 50) -> list[dict]:
        stmt = select(AssessmentRow).order_by(AssessmentRow.created_at.desc()).limit(limit)
        if user_id is not None:
            stmt = stmt.where(AssessmentRow.user_id == user_id)
        async with self._sm() as s:
            return [
                {
                    "id": r.id,
                    "user_id": r.user_id,
                    "session_id": r.session_id,
                    "proposal": r.proposal,
                    "verdict": r.verdict,
                    "summary": r.summary,
                    "created_at": r.created_at,
                }
                for r in (await s.scalars(stmt)).all()
            ]
