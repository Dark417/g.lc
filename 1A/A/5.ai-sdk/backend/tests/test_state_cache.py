"""Cache server roles: distributed session lock + registry, LLM cache, failure policies.

Runs against a real redis-server (the `redis_url` fixture); skipped if it is not installed.
"""

import asyncio

import pytest
from fastapi.testclient import TestClient

from app.container import build_container
from app.core.sessions import LockUnavailable, RedisLock, RedisSessionRegistry, SessionBusy
from app.main import create_app
from app.schemas import RunRequest
from app.state.cache import LlmResponseCache, redis_client
from tests.conftest import EchoAdapter


@pytest.fixture
async def redis(redis_url):
    client = redis_client(redis_url)
    await client.flushdb()
    yield client
    await client.aclose()


def req(**kw) -> RunRequest:
    return RunRequest(framework="echo", pattern="single", message="hi", **kw)


async def test_two_replicas_share_lock_and_records(redis_url, redis):
    replica_a = RedisSessionRegistry(redis_client(redis_url))
    replica_b = RedisSessionRegistry(redis_client(redis_url))
    async with replica_a.acquire(req(session_id="s1")) as rec:
        rec.native["claude_session_id"] = "cli-1"
        with pytest.raises(SessionBusy):
            await replica_b.check(req(session_id="s1"))
        with pytest.raises(SessionBusy):
            async with replica_b.acquire(req(session_id="s1")):
                pass
    # released, and the record (with what the adapter wrote into it) is visible to replica B
    async with replica_b.acquire(req(session_id="s1")) as rec_b:
        assert rec_b.native["claude_session_id"] == "cli-1"
    assert [r.id for r in await replica_b.list("demo-user")] == ["s1"]


async def test_lease_is_renewed_while_working_and_expires_when_holder_dies(redis):
    holder = RedisLock(redis, "lock:x", ttl_ms=300)
    assert await holder.acquire()
    await asyncio.sleep(0.7)  # longer than the TTL: the heartbeat kept it
    assert not await RedisLock(redis, "lock:x", ttl_ms=300).acquire()
    holder._heartbeat.cancel()  # simulate a crashed replica: no more renewals
    await asyncio.sleep(0.4)
    successor = RedisLock(redis, "lock:x", ttl_ms=300)
    assert await successor.acquire()
    await holder.release()  # the dead holder's late release must not free the successor's lock
    assert await redis.get("lock:x") == successor.token
    await successor.release()
    assert await redis.get("lock:x") is None


def test_api_with_redis_registry(redis_url, settings):
    settings.redis_url = redis_url
    container = build_container(settings, adapter_specs={})
    container.registry.register(EchoAdapter())
    with TestClient(create_app(container)) as client:
        sid = client.post("/v1/runs", json=req().model_dump()).json()["session_id"]
        client.post("/v1/runs", json=req(session_id=sid).model_dump())
        assert client.get(f"/v1/sessions/{sid}").json()["turns"] == 2
        assert client.get(f"/v1/sessions/{sid}/history").status_code == 501  # echo has no StateOps
        assert client.delete(f"/v1/sessions/{sid}").status_code == 204
        assert client.get(f"/v1/sessions/{sid}").status_code == 404


def test_lock_fails_closed_when_cache_is_down(settings):
    settings.redis_url = "redis://127.0.0.1:1/0"  # nothing listens here
    container = build_container(settings, adapter_specs={})
    container.registry.register(EchoAdapter())
    with TestClient(create_app(container)) as client:
        r = client.post("/v1/runs", json=req(session_id="s1").model_dump())
    assert r.status_code == 503 and "cache server unavailable" in r.json()["detail"]


async def test_lock_unavailable_raised_directly():
    registry = RedisSessionRegistry(redis_client("redis://127.0.0.1:1/0"))
    with pytest.raises(LockUnavailable):
        await registry.get("s1")


async def test_llm_cache_hit_miss_and_fail_open(redis):
    cache = LlmResponseCache(redis, ttl_s=60)
    key = cache.key(model="m", messages=[{"role": "user", "content": "hi"}])
    assert key == cache.key(messages=[{"role": "user", "content": "hi"}], model="m")  # order-free
    assert await cache.get(key) is None
    await cache.put(key, {"text": "hello"})
    assert await cache.get(key) == {"text": "hello"}
    assert (cache.hits, cache.misses) == (1, 1)
    assert 0 < await redis.ttl(key) <= 60

    dead = LlmResponseCache(redis_client("redis://127.0.0.1:1/0"))
    assert await dead.get(key) is None  # no exception: a cache outage only costs latency
    await dead.put(key, {"text": "x"})


def test_memories_endpoint_neutral_fallback(client):
    client.post("/v1/runs", json={"framework": "echo", "pattern": "single", "message": "hi"})
    assert client.get("/v1/users/demo-user/memories").json() == []
    assert client.get("/v1/users/demo-user/memories?provider=mars").status_code == 404
