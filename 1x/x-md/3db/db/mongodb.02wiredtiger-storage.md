# 03db.04mongodb.02wiredtiger-storage WiredTiger Storage Engine

> The engine under every document: a cached B+ tree with Multi-Version Concurrency Control (MVCC), a 100 milliseconds (ms) journal, and a 60 s checkpoint.

## Index

- [1. What And Why](#1-what-and-why)
- [2. Components](#2-components)
  - [2.1 Cache](#21-cache)
  - [2.2 Update Chain And MVCC](#22-update-chain-and-mvcc)
  - [2.3 Eviction And Reconciliation](#23-eviction-and-reconciliation)
  - [2.4 Checkpoint And Journal](#24-checkpoint-and-journal)
  - [2.5 Compression](#25-compression)
- [3. Cache Health In Code](#3-cache-health-in-code)
- [4. Decisions And Best Practices](#4-decisions-and-best-practices)
- [5. Failure Modes](#5-failure-modes)
- [Related](#related)

## 1. What And Why

WiredTiger is the default engine since 3.2 and the only one since 4.2 (MMAPv1 removed).

- What: B+ tree row-store
  - MVCC snapshot isolation
  - Copy-on-write page reconciliation
  - Block compression
  - Write-ahead journal
- MMAPv1 problems it fixed
  - Collection-level (earlier database-level) locks capped write throughput regardless of hardware
  - In-place updates with padding; a grown document had to MOVE
    - Every index entry pointing at it was rewritten
  - No compression ⇒ field-name repetition paid in full
  - Operating System (OS) page cache ⇒ the engine controlled no eviction policy
- Owning the cache unlocked the rest
  - MVCC → commit timestamps → `recoverToStableTimestamp` (rollback by storage rewind, 4.0)
- Neighbours
  - InnoDB: B+ tree MVCC, but clustered on the primary key
  - RocksDB / Log-Structured Merge-tree (LSM): write-optimized (MongoRocks, TiKV)
  - Aurora-style log-structured storage: what Amazon DocumentDB uses instead
- ⚠️ Not the OS page cache: two caches to size (WiredTiger + filesystem)
- Wrong answer to: write-saturated append streams where an LSM's sequential writes win

```text
write ─▶ ┌──────────────────────────────────────────┐
         │ cache: leaf page image + per-key update   │
         │ chain [txn105]→[txn99]→[txn87]  (MVCC)    │
         └──────┬───────────────┬──────────────┬────┘
                ▼               ▼              ▼
         ┌────────────┐  ┌────────────┐  ┌────────────┐
         │ JOURNAL    │  │ EVICTION   │  │ CHECKPOINT │
         │ fsync      │  │ reconcile  │  │ every 60 s │
         │ ~100 ms    │  │ → new blks │  │ snapshot   │
         └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
               └───────────────┼───────────────┘
                               ▼
         ┌──────────────────────────────────────────┐
         │ data files (snappy blocks) + OS fs cache │
         └──────────────────────────────────────────┘
```

Every write lands in cache first; durability comes from the journal, recovery from the checkpoint.

## 2. Components

Each part has one job; the oplog is itself a WiredTiger collection.

| Component | Job |
| --- | --- |
| Cache | Hold decompressed page images and update chains |
| Update chain | Recent and uncommitted versions per key (MVCC) |
| Eviction | Reclaim cache by writing dirty pages to new blocks |
| Checkpoint | Crash-consistent on-disk snapshot root |
| Journal (Write-Ahead Log, WAL) | Durability between checkpoints |
| Oplog | Ordered idempotent write log for replication |

### 2.1 Cache

The cache holds decompressed pages; its size decides whether reads touch disk.

- Default size: `max(50% of (RAM − 1 GB), 256 MB)` (`cacheSizeGB`, MongoDB 8.0 docs)
- The other half of Random-Access Memory (RAM) is deliberate
  - Filesystem cache of compressed blocks ⇒ a miss is memcpy + decompress, not disk
  - Connections and aggregation memory
- ⚠️ Compression does NOT save WiredTiger cache; images are decompressed
  - The most common wrong statement about MongoDB memory
- Eviction thresholds (defaults; verify with `serverStatus().wiredTiger.cache`)
  - ~80% used: background eviction starts
  - ~95% used: application threads are recruited to evict
  - Dirty data: ~5% target, ~20% trigger
- App-thread eviction ⇒ every operation stalls at once ("everything got slow")
- Indexes live in the same cache; with 8 indexes they can dominate
- Sizing input = working set (hot docs + their index pages), not total data
  - 2 terabytes (TB) collection with a 20 gigabytes (GB) hot subset needs cache for 20 GB
  - Working set 40 GB ⇒ ~96 GB RAM, not 64 GB

### 2.2 Update Chain And MVCC

Each key keeps a newest-first chain of versions tagged with a transaction id.

- Since 4.0 versions also carry a commit timestamp
- A reader takes a snapshot and walks to the newest visible version
  - Read cost grows with concurrent versions of a key
- Small `$set` updates use `WT_MODIFY`: a delta, not a full image
  - ⚠️ Only below a size threshold; growing a doc or touching arrays writes a full image
- Conflict rule: two concurrent writers on one key ⇒ the later gets `WT_ROLLBACK`
  - Outside a transaction: surfaced as `WriteConflict`, retried by the server
  - Inside a transaction: `TransientTransactionError` to the client
- Long transactions or `majority` reads pin the oldest timestamp ⇒ old versions stay cached node-wide

### 2.3 Eviction And Reconciliation

Dirty pages are written to NEW blocks; nothing is overwritten in place.

- Old blocks are freed after the next checkpoint
- Result: no torn-page protection needed (contrast InnoDB's doublewrite buffer)
  - A torn write can only hit blocks no checkpoint root points at
- Cost: write amplification
  - One-field update in a 32 kilobytes (KB) leaf rewrites the whole leaf
- Cost: fragmentation
  - Disk used can sit well above `collStats.size`
  - `compact` blocks that node ⇒ run rolling on secondaries, or initial-sync a fresh member

### 2.4 Checkpoint And Journal

The checkpoint is the restart point; the journal fills the gap since it.

- Checkpoint every 60 s (or on `fsync` / shutdown); the metadata root is written last, atomically
- Recovery: open the newest checkpoint → replay the journal forward
- Journal: group-committed, fsynced every 100 ms (`storage.journal.commitIntervalMs`)
  - Or immediately when a write asks `j: true`
- `{w: 1}` alone = acknowledged from primary memory
  - Possibly not on the primary's disk
  - Definitely not on any secondary
  - A real loss window, not a theoretical one
- Without the journal: lose up to 60 s (cannot be disabled on replica sets since 4.0)
- `j: true` with `w: "majority"` on 3+ data nodes is mostly redundant ([11read-write-concern](04mongodb.11read-write-concern.md))

### 2.5 Compression

Collections use block compression; indexes use prefix compression.

- Collections: snappy default; `zstd` (4.2+) and `zlib` available
- Indexes: prefix compression (shared key prefixes once per page)
  - Index pages are traversed constantly; block decompression per descent is too costly
- Order of magnitude: snappy 2–4× on document data; zstd better at more Central Processing Unit (CPU)
  - Measure on your data; never quote an unobserved ratio

| Option | Buys | Costs | Choose when |
| --- | --- | --- | --- |
| snappy | Cheap CPU, ~2–4× | Larger disk than zstd | Default |
| zstd | Best ratio | More CPU on eviction and read | Storage-bound, CPU < ~50% |
| none | Lowest CPU | Full storage, worse fs-cache density | Already-compressed blobs only |

## 3. Cache Health In Code

The signal is the RATE of cache misses, not utilization.

- Utilization sits near 80% permanently by design ⇒ useless as an alert
- Watch
  - `bytes read into cache` rate: flat near zero at steady state = sized right
  - `pages evicted by application threads` > 0 = already an incident
  - `tracked dirty bytes`: checkpoint pressure

**Java**

```java
// infra/_03db_04mongodb/MongoAdmin.java
// Cache health: the signal is the RATE of "bytes read into cache" (misses) and any eviction done by
// application threads, not utilization (which sits near 80% by design).
public Document cacheHealth() {
    Document cache = db.runCommand(new Document("serverStatus", 1))
            .get("wiredTiger", Document.class)
            .get("cache", Document.class);
    return new Document("maxBytes", cache.get("maximum bytes configured"))
            .append("currentBytes", cache.get("bytes currently in the cache"))
            .append("dirtyBytes", cache.get("tracked dirty bytes in the cache"))
            .append("bytesReadIntoCache", cache.get("bytes read into cache"))
            .append("pagesEvictedByAppThreads", cache.get("pages evicted by application threads"));
}
```

**Python**

```python
# app/infra/_03db_04mongodb.py
def cache_health(self) -> Doc:
    """Watch the RATE of bytes read into cache and app-thread eviction, not utilization (~80% by design)."""
    cache = self.db.command("serverStatus")["wiredTiger"]["cache"]
    return {
        "maxBytes": cache["maximum bytes configured"],
        "currentBytes": cache["bytes currently in the cache"],
        "dirtyBytes": cache["tracked dirty bytes in the cache"],
        "bytesReadIntoCache": cache["bytes read into cache"],
        "pagesEvictedByAppThreads": cache["pages evicted by application threads"],
    }
```

**Catch**

- Counters are cumulative: sample twice and diff to get a rate
- DocumentDB returns a reduced `serverStatus` without these WiredTiger fields
- Bigger instance vs read replica: if reads miss cache, a replica has the same miss ratio ⇒ scale up

## 4. Decisions And Best Practices

| Designers chose | Rejected | Cost |
| --- | --- | --- |
| B+ tree row-store | LSM | Worse random-write amplification |
| Engine-managed cache | OS page cache (MMAPv1) | Two caches to size |
| Copy-on-write reconcile | In-place + doublewrite | Write amplification, fragmentation |
| Compression on by default | Off | CPU on every page read/write |

| You decide | Deciding variable |
| --- | --- |
| Cache size | Working set; `bytes read into cache` near zero = enough |
| snappy vs zstd | Storage bill vs CPU headroom |
| `j: true` per write | Is a 100 ms primary-crash window acceptable without majority? |
| Instance memory | Cache ≈ 50% of RAM ⇒ double the working set |

- Best practices (rule → failure prevented)
  - Size RAM from the working set, then double → latency cliff when the set exceeds cache
  - Alert on cache-miss rate, not utilization → paging after the incident started
  - Alert on app-thread eviction > 0 → every p99 degrading at once
  - Never disable the journal → losing up to 60 s on unclean shutdown
  - Narrow `$set`, not full replace → update-chain growth, full-page rewrites
  - `maxTimeMS` on analytic clients; analytics node via tags → a Business Intelligence (BI) scan evicting Online Transaction Processing (OLTP)

## 5. Failure Modes

| Failure | Trigger | Detect | Fix |
| --- | --- | --- | --- |
| Eviction storm | Working set > cache; full scan | App-thread eviction > 0 | RAM; index the scan; analytics node |
| Write-conflict storm | Hot single doc (counter) | `metrics.operation.writeConflicts` | Shard the counter; move it out |
| Checkpoint stall | Dirty cache, slow disk | p99 sawtooth, 60 s period | Faster disk; lower dirty target |
| Journal fsync latency | Slow disk; Elastic Block Store (EBS) credits gone | `wiredTiger.log` fsync time | Provisioned Input/Output Operations Per Second (IOPS); separate volume |
| Disk fill | Copy-On-Write (COW) + large deletes | Disk used ≫ `collStats.size` | Rolling `compact`; fresh initial sync |

- 60 s sawtooth diagnosis
  - Checkpoint duration growing → disk-bound → IOPS / separate journal volume
  - Dirty bytes hit trigger before checkpoint → lower `eviction_dirty_target` (smooth baseline beats spikes)
  - First check for a self-inflicted burst (1 M updates in 5 s); throttling is cheaper
- Canonical pattern: the analytics query that took down OLTP
  - Symptom: nightly, unrelated point reads 50× slower for ~20 min
  - Cause: unindexed BI `find()` on the primary swept the collection through cache
  - Fix: tagged analytics secondary + covering index
  - Guardrail: `maxTimeMS`, cache-miss alert, revoke primary access from BI credentials
- Historical: pre-4.0 rollback replayed files capped at 300 megabytes (MB) ⇒ larger needed a full resync (4.0 release notes)
- Exceptions
  - `WriteConflict`: retryable, mostly invisible outside transactions
  - `ExceededMemoryLimit` (100 MB blocking stage without `allowDiskUse`): change the query
  - Disk full: terminal for the node; a majority-write cluster survives one such node

## Related

- [00index](04mongodb.00index.md)
- [01document-model-bson](04mongodb.01document-model-bson.md)
- [10replica-sets-oplog](04mongodb.10replica-sets-oplog.md)
