# Redis — Implementation

> Implementation pair of [1.redis.md](1.redis.md); same section order. Rules: [.agents/rules.md](../../.agents/rules.md).
> Snippets are focused and compile in isolation; not a runnable project.
> Libraries: Python → `redis` (redis-py 5.x, async via `redis.asyncio`); Java → **Lettuce** (default in Spring Boot, netty, async/reactive, cluster-aware) and **Jedis** (simple, blocking) mentioned where different; Spring → `spring-boot-starter-data-redis`, `spring-boot-starter-cache`.

## Index
- [0. Setup and admin](#0-setup-and-admin)
  - [0.1 Local (standalone, sentinel, cluster)](#01-local-standalone-sentinel-cluster)
  - [0.2 redis-cli ops cheat sheet](#02-redis-cli-ops-cheat-sheet)
  - [0.3 Client setup and connection pools](#03-client-setup-and-connection-pools)
- [1. Core commands per data type](#1-core-commands-per-data-type)
  - [1.1 String / counter / bitmap](#11-string--counter--bitmap)
  - [1.2 Hash](#12-hash)
  - [1.3 List](#13-list)
  - [1.4 Set / Sorted set](#14-set--sorted-set)
  - [1.5 HyperLogLog / Geo / SCAN](#15-hyperloglog--geo--scan)
- [2. Expiry, eviction, memory](#2-expiry-eviction-memory)
- [3. Persistence, replication, HA clients](#3-persistence-replication-ha-clients)
  - [3.1 Persistence config](#31-persistence-config)
  - [3.2 Replication + WAIT](#32-replication--wait)
  - [3.3 Sentinel-aware clients](#33-sentinel-aware-clients)
  - [3.4 Cluster-aware clients and hashtags](#34-cluster-aware-clients-and-hashtags)
- [4. Atomicity: pipeline, MULTI/WATCH, Lua, Functions](#4-atomicity-pipeline-multiwatch-lua-functions)
- [5. Caching](#5-caching)
  - [5.1 Cache-aside (manual)](#51-cache-aside-manual)
  - [5.2 Stampede protection: lock + logical expiry](#52-stampede-protection-lock--logical-expiry)
  - [5.3 Spring Cache abstraction](#53-spring-cache-abstraction)
  - [5.4 Client-side caching (tracking)](#54-client-side-caching-tracking)
  - [5.5 Null caching, Bloom, jitter](#55-null-caching-bloom-jitter)
- [6. Locks, rate limiting, idempotency](#6-locks-rate-limiting-idempotency)
  - [6.1 Distributed lock with token + fencing](#61-distributed-lock-with-token--fencing)
  - [6.2 Rate limiters (fixed, sliding, token bucket)](#62-rate-limiters-fixed-sliding-token-bucket)
  - [6.3 Idempotency key](#63-idempotency-key)
  - [6.4 Redisson (Java) helpers](#64-redisson-java-helpers)
- [7. Messaging: Pub/Sub, Streams, queues](#7-messaging-pubsub-streams-queues)
  - [7.1 Pub/Sub](#71-pubsub)
  - [7.2 Streams with consumer groups, retry, DLQ](#72-streams-with-consumer-groups-retry-dlq)
  - [7.3 List queue and delay queue](#73-list-queue-and-delay-queue)
  - [7.4 Keyspace notifications](#74-keyspace-notifications)
- [8. Redis Stack: JSON, Search, vectors, Bloom](#8-redis-stack-json-search-vectors-bloom)
- [9. Spring Boot wiring](#9-spring-boot-wiring)
- [10. Config tables](#10-config-tables)
  - [10.1 Server config](#101-server-config)
  - [10.2 Client config](#102-client-config)
- [11. Observability and testing](#11-observability-and-testing)
- [References](#references)

---

## 0. Setup and admin

### 0.1 Local (standalone, sentinel, cluster)
```yaml
# docker-compose.yml — standalone with persistence
services:
  redis:
    image: redis:8
    command: ["redis-server", "--appendonly", "yes", "--maxmemory", "512mb", "--maxmemory-policy", "allkeys-lru"]
    ports: ["6379:6379"]
    volumes: ["redis-data:/data"]
volumes: { redis-data: {} }
```
```bash
# sentinel (3 sentinels + primary + 2 replicas) — sentinel.conf minimal
sentinel monitor mymaster redis-primary 6379 2
sentinel down-after-milliseconds mymaster 5000
sentinel failover-timeout mymaster 60000
sentinel parallel-syncs mymaster 1

# cluster (6 nodes, 3 primaries + 3 replicas)
for p in 7000 7001 7002 7003 7004 7005; do redis-server --port $p --cluster-enabled yes --cluster-config-file nodes-$p.conf --daemonize yes; done
redis-cli --cluster create 127.0.0.1:7000 127.0.0.1:7001 127.0.0.1:7002 127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 --cluster-replicas 1
```
- deps: Python `pip install redis` (`redis[hiredis]` for faster parsing); Java `io.lettuce:lettuce-core` / `redis.clients:jedis` / `org.redisson:redisson`; Spring Boot `spring-boot-starter-data-redis` (Lettuce)

### 0.2 redis-cli ops cheat sheet
```bash
redis-cli -h host -p 6379 -a pw --tls                          # connect
redis-cli INFO memory | grep -E "used_memory_human|used_memory_rss_human|mem_fragmentation_ratio"
redis-cli INFO stats | grep -E "keyspace_hits|keyspace_misses|evicted_keys|expired_keys|rejected_connections"
redis-cli INFO replication                                     # role, offsets, lag
redis-cli INFO persistence | grep -E "rdb_last_bgsave_status|aof_last_write_status|latest_fork_usec"
redis-cli --bigkeys; redis-cli --memkeys; redis-cli --hotkeys   # hotkeys needs LFU policy
redis-cli --latency; redis-cli --latency-history; redis-cli LATENCY LATEST
redis-cli SLOWLOG GET 25; redis-cli CONFIG SET slowlog-log-slower-than 5000
redis-cli MEMORY USAGE bigkey; redis-cli MEMORY DOCTOR; redis-cli OBJECT ENCODING k; redis-cli OBJECT FREQ k
redis-cli --scan --pattern 'sess:*' | head                     # never KEYS in prod
redis-cli CLIENT LIST; redis-cli CLIENT KILL TYPE pubsub
redis-cli CONFIG SET maxmemory 4gb; redis-cli CONFIG REWRITE
redis-cli BGSAVE; redis-cli BGREWRITEAOF; redis-cli LASTSAVE
redis-cli DEBUG SLEEP 0                                        # (never in prod) ; MONITOR briefly on a replica only
# sentinel
redis-cli -p 26379 SENTINEL get-master-addr-by-name mymaster; redis-cli -p 26379 SENTINEL failover mymaster
# cluster
redis-cli -c -p 7000 CLUSTER NODES; redis-cli --cluster check 127.0.0.1:7000; redis-cli --cluster info 127.0.0.1:7000
redis-cli --cluster reshard 127.0.0.1:7000 --cluster-from <id> --cluster-to <id> --cluster-slots 1000 --cluster-yes
redis-cli --cluster rebalance 127.0.0.1:7000 --cluster-use-empty-masters
redis-cli -p 7003 CLUSTER FAILOVER                             # on a replica: manual, no-loss failover
# ACL
redis-cli ACL SETUSER app on '>s3cret' '~cache:*' '+@read' '+@write' '-@dangerous'
redis-cli ACL LIST
```

### 0.3 Client setup and connection pools
```python
import redis
r = redis.Redis(host="localhost", port=6379, password=None, db=0, decode_responses=True,
                socket_timeout=0.5, socket_connect_timeout=0.5, health_check_interval=30,
                retry_on_timeout=True, max_connections=50)               # pool is built in; share one client per process
# async
from redis.asyncio import Redis as AsyncRedis
ar = AsyncRedis.from_url("redis://localhost:6379/0", decode_responses=True)
```
```java
// Lettuce (thread-safe single connection, multiplexed; pool only for blocking cmds / transactions)
RedisClient client = RedisClient.create(RedisURI.Builder.redis("localhost", 6379).withTimeout(Duration.ofMillis(500)).build());
StatefulRedisConnection<String, String> conn = client.connect();
RedisCommands<String, String> sync = conn.sync();
RedisAsyncCommands<String, String> async = conn.async();
// Jedis (one connection per thread; use pool)
JedisPool pool = new JedisPool(new JedisPoolConfig(), "localhost", 6379);
try (Jedis j = pool.getResource()) { j.set("k", "v"); }
```
```java
// Spring Boot: StringRedisTemplate / RedisTemplate auto-configured from spring.data.redis.* (§9)
@Autowired StringRedisTemplate redis;   // string keys/values
@Autowired RedisTemplate<String, Object> redisTemplate;   // configure JSON serializer (§9)
```

---

## 1. Core commands per data type

### 1.1 String / counter / bitmap
```python
r.set("user:42:name", "ann", ex=3600)                 # SET with TTL
r.set("lock:res", "tok", nx=True, px=30_000)          # SET NX PX → True/None
r.get("user:42:name"); r.mget(["a", "b"]); r.mset({"a": 1, "b": 2})
r.incr("pv:2026-08-26"); r.incrby("bal:42", -5); r.incrbyfloat("x", 0.5)
r.getex("k", ex=60)                                   # get + refresh TTL (6.2)
r.setbit("seen:2026-08-26", 1_000_001, 1); r.bitcount("seen:2026-08-26"); r.getbit("seen:2026-08-26", 42)
r.bitop("AND", "seen:both", "seen:d1", "seen:d2")
```
```java
sync.set("user:42:name", "ann", SetArgs.Builder.ex(3600));
sync.set("lock:res", "tok", SetArgs.Builder.nx().px(30_000));       // "OK" or null
sync.incr("pv:2026-08-26"); sync.incrby("bal:42", -5);
sync.setbit("seen:2026-08-26", 1_000_001, 1); sync.bitcount("seen:2026-08-26");
// Spring
redis.opsForValue().set("user:42:name", "ann", Duration.ofHours(1));
Boolean ok = redis.opsForValue().setIfAbsent("lock:res", "tok", Duration.ofSeconds(30));
redis.opsForValue().increment("pv:2026-08-26");
```

### 1.2 Hash
```python
r.hset("sess:abc", mapping={"uid": 42, "role": "admin", "ts": 1756200000}); r.expire("sess:abc", 1800)
r.hget("sess:abc", "uid"); r.hmget("sess:abc", ["uid", "role"]); r.hgetall("sess:abc")   # hgetall O(n): bounded hashes only
r.hincrby("cart:42", "sku-1", 2); r.hdel("cart:42", "sku-1"); r.hexists("cart:42", "sku-1")
for field, val in r.hscan_iter("big:hash", count=500): ...            # paginate large hashes
r.hexpire("sess:abc", 600, "tmp")                                      # per-field TTL (7.4+)
# bucketing: many small objects → one listpack hash per 1000 ids
r.hset(f"user:{42 // 1000}", "42", json.dumps(profile))
```
```java
sync.hset("sess:abc", Map.of("uid", "42", "role", "admin")); sync.expire("sess:abc", 1800);
sync.hincrby("cart:42", "sku-1", 2); Map<String,String> all = sync.hgetall("sess:abc");
// Spring
redis.opsForHash().putAll("sess:abc", Map.of("uid", "42")); redis.opsForHash().increment("cart:42", "sku-1", 2);
```

### 1.3 List
```python
r.lpush("timeline:42", "post-9"); r.ltrim("timeline:42", 0, 99)       # capped recent-100
r.lrange("timeline:42", 0, 9)
r.rpush("q:jobs", job); item = r.blpop("q:jobs", timeout=5)             # simple queue; None on timeout
r.blmove("q:jobs", "q:processing", 5, "RIGHT", "LEFT")                  # reliable queue: move then LREM on done
```
```java
sync.lpush("timeline:42", "post-9"); sync.ltrim("timeline:42", 0, 99);
KeyValue<String,String> kv = sync.blpop(5, "q:jobs");
String job = sync.blmove("q:jobs", "q:processing", LMoveArgs.Builder.rightLeft(), 5);
// Spring: redis.opsForList().leftPush(...), rightPop("q:jobs", Duration.ofSeconds(5))
```

### 1.4 Set / Sorted set
```python
r.sadd("tags:post9", "redis", "cache"); r.sismember("tags:post9", "redis"); r.scard("tags:post9")
r.sinter("likes:a", "likes:b"); r.sinterstore("tmp", "likes:a", "likes:b"); r.srandmember("pool", 3); r.spop("pool")
for m in r.sscan_iter("big:set", count=1000): ...

r.zadd("board", {"ann": 120, "bob": 95}); r.zincrby("board", 10, "bob")
r.zrevrange("board", 0, 9, withscores=True)                  # top 10
r.zrevrank("board", "ann"); r.zscore("board", "ann")
r.zrangebyscore("due", 0, now_ms, start=0, num=100)          # delay queue poll
r.zremrangebyscore("win:u42", 0, now_ms - 60_000)            # sliding window cleanup
r.zadd("due", {job_id: run_at_ms}); r.zpopmin("due")          # ZPOPMIN / BZPOPMIN blocking
```
```java
sync.zadd("board", 120, "ann"); sync.zincrby("board", 10, "bob");
List<ScoredValue<String>> top = sync.zrevrangeWithScores("board", 0, 9);
Long rank = sync.zrevrank("board", "ann");
List<String> due = sync.zrangebyscore("due", Range.create(0, nowMs), Limit.create(0, 100));
// Spring: redis.opsForZSet().reverseRangeWithScores("board", 0, 9)
```

### 1.5 HyperLogLog / Geo / SCAN
```python
r.pfadd("uv:2026-08-26", "u1", "u2"); r.pfcount("uv:2026-08-26"); r.pfmerge("uv:week", "uv:d1", "uv:d2")
r.geoadd("drivers", (-122.42, 37.77, "d1")); r.geosearch("drivers", longitude=-122.4, latitude=37.8, radius=5, unit="km", withdist=True)
for key in r.scan_iter(match="sess:*", count=1000): r.unlink(key)     # SCAN + UNLINK, never KEYS + DEL
```
```java
sync.pfadd("uv:2026-08-26", "u1", "u2"); sync.pfcount("uv:2026-08-26");
ScanCursor c = ScanCursor.INITIAL;
do { KeyScanCursor<String> page = sync.scan(c, ScanArgs.Builder.matches("sess:*").limit(1000));
     if (!page.getKeys().isEmpty()) sync.unlink(page.getKeys().toArray(new String[0])); c = page; } while (!c.isFinished());
```

---

## 2. Expiry, eviction, memory
```python
r.expire("k", 60); r.pexpire("k", 500); r.expireat("k", ts); r.ttl("k"); r.persist("k")
r.set("k", v, ex=random.randint(540, 660))            # TTL jitter ±10 % → no avalanche
r.unlink("huge:key")                                  # async free
r.config_set("maxmemory-policy", "allkeys-lfu")
print(r.info("memory")["mem_fragmentation_ratio"]); r.config_set("activedefrag", "yes")
r.memory_usage("k"); r.object("encoding", "k")
```
```java
sync.expire("k", 60); sync.ttl("k"); sync.unlink("huge:key");
sync.configSet("maxmemory-policy", "allkeys-lfu");
// Spring: redis.expire("k", Duration.ofSeconds(60)); redis.unlink("huge:key");
```
```conf
# redis.conf — cache instance
maxmemory 8gb
maxmemory-policy allkeys-lfu
maxmemory-samples 10
lazyfree-lazy-eviction yes
lazyfree-lazy-expire yes
lazyfree-lazy-server-del yes
replica-lazy-flush yes
activedefrag yes
hz 10
active-expire-effort 1
hash-max-listpack-entries 128
hash-max-listpack-value 64
```

---

## 3. Persistence, replication, HA clients

### 3.1 Persistence config
```conf
# durable-ish instance (sessions, queues)
appendonly yes
appendfsync everysec
aof-use-rdb-preamble yes
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
save 3600 1 300 100 60 10000        # RDB too (backups, replica sync)
stop-writes-on-bgsave-error yes
rdbcompression yes
# pure cache: appendonly no ; save ""
```
```bash
# OS prerequisites (avoid fork stalls / failed BGSAVE)
echo never > /sys/kernel/mm/transparent_hugepage/enabled
sysctl vm.overcommit_memory=1
```

### 3.2 Replication + WAIT
```conf
# replica
replicaof redis-primary 6379
replica-read-only yes
repl-diskless-sync yes
repl-diskless-sync-delay 5
repl-backlog-size 256mb           # ≈ write MB/s × seconds of tolerated outage
# primary safety
min-replicas-to-write 1
min-replicas-max-lag 10
```
```python
r.set("order:9", "paid"); acked = r.wait(1, 500)          # block ≤500 ms until 1 replica has it; returns count
r.execute_command("WAITAOF", 1, 1, 500)                  # 7.2: local fsync + 1 replica fsync
```
```java
sync.set("order:9", "paid"); Long acked = sync.waitForReplication(1, 500);
```

### 3.3 Sentinel-aware clients
```python
from redis.sentinel import Sentinel
s = Sentinel([("s1", 26379), ("s2", 26379), ("s3", 26379)], socket_timeout=0.5)
primary = s.master_for("mymaster", decode_responses=True)    # re-resolves on failover
replica = s.slave_for("mymaster", decode_responses=True)     # read-only, stale
primary.set("k", "v"); replica.get("k")
```
```java
RedisURI uri = RedisURI.Builder.sentinel("s1", 26379, "mymaster").withSentinel("s2", 26379).withSentinel("s3", 26379).build();
StatefulRedisMasterReplicaConnection<String,String> c = MasterReplica.connect(client, StringCodec.UTF8, uri);
c.setReadFrom(ReadFrom.REPLICA_PREFERRED);   // reads to replicas, writes to primary
```
```yaml
# Spring
spring.data.redis.sentinel.master: mymaster
spring.data.redis.sentinel.nodes: s1:26379,s2:26379,s3:26379
```

### 3.4 Cluster-aware clients and hashtags
```python
from redis.cluster import RedisCluster
rc = RedisCluster(host="127.0.0.1", port=7000, decode_responses=True, read_from_replicas=True)
rc.set("user:{42}:profile", "..."); rc.set("user:{42}:cart", "...")   # same slot → MGET/Lua allowed
rc.mget(["user:{42}:profile", "user:{42}:cart"])
rc.mget(["a", "b"])                     # redis-py splits per slot automatically (not atomic)
print(rc.keyslot("user:{42}:x"))        # 16384-space slot
```
```java
RedisClusterClient cc = RedisClusterClient.create("redis://127.0.0.1:7000");
cc.setOptions(ClusterClientOptions.builder()
    .topologyRefreshOptions(ClusterTopologyRefreshOptions.builder().enablePeriodicRefresh(Duration.ofSeconds(30)).enableAllAdaptiveRefreshTriggers().build())
    .build());
StatefulRedisClusterConnection<String,String> cconn = cc.connect();
cconn.setReadFrom(ReadFrom.REPLICA_PREFERRED);
RedisAdvancedClusterCommands<String,String> cs = cconn.sync();
cs.mset(Map.of("user:{42}:profile", "..", "user:{42}:cart", ".."));   // Lettuce fans out cross-slot MSET/MGET/DEL
```
```yaml
spring.data.redis.cluster.nodes: 127.0.0.1:7000,127.0.0.1:7001,127.0.0.1:7002
spring.data.redis.cluster.max-redirects: 3
spring.data.redis.lettuce.cluster.refresh.adaptive: true
spring.data.redis.lettuce.cluster.refresh.period: 30s
```

---

## 4. Atomicity: pipeline, MULTI/WATCH, Lua, Functions
```python
# pipeline (no atomicity, one RTT)
with r.pipeline(transaction=False) as p:
    for i in range(1000): p.hset(f"user:{i}", "seen", 1)
    p.execute()

# MULTI/EXEC (atomic block) — transaction=True default
with r.pipeline() as p:
    p.multi(); p.decrby("stock:sku1", 1); p.rpush("orders", "o9"); p.execute()

# WATCH: optimistic CAS with retry
def reserve(sku, n):
    with r.pipeline() as p:
        while True:
            try:
                p.watch(f"stock:{sku}")
                stock = int(p.get(f"stock:{sku}") or 0)
                if stock < n: p.unwatch(); return False
                p.multi(); p.decrby(f"stock:{sku}", n); p.execute(); return True
            except redis.WatchError: continue            # key changed → retry

# Lua: atomic read-branch-write (preferred for hot keys)
RESERVE = r.register_script("""
local s = tonumber(redis.call('GET', KEYS[1]) or '0')
if s < tonumber(ARGV[1]) then return 0 end
redis.call('DECRBY', KEYS[1], ARGV[1]); return 1""")
ok = RESERVE(keys=["stock:sku1"], args=[2])                  # EVALSHA with EVAL fallback on NOSCRIPT

# Functions (7.0): persisted + replicated
r.function_load("""#!lua name=inv
redis.register_function('reserve', function(keys, args)
  local s = tonumber(redis.call('GET', keys[1]) or '0')
  if s < tonumber(args[1]) then return 0 end
  redis.call('DECRBY', keys[1], args[1]); return 1 end)""", replace=True)
r.fcall("reserve", 1, "stock:sku1", 2)
```
```java
// Lettuce pipelining = async commands + flush
async.setAutoFlushCommands(false);
List<RedisFuture<?>> fs = new ArrayList<>();
for (int i = 0; i < 1000; i++) fs.add(async.hset("user:" + i, "seen", "1"));
async.flushCommands(); LettuceFutures.awaitAll(Duration.ofSeconds(5), fs.toArray(new RedisFuture[0]));
async.setAutoFlushCommands(true);

// MULTI/EXEC + WATCH (needs a dedicated connection — not the shared one)
sync.watch("stock:sku1"); int stock = Integer.parseInt(sync.get("stock:sku1"));
if (stock >= 2) { sync.multi(); sync.decrby("stock:sku1", 2); TransactionResult res = sync.exec(); /* res.wasDiscarded() → retry */ } else sync.unwatch();

// Lua
String RESERVE = "local s=tonumber(redis.call('GET',KEYS[1]) or '0') if s<tonumber(ARGV[1]) then return 0 end redis.call('DECRBY',KEYS[1],ARGV[1]) return 1";
String sha = sync.scriptLoad(RESERVE);
Long ok = sync.evalsha(sha, ScriptOutputType.INTEGER, new String[]{"stock:sku1"}, "2");   // catch RedisNoScriptException → eval
```
```java
// Spring: RedisScript bean, template.execute handles EVALSHA/EVAL fallback
@Bean RedisScript<Long> reserveScript() { return RedisScript.of(new ClassPathResource("reserve.lua"), Long.class); }
Long ok = redis.execute(reserveScript, List.of("stock:sku1"), "2");
// Spring transactions: redis.execute(new SessionCallback<>() { ops.multi(); ...; return ops.exec(); })
```

---

## 5. Caching

### 5.1 Cache-aside (manual)
```python
def get_user(uid):
    key = f"user:{uid}"
    if (v := r.get(key)) is not None:
        return None if v == "__null__" else json.loads(v)
    row = db.fetch_user(uid)
    r.set(key, json.dumps(row) if row else "__null__", ex=jitter(600) if row else 30)
    return row

def update_user(uid, fields):
    db.update_user(uid, fields)
    r.delete(f"user:{uid}")                              # invalidate, don't update
    schedule(lambda: r.delete(f"user:{uid}"), delay=0.5) # delayed double delete for the read-load-stale race
```
```java
public User getUser(long id) {
    String key = "user:" + id;
    String v = redis.opsForValue().get(key);
    if (v != null) return NULL_MARK.equals(v) ? null : json.read(v, User.class);
    User u = repo.findById(id).orElse(null);
    redis.opsForValue().set(key, u == null ? NULL_MARK : json.write(u), u == null ? Duration.ofSeconds(30) : jitter(Duration.ofMinutes(10)));
    return u;
}
@Transactional public void updateUser(User u) { repo.save(u); TransactionSynchronizationManager.registerSynchronization(
    new TransactionSynchronization() { public void afterCommit() { redis.delete("user:" + u.id()); } }); }   // delete AFTER DB commit
```

### 5.2 Stampede protection: lock + logical expiry
```python
def get_with_singleflight(key, loader, ttl=600, lock_ttl=5):
    v = r.get(key)
    if v is not None: return json.loads(v)
    token = uuid4().hex
    if r.set(f"lock:{key}", token, nx=True, px=lock_ttl * 1000):     # one rebuilder
        try:
            data = loader(); r.set(key, json.dumps(data), ex=jitter(ttl)); return data
        finally:
            r.eval("if redis.call('GET',KEYS[1])==ARGV[1] then return redis.call('DEL',KEYS[1]) end", 1, f"lock:{key}", token)
    for _ in range(50):                                               # others wait briefly
        time.sleep(0.05)
        if (v := r.get(key)) is not None: return json.loads(v)
    return loader()                                                   # fallback: hit DB

# logical expiry: physical TTL long, logical TTL in value → serve stale, refresh async
def get_logical(key, loader, logical_ttl=60, physical_ttl=3600):
    raw = r.get(key)
    if raw:
        obj = json.loads(raw)
        if obj["exp"] > time.time(): return obj["v"]
        if r.set(f"refresh:{key}", 1, nx=True, ex=10):
            executor.submit(lambda: r.set(key, json.dumps({"v": loader(), "exp": time.time() + logical_ttl}), ex=physical_ttl))
        return obj["v"]                                               # stale but instant
    v = loader(); r.set(key, json.dumps({"v": v, "exp": time.time() + logical_ttl}), ex=physical_ttl); return v
```
```java
// Java: same shape; Caffeine in-process single-flight first, Redis lock second
LoadingCache<String, User> l1 = Caffeine.newBuilder().expireAfterWrite(Duration.ofSeconds(5)).maximumSize(10_000).build(this::loadFromRedisOrDb);
```

### 5.3 Spring Cache abstraction
```java
@EnableCaching @Configuration
class CacheConfig {
    @Bean RedisCacheManager cacheManager(RedisConnectionFactory cf) {
        RedisCacheConfiguration base = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(10))
            .serializeValuesWith(SerializationPair.fromSerializer(new GenericJackson2JsonRedisSerializer()))
            .disableCachingNullValues()                      // or keep nulls with short TTL via separate cache
            .prefixCacheNameWith("app:");
        return RedisCacheManager.builder(cf).cacheDefaults(base)
            .withCacheConfiguration("users", base.entryTtl(Duration.ofMinutes(30)))
            .transactionAware()                              // cache ops after DB tx commit
            .build();
    }
}
@Service class UserService {
    @Cacheable(value = "users", key = "#id", sync = true)    // sync=true → single-flight within the JVM
    public User get(long id) { return repo.findById(id).orElseThrow(); }
    @CachePut(value = "users", key = "#u.id") public User save(User u) { return repo.save(u); }
    @CacheEvict(value = "users", key = "#id") public void delete(long id) { repo.deleteById(id); }
    @CacheEvict(value = "users", allEntries = true) public void flush() {}
}
```
- Python equivalents: `cachetools` (in-process), `aiocache` with Redis backend, or a small decorator over the cache-aside function

### 5.4 Client-side caching (tracking)
```python
# redis-py 5: RESP3 + client tracking
r3 = redis.Redis(protocol=3, cache_config=redis.cache.CacheConfig())   # local cache, server pushes invalidations
r3.get("flag:beta")   # served locally until key changes on the server
```
```java
StatefulRedisConnection<String,String> c = client.connect();      // RESP3 default in Lettuce 6
Map<String,String> local = new ConcurrentHashMap<>();
CacheFrontend<String,String> frontend = ClientSideCaching.enable(CacheAccessor.forMap(local), c, TrackingArgs.Builder.enabled());
String v = frontend.get("flag:beta");                               // local map, invalidated by server push
```

### 5.5 Null caching, Bloom, jitter
```python
def jitter(ttl): return int(ttl * random.uniform(0.9, 1.1))
r.execute_command("BF.RESERVE", "ids:users", 0.001, 10_000_000)  # Redis Stack / Redis 8
r.execute_command("BF.ADD", "ids:users", 42)
if not r.execute_command("BF.EXISTS", "ids:users", uid): return None   # penetration guard
```

---

## 6. Locks, rate limiting, idempotency

### 6.1 Distributed lock with token + fencing
```python
UNLOCK = "if redis.call('GET',KEYS[1])==ARGV[1] then return redis.call('DEL',KEYS[1]) else return 0 end"
EXTEND = "if redis.call('GET',KEYS[1])==ARGV[1] then return redis.call('PEXPIRE',KEYS[1],ARGV[2]) else return 0 end"

class Lock:
    def __init__(self, r, name, ttl_ms=30_000): self.r, self.key, self.ttl, self.tok = r, f"lock:{name}", ttl_ms, uuid4().hex
    def acquire(self):
        if self.r.set(self.key, self.tok, nx=True, px=self.ttl):
            self.fence = self.r.incr("fence:" + self.key)      # monotonic fencing token → pass to the resource
            return True
        return False
    def extend(self): return self.r.eval(EXTEND, 1, self.key, self.tok, self.ttl) == 1   # watchdog thread calls periodically
    def release(self): self.r.eval(UNLOCK, 1, self.key, self.tok)

# redis-py built-in: with r.lock("res", timeout=30, blocking_timeout=5): ...   (token + Lua release, no fencing)
```
```java
// Lettuce
String tok = UUID.randomUUID().toString();
boolean got = "OK".equals(sync.set("lock:res", tok, SetArgs.Builder.nx().px(30_000)));
long fence = got ? sync.incr("fence:lock:res") : -1;
// release
sync.eval("if redis.call('GET',KEYS[1])==ARGV[1] then return redis.call('DEL',KEYS[1]) else return 0 end", ScriptOutputType.INTEGER, new String[]{"lock:res"}, tok);
// Spring Integration: RedisLockRegistry registry = new RedisLockRegistry(cf, "locks", 30_000); Lock l = registry.obtain("res"); l.tryLock(5, SECONDS)
```
- resource side: `UPDATE t SET … WHERE id=? AND fence < ?` → rejects writes from an expired holder

### 6.2 Rate limiters (fixed, sliding, token bucket)
```python
# fixed window
def allow_fixed(uid, limit=100, window=60):
    key = f"rl:{uid}:{int(time.time()) // window}"
    with r.pipeline() as p:
        p.incr(key); p.expire(key, window); n, _ = p.execute()
    return n <= limit

# sliding window log (Lua, atomic)
SLIDING = r.register_script("""
redis.call('ZREMRANGEBYSCORE', KEYS[1], 0, ARGV[1] - ARGV[2])
local n = redis.call('ZCARD', KEYS[1])
if n >= tonumber(ARGV[3]) then return 0 end
redis.call('ZADD', KEYS[1], ARGV[1], ARGV[1] .. '-' .. ARGV[4]); redis.call('PEXPIRE', KEYS[1], ARGV[2]); return 1""")
def allow_sliding(uid, limit=100, window_ms=60_000):
    return SLIDING(keys=[f"rl:{uid}"], args=[int(time.time()*1000), window_ms, limit, uuid4().hex]) == 1

# token bucket (Lua)
BUCKET = r.register_script("""
local rate, cap, now, cost = tonumber(ARGV[1]), tonumber(ARGV[2]), tonumber(ARGV[3]), tonumber(ARGV[4])
local b = redis.call('HMGET', KEYS[1], 'tokens', 'ts')
local tokens = tonumber(b[1]) or cap; local ts = tonumber(b[2]) or now
tokens = math.min(cap, tokens + (now - ts) * rate / 1000)
local ok = 0
if tokens >= cost then tokens = tokens - cost; ok = 1 end
redis.call('HSET', KEYS[1], 'tokens', tokens, 'ts', now); redis.call('PEXPIRE', KEYS[1], math.ceil(cap / rate * 1000) * 2)
return ok""")
def allow_bucket(uid, rate=10, cap=50): return BUCKET(keys=[f"tb:{uid}"], args=[rate, cap, int(time.time()*1000), 1]) == 1
```
```java
// Java: same Lua via RedisScript<Long> (Spring) or sync.evalsha; Bucket4j + Redis (Lettuce/Redisson) gives token bucket out of the box
@Bean RedisScript<Long> slidingScript() { return RedisScript.of(new ClassPathResource("sliding.lua"), Long.class); }
boolean allowed = redis.execute(slidingScript, List.of("rl:" + uid), String.valueOf(nowMs), "60000", "100", UUID.randomUUID().toString()) == 1L;
```

### 6.3 Idempotency key
```python
def idempotent(key, ttl=86_400):
    def deco(fn):
        def wrapper(*a, **k):
            k_ = f"idem:{key(*a, **k)}"
            if not r.set(k_, "IN_PROGRESS", nx=True, ex=60): 
                cached = r.get(k_)
                if cached == "IN_PROGRESS": raise Conflict("retry later")
                return json.loads(cached)
            try:
                res = fn(*a, **k); r.set(k_, json.dumps(res), ex=ttl); return res
            except Exception: r.delete(k_); raise
        return wrapper
    return deco
```
```java
// Spring filter / interceptor: header Idempotency-Key → SET NX; store response body on success (same shape as above)
Boolean first = redis.opsForValue().setIfAbsent("idem:" + key, "IN_PROGRESS", Duration.ofMinutes(1));
```

### 6.4 Redisson (Java) helpers
```java
RedissonClient rd = Redisson.create(Config.fromYAML(...));          // supports sentinel/cluster
RLock lock = rd.getLock("res");
if (lock.tryLock(5, 30, TimeUnit.SECONDS)) { try { work(); } finally { lock.unlock(); } }   // watchdog auto-extends if leaseTime = -1
RRateLimiter rl = rd.getRateLimiter("api:" + uid); rl.trySetRate(RateType.OVERALL, 100, 1, RateIntervalUnit.MINUTES); rl.tryAcquire();
RMapCache<String, User> m = rd.getMapCache("users"); m.put("42", u, 10, TimeUnit.MINUTES);   // per-entry TTL
RBloomFilter<Long> bf = rd.getBloomFilter("ids"); bf.tryInit(10_000_000L, 0.001);
```

---

## 7. Messaging: Pub/Sub, Streams, queues

### 7.1 Pub/Sub
```python
r.publish("cache:invalidate", "user:42")
ps = r.pubsub(ignore_subscribe_messages=True)
ps.subscribe("cache:invalidate"); ps.psubscribe("events:*")
for msg in ps.listen(): local_cache.pop(msg["data"], None)      # run in its own thread; no history, no ack
# cluster: r.spublish / ps.ssubscribe (sharded, 7.0)
```
```java
StatefulRedisPubSubConnection<String,String> pub = client.connectPubSub();
pub.addListener(new RedisPubSubAdapter<>() { public void message(String ch, String m) { local.remove(m); } });
pub.sync().subscribe("cache:invalidate");
sync.publish("cache:invalidate", "user:42");
```
```java
// Spring
@Bean RedisMessageListenerContainer container(RedisConnectionFactory cf, MessageListenerAdapter l) {
    var c = new RedisMessageListenerContainer(); c.setConnectionFactory(cf); c.addMessageListener(l, new ChannelTopic("cache:invalidate")); return c; }
@Bean MessageListenerAdapter listener(Invalidator inv) { return new MessageListenerAdapter(inv, "onMessage"); }
redis.convertAndSend("cache:invalidate", "user:42");
```

### 7.2 Streams with consumer groups, retry, DLQ
```python
# producer
r.xadd("jobs", {"type": "resize", "id": "9"}, maxlen=1_000_000, approximate=True)
# group (idempotent create)
try: r.xgroup_create("jobs", "workers", id="0", mkstream=True)
except redis.ResponseError as e:
    if "BUSYGROUP" not in str(e): raise
# consumer loop
def worker(name, max_deliveries=5):
    while True:
        for stream, entries in r.xreadgroup("workers", name, {"jobs": ">"}, count=10, block=5000) or []:
            for eid, fields in entries:
                try: handle(fields); r.xack("jobs", "workers", eid)
                except Exception: pass                                        # stays in PEL → reclaimed later
        # reclaim stale entries from dead consumers (idle > 60 s)
        _, claimed, _ = r.xautoclaim("jobs", "workers", name, min_idle_time=60_000, start_id="0-0", count=10)
        for eid, fields in claimed:
            deliveries = next((p["times_delivered"] for p in r.xpending_range("jobs", "workers", eid, eid, 1)), 1)
            if deliveries > max_deliveries:
                r.xadd("jobs:dlq", {**fields, "orig_id": eid, "reason": "max_deliveries"}); r.xack("jobs", "workers", eid); continue
            try: handle(fields); r.xack("jobs", "workers", eid)
            except Exception: pass
# ops
r.xinfo_groups("jobs"); r.xpending("jobs", "workers"); r.xlen("jobs"); r.xtrim("jobs", maxlen=100_000, approximate=True)
```
```java
sync.xadd("jobs", XAddArgs.Builder.maxlen(1_000_000).approximateTrimming(), Map.of("type", "resize", "id", "9"));
try { sync.xgroupCreate(XReadArgs.StreamOffset.from("jobs", "0"), "workers", XGroupCreateArgs.Builder.mkstream()); } catch (RedisBusyException ignore) {}
List<StreamMessage<String,String>> msgs = sync.xreadgroup(Consumer.from("workers", "w1"), XReadArgs.Builder.count(10).block(5000),
        XReadArgs.StreamOffset.lastConsumed("jobs"));
for (var m : msgs) { try { handle(m.getBody()); sync.xack("jobs", "workers", m.getId()); } catch (Exception e) { /* left pending */ } }
ClaimedMessages<String,String> claimed = sync.xautoclaim("jobs", XAutoClaimArgs.Builder.xautoclaim(Consumer.from("workers", "w1"), 60_000, "0-0").count(10));
```
```java
// Spring Data Redis StreamMessageListenerContainer
@Bean StreamMessageListenerContainer<String, MapRecord<String,String,String>> streamContainer(RedisConnectionFactory cf) {
    var c = StreamMessageListenerContainer.create(cf, StreamMessageListenerContainerOptions.builder().pollTimeout(Duration.ofSeconds(5)).batchSize(10).build());
    c.receive(Consumer.from("workers", "w1"), StreamOffset.create("jobs", ReadOffset.lastConsumed()), rec -> {
        handle(rec.getValue()); redis.opsForStream().acknowledge("jobs", "workers", rec.getId()); });   // receive() = manual ack; receiveAutoAck() auto
    c.start(); return c;
}
redis.opsForStream().add(StreamRecords.newRecord().in("jobs").ofMap(Map.of("type", "resize")));
```

### 7.3 List queue and delay queue
```python
# reliable list queue
job = r.blmove("q:jobs", "q:processing", 5, "RIGHT", "LEFT")
if job: handle(job); r.lrem("q:processing", 1, job)             # reaper re-queues stale q:processing entries

# delay queue on sorted set: atomic claim of due jobs
CLAIM = r.register_script("""
local due = redis.call('ZRANGEBYSCORE', KEYS[1], 0, ARGV[1], 'LIMIT', 0, ARGV[2])
if #due > 0 then redis.call('ZREM', KEYS[1], unpack(due)) end
return due""")
r.zadd("due", {json.dumps(job): run_at_ms})
for j in CLAIM(keys=["due"], args=[int(time.time()*1000), 100]): handle(json.loads(j))
```

### 7.4 Keyspace notifications
```bash
redis-cli CONFIG SET notify-keyspace-events Ex        # E = keyevent channel, x = expired
```
```python
ps = r.pubsub(); ps.psubscribe("__keyevent@0__:expired")
for m in ps.listen():
    if m["type"] == "pmessage": on_expired(m["data"])   # fires when actually deleted (lazy/active) — not exact; best effort only
```

---

## 8. Redis Stack: JSON, Search, vectors, Bloom
```python
# JSON
r.json().set("user:42", "$", {"name": "ann", "tags": ["a"], "emb": [0.1] * 4})
r.json().get("user:42", "$.name"); r.json().arrappend("user:42", "$.tags", "b"); r.json().numincrby("user:42", "$.visits", 1)

# Search index over JSON with a vector field (HNSW) — semantic cache
from redis.commands.search.field import TextField, TagField, VectorField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query
r.ft("idx:llm").create_index(
    [TagField("$.model", as_name="model"), TextField("$.prompt", as_name="prompt"),
     VectorField("$.emb", "HNSW", {"TYPE": "FLOAT32", "DIM": 1536, "DISTANCE_METRIC": "COSINE", "M": 16, "EF_CONSTRUCTION": 200}, as_name="emb")],
    definition=IndexDefinition(prefix=["llmcache:"], index_type=IndexType.JSON))

def semantic_lookup(model, emb, threshold=0.05):
    q = (Query("(@model:{$model})=>[KNN 1 @emb $vec AS score]").sort_by("score").return_fields("score", "$.answer")
         .dialect(2).paging(0, 1))
    res = r.ft("idx:llm").search(q, {"vec": np.asarray(emb, dtype=np.float32).tobytes(), "model": model})
    return res.docs[0]["$.answer"] if res.docs and float(res.docs[0]["score"]) < threshold else None

def semantic_store(model, prompt, emb, answer, ttl=86_400):
    key = f"llmcache:{uuid4().hex}"
    r.json().set(key, "$", {"model": model, "prompt": prompt, "emb": emb, "answer": answer}); r.expire(key, ttl)

# Bloom / Count-Min / Top-K (RedisBloom)
r.bf().reserve("seen", 0.001, 10_000_000); r.bf().add("seen", "id-1"); r.bf().exists("seen", "id-1")
r.topk().reserve("hot", 10); r.topk().add("hot", "k1")
```
```java
// Jedis has first-class Stack support (UnifiedJedis.jsonSet / ftCreate / ftSearch); Lettuce via custom commands or lettuce-modules
UnifiedJedis j = new UnifiedJedis("redis://localhost:6379");
j.jsonSet("user:42", Path2.ROOT_PATH, Map.of("name", "ann"));
j.ftCreate("idx:llm", FTCreateParams.createParams().on(IndexDataType.JSON).addPrefix("llmcache:"),
    TagField.of("$.model").as("model"), VectorField.builder().fieldName("$.emb").as("emb").algorithm(VectorAlgorithm.HNSW)
        .addAttribute("TYPE", "FLOAT32").addAttribute("DIM", 1536).addAttribute("DISTANCE_METRIC", "COSINE").build());
SearchResult sr = j.ftSearch("idx:llm", "(@model:{gpt})=>[KNN 1 @emb $vec AS score]",
    FTSearchParams.searchParams().addParam("vec", vecBytes).sortBy("score", SortingOrder.ASC).dialect(2));
// Spring AI: RedisVectorStore bean wraps this for RAG / semantic cache
```

---

## 9. Spring Boot wiring
```yaml
spring:
  data:
    redis:
      host: localhost
      port: 6379
      password: ${REDIS_PW:}
      database: 0
      timeout: 500ms
      connect-timeout: 500ms
      ssl.enabled: false
      client-type: lettuce
      lettuce:
        pool: { max-active: 32, max-idle: 16, min-idle: 4, max-wait: 200ms }   # needs commons-pool2; only for blocking/tx use
        shutdown-timeout: 100ms
      # sentinel: { master: mymaster, nodes: s1:26379,s2:26379,s3:26379 }
      # cluster:  { nodes: n1:7000,n2:7001, max-redirects: 3 }
  cache:
    type: redis
    redis: { time-to-live: 10m, cache-null-values: false, key-prefix: "app:", use-key-prefix: true }
  session:
    store-type: redis            # spring-session-data-redis → HttpSession in Redis (Hash + TTL)
    timeout: 30m
```
```java
@Configuration
class RedisConfig {
    @Bean RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory cf) {
        var t = new RedisTemplate<String, Object>(); t.setConnectionFactory(cf);
        t.setKeySerializer(new StringRedisSerializer()); t.setHashKeySerializer(new StringRedisSerializer());
        var json = new GenericJackson2JsonRedisSerializer();
        t.setValueSerializer(json); t.setHashValueSerializer(json);
        return t;
    }
    @Bean LettuceClientConfigurationBuilderCustomizer lettuceCustomizer() {
        return b -> b.clientOptions(ClientOptions.builder()
            .timeoutOptions(TimeoutOptions.enabled(Duration.ofMillis(500)))
            .disconnectedBehavior(ClientOptions.DisconnectedBehavior.REJECT_COMMANDS)   // fail fast, don't queue forever
            .autoReconnect(true).build())
            .readFrom(ReadFrom.REPLICA_PREFERRED);
    }
}
// Resilience: wrap cache reads in a circuit breaker (Resilience4j) → fall through to DB when Redis is down
```

---

## 10. Config tables

### 10.1 Server config
| Config | Default | What it trades | Change when |
| --- | --- | --- | --- |
| `maxmemory` | 0 (unlimited) | OOM-kill ↔ eviction | always set (≈ 70–80 % of RAM, leave room for fork/COW) |
| `maxmemory-policy` | noeviction | fail writes ↔ evict | `allkeys-lru/lfu` cache; `noeviction` for queues/locks instance |
| `maxmemory-samples` | 5 | eviction accuracy ↔ CPU | 10 for closer-to-true LRU |
| `lazyfree-lazy-*` | no (7.x: some yes) | main-thread free ↔ background | yes for big values |
| `appendonly` / `appendfsync` | no / everysec | durability ↔ throughput | yes/everysec for non-cache |
| `save` | 3600 1 300 100 60 10000 | snapshot frequency ↔ fork cost | `""` for pure cache |
| `repl-backlog-size` | 1 MB | partial resync window ↔ memory | minutes of write traffic |
| `repl-diskless-sync` | yes (7.0+) | disk I/O ↔ memory during sync | keep yes on slow disks |
| `min-replicas-to-write` / `-max-lag` | 0 / 10 | availability ↔ bounded loss | 1 / 10 for important data |
| `timeout` | 0 | idle connection reaping | 300 for many short-lived clients |
| `tcp-keepalive` | 300 | dead-peer detection | lower behind NAT/LB |
| `maxclients` | 10000 | connections ↔ fd/memory | raise with ulimit for many pods |
| `client-output-buffer-limit` | normal 0; replica 256mb 64mb 60; pubsub 32mb 8mb 60 | protect server ↔ disconnect slow clients | tighten pubsub, raise replica for big syncs |
| `io-threads` / `io-threads-do-reads` | 1 / no | throughput ↔ CPU | cores−1 / yes when network-bound |
| `hz` | 10 | expire/evict responsiveness ↔ CPU | 20–50 for many TTL keys |
| `active-expire-effort` | 1 | expired memory reclaim ↔ latency | up to 10 under TTL pressure |
| `activedefrag` | no | fragmentation ↔ CPU | yes when ratio > 1.5 |
| `hash/zset/set/list-max-listpack-*` | 128/64 etc. | memory ↔ O(n) ops | raise modestly (256/128) for memory |
| `slowlog-log-slower-than` | 10000 µs | visibility ↔ log volume | 1000–5000 |
| `latency-monitor-threshold` | 0 | latency events | 100 ms |
| `notify-keyspace-events` | "" | events ↔ CPU | only the classes you need |
| `cluster-node-timeout` | 15000 | false failover ↔ detection | 5000–15000 |
| `cluster-require-full-coverage` | yes | consistency ↔ partial availability | no for cache clusters |
| `cluster-allow-reads-when-down` | no | stale reads during outage | yes for cache |
| `protected-mode` / `bind` / `requirepass` / ACL / `tls-port` | on / 127.0.0.1 | security | always in prod |
| `rename-command` | — | hide dangerous cmds (legacy) | prefer ACL `-@dangerous` |

### 10.2 Client config
| Client | Key settings | Note |
| --- | --- | --- |
| redis-py | `socket_timeout`, `socket_connect_timeout`, `retry`/`retry_on_timeout`, `max_connections`, `health_check_interval`, `decode_responses`, `protocol=3` | one `Redis` per process; pool internal; `RedisCluster` for cluster |
| Lettuce | `ClientOptions.timeoutOptions`, `disconnectedBehavior`, `autoReconnect`, `ReadFrom`, `ClusterTopologyRefreshOptions` | one shared connection is fine (multiplexed); pool only for MULTI/WATCH/BLPOP |
| Jedis | `JedisPoolConfig(maxTotal, maxIdle, minIdle, maxWait)`, `testOnBorrow` | blocking; one connection per thread |
| Spring Data Redis | `spring.data.redis.timeout`, `lettuce.pool.*`, serializers, `cache.redis.time-to-live` | `StringRedisTemplate` for strings, custom `RedisTemplate` for JSON |
| Redisson | `lockWatchdogTimeout` (30 s), `retryAttempts`, `connectionPoolSize`, `readMode` | higher-level primitives, heavier |

---

## 11. Observability and testing
| Signal (`INFO` / exporter) | Meaning | Alert |
| --- | --- | --- |
| `used_memory` / `maxmemory`, `used_memory_rss` | headroom, fragmentation | > 85 %; ratio > 1.5 |
| `evicted_keys`, `expired_keys` | pressure | evictions on a non-cache instance = bug |
| `keyspace_hits/(hits+misses)` | hit ratio | drop vs baseline |
| `instantaneous_ops_per_sec`, `total_commands_processed` | load | saturation of one core |
| `connected_clients`, `rejected_connections`, `blocked_clients` | connection health | rejected > 0 |
| `master_repl_offset − slave_repl_offset`, `master_link_status` | replication lag | lag > seconds, link down |
| `rdb_last_bgsave_status`, `aof_last_write_status`, `latest_fork_usec` | persistence health | err; fork > 100 ms |
| `SLOWLOG`, `LATENCY LATEST` | stalls | any > 10 ms entries |
| `cluster_state`, `cluster_slots_ok` | cluster health | ≠ ok / < 16384 |
| stream `XINFO GROUPS` `lag`, `pending` | consumer backlog | growing |
- Testing
```java
// Testcontainers
static GenericContainer<?> redis = new GenericContainer<>("redis:8").withExposedPorts(6379);
@DynamicPropertySource static void props(DynamicPropertyRegistry r) {
    r.add("spring.data.redis.host", redis::getHost); r.add("spring.data.redis.port", redis::getFirstMappedPort); }
```
```python
# pytest: testcontainers-python or fakeredis (in-memory, supports Lua via lupa) for unit tests
import fakeredis; r = fakeredis.FakeRedis(decode_responses=True)
from testcontainers.redis import RedisContainer
with RedisContainer("redis:8") as c: r = c.get_client()
```
- Tests worth writing: lock release only by owner (wrong token → 0); lock expiry + fencing token rejects stale writer; rate limiter boundary (limit, limit+1, window roll); cache-aside null marker TTL; stampede test with 100 concurrent misses → 1 loader call; stream consumer crash → `XAUTOCLAIM` redelivers, DLQ after N; failover (sentinel) → client reconnects and writes resume; cluster `CROSSSLOT` guard in key naming

---

## References
- Redis command reference and docs: data types, scripting, functions, streams, client-side caching, ACL, cluster tutorial (redis.io/docs, 7.x/8.x, accessed 2026-08)
- redis-py 5.x docs (redis.readthedocs.io): cluster, sentinel, cache, scripting
- Lettuce reference (lettuce.io): master/replica, cluster topology refresh, client-side caching; Jedis wiki (Redis Stack commands)
- Spring Data Redis reference; Spring Boot `spring.data.redis.*` properties; Spring Cache; Spring Session Redis
- Redisson wiki: distributed locks, watchdog, rate limiter
- RediSearch vector similarity docs (HNSW/FLAT params); RedisJSON; RedisBloom
- Testcontainers (Java/Python), fakeredis
- Concept pair: [1.redis.md](1.redis.md)
