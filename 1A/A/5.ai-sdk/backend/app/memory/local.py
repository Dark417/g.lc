"""SQLite long-term memory.

# ILLUSTRATION: verbatim facts + keyword-overlap scoring. No extraction, no embeddings.
# PRODUCTION: a managed memory service that *extracts* and consolidates facts from
# conversations: AgentCore Memory (app/memory/agentcore.py) or Vertex Memory Bank
# (app/memory/vertex_bank.py).
"""

import re
import time
from pathlib import Path

import aiosqlite

from app.memory.base import MemoryRecord

_WORD = re.compile(r"[a-z0-9]+")


def _stem(word: str) -> str:
    for suffix in ("ing", "es", "ed", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def _words(text: str) -> set[str]:
    return {_stem(w) for w in _WORD.findall(text.lower()) if len(w) > 2}


class SqliteMemory:
    name = "local"

    def __init__(self, path: Path):
        self.path = str(path)
        self._init = False

    async def _db(self) -> aiosqlite.Connection:
        db = await aiosqlite.connect(self.path)
        if not self._init:
            await db.execute(
                "CREATE TABLE IF NOT EXISTS memories ("
                "id INTEGER PRIMARY KEY, user_id TEXT, session_id TEXT, text TEXT, created REAL)"
            )
            await db.commit()
            self._init = True
        return db

    async def add(self, user_id: str, text: str, session_id: str) -> str:
        db = await self._db()
        try:
            cur = await db.execute(
                "INSERT INTO memories(user_id, session_id, text, created) VALUES (?,?,?,?)",
                (user_id, session_id, text, time.time()),
            )
            await db.commit()
            return str(cur.lastrowid)
        finally:
            await db.close()

    async def search(self, user_id: str, query: str, k: int = 5) -> list[MemoryRecord]:
        db = await self._db()
        try:
            rows = await (
                await db.execute(
                    "SELECT text, session_id FROM memories WHERE user_id=? ORDER BY created DESC",
                    (user_id,),
                )
            ).fetchall()
        finally:
            await db.close()
        q = _words(query)
        scored = []
        for text, session_id in rows:
            overlap = len(q & _words(text))
            if overlap or not q:
                scored.append(MemoryRecord(text=text, score=float(overlap), source=session_id))
        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[:k]
