"""RedisSessionStore: the Claude Agent SDK's SessionStore protocol on a cache server.

Why: the Claude Code CLI writes each session as JSONL on the local disk of the replica that ran it,
so `resume=` only works on that replica. With `ClaudeAgentOptions(session_store=...)` the SDK
mirrors every transcript entry to the store and can rebuild a session from it on any replica.
This closes the "Claude Agent SDK managed sessions" gap in docs/design/03-cloud-branches.md.

Layout (all keys under one prefix):
  {p}:{project}/{session}[/{subpath}]   Redis LIST of JSON transcript entries (append-only)
  {p}:mtimes:{project}                  HASH session_id -> last write (epoch ms)
  {p}:subkeys:{project}/{session}       SET of subpaths (subagent transcripts, metadata)

Only append() and load() are required by the protocol; list/delete/subkeys enable list_sessions,
delete_session, and subagent transcripts. Retention is ours: we set a TTL on every key.
On ElastiCache / Memorystore / MemoryDB unchanged (same protocol).
"""

import json
import time
from typing import Any


class RedisSessionStore:
    def __init__(self, redis, prefix: str = "claude", ttl_s: int = 30 * 24 * 3600):
        self.redis, self.prefix, self.ttl_s = redis, prefix, ttl_s

    def _key(self, key: dict) -> str:
        base = f"{self.prefix}:{key['project_key']}/{key['session_id']}"
        return f"{base}/{key['subpath']}" if key.get("subpath") else base

    def _mtimes(self, project_key: str) -> str:
        return f"{self.prefix}:mtimes:{project_key}"

    def _subkeys(self, key: dict) -> str:
        return f"{self.prefix}:subkeys:{key['project_key']}/{key['session_id']}"

    async def append(self, key: dict, entries: list[dict[str, Any]]) -> None:
        if not entries:
            return
        k = self._key(key)
        pipe = self.redis.pipeline()
        pipe.rpush(k, *[json.dumps(e, default=str) for e in entries])
        pipe.expire(k, self.ttl_s)
        if key.get("subpath"):
            pipe.sadd(self._subkeys(key), key["subpath"])
            pipe.expire(self._subkeys(key), self.ttl_s)
        else:
            pipe.hset(self._mtimes(key["project_key"]), key["session_id"], int(time.time() * 1000))
        await pipe.execute()

    async def load(self, key: dict) -> list[dict[str, Any]] | None:
        k = self._key(key)
        if not await self.redis.exists(k):
            return None
        return [json.loads(raw) for raw in await self.redis.lrange(k, 0, -1)]

    async def list_sessions(self, project_key: str) -> list[dict[str, Any]]:
        mtimes = await self.redis.hgetall(self._mtimes(project_key))
        return [{"session_id": sid, "mtime": int(mtime)} for sid, mtime in mtimes.items()]

    async def list_subkeys(self, key: dict) -> list[str]:
        return sorted(await self.redis.smembers(self._subkeys(key)))

    async def delete(self, key: dict) -> None:
        if key.get("subpath"):
            await self.redis.delete(self._key(key))
            await self.redis.srem(self._subkeys(key), key["subpath"])
            return
        subs = await self.list_subkeys(key)
        await self.redis.delete(
            self._key(key), self._subkeys(key), *[self._key({**key, "subpath": s}) for s in subs]
        )
        await self.redis.hdel(self._mtimes(key["project_key"]), key["session_id"])
