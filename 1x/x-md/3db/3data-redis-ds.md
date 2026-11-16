# 4data-redis-ds — Redis And Cache Key Design

- **In plain words:** designing for Redis means choosing key names, the data structure behind each key, and how long each key lives, so lookups are one fast step and memory stays bounded.
- Why a separate file from [4data-nosql-ds.md](4data-nosql-ds.md): a NoSQL schema is a source of truth designed for queries; a cache schema is a disposable copy designed for one lookup, with expiry and memory as first-class concerns
- Mechanics and commands: [4redis.md](4redis.md), [4redis-c.md](4redis-c.md)

## Index

- [0. One-Minute Version](#0-one-minute-version)
- [1. Cache Design vs Database Design](#1-cache-design-vs-database-design)
- [2. Key Naming](#2-key-naming)
- [3. Picking The Data Structure](#3-picking-the-data-structure)
- [4. TTL And Invalidation](#4-ttl-and-invalidation)
- [5. Sizing And Memory](#5-sizing-and-memory)
- [6. Cluster: Hash Slots And Hot Keys](#6-cluster-hash-slots-and-hot-keys)
- [7. Worked Designs](#7-worked-designs)
- [8. Failure Modes](#8-failure-modes)
- [9. Interview Questions](#9-interview-questions)
- [References](#references)

---

## 0. One-Minute Version

- **What:** keys, value types and expiry for data held in memory
- **Why:** Redis answers in well under a millisecond on the server (order of magnitude), but only for lookups you designed a key for; memory is the cost
- **How:** one key per lookup, structured names, the smallest fitting data type, a TTL on everything that is a copy
- **Catch:** no secondary indexes and no joins; if you need a new lookup, you need a new key
- 🗣 "I design one key per access pattern, give every cached copy a TTL with jitter, and size memory from key count × value size."

## 1. Cache Design vs Database Design

| Question | NoSQL database (DynamoDB, MongoDB) | Redis as a cache |
|---|---|---|
| Is it the source of truth? | Yes | No: a rebuildable copy |
| Durability | Replicated, persistent | Optional (RDB / AOF); assume loss |
| Query flexibility | Partition key + sort key / indexes | Exact key only (plus ranges inside sorted sets) |
| Lifetime | Until deleted (or TTL) | TTL on almost everything |
| Size limit | Effectively unbounded storage | RAM of the cluster |
| Design driver | Access patterns + consistency | Hit rate, memory, invalidation |

- Redis as primary store (sessions, rate limits, leaderboards) is fine when losing data is acceptable or AOF + replicas cover it

## 2. Key Naming

- Pattern: `<app>:<entity>:<id>[:<field>]`, e.g. `shop:user:42:profile`, `shop:cart:42`
- Put the version in the key when the value shape changes: `shop:v2:user:42` (old keys expire on their own)
- Keep keys short but readable; key bytes count toward memory
- Tenant first in multi-tenant systems: `t:acme:user:42`
- Use hash tags to keep keys that must be used together on one cluster slot: `cart:{42}:items`, `cart:{42}:meta`

## 3. Picking The Data Structure

| Need | Type | Example |
|---|---|---|
| Cached object, read whole | String (JSON or serialized) | `user:42` → JSON |
| Object with fields read or updated separately | Hash | `HINCRBY cart:42 sku123 1` |
| Ranking, time-ordered feed, sliding window | Sorted set | `ZADD leaderboard 980 user:42` |
| Membership, dedupe | Set | `SADD seen:job:7 msg-abc` |
| Queue, recent items | List | `LPUSH feed:42 …` + `LTRIM` to cap length |
| Event log with consumer groups | Stream | `XADD orders * …` |
| Unique count (approximate) | HyperLogLog | `PFADD visitors:2026-11-15 user:42` |
| Flags per id | Bitmap | `SETBIT active:2026-11-15 42 1` |
| Nearby search | Geo | `GEOADD drivers lon lat driver:9` |

- Small hashes, lists and sets use compact encodings (listpack), a large memory saving under the size thresholds

## 4. TTL And Invalidation

- **In plain words:** every cached copy needs an expiry, and every write to the source needs a plan for the stale copy.
- TTL by how stale you can tolerate: config minutes, prices seconds, sessions = idle timeout
- Add jitter (±10%) so keys created together don't expire together (avalanche)
- Invalidation options
  - Delete on write (cache-aside): write DB, then `DEL key`
  - Write-through: update cache in the same code path as the DB
  - Event-driven: CDC or domain events delete or refresh keys
- Race: a reader can repopulate an old value between the DB write and the `DEL`; short TTLs or versioned values bound the damage
- Hot key rebuild: single-flight lock (`SET lock:key NX PX 3000`) or early refresh before expiry (stampede protection)
- Negative caching: store "not found" briefly to stop repeated misses (penetration)

## 5. Sizing And Memory

- Memory ≈ keys × (key bytes + value bytes + per-key overhead of roughly tens of bytes) (order of magnitude; measure with `MEMORY USAGE`)
- Example: 10M users × ~1 KB profile ≈ 10 GB, plus overhead and replica copies
- `maxmemory` + eviction policy
  - `allkeys-lru` / `allkeys-lfu` for pure caches
  - `volatile-*` when some keys must never be evicted
  - `noeviction` for primary-store use: writes fail instead of losing data
- Avoid big keys: a 1M-member set or a 10 MB string blocks the single thread on read, delete and migration

## 6. Cluster: Hash Slots And Hot Keys

- Redis Cluster splits keys into 16,384 hash slots spread across primaries (Redis docs)
- Multi-key commands and Lua scripts work only within one slot: use hash tags
- Hot key (one celebrity profile): replicate it under several keys (`user:42#1..#8`) and read one at random, or add an in-process cache in front
- Hot shard from bad hash tags: a tag like `{2026-11-15}` sends a whole day to one slot

## 7. Worked Designs

| Use case | Keys and types | TTL |
|---|---|---|
| User profile cache | `user:{id}` String JSON | 10 min ± jitter; `DEL` on update |
| Session store | `sess:{sessionId}` Hash | Sliding: `EXPIRE` on each request |
| Rate limiter (sliding window) | `rl:{apiKey}:{route}` Sorted set of timestamps | Window length |
| Leaderboard | `lb:{game}:{season}` Sorted set | Season end, or none |
| Idempotency record | `idem:{key}` String with the stored response | Client retry window (e.g. 24 h) |
| Distributed lock (efficiency only) | `lock:{resource}` String token via `SET NX PX` | Lease time |

## 8. Failure Modes

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Stampede | Hot key expires under load | DB spike at expiry | Single-flight lock, early refresh |
| Avalanche | Many keys share one TTL | DB spike at a fixed time | TTL jitter |
| Penetration | Lookups for ids that don't exist | Misses never become hits | Negative cache, Bloom filter |
| Stale data | Missed invalidation | User reports, version mismatch | Delete on write, short TTL, versioned keys |
| Memory full | No TTL, unbounded keys | Evictions or write errors | TTLs, `maxmemory` policy, sizing |
| Big key stall | Huge collection deleted or read | Latency spikes on one shard | Split keys; `UNLINK` instead of `DEL` |

## 9. Interview Questions

**Q1. How do you design cache keys for a user service?**
- L4: `app:user:{id}` with a JSON value and a TTL; delete on update
- L5 extra: version the key with the schema, jitter TTLs, single-flight on hot keys, hash tags for keys used together in a cluster

**Q2. Redis or DynamoDB for this data?**
- L4: Redis for fast, disposable lookups; DynamoDB as a durable source of truth
- L5 extra: decide by durability need, query shape (exact key vs key + range), and memory cost vs storage cost; often both: DynamoDB as truth, Redis in front

## References

- [Redis docs — Data types](https://redis.io/docs/latest/develop/data-types/)
- [Redis docs — Key eviction](https://redis.io/docs/latest/develop/reference/eviction/)
- [Redis docs — Cluster specification (hash slots)](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/)
