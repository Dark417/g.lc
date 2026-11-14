"""Cache server client + an exact-match LLM response cache.

One client for every RESP server: Redis OSS, Valkey, AWS ElastiCache / MemoryDB, GCP Memorystore.
Only REDIS_URL changes between them.

Failure policy (docs/design/07): caches fail OPEN (a cache outage costs latency, never data);
the session lock fails CLOSED (see app/core/sessions.py).
"""

import hashlib
import json
import logging
from typing import Any

from redis.exceptions import RedisError

log = logging.getLogger(__name__)

# What "the cache server is down" looks like to a caller.
CACHE_ERRORS = (RedisError, ConnectionError, OSError)


def redis_client(url: str):
    """A client with its own connection pool. Build one per container (pools bind to a loop)."""
    import redis.asyncio as redis

    return redis.from_url(url, decode_responses=True, health_check_interval=30)


class LlmResponseCache:
    """Exact-match cache: same model + system + messages + tools -> same response.

    Good for deterministic, repeated prompts (evals, FAQs, retries after a crash). Not a semantic
    cache: one character of difference misses. Contrast with *server-side* caches, which cache
    the prompt prefix, not the answer: Anthropic prompt caching, Gemini context caching.
    """

    def __init__(self, redis, ttl_s: int = 3600, prefix: str = "llmcache"):
        self.redis, self.ttl_s, self.prefix = redis, ttl_s, prefix
        self.hits = self.misses = 0

    def key(self, **request: Any) -> str:
        blob = json.dumps(request, sort_keys=True, default=str)
        return f"{self.prefix}:{hashlib.sha256(blob.encode()).hexdigest()}"

    async def get(self, key: str) -> Any | None:
        try:
            raw = await self.redis.get(key)
        except CACHE_ERRORS as e:  # fail open
            log.warning("llm cache read failed: %s", e)
            return None
        if raw is None:
            self.misses += 1
            return None
        self.hits += 1
        return json.loads(raw)

    async def put(self, key: str, value: Any) -> None:
        try:
            await self.redis.set(key, json.dumps(value, default=str), ex=self.ttl_s)
        except CACHE_ERRORS as e:  # fail open
            log.warning("llm cache write failed: %s", e)
