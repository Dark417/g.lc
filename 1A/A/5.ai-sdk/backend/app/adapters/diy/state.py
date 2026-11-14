"""Loop state and checkpoints, built by hand.

LoopState is everything needed to continue a conversation *or a half-finished turn*. After every
step the loop writes a Checkpoint (a full snapshot, with a parent pointer). That one decision
gives us, for free:
  recovery     reload the latest checkpoint and continue from its `status`
  time travel  list checkpoints; any of them can be loaded
  fork         copy a checkpoint into a new session (copy-on-write branching)

Stores:
  SqliteCheckpointStore   durable source of truth   # PRODUCTION: Postgres / DynamoDB / Firestore
  CachedCheckpointStore   write-through + read-through Redis copy of the *latest* checkpoint,
                          so the hot path (load latest at the start of each turn) skips the DB.
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Protocol

import aiosqlite

from app.state.cache import CACHE_ERRORS

log = logging.getLogger(__name__)

# The loop's state machine (docs/design/07-state-and-memory.md):
READY, CALL_MODEL, RUN_TOOLS, DONE = "ready", "call_model", "run_tools", "done"


@dataclass
class LoopState:
    session_id: str
    user_id: str
    messages: list[dict] = field(default_factory=list)  # the full conversation: source of truth
    vars: dict[str, Any] = field(default_factory=dict)  # session key-value state
    summary: str = ""  # rolling summary of messages[:summarized_upto] (summary strategy)
    summarized_upto: int = 0
    status: str = READY
    turn: int = 0
    step: int = 0
    pending_tools: list[dict] = field(default_factory=list)  # tool_use blocks not yet run
    tool_results: list[dict] = field(default_factory=list)  # results of this step so far
    usage: dict[str, int] = field(default_factory=dict)

    def add_usage(self, usage: dict[str, int | None]) -> None:
        for k, v in usage.items():
            if isinstance(v, int):
                self.usage[k] = self.usage.get(k, 0) + v


@dataclass
class Checkpoint:
    checkpoint_id: str
    session_id: str
    parent_id: str | None
    label: str  # what just happened: user / model / tool:<name> / tools_done / done / fork
    state: LoopState
    created_at: float = field(default_factory=time.time)

    def meta(self) -> dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "parent_id": self.parent_id,
            "label": self.label,
            "turn": self.state.turn,
            "step": self.state.step,
            "status": self.state.status,
            "messages": len(self.state.messages),
            "created_at": self.created_at,
        }

    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str)

    @classmethod
    def from_json(cls, raw: str) -> Checkpoint:
        data = json.loads(raw)
        data["state"] = LoopState(**data["state"])
        return cls(**data)

    @classmethod
    def of(cls, state: LoopState, label: str, parent_id: str | None) -> Checkpoint:
        cid = f"{state.turn:04d}-{state.step:04d}-{uuid.uuid4().hex[:6]}"
        return cls(
            cid,
            state.session_id,
            parent_id,
            label,
            LoopState(**json.loads(json.dumps(asdict(state)))),
        )


class CheckpointStore(Protocol):
    name: str

    async def put(self, ckpt: Checkpoint) -> None: ...
    async def latest(self, session_id: str) -> Checkpoint | None: ...
    async def get(self, session_id: str, checkpoint_id: str) -> Checkpoint | None: ...
    async def list(self, session_id: str) -> list[Checkpoint]: ...
    async def delete(self, session_id: str) -> None: ...


class SqliteCheckpointStore:
    name = "sqlite"

    def __init__(self, path: Path):
        self.path = str(path)
        self._ready = False

    async def _db(self) -> aiosqlite.Connection:
        db = await aiosqlite.connect(self.path)
        if not self._ready:
            await db.execute(
                "CREATE TABLE IF NOT EXISTS checkpoints (session_id TEXT, checkpoint_id TEXT, "
                "created REAL, body TEXT, PRIMARY KEY (session_id, checkpoint_id))"
            )
            await db.commit()
            self._ready = True
        return db

    async def put(self, ckpt: Checkpoint) -> None:
        db = await self._db()
        try:
            await db.execute(
                "INSERT INTO checkpoints VALUES (?,?,?,?)",
                (ckpt.session_id, ckpt.checkpoint_id, ckpt.created_at, ckpt.to_json()),
            )
            await db.commit()
        finally:
            await db.close()

    async def _rows(self, sql: str, args: tuple) -> list[Checkpoint]:
        db = await self._db()
        try:
            rows = await (await db.execute(sql, args)).fetchall()
        finally:
            await db.close()
        return [Checkpoint.from_json(r[0]) for r in rows]

    async def latest(self, session_id: str) -> Checkpoint | None:
        rows = await self._rows(
            "SELECT body FROM checkpoints WHERE session_id=? ORDER BY created DESC, rowid DESC LIMIT 1",
            (session_id,),
        )
        return rows[0] if rows else None

    async def get(self, session_id: str, checkpoint_id: str) -> Checkpoint | None:
        rows = await self._rows(
            "SELECT body FROM checkpoints WHERE session_id=? AND checkpoint_id=?",
            (session_id, checkpoint_id),
        )
        return rows[0] if rows else None

    async def list(self, session_id: str) -> list[Checkpoint]:
        return await self._rows(
            "SELECT body FROM checkpoints WHERE session_id=? ORDER BY created DESC, rowid DESC",
            (session_id,),
        )

    async def delete(self, session_id: str) -> None:
        db = await self._db()
        try:
            await db.execute("DELETE FROM checkpoints WHERE session_id=?", (session_id,))
            await db.commit()
        finally:
            await db.close()


class CachedCheckpointStore:
    """Redis in front of the durable store, for the one read that happens every turn: latest().

    Write-through: durable first (it is the source of truth), then the cache.
    Read-through:  cache hit -> done; miss -> durable, then fill the cache.
    Fail open:     any cache error falls back to the durable store.
    """

    name = "sqlite+redis"

    def __init__(self, durable: CheckpointStore, redis, ttl_s: int = 3600):
        self.durable, self.redis, self.ttl_s = durable, redis, ttl_s
        self.hits = self.misses = 0

    @staticmethod
    def _key(session_id: str) -> str:
        return f"diy:ckpt:{session_id}"

    async def put(self, ckpt: Checkpoint) -> None:
        await self.durable.put(ckpt)
        try:
            await self.redis.set(self._key(ckpt.session_id), ckpt.to_json(), ex=self.ttl_s)
        except CACHE_ERRORS as e:
            log.warning("checkpoint cache write failed: %s", e)

    async def latest(self, session_id: str) -> Checkpoint | None:
        try:
            raw = await self.redis.get(self._key(session_id))
        except CACHE_ERRORS as e:
            log.warning("checkpoint cache read failed: %s", e)
            raw = None
        if raw:
            self.hits += 1
            return Checkpoint.from_json(raw)
        self.misses += 1
        ckpt = await self.durable.latest(session_id)
        if ckpt is not None:
            try:
                await self.redis.set(self._key(session_id), ckpt.to_json(), ex=self.ttl_s)
            except CACHE_ERRORS:
                pass
        return ckpt

    async def get(self, session_id: str, checkpoint_id: str) -> Checkpoint | None:
        return await self.durable.get(session_id, checkpoint_id)

    async def list(self, session_id: str) -> list[Checkpoint]:
        return await self.durable.list(session_id)

    async def delete(self, session_id: str) -> None:
        await self.durable.delete(session_id)
        try:
            await self.redis.delete(self._key(session_id))
        except CACHE_ERRORS:
            pass
