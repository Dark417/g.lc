# Storage Systems: A Selection Framework

> Companion to `document-store-comparison.md`, which was scoped to one product category. This
> document rebuilds the landscape on the axis that actually predicts behaviour.
>
> Price and version anchors are as of mid-2026, us-east-1 where AWS-specific. Treat every number as
> **order of magnitude for comparison** unless it is a documented hard limit.

---

## 0. The usual taxonomy is a marketing artifact

"Document / key-value / wide-column / graph / relational" is how vendors segment a market. It
predicts almost nothing about how a system behaves, because it describes the **API surface**, not the
**storage engine**. Two consequences:

- MongoDB and Cassandra are both called "NoSQL." MongoDB is a B+ tree with a single write primary;
  Cassandra is an LSM tree with masterless quorum writes. They share nothing that matters — not the
  write path, not the read amplification profile, not the failure model, not the cost curve.
- PostgreSQL with a `jsonb` column and MongoDB have nearly identical _capabilities_ for
  semi-structured data. The taxonomy puts them in different families.

The categorization that predicts behaviour is: **what data structure answers a read, and what path
does a write take to durability.** Everything you care about — latency shape, write amplification,
what queries are possible, what the bill looks like — falls out of those two.

---

## 1. The seven engine families

| Family                          | Read structure                                                               | Write path                                                                 | Optimized for                                                       | Structurally bad at                                                                         |
| ------------------------------- | ---------------------------------------------------------------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| **B+ tree (page-oriented)**     | Balanced tree, high fanout, 3–4 levels for billions of keys                  | Modify page in place or copy-on-write; page splits                         | Predictable point + range reads; mixed read/write                   | Random-write-saturated workloads (page split + write amplification)                         |
| **LSM tree**                    | Memtable + N levels of immutable sorted files, bloom-filtered                | Append to WAL + in-memory table, flush sequentially, compact in background | Very high write throughput; sequential I/O                          | Read latency variance (must check multiple levels); space amplification during compaction   |
| **Inverted index**              | term → posting list of doc IDs; plus columnar `doc_values` and BKD trees     | Buffer → immutable segment on refresh → background merge                   | "Which documents match this arbitrary predicate", relevance ranking | Being a system of record; point updates (delete-tombstone + reinsert); real-time visibility |
| **Columnar**                    | Values stored per column, compressed and encoded; sparse or zone-map indexes | Bulk append of large blocks; merges                                        | Scanning many rows, few columns; aggregation                        | Point reads; single-row updates; high-frequency small writes                                |
| **Hash-partitioned KV**         | Hash(key) → partition → local B-tree or LSM                                  | Quorum-replicated write to the partition's replicas                        | Bounded latency at any data size; horizontal scale by key           | Anything not addressed by key; cross-partition queries and joins                            |
| **In-memory structures**        | Native data structures in RAM (hash, skip list, radix tree)                  | RAM write + optional async persistence                                     | Sub-millisecond ops; complex atomic data-structure primitives       | Data larger than RAM; durability guarantees you'd bet a ledger on                           |
| **Immutable object + manifest** | Flat key → blob; a metadata layer names which blobs form the current table   | Write whole new objects; atomically swap a metadata pointer                | Cost per byte; unbounded volume; replayability                      | Latency; partial update; anything on a request path                                         |

Everything else in this document is a product built on one of these, or a hybrid that layers two.

**The single most useful implication**: read amplification, write amplification, and space
amplification form a three-way tradeoff (the "RUM conjecture"), and you cannot optimize all three. A
B+ tree minimizes read amplification and pays in write amplification. An LSM minimizes write
amplification and pays in read and space amplification. Columnar minimizes read amplification _for
scans specifically_ and pays by making point access terrible. When someone claims a system is fast,
the useful question is "at the expense of which of the three."

---

## 2. The families in detail

### 2.1 B+ tree, page-oriented

**Mechanism.** A balanced tree of fixed-size pages (4–32 KB). Internal pages hold keys and child
pointers; leaf pages hold keys and either the row itself (clustered) or a pointer to it
(non-clustered). Fanout is in the hundreds, so a tree over 10⁹ keys is 3–4 levels deep — a point read
is 3–4 page accesses, and the upper levels are almost always cached, so the practical cost is one
disk read or zero.

**Design intention.** Minimize and _bound_ the number of I/Os per lookup, in an era where a disk seek
was 10 ms and the whole design question was "how few seeks can I get away with." The bound is what
buys predictability: a B+ tree lookup costs the same whether the table has a thousand rows or a
billion, modulo cache.

**What problem it solves.** Mixed OLTP: find one row by key, scan a range in sorted order, update in
place, all with predictable latency.

**Internal variants that matter:**

- **Clustered** (InnoDB): the leaf _is_ the row, ordered by primary key. PK lookups are one tree
  descent; secondary indexes store the PK, so a secondary lookup is two descents. Range scans on the
  PK are physically sequential.
- **Non-clustered / heap** (PostgreSQL, MongoDB WiredTiger): the tree points at a row identifier;
  the row lives elsewhere. Secondary index entries are small and stable — a row that moves doesn't
  invalidate every index. Cost: every non-covered lookup is a second random access.
