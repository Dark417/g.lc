"""Long-term memory, built by hand: extract -> consolidate -> retrieve -> inject.

Two ways memories get written, and this project shows both:
  agent-directed   the model calls `remember` (app/tools/knowledge.py): explicit, sparse
  system-directed  after each turn we ask a model to extract durable facts (this module):
                   automatic, what AgentCore strategies and Vertex Memory Bank do as a service

Consolidation is the hard part managed services sell: without it memory fills with duplicates and
contradictions ("lives in Paris", "moved to Berlin"). Ours: embed the new fact, find the most
similar existing one; above a threshold it *replaces* it (newest wins, version bumped), else insert.

# ILLUSTRATION: hashing embeddings + SQLite + cosine in Python.
# PRODUCTION: real embeddings + pgvector / OpenSearch, or the managed services (bedrock / vertex).
"""

import json
import math
import re
import time
from collections.abc import Awaitable, Callable
from pathlib import Path

import aiosqlite

from app.rag.local import HashingEmbedder

EXTRACT_MARKER = "[diy:extract]"
EXTRACT_PROMPT = (
    f"{EXTRACT_MARKER} Extract durable facts about the user (identity, preferences, environment, "
    "goals) from the exchange. Ignore questions and small talk. Reply with only JSON: "
    '{"facts": ["...", "..."]} or {"facts": []}.'
)


def _cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b, strict=True)) / (
        (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))) or 1.0
    )


class FactStore:
    def __init__(self, path: Path, update_threshold: float = 0.6):
        self.path = str(path)
        self.embedder = HashingEmbedder()
        self.update_threshold = update_threshold
        self._ready = False

    async def _db(self) -> aiosqlite.Connection:
        db = await aiosqlite.connect(self.path)
        if not self._ready:
            await db.execute(
                "CREATE TABLE IF NOT EXISTS facts (id INTEGER PRIMARY KEY, user_id TEXT, text TEXT, "
                "embedding TEXT, version INTEGER, source_session TEXT, updated REAL)"
            )
            await db.commit()
            self._ready = True
        return db

    async def _all(self, user_id: str) -> list[tuple]:
        db = await self._db()
        try:
            return await (
                await db.execute(
                    "SELECT id, text, embedding, version, source_session, updated FROM facts WHERE user_id=?",
                    (user_id,),
                )
            ).fetchall()
        finally:
            await db.close()

    async def consolidate(self, user_id: str, fact: str, session_id: str) -> dict:
        vec = self.embedder.embed(fact)
        best, best_score = None, 0.0
        for row in await self._all(user_id):
            score = _cosine(vec, json.loads(row[2]))
            if score > best_score:
                best, best_score = row, score
        db = await self._db()
        try:
            if best is not None and best[1].strip().lower() == fact.strip().lower():
                return {"op": "noop", "fact": fact}
            if best is not None and best_score >= self.update_threshold:
                await db.execute(
                    "UPDATE facts SET text=?, embedding=?, version=version+1, source_session=?, updated=? WHERE id=?",
                    (fact, json.dumps(vec), session_id, time.time(), best[0]),
                )
                await db.commit()
                return {
                    "op": "update",
                    "fact": fact,
                    "replaced": best[1],
                    "similarity": round(best_score, 3),
                }
            await db.execute(
                "INSERT INTO facts (user_id, text, embedding, version, source_session, updated) VALUES (?,?,?,?,?,?)",
                (user_id, fact, json.dumps(vec), 1, session_id, time.time()),
            )
            await db.commit()
            return {"op": "insert", "fact": fact}
        finally:
            await db.close()

    async def search(
        self, user_id: str, query: str, k: int = 5, min_score: float = 0.05
    ) -> list[dict]:
        vec = self.embedder.embed(query)
        scored = [
            {
                "text": r[1],
                "score": round(_cosine(vec, json.loads(r[2])), 3),
                "version": r[3],
                "source": r[4],
            }
            for r in await self._all(user_id)
        ]
        hits = [s for s in scored if s["score"] >= min_score] if query else scored
        return sorted(hits, key=lambda s: s["score"], reverse=True)[:k]

    async def delete_user(self, user_id: str) -> None:
        db = await self._db()
        try:
            await db.execute("DELETE FROM facts WHERE user_id=?", (user_id,))
            await db.commit()
        finally:
            await db.close()


def parse_facts(text: str) -> list[str]:
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        return []
    try:
        facts = json.loads(match.group(0)).get("facts", [])
    except ValueError:
        return []
    return [f.strip() for f in facts if isinstance(f, str) and f.strip()][:5]


Complete = Callable[[str, list[dict]], Awaitable[str]]


async def extract_and_consolidate(
    store: FactStore, complete: Complete, user_id: str, session_id: str, turn_messages: list[dict]
) -> list[dict]:
    transcript = "\n".join(
        f"{m['role']}: {m['content'] if isinstance(m['content'], str) else ' '.join(b.get('text', '') for b in m['content'] if isinstance(b, dict))}"
        for m in turn_messages
    )
    facts = parse_facts(await complete(EXTRACT_PROMPT, [{"role": "user", "content": transcript}]))
    return [await store.consolidate(user_id, f, session_id) for f in facts]
