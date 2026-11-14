"""SessionRegistry: our session id -> bound target, native ids, and a run lock.

The lock is the pattern from 0.learn/fastapi-bedrock-asyncSessionMemory.py: one agent loop per
session at a time; a concurrent request gets 409 instead of interleaving two loops on one history.

Two implementations, one interface:
  InMemorySessionRegistry  ILLUSTRATION: process memory + asyncio.Lock. One replica only.
  RedisSessionRegistry     records as JSON in Redis + a leased lock (SET NX PX, renewed by a
                           heartbeat, released by compare-and-delete). Any number of replicas.
                           Works on Redis, Valkey, ElastiCache, Memorystore (same protocol).

Conversation *content* is not stored here. It lives in each framework's own store. See
docs/design/07-state-and-memory.md.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass, field
from typing import Any, Protocol

from app.schemas import RunRequest
from app.state.cache import CACHE_ERRORS


class SessionBusy(RuntimeError):
    pass


class SessionMismatch(ValueError):
    pass


class LockUnavailable(RuntimeError):
    """The cache server holding the lock is unreachable. We fail closed (503)."""


@dataclass
class SessionRecord:
    id: str
    user_id: str
    framework: str
    pattern: str
    provider: str
    created_at: float = field(default_factory=time.time)
    turns: int = 0
    last_output: Any = None
    # Framework-native ids or state handles, e.g. {"claude_session_id": "..."} or
    # {"pending_interrupt": True} for LangGraph hitl. Must stay JSON-serialisable.
    native: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> dict[str, Any]:
        return {
            "session_id": self.id,
            "user_id": self.user_id,
            "target": f"{self.framework}:{self.pattern}:{self.provider}",
            "turns": self.turns,
            "created_at": self.created_at,
            "native": {k: v for k, v in self.native.items() if isinstance(v, str | int | bool)},
        }

    @classmethod
    def new(cls, req: RunRequest, session_id: str | None = None) -> SessionRecord:
        return cls(
            id=session_id or req.session_id or uuid.uuid4().hex,
            user_id=req.user_id,
            framework=req.framework,
            pattern=req.pattern,
            provider=req.provider,
        )


def _check_binding(rec: SessionRecord, req: RunRequest) -> None:
    if (rec.framework, rec.pattern, rec.provider) != (req.framework, req.pattern, req.provider):
        raise SessionMismatch(
            f"session {rec.id} is bound to {rec.framework}:{rec.pattern}:{rec.provider}; "
            "start a new session for a different target"
        )
    if rec.user_id != req.user_id:
        raise SessionMismatch(f"session {rec.id} belongs to another user")


class SessionRegistry(Protocol):
    async def get(self, session_id: str) -> SessionRecord | None: ...
    async def list(self, user_id: str | None = None) -> list[SessionRecord]: ...
    async def save(self, rec: SessionRecord) -> None: ...
    async def delete(self, session_id: str) -> None: ...
    async def check(self, req: RunRequest) -> None: ...
    def acquire(self, req: RunRequest) -> contextlib.AbstractAsyncContextManager[SessionRecord]: ...


class InMemorySessionRegistry:
    # ILLUSTRATION: process memory. Correct for one replica only.
    def __init__(self) -> None:
        self._records: dict[str, SessionRecord] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    async def get(self, session_id: str) -> SessionRecord | None:
        return self._records.get(session_id)

    async def list(self, user_id: str | None = None) -> list[SessionRecord]:
        return [r for r in self._records.values() if user_id is None or r.user_id == user_id]

    async def save(self, rec: SessionRecord) -> None:
        self._records[rec.id] = rec
        self._locks.setdefault(rec.id, asyncio.Lock())

    async def delete(self, session_id: str) -> None:
        self._records.pop(session_id, None)
        self._locks.pop(session_id, None)

    async def check(self, req: RunRequest) -> None:
        """Cheap pre-flight check so HTTP can answer 409 before a stream starts."""
        rec = self._records.get(req.session_id or "")
        if rec is None:
            return
        _check_binding(rec, req)
        if self._locks[rec.id].locked():
            raise SessionBusy(f"session {rec.id} is processing a prior request")

    @asynccontextmanager
    async def acquire(self, req: RunRequest) -> AsyncIterator[SessionRecord]:
        await self.check(req)
        rec = self._records.get(req.session_id or "") or SessionRecord.new(req)
        await self.save(rec)
        lock = self._locks[rec.id]
        if lock.locked():  # lost a race after check()
            raise SessionBusy(f"session {rec.id} is processing a prior request")
        async with lock:
            yield rec


# Release only if we still own the lock (a lease may have expired and been taken by another
# replica); extend only if we still own it. Both atomic on the server.
_RELEASE = "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end"
_EXTEND = "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('pexpire', KEYS[1], ARGV[2]) else return 0 end"


class RedisLock:
    """A leased mutex: SET key token NX PX ttl. The holder renews it while working; if the
    holder dies, the lease expires and the session unlocks itself."""

    def __init__(self, redis, key: str, ttl_ms: int):
        self.redis, self.key, self.ttl_ms = redis, key, ttl_ms
        self.token = uuid.uuid4().hex
        self._heartbeat: asyncio.Task | None = None

    async def acquire(self) -> bool:
        ok = await self.redis.set(self.key, self.token, nx=True, px=self.ttl_ms)
        if ok:
            self._heartbeat = asyncio.create_task(self._renew())
        return bool(ok)

    async def _renew(self) -> None:
        while True:
            await asyncio.sleep(self.ttl_ms / 3000)
            if not await self.redis.eval(_EXTEND, 1, self.key, self.token, self.ttl_ms):
                return  # lost the lease; the run continues but can no longer claim exclusivity

    async def release(self) -> None:
        if self._heartbeat:
            self._heartbeat.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._heartbeat
        await self.redis.eval(_RELEASE, 1, self.key, self.token)


class RedisSessionRegistry:
    """Session records + locks in a cache server, shared by every replica."""

    def __init__(self, redis, lock_ttl_s: int = 300, record_ttl_s: int = 30 * 24 * 3600):
        self.redis = redis
        self.lock_ttl_ms = lock_ttl_s * 1000
        self.record_ttl_s = record_ttl_s

    @staticmethod
    def _key(session_id: str) -> str:
        return f"session:{session_id}"

    @staticmethod
    def _lock_key(session_id: str) -> str:
        return f"lock:session:{session_id}"

    async def _call(self, coro):
        try:
            return await coro
        except CACHE_ERRORS as e:
            raise LockUnavailable(f"cache server unavailable: {e}") from e

    async def get(self, session_id: str) -> SessionRecord | None:
        raw = await self._call(self.redis.get(self._key(session_id)))
        return SessionRecord(**json.loads(raw)) if raw else None

    async def list(self, user_id: str | None = None) -> list[SessionRecord]:
        records = []
        async for key in self.redis.scan_iter(match="session:*", count=200):
            raw = await self.redis.get(key)
            if raw:
                rec = SessionRecord(**json.loads(raw))
                if user_id is None or rec.user_id == user_id:
                    records.append(rec)
        return sorted(records, key=lambda r: r.created_at)

    async def save(self, rec: SessionRecord) -> None:
        payload = json.dumps(asdict(rec), default=str)
        await self._call(self.redis.set(self._key(rec.id), payload, ex=self.record_ttl_s))

    async def delete(self, session_id: str) -> None:
        await self._call(self.redis.delete(self._key(session_id), self._lock_key(session_id)))

    async def check(self, req: RunRequest) -> None:
        if not req.session_id:
            return
        rec = await self.get(req.session_id)
        if rec is None:
            return
        _check_binding(rec, req)
        if await self._call(self.redis.exists(self._lock_key(rec.id))):
            raise SessionBusy(f"session {rec.id} is processing a prior request")

    @asynccontextmanager
    async def acquire(self, req: RunRequest) -> AsyncIterator[SessionRecord]:
        await self.check(req)
        rec = (await self.get(req.session_id)) if req.session_id else None
        rec = rec or SessionRecord.new(req)
        lock = RedisLock(self.redis, self._lock_key(rec.id), self.lock_ttl_ms)
        if not await self._call(lock.acquire()):  # lost a race after check()
            raise SessionBusy(f"session {rec.id} is processing a prior request")
        try:
            await self.save(rec)
            yield rec
        finally:
            # Adapters mutate rec.native / turns during the run; persist before unlocking.
            await self.save(rec)
            await lock.release()