- **Copy-on-write reconciliation** (WiredTiger, LMDB): dirty pages are written to _new_ blocks rather
  than overwritten. Buys cheap snapshots and removes the torn-page problem (which is why InnoDB needs
  a doublewrite buffer and WiredTiger doesn't). Pays in space amplification and fragmentation.

**Advantages.** Predictable read latency; efficient range scans; mature; supports secondary indexes
naturally; a single structure serves point and range access.

**Disadvantages.** Random writes cause page splits and rewrite whole pages for one-field changes —
write amplification on the order of the page size divided by the change size. Under a
write-saturated workload the tree is the bottleneck, and there's no configuration that fixes it.
Scaling writes requires partitioning, which is a topology decision, not a tuning knob.

**Who runs it at scale.** PostgreSQL, MySQL/InnoDB, Oracle, SQL Server, MongoDB (WiredTiger), Amazon
DocumentDB, Couchbase, SQLite, LMDB.

**Wrong answer to.** Firehose ingestion where the write rate exceeds what one primary's page cache
and disk can absorb. That's the LSM case, or the columnar-batch case.

---

### 2.2 LSM tree (log-structured merge)

**Mechanism.** Writes go to a write-ahead log (durability) and an in-memory sorted structure, usually
a skip list (the **memtable**). When the memtable fills, it is flushed _sequentially_ to an immutable
sorted file (an **SSTable**). Background **compaction** merges SSTables to bound their number and
remove overwritten/deleted keys. A read checks the memtable, then SSTables newest-to-oldest, using
**bloom filters** to skip files that certainly don't contain the key, and a block cache to avoid disk.

**Design intention.** Convert random writes into sequential writes. On spinning disks that was a 100×
difference; on SSDs it's smaller but still real, and it also reduces write wear and lets you exploit
the full sequential bandwidth of the device.

**What problem it solves.** Ingest rates that a B+ tree cannot absorb — time series, event streams,
high-cardinality upserts, write-heavy operational stores.

**Compaction strategies — the real tuning surface:**

| Strategy               | Write amplification                          | Space amplification                            | Read amplification               | Use when                                                       |
| ---------------------- | -------------------------------------------- | ---------------------------------------------- | -------------------------------- | -------------------------------------------------------------- |
| **Leveled (LCS)**      | High — a key may be rewritten once per level | Low (~1.1×)                                    | Low — at most one file per level | Read-heavy, space-constrained                                  |
| **Size-tiered (STCS)** | Low                                          | High (can transiently need ~2× the table size) | High — many overlapping files    | Write-heavy, disk is cheap                                     |
| **Time-window (TWCS)** | Low                                          | Low                                            | Low for time-bounded queries     | Time series with TTL — drops whole SSTables instead of merging |

**Advantages.** Extremely high write throughput; sequential I/O; compression works well on sorted
blocks; deletes and TTL are cheap (a tombstone, reclaimed at compaction).

**Disadvantages.**

- **Read amplification** — a point read may touch several files. Bloom filters make the common case
  one file, but the _tail_ is worse and more variable than a B+ tree's.
- **Compaction is a background job competing with your foreground traffic.** The classic incident
  shape is: write rate rises, compaction falls behind, SSTable count grows, read latency degrades,
  which slows everything, which makes compaction fall further behind. Congestive collapse.
- **Tombstones.** In Cassandra specifically, deleted rows leave tombstones for `gc_grace_seconds`
  (default 10 days) so that a resurrected replica can't undelete them. A workload that deletes
  heavily accumulates tombstones that must be read through, and "queue in Cassandra" is a known
  anti-pattern for exactly this reason.
- **Space amplification during compaction** — you need free disk to compact, so a full disk is
  unrecoverable without adding capacity.

**Who runs it at scale.** Cassandra, ScyllaDB, HBase, Bigtable, RocksDB (and everything built on it:
TiKV, CockroachDB's Pebble, Kafka Streams state stores, Flink state), LevelDB, InfluxDB (older
engines), Riak.

**Wrong answer to.** Workloads dominated by point reads with a strict p99, and anything needing joins
or ad-hoc predicates — these systems generally offer neither.

---

### 2.3 Inverted index

**Mechanism.** Three structures inside one index, and conflating them is the most common error:

- **Inverted index** — a term dictionary mapping each analyzed term to a **posting list** of document
  IDs (plus positions, frequencies). Answers "which documents contain T" in time proportional to the
  posting list, not to the corpus.
- **`doc_values`** — a per-segment **columnar** structure holding field values _by document ID_. This
  is what powers sorting, aggregations, and faceting. Without it, those operations are impossible;
  the inverted index is the wrong direction for them.
- **BKD trees** — block KD-trees for numeric, date, and geo range predicates.

Segments are **immutable**. A write buffers in memory plus a transaction log; a **refresh** (default
1 s in OpenSearch/Elasticsearch) seals a new segment and makes it searchable; background **merges**
combine small segments; deletes are tombstones reclaimed at merge.

**Design intention.** Invert the relationship. A row store asks "given this document, what does it
contain"; an inverted index asks "given this term, which documents have it" — which is the question a
search box actually poses. Immutable segments exist so that reads need no locking and merges can run
concurrently with everything else.

**What problem it solves.** Arbitrary boolean combinations over many fields, full-text matching with
analysis (stemming, synonyms, language handling), and relevance ranking. For a B+ tree system, "filter
on any 5 of 150 attributes" is a combinatorial index problem with no solution; for an inverted index
it's one query.

**Advantages.** The only family where ad-hoc multi-attribute filtering scales. Rich aggregations and
faceting. Horizontal scale by shard. Relevance scoring is native.

**Disadvantages.**

- **No transactions.** Optimistic concurrency on a single document (`if_seq_no` / `if_primary_term`)
  and nothing more.
- **Near-real-time, not real-time.** A write is invisible until refresh.
- **Primary shard count is fixed at index creation.** You can `_split` by an integer factor, `_shrink`,
  or reindex — you cannot freely resize. Under-shard and you have hot shards you can't split; over-shard
  and every query fans out to hundreds of tiny shards where p99 is the max over all of them.
- **Mapping changes require a reindex.** Changing a field's type is not an `ALTER`.
- **Update-heavy workloads are expensive** — every update is a tombstone plus a new document, which
  drives merge pressure.

**Who runs it at scale.** Elasticsearch, OpenSearch, Solr, Vespa, Lucene directly, Algolia, Typesense,
Meilisearch, Quickwit (Lucene-alike over object storage).

**Wrong answer to.** Being your system of record. The durability model, the lack of transactions, and
the reindex-for-schema-change property all assume the index is derived and rebuildable. If you cannot
rebuild it, you have a problem you haven't found yet.

---

### 2.4 Columnar

**Mechanism.** Store values column by column rather than row by row. Three things follow immediately:

- **Compression is dramatically better**, because adjacent values share a type and often a
  distribution — run-length encoding, dictionary encoding, delta and frame-of-reference encoding, bit
  packing. 5–20× on real data is ordinary.
- **Column pruning** — a query touching 4 of 150 columns reads roughly 4/150 of the bytes.
- **Vectorized execution** — operate on batches of column values in tight loops that the CPU can
  pipeline and SIMD, instead of interpreting one row at a time. Order-of-magnitude constant-factor
  win over row-at-a-time execution.

Indexing is usually **sparse** rather than exact: ClickHouse's `MergeTree` primary key is one index
entry per `index_granularity` rows (default 8192), so it locates a _block_, not a row. Parquet stores
per-row-group min/max statistics so a reader can skip row groups entirely (zone maps).

**Design intention.** Analytical queries touch few columns and many rows; row storage forces you to
read all columns of every row you scan. Columnar makes the bytes read proportional to the columns you
asked for.

**What problem it solves.** Aggregation and scanning over large volumes: `SELECT region, SUM(amount)
FROM trades WHERE dt > ... GROUP BY region` over a billion rows.

**Advantages.** Compression, scan throughput, aggregation speed, cheap storage per logical row.

**Disadvantages.**

- **Point reads are pathological** — reconstructing one row means touching every column's storage.
- **Single-row updates are worse.** Most columnar systems implement update as
  delete-marker-plus-insert, reconciled at merge (ClickHouse's `ReplacingMergeTree`, Delta's
  deletion vectors, Hudi's merge-on-read). A workload of frequent small updates fights the format.
- **No meaningful transactional isolation** in most of them; ClickHouse in particular has weak
  guarantees around deduplication and mutation visibility, by design.

**Who runs it at scale.** ClickHouse, DuckDB, Druid, Pinot, Redshift, Snowflake, BigQuery, Vertica,
and — as a _format_ rather than a system — Parquet and ORC, which is how columnar reaches the
lakehouse.

**Wrong answer to.** Anything on a transactional request path. A columnar store behind a user-facing
CRUD API is a category error, with the partial exception of Druid and Pinot, which are specifically
engineered for sub-second user-facing analytics through segment pre-aggregation and bitmap indexes.

---

### 2.5 Hash-partitioned key-value

**Mechanism.** `hash(partition_key)` selects a partition; the partition is replicated (typically 3
ways, across failure domains) and holds a local ordered structure — a B-tree or an LSM — so that a
sort key within the partition supports range scans. Routing is O(1) and involves no query planning at
all.

**Design intention.** Make latency independent of data size _by construction_, by removing from the
API any operation whose cost isn't bounded. DynamoDB refusing to let you query a non-key attribute
isn't a missing feature; it's the mechanism that lets it promise single-digit milliseconds at any
table size.

**What problem it solves.** Very high-volume, key-addressed access with a hard latency SLO and no
appetite for operations.

**Advantages.** Flat latency at any scale; near-zero operational burden in the managed versions;
horizontal scale by adding partitions transparently.

**Disadvantages.**

- **The key is the access path, and you usually can't change it.** In DynamoDB the table's key schema
  is fixed forever.
- **Hot partitions.** The flat-latency promise is conditional on the key distributing. A key like
  `TENANT#bigcustomer` concentrates on one partition and throttles at that partition's ceiling
  regardless of table-level capacity. The fix is key design — write sharding with a suffix — not
  capacity.
- **No joins, no aggregation, no ad-hoc predicates.** `Scan` exists and reads the entire table,
  billing you for everything read and filtering afterwards.
- **Hashing destroys locality.** A range query across keys is impossible; only a range on the _sort_
  key within one partition works.

**Who runs it at scale.** DynamoDB, Bigtable (though Bigtable is range-partitioned on a sorted row
key, which preserves range scans — a meaningful difference), Cosmos DB, Aerospike, Riak, and
Cassandra when used as a pure KV store.

**Wrong answer to.** A product whose access patterns aren't settled. You are choosing a system whose
primary key can never change, for data whose usage you can't yet predict.

---

### 2.6 In-memory structures

**Mechanism.** Data lives in RAM as native data structures — hash tables, skip lists (sorted sets),
radix trees, linked lists, HyperLogLog sketches, streams. Redis executes commands on a single thread
(with threaded network I/O added in 6.0 and further parallelism in later versions and in Valkey), so
individual commands are atomic without locks and multi-command atomicity comes from `MULTI`/`EXEC` or
Lua scripts. Persistence is optional and asynchronous: point-in-time **RDB** snapshots, an
append-only **AOF** log (fsync policy `everysec` by default), or both.

**Design intention.** Remove the disk from the read path entirely, and expose _data structures_ rather
than just a byte blob, so that operations like "increment this counter," "add to this sorted set and
return the rank," and "atomically pop from this list" are single round trips instead of
read-modify-write cycles.

**What problem it solves.** Sub-millisecond access, rate limiting, leaderboards, session state,
distributed locks, deduplication, and absorbing read load in front of a slower store.

**Advantages.** Latency an order of magnitude below any disk-backed store; rich atomic primitives;
extremely simple operationally at small scale.

**Disadvantages.**

- **RAM is the capacity limit,** and RAM is roughly an order of magnitude more expensive per byte than
  SSD.
- **Durability is best-effort by default.** With `appendfsync everysec` you can lose the last second;
  with async replication you can lose more on a failover. Redis Cluster explicitly does not guarantee
  strong consistency. Treating it as a system of record for anything that matters is a mistake people
  make because it _feels_ like a database.
- **Single-threaded command execution** means one expensive command (`KEYS *`, a large `SORT`, a big
  Lua script) blocks everything. This is the most common Redis incident.
- Licensing: Redis moved off BSD in 2024, prompting the **Valkey** fork under the Linux Foundation.
  For new work this is a real decision, not trivia — AWS ElastiCache and most cloud providers now
  offer Valkey.

**Who runs it at scale.** Redis, Valkey, Memcached (pure cache, multithreaded, slab allocator, no data
structures), Hazelcast, DragonflyDB, Aerospike (hybrid memory/SSD).

**Wrong answer to.** Any store of record. Also, as a "cache" in front of a database when the real
problem is a missing index — you've added a consistency boundary to avoid fixing a query.

---

### 2.7 Immutable objects plus a manifest (object storage and lakehouse table formats)

**Mechanism, layer 1 — object storage.** A flat key → blob namespace over an erasure-coded,
massively distributed fabric. There is no hierarchy (prefixes are a naming convention), no partial
update (a `PUT` replaces the whole object), and no cross-object transaction. S3 is designed for
eleven nines of durability and has offered strong read-after-write consistency since December 2020.
Latency is tens of milliseconds to first byte — three orders of magnitude worse than a cached B+ tree
read, and irrelevant, because that's not what it's for.

**Mechanism, layer 2 — table formats.** Object storage alone gives you "files in a bucket," which has
no schema, no atomicity, and requires an expensive `LIST` to know what exists. A **table format**
adds a metadata layer:

- **Apache Iceberg** — a metadata file points to a manifest list, which points to manifest files,
  which point to data files, each with column statistics. A commit atomically swaps the pointer to a
  new metadata file. That single atomic swap is what provides ACID, snapshot isolation, and time
  travel. Partitioning is _hidden_ (the engine derives partition values from a transform), which is
  why Iceberg supports partition evolution and Hive-style partitioning does not.
- **Delta Lake** — a `_delta_log` directory of ordered JSON commit files, periodically checkpointed to
  Parquet. Optimistic concurrency: readers read the log up to a version, writers append the next
  version and fail if someone got there first. Deletion vectors avoid rewriting whole files on delete.
- **Apache Hudi** — upsert-first. Copy-on-write tables rewrite files on update (read-optimized);
  merge-on-read tables append delta logs merged at read time (write-optimized). The
  copy-on-write/merge-on-read choice _is_ the read/write amplification tradeoff, made explicit.

**Design intention.** Decouple storage from compute so that (a) storage cost tracks bytes at object-
storage rates rather than at attached-disk rates, (b) many engines can read the same table, and (c)
compute scales to zero when nobody is querying.

**What problem it solves.** Unbounded historical volume at a cost per byte that no database matches,
with replayability — if a downstream system is wrong, you recompute it from the source of truth.

**Advantages.** Cheapest durable storage available; effectively unlimited; engine-agnostic; time
travel and schema evolution; compute and storage scale independently.

**Disadvantages.**

- **Latency is seconds to minutes, always.** There is no configuration that makes this a request-path
  store.
- **Small files destroy performance.** A streaming writer producing a file per minute per partition
  creates a metadata and `LIST` problem that dominates query time; compaction becomes a required,
  ongoing maintenance job.
- **Concurrent writers are optimistic**, so a high-contention write pattern produces commit conflicts
  and retries. These formats assume few writers and many readers.
- **The metadata layer is a real system** you now operate — manifest bloat, snapshot expiry, orphan
  file cleanup.

**Who runs it at scale.** S3/GCS/Azure Blob/MinIO as the substrate; Iceberg, Delta Lake, Hudi as the
format; Athena/Trino, Spark, Databricks, Snowflake, BigQuery, DuckDB, Flink as engines.

**Wrong answer to.** Anything a user is waiting on.

---

### 2.8 The specialized families

These don't fit the seven cleanly because they optimize for a query type rather than an access shape.

**Distributed SQL (NewSQL).** Range-partition the key space, run **Raft** per range for replication,
and coordinate cross-range transactions with 2PC over a global timestamp source. Spanner uses
**TrueTime** — GPS and atomic clocks giving a bounded uncertainty interval, so a transaction waits out
the uncertainty before committing and gets **external consistency** (linearizability across the whole
database). CockroachDB uses hybrid logical clocks instead, giving serializable isolation without the
hardware.

_Intention_: horizontal scale-out _and_ real transactions, which the previous generation forced you to
choose between. _Cost_: a cross-range transaction pays consensus latency plus 2PC, so a workload that
doesn't co-locate related rows is meaningfully slower than a single-node Postgres. _Products_: Spanner,
CockroachDB, TiDB, YugabyteDB, Aurora DSQL, Vitess (sharded MySQL, weaker guarantees).

**Time-series.** Exploits three properties of the workload: writes are append-only and roughly ordered
by time, queries are almost always time-bounded, and old data is deleted wholesale. Mechanisms:
delta-of-delta timestamp encoding plus XOR float compression (from Facebook's **Gorilla** paper) for
10× compression over general-purpose; time-partitioned chunks so retention is a partition drop rather
than a delete scan; and often a columnar layout per metric.

_Intention_: make the common case (recent data, one metric, a time range) cost almost nothing, and
make deletion free. _Products_: Prometheus (local TSDB, 2-hour blocks, pull model), VictoriaMetrics,
InfluxDB (v3 rebuilt on Parquet + DataFusion — check the version before making claims),
TimescaleDB (a Postgres extension: hypertables auto-partition into chunks, compressed chunks are
columnar), MongoDB time-series collections (bucketing implemented in the engine), Amazon Timestream.

**Graph.** The mechanism worth knowing is Neo4j's **index-free adjacency**: a node record contains a
direct pointer to its first relationship record, and relationship records form doubly-linked lists.
Traversing one hop is pointer-chasing at fixed cost, independent of total graph size. A relational
join over an edge table costs an index lookup per hop, and multi-hop queries multiply that.

_Intention_: make traversal depth the cost driver instead of dataset size. _Cost_: everything that
isn't a traversal — bulk scans, aggregations, ad-hoc filtering — is worse than in a relational store,
and horizontal partitioning of a graph is genuinely hard because edges cross partitions.
_Products_: Neo4j, Amazon Neptune, TigerGraph, JanusGraph, Memgraph; and `pgRouting`/recursive CTEs in
Postgres, which handle shallow traversals well enough that most "graph problems" don't need a graph
database.

**Vector / approximate nearest neighbour.** Fundamentally different from every other index here,
because it is **approximate by design**. You are not finding the answer; you are finding close-enough
answers fast, and recall is a tunable you trade against latency.

- **HNSW** (hierarchical navigable small world) — a multi-layer proximity graph; search descends from
  a sparse top layer to a dense bottom layer, greedily following the nearest neighbour. Logarithmic
  search, excellent recall/latency, but the whole graph wants to be in memory and builds are expensive.
- **IVF** (inverted file) — cluster vectors around centroids, probe the `nprobe` nearest clusters.
  Cheaper to build and lighter on memory, lower recall at equal latency. Often combined with product
  quantization (**IVF-PQ**) to compress vectors at further recall cost.

_Intention_: exact nearest-neighbour search in high dimensions is no better than a linear scan (the
curse of dimensionality), so the entire field accepts approximation. _Products_: pgvector (HNSW and
IVFFlat inside Postgres — usually the right first choice, because it avoids a second system),
OpenSearch k-NN, Pinecone, Weaviate, Qdrant, Milvus, Vespa, MongoDB Atlas Vector Search, FAISS
(a library, not a service).

**The log as a storage tier.** Kafka is usually discussed as a message broker, but its storage engine
is a design worth knowing: an append-only sequence of segment files per partition, reads served from
the OS page cache with zero-copy `sendfile`, retention by time or size, and — since KIP-405 — tiered
storage offloading old segments to object storage.

_Intention_: make the log the durable, replayable, ordered source of truth, and let every downstream
store be a materialized projection of it. _This is the mechanism behind every CDC architecture in this
document._ _Products_: Kafka, Redpanda (C++, thread-per-core, no ZooKeeper), Pulsar (separates serving
from storage via BookKeeper), Kinesis, AWS MSK.

---

## 3. The complete map

| Category              | Engine family                | Products                                                                | Primary role                                       |
| --------------------- | ---------------------------- | ----------------------------------------------------------------------- | -------------------------------------------------- |
| **Relational OLTP**   | B+ tree                      | PostgreSQL, MySQL/InnoDB, Aurora (PG/MySQL), Oracle, SQL Server, SQLite | System of record with cross-entity invariants      |
| **Distributed SQL**   | B+/LSM + Raft + 2PC          | Spanner, CockroachDB, TiDB, YugabyteDB, Aurora DSQL                     | System of record needing horizontal write scale    |
| **Document**          | B+ tree                      | MongoDB, Amazon DocumentDB, Couchbase, Firestore, RavenDB               | Variable-shape entities; materialized read models  |
| **Managed KV**        | Hash-partitioned             | DynamoDB, Cosmos DB, Bigtable, Aerospike                                | Key-addressed access at scale with a hard SLO      |
| **Wide-column**       | LSM                          | Cassandra, ScyllaDB, HBase, Bigtable                                    | Write-saturated, multi-region, tunable-consistency |
| **Search**            | Inverted index               | Elasticsearch, OpenSearch, Solr, Vespa, Algolia, Typesense              | Derived index for ad-hoc filtering and relevance   |
| **Cache / in-memory** | RAM structures               | Redis, Valkey, Memcached, Hazelcast, DragonflyDB                        | Latency floor; atomic primitives; load shedding    |
| **OLAP columnar**     | Columnar                     | ClickHouse, Druid, Pinot, Redshift, Snowflake, BigQuery, DuckDB         | Aggregation over large volumes                     |
| **Object storage**    | Immutable blob               | S3, GCS, Azure Blob, MinIO, Ceph                                        | Cheapest durable bytes; replay source              |
| **Lakehouse format**  | Manifest over columnar files | Iceberg, Delta Lake, Hudi                                               | Turning a bucket into a transactional table        |
| **Lakehouse engine**  | Columnar scan                | Athena/Trino, Spark, Databricks, Flink, DuckDB                          | Query the lake                                     |
| **Time-series**       | Specialized columnar/LSM     | Prometheus, VictoriaMetrics, InfluxDB, TimescaleDB, Timestream          | Metrics and telemetry with retention               |
| **Graph**             | Index-free adjacency         | Neo4j, Neptune, TigerGraph, JanusGraph                                  | Multi-hop traversal                                |
| **Vector**            | HNSW / IVF                   | pgvector, Pinecone, Weaviate, Qdrant, Milvus, OpenSearch k-NN           | Semantic retrieval                                 |
| **Log**               | Append-only segments         | Kafka, Redpanda, Pulsar, Kinesis                                        | Ordered replayable source; the CDC backbone        |
| **Blob + metadata**   | Object + DB pointer          | S3 + any DB holding the key                                             | Large binaries — never in the database             |

That last row is a rule, not a category: **large binaries go in object storage with the key in the
database.** A 5 MB PDF in a `jsonb` column or a MongoDB document inflates every read of that row
through the buffer cache, whether or not you projected the blob. This is the single most common
storage mistake in enterprise applications.

---

## 4. The selection framework

Five questions, in order. Each one collapses the space, so answer them in sequence rather than
comparing products.

### Q1 — Is this the system of record, or a derived view?

The single highest-leverage question, because it changes the requirements entirely.

|               | System of record                                                 | Derived view                                                |
| ------------- | ---------------------------------------------------------------- | ----------------------------------------------------------- |
| Consistency   | Must be strong enough to enforce your invariants                 | Eventual is fine                                            |
| Durability    | Loss is an incident                                              | Loss is a rebuild                                           |
| Transactions  | Often required                                                   | Almost never                                                |
| Schema change | Migration                                                        | Reindex                                                     |
| Candidates    | Postgres, MySQL, MongoDB, DynamoDB, Spanner, Iceberg/Delta on S3 | OpenSearch, Redis, ClickHouse, MongoDB-as-read-model, Druid |

Getting this wrong in the permissive direction — treating a derived store as authoritative — is how
you end up with two divergent copies and no reconciliation path. Enforce it structurally: exactly one
system owns each entity, everything else has a documented, tested rebuild procedure. The test is
simple and rarely run: **can you delete the derived store and rebuild it? How long does it take?** If
nobody knows, it's authoritative whether you intended it or not.

### Q2 — What shape is the dominant read?

This maps almost 1:1 to index structure, which is why it's the second question.

| Read shape                                | Structure that answers it | Default choice                                               |
| ----------------------------------------- | ------------------------- | ------------------------------------------------------------ |
| Point by primary key                      | Any                       | Cheapest that meets the SLO — often the cache tier           |
| Range by key prefix                       | B+ tree or sorted LSM     | Postgres, MongoDB, DynamoDB sort key, Bigtable               |
| Arbitrary predicate on 1–3 known fields   | B+ tree secondary index   | Postgres, MongoDB                                            |
| Arbitrary predicate on any of many fields | Inverted index            | OpenSearch                                                   |
| Full-text with relevance                  | Inverted index            | OpenSearch, Vespa, Algolia                                   |
| Aggregate over millions of rows           | Columnar                  | ClickHouse, Druid, Athena, Snowflake                         |
| Multi-hop traversal                       | Index-free adjacency      | Neo4j — but check whether a recursive CTE suffices           |
| Semantic similarity                       | HNSW / IVF                | pgvector first; a dedicated store only when it doesn't scale |
| Pre-joined view matching a UI screen      | Document store or cache   | §5                                                           |

### Q3 — What shape is the write?

| Write shape                  | Family                    | Why                                                  |
| ---------------------------- | ------------------------- | ---------------------------------------------------- |
| Point updates, moderate rate | B+ tree                   | Predictable reads matter more than write throughput  |
| Very high-rate appends       | LSM or log                | Sequential writes; compaction absorbs the reordering |
| Bulk load, then read-only    | Columnar                  | Large blocks compress and scan well                  |
| High-cardinality upsert      | LSM or Hudi merge-on-read | Both are designed for merge-on-read semantics        |
| Write once, read rarely      | Object storage            | Cheapest bytes                                       |

Cross-check Q2 against Q3. Conflicts are where architecture happens: "high-rate appends _and_ ad-hoc
filtering" means two systems and a CDC feed, not one system that does both badly.

### Q4 — What's the strongest consistency requirement, expressed as an invariant?

Not "we need consistency" — name the invariant and where it lives.

| Invariant                                                              | Minimum you need                                                                                                                                            |
| ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Spans multiple entities ("balance never negative across two accounts") | Multi-row ACID: Postgres, Spanner, CockroachDB. Note MongoDB gives **snapshot** isolation, which permits write skew — Postgres `SERIALIZABLE` does not      |
| Within one entity ("stock never negative for this SKU")                | Single-document/row atomic conditional update. Every store here does this. **This is most invariants**, and recognizing it saves you a transactional system |
| "Don't process this twice"                                             | An idempotency key with a unique constraint — cheaper than a transaction, in any store                                                                      |
| None; eventual is fine                                                 | Everything is a candidate                                                                                                                                   |

The reason to insist on naming the invariant: the majority of "we need ACID" requirements turn out to
be single-entity, which every store satisfies with a conditional update, and the rest turn out to be
satisfiable with an idempotency key. Genuine multi-entity invariants are rarer than people assume, and
identifying that is worth more than any product comparison.

### Q5 — Latency budget and duty cycle

| Budget    | Viable                                                             |
| --------- | ------------------------------------------------------------------ |
| < 1 ms    | In-memory only                                                     |
| 1–10 ms   | B+ tree with a resident working set; DynamoDB; hash-partitioned KV |
| 10–100 ms | Anything OLTP; search; a lightly-loaded columnar store             |
| Seconds   | Lakehouse engines, large aggregations                              |
| Minutes   | Batch                                                              |

**Duty cycle decides serverless vs provisioned, and it's the axis people skip.** Spiky and
unpredictable favours DynamoDB on-demand, Athena, Aurora Serverless. Steady high volume favours
provisioned capacity or a right-sized instance, usually by a large margin. "Serverless" describes a
billing model, not a cost advantage.

---

## 5. The pattern you're describing: a document store as the serving layer

The shape is: **object storage or a lake for raw and historical data → a relational database as the
curated system of record → MongoDB as a read layer in front of the presentation tier.**

### What it actually is

This is **CQRS with a materialized read model**, and the driver is almost always the same: the
presentation layer needs a _pre-joined, pre-shaped_ object that matches a screen, and producing that
from a normalized relational schema costs N joins on every request. So you compute the shape once at
write time and store it as a document, and the read becomes a single point lookup.

The tiers, honestly labelled:

| Tier                         | Real job                                                            | Why it can't be one of the others                         |
| ---------------------------- | ------------------------------------------------------------------- | --------------------------------------------------------- |
| Object storage / lakehouse   | Cheapest durable bytes; the replay source; analytics substrate      | Latency is seconds — never a request path                 |
| Relational (Postgres/Aurora) | Enforce cross-entity invariants; be the thing you reconcile against | Producing UI-shaped documents costs joins per request     |
| Document store (MongoDB)     | Serve a pre-computed shape in one read                              | It cannot enforce the invariants the relational tier does |
| Presentation                 | —                                                                   | —                                                         |

The property that makes this work: the serving tier is **derived and rebuildable**, so it doesn't need
transactions, doesn't need strong consistency, and its failure mode is "rebuild the projection" rather
than "lose data."

### Why it works, mechanically

Three separate wins, and they're worth separating because only some of them apply to any given system:

1. **Read amplification collapses.** A screen assembled from 6 relational tables costs 6 index
   descents plus 6 heap fetches, per request, forever. The same screen as one document is one B+ tree
   descent plus one fetch. At high read:write ratios this is the whole argument.
2. **The join is moved from read time to write time,** where it happens once per change instead of
   once per view. If a record is written once and read 10 000 times, you've moved the cost by four
   orders of magnitude.
3. **The tiers can be scaled and priced independently.** The serving tier scales with traffic; the
   relational tier scales with write volume; the lake scales with retention. Coupling them means
   sizing all three for the peak of the worst one.

### Where I'd push back

**MongoDB is often chosen for this role because the team knows MongoDB, not because the read model
needs a query engine.** That's worth saying out loud, because the honest comparison is:

| Serving store                                                      | When it's right                                                                                                                              | When it isn't                                                                                                                                   |
| ------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **Redis / Valkey**                                                 | The read model is pure key → blob, latency floor matters, and you can rebuild it from the source quickly                                     | Working set exceeds RAM economics; you need secondary queries on the projection; you need it to survive a total flush without a thundering herd |
| **DynamoDB**                                                       | Key-addressed, very high volume, flat latency SLO, zero ops appetite                                                                         | You need ad-hoc filters or sorts on the projection; the access pattern will change                                                              |
| **MongoDB**                                                        | The projection needs **secondary-index queries** — filter, sort, paginate on fields other than the key — and documents are large or variable | The projection is pure key lookup. Then you're paying for a query engine you don't use, plus an ops surface                                     |
| **OpenSearch**                                                     | The projection is queried by arbitrary attribute combinations or full text                                                                   | You need point-read latency; it's the wrong shape and you'll be disappointed                                                                    |
| **Postgres materialized view / a denormalized table with `jsonb`** | The volume is moderate                                                                                                                       | Read volume genuinely exceeds what the primary can serve — but check this, because the number is higher than people think                       |

**The deciding variable is whether the serving tier needs to be queried, or only fetched.** If your
read model is fetched by key, MongoDB is a heavier, more expensive Redis. If it's filtered and sorted
on secondary fields, MongoDB is exactly right and the others aren't. That single question should
decide it, and it usually isn't asked.

**And the tier I'd challenge hardest is the middle one.** Two genuinely different architectures get
described with the same diagram:

- **(a) Relational is the system of record, MongoDB is a projection of it.** Coherent. The relational
  tier enforces invariants, CDC feeds the projection, and the projection is rebuildable. Ship it.
- **(b) The lake is the source of truth, the relational tier is a curated intermediate, MongoDB is
  another copy.** Now you have three copies, three consistency boundaries, and — critically — the
  relational tier is doing nothing that the lake and the serving tier don't already do. This shape is
  usually organizational (a data team owns the lake, an application team owns the serving store, and
  the warehouse in the middle is where they meet) rather than technical.

Before building (b), the question I'd force: **what invariant does the relational tier enforce that
nothing else can?** If the answer is "none, it's where we do transformations," that's a compute
concern and belongs in the pipeline, not in a third durable copy that you now have to keep consistent
and pay for.

### The failure mode, and the guardrail

The projection becomes authoritative by accident. Someone needs a field the CDC feed doesn't carry,
or the replication lag is annoying during a demo, so they write to MongoDB directly. Now you have
divergence with no reconciliation path, and it will be discovered by a customer, months later,
through a number that doesn't match.

The guardrails that actually hold, in order of strength:

1. **The projection has no write credentials for the application.** Only the CDC consumer can write.
   Structural, not procedural — this is the one that survives new team members.
2. **A scheduled rebuild.** Rebuild the projection from scratch on a schedule (weekly is fine) into a
   new collection and swap an alias. This makes rebuildability a tested property rather than an
   assumption, and it silently repairs any drift that occurred.
3. **A reconciliation job** comparing counts and checksums between source and projection, alerting on
   divergence. Weaker than (1) and (2) because it detects rather than prevents, but it's the one that
   tells you the other two broke.

### The CDC feed must emit only committed writes

This is the correctness requirement that a diagram never shows. The projection must be fed by
something that only ever publishes committed data:

- **MongoDB change streams** — majority-committed by construction, so a rolled-back write can never
  appear downstream.
- **PostgreSQL logical decoding** (Debezium) — emits at commit, from the WAL.
- **DynamoDB Streams** — reflects committed items.

The alternative — the application writes to both stores — is a **dual write**, and it has no correct
implementation. The first write can succeed and the second fail; retries create duplicates; and there
is no ordering guarantee between two independent systems. Every "we'll just add a retry" version of
this is broken in a way that shows up as slow, quiet divergence. If you take one thing from this
section: **projections are fed from a log, not from application code.**

### The reference shape I'd actually draw

```
      writes (transactional)
            │
            ▼
   ┌──────────────────────┐
   │ Aurora PostgreSQL    │  system of record
   │ • cross-entity       │  • enforces the invariants
   │   invariants         │  • the thing you reconcile against
   │ • jsonb for the      │
   │   genuinely variable │
   └──────────┬───────────┘
              │ logical decoding (Debezium) → Kafka
              │   ordered, replayable, committed-only
    ┌─────────┼──────────────┬────────────────────┐
    ▼         ▼              ▼                    ▼
┌────────┐ ┌──────────┐ ┌──────────────┐ ┌─────────────────┐
│MongoDB │ │OpenSearch│ │ Redis/Valkey │ │ S3 + Iceberg    │
│UI-shaped│ │ad-hoc    │ │hot subset,   │ │ history,        │
│read     │ │filter +  │ │latency floor │ │ analytics,      │
│models   │ │full text │ │              │ │ Athena/Spark    │
└────────┘ └──────────┘ └──────────────┘ └─────────────────┘
   ALL REBUILDABLE FROM THE LOG — none of them is authoritative
```

Two properties make this correct rather than just fashionable:

- Everything below the log is derived, so its consistency model doesn't have to be strong, and its
  failure mode is a rebuild.
- The log is the ordering authority. Without it — with the application writing to each store — you
  have N dual-write problems and no way to reason about what's true.

**And you should not build all four branches on day one.** Start with the system of record and add a
projection when a _measured_ access pattern justifies it. Each branch is a consistency boundary, a
rebuild procedure, an on-call surface, and a bill. The architecture above is a destination, not a
starting point, and teams that start there spend their first year operating infrastructure instead of
shipping.

---

## 6. Interview questions

**Q:** How do you choose a database?

**Answer** — Not by comparing products. I'd answer five questions in order, because each one collapses
the space.

First, **is this the system of record or a derived view?** That changes every other requirement — a
derived view can be eventually consistent, non-transactional, and rebuildable, which puts search
engines, caches, and columnar stores on the table that otherwise wouldn't be.

Second, **what shape is the dominant read?** This maps almost directly to an index structure. Point
lookup by key, range on a key prefix, arbitrary predicate on a few known fields, arbitrary predicate
on any of many fields, aggregate over millions of rows, multi-hop traversal, nearest-neighbour — each
one has a data structure that answers it and several that can't.

Third, **what shape is the write?** Point updates favour a B+ tree; very high-rate appends favour an
LSM or a log; bulk-then-read favours columnar. Where Q2 and Q3 conflict — high ingest _and_ ad-hoc
filtering — that's where you get two systems and a CDC feed, and recognizing the conflict is the
design work.

Fourth, **what's the strongest invariant, named concretely?** Not "we need consistency." Most stated
ACID requirements turn out to be single-entity, which every store satisfies with a conditional update,
and most of the rest are satisfied by an idempotency key with a unique constraint. Genuine
multi-entity invariants are rarer than people assume, and if you have one, that's the requirement that
picks the store.

Fifth, **latency budget and duty cycle.** Duty cycle is the one people skip, and it's what decides
serverless versus provisioned — "serverless" is a billing model, not a cost advantage.

The framing I'd add: the default answer is PostgreSQL until something specific rules it out, because
one system with real transactions, a cost-based optimizer, and a `jsonb` column covers a surprising
fraction of the space, and every additional store is a consistency boundary you now own.

---

**Q:** Why is MongoDB a reasonable serving layer in front of a relational system of record, and when
is it the wrong choice?

**Answer** — The pattern is CQRS with a materialized read model. The driver is read amplification: a
screen assembled from six normalized tables costs six index descents plus six heap fetches per
request, forever. Precompute the joined shape at write time and the read becomes one document fetch.
You've moved the join from read time to write time, which at high read-to-write ratios is a win of
several orders of magnitude.

MongoDB is right for that role when the projection needs to be **queried** — filtered, sorted, and
paginated on fields other than the key. Secondary indexes on a materialized view are exactly what it
provides and what a cache doesn't.

It's the wrong choice when the projection is **fetched by key and nothing else**. Then it's a heavier,
more expensive Redis with an ops surface you don't need, and DynamoDB would give you flatter latency
at lower cost with zero operations. The deciding question — "is this projection queried, or only
fetched?" — should decide the choice, and in my experience it usually isn't asked; the store gets
picked because the team already runs it.

The thing I'd flag regardless of the choice: the projection must be fed by a log, not by application
code. Change streams, logical decoding via Debezium, DynamoDB Streams — something that emits only
committed writes in order. An application writing to both stores is a dual write, and there is no
correct implementation of a dual write: the second write can fail, retries duplicate, and there's no
ordering guarantee across two systems. It fails as slow, quiet divergence that a customer eventually
finds.

---

**Q:** Compare B+ tree and LSM tree storage engines.

**Answer** — They sit on opposite sides of the read/write amplification tradeoff.

A **B+ tree** keeps a balanced tree of pages with fanout in the hundreds, so a lookup over a billion
keys is three or four page accesses and the upper levels are cached. Reads are cheap and, more
importantly, _predictable_. The cost is on writes: changing one field rewrites a whole page, and
random inserts cause page splits, so write amplification is roughly page size over change size.

An **LSM tree** buffers writes in an in-memory sorted structure plus a WAL and flushes them
sequentially to immutable sorted files, with background compaction merging them. Writes are sequential
and fast. The cost is read amplification — a lookup may check the memtable plus several levels, and
bloom filters make the common case one file but leave the tail worse and more variable. Plus space
amplification during compaction, and compaction itself is a background job competing with foreground
traffic.

The failure shape that distinguishes them in production: an LSM under sustained overload falls into
**congestive collapse** — write rate rises, compaction falls behind, file count grows, reads slow,
everything slows, compaction falls further behind. A B+ tree under overload degrades more gracefully
because there's no background process to fall behind.

So: B+ tree when read predictability matters and the write rate fits one node — which is most OLTP.
LSM when ingest is the binding constraint — time series, event streams, high-cardinality upserts. And
LSM compaction strategy is a real tuning surface, not a detail: leveled compaction minimizes space at
high write amplification, size-tiered does the reverse, and time-window compaction for time-series
data drops whole files instead of merging them, which makes retention free.

---

**Q:** You have raw data in S3, a curated Postgres database, and MongoDB serving the API. Is that too
many systems?

**Answer** — Possibly, and the way to tell is to ask what each tier does that no other tier can.

S3 earns its place on cost per byte and replayability — it's the thing you recompute everything else
from, and no database matches its storage price. MongoDB earns its place if the API serves pre-joined,
UI-shaped documents that would otherwise cost joins per request, and especially if those documents
need secondary-index queries.

Postgres in the middle is the one to interrogate. If it's enforcing cross-entity invariants — the
thing that makes a write valid or invalid, the thing you reconcile against during an incident — it's
load-bearing and it stays. If it's "where we do transformations," that's a compute concern, and it
belongs in the pipeline rather than in a third durable copy with its own consistency boundary, its own
backup story, and its own bill.

That distinction matters because the two architectures look identical on a diagram and behave
completely differently. In one, Postgres is the source of truth and MongoDB is a rebuildable
projection — coherent, and I'd ship it. In the other, the lake is the source of truth and Postgres is
a staging area that happens to be durable — in which case you have three copies of the same facts and
no clear owner, and the reconciliation question ("which one is right?") has no answer.

The organizational reality worth naming: this shape often exists because a data team owns the lake and
an application team owns the serving store, and the warehouse in the middle is where their
responsibilities meet. That's a real constraint and sometimes the right answer, but it should be
stated as an organizational decision rather than defended as a technical one.

---

**Q:** When would you _not_ use PostgreSQL?

**Answer** — I'd start from the position that Postgres is the default and something specific has to
rule it out, because one system with real transactions, a cost-based optimizer, `jsonb` for
semi-structured fields, and `pgvector` for embeddings covers a lot of ground, and every additional
store is a consistency boundary you own forever.

The things that genuinely rule it out:

- **Write volume exceeding a single primary**, with no natural way to partition by tenant. That's
  distributed SQL (Spanner, CockroachDB) or a partitioned NoSQL store — and I'd want the measurement,
  because the ceiling on a large modern instance is higher than most teams assume.
- **Arbitrary multi-attribute filtering across many fields**, which is combinatorial for a B-tree and
  native for an inverted index. OpenSearch as a derived index, not a replacement.
- **Aggregation over hundreds of millions of rows on a dashboard.** Row storage reads every column of
  every row it scans; columnar reads only what you project. ClickHouse or a lakehouse.
- **A hard sub-millisecond SLO**, which means the read path can't touch disk. Redis or Valkey.
- **Unbounded historical volume** where you're paying database storage rates for data queried monthly.
  S3 plus a table format.
- **Very high-rate append-only ingestion**, where the B+ tree write amplification is the constraint.
  LSM or a log.

What I'd resist is the reverse framing — choosing something else first and then discovering you need
transactions, joins, or an index you didn't plan for. Those are much harder to add later than
throughput is.

---

## 7. Quick reference

| If the dominant requirement is…                                          | Start here                                                      |
| ------------------------------------------------------------------------ | --------------------------------------------------------------- |
| Cross-entity invariants, joins, unknown future queries                   | **PostgreSQL / Aurora**                                         |
| The above but beyond one primary's write capacity                        | CockroachDB, Spanner, TiDB                                      |
| Variable-shape entities; UI-shaped read models needing secondary queries | **MongoDB**                                                     |
| Key-addressed, flat latency at scale, known access patterns, no ops      | **DynamoDB**                                                    |
| Write-saturated, multi-region, tunable consistency                       | Cassandra / ScyllaDB                                            |
| Ad-hoc filtering across many fields; full text; relevance                | **OpenSearch** _(derived)_                                      |
| Sub-millisecond; counters, locks, rate limits, sessions                  | **Redis / Valkey** _(derived)_                                  |
| Aggregation over very large row counts                                   | ClickHouse, Druid, Snowflake                                    |
| Cheap unbounded history; replay source; infrequent analytics             | **S3 + Iceberg/Delta + Athena**                                 |
| Metrics and telemetry with retention                                     | Prometheus, VictoriaMetrics, TimescaleDB                        |
| Multi-hop traversal                                                      | Neo4j — after checking a recursive CTE                          |
| Semantic similarity                                                      | **pgvector** first; dedicated stores only when it doesn't scale |
| Ordered, replayable feed between all of the above                        | **Kafka**                                                       |
| Large binaries                                                           | **Object storage, key in the database.** Never in the row       |

Two rules that override the table:

1. **Fewer systems beats better-fit systems, until measurement says otherwise.** Each store is a
   consistency boundary, a backup story, an on-call rotation, and a bill. Two well-understood systems
   usually beat five optimal ones.
2. **Exactly one system owns each entity.** Everything else is a projection fed from a log, with a
   tested rebuild path. The test is: delete it and rebuild it. If nobody has ever done that, it is
   authoritative whether you intended it or not.

---

## References

1. **"Amazon DynamoDB: A Scalable, Predictably Performant, and Fully Managed NoSQL Database Service"**
   — USENIX ATC 2022. https://www.usenix.org/conference/atc22/presentation/elhemali — the
   authoritative account of hash partitioning, adaptive capacity, and why the API refuses non-key
   access.
2. **`facebook/rocksdb`** — https://github.com/facebook/rocksdb — the wiki on compaction styles and
   the tuning guide is the best available explanation of LSM read/write/space amplification, and it's
   the engine under a large fraction of the systems in §3.
3. **`apache/iceberg`** — https://github.com/apache/iceberg — read the spec
   (`format/spec.md`) for how a metadata pointer swap produces ACID over object storage. This is the
   mechanism behind the entire lakehouse category.
4. **`apache/lucene`** — https://github.com/apache/lucene — `lucene/core/.../index/` for segments and
   merges, `.../codecs/` for postings, BKD trees, and `doc_values`. OpenSearch is a distribution layer
   over this.
5. **"Gorilla: A Fast, Scalable, In-Memory Time Series Database"** — VLDB 2015 — delta-of-delta and
   XOR compression, the basis of nearly every modern TSDB.
6. **"Designing Data-Intensive Applications"**, Kleppmann — ch. 3 for B-tree vs LSM, ch. 5–6 for
   replication and partitioning, ch. 7 for isolation levels. The framing this whole document assumes.
7. **"Efficient and robust approximate nearest neighbor search using HNSW graphs"** — Malkov & Yashunin,
   2016 — https://arxiv.org/abs/1603.09320 — the algorithm behind pgvector, Qdrant, Weaviate, and
   most of the vector category.
8. **Martin Fowler on CQRS** — https://martinfowler.com/bliki/CQRS.html — short, and specifically
   includes the caution that CQRS is a targeted pattern with real costs, not a default architecture.
   Worth reading before building §5.
