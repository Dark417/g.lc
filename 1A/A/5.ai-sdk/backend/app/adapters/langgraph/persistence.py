"""LangGraph persistence per provider branch.

Checkpointer (short-term: full graph state per thread_id, after every step)
  raw / vertex  AsyncSqliteSaver                 PRODUCTION (vertex): Postgres saver on Cloud SQL,
                                                 or host the graph on Agent Engine (LanggraphAgent)
  bedrock       LANGGRAPH_CHECKPOINTER picks one:
                  agentcore  AgentCoreMemorySaver   checkpoints as AgentCore Memory events
                  dynamodb   DynamoDBSaver          DynamoDB items (PK/SK), >350 KB offloaded to S3, TTL
                  valkey     AsyncValkeySaver       ElastiCache for Valkey (in-memory, fastest; use
                                                    MemoryDB or AOF if checkpoints must survive)
                  sqlite     local fallback
Node cache (memoised node results, keyed by CachePolicy.key_func)
  bedrock + VALKEY_URL/REDIS_URL  ValkeyCache (ElastiCache)      otherwise  InMemoryCache
Store (long-term: across threads)
  raw / vertex  InMemoryStore                    ILLUSTRATION: process memory
  bedrock       AgentCoreMemoryStore             put() writes messages as events; search() reads
                                                 facts AgentCore *extracted* from them
"""

import asyncio
import re
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from langchain_core.messages import BaseMessage
from langgraph.cache.base import BaseCache
from langgraph.cache.memory import InMemoryCache
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore

from app.config import Settings

_in_memory_store = InMemoryStore()
_in_memory_cache = InMemoryCache()


def node_cache(provider: str, s: Settings) -> BaseCache:
    if provider == "bedrock" and (s.valkey_url or s.redis_url):
        import valkey
        from langgraph_checkpoint_aws import ValkeyCache

        return ValkeyCache(valkey.Valkey.from_url(_valkey_url(s)), ttl=300)
    return _in_memory_cache


def _valkey_url(s: Settings) -> str:
    url = s.valkey_url or s.redis_url
    return url.replace("redis://", "valkey://", 1).replace("rediss://", "valkeys://", 1)


@asynccontextmanager
async def checkpointer(provider: str, s: Settings) -> AsyncIterator[BaseCheckpointSaver]:
    kind = s.langgraph_checkpointer if provider == "bedrock" else "sqlite"
    if kind == "agentcore" and s.agentcore_memory_id:
        from langgraph_checkpoint_aws import AgentCoreMemorySaver

        yield AgentCoreMemorySaver(s.agentcore_memory_id, region_name=s.aws_region)
        return
    if kind == "dynamodb":
        from langgraph_checkpoint_aws import DynamoDBSaver

        offload = {"bucket_name": s.s3_checkpoint_bucket} if s.s3_checkpoint_bucket else None
        yield DynamoDBSaver(
            table_name=s.dynamodb_checkpoint_table,
            region_name=s.aws_region,
            ttl_seconds=30 * 24 * 3600,
            enable_checkpoint_compression=True,
            s3_offload_config=offload,
        )
        return
    if kind == "valkey" and (s.valkey_url or s.redis_url):
        from langgraph_checkpoint_aws import AsyncValkeySaver

        async with AsyncValkeySaver.from_conn_string(
            _valkey_url(s), ttl_seconds=7 * 24 * 3600
        ) as saver:
            yield saver
        return
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

    async with AsyncSqliteSaver.from_conn_string(str(s.data_path / "langgraph.db")) as saver:
        yield saver


def store(provider: str, s: Settings) -> BaseStore:
    if provider == "bedrock" and s.agentcore_memory_id:
        from langgraph_checkpoint_aws import AgentCoreMemoryStore

        return AgentCoreMemoryStore(memory_id=s.agentcore_memory_id, region_name=s.aws_region)
    return _in_memory_store


def _is_agentcore(st: BaseStore) -> bool:
    return type(st).__name__ == "AgentCoreMemoryStore"


async def save_message(st: BaseStore, user_id: str, thread_id: str, message: BaseMessage) -> None:
    """Long-term write. AgentCore wants namespace (actor_id, session_id) and a BaseMessage."""
    await asyncio.to_thread(st.put, (user_id, thread_id), uuid.uuid4().hex, {"message": message})


async def search_memories(st: BaseStore, user_id: str, query: str, limit: int = 5) -> list[str]:
    """Long-term read: AgentCore's extracted facts, or (locally) this user's past messages."""
    if _is_agentcore(st):
        items = await asyncio.to_thread(st.search, ("facts", user_id), query=query, limit=limit)
        return [str(i.value.get("content", i.value)) for i in items]
    items = await asyncio.to_thread(st.search, (user_id,), limit=50)
    words = {w for w in re.findall(r"[a-z0-9]+", query.lower()) if len(w) > 3}
    texts = [str(i.value["message"].content) for i in items if "message" in i.value]
    hits = [t for t in texts if words & set(re.findall(r"[a-z0-9]+", t.lower()))]
    return hits[-limit:]
