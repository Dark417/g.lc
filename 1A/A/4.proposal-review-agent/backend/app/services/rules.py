"""Rule use cases: CRUD + keep the rule embeddings in sync with the relational source of truth."""

from typing import Literal

from app.domain.models import Rule, RuleIn, RuleStatus, RuleUpdate
from app.rag.retriever import Retriever
from app.storage.rules_repo import SqlRuleRepository


class RuleService:
    def __init__(self, repo: SqlRuleRepository, retriever: Retriever) -> None:
        self.repo = repo
        self._retriever = retriever

    async def create(
        self, data: RuleIn, actor: str, *, on_conflict: Literal["error", "renumber"] = "error"
    ) -> Rule:
        rule = await self.repo.create(data, actor, on_conflict=on_conflict)
        if rule.status == RuleStatus.ACTIVE:
            await self._retriever.index_rule(rule)
        return rule

    async def create_many(self, items: list[RuleIn], actor: str) -> list[Rule]:
        return [await self.create(i, actor, on_conflict="renumber") for i in items]

    async def update(self, code: str, patch: RuleUpdate, actor: str) -> Rule | None:
        rule = await self.repo.update(code, patch, actor)
        if rule is None:
            return None
        if rule.status == RuleStatus.ACTIVE:
            await self._retriever.index_rule(rule)
        else:
            await self._retriever.remove_rule(rule.code)
        return rule

    async def retire(self, code: str, actor: str, reason: str = "") -> Rule | None:
        return await self.update(
            code, RuleUpdate(status=RuleStatus.RETIRED, change_note=reason or "retired"), actor
        )

    async def reindex(self) -> int:
        rules = await self.repo.list(status=RuleStatus.ACTIVE, limit=100_000)
        for r in rules:
            await self._retriever.index_rule(r)
        return len(rules)
