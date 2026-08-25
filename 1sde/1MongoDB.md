# MongoDB

> Version anchor: MongoDB **8.0** server docs unless stated otherwise. Behaviour marked with a
> version tag (`since 6.0`, `removed in 4.2`) changed across releases — verify against the release
> you actually run before quoting it in an interview.

---

## 1. Document & Storage Model

### 1.1 BSON and the Document Model

#### Concept

- **What it is** — BSON is a length-prefixed, typed binary serialization format; a MongoDB
  document is exactly one BSON object, hard-capped at **16 MB** (`BSON document size limit`,
  MongoDB Limits & Thresholds docs, 8.0).

  Expansion: every value carries a 1-byte type code; every field name is stored as a
  null-terminated string **in every document** (no shared schema dictionary); every embedded
  document and array is length-prefixed so a reader can skip an entire subtree without parsing it.
  Arrays are encoded as documents with stringified integer keys (`"0"`, `"1"`, `"2"`) — which is
  why array element storage is not free and why positional operators (`$`, `$[]`, `$[<id>]`) exist
  at all.

- **What problem it solves** — JSON has no type system (no int64, no binary, no date, no
  fixed-point decimal), no length prefixes (a parser must scan linearly to find field _n_), and
  lossy number semantics (everything is an IEEE-754 double). BSON adds types and skip-ahead
  traversal so the server can extract one field from a 200 KB document without deserializing the
  whole thing.

- **What it replaced** — (a) fixed-schema relational rows requiring a DDL migration per shape
  change, and (b) application-side ORM mapping between object graphs and normalized tables. The
  prior art was insufficient specifically for _variable-shape_ data — per-tenant custom fields,
  product catalogs with type-dependent attributes, third-party payloads. The relational escape
  hatches were EAV tables (unindexable, join-explosive), sparse wide tables (hundreds of NULL
  columns), or a `TEXT` blob (opaque to the query engine).

  Defeater: this advantage collapses when the shape is actually stable. If your documents all have
  the same 40 fields, you have paid the field-name-repetition tax and the no-foreign-keys tax for
  nothing.

- **What it works with / ecosystem** — sits directly above WiredTiger (§1.2), below the query and
  aggregation layer. Beside it: PostgreSQL `jsonb` (also binary, also typed, but a _column_ inside
  an MVCC row), Elasticsearch `_source` (raw JSON blob retained alongside an inverted index),
  DynamoDB's item attribute-value map (typed, but 400 KB and no nested indexing). Drivers do
  BSON↔language-type mapping. Conflicts with anything that needs the storage engine to enforce
  cross-document invariants — MongoDB has no foreign keys and no cascading deletes at any version.

- **Place in the world** — catalogs, CMS, per-tenant configuration, event/audit stores, IoT and
  telemetry payloads, "the shape of this object is dictated by an upstream vendor." Run at scale
  by anyone with heterogeneous entity types. **Wrong answer to**: workloads whose dominant access
  pattern is multi-entity JOIN + aggregation across the whole corpus (that is a warehouse or
  lakehouse — see the comparison doc, Athena/Redshift), and any domain where a broken referential
  invariant is a correctness incident rather than a UI bug.

#### Architecture & Core Components

```
BSON document on the wire / on disk
┌──────────┬───────────────────────────────────────────────┬──────┐
│ int32    │ element*                                       │ 0x00 │
│ totalLen │                                                │ EOO  │
└──────────┴───────────────────────────────────────────────┴──────┘
                     │
                     ▼  one element
        ┌────────┬──────────────────┬──────────────────────┐
        │ 1 byte │ cstring          │ value                │
        │ type   │ field name       │ (type-dependent,     │
        │ code   │ (repeated in     │  itself length-      │
        │        │  every document) │  prefixed if nested) │
        └────────┴──────────────────┴──────────────────────┘

Control flow: driver ──serialize──▶ wire protocol (OP_MSG)
                                        │
                                        ▼
                            mongod command layer
                                        │
                     ┌──────────────────┴──────────────────┐
                     ▼                                     ▼
             query/agg execution                  WiredTiger row-store
             (reads BSON via                      (stores BSON bytes
              skip-ahead traversal)                verbatim as the value)
```

| Component                 | Single responsibility                                              |
| ------------------------- | ------------------------------------------------------------------ |
| Length prefix (int32)     | Lets a reader skip a document/subtree without parsing it           |
| Type byte                 | Disambiguates value encoding and fixes cross-type sort order       |
| Field-name cstring        | Self-describing key; the reason documents are storage-heavy        |
| `ObjectId`                | Default `_id`; roughly-monotonic 12-byte unique identifier         |
| BSON canonical type order | Total order over heterogeneous values, used by indexes and `$sort` |

#### How Each Component Works

**Length prefix**

- Data structure: leading little-endian `int32` = total byte length including itself and the
  trailing `0x00`.
- Input: byte offset. Output: offset of the next sibling element. State owned: none.
- Lifecycle: computed at serialization, validated at parse. A corrupt prefix is detected as
  `InvalidBSON` at parse time, not silently tolerated.
- Interaction: WiredTiger stores the BSON value opaquely; only the query layer interprets it.

**Type byte and canonical type order**

- Order (low→high): `MinKey < Null < Numbers (int32/int64/double/decimal128, compared by value)
< String < Object < Array < BinData < ObjectId < Boolean < Date < Timestamp < Regex < MaxKey`
  (MongoDB "Comparison/Sort Order" docs, 8.0).
- The four numeric types collapse into **one** sort class and compare by numeric value, so `1`
  (int32) and `1.0` (double) are equal for query and index purposes.
  Defeater: they are **not** equal for `$type` filtering, and `Decimal128 → double` conversion in
  a `$group`/`$sum` can silently lose precision. Money in `double` is a defect, not a style
  preference.

**Field-name cstring**

- There is no per-collection schema dictionary. A collection of 100 M documents with a field named
  `transactionSettlementDate` stores that 24-byte string 100 M times ≈ 2.4 GB **before**
  compression. WiredTiger's block compression (snappy by default) recovers most of it on disk;
  it does **not** recover it in the WiredTiger cache page images or in network payloads.
- This is the entire argument for short field names — and the argument against is readability plus
  the fact that compression already handles the disk side. See tradeoff table.

**`ObjectId` (12 bytes, since MongoDB 3.4)**

- Layout: 4-byte big-endian Unix timestamp (seconds) ‖ 5-byte per-process random value ‖ 3-byte
  big-endian counter initialized randomly.
- Property: **roughly** monotonic — increasing across seconds, arbitrary within a second and
  across processes.
  Defeater: this is _not_ a clock and _not_ a total order. Two `ObjectId`s generated in the same
  second on different app servers have no defined relative order, and clock skew can invert them
  across seconds. Never use `ObjectId` ordering as an event ordering guarantee.
- Consequence of monotonicity: `_id` index inserts land at the right-hand edge of the B+ tree —
  excellent cache locality and near-zero page splits elsewhere, but a single hot leaf page.
  On a **sharded** cluster with a range-based `_id` shard key this becomes a single hot shard
  absorbing 100% of inserts (§4.1).

#### Design Decisions, Tradeoffs & Best Practices

**Decisions the designers made**

| Decision                                       | Alternative rejected                          | Why                                                                                                                                                         |
| ---------------------------------------------- | --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Self-describing documents (field names inline) | Per-collection schema dictionary / Avro-style | Schema-on-read flexibility; no coordination on shape change. Cost: storage + no compile-time contract                                                       |
| 16 MB hard document cap                        | Unbounded documents                           | Bounds server memory per operation, wire payload, and replication oplog entry size. Cost: forces the "unbounded array" problem into the schema design phase |
| Binary format with length prefixes             | Text JSON on disk                             | Skip-ahead field access, real types. Cost: not human-readable, needs a driver                                                                               |
| Arrays as integer-keyed documents              | Native array encoding                         | Uniform element encoding, positional addressing. Cost: array elements carry key overhead                                                                    |

**Decisions you have to make**

| Decision                                         | Deciding variable                                                                                                                               |
| ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Custom `_id` vs default `ObjectId`               | Do you have a natural, immutable, unique business key that you also query by? If yes, use it and save an index. If it is not immutable, do not. |
| Short vs descriptive field names                 | Documents-per-collection × field-name bytes vs. WiredTiger cache size. Below ~10⁸ documents this is almost always premature.                    |
| Embed vs reference                               | §6.1 — driven by cardinality and update locality                                                                                                |
| Store money as `Decimal128` vs int64 minor units | Cross-currency arithmetic and rounding rules. Default: int64 minor units + explicit currency code, because it is unambiguous in every driver.   |

| Option                                       | Buys you                                                     | Costs you                                                                    | Choose when                                     |
| -------------------------------------------- | ------------------------------------------------------------ | ---------------------------------------------------------------------------- | ----------------------------------------------- |
| `ObjectId` `_id`                             | Free unique ID, insert locality, embedded creation timestamp | Meaningless to the business; 12 bytes                                        | Default. Almost always.                         |
| Natural-key `_id` (e.g. ISIN, tenantId+date) | One fewer unique index; idempotent upserts for free          | Immutable forever — a business rule change becomes a full collection rewrite | Key is genuinely immutable and you upsert by it |
| Hashed `_id`                                 | Uniform shard distribution                                   | Destroys range queries on `_id`; loses insert locality                       | Sharded, insert-heavy, no `_id` range scans     |

**Best practices** (rule → failure it prevents)

- **Never let an array grow without a modeled bound.** Prevents hitting the 16 MB cap in
  production with `BSONObjectTooLarge`, which is unrecoverable without a schema migration and
  fails _writes_, not reads.
- **Do not store two numeric types in the same field across documents.** Prevents `$sort` and
  range-index results that are correct-but-astonishing, and prevents `$type` filters silently
  missing rows.
- **Set an explicit `$jsonSchema` validator on collections with a stable shape.** Prevents the
  slow drift where one producer starts writing `status: "ACTIVE"` and another writes
  `status: {code: 1}`, which surfaces months later as an index that no longer covers.
- **Never encode business meaning into `ObjectId` timestamps.** Prevents ordering bugs from clock
  skew and from same-second generation on multiple app hosts.

#### Failure Modes, Exception Handling & Production Issues

| Failure                                   | Trigger                                                                                      | Blast radius                                                              | Detection signal                                                           | Mitigation                                                                             |
| ----------------------------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `BSONObjectTooLarge`                      | Unbounded array / embedded growth crosses 16 MB                                              | All writes to that one document fail; document becomes read-only-ish      | Write error code 10334; document size percentiles trending up              | Bucket pattern (cap N elements per bucket doc); or reference-out to a child collection |
| Working-set blowup from field names       | Very wide documents × very high doc count                                                    | Cache eviction storm → every read becomes disk I/O; cluster-wide latency  | `wiredTiger.cache` bytes-read-into-cache rising; `cache.eviction` counters | Shorten hot field names; project fewer fields; scale cache                             |
| Silent numeric precision loss             | `Decimal128` values aggregated through `$sum` after a `$toDouble`, or money stored as double | Wrong money. Not detected by any system signal                            | Reconciliation break against source of truth                               | int64 minor units; `Decimal128` end-to-end with no double coercion                     |
| Mixed-type field breaks index selectivity | Two producers write different types to the same field                                        | Query planner picks a plan with poor `nReturned/totalKeysExamined`        | `explain` showing keysExamined ≫ nReturned                                 | Schema validator; backfill migration                                                   |
| `$` / `.` in field names                  | Storing raw third-party JSON keys                                                            | Query and update paths for that field become unaddressable by dotted path | Fields readable but not queryable                                          | Since 5.0 the server accepts them; sanitize/escape at ingest anyway                    |

**Exception handling.** Write failures on document size and validation are **terminal** — retrying
sends the same bytes. `WriteConflict` (WiredTiger MVCC) is **retryable** and is retried internally
by the server for non-transactional single-document writes; inside a transaction it surfaces as
`TransientTransactionError` and the _whole transaction_ must be retried (§5.1). The poison-pill
risk lives in any consumer that reads a document, mutates, and writes back: a document that has
grown past 16 MB will fail that write forever, and a naive retry loop will spin on it.

**Real production issues**

- `Canonical failure pattern (not a specific incident)` — **The unbounded comment array.** Symptom:
  writes to a small subset of documents start failing at ~99.9th percentile document size; app
  error rate is low but concentrated on the most valuable entities (the popular ones). Root cause:
  `comments: []` embedded in the parent, no cap. Fix: bucket pattern — `{parentId, seq, comments:
[...≤500]}` with a compound index on `{parentId: 1, seq: -1}`. Guardrail: a document-size
  histogram alert (`$bsonSize` in a scheduled `$group`) firing at 4 MB, not at 16 MB.
- Public reference for the size limit and its rationale: MongoDB Limits & Thresholds docs; MongoDB
  design-pattern series on the Bucket and Outlier patterns (official MongoDB blog, "Building with
  Patterns").

#### Interview Questions

**Q:** Why is there a 16 MB document limit, and what do you do when you hit it?

**L4 answer** — It bounds per-operation memory on the server, the wire payload, and the size of a
single oplog entry. When you hit it, the document model is wrong: split the growing array into a
child collection, or use the bucket pattern to cap array length per document and add a sequence
field. `$bsonSize` in an aggregation tells you current sizes.

**L5 answer** — Plus: the limit is what lets the server treat a document as an atomic unit — every
single-document update is atomic without a transaction precisely because the server can materialize
the whole document. Removing the limit would push you into intra-document concurrency control.
Practically I'd never design to 16 MB; I'd set an internal budget an order of magnitude lower (~1 MB)
because the real constraint is the WiredTiger cache: a 5 MB document means every read of any field
in it pulls 5 MB of page images through cache, so the working set is defined by document size, not
by field access. In a bucket-pattern migration the thing that breaks is the read path — clients that
did `findOne({_id})` now need an aggregation with `$unwind`/`$slice`, so I'd ship the write-side
bucketing behind a dual-read first, then cut over.

---

**Q:** You have a field storing a monetary amount. What type?

**L4 answer** — Not `double` — IEEE-754 cannot represent 0.1 exactly and errors accumulate across
aggregation. Use `Decimal128` (IEEE-754-2008 decimal, 34 significant digits) or store integer minor
units in an `int64` with an explicit currency code.

**L5 answer** — Plus: `Decimal128` is correct but has sharp edges. Drivers map it to language types
inconsistently (Java `BigDecimal` yes; JS has no native decimal, so the Node driver hands you a
`Decimal128` wrapper that is easy to `Number()` away). Aggregation operators will happily widen a
`Decimal128` to `double` if any operand in the expression is a double, and there's no error — so a
single legacy document with a double amount silently poisons a `$sum`. My default is int64 minor
units because the failure mode of a wrong integer is loud and the failure mode of a lossy decimal is
a reconciliation break three months later. I'd only choose `Decimal128` where the domain genuinely
needs sub-minor-unit precision, e.g. FX rates or unit prices on bond quantities.

---

**Q:** What is an `ObjectId` made of and what can you infer from it?

**L4 answer** — 12 bytes: 4-byte Unix timestamp in seconds, 5-byte per-process random value, 3-byte
counter (since 3.4). You can infer creation time to one-second resolution. It's unique and roughly
monotonic, so `_id` index inserts are right-hand-edge appends.

**L5 answer** — Plus: "roughly monotonic" is the whole story. Within a second there is no order;
across processes there is no order; with clock skew the order can invert. So `sort({_id: 1})` is a
_stable pagination_ key, not an _event ordering_ key — I've seen teams conflate those and produce
out-of-order event streams. The monotonicity also has a cost: on a sharded cluster with a
range-based `_id` shard key, 100% of inserts land on the shard owning `MaxKey`, and adding shards
doesn't help because the balancer only moves cold data. That is exactly the case for a hashed shard
key or a compound key with a high-cardinality prefix. The upside of monotonicity — one hot leaf page
instead of random page splits across the whole tree — is real on a single replica set, so the right
answer is genuinely different sharded vs. unsharded.

---

**Q:** Field names are stored in every document. Should you shorten them?

**L4 answer** — Usually no. WiredTiger applies snappy block compression to collection data by
default, which compresses repeated field names well. Shortening trades readability for a saving
that compression mostly already made.

**L5 answer** — Plus: the argument for shortening isn't about disk, it's about the WiredTiger cache
and the wire. Cache holds decompressed page images, so field-name bytes occupy cache 1:1, and cache
is the scarce resource that determines whether your working set is memory-resident. Order of
magnitude: at 10⁸ documents with 30 fields averaging 15-byte names, that's ~45 GB of name bytes
resident if the whole collection is hot. So the deciding variable is `document_count ×
name_bytes` relative to cache size, and the answer flips somewhere around 10⁸ documents. Below
that I'd never do it, because the operational cost of a schema where nobody can read a query is
paid every day and the storage saving is paid once. If I did need it, I'd do it at the driver/codec
layer (`@BsonProperty` in the Java driver) so application code keeps readable names.

#### L5-Only Questions

**Q:** Your team wants to store raw vendor JSON payloads verbatim alongside a normalized projection
in the same document. Argue for and against, then decide.

**L5 answer** — For: audit and replay. You can reprocess without re-fetching from the vendor, and
you can prove what you received when a reconciliation breaks — which in a financial-data context is
the thing that actually gets asked. Against: it typically doubles or triples document size, and
because the raw blob is in the same document, every read of the _normalized_ fields pulls the raw
bytes through the WiredTiger cache. That inflates the working set by the size of data nobody
queries. It also puts unsanitized vendor field names (`$`, `.`, unpredictable casing) into your
document.

Decision: split. Normalized document in the hot collection; raw payload in a separate collection
keyed by the same `_id`, or in S3 with the object key stored in the hot document. S3 is my default
because the raw payload is write-once/read-rarely, which is exactly the access pattern object
storage prices for, and it removes the blob from the cache entirely. The tradeoff I'm accepting is
that replay now requires a second system to be up — acceptable, because replay is not on the
request path. I'd only keep them co-located if the payload is small (order of a few KB) and the
audit read genuinely happens on the same request as the normalized read.

---

**Q:** Design a document-size guardrail that catches growth before it becomes an incident.

**L5 answer** — Three layers, because each catches a different class.

1. _Write-time_: a `$jsonSchema` validator with `maxItems` on any array that can grow. This is the
   only layer that fails fast at the producer. Its limit is that `$jsonSchema` can't express "total
   document bytes," so it catches array cardinality, not blob width.
2. _Continuous_: a scheduled aggregation
   `db.c.aggregate([{$project: {sz: {$bsonSize: "$$ROOT"}}}, {$bucket: ...}])` emitting a size
   histogram to Datadog, alerting at 4 MB p99 — a quarter of the limit, so you have time for a
   migration, not a hotfix. Run it on a secondary with `readPreference: secondary` and
   `allowDiskUse`, because it is a full collection scan.
3. _Structural_: cap the array in the data model itself via the bucket pattern, so the guardrail is
   the schema rather than a monitor. This is the one that actually holds, because monitors get
   muted.

The thing I'd push back on is a per-write `$bsonSize` check in application code: it costs on every
write, it's easy to bypass from a second service, and it duplicates what the validator does
authoritatively at the server.

---

### 1.2 WiredTiger Storage Engine

#### Concept

- **What it is** — WiredTiger is MongoDB's default storage engine (since **3.2**; the only option
  since **4.2** when MMAPv1 was removed): a B+ tree row-store with MVCC snapshot isolation,
  copy-on-write page reconciliation, block compression, and a write-ahead journal.

- **What problem it solves** — MMAPv1's collection-level (later database-level) locking serialized
  writes, and its in-place update model required per-document padding and forced expensive
  _document moves_ when a document grew past its padded slot — which also invalidated every index
  entry pointing at it. WiredTiger gives document-level concurrency via MVCC and removes document
  moves by decoupling the logical `RecordId` from the physical location.

- **What it replaced** — MMAPv1 (memory-mapped files, OS page cache, no compression, no MVCC).
  Specifically insufficient because: (a) lock granularity capped write throughput regardless of
  hardware, (b) no compression meant storage cost scaled with the field-name repetition problem
  from §1.1, and (c) the OS page cache gave the engine no control over eviction policy.

- **What it works with / ecosystem** — sits below the query layer, above the filesystem. Composes
  with the journal for durability and with the oplog for replication (the oplog is itself a
  WiredTiger collection). Beside it: InnoDB (also B+ tree MVCC, but clustered on the primary key),
  RocksDB/LSM (write-optimized, used by MongoRocks and by TiKV), Aurora's log-structured
  distributed storage (which is what Amazon DocumentDB uses instead — see the comparison doc).

  Conflicts with: assumptions that MongoDB uses the OS page cache. It doesn't, primarily —
  it manages its own cache, and _also_ benefits from the filesystem cache holding compressed
  blocks. Sizing a host as if there were one cache is a common mistake.

- **Place in the world** — every self-managed MongoDB and every Atlas cluster. **Wrong answer to**:
  write-saturated append-only workloads where an LSM tree's sequential-write advantage matters more
  than read amplification — though in practice you'd solve that by not putting that workload in
  MongoDB rather than by swapping engines.

#### Architecture & Core Components

```
                    ┌─────────────────────────────────────────┐
   write ─────────▶ │  In-memory B+ tree page                 │
                    │   leaf page image (clean, from disk)    │
                    │   + per-key UPDATE CHAIN (skiplist)     │◀── MVCC versions
                    │     [txnId=105]→[txnId=99]→[txnId=87]   │    tagged w/ txn id
                    └───────────────┬─────────────────────────┘
                                    │
        ┌───────────────────────────┼──────────────────────────┐
        ▼                           ▼                          ▼
  ┌───────────┐            ┌────────────────┐         ┌────────────────┐
  │  JOURNAL  │            │   EVICTION     │         │  CHECKPOINT    │
  │ (WAL)     │            │  reconcile     │         │  every 60 s    │
  │ fsync per │            │  page → new    │         │  writes a      │
  │ 100 ms or │            │  disk blocks   │         │  consistent    │
  │ on j:true │            │  (copy-on-     │         │  snapshot root │
  └─────┬─────┘            │   write)       │         └────────┬───────┘
        │                  └────────┬───────┘                  │
        └───────────────────────────┴──────────────────────────┘
                                    ▼
                       ┌────────────────────────────┐
                       │ data files (compressed     │
                       │ blocks; snappy default)    │
                       │ + OS filesystem cache      │
                       └────────────────────────────┘
```

| Component                       | Single responsibility                                            |
| ------------------------------- | ---------------------------------------------------------------- |
| WiredTiger cache                | Hold decompressed B+ tree page images and update chains          |
| Update chain (skiplist per key) | Hold uncommitted + recent committed versions for MVCC            |
| Eviction                        | Reclaim cache by reconciling dirty pages into new on-disk blocks |
| Checkpoint                      | Produce a crash-consistent on-disk snapshot root                 |
| Journal (WAL)                   | Make writes durable between checkpoints                          |
| Block compressor                | Trade CPU for disk bytes and filesystem-cache density            |
| Oplog (a WT collection)         | Ordered, idempotent record of writes for replication             |

#### How Each Component Works

**Cache**

- Default size: `max(50% of (RAM − 1 GB), 256 MB)` (`storage.wiredTiger.engineConfig.cacheSizeGB`,
  MongoDB 8.0 docs). The remaining RAM is deliberately left to the filesystem cache and to
  connection/aggregation memory.
- Holds _decompressed_ page images. Compression ratio therefore reduces disk and filesystem-cache
  footprint but **not** WiredTiger cache footprint.
  Defeater for "compression saves memory": it does not save WiredTiger cache; that is the most
  commonly wrong statement about MongoDB memory sizing.
- Eviction thresholds (defaults, WiredTiger config): eviction triggers around **80%** cache used,
  application threads are recruited to help evict around **95%**, and dirty-data thresholds sit
  around 5%/20%. Verify against your build via `db.serverStatus().wiredTiger.cache`.
  When application threads evict, latency for _all_ operations spikes — this is the classic
  "everything got slow at once" signature.

**Update chain / MVCC**

- Structure: per-key singly-linked chain of update structures, newest first, each tagged with a
  transaction id and (since 4.0) a commit timestamp.
- A reader takes a snapshot and walks the chain to the newest version visible to it. So read cost
  grows with the number of concurrent versions of a key.
- Small `$set` updates use WiredTiger's `WT_MODIFY` path, storing a delta rather than a full new
  document image, which bounds chain memory for hot-field updates.
  Defeater: this only applies below a size threshold and for updates the server can express as a
  delta; growing a document or touching an array typically writes a full new image.
- Conflict rule: two concurrent transactions writing the same key → the later one gets
  `WT_ROLLBACK`, surfaced as `WriteConflict`. Single-document writes retry internally; transactional
  writes surface `TransientTransactionError` to the client.

**Eviction and reconciliation**

- Copy-on-write: a dirty page is reconciled into **new** blocks; old blocks are freed after the
  next checkpoint. No in-place page overwrite, which is why crash recovery does not need
  page-tear protection (contrast: InnoDB's doublewrite buffer).
- Cost: write amplification. A one-field update on a document in a 32 KB leaf page rewrites the
  whole leaf.

**Checkpoint**

- Every **60 seconds** by default (or on `fsync`/shutdown), WiredTiger writes a consistent snapshot
  and updates the metadata root atomically.
- Recovery: on restart, open the last checkpoint, then replay the journal forward.
  Defeater for "checkpoints make you safe": without the journal you lose up to 60 s of writes.
  With `journal` disabled (not possible since 4.0 on replica sets) you lose to the last checkpoint.

**Journal (WAL)**

- Buffered, group-committed, and fsynced every **100 ms** by default
  (`storage.journal.commitIntervalMs`), or immediately when a write specifies `j: true`.
- So `{w: 1}` alone means: acknowledged from the primary's memory, possibly not yet on the
  primary's disk, definitely not on any secondary. That is a real data-loss window, not a
  theoretical one.

**Compression**

- Collections: **snappy** by default; `zstd` (since 4.2) and `zlib` available. Indexes: **prefix
  compression** by default (shared key prefixes stored once per page), not block compression.
- Order of magnitude: snappy typically 2–4× on document-shaped data, zstd meaningfully better at
  more CPU. Measure on your data — do not quote a ratio you didn't observe.

#### Design Decisions, Tradeoffs & Best Practices

**Decisions the designers made**

| Decision                     | Alternative rejected                                       | Why                                                                                                                                                                                 |
| ---------------------------- | ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| B+ tree row-store            | LSM tree (WiredTiger supports LSM, MongoDB doesn't use it) | Read latency predictability and range-scan efficiency; MongoDB's dominant workloads are read-heavy with secondary-index lookups. Cost: worse random-write amplification than an LSM |
| Engine-managed cache         | Rely on OS page cache (MMAPv1)                             | Control over eviction policy and dirty-page accounting; ability to hold decompressed images. Cost: you now have two caches to size                                                  |
| Copy-on-write reconciliation | In-place page update + doublewrite                         | No torn-page problem, cheap snapshots, enables `recoverToStableTimestamp` for rollback. Cost: write amplification and free-space fragmentation                                      |
| Compression on by default    | Off by default                                             | Storage cost dominates for document data. Cost: CPU on every page read/write                                                                                                        |

**Decisions you have to make**

| Decision                       | Deciding variable                                                                                                                                                                              |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Cache size                     | Working-set size, _not_ total data size. If `bytesReadIntoCache` is near zero at steady state, cache is adequate.                                                                              |
| snappy vs zstd                 | CPU headroom vs storage bill. Default snappy; move to zstd when you are storage-bound and CPU is below ~50%.                                                                                   |
| `j: true` per write vs default | Whether a 100 ms loss window on a primary crash is acceptable. With `w: "majority"` on a 3-node set you already survive a single-node crash, so per-write `j: true` is usually redundant cost. |
| Instance memory                | Cache ≈ 50% of RAM. If working set is 40 GB, you need ~96 GB RAM, not 64 GB.                                                                                                                   |

| Option         | Buys you         | Costs you                                         | Choose when                                               |
| -------------- | ---------------- | ------------------------------------------------- | --------------------------------------------------------- |
| snappy         | Cheap CPU, ~2–4× | Larger disk than zstd                             | Default                                                   |
| zstd           | Best ratio       | Noticeably more CPU on eviction and read          | Storage-bound, CPU headroom exists                        |
| No compression | Lowest CPU       | Full storage cost, worse filesystem-cache density | Almost never; only for already-compressed binary payloads |

**Best practices** (rule → failure it prevents)

- **Size RAM from the working set, then double it for cache-is-50%.** Prevents the cliff where the
  working set exceeds cache and every read becomes a disk read — a step function in latency, not a
  gradient.
- **Alert on `wiredTiger.cache.bytes read into cache` rate, not on cache utilization.** Prevents
  paging in an incident that already started; utilization sits at ~80% permanently by design and is
  therefore not a signal.
- **Alert on eviction by application threads
  (`cache.pages evicted by application threads`) being non-zero.** Prevents the case where user
  operations are stalling to do the engine's housekeeping and every p99 in the service degrades
  simultaneously.
- **Do not disable the journal.** Prevents losing everything since the last checkpoint (up to 60 s)
  on an unclean shutdown.
- **Keep documents small and updates narrow (`$set` on a field, not full-document replace).**
  Prevents update-chain memory growth and full-page reconciliation on every write.

#### Failure Modes, Exception Handling & Production Issues

| Failure                      | Trigger                                                       | Blast radius                                                | Detection signal                                                            | Mitigation                                                                                                 |
| ---------------------------- | ------------------------------------------------------------- | ----------------------------------------------------------- | --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Cache eviction storm         | Working set > cache; or a full-collection scan sweeping cache | Node-wide latency collapse; replication lag follows         | `pages evicted by application threads` > 0; `bytes read into cache` spiking | Add RAM; add an index so the scan stops; run analytics on a secondary/analytics node                       |
| Write conflict storm         | Many writers hot-spotting one document (a counter)            | Retry amplification; CPU burn; apparent throughput collapse | `WriteConflict` rate; `serverStatus().metrics.operation.writeConflicts`     | Shard the counter across N documents; or move counters out of MongoDB                                      |
| Checkpoint stall             | Huge dirty-cache accumulation, slow disk                      | Periodic ~60 s-cycle latency spikes                         | Sawtooth p99 with 60 s period; `cache.tracked dirty bytes`                  | Faster disk; smaller cache dirty thresholds; reduce write burstiness                                       |
| Journal fsync latency        | Slow/contended disk, EBS burst credits exhausted              | All `j:true` and majority writes stall                      | `wiredTiger.log` fsync duration; disk `await`                               | Provisioned IOPS; separate journal volume                                                                  |
| Disk fill from fragmentation | Copy-on-write + large deletes without reuse                   | Node down, hard                                             | Disk used ≫ `collStats.size`                                                | `compact` (blocking on that node — run rolling on secondaries); or initial-sync a fresh secondary and roll |

**Exception handling.** `WriteConflict` is retryable and mostly invisible outside transactions.
`ExceededMemoryLimit` on aggregation (100 MB per blocking stage without `allowDiskUse`) is
retryable only if you change the query. Disk-full is terminal and takes the node out of the replica
set; a majority-write cluster survives one such node and stalls if it loses a majority. Poison-pill
risk: a single query that scans a huge collection will evict the entire working set — one bad
report from a BI tool can degrade the OLTP path, which is the argument for a dedicated analytics
node with `readPreference: {tags: {nodeType: "analytics"}}`.

**Real production issues**

- **Public, cited:** MongoDB's own engineering write-ups on the WiredTiger `recoverToStableTimestamp`
  mechanism explain why replica-set rollback changed from replaying rollback files to a storage-level
  rewind in 4.0 — the older mechanism could exceed its 300 MB rollback limit and require a full
  resync, which on a large node is hours of unavailability for that member (MongoDB 4.0 release
  notes; MongoDB "Rollbacks During Replica Set Failover" docs).
- `Canonical failure pattern (not a specific incident)` — **The analytics query that took down
  OLTP.** Symptom: p99 on unrelated point reads jumps 50× for ~20 minutes, once a night. Root cause:
  a nightly BI extract issuing an unindexed `find()` on the primary; the collection scan pulled the
  entire collection through the WiredTiger cache and evicted the OLTP working set. Fix: route it to
  a tagged analytics secondary and add the covering index. Guardrail: `maxTimeMS` on every
  analytical client, plus an alert on `bytes read into cache` rate, plus revoking primary read
  access from BI credentials — the last one is the only one that survives a new team joining.

#### Interview Questions

**Q:** How much RAM does a MongoDB node need?

**L4 answer** — Enough that the working set (frequently-accessed documents _and_ their index pages)
fits in the WiredTiger cache, which defaults to `max(50% of (RAM − 1 GB), 256 MB)`. So working-set
size roughly doubled. Total data size is not the input — a 2 TB collection with a 20 GB hot subset
needs cache for 20 GB.

**L5 answer** — Plus: the number people get wrong is that compression does not reduce cache
footprint — the cache holds decompressed page images, so a 4× compression ratio buys you disk and
filesystem-cache density, not memory. The other half of RAM isn't waste: it holds compressed blocks
in the filesystem cache, which turns a cache miss from a disk read into a memcpy + decompress, so
the latency cliff is two-tiered rather than one. The diagnostic I actually use isn't a sizing
formula, it's `wiredTiger.cache["bytes read into cache"]` rate at steady state — if it's flat near
zero, you're sized correctly regardless of what the formula said; if it's climbing, you're
short, and if `pages evicted by application threads` is non-zero you're already in incident
territory. Index size is the part people forget: indexes live in the same cache and on a
write-heavy collection with 8 indexes they can dominate.

---

**Q:** Walk through what happens on `db.orders.updateOne({_id: x}, {$set: {status: "SHIPPED"}})`
with `{w: "majority", j: true}`.

**L4 answer** — Router/primary locates the document via the `_id` index (B+ tree descent → RecordId
→ row-store lookup). WiredTiger creates a new version on that key's update chain under a
transaction id. The op is written to the journal buffer, and because `j: true`, the client waits for
the journal fsync. The op is also appended to the oplog. Secondaries tail the oplog and apply it;
once a majority have acknowledged, the primary returns success to the client.

**L5 answer** — Plus the ordering and the failure points. The journal fsync and the oplog write are
part of the same WiredTiger transaction — the oplog is just another WiredTiger collection, which is
what makes "the write happened" and "the write is replicable" atomic. `j: true` on a
`w: "majority"` write is largely redundant: majority acknowledgment already implies the write
survives a single-node crash, so you're paying an fsync for a scenario (simultaneous majority
crash) where you have bigger problems. I'd drop `j: true` and keep `w: "majority"`.

What actually breaks: the `$set` uses WiredTiger's `WT_MODIFY` delta path since the change is small
and doesn't grow the document — good, because the alternative is a full document image on the
update chain. If instead this were `$push` onto an array, you'd get a full new image every time and
the update chain for a hot document becomes a memory problem. And `w: "majority"` has a subtle
availability property: on a 3-node set losing one secondary, majority is still 2, so you're fine; on
a **2-node** set (plus arbiter) losing the secondary means majority writes block indefinitely —
which is why arbiters are a trap that people deploy to "save money" and then discover during a
maintenance window.

---

**Q:** Your p99 read latency shows a sawtooth with a ~60 second period. Diagnose.

**L4 answer** — 60 seconds is the WiredTiger checkpoint interval. Dirty pages accumulate in cache
and are flushed at checkpoint; if the disk can't absorb the burst, operations stall behind it. Check
`wiredTiger.transaction` checkpoint duration and disk write latency/queue depth.

**L5 answer** — Plus: the fix depends on which side is saturated. If checkpoint _duration_ is
growing, the disk is the constraint — provisioned IOPS, or a separate volume for the journal so
journal fsyncs aren't queued behind checkpoint writes. If dirty bytes are hitting the eviction
trigger _before_ the checkpoint, the problem is write rate versus eviction throughput, and lowering
`eviction_dirty_target` makes eviction more continuous — you trade a smooth higher baseline for the
absence of the spike, which is almost always the right trade for a latency-SLO service. The thing
I'd check first though is whether the write burstiness is self-inflicted: a batch job doing a
million updates in a 5-second window produces exactly this shape, and throttling the job is cheaper
than re-architecting storage.

---

**Q:** Why did MongoDB replace MMAPv1?

**L4 answer** — MMAPv1 locked at collection level (database level before 3.0), so write concurrency
was capped independent of hardware. It updated documents in place with padding, so a document that
outgrew its slot had to be _moved_, which required rewriting every index entry pointing to it. It
had no compression and no MVCC. WiredTiger gives document-level concurrency, no document moves,
compression, and snapshot isolation.

**L5 answer** — Plus: the deeper reason is that MMAPv1 delegated caching to the OS, so MongoDB had
no way to reason about eviction, no way to hold decompressed images, and no way to implement
snapshots. Owning the cache is what made everything after it possible — MVCC, then commit
timestamps, then `recoverToStableTimestamp`, which is what lets replica-set rollback rewind storage
instead of replaying rollback files with a 300 MB ceiling. That chain is why the engine swap was
strategically necessary and not just a performance win. The cost MongoDB accepted: write
amplification from copy-on-write reconciliation, and a second cache to size. It's a good trade for
read-heavy document workloads and a bad one for write-saturated append streams — which is the
honest answer to "why not MongoDB for a firehose."

#### L5-Only Questions

**Q:** You're deciding between a larger instance and adding a read-replica for a read-heavy
MongoDB workload. Which, and what's the deciding variable?

**L5 answer** — The deciding variable is whether you are cache-bound or CPU/connection-bound, and
you can tell which from `bytes read into cache`. If reads are missing cache, adding a replica does
not help — the replica has the same working set and the same cache-to-data ratio, so you've bought
a second machine that also thrashes. Scale up. If reads are hitting cache and you're saturating CPU
or connections, scale out.

There's a second consideration that usually decides it: reading from secondaries changes your
consistency contract. `readPreference: secondaryPreferred` gives you reads that can lag the primary
by however far replication lag is, and lag is unbounded during a burst. For a workload where
"user updated their profile and immediately re-read it" is a supported flow, that's a correctness
regression disguised as a scaling win. You can recover it with causal-consistent sessions
(`afterClusterTime`), but that makes the secondary _wait_ for the write to arrive, which erodes the
latency benefit you scaled out for.

My default: scale up first, because it preserves the consistency model and MongoDB nodes go very
large. Scale out reads only for genuinely stale-tolerant traffic — analytics, search backfill,
export — and route it explicitly with node tags rather than a global read preference, so nobody
accidentally moves the OLTP path onto a lagging node.

---

**Q:** Explain how MongoDB gets crash-consistent recovery without a doublewrite buffer.

**L5 answer** — Because WiredTiger never overwrites a page in place. Reconciliation writes a dirty
page to _new_ blocks; the previous blocks stay valid until the next checkpoint frees them. A torn
write can therefore only corrupt blocks that no committed checkpoint root points at, so there is no
partial-page problem to defend against. InnoDB needs the doublewrite buffer precisely because it
does overwrite pages in place and a torn 16 KB page under a 4 KB sector device is unrecoverable.

The checkpoint root is written last and atomically, so recovery is: open the newest valid checkpoint,
then replay the journal from that checkpoint's LSN forward. Everything between the last checkpoint
and the crash comes from the journal, which is why disabling the journal costs you up to the full
checkpoint interval.

The cost of this design is space and fragmentation: freed blocks are reused from a free list, but a
workload with large deletes or heavily varying page sizes leaves holes, and disk usage can sit well
above `collStats.size` indefinitely. `compact` reclaims it but blocks that node, so the operational
answer is a rolling `compact` across secondaries, or — for large nodes — an initial sync of a fresh
member, which is slower but doesn't hold a lock. This is the tradeoff people don't anticipate:
copy-on-write buys you cheap snapshots and simple recovery, and bills you in space amplification.

---

## 2. Indexing & Query Planning

### 2.1 Index Structures and Index Types

#### Concept

- **What it is** — Every MongoDB index is a B+ tree mapping a serialized key (`KeyString`, an
  order-preserving byte encoding of the indexed BSON values) to a `RecordId` identifying the
  document in the collection's row-store.

- **What it solves** — Turns a `O(n)` collection scan into a `O(log n)` tree descent plus a bounded
  range walk, and — critically — makes `$sort` free when the index order already matches the
  requested order, avoiding an in-memory blocking sort with a 100 MB limit.

- **What it replaced** — Nothing exotic; this is the same B+ tree idea as every relational engine.
  What's specific to MongoDB is what it indexes: paths into a nested document, including _inside
  arrays_ (multikey), which relational engines historically could not do without normalizing the
  array into a child table.

- **What it works with / ecosystem** — sits between the query planner (§2.2) and WiredTiger. Every
  index is a separate WiredTiger table with its own pages competing for the same cache. Composes
  with the aggregation framework (`$match` at the front of a pipeline can use an index; after a
  `$group` it cannot). Conflicts with high write throughput: every index multiplies write cost.

  Beside it: DynamoDB GSIs (a physically separate replicated table, eventually consistent),
  Elasticsearch inverted indexes (term → posting list, a fundamentally different structure aimed at
  relevance), PostgreSQL GIN on `jsonb` (inverted, containment-oriented). See the comparison doc.

- **Place in the world** — the single highest-leverage thing you control in a MongoDB deployment.
  **Wrong answer to**: full-text relevance ranking (MongoDB's `text` index does term matching with a
  crude score; if relevance is the product, use OpenSearch/Atlas Search), and to
  arbitrary-dimension ad-hoc analytical filtering (you cannot index 40 fields' worth of
  combinations — that's a columnar store's job).

#### Architecture & Core Components

```
  find({status:"OPEN", ts:{$gt:T}}).sort({ts:1})
                 │
                 ▼
        ┌─────────────────┐
        │  Query Planner  │  (§2.2)
        └────────┬────────┘
                 │ chooses IXSCAN on {status:1, ts:1}
                 ▼
  ┌─────────────────────────────┐
  │ INDEX  (WiredTiger B+ tree) │
  │  key = KeyString(status,ts) │
  │  val = RecordId             │
  │  leaf pages prefix-compressed│
  └──────────────┬──────────────┘
                 │ RecordId    ◀── this hop is the "FETCH"
                 ▼
  ┌─────────────────────────────┐
  │ COLLECTION (WT row-store)   │
  │  key = RecordId (int64)     │
  │  val = BSON bytes           │
  └─────────────────────────────┘

  Covered query = planner proves all needed fields are in the index
                  ⇒ FETCH stage is elided entirely
```

| Component            | Single responsibility                                                     |
| -------------------- | ------------------------------------------------------------------------- |
| `KeyString` encoding | Order-preserving byte serialization so B+ tree comparison is `memcmp`     |
| Index B+ tree        | Ordered key → `RecordId` mapping                                          |
| `RecordId`           | Stable 64-bit handle to a document, decoupled from physical location      |
| Multikey flag        | Per-index marker that at least one document indexed an array at that path |
| Prefix compression   | Store shared leaf-page key prefixes once                                  |

#### How Each Component Works

**`KeyString`**

- Encodes BSON values into bytes such that byte order equals BSON canonical sort order (§1.1), so
  the tree never needs to interpret BSON during comparison.
- This encoding change (4.2) is what removed the old **1024-byte index key limit**. Before 4.2,
  indexing a long string field would fail the write (or silently skip the document, depending on
  version/settings); since 4.2 with FCV 4.2+, long keys are allowed.
  Defeater: allowed does not mean advisable. A 4 KB index key wrecks page fanout — fewer keys per
  page means a taller tree and more page reads per lookup.

**Index B+ tree**

- Limits: **64 indexes per collection**, **32 fields per compound index** (Limits & Thresholds, 8.0).
- Compound index keys are ordered left-to-right, so the index supports queries on any **prefix** of
  its fields — `{a:1, b:1, c:1}` serves `{a}`, `{a,b}`, `{a,b,c}` but not `{b}` or `{b,c}`.
- Sort direction matters only for _multi-field_ sorts: `{a:1, b:1}` can serve `sort({a:1,b:1})` and
  `sort({a:-1,b:-1})` (walk backwards) but **not** `sort({a:1,b:-1})`.

**Multikey indexes**

- When any document has an array at an indexed path, the index generates **one entry per array
  element** and the index is permanently flagged multikey.
- Defeater set (these are the ones that get asked):
  - **At most one array field per compound index.** `{tags: 1, comments.body: 1}` fails to insert a
    document where both are arrays (`CannotIndexParallelArrays`).
  - A multikey index **cannot cover** a query — the server can't reconstruct the original array from
    index entries, so a FETCH is always required.
  - The multikey flag is **not cleared** when the arrays go away. Delete every array document and
    the index stays multikey until rebuilt, keeping the planner's restrictions in place.
  - Sorting on a multikey field can require a blocking sort even though an index exists, because
    index order is over elements, not over documents.

**Other index types — the ones with real gotchas**

| Type                                  | Mechanism                                                       | The defeater                                                                                                                                                                                                                                                          |
| ------------------------------------- | --------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `hashed`                              | Indexes `hash(value)`                                           | No range queries, no sort. Cannot be a unique index in a compound with a range field the way you'd hope.                                                                                                                                                              |
| `TTL` (`expireAfterSeconds`)          | Background thread scans every **60 s** and deletes expired docs | Deletion is _not_ prompt — documents can persist minutes past expiry under load, so it is not a security control. TTL threads don't run on secondaries (deletes replicate via oplog). Field must be a `Date` or array of `Date`; wrong type ⇒ silently never expires. |
| `partial` (`partialFilterExpression`) | Indexes only documents matching a predicate                     | The planner uses it **only** if it can prove the query is a subset of the filter. `{status:"OPEN"}` partial index will not serve `find({status: {$in:["OPEN","NEW"]}})`.                                                                                              |
| `sparse`                              | Skips documents missing the field                               | A sparse index cannot serve a sort that must include missing-field documents. Largely superseded by `partial`.                                                                                                                                                        |
| `unique`                              | Unique constraint via the index                                 | Uniqueness is per-shard-key-scoped on sharded collections — a unique index must be prefixed by the shard key, otherwise it cannot be enforced globally. Nulls/missing count as one value, so a sparse+unique combination is usually what you actually wanted.         |
| `wildcard` (`$**`, since 4.2)         | Indexes every path                                              | Cannot be compound with non-wildcard fields (limited support added later — verify per version), and the planner treats it conservatively. It is an escape hatch for genuinely unknown query shapes, not a substitute for knowing your access patterns.                |
| `text`                                | Term index with stemming/stop-words                             | One text index per collection. Scoring is not competitive with Lucene. `$text` cannot be combined with `$or` freely and can't be used with `hint()`.                                                                                                                  |
| `2dsphere`                            | GeoJSON on a spherical model, S2 cells                          | `2d` (legacy, planar) and `2dsphere` are not interchangeable; mixing them produces wrong distances at scale.                                                                                                                                                          |

**Index builds**

- Since **4.2**, index builds use a single "hybrid" method that holds an exclusive lock only briefly
  at the start and end; the collection remains writable in between. The old `{background: true}`
  option is deprecated/ignored.
- On a replica set, the build runs on all members and the primary waits for a majority to finish
  before committing. So an index build's duration is bounded by the _slowest_ member.
  Defeater: "index builds are online now" is only true for availability, not for resource usage —
  a build on a large collection saturates disk and cache and will degrade the node.

#### Design Decisions, Tradeoffs & Best Practices

**Decisions the designers made**

| Decision                                                     | Alternative rejected                 | Why                                                                                                                                                                                    |
| ------------------------------------------------------------ | ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Secondary index → `RecordId` → document (non-clustered)      | Clustered index on `_id` like InnoDB | Secondary index entries stay small and stable; a document move doesn't rewrite every index. Cost: every non-covered query pays a second B+ tree lookup                                 |
| Multikey (index into arrays)                                 | Require normalization                | Makes the document model actually queryable. Cost: index size proportional to array cardinality; covering impossible                                                                   |
| Prefix compression on index pages, not block compression     | Block-compress index pages           | Index pages are traversed constantly; decompressing on every descent is too expensive. Cost: worse ratio than collection data                                                          |
| Clustered collections (since 5.3, `clusteredIndex` on `_id`) | Only non-clustered                   | Removes the FETCH hop for `_id` lookups on the collections where that dominates. Cost: only `_id`, and secondary indexes now store the full `_id` as their pointer, making them larger |

**Decisions you have to make**

| Decision                    | Deciding variable                                                                                                                              |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Which compound indexes      | Query shapes × selectivity. Follow ESR (§2.2).                                                                                                 |
| How many indexes            | Write amplification: every index is an extra B+ tree write per insert. If write latency matters, count them.                                   |
| Index on an array field     | Average and p99 array length. A 10 000-element array produces 10 000 index entries per document.                                               |
| `hashed` vs range shard key | §4.1                                                                                                                                           |
| Partial vs full index       | If a predicate is in ≥95% of queries and cuts the indexed set ≥10×, partial wins. Otherwise the planner-eligibility complexity isn't worth it. |

| Option                               | Buys you                                            | Costs you                                                       | Choose when                             |
| ------------------------------------ | --------------------------------------------------- | --------------------------------------------------------------- | --------------------------------------- |
| One wide compound index              | Serves many prefix queries with one tree            | Large keys, poor fanout, ordering rigid                         | Query shapes share a stable prefix      |
| Several narrow indexes               | Precise, small                                      | N× write amplification; planner has more candidates to evaluate | Genuinely distinct access patterns      |
| Wildcard index                       | Query anything without knowing shapes               | Bigger, slower, planner-conservative, no sort help              | Truly ad-hoc / per-tenant custom fields |
| Covering index (all fields in index) | Elides FETCH entirely — often 2–5× fewer page reads | Index grows to hold projected fields; not possible if multikey  | Hot read path with a small projection   |

**Best practices** (rule → failure it prevents)

- **Every production query must have an `explain("executionStats")` where
  `totalKeysExamined / nReturned` is near 1.** Prevents the index that "exists" but is being used as
  a wide range scan with a post-filter, which looks indexed in `explain`'s stage name and behaves
  like a scan.
- **Never create an index without deleting one, past ~8 indexes on a write-hot collection.** Prevents
  unbounded write amplification, which shows up as rising replication lag, not as a query problem.
- **Use `$indexStats` before dropping an index.** Prevents dropping the index that serves a monthly
  batch job nobody remembered.
- **Set `expireAfterSeconds` only on a `Date`-typed field, and verify with a canary document.**
  Prevents a TTL index that silently never deletes anything, which surfaces as unbounded collection
  growth six months later.
- **On sharded collections, prefix every unique index with the shard key.** Prevents the discovery
  at shard time that your uniqueness constraint is unenforceable and has to be moved to the
  application.
- **Build indexes with a rolling procedure on very large collections, or accept the node-level
  performance hit and schedule it.** Prevents "the build is online" turning into a saturated primary.

#### Failure Modes, Exception Handling & Production Issues

| Failure                                   | Trigger                                                 | Blast radius                                                     | Detection signal                                                       | Mitigation                                                                        |
| ----------------------------------------- | ------------------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| Multikey index explosion                  | Array field with high cardinality gets indexed          | Index size ≫ collection size; cache pressure; slow writes        | `indexSizes` in `collStats` vs `size`                                  | Don't index the array; or index a derived, deduplicated, bounded field            |
| `CannotIndexParallelArrays`               | Compound index over two array paths, document has both  | That write fails; others succeed                                 | Write error 171                                                        | Redesign — one array per compound index, always                                   |
| TTL never fires                           | Field is a string, not a `Date`                         | Unbounded collection growth                                      | Collection count grows monotonically; `ttl.deletedDocuments` flat at 0 | Type-fix + backfill; validator to enforce the type                                |
| Partial index not used                    | Query predicate isn't provably a subset of the filter   | Silent fallback to COLLSCAN                                      | `explain` shows COLLSCAN despite the index existing                    | Match the predicate exactly, or use a full index                                  |
| Blocking sort `ExceededMemoryLimit`       | `sort()` on a non-indexed field over a large result set | Query fails at 100 MB (32 MB in older versions)                  | Error 292 / `SORT` stage with `memLimit`                               | Index to support the sort; or `allowDiskUse` (aggregation) and accept the latency |
| Write amplification from too many indexes | 12 indexes on a high-insert collection                  | Replication lag → stale secondary reads → majority-write latency | Secondary lag; `insert` op latency p99                                 | Consolidate via `$indexStats`; drop unused                                        |
| Index build saturates node                | Build on a multi-TB collection                          | Node-wide latency; possible election if it becomes unresponsive  | Disk saturation during build                                           | Rolling build across members; schedule off-peak                                   |

**Exception handling.** Index-violation errors (`DuplicateKey`, code 11000) are **terminal** for
that write — retrying is pointless unless the app's intent was an upsert. `CannotIndexParallelArrays`
is terminal and structural. `ExceededMemoryLimit` on a blocking sort is terminal for that query
shape and is a design signal, not a transient. Poison-pill risk lives in bulk-write pipelines using
`ordered: true`: one `DuplicateKey` aborts the remainder of the batch, so a retry re-sends
already-applied writes; use `ordered: false` and reconcile the per-document error array.

**Real production issues**

- **Public, cited:** the removal of the 1024-byte index key limit and the introduction of the new
  `KeyString` format is documented in the MongoDB 4.2 release notes; prior to that, an oversized key
  caused the _insert to fail_ on a collection with `failIndexKeyTooLong: true` and, in earlier
  configurations, caused documents to be silently absent from the index — meaning queries returned
  incomplete results with no error. That silent-incorrectness mode is the reason the format changed.
- `Canonical failure pattern (not a specific incident)` — **The index that exists and doesn't
  help.** Symptom: a dashboard query takes 8 s; `explain` shows `IXSCAN`, so the team concludes the
  index is fine and blames the network. Root cause: index `{tenantId: 1}` with a post-filter on
  `status` and an in-memory sort on `createdAt`; `totalKeysExamined` = 2.1 M, `nReturned` = 20. Fix:
  compound index `{tenantId: 1, status: 1, createdAt: -1}` following ESR. Guardrail: a CI check that
  runs `explain` on every registered query shape and fails the build if
  `totalKeysExamined / nReturned > 10` — because "there is an IXSCAN in the plan" is not the same
  claim as "the index is selective," and only a ratio catches the difference.

#### Interview Questions

**Q:** How does a secondary index lookup differ from an `_id` lookup?

**L4 answer** — Both descend a B+ tree, but a secondary index stores `key → RecordId`, so after
finding the entry the server does a second lookup in the collection's row-store to fetch the
document (the FETCH stage). An `_id` lookup on a clustered collection (5.3+) or a covered query
skips that second hop.

**L5 answer** — Plus: that second hop is the reason index _selectivity_ matters more than index
_existence_. Each FETCH is a random read into the collection tree, so an index that narrows 10 M
documents to 100 K still costs 100 K random reads, and if those pages aren't cached the query is
disk-bound regardless of the index. That's what makes covering indexes disproportionately valuable
— they turn N random reads into a sequential leaf-page walk. The design reason MongoDB chose
non-clustered by default is that it decouples index entries from physical location: a document that
grows and gets rewritten doesn't invalidate every secondary index entry. InnoDB pays the opposite
price — its secondary indexes store the primary key, so they're larger and every secondary lookup
is two B+ tree descents. MongoDB's clustered collections (5.3+) opt into the InnoDB tradeoff for
`_id`-dominant workloads, and you take it when `_id` point-reads dominate and you have few secondary
indexes.

---

**Q:** What is a multikey index and what can't it do?

**L4 answer** — An index on a field whose value is an array; the index generates one entry per array
element. Restrictions: at most one array field per compound index (parallel arrays fail to insert),
and a multikey index cannot cover a query because the array can't be reconstructed from index
entries. The multikey flag persists once set, even after the arrays are removed.

**L5 answer** — Plus: the sizing consequence is the one that bites. Index entry count is
`documents × average array length`, so a `tags` array averaging 12 elements makes the index 12×
larger than a scalar index on the same collection — and that index competes for the same WiredTiger
cache as the documents. I've seen index-to-data ratios exceed 1:1 from a single multikey index.

The subtler correctness issue: `$elemMatch` versus multiple predicates. `find({scores: {$gt: 80,
$lt: 90}})` matches a document with `scores: [95, 85]` because _some_ element satisfies each
predicate independently — the index bounds are computed per-element, not per-document. You need
`$elemMatch` to require one element to satisfy both, and the planner's index bounds for
`$elemMatch` are tighter as a result. That's a bug class that passes tests written with
single-element arrays and fails in production.

If I owned this, the design move is to not index the array at all: maintain a bounded, deduplicated,
derived scalar or small array (`tagCount`, `primaryTag`) for the common query, and reserve the
multikey index for the genuinely low-cardinality case.

---

**Q:** You have `{a: 1, b: 1, c: 1}`. Which of these use it, and how well?
`find({a: 1})`, `find({b: 2})`, `find({a: 1, c: 3})`, `find({a: 1}).sort({b: 1})`,
`find({a: {$gt: 1}, b: 2})`.

**L4 answer** —

- `{a:1}` — yes, prefix, fully bounded.
- `{b:2}` — no. Not a prefix. COLLSCAN (or a wasteful full index scan).
- `{a:1, c:3}` — yes for `a`; `c` cannot be bounded because `b` is unconstrained, so `c` becomes a
  filter applied to index keys, not a bound. Works but examines more keys than it returns.
- `{a:1}.sort({b:1})` — yes, and the sort is free: within `a=1` the index is already ordered by `b`.
- `{a: {$gt:1}, b:2}` — the range on `a` prevents `b` from being a bound; `b` is a residual filter.
  This is exactly the ESR violation.

**L5 answer** — Plus the general rule and why: an index gives you _contiguous bounds_ only up to the
first non-equality predicate. Everything after that is a filter over a range scan, so
`totalKeysExamined` inflates. That's the mechanical reason behind ESR — Equality fields first
(they pin the range), then Sort fields (so the walk emerges pre-ordered), then Range fields (they
must be last because they end contiguity).

For the last case specifically, the fix is `{b: 1, a: 1}`: equality on `b` pins, range on `a` walks.
And that's the practical point — the _same set of fields_ in a different order is a different
index with different capability, which is why "we already have an index on those fields" is not an
answer to "is this query fast." At L5 I'd also note that the planner will sometimes choose a plan
using `{a,b,c}` for `{b:2}` as a full index scan if the index is much smaller than the collection,
so `explain` showing `IXSCAN` there is not evidence of health — check `totalKeysExamined`.

---

**Q:** When would you use a partial index over a full index?

**L4 answer** — When queries always include a predicate that selects a small fraction of the
collection — e.g. `{status: "OPEN"}` where 2% of orders are open. The partial index only stores
those documents, so it's smaller, cheaper to maintain, and more cache-resident. The catch: the
planner only uses it when it can prove the query predicate is a subset of `partialFilterExpression`.

**L5 answer** — Plus the failure mode that makes people abandon them: the subset proof is
syntactic and conservative. A partial index filtered on `{status: "OPEN"}` will **not** serve
`find({status: {$in: ["OPEN"]}})` in older versions, and will not serve `{status: {$ne: "CLOSED"}}`
at all. So the index silently stops being used after an innocuous query refactor, and you get a
COLLSCAN with no error. That's why I gate partial indexes behind an `explain` assertion in CI.

The real win case is a soft-delete or state-machine collection where 98% of rows are terminal and
never queried. There the partial index isn't a 2× improvement, it's the difference between an index
that fits in cache and one that doesn't — a step function. Against that, if the selective predicate
appears in only _some_ queries, you need the full index anyway and you're now maintaining two.
Deciding variable: does _every_ query on this path carry the predicate? If not, don't.

#### L5-Only Questions

**Q:** A collection has 11 indexes. Write throughput has degraded 40% over six months and
replication lag now spikes during business hours. Walk me through the remediation.

**L5 answer** — First, confirm the causal chain rather than assuming it. Every insert writes 1
collection entry + 11 index entries, each a separate B+ tree descent and dirty page. So write cost
is roughly linear in index count, and the _replication_ symptom follows because secondaries apply
the same writes with the same index maintenance — lag is the honest signal that the write path is
over budget.

Diagnosis order:

1. `$indexStats` per index, over a window long enough to capture monthly jobs (I'd want 35+ days;
   `$indexStats` counters reset on restart, so I'd snapshot them to a time series rather than
   reading them once — this is the step people skip and then drop a needed index).
2. Cross-reference with `db.currentOp` / profiler-collected query shapes so I can name which shape
   each index serves. An index with usage but no identifiable owner is a red flag for a BI tool.
3. Check for redundancy: `{a:1}` is subsumed by `{a:1,b:1}` and can go. `{a:1,b:1}` and `{b:1,a:1}`
   are not redundant and both may be needed — resist the instinct to "consolidate" those.
4. Check `indexSizes` — one multikey index is often most of the cost, and dropping it is worth
   several scalar ones.

Remediation: drop in stages with a rollback plan, and use `hideIndex()` first rather than
`dropIndex()`. Hiding makes the index invisible to the planner while still maintaining it, so if a
query shape regresses you unhide instantly instead of rebuilding for four hours on a multi-TB
collection. That single practice is the difference between a 30-second rollback and an incident.

What I'd push back on: the framing that this is an index problem. 11 indexes usually means the
collection is serving too many access patterns, and the structural fix might be to move the
analytical shapes off MongoDB entirely — into the search/analytics tier — rather than to keep
tuning the trade between read and write on one collection.

---

**Q:** Design the index strategy for a multi-tenant collection: 4 000 tenants, extremely skewed
(the largest tenant is 30% of documents), queries always filter by `tenantId` plus 1–3 of about 15
optional filters, sorted by `updatedAt`.

**L5 answer** — The constraint that decides this is that 15 optional filters have up to 2^15 shapes,
so per-shape compound indexes are not an option. Three candidate strategies:

1. **`{tenantId: 1, updatedAt: -1}` plus residual filtering.** ESR-compliant: equality on tenant,
   then sort. Every query gets a bounded, pre-sorted walk within one tenant, and the optional
   filters are applied as residuals during the walk. Cost: for the 30% tenant, the walk is over
   ~1.2 M keys per query if the filters are selective. Works if you paginate — the walk stops after
   the page fills, so `totalKeysExamined` is bounded by page size _divided by_ filter selectivity,
   not by tenant size. That last point is the crux: it's fine when filters keep ~10%+ of the tenant,
   and catastrophic when a filter matches 0.01% because you walk the whole tenant to find nothing.

2. **Wildcard index `{"$**": 1}`scoped with`wildcardProjection`.** Handles arbitrary filters, but
gives up the sort (you'd get a blocking sort on `updatedAt`), and the planner won't combine it
   with the tenant equality as well as a purpose-built compound. I'd reject it: trading a guaranteed
   free sort for filter flexibility is the wrong direction when every query sorts.

3. **A small set of compound indexes covering the 4–5 filters that actually appear in >80% of
   traffic**, each prefixed `{tenantId: 1, <filter>: 1, updatedAt: -1}`, plus strategy 1 as the
   fallback. This is what I'd ship. You get the ESR-optimal path for the common shapes and a
   correct-if-slower path for the tail, and you can measure the tail with the profiler and promote a
   shape into its own index when it earns one.

The skew needs a separate answer. If the 30% tenant genuinely degrades, the move is not a better
index — it's isolation: shard on `{tenantId: "hashed"}` so that tenant's data spreads, or physically
separate the whale onto its own cluster. Indexing cannot fix a workload where one key is 30% of the
data, because index bounds within that tenant are still over a huge range. I'd surface that early
rather than iterate on indexes for a quarter.

I'd also insist on `maxTimeMS` on every query here, because multi-tenant skew means the same query
shape has wildly different costs per tenant, and without a deadline the whale tenant's slow queries
become everyone's queue depth.

---

### 2.2 Query Planner, Plan Cache, and ESR

#### Concept

- **What it is** — MongoDB's planner is **empirical, not cost-model-based**: it enumerates candidate
  plans, _actually runs_ them in parallel for a bounded trial, picks the one that produced results
  most efficiently, and caches that choice keyed by query shape.

- **What it solves** — Removes the need for accurate table statistics and a cost model. A
  cost-based optimizer (PostgreSQL, Oracle) needs histograms, and histograms on schemaless nested
  documents with arrays are hard to maintain and easy to get catastrophically wrong.

- **What it replaced** — Cost-based optimization. Specifically insufficient here because MongoDB has
  no fixed schema to build statistics against, field cardinality can vary per tenant within one
  collection, and multikey arrays make selectivity estimation unreliable.

  Defeater: the empirical approach has its own failure — it optimizes for the _first_ execution's
  data distribution and caches it, so a plan chosen when a tenant had 100 documents persists after
  that tenant has 10 M.

- **What it works with / ecosystem** — sits above the index layer (§2.1), below the aggregation
  framework. Two execution engines exist: the **classic** engine and the **SBE** (slot-based
  execution) engine introduced in **5.0**; eligibility for SBE has changed materially across 5.0 →
  7.0 → 8.0, so read `explain().queryPlanner.winningPlan.queryFramework` rather than assuming.

- **Place in the world** — you meet it every time you run `explain()`. **Wrong answer to**:
  workloads needing plan stability guarantees — MongoDB has `hint()` and index filters, but nothing
  as strong as Oracle's stored outlines.

#### Architecture & Core Components

```
      query
        │
        ▼
  ┌──────────────┐   shape hit    ┌───────────────┐
  │ canonicalize │ ─────────────▶ │  PLAN CACHE   │──▶ cached plan
  │ → query shape│                │ key = shape   │      │
  └──────┬───────┘                └───────────────┘      │ replan if
         │ miss                                          │ works ≫ expected
         ▼                                               ▼ (10× regression)
  ┌───────────────────┐
  │ plan ENUMERATION  │  index intersection, prefix matching, $or subplanning
  └────────┬──────────┘
           ▼
  ┌───────────────────────────────────────────────┐
  │ TRIAL PERIOD — run all candidates round-robin  │
  │ stop at: 101 results, OR ~10 000 "works",      │
  │          OR 30% of collection scanned          │
  │ score = productivity (advances / works)        │
  │         + bonuses (no blocking sort, covered)  │
  └────────┬──────────────────────────────────────┘
           ▼
     winning plan → executed to completion → cached
```

| Component     | Single responsibility                                                                  |
| ------------- | -------------------------------------------------------------------------------------- |
| Canonicalizer | Reduce a query to a _shape_ (predicate structure + sort + projection, values stripped) |
| Enumerator    | Produce candidate plans from eligible indexes                                          |
| Trial runner  | Execute candidates concurrently for a bounded budget                                   |
| Scorer        | Rank by productivity plus structural bonuses                                           |
| Plan cache    | Map shape → winning plan; hold the works-count that justified it                       |
| Replanner     | Evict and re-enumerate when a cached plan underperforms                                |

#### How Each Component Works

**Query shape**

- Values are stripped: `{tenantId: "A"}` and `{tenantId: "B"}` are the **same shape** and share one
  cached plan.
- This is the single most important fact about the plan cache, because it means a skewed collection
  gets one plan for a tenant with 10 documents and a tenant with 10 M documents.
- Sort and projection are part of the shape; `$in` with different array lengths can produce
  different shapes.

**Trial period**

- Budget parameters (defaults, subject to change; verify with
  `db.adminCommand({getParameter:1, internalQueryPlanEvaluationWorks:1})`):
  `internalQueryPlanEvaluationWorks` ≈ 10 000 units, `internalQueryPlanEvaluationCollFraction` ≈ 0.3,
  and an early stop at 101 results.
- A "work" is one unit of plan progress — an index-key advance, a document fetch, a filter
  evaluation.
- Scoring is **productivity** (`advances / works`) plus bonuses for not needing a blocking sort and
  for covered plans.
- Defeater: because the trial stops at 101 results, a plan that is fast to first-101 and terrible
  thereafter can win. This is exactly the pathology behind "the query was fine in staging."

**Plan cache and replanning**

- Cached entries store the works count of the winning plan's trial. On subsequent executions, if the
  plan's actual works exceeds that by roughly **10×** (`internalQueryCacheEvictionRatio`), the entry
  is evicted and the query is re-planned.
- The cache is per-`mongod`, in-memory, and **cleared on restart, on index creation/drop, and on
  most catalog changes**.
- Consequence: after a restart or an index build, the first execution of every shape pays trial cost.
  On a large deployment this is a visible latency bump — a real reason to warm caches before
  taking traffic.

**ESR rule (Equality, Sort, Range)**

- Compound index field order should be: fields with **equality** predicates, then fields used for
  **sort**, then fields with **range** predicates. (MongoDB "Performance Best Practices / ESR Rule"
  docs.)
- Mechanism: equality predicates pin an index value, keeping the scanned region contiguous. Within
  that region, the index is already ordered by the next field, so a sort on it is free. A range
  predicate ends contiguity — anything after it can only be a residual filter, not a bound.
- Defeater: ESR is a heuristic about _bounds_, and it loses to selectivity in one case — if a range
  is extremely selective (`ts > now-1s` on a firehose) and the equality field is not (`region` with
  3 values), a range-first index can win. ESR is right by default; measure the exception.

**SBE**

- Slot-based execution compiles a plan into a tree of slot-passing stages, avoiding per-document
  BSON materialization between stages. Introduced 5.0. Eligibility narrowed in 7.0 and shifted again
  in 8.0.
- Practical impact: it matters most for aggregation pipelines with `$group`/`$lookup`. Do not
  claim a speedup number without measuring; the honest statement is "it changes the constant factor
  on pipeline execution, not the algorithmic complexity."

#### Design Decisions, Tradeoffs & Best Practices

**Decisions the designers made**

| Decision                       | Alternative rejected                 | Why                                                                                                                                                                                      |
| ------------------------------ | ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Empirical trial                | Cost-based optimizer with histograms | No stable schema to build statistics on; array/multikey selectivity is not estimable. Cost: no cross-query global optimization; plans can be chosen on unrepresentative first executions |
| Value-stripped query shapes    | Per-value plan caching               | Bounded cache size, high hit rate. Cost: skewed data gets one plan for all values                                                                                                        |
| Replan on 10× works regression | Never replan / always replan         | Self-healing without constant re-trial cost. Cost: you eat 10× the work _before_ it heals, once per regression                                                                           |
| Cache in memory, per-node      | Persistent shared cache              | Simplicity; no distributed cache invalidation. Cost: cold start after every restart and every index change                                                                               |

**Decisions you have to make**

| Decision                                         | Deciding variable                                                                                                                                                                   |
| ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `hint()` a plan or trust the planner             | Whether the shape's cost varies with values (multi-tenant skew ⇒ hint or split shapes)                                                                                              |
| Index filters (`planCacheSetFilter`) vs `hint()` | `hint()` is per-query and visible in code; index filters are server-side and invisible to developers. Default to `hint()` — invisible server state is an incident waiting to happen |
| Warm the cache after deploy/restart              | Whether cold-start p99 breaches SLO                                                                                                                                                 |
| ESR vs selectivity-first ordering                | Measured `totalKeysExamined` on real data. Default ESR                                                                                                                              |

| Option            | Buys you                         | Costs you                                                               | Choose when                                                     |
| ----------------- | -------------------------------- | ----------------------------------------------------------------------- | --------------------------------------------------------------- |
| Trust the planner | Zero maintenance; adapts to data | Skew pathologies; plan flips after restart                              | Uniform data distribution                                       |
| `hint()`          | Deterministic plan               | You now own the decision forever, including after the data changes      | Multi-tenant skew, or a query where a wrong plan is an incident |
| Index filter      | Deterministic, no code change    | Server-side hidden state; lost on restart; a trap for the next engineer | Emergency mitigation only                                       |

**Best practices** (rule → failure it prevents)

- **`explain("executionStats")`, never `explain()` alone.** Prevents reasoning from
  `winningPlan.stage` (which says `IXSCAN` even for a terrible plan) instead of from
  `totalKeysExamined` / `nReturned` / `executionTimeMillis`, which is the actual evidence.
- **Run `explain` against production-shaped data volume.** Prevents the staging-passes /
  production-fails class caused by the trial period's 101-result early stop.
- **Enable the profiler at `slowms` for a sampled window, not permanently.** Prevents both blindness
  and the write amplification of profiling everything.
- **Give every user-facing query a `maxTimeMS`.** Prevents a bad plan from converting into unbounded
  queue depth; MongoDB has no statement timeout by default.
- **Never leave an index filter in place after an incident.** Prevents the next engineer spending a
  day on "why is the planner ignoring my new index."

#### Failure Modes, Exception Handling & Production Issues

| Failure                      | Trigger                                       | Blast radius                                                   | Detection signal                                        | Mitigation                                                      |
| ---------------------------- | --------------------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------- | --------------------------------------------------------------- |
| Bad cached plan from skew    | First execution of a shape hits a tiny tenant | That shape is slow for large tenants until 10× replan triggers | `executionTimeMillis` bimodal by value, not by shape    | Split the shape, or `hint()`                                    |
| Plan flip after restart      | Cache cleared; different trial outcome        | Latency changes with no deploy                                 | Latency step change correlated with process restart     | Warm-up queries in the readiness probe; `hint()` critical paths |
| Cold cache after index build | Cache invalidated by catalog change           | Trial cost on every shape at once                              | Latency bump immediately post-build                     | Build during low traffic; warm after                            |
| Trial-period mis-pick        | Plan fast to first 101 rows, slow after       | Query times out only on large result sets                      | `explain` differs from observed prod behaviour          | Test with realistic `limit` and data volume                     |
| `$or` subplanning blowup     | Large `$or` with heterogeneous branches       | Enumeration explosion, high planning CPU                       | High `executionTimeMillis` with low `totalKeysExamined` | Rewrite as `$in` where possible; split into separate queries    |
| Unbounded query, no timeout  | Missing `maxTimeMS`                           | Connection pool exhaustion → cluster-wide                      | Rising `currentOp` counts with high `secs_running`      | `maxTimeMS` everywhere; `killOp` runbook                        |

**Exception handling.** `MaxTimeMSExpired` (code 50) is **retryable in principle but almost always
shouldn't be** — the same query will take the same time. Treat it as a signal to degrade (return
partial results, or fail the feature) rather than to retry.
`ExceededTimeLimit` on a cursor `getMore` kills the cursor; the client must restart the iteration,
which is why long-running exports need a resumable key rather than a long-lived cursor.
`CursorNotFound` (code 43) after 10 minutes of inactivity (`cursorTimeoutMillis` default 600 000) is
terminal for that cursor — poison-pill risk lives in an export job whose downstream is slow enough
to idle the cursor out, which then restarts from the beginning forever.

**Real production issues**

- `Canonical failure pattern (not a specific incident)` — **Plan flip on failover.** Symptom: p99 on
  one endpoint triples immediately after a routine primary election, with no deploy. Root cause: the
  new primary's plan cache is empty; its trial for that shape ran against a moment when the working
  set was cold, and it cached the plan that reached 101 results first — an index scan that was fast
  to the first page and pathological over the full range. Fix: `hint()` the correct index on that
  path. Guardrail: a readiness probe that executes the top-20 query shapes before the node accepts
  traffic, so the trial happens under controlled conditions rather than under production load.
- `Canonical failure pattern (not a specific incident)` — **The multi-tenant shape.** Symptom: one
  customer reports 30 s page loads; everyone else is at 80 ms; the query is identical. Root cause:
  value-stripped shape sharing, plan chosen for a small tenant. Fix: two options — force the plan
  with `hint()`, or make the shapes different by adding a tenant-tier literal into the predicate so
  large tenants get their own cache entry. I'd take `hint()` because the second is a hack that the
  next refactor deletes.

#### Interview Questions

**Q:** How does MongoDB choose an index?

**L4 answer** — It doesn't use a cost model. It enumerates candidate plans from eligible indexes and
runs them concurrently for a bounded trial — stopping at 101 results or roughly 10 000 work units —
then scores them on productivity (results per unit of work), with bonuses for avoiding a blocking
sort and for covered plans. The winner is cached by query shape and reused. If a cached plan later
performs ~10× worse than its trial, the entry is evicted and the query is re-planned.

**L5 answer** — Plus why that design, and where it breaks. Empirical selection exists because
MongoDB has no schema to build histograms on and multikey arrays make selectivity estimation
unreliable — a cost model would be confidently wrong. The price is that the choice is made from one
sample, and the sample is bounded by 101 results, so a plan that is cheap to the first page and
expensive thereafter wins the trial and loses in production. Combined with value-stripped shapes,
that produces the classic multi-tenant pathology: one plan serves a 100-document tenant and a
10-million-document tenant.

The 10× replan is a genuine self-healing mechanism, but note what it means operationally — you must
_experience_ a 10× regression before it fires, once, per node, per cache clear. On a shape that runs
100 times a second, that's a visible incident. So for paths where a wrong plan is an SLO breach, I
pin with `hint()` and accept ownership of that decision, with a review whenever the collection's
index set changes. What I would _not_ do is use `planCacheSetFilter` — it's server-side invisible
state that survives no code review and is lost on restart, which is the worst of both.

---

**Q:** Explain ESR and give me a case where it's wrong.

**L4 answer** — Order compound index fields Equality → Sort → Range. Equality predicates pin the
scanned region to a contiguous block; within that block the index is already sorted by the next
field, so a sort on it is free; a range predicate ends contiguity, so nothing after it can be a
bound. Violating it — putting a range before a sort field — forces a blocking in-memory sort.

**L5 answer** — Plus the exception. ESR optimizes for _bound tightness_, not for _absolute rows
examined_, and those diverge when the range is far more selective than the equality. Take a
telemetry collection: `find({region: "us-east", ts: {$gt: now-5s}}).sort({ts: -1})`. `region` has 4
values, so ESR's `{region:1, ts:-1}` is right — equality pins to a quarter of the collection, and
the sort is free. But if the equality field were `dataCenterId` with 4 000 values and near-uniform
distribution, and the range were 5 seconds out of 90 days, both orderings pin tightly and you'd
measure rather than reason.

The genuine exception is when the sort field and the range field are the _same_ field, which is
extremely common in time-series pagination (`ts > X`, `sort by ts`). There ESR is trivially
satisfied because the range field is also the sort field and the index walk is both bounded and
ordered — people mis-apply ESR here and add a redundant index. The check that settles any of these
is `totalKeysExamined / nReturned` under `explain("executionStats")` on production-volume data;
ESR is the prior, not the proof.

---

**Q:** Same query, same code, but one customer is 100× slower. Where do you look?

**L4 answer** — The plan cache. Query shapes are value-stripped, so all customers share one cached
plan chosen from whichever value first triggered the trial. Confirm with `explain("executionStats")`
run with the slow customer's actual values, and compare `totalKeysExamined` against a fast
customer's. Also check whether that customer's data is skewed enough that a different index would
win.

**L5 answer** — Plus how I'd distinguish it from the other three causes, because "plan cache" is
only one of them:

1. **Plan cache / shape sharing** — `explain` with the slow value shows a different
   keys-examined ratio than the fast value under the _same_ winning plan. Fix: `hint()`.
2. **Data skew independent of plan** — the plan is optimal and the tenant just has 30% of the
   documents. `explain` shows a high `nReturned` too. No index fixes this; the fix is isolation —
   shard, or move the whale to its own cluster.
3. **Working set** — the whale's pages aren't cache-resident so every FETCH is a disk read.
   `explain` looks identical between tenants but `executionTimeMillis` diverges; the tell is in
   `wiredTiger` cache counters, not in `explain`. Fix is RAM or a covering index.
4. **Unbounded array / document size** — the tenant's documents are 40× larger, so the same
   `nReturned` moves 40× the bytes.

I'd run all four checks before touching an index, because three of them are made _worse_ by adding
one. And regardless of cause, the immediate mitigation is a `maxTimeMS` on that path so a slow
tenant can't consume the shared connection pool — noisy-neighbour containment first, root cause
second.

#### L5-Only Questions

**Q:** Design a regression gate that catches query-performance regressions before deploy.

**L5 answer** — The naive version — assert `executionTimeMillis < N` — is worthless: it's
machine-dependent, cache-dependent, and flaky, so it gets muted within a month. The gate has to
assert on _plan shape and work_, which are deterministic given data.

What I'd build:

1. A registry of query shapes extracted from the code — in Java that means every
   `MongoCollection.find/aggregate` call site behind a named repository method, so the shape is a
   reviewable artifact rather than an emergent string.
2. A seeded fixture dataset with production-_shaped_ cardinality (not production data — that's a
   compliance problem, and not production _volume_ — that's too slow for CI; production
   _distribution_ at 1/1000 scale, with the skew preserved, because skew is what breaks plans).
3. For each shape, run `explain("executionStats")` with `allPlansExecution` and assert three
   things: (a) `winningPlan` contains no `COLLSCAN` and no blocking `SORT`, (b)
   `totalKeysExamined / nReturned ≤ threshold` per shape, (c) the winning index _name_ matches a
   checked-in expectation. (c) is the one that catches the real regressions — a developer adds an
   index for a new feature and it wins the trial for an existing shape and is worse.
4. Fail the build with a diff of expected vs actual plan, and require an explicit expectation update
   in the PR. That makes plan changes reviewable, which is the actual goal.

Limits I'd state honestly: this cannot catch cache-residency regressions (a plan can be identical
and 50× slower because the index no longer fits in RAM), and it cannot catch skew that only exists
at production volume. Those need production canarying with the profiler, not CI. So the gate is
necessary and not sufficient, and I'd pair it with a profiler-fed dashboard of
`keysExamined/docsReturned` by shape in prod.

---

**Q:** Your team wants to add `planCacheSetFilter` on three hot queries to stop plan flapping.
Argue the decision.

**L5 answer** — I'd reject it and use `hint()` instead, for one reason that outweighs the
convenience: index filters are _server-side, invisible, and non-durable_. They don't appear in the
application repository, so a code review of the query shows a plan that isn't what runs; they're
lost on restart, so the behaviour silently reverts during a failover; and they're per-`mongod`, so a
5-node replica set can have five different effective plans if someone applied the filter unevenly.
Every one of those is a debugging trap that costs more than the flapping did.

`hint()` has real costs and I'd name them: it's brittle across index renames, it prevents the
planner from ever using a better index you add later, and it converts "the database adapts" into
"an engineer must remember." So I'd scope it narrowly — only the shapes where a wrong plan breaches
an SLO, with the index name as a constant next to the query, plus the CI plan-assertion gate above
so a dropped index fails the build rather than the request.

There's also the option nobody proposes: fix the cause. Plan flapping usually means two plans have
genuinely similar trial scores, which means the index set is ambiguous for that shape. Adding one
purpose-built compound index that dominates both candidates removes the ambiguity permanently and
requires no pinning at all. That's more work than a filter and it's the answer that's still correct
in two years, so it's where I'd start.

---

## 3. Replication

### 3.1 Replica Sets, Elections, and the Oplog

#### Concept

- **What it is** — A replica set is a group of `mongod` processes (max **50** members, max **7**
  voting) holding the same data, with exactly one **primary** accepting writes and secondaries
  replicating asynchronously by tailing the primary's **oplog**.

- **What it solves** — Automatic failover (no human in the loop for a node loss), durability beyond
  one machine, and read scale-out for stale-tolerant traffic.

- **What it replaced** — MongoDB's older master/slave replication, which had no automatic election
  and required manual promotion. Insufficient because failover was an operational procedure, not a
  property of the system.

- **What it works with / ecosystem** — the oplog is a capped WiredTiger collection
  (`local.oplog.rs`); change streams, the MongoDB Kafka connector, and Atlas triggers all read it.
  Sharding (§4) composes replica sets — every shard _is_ a replica set, and so is the config server
  set (CSRS).

  Conflicts with: any assumption of synchronous replication. Replication is asynchronous;
  `w: "majority"` makes the _acknowledgement_ wait for a majority, it does not make the replication
  itself synchronous.

- **Place in the world** — every non-toy MongoDB deployment. **Wrong answer to**: multi-region
  active-active writes. A replica set has exactly one primary; a geographically distributed replica
  set gives you multi-region _durability_ and _reads_, with cross-region latency on every majority
  write. Multi-master requires a different system.

#### Architecture & Core Components

```
              client (driver holds topology + monitors all members)
                    │ writes
                    ▼
        ┌───────────────────────────┐
        │        PRIMARY            │
        │  applies write to WT      │
        │  appends to local.oplog.rs│◀── capped, idempotent entries
        └───────┬───────────┬───────┘
      oplog pull│           │oplog pull      heartbeats every 2 s
                ▼           ▼                (all-to-all)
        ┌────────────┐  ┌────────────┐
        │ SECONDARY  │  │ SECONDARY  │
        │ apply +    │  │ apply +    │
        │ own oplog  │  │ own oplog  │  ◀── secondaries may sync from
        └────────────┘  └────────────┘       another secondary (chaining)

  election: no heartbeat from primary for electionTimeoutMillis (10 000 ms)
         → candidate requests votes → needs strict majority of *voting* members
         → higher term wins; old primary steps down on seeing a higher term
```

| Component                | Single responsibility                                         |
| ------------------------ | ------------------------------------------------------------- |
| Primary                  | Sole write acceptor; sole oplog producer                      |
| Oplog (`local.oplog.rs`) | Ordered, idempotent, capped record of applied writes          |
| Secondary                | Pull, apply, and re-publish oplog; serve stale-tolerant reads |
| Heartbeat                | Liveness and topology propagation, every 2 s                  |
| Election (PV1)           | Choose a new primary with majority consent                    |
| Term                     | Monotonic epoch number that fences stale primaries            |
| Arbiter                  | Vote without holding data                                     |

#### How Each Component Works

**Oplog**

- A **capped collection**; default size **5% of free disk, min 990 MB, max 50 GB** (MongoDB docs,
  8.0). Once full, oldest entries are overwritten.
- Entries are **idempotent by construction**: the server rewrites non-deterministic operations
  before logging. `{$inc: {n: 1}}` is logged as `{$set: {n: <resulting value>}}`; `$push` with
  `$slice` is logged as the resulting array.
  Why: a secondary may apply an entry more than once during recovery, and idempotence makes
  re-application safe without the primary tracking per-secondary progress.
  Defeater: idempotence is per-entry. It does not make _transactions_ replayable — those get
  `applyOps` entries and a distinct commit protocol.
- **Oplog window** = wall-clock time covered by the current oplog contents. It is the single most
  important operational number in a replica set: a secondary that falls further behind than the
  window becomes `RECOVERING` and requires a **full initial sync**, which on a multi-TB node is
  hours.
  Defeater for "just size the oplog by disk %": the correct sizing input is
  `peak_write_rate × required_recovery_window`, where the required window must cover your longest
  maintenance operation (index build, backup restore, network partition). 5% of disk is a default,
  not a design.

**Replication flow**

- Secondaries **pull** (tail) the oplog; the primary does not push. This is a deliberate deviation
  from Raft, where the leader drives log replication.
- **Chaining** is enabled by default: a secondary may sync from another secondary that is closer,
  reducing primary egress in a multi-region set at the cost of one extra hop of lag.
- Apply is batched and parallelized across writer threads, partitioned by document `_id` so
  same-document ordering is preserved.
  Defeater: parallel apply means secondaries can be _transiently_ inconsistent mid-batch; that's why
  `readConcern: "local"` on a secondary can see a state the primary never had at any single instant,
  and why `readConcern: "majority"` reads a stable snapshot instead.

**Elections (protocol version 1)**

- Raft-_like_: terms, majority votes, one vote per member per term. Differences from Raft: the log
  is pulled by followers rather than pushed by the leader, and there is no log-matching property —
  which is precisely why MongoDB needs **rollback** (below) and Raft does not.
- Trigger: `electionTimeoutMillis` (default **10 000 ms**) without hearing from the primary.
- Requirement: a strict majority of _configured voting_ members. So a 4-member set tolerates 1
  failure (majority is 3) — the same as a 3-member set, which is why even member counts are a
  mistake.
- Priority (`members[n].priority`) biases who runs; `priority: 0` makes a member ineligible.
- Observed failover time is typically on the order of ~10–15 s with defaults (election timeout plus
  election round-trips) — _order of magnitude_, dominated by `electionTimeoutMillis`. Drivers
  buffer and retry through it if `retryWrites` is on, so application impact can be near-zero for
  writes and is a hard error for reads without retry logic.

**Rollback**

- Scenario: a primary accepts writes, becomes partitioned before a majority replicates them, a new
  primary is elected, and the old primary rejoins. Its extra writes were never majority-committed
  and must be discarded.
- Since **4.0**: implemented as `recoverToStableTimestamp` — WiredTiger rewinds storage to the last
  stable (majority-committed) timestamp. Before 4.0 it replayed rollback files and was bounded at
  **300 MB**, beyond which the member required a full resync.
- Defeater for "MongoDB never loses acknowledged writes": it never loses writes acknowledged with
  `w: "majority"`. Writes acknowledged with `w: 1` **can** be rolled back. That is the entire reason
  the default changed to `majority` in 5.0.

**Arbiters**

- Vote but hold no data. Cheap.
- Defeater and the reason to avoid them: with `{P, S, A}`, losing the secondary leaves a majority
  (P+A = 2 of 3) so the primary stays writable — but there is now **no second data-bearing member**,
  so `w: "majority"` writes cannot be satisfied and block until `wtimeout`. You've traded a clean
  failure for a silent stall. Also, with an arbiter you cannot use `readConcern: "majority"`
  meaningfully and you have no redundancy at all during the outage.

#### Design Decisions, Tradeoffs & Best Practices

**Decisions the designers made**

| Decision                          | Alternative rejected                  | Why                                                                                                                                                                     |
| --------------------------------- | ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Single primary                    | Multi-master with conflict resolution | Preserves single-document atomicity and a linearizable-ish write path without CRDTs or LWW. Cost: writes don't scale with replicas; multi-region writes pay WAN latency |
| Pull-based oplog tailing          | Leader-push (Raft)                    | Lets secondaries chain, control their own pace, and resync flexibly. Cost: no log-matching ⇒ rollback is required                                                       |
| Idempotent oplog entries          | Logical operation log                 | Safe re-application without per-follower state. Cost: `$inc` becomes `$set`, so the oplog can be larger and loses operation intent                                      |
| Capped oplog                      | Unbounded log                         | Bounded disk. Cost: a lagging secondary can fall off the window and need a full resync                                                                                  |
| Default `w: "majority"` since 5.0 | Default `w: 1`                        | Acknowledged writes are rollback-safe by default. Cost: every write pays a replication round trip                                                                       |

**Decisions you have to make**

| Decision                | Deciding variable                                                                                                                  |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Member count            | Failure tolerance = `floor((N-1)/2)`. Always odd. 3 for most; 5 when you need to survive a node loss _during_ a maintenance window |
| Oplog size              | `peak_write_bytes/sec × longest_expected_lag`. Size for your longest index build, not for 5% of disk                               |
| Geographic distribution | Whether `w: "majority"` latency (which becomes cross-region RTT) fits the write SLO                                                |
| Arbiter or not          | Almost always **not**. Use a data-bearing `priority: 0` member instead                                                             |
| `electionTimeoutMillis` | Lower = faster failover, more spurious elections on a jittery network. Don't tune below default without evidence                   |

| Option                                        | Buys you                                         | Costs you                                                  | Choose when                                |
| --------------------------------------------- | ------------------------------------------------ | ---------------------------------------------------------- | ------------------------------------------ |
| 3 members, 1 region                           | Simple, cheap, fast majority                     | Region loss = total loss                                   | Single-region SLA                          |
| 5 members, 3 regions                          | Survives a region loss with a majority elsewhere | Every majority write pays cross-region RTT                 | Regional DR is a hard requirement          |
| 3 members + `priority: 0` member in DR region | DR copy without affecting elections              | DR member can't be promoted automatically                  | DR is an RPO/RTO commitment, not an HA one |
| Arbiter                                       | Cheap majority                                   | `w:"majority"` stalls on any data-node loss; no redundancy | Never, in a system you're on call for      |

**Best practices** (rule → failure it prevents)

- **Alert on oplog _window in seconds_, not oplog size.** Prevents the case where a growing write
  rate silently shrinks the recovery window from 48 h to 40 min and the next maintenance triggers a
  full initial sync.
- **Keep `w: "majority"` and enable `retryWrites`.** Prevents rolled-back acknowledged writes, and
  prevents a routine election from surfacing as user-visible write errors.
- **Use odd member counts.** Prevents paying for a fourth node that adds zero failure tolerance.
- **Prefer a data-bearing `priority: 0` member over an arbiter.** Prevents the majority-write stall
  described above.
- **Set `maxStalenessSeconds` on any secondary read preference.** Prevents routing reads to a member
  that is hours behind, which the driver will otherwise happily do.
- **Test failover deliberately (`rs.stepDown()`) on a schedule, in an environment that mirrors
  prod.** Prevents discovering during an incident that your driver retry configuration was never
  exercised.

#### Failure Modes, Exception Handling & Production Issues

| Failure                                | Trigger                                                       | Blast radius                                                              | Detection signal                                                  | Mitigation                                                 |
| -------------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------- | ----------------------------------------------------------------- | ---------------------------------------------------------- |
| Secondary falls off oplog window       | Long index build, network partition, slow disk                | That member needs full initial sync (hours); reduced redundancy meanwhile | Member state `RECOVERING`; oplog window seconds dropping          | Size oplog for the longest operation; throttle bulk writes |
| Rollback of `w:1` writes               | Primary partitioned before majority replication               | Acknowledged writes silently disappear                                    | Rollback log entries on the old primary                           | `w: "majority"` (default since 5.0)                        |
| Majority-write stall                   | Lost enough data-bearing members that majority is unreachable | All writes block until `wtimeout`, then fail                              | Write latency → `wtimeout`; `replSetGetStatus` shows members down | Odd counts; no arbiters; monitor member health             |
| Election storm                         | Flapping network, aggressive `electionTimeoutMillis`          | Repeated brief write unavailability                                       | Term number incrementing rapidly                                  | Fix the network; don't lower the timeout                   |
| Stale secondary reads                  | `secondaryPreferred` without `maxStalenessSeconds`            | Users read old data with no error                                         | Replication lag metric; user reports of "my update vanished"      | `maxStalenessSeconds`; causal sessions; or read primary    |
| Replication lag from index maintenance | Too many indexes / bulk write burst                           | Lag → stale reads → majority-write latency                                | `replSetGetStatus` optime difference                              | Reduce indexes; throttle batch jobs                        |

**Exception handling.** `NotWritablePrimary` (code 10107) and `PrimarySteppedDown` (189) are
**retryable** — modern drivers with `retryWrites=true` retry once against the new primary
automatically, using the session's transaction number so the retry is idempotent even if the first
attempt actually succeeded. `WriteConcernFailed` / `wtimeout` is the dangerous one: it means the
write **may have been applied locally** but did not reach a majority — it is not a rollback and not
a success, and the only correct application response is to re-check state, not to blindly retry a
non-idempotent operation. Poison-pill risk: any write path that retries on `wtimeout` without
idempotency keys will double-apply during a partition.

**Real production issues**

- **Public, cited:** MongoDB 4.0 release notes and the "Rollbacks During Replica Set Failover"
  documentation describe the pre-4.0 rollback limit (300 MB of rollback data, beyond which the
  member required a resync) and the move to `recoverToStableTimestamp`. This is a real,
  documented, historical failure mode — a large partition could turn a rejoining member into a
  multi-hour resync.
- **Public, cited:** the MongoDB 5.0 release notes changed the default write concern to
  `w: "majority"`, explicitly to make acknowledged writes durable against rollback by default. That
  a vendor changed a default with a measurable latency cost is the strongest available evidence that
  the `w: 1` default was producing real data loss in the field.
- `Canonical failure pattern (not a specific incident)` — **The index build that cost a resync.**
  Symptom: a 6-hour index build on a 3 TB collection completes; one secondary is now `RECOVERING`
  and initial sync takes 9 hours, during which the set has no failure tolerance. Root cause: oplog
  window was 4 hours at current write rate, because it was sized at 5% of disk years ago when write
  volume was a tenth of today's. Fix: resize the oplog (`replSetResizeOplog`, online since 3.6) to
  cover 3× the longest expected operation. Guardrail: alert on oplog window _seconds_ with a
  threshold derived from the longest maintenance operation in the runbook — the alert must be in
  time units, because size in GB is meaningless without the write rate.

#### Interview Questions

**Q:** Walk me through a MongoDB failover.

**L4 answer** — Members heartbeat every 2 s. If a secondary hasn't heard from the primary for
`electionTimeoutMillis` (default 10 s), it increments the term and requests votes. It needs a strict
majority of configured voting members. On winning it becomes primary; the old primary steps down when
it sees the higher term. Drivers detect the topology change via their own monitoring and, with
`retryWrites=true`, retry the in-flight write against the new primary. Total impact is typically on
the order of 10–15 s of write unavailability.

**L5 answer** — Plus the two things that determine whether this is a non-event or an incident.

First, **what happens to writes the old primary accepted but never replicated to a majority**.
They're rolled back — the old primary rewinds storage to the last stable timestamp when it rejoins.
If they were acknowledged with `w: 1`, the client was told "success" and the write is gone. That's
why `w: "majority"` is the default since 5.0 and why I'd never override it downward on a system of
record. Note the asymmetry: the client can't distinguish "rolled back" from "never happened," so the
application has to be built on idempotency keys if correctness matters.

Second, **`wtimeout` semantics**. A majority write that times out is genuinely ambiguous — it may
have been applied locally and may still replicate afterwards. It's neither success nor rollback.
Retrying a non-idempotent write on `wtimeout` is a double-apply bug, and I've seen that shipped more
than once.

The design point underneath: MongoDB's election is Raft-like but secondaries _pull_ the oplog rather
than the leader pushing it, and there's no log-matching property. That's why rollback exists at all
— in real Raft, a follower's log is forced to match the leader's, so divergence is repaired by
truncation as part of the protocol. MongoDB gets flexible chaining and independent secondary pacing,
and pays for it with a rollback mechanism and the `w: 1` durability gap.

---

**Q:** Should you use an arbiter?

**L4 answer** — Almost never. An arbiter votes but holds no data, so it makes a 2-node set into a
3-vote set cheaply. The problem: in a `{P, S, A}` set, losing the secondary leaves a voting majority
so the primary stays writable, but there is no second data-bearing member — `w: "majority"` writes
can't be satisfied and block until `wtimeout`. You've also lost all redundancy. Use a data-bearing
`priority: 0` member instead.

**L5 answer** — Plus: the arbiter is a cost optimization that inverts your failure model. Without it,
losing a node in a 3-node set is degraded-but-correct; with it, losing the one secondary means you
are simultaneously (a) unable to satisfy the default write concern, (b) unreplicated, and (c) still
accepting writes — the worst possible combination, because the system looks up while silently having
zero durability margin. `readConcern: "majority"` also becomes meaningless.

The only case I'd entertain is a genuinely cost-constrained non-critical workload where you've
explicitly downgraded to `w: 1` and accepted the rollback risk in writing. Even then, in a cloud
environment the price delta between an arbiter instance and a small data-bearing secondary is small
enough that it's not worth the operational asymmetry. This is a good example of a cheap decision
whose cost is paid entirely during an incident, which is when you have the least capacity to reason
about it.

---

**Q:** How do you size the oplog?

**L4 answer** — Not by the 5%-of-disk default. Size it as `peak write bytes/sec × the recovery
window you need`. The window must cover your longest expected lag event — an index build, a backup,
a network partition — because a secondary that falls further behind than the oplog window requires
a full initial sync. Monitor the oplog _window in seconds_ (`rs.printReplicationInfo()`), not size
in GB. Resize online with `replSetResizeOplog`.

**L5 answer** — Plus: the sizing input people miss is that the oplog holds _idempotent rewritten_
entries, not the original operations. `{$inc: {counter: 1}}` becomes `{$set: {counter: 8471}}`, and
a `$push` onto a large array logs the resulting array — so a workload of tiny updates to large
documents produces an oplog vastly bigger than the write payload. I'd measure oplog bytes/sec
empirically rather than derive it from application write volume, because the ratio can be 10× and is
completely invisible from the app side.

The second-order effect: oplog size and initial-sync time interact badly. A larger oplog buys a
longer window, but initial sync itself must complete _within_ the window it started with, plus the
oplog accumulated during the sync — so on a very large node, an undersized oplog makes initial sync
fail repeatedly, which is a spiral. The escape is a dedicated sync source, file-copy-based initial
sync (Enterprise/Atlas), or restoring from a snapshot and letting the member catch up from the
oplog. On multi-TB nodes I'd plan for snapshot-restore as the primary recovery path and treat
logical initial sync as the fallback, because time-to-restore-redundancy is the number that matters
during an incident.

#### L5-Only Questions

**Q:** You need a MongoDB deployment surviving the loss of an AWS region with an RPO of zero.
Design it and state what it costs.

**L5 answer** — RPO zero means no acknowledged write may be lost, which means the acknowledgement
must be conditioned on the write having crossed the region boundary. That is a `w: "majority"` write
in a topology where no majority exists within a single region.

Topology: 5 voting data-bearing members across **3** regions — 2 / 2 / 1. Check the failure math: any
single region loss leaves at least 3 of 5 members, which is a majority, so an election succeeds and
majority writes remain satisfiable. A 2/2/1 layout is required rather than 3/2 — with 3/2, losing the
3-member region leaves 2 of 5 and the cluster is read-only until manual intervention, which fails
the requirement.

What it costs, stated plainly:

- **Every write pays a cross-region RTT.** Majority = 3 of 5, and with 2 members local to the primary
  the third acknowledgement must come from another region. So write latency floors at roughly the
  inter-region RTT — order of magnitude tens of milliseconds within a continent, higher
  transcontinental. If the write SLO is 20 ms, this design is infeasible and the requirement has to
  change, not the topology. That is the conversation to have on day one.
- **Reads** are fine — local secondary reads with `maxStalenessSeconds`, or primary reads if you need
  freshness and accept the routing.
- **Cost**: 5 data-bearing nodes plus cross-region data transfer on all replication traffic, which is
  usually the surprising line item.

What I'd challenge before building it: RPO zero is frequently stated and rarely meant. If the true
requirement is "no lost _customer-visible_ transactions," an alternative is single-region MongoDB
with `w: "majority"` plus an idempotent, durably-queued write path — the client's request is durable
in a cross-region queue before MongoDB is touched — which gets RPO zero at the _business_ boundary
with single-region write latency. That's usually the better system, and it's a design conversation,
not a database configuration.

I would not use `w: 5` (all members). It converts any single member's slowness into total write
unavailability, and it buys nothing over `majority` for the stated requirement.

---

**Q:** A secondary is at 45 minutes of lag and climbing during peak hours; oplog window is 6 hours.
What do you do, in order?

**L5 answer** — First, decide whether this is an emergency. It is not yet — 45 min against a 6 h
window means hours of headroom — but the _derivative_ is what matters, so I'd compute
time-to-window-exhaustion at the current rate before anything else. That number decides whether I
mitigate or investigate.

Then diagnose the mechanism, because the fixes are mutually exclusive:

1. **Apply-bound (CPU/disk on the secondary).** Common cause: the secondary is a smaller instance
   type than the primary, which people do to save money and which guarantees lag under peak write
   load. Fix: match instance types. Most common cause, least interesting.
2. **Index maintenance.** A high index count means the secondary does the same N B+ tree writes per
   oplog entry. If lag correlates with a recently added index, that's it.
3. **A long-running operation blocking apply.** A `readConcern: "majority"` snapshot held open by a
   long analytics query on the secondary can pin the oldest timestamp and stall the applier. Check
   `currentOp` on the secondary for long-running reads. This one surprises people because the cause
   is a _read_.
4. **Chaining.** If the secondary syncs from another lagging secondary, lag compounds. Check
   `syncSourceHost` in `replSetGetStatus`.

Immediate mitigations in order of reversibility: throttle or pause any batch write job (cheapest,
instantly reversible); kill long-running secondary reads; disable chaining or force the sync source
to the primary. If the window is genuinely at risk, resize the oplog with `replSetResizeOplog` —
online, and it buys time without touching the write path.

What I would _not_ do is remove the secondary from the set to "let it catch up" — it catches up the
same either way, and you've now removed a voting member during an incident. And I'd make sure the lag
alert threshold is expressed as a fraction of the oplog window rather than an absolute minute count,
because 45 minutes is fine at a 6-hour window and an emergency at a 1-hour one.

---

### 3.2 Write Concern, Read Concern, Read Preference

#### Concept

- **What it is** — Three orthogonal knobs. **Write concern** (`w`, `j`, `wtimeout`) defines when a
  write is acknowledged. **Read concern** (`local`, `available`, `majority`, `linearizable`,
  `snapshot`) defines what a read is allowed to see. **Read preference** (`primary`,
  `primaryPreferred`, `secondary`, `secondaryPreferred`, `nearest`) defines which member serves it.

- **What it solves** — Lets a single deployment serve both "this must never be lost" and "this is a
  dashboard, stale is fine" without running two databases. The tunability is per-operation.

- **What it replaced** — A single fixed consistency level. Insufficient because the durability
  requirement of an audit write and a click-tracking write differ by orders of magnitude, and paying
  the audit price for both is expensive.

- **What it works with / ecosystem** — combines with causal-consistent **sessions**
  (`afterClusterTime`), with transactions (§5.1, which set concerns at the transaction level), and
  with sharding (where `linearizable` is not supported).

  Conflicts with: intuition. These three are _not_ a consistency level in the CAP/ANSI sense, and
  combining them incorrectly produces guarantees weaker than either implies alone.

- **Place in the world** — every driver call. **Wrong answer to**: implementing application-level
  correctness. `w: "majority"` gives you durability, not serializability; you still need optimistic
  concurrency (a version field) to prevent lost updates.

#### Architecture & Core Components

```
  WRITE CONCERN                READ CONCERN                READ PREFERENCE
  "when is it acked?"          "what may I see?"           "who serves me?"
  ─────────────────            ─────────────────           ────────────────
  w:0   fire & forget          local     — whatever this    primary
  w:1   primary memory                     node has         primaryPreferred
  w:"majority" ← default 5.0   available — sharded, may     secondary
  j:true  primary journal                  include orphans  secondaryPreferred
  wtimeout: ms                 majority  — majority-        nearest
                                           committed only     (+ maxStalenessSeconds,
                               linearizable — real-time         + tag sets)
                                           order, primary,
                                           single doc only
                               snapshot  — txn snapshot

  Orthogonal. w:"majority" + readConcern:"local" on a secondary
  is a completely normal and completely stale combination.
```

| Component             | Single responsibility                                              |
| --------------------- | ------------------------------------------------------------------ |
| `w`                   | How many members must acknowledge before the client is told "done" |
| `j`                   | Whether the primary's journal must be fsynced first                |
| `wtimeout`            | Bound the wait — and introduce ambiguity                           |
| Read concern          | Visibility rule applied at read time                               |
| Read preference       | Member selection                                                   |
| `maxStalenessSeconds` | Reject members lagging beyond a bound                              |
| Causal session        | Enforce read-your-writes across members via `afterClusterTime`     |

#### How Each Component Works

**`w: "majority"`**

- The primary waits until a majority of _data-bearing voting_ members have applied the write to
  their oplog and made it durable per their own `j` settings.
- This is what makes the write **rollback-safe**: rollback rewinds to the last majority-committed
  point, so a majority-acknowledged write is by definition not rolled back.
- Defeater: majority acknowledgement is not synchronous replication to _all_ members. A secondary
  outside the majority can be arbitrarily behind, and a read routed there sees pre-write state.

**`j: true`**

- Waits for the primary's journal fsync (which otherwise happens on a ~100 ms interval).
- Defeater: with `w: "majority"` on 3+ data-bearing nodes, `j: true` is mostly redundant — you're
  protecting against simultaneous majority crash. It roughly doubles write latency for a scenario
  in which you have bigger problems. Default: `w: "majority"`, `j` unset.

**`wtimeout`**

- Bounds the wait. On expiry the client gets `WriteConcernError` — and the write **may still be
  applied and may still replicate**.
- This is the single most misunderstood semantic in MongoDB. `wtimeout` is not a rollback and not a
  cancel. Any retry must be idempotent.

**`readConcern: "majority"`**

- Returns only data that is majority-committed, so the read never sees a value that could later be
  rolled back.
- Cost: the node must maintain a majority-committed snapshot, which pins WiredTiger's oldest
  timestamp and holds versions in cache.
- Defeater: `majority` does **not** mean "latest." A `majority` read on a secondary returns the
  majority-committed state _as that secondary knows it_, which lags.

**`readConcern: "linearizable"`**

- Real-time ordering: the read reflects all writes that completed before it began.
- Constraints: primary only, **single-document** reads only, and the server performs a no-op write
  and waits for majority to confirm it is still primary — so it costs a majority round trip _on a
  read_. Not supported on sharded collections. Should be paired with `maxTimeMS` because it can
  block indefinitely.
- Use it approximately never. If you need this, you usually need a transaction or a different data
  model.

**Causal consistency (sessions)**

- A client session tracks the cluster time of its last operation and sends `afterClusterTime` on
  subsequent reads; the target member waits until it has replicated to that point.
- This is how you get read-your-writes on secondaries. Cost: the read _blocks_ until the secondary
  catches up, so you've converted a stale read into a slow one.
- Defeater: causal consistency is per-session. Two different services acting on behalf of the same
  user do not share a session unless you propagate the cluster time explicitly, which almost nobody
  does — so "read-your-writes" breaks across service boundaries.

**Read preference and `maxStalenessSeconds`**

- `secondaryPreferred` falls back to the primary if no secondary is eligible — which means a
  secondary-read config silently becomes a primary-read config under failure, doubling primary load
  exactly when it's least able to take it.
- `maxStalenessSeconds` (minimum 90) excludes members lagging beyond the bound. Without it, the
  driver will route to an arbitrarily stale member.
- Tag sets (`{nodeType: "analytics"}`) are the correct mechanism for isolating analytical reads —
  better than a global read preference because it's explicit per client.

#### Design Decisions, Tradeoffs & Best Practices

**Decisions the designers made**

| Decision                                              | Alternative rejected       | Why                                                                                                                                                             |
| ----------------------------------------------------- | -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Three orthogonal knobs, per-operation                 | One global isolation level | Different operations in one app have genuinely different needs. Cost: enormous room for incorrect combinations, and no single place to reason about consistency |
| Default `w: "majority"` (5.0+)                        | Default `w: 1`             | Correct-by-default durability. Cost: baseline write latency includes a replication round trip                                                                   |
| Causal consistency via explicit sessions              | Global causal consistency  | Cheap when unused. Cost: it's opt-in, so most applications don't have it and don't know                                                                         |
| `linearizable` restricted to single-doc primary reads | General linearizability    | Anything broader needs distributed coordination on every read. Cost: the option exists and looks more useful than it is                                         |

**Decisions you have to make**

| Decision                           | Deciding variable                                                                                                   |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `w` per write path                 | Is losing this write on a failover a business incident? Audit/financial ⇒ majority. Telemetry ⇒ `w:1` is defensible |
| Read from secondaries              | Can the consumer tolerate replication lag, unbounded during bursts?                                                 |
| `readConcern: "majority"` on reads | Would seeing a rolled-back value cause incorrect behaviour downstream (e.g. emitting an event)?                     |
| Session causal consistency         | Does the same user immediately re-read what they wrote, through the same service?                                   |

| Option                           | Buys you                  | Costs you                                                     | Choose when                                                       |
| -------------------------------- | ------------------------- | ------------------------------------------------------------- | ----------------------------------------------------------------- |
| `w:1`                            | Lowest latency            | Rollback on failover; acknowledged data can vanish            | Metrics, logs, caches — never a system of record                  |
| `w:"majority"`                   | Rollback-safe             | One replication RTT per write                                 | Default. Everything transactional                                 |
| `w:"majority", j:true`           | Survives majority crash   | ~2× write latency                                             | Regulatory requirement you can point to                           |
| `readConcern:"local"` on primary | Fastest correct-ish read  | May read a value that later rolls back                        | Most reads                                                        |
| `readConcern:"majority"`         | Never read a doomed write | Snapshot maintenance cost; still lags on secondaries          | Reads that trigger side effects (publish an event, charge a card) |
| `linearizable`                   | Real-time ordering        | Majority RTT on a read; primary-only; single doc; no sharding | Almost never                                                      |

**Best practices** (rule → failure it prevents)

- **Never use `w: 0`.** Prevents silent write loss with no error path at all — you cannot even
  detect it.
- **Set `readConcern: "majority"` on any read whose result causes an external side effect.**
  Prevents publishing an event or issuing a payment for a write that subsequently rolls back — an
  unrecoverable inconsistency between systems.
- **Always pair secondary reads with `maxStalenessSeconds`.** Prevents routing to a member hours
  behind with no error.
- **Never retry a `wtimeout` failure without an idempotency key.** Prevents double-apply.
- **Use tag sets for analytics reads, not a global `secondaryPreferred`.** Prevents a failover from
  silently moving analytical load onto the primary.
- **Treat `w` and `readConcern` as a _pair_ documented per data flow.** Prevents the extremely common
  "we use majority writes so we're consistent" claim while every read is `local` on a lagging
  secondary.

#### Failure Modes, Exception Handling & Production Issues

| Failure                                     | Trigger                                          | Blast radius                                  | Detection signal                                         | Mitigation                                    |
| ------------------------------------------- | ------------------------------------------------ | --------------------------------------------- | -------------------------------------------------------- | --------------------------------------------- |
| Silent write loss                           | `w: 0` or `w: 1` + failover                      | Data gone, no error ever raised               | Only detectable by reconciliation against another system | `w: "majority"`                               |
| `wtimeout` double-apply                     | Retry on `WriteConcernError` without idempotency | Duplicate records / double charges            | Duplicate detection downstream                           | Idempotency keys; upsert on a natural key     |
| Stale read after write                      | Secondary read, no causal session                | User sees their update vanish, then reappear  | Support tickets; hard to reproduce                       | Causal session, or read primary for that flow |
| Secondary reads collapse to primary         | `secondaryPreferred` during a secondary outage   | Primary load doubles at the worst moment      | Primary op counts jump on member loss                    | Explicit tag-set routing; capacity headroom   |
| Majority-write stall                        | Lost majority of data-bearing members            | Writes block to `wtimeout` then fail          | `replSetGetStatus`; write latency cliff                  | Odd member counts; no arbiters                |
| Cache pressure from `majority` read concern | Long-held majority snapshots                     | Cache full of old versions; eviction pressure | Oldest-timestamp lag                                     | Bound query duration with `maxTimeMS`         |

**Exception handling.** MongoDB distinguishes `writeError` (the write itself failed — usually
terminal, e.g. `DuplicateKey`) from `writeConcernError` (the write applied locally but the concern
wasn't met — ambiguous). Drivers surface these differently and application code routinely conflates
them; that conflation is the bug. `NotWritablePrimary` is retryable and handled by `retryWrites`.
`ReadConcernMajorityNotAvailableYet` occurs on a freshly-started node before it has a
majority-committed snapshot and is retryable. Poison-pill risk: a durable outbox pattern that writes
to MongoDB and publishes on success will publish for writes that later roll back, unless the read
that drives publication uses `readConcern: "majority"` — this is the most common correctness bug in
MongoDB-plus-message-broker architectures.

**Real production issues**

- **Public, cited:** the MongoDB 5.0 release notes changed the default write concern from `w: 1` to
  `w: "majority"` specifically so acknowledged writes are durable against rollback. That the vendor
  changed a default with a latency cost is the strongest available evidence that the old default was
  producing real-world data loss.
- `Canonical failure pattern (not a specific incident)` — **The outbox that published a rolled-back
  write.** Symptom: downstream consumers hold records for entities that don't exist in MongoDB;
  reconciliation breaks; the "missing" records were never in the database. Root cause: service wrote
  with `w: 1`, read back with `readConcern: "local"`, published to the broker; a failover rolled the
  write back. Fix: `w: "majority"` on the write and `readConcern: "majority"` on the outbox poller.
  Guardrail: assert in code review that any read feeding an external publish uses majority read
  concern — and better, use change streams, which are majority-committed by construction and
  therefore immune to this class.

#### Interview Questions

**Q:** What's the difference between write concern and read concern?

**L4 answer** — Write concern controls _when the client is told a write succeeded_ — `w: 1` means
the primary applied it in memory, `w: "majority"` means a majority of data-bearing members have it,
which makes it rollback-safe. Read concern controls _what a read may see_ — `local` returns whatever
the queried node has (which might later roll back), `majority` returns only majority-committed data.
They're orthogonal: you can write with majority and read stale data from a secondary with `local`.

**L5 answer** — Plus: the orthogonality is the whole point and the whole trap. "We use
`w: majority` so we're consistent" is the most common wrong claim about a MongoDB deployment,
because durability of writes says nothing about visibility of reads.

The case where the distinction becomes a correctness bug rather than a performance nuance is any
read that triggers a side effect outside MongoDB. If an outbox poller reads with `local` and
publishes to a broker, a subsequent rollback leaves the broker holding a record for a write that
never committed — and there is no compensating action, because the database has no record it ever
happened. So my rule is: reads that cause external effects use `readConcern: "majority"`, or better,
use change streams, which are majority-committed by construction and remove the decision from the
developer.

The cost of `readConcern: "majority"` that people don't anticipate is storage-engine pressure — the
node must hold a majority-committed snapshot, pinning WiredTiger's oldest timestamp, so a
long-running majority read retains old versions in cache. That's why `maxTimeMS` isn't optional on
those paths.

---

**Q:** A write returns a `wtimeout` error. Did it happen?

**L4 answer** — Unknown. `wtimeout` means the write concern wasn't satisfied within the time limit;
the write was likely applied on the primary and may replicate afterwards. It is neither a success
nor a rollback. Blindly retrying a non-idempotent write will double-apply.

**L5 answer** — Plus how to build so this doesn't matter. The ambiguity is inherent — it's the
standard distributed-systems "the acknowledgement was lost" problem, and no write concern setting
removes it. So the design answer is to make every write idempotent rather than to make the
acknowledgement reliable:

- Use `updateOne` with an upsert on a client-generated idempotency key rather than `insertOne`, so a
  retry converges instead of duplicating.
- Or rely on `retryWrites=true`, which does this correctly at the driver level for a _single_
  automatic retry: the driver attaches a transaction number to the session, and the server records
  the outcome in `config.transactions`, so a retry of an already-applied write returns the original
  result rather than re-applying. That mechanism only covers driver-initiated retries of specific
  error classes, so application-level retry loops still need their own key.

Second-order point: `wtimeout` on a majority write is often a _symptom_, not a transient. It usually
means you've lost enough data-bearing members that majority is unreachable, or replication lag has
exceeded the timeout. Retrying harder makes it worse. The right response to a rising `wtimeout` rate
is to shed load and check `replSetGetStatus`, not to increase the timeout — increasing the timeout
converts a fast failure into a queue-depth incident.

---

**Q:** When would you read from a secondary?

**L4 answer** — When the consumer tolerates replication lag: analytics, reporting, exports, search
index backfill. Never for read-your-writes flows or anything driving a decision that must reflect
current state. If you do it, set `maxStalenessSeconds` so the driver won't route to an arbitrarily
lagging member, and prefer tag-set routing over a global `secondaryPreferred`.

**L5 answer** — Plus the two failure modes that make secondary reads a worse scaling lever than
people expect.

First, **`secondaryPreferred` fails open toward the primary.** Lose your secondaries and the
analytical load lands on the primary — at exactly the moment the primary is already degraded. So the
read preference that looks like isolation is actually a load amplifier under failure. Tag sets with
`secondary` (not `secondaryPreferred`) fail _closed_, which is what you want for analytics: the
report errors, the OLTP path survives.

Second, **secondaries don't have spare capacity by default.** They apply every write the primary
does, including every index maintenance operation, so a secondary's write-side load is already equal
to the primary's. Adding read load increases replication lag, which degrades the very staleness bound
you set. That feedback loop is why secondary reads scale reads sublinearly.

If someone proposes secondary reads to solve a load problem, I'd first check whether the problem is
cache-bound (§1.2) — in which case a replica has the same problem — and I'd push toward a dedicated
analytics node with `priority: 0`, `votes: 0`, and its own tag, sized differently, so the analytical
workload has genuinely separate resources and can't win an election.

#### L5-Only Questions

**Q:** Specify the write concern, read concern, and read preference for each of: a payment ledger
entry, a user profile update, an IoT telemetry point, and a nightly BI extract. Justify each.

**L5 answer**

| Flow                | `w`        | `readConcern`                                                              | `readPreference`                                 | Reasoning                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| ------------------- | ---------- | -------------------------------------------------------------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Payment ledger      | `majority` | `majority` on any read feeding a side effect; `local` on primary otherwise | `primary`                                        | Rollback of a ledger entry is unrecoverable — the money moved and the record didn't. Majority read concern on the outbox path is non-negotiable because publishing a payment event for a rolled-back write creates cross-system divergence with no compensating action. I would _not_ add `j: true`: on 3+ data-bearing members majority already covers single-node crash, and doubling write latency on the payment path to cover simultaneous majority failure is the wrong trade. |
| User profile update | `majority` | `local`, but on a **causally consistent session**                          | `primary`                                        | The correctness requirement here isn't durability, it's read-your-writes — the user updates their name and immediately reloads. Causal session gets that on secondaries; simplest is to read primary for this flow, since profile reads are low-volume. I'd resist routing profile reads to secondaries; the traffic doesn't justify the consistency complexity.                                                                                                                     |
| IoT telemetry       | `w: 1`     | `local`                                                                    | `secondaryPreferred` + `maxStalenessSeconds`     | Losing a handful of points on a failover is not a business event, and the volume makes majority latency the dominant cost. This is the one place `w: 1` is genuinely correct, and it should be a documented decision, not a default that leaked in.                                                                                                                                                                                                                                  |
| Nightly BI extract  | n/a        | `local`                                                                    | `secondary` with a `{nodeType: "analytics"}` tag | `secondary` not `secondaryPreferred`, deliberately — I want this to fail closed if the analytics node is gone rather than land on the primary. Plus `maxTimeMS` and `allowDiskUse`, because the real risk is this query evicting the OLTP working set.                                                                                                                                                                                                                               |

The meta-point: these should live as named constants in one configuration class, not scattered at
call sites, because the failure mode is drift — someone copies the telemetry `w: 1` into a ledger
path during a refactor and nobody notices until a failover.

---

**Q:** Your architecture writes to MongoDB and publishes to a message broker. Design it so a
rollback can't produce a phantom event.

**L5 answer** — The naive version — write, then publish — is broken in two independent ways: a crash
between the two loses the event, and a rollback after the publish creates a phantom. Neither is
fixed by write concern alone.

Options:

1. **Transactional outbox + `readConcern: "majority"` poller.** Write the domain document and an
   outbox document in one multi-document transaction (§5.1), so they commit atomically. A poller
   reads the outbox with `readConcern: "majority"` and publishes, then marks published. The majority
   read concern is the part that prevents phantoms — it guarantees the poller never sees a write that
   can still be rolled back. Delivery is at-least-once, so consumers must be idempotent.
   Cost: a transaction on the write path, plus poller latency.

2. **Change streams.** A change stream is built on the oplog and only emits **majority-committed**
   events by construction, with a resume token for at-least-once delivery across restarts. This
   removes the phantom problem structurally rather than by developer discipline, and removes the
   outbox collection entirely.
   Cost: the resume token must be persisted durably by the consumer, and if the consumer is down
   longer than the oplog window, the resume point is gone and you need a reconciliation path. That
   oplog-window dependency is the real operational risk and it's the same number from §3.1.

I'd choose **change streams**, because the property I care about — never emit an uncommitted write —
is provided by the mechanism rather than by remembering to set a read concern, and mechanisms survive
team turnover in a way that conventions don't. I'd keep the outbox pattern in reserve for the case
where the event payload must be a business-defined shape decoupled from the document schema, since
change streams give you the document delta, not your event contract.

Either way, consumers must be idempotent — at-least-once is the ceiling here, and anyone promising
exactly-once across a database and a broker without an idempotency key is describing something that
doesn't exist.

---

## 4. Sharding

### 4.1 Shard Keys, Routing, and the Balancer

#### Concept

- **What it is** — Horizontal partitioning of a collection across multiple replica sets (shards) by
  a **shard key**, with `mongos` routers directing operations and **config servers** (a replica set,
  CSRS since 3.4) holding the authoritative chunk-to-shard map.

- **What it solves** — Working set larger than one machine's RAM, or write throughput exceeding one
  primary. Those are the _only_ two problems sharding solves.

- **What it replaced** — Application-level sharding (hash the tenant ID in your service, pick a
  connection string). Insufficient because rebalancing required an offline migration you wrote
  yourself, and cross-shard queries had no query engine.

- **What it works with / ecosystem** — composes replica sets (§3). `mongos` is stateless and
  horizontally scalable. Conflicts with: transactions (cross-shard transactions use two-phase
  commit and cost far more), unique indexes (must be shard-key-prefixed), and `linearizable` read
  concern (unsupported).

- **Place in the world** — clusters past roughly a few TB of working set or past a single primary's
  write ceiling. **Wrong answer to**: a performance problem caused by a missing index, a bad schema,
  or an undersized instance — which is what it's most often deployed for. Sharding a badly-modeled
  collection makes it worse and adds an irreversible operational burden.

#### Architecture & Core Components

```
                    ┌──────────────────┐
   app ──────────▶  │      mongos      │  stateless router (run many)
                    │  caches chunk map│
                    └────┬────────┬────┘
                         │        │ chunk map reads
                         │        ▼
                         │   ┌──────────────────────┐
                         │   │ CONFIG SERVERS (CSRS)│ replica set
                         │   │ config.chunks        │ authoritative ranges
                         │   │ config.shards        │
                         │   └──────────────────────┘
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   ┌─────────┐      ┌─────────┐      ┌─────────┐
   │ SHARD A │      │ SHARD B │      │ SHARD C │   each = a full replica set
   │ chunks  │      │ chunks  │      │ chunks  │
   │ [min,x) │      │ [x, y)  │      │ [y,max) │
   └─────────┘      └─────────┘      └─────────┘
        ▲                                  ▲
        └────────── BALANCER ──────────────┘
             (runs on config-server primary;
              moves chunks to even out data size)

  Targeted query   : predicate includes the shard key → 1 shard
  Scatter-gather   : predicate omits it → all shards, merged at mongos
```

| Component             | Single responsibility                                                 |
| --------------------- | --------------------------------------------------------------------- |
| `mongos`              | Route, merge, and be stateless                                        |
| Config servers (CSRS) | Authoritative chunk range → shard mapping                             |
| Shard                 | Own a set of chunk ranges; is itself a replica set                    |
| Chunk                 | A contiguous shard-key range; the unit of migration                   |
| Balancer              | Even out data distribution by migrating chunks                        |
| Shard key             | Determines routing, distribution, and everything that will hurt later |

#### How Each Component Works

**Shard key**

- Must be indexed. Can be **ranged** (index on the field(s)) or **hashed** (index on
  `hash(field)`).
- Governs three independent properties, and a good key needs all three:
  1. **Cardinality** — the number of distinct values bounds the number of chunks. A boolean shard
     key gives you 2 chunks forever, regardless of data volume.
  2. **Frequency (distribution)** — even if cardinality is high, if 40% of documents share one
     value, that value's chunk cannot be split (a **jumbo chunk**) and one shard carries 40% of the
     data permanently.
  3. **Monotonicity** — a monotonically increasing key (timestamp, `ObjectId`) sends all inserts to
     the chunk owning `MaxKey`, i.e. one shard, forever. Adding shards does not help.
- Since **4.4** you can _refine_ a shard key by appending suffix fields
  (`refineCollectionShardKey`). Since **5.0** you can **reshard** a collection entirely
  (`reshardCollection`), with 8.0 improving its performance — but resharding rewrites the
  collection and is a major operation, not a routine one.
- Defeater for "just pick something high-cardinality": high cardinality with monotonicity is the
  worst case, because it looks fine in a design review and hot-spots in production.

**Hashed vs ranged**

|                          | Hashed                                           | Ranged                      |
| ------------------------ | ------------------------------------------------ | --------------------------- |
| Insert distribution      | Even, by construction                            | Depends entirely on the key |
| Range queries on the key | **Impossible to target** — always scatter-gather | Targeted                    |
| Sort on the key          | No help                                          | Index order usable          |
| Monotonic key            | Fixed                                            | Broken                      |

Defeater for hashed: hashing destroys locality, so a query for "all events for tenant X in the last
hour" becomes scatter-gather even though tenant X is a single value — unless the hashed field is the
tenant itself. Compound shard keys like `{tenantId: 1, ts: 1}` (ranged) give you tenant-targeted
queries _and_ time locality within a tenant; the risk is tenant skew.

**Chunks and the balancer**

- Default chunk size: **128 MB** since MongoDB **6.0** (previously 64 MB).
- Since **6.0**, automatic chunk _splitting_ was removed in favour of data-size-aware balancing; the
  balancer moves data based on measured size per shard rather than chunk counts. **7.0** added
  automatic chunk merging. Version-anchor this carefully in an interview — the mechanism genuinely
  changed, and stating pre-6.0 behaviour as current is a tell.
- Migration protocol: the balancer instructs a donor shard to copy a chunk to a recipient, catches
  up on changes, then updates `config.chunks` and the routers' epoch. Documents left behind on the
  donor after a failed migration are **orphans**; `readConcern: "available"` can return them, which
  is why it is not the default.
- A **jumbo chunk** is a chunk that cannot be split because every document in it shares one shard
  key value. It cannot be migrated by the normal path and permanently unbalances the cluster.

**Routing**

- `mongos` caches the chunk map and stamps requests with a version. If a shard sees a stale version,
  it returns `StaleConfig` and the router refreshes and retries — transparently to the client.
- **Targeted** operation: the query predicate contains the shard key (or a prefix of a compound
  shard key). One shard.
- **Scatter-gather**: it doesn't. Every shard is queried, results merged at `mongos`. Cost scales
  with shard count, and latency is bounded by the _slowest_ shard, so scatter-gather latency
  degrades as you add shards — sharding makes these queries worse, not better.
- Sorted scatter-gather requires a merge at `mongos`; if the sort isn't index-supported per shard it
  becomes a blocking sort per shard plus a merge.

**Config servers**

- A replica set holding `config.chunks`, `config.shards`, `config.collections`.
- If the config server replica set loses its majority, the cluster becomes **read-only for
  metadata**: existing routing continues from cached maps, but no chunk migrations, no splits, no
  new `mongos` startup. It is not an immediate outage, which is exactly why config-server health is
  under-monitored.

#### Design Decisions, Tradeoffs & Best Practices

**Decisions the designers made**

| Decision                                            | Alternative rejected                        | Why                                                                                                                                                                                    |
| --------------------------------------------------- | ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Range-based chunks with a balancer                  | Consistent hashing (Dynamo/Cassandra style) | Preserves range-query targeting and lets the balancer respond to actual data size. Cost: needs a balancer and a metadata service; hot ranges are possible                              |
| Shard key immutable (pre-5.0)                       | Freely mutable                              | Routing correctness depends on a document's key not moving. Cost: a wrong key was a permanent mistake for years — hence `refineCollectionShardKey` (4.4) and `reshardCollection` (5.0) |
| Stateless `mongos` with cached map + version stamps | Routers as consensus participants           | Routers scale horizontally and can be co-located with app servers. Cost: `StaleConfig` retry churn during migrations                                                                   |
| Config servers as a replica set (CSRS, 3.4+)        | Three mirrored standalone config servers    | Uses the same replication and election machinery; majority-committed metadata. Cost: none meaningful — the old design was strictly worse                                               |

**Decisions you have to make**

| Decision           | Deciding variable                                                                                               |
| ------------------ | --------------------------------------------------------------------------------------------------------------- |
| Shard or not       | Is the working set > one machine's RAM, or write rate > one primary? If not, **do not shard**                   |
| Shard key          | The dominant query predicate. If your top query doesn't contain the key, you've chosen wrong                    |
| Hashed vs ranged   | Do you need range/prefix targeting on that field? Ranged if yes, hashed if the field is monotonic and you don't |
| Compound shard key | Almost always yes — `{highCardinalityRoutingField: 1, secondaryField: 1}`                                       |
| Zones              | Data residency / tiering requirements only                                                                      |

| Option                                 | Buys you                                                                  | Costs you                                        | Choose when                                           |
| -------------------------------------- | ------------------------------------------------------------------------- | ------------------------------------------------ | ----------------------------------------------------- |
| Don't shard                            | No routing, no balancer, cheap transactions, unique indexes work normally | Bounded by one machine                           | Until you provably can't. This is the default         |
| Ranged `{tenantId:1, ts:1}`            | Tenant-targeted queries, time locality                                    | Tenant skew ⇒ jumbo chunks / hot shard           | Multi-tenant with reasonable tenant size distribution |
| Hashed `{_id: "hashed"}`               | Perfectly even writes                                                     | Every range query is scatter-gather; no locality | Write-saturated, point-lookup-only access             |
| Compound `{tenantId: "hashed", ts: 1}` | Even distribution + within-tenant time ordering                           | Cross-tenant range queries scatter               | Skewed tenants where you must break up a whale        |

**Best practices** (rule → failure it prevents)

- **Do not shard to fix a query that a compound index would fix.** Prevents adding permanent
  operational complexity to a problem that had a one-line solution — the single most common sharding
  mistake.
- **Verify shard-key candidates against the top 10 query shapes by volume before committing.**
  Prevents a cluster where the dominant query is scatter-gather and latency is bounded by the
  slowest shard.
- **Never use a monotonically increasing field as a ranged shard key.** Prevents all inserts landing
  on the shard owning `MaxKey`, which makes adding shards useless.
- **Check the frequency distribution of the key, not just cardinality.** Prevents jumbo chunks from
  a high-cardinality field where one value is 30% of documents.
- **Prefix every unique index with the shard key.** Prevents discovering at shard time that
  uniqueness cannot be enforced and must move to the application.
- **Monitor the scatter-gather rate (profiler `nShards`, `mongos` logs).** Prevents a slow drift
  where new features add unsharded predicates until most traffic is broadcast.
- **Alert on config-server replica-set health independently.** Prevents the silent state where
  migrations have been stalled for weeks and the cluster is quietly unbalancing.

#### Failure Modes, Exception Handling & Production Issues

| Failure                      | Trigger                                                   | Blast radius                                                                  | Detection signal                                             | Mitigation                                                                                              |
| ---------------------------- | --------------------------------------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| Hot shard from monotonic key | Ranged shard key on timestamp/`ObjectId`                  | One shard takes 100% of writes; adding shards does nothing                    | Per-shard write op rate wildly uneven                        | Reshard (5.0+) to hashed or a compound key with a high-cardinality prefix                               |
| Jumbo chunk                  | One shard-key value exceeds chunk size and can't be split | Permanent imbalance; that chunk never migrates                                | `sh.status()` shows jumbo flag                               | Refine the shard key (4.4+) to add a splitting suffix; or reshard                                       |
| Scatter-gather creep         | New queries omit the shard key                            | Latency = slowest shard; cluster load = N×                                    | Profiler `nShards` > 1 on high-volume shapes                 | Add the shard key to the predicate; a secondary index alone doesn't help — the key must be in the query |
| Orphaned documents           | Failed/interrupted migration                              | `readConcern: "available"` reads see duplicates                               | Range-deleter metrics                                        | Never use `readConcern: "available"`; let the range deleter run                                         |
| Config server majority loss  | CSRS outage                                               | No migrations, no splits, no new `mongos`; existing routing survives on cache | CSRS `replSetGetStatus`                                      | Treat CSRS as tier-0; monitor separately                                                                |
| Balancer causing load        | Migrations during peak                                    | Extra I/O and cache pressure on donor/recipient                               | Balancer round metrics correlated with latency               | Schedule a balancer window off-peak                                                                     |
| Cross-shard transaction cost | Multi-document txn spanning shards                        | 2PC latency; higher abort rate                                                | Transaction commit latency; `TransientTransactionError` rate | Model so transactions stay within one shard key value                                                   |

**Exception handling.** `StaleConfig` is **retryable and handled by `mongos` transparently** — it is
not an application error, and seeing it in logs is normal during migrations. `ShardNotFound` and
`FailedToSatisfyReadPreference` are surfaced to the client and are retryable at the driver level.
Cross-shard transactions abort with `TransientTransactionError` far more often than single-shard
ones, and the _entire transaction_ must be retried by the application — poison-pill risk lives in a
retry loop around a transaction that will never succeed because it spans too many shards or exceeds
`transactionLifetimeLimitSeconds`.

**Real production issues**

- **Public, cited:** MongoDB 6.0 release notes document the removal of automatic chunk splitting in
  favour of data-size-aware balancing, and 7.0 added automatic chunk merging. Prior to this, clusters
  accumulated enormous numbers of tiny chunks over time, inflating `config.chunks` and making
  balancer rounds and metadata refreshes slow — a vendor-acknowledged operational problem that
  motivated a redesign.
- `Canonical failure pattern (not a specific incident)` — **The `_id`-sharded cluster that didn't
  scale.** Symptom: team shards an insert-heavy collection on `{_id: 1}` (ranged). Write throughput
  is unchanged after adding three shards; one shard is at 100% CPU and the others near idle. Root
  cause: `ObjectId` is roughly monotonic, so every insert routes to the chunk owning `MaxKey`, which
  lives on exactly one shard; the balancer only migrates _cold_ chunks and cannot move the hot edge.
  Fix: `reshardCollection` to `{_id: "hashed"}` if access is point-lookup-only, or to
  `{tenantId: 1, _id: 1}` if tenant-scoped queries dominate. Guardrail: a pre-shard checklist that
  requires demonstrating, on production data, the frequency distribution of the candidate key and
  the fraction of top-10 query shapes that would be targeted.

#### Interview Questions

**Q:** What makes a good shard key?

**L4 answer** — Three properties simultaneously: high **cardinality** (enough distinct values to
produce many chunks), even **frequency** (no single value holding a large fraction of documents,
which creates unsplittable jumbo chunks), and **non-monotonicity** (an always-increasing key sends
every insert to the shard owning the top range). On top of that, it must appear in your dominant
query predicates — otherwise every query is scatter-gather and sharding has made you slower.

**L5 answer** — Plus the ranking, because the properties aren't equally weighted. Query targeting is
the one I'd optimize first: a perfectly distributed key that isn't in your queries gives you a
cluster where every read hits every shard, and scatter-gather latency is the _max_ over shards, so
p99 gets worse with each shard you add. That's a cluster that costs more and performs worse — the
distribution was fine and the design was wrong.

The classic tension is `{tenantId: 1, ts: 1}` (targeted, time-local, but skewed by whale tenants)
versus `{_id: "hashed"}` (perfectly distributed, zero targeting). My default for multi-tenant is the
compound ranged key, because tenant-scoped queries are almost always the dominant shape, and I'd
handle whales separately — with zones to pin a whale to dedicated shards, or by refining the key
with a suffix that splits the whale's range. Solving skew with hashing throws away targeting for
everyone to fix a problem with a few tenants.

Since 5.0 `reshardCollection` exists, so this is recoverable — but it rewrites the collection, and on
a multi-TB cluster that's a planned operation with real duration. "We can reshard later" is a
mitigation, not a reason to think less carefully up front.

---

**Q:** You shard on `{createdAt: 1}` for a time-series workload. What happens?

**L4 answer** — All inserts go to one shard — the one owning the chunk containing `MaxKey` — because
`createdAt` is monotonically increasing. Write throughput doesn't improve no matter how many shards
you add, since the balancer only migrates cold chunks and can't move the hot edge. Reads for recent
data also concentrate on that shard. Fix: hashed key, or a compound key with a high-cardinality
non-monotonic prefix.

**L5 answer** — Plus: what makes this insidious is that it _works correctly_ and looks reasonable in
`sh.status()` — data is distributed roughly evenly across shards, because old chunks did migrate.
Only the _write_ distribution is broken, and if you monitor storage per shard rather than ops per
shard, everything looks healthy. So the detection signal has to be per-shard write op rate, not data
size.

The right key depends on the query pattern, and this is where I'd push back on the framing. If
queries are "recent data for a given device," `{deviceId: 1, createdAt: 1}` gives even write
distribution across devices _and_ targeted range queries within a device — both properties. If
queries are "all data in a time window across devices," no shard key helps: that query is inherently
scatter-gather, and you should question whether MongoDB is the right store, because that access
pattern is what a columnar/lakehouse system is built for.

Also worth raising: MongoDB has native **time-series collections** since 5.0, which bucket internally
and handle the monotonic-insert problem differently. If the workload is genuinely time-series, that's
the first thing to evaluate, before shard-key design — I'd rather remove the problem than solve it.

---

**Q:** When should you _not_ shard?

**L4 answer** — When the working set fits on one machine and one primary handles the write rate.
Sharding adds `mongos` routing, config servers, a balancer, cross-shard transaction cost, shard-key
prefix requirements on unique indexes, and an operational surface you can't easily undo. If the
problem is a missing index, a bad schema, or an undersized instance, sharding makes it worse.

**L5 answer** — Plus a decision procedure rather than a rule. Sharding solves exactly two problems:
working set exceeding one machine's RAM, and write rate exceeding one primary. Before I'd agree to
shard, I'd want evidence for one of those specifically:

- For working set: `wiredTiger.cache["bytes read into cache"]` climbing at steady state _on the
  largest available instance type_. Note the qualifier — MongoDB nodes go to hundreds of GB of RAM,
  so "we're at 64 GB and struggling" is an instance-size problem, not a sharding problem.
- For write rate: primary CPU or disk saturated by writes with an index set already minimized.

And I'd check the alternatives that are cheaper and reversible, in order: fix the indexes; move
analytical reads to a tagged secondary; archive cold data out (often 80% of the collection, and it
shrinks the working set enormously); use time-series collections if applicable; scale up.

The asymmetry that decides it: scaling up is reversible in an afternoon. Sharding is a one-way door
in practice — you can `reshardCollection` but you cannot easily un-shard, and every subsequent design
decision (transactions, unique indexes, query shapes) is constrained by it forever. Given that
asymmetry, the burden of proof sits heavily on sharding, and I'd want the evidence written down
before starting.

---

**Q:** Explain a scatter-gather query and why it gets worse as you add shards.

**L4 answer** — A query whose predicate doesn't include the shard key. `mongos` can't determine which
shard owns the data, so it broadcasts to all shards and merges results. Cost scales with shard count,
and total latency is bounded by the slowest shard.

**L5 answer** — Plus the tail-latency argument, which is the real reason. Latency is the **maximum**
over N shards, not the average, so if each shard's p99 is 50 ms and you have 10 shards, the query's
expected latency approaches the 99.9th percentile of a single shard — you've turned a p99 into a
p99.9. Adding shards makes this monotonically worse. That's the mathematical statement of why
sharding is not a general performance improvement.

There's a second cost: connection and cursor amplification. Each broadcast opens cursors on every
shard, and a sorted scatter-gather requires `mongos` to hold a merge buffer. A handful of concurrent
scatter-gather queries with large sorts can exhaust `mongos` memory, which takes down routing for
everyone — and `mongos` is where people forget to set resource limits because it's "stateless."

Operationally, the thing I'd instrument is the _fraction_ of ops that are targeted, from the profiler
or `mongos` logs. The failure mode is drift: the cluster is designed with targeted queries, then two
years of feature work adds shapes without the shard key, and nobody notices until p99 doubles. A
dashboard of targeted-vs-broadcast by query shape catches it while it's still one query, not twenty.

#### L5-Only Questions

**Q:** A 12-shard cluster is 60% idle on 11 shards and saturated on one. `sh.status()` shows balanced
data sizes. Diagnose and fix.

**L5 answer** — Balanced data with unbalanced load means the imbalance is in the _access pattern_,
not the distribution — which immediately rules out the balancer and rules out jumbo chunks as the
primary cause. Three candidates:

1. **Monotonic ranged shard key.** Data is balanced because old chunks migrated, but all _writes_ go
   to the chunk owning `MaxKey`. Confirm by comparing per-shard `opcounters.insert` — most likely
   cause, and the signature matches exactly.
2. **Frequency skew within a valid key.** One tenant is 30% of traffic but not 30% of storage — a
   small-but-hot tenant. Data size looks balanced, read ops don't. Confirm from per-shard read op
   rate plus a top-N-by-tenant query in the profiler.
3. **A hot single document** (a counter, a config doc, a lock) living on one shard. Confirm from
   `WriteConflict` rate on that shard specifically.

The distinguishing measurement is per-shard `opcounters` split by insert/query/update, correlated
with the profiler's shard-key values. I'd get that before touching anything, because the three fixes
are incompatible.

Fixes by cause:

- (1) `reshardCollection` to a hashed or compound key. Plan it as a migration with a duration
  estimate, not a config change.
- (2) Zones — pin the hot tenant to dedicated shards, which is the mechanism actually designed for
  this and doesn't require rewriting the collection. Or refine the shard key with a suffix that
  splits that tenant's range.
- (3) Not a sharding fix at all. Shard the counter across N documents, or move it out of MongoDB — a
  hot counter is a bad fit for any B+ tree store and belongs in Redis or in an aggregated
  write-behind.

The mitigation I'd apply while diagnosing is `maxTimeMS` on the affected paths, so the saturated
shard sheds load rather than accumulating queue depth and dragging the merge latency of every
scatter-gather query with it.

---

**Q:** Design the sharding strategy for a multi-tenant SaaS with 50 000 tenants where the largest
tenant is 15% of total data and the smallest 40 000 tenants are 5% combined.

**L5 answer** — The distribution is the whole problem: this is a power law, so _any_ pure `tenantId`
key produces jumbo chunks at the head and wasted chunks at the tail.

The key I'd start from: `{tenantId: 1, _id: 1}` ranged. Rationale — tenant equality is in essentially
every query (it must be, for isolation), so this gives targeted routing for the dominant shape, and
the `_id` suffix provides splitting granularity _within_ a tenant, which is what prevents the head
tenants from becoming unsplittable jumbo chunks. That suffix is the specific fix for the
frequency-skew failure, and it's why I wouldn't use bare `{tenantId: 1}`.

Then handle head and tail separately, because one key can't serve both:

- **Head (the 15% tenant and the next few):** zones. Pin them to dedicated shards with
  `addShardToZone` / `updateZoneKeyRange`. This is the mechanism designed for exactly this, and it
  converts a noisy-neighbour problem into a capacity-planning problem, which is much easier to reason
  about. The cost is that you now manage zone ranges as those tenants grow, and zone boundaries are a
  manual artifact — I'd automate assignment off a tenant-size job rather than leaving it to someone's
  memory.
- **Tail (40 000 tiny tenants):** they're 5% of data and spread naturally by `tenantId` range. The
  risk here isn't distribution, it's _chunk count_ — many tiny ranges inflate `config.chunks`.
  Post-7.0 automatic merging handles this; on older versions I'd schedule `mergeChunks`.

What I'd reject: `{tenantId: "hashed"}`. It fixes the head-tenant distribution but destroys targeted
range queries within a tenant (list this tenant's records ordered by date — which is every SaaS list
view), converting the most common query in the product into scatter-gather. Solving a 15%-of-data
problem by degrading 100% of queries is the wrong trade.

The thing I'd insist on before any of this: proving sharding is needed at all. 50 000 tenants is a
business-scale number, not a data-scale number — if the total working set is 300 GB, a single large
replica set is simpler, supports cheap transactions, has no shard-key constraint on unique indexes,
and can be scaled up further. I'd want the working-set measurement first, and I'd expect to be told
the real driver is either a data-residency compliance requirement (which is a zones answer, and a
legitimate reason to shard early) or an anticipated growth curve (which is a "design the key now,
shard later" answer).

---

## 5. Transactions & Consistency

### 5.1 Multi-Document Transactions

#### Concept

- **What it is** — ACID transactions spanning multiple documents, collections, and databases;
  available on replica sets since **4.0** and on sharded clusters since **4.2**. Isolation level is
  **snapshot isolation**, implemented on WiredTiger's MVCC.

- **What it solves** — Cross-document invariants. Before 4.0, the only atomicity unit was a single
  document, so any invariant spanning entities required either denormalizing them into one document
  or implementing a two-phase commit in application code.

- **What it replaced** — (a) the documented application-level two-phase-commit pattern MongoDB used
  to publish, which was correct but required every client to implement it identically and offered no
  isolation; (b) forced denormalization, which solved atomicity by making documents unboundedly
  large (§1.1).

- **What it works with / ecosystem** — built on WiredTiger MVCC and commit timestamps, on
  `readConcern: "snapshot"`, and on retryable-write session infrastructure. On sharded clusters,
  uses **two-phase commit** across participating shards.

  Conflicts with: the document model itself. The existence of transactions is not permission to model
  relationally.

- **Place in the world** — the small fraction of operations with a genuine cross-entity invariant:
  transfer between accounts, order + inventory decrement, outbox + domain write. **Wrong answer to**:
  the general read-modify-write pattern, which single-document atomic operators (`$inc`, `$set` with
  a version predicate) handle at a fraction of the cost.

#### Architecture & Core Components

```
  session.startTransaction({readConcern:{level:"snapshot"},
                            writeConcern:{w:"majority"}})
        │
        ▼
  ┌──────────────────────────────────────────────────┐
  │ WiredTiger snapshot pinned at start               │
  │  all reads see this snapshot; writes buffered as  │
  │  uncommitted versions on update chains            │
  └───────────────┬──────────────────────────────────┘
                  │ any conflicting concurrent write
                  │ ⇒ WT_ROLLBACK ⇒ TransientTransactionError
                  │    (retry the WHOLE transaction)
                  ▼
        commitTransaction
                  │
    ┌─────────────┴──────────────────┐
    │ single shard / replica set     │ single oplog entry (or applyOps
    │  → local commit + oplog write  │  chain if > 16 MB, 4.2+)
    └────────────────────────────────┘
    ┌────────────────────────────────────────────────┐
    │ SHARDED: two-phase commit                       │
    │  mongos = coordinator                           │
    │  prepare → all participants vote                │
    │  → coordinator decision persisted               │
    │  → commit/abort broadcast                       │
    │  participants hold PREPARED state (blocking)    │
    └────────────────────────────────────────────────┘
```

| Component                           | Single responsibility                               |
| ----------------------------------- | --------------------------------------------------- |
| Client session                      | Carry the logical session id and transaction number |
| Snapshot                            | Fix the read view for the transaction's lifetime    |
| Update chain (uncommitted versions) | Hold writes until commit                            |
| Commit timestamp                    | Order the transaction in the oplog                  |
| 2PC coordinator (`mongos`)          | Drive prepare/commit across shards                  |
| `transactionLifetimeLimitSeconds`   | Bound how long a snapshot may be pinned             |

#### How Each Component Works

**Snapshot isolation**

- All reads in the transaction see the state as of transaction start. Writes create uncommitted
  versions.
- Defeater — and this is the important one: snapshot isolation is **not serializable**. It prevents
  dirty reads, non-repeatable reads, and phantom reads within the snapshot, but permits **write
  skew**: two transactions read overlapping data, write disjoint documents, and both commit, leaving
  an invariant violated that neither transaction alone would violate. MongoDB does not detect write
  skew. If your invariant is "at least one doctor must remain on call," transactions do not save you
  — you need to write to a common document to force a conflict.

**Conflict detection**

- First-writer-wins on a per-document basis: if another transaction commits a write to a document
  this transaction has written, this transaction gets `WT_ROLLBACK`.
- Surfaced as `TransientTransactionError`. The **entire transaction must be retried from the
  beginning** — you cannot retry a single operation.
- Drivers provide `withTransaction()`, which implements the correct retry loop for both
  `TransientTransactionError` and `UnknownTransactionCommitResult`. Hand-rolling this loop is a
  common source of bugs; use the callback API.

**Lifetime limit**

- `transactionLifetimeLimitSeconds` default **60**. A transaction exceeding it is aborted
  server-side.
- Reason: an open transaction pins the WiredTiger oldest timestamp, preventing version cleanup. A
  long transaction therefore causes cache growth for the _whole node_, not just for itself.
- Defeater for "just raise the limit": raising it converts a bounded per-transaction failure into an
  unbounded node-wide cache problem. The limit is a safety valve, not a tuning parameter.

**Oplog representation**

- A committed transaction appears as `applyOps` entries so secondaries apply it atomically. Before
  4.2 the whole transaction had to fit in one 16 MB oplog entry, which capped transaction size; 4.2+
  chains multiple entries.
- Defeater: "unlimited transaction size" is still wrong in practice — a large transaction holds a
  snapshot longer, increases conflict probability, and creates an oplog burst that can push
  secondaries toward the window limit.

**Sharded (distributed) transactions**

- `mongos` coordinates a two-phase commit across participating shards.
- Participants enter a **prepared** state, which holds locks and blocks conflicting operations until
  the decision arrives. A coordinator failure between prepare and decision leaves participants
  blocked until recovery — the classic 2PC blocking problem, which MongoDB mitigates by persisting
  the coordinator decision, not by eliminating.
- Cost: at minimum two extra round trips plus majority writes at each phase. Abort rates are
  materially higher than single-shard.

**Retryable writes vs transactions**

- Distinct mechanisms sharing session infrastructure. A retryable write attaches a transaction number
  to a single-document write; the server records the result in `config.transactions` so a retry
  returns the original outcome rather than re-applying. That gives idempotence _without_ a
  transaction and without snapshot cost — it's the right tool far more often than a transaction is.

#### Design Decisions, Tradeoffs & Best Practices

**Decisions the designers made**

| Decision                      | Alternative rejected                                       | Why                                                                                                                                                 |
| ----------------------------- | ---------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Snapshot isolation            | Serializable                                               | SI is achievable on MVCC without predicate locking or a certification phase. Cost: write skew is permitted and undetected                           |
| 60 s default lifetime limit   | Unbounded                                                  | An open snapshot pins the oldest timestamp and grows cache node-wide. Cost: long transactions must be redesigned, not configured around             |
| 2PC for sharded transactions  | Deterministic/Calvin-style, or no cross-shard transactions | Preserves the same API across topologies. Cost: blocking prepared state, higher latency, higher abort rate                                          |
| Transactions added late (4.0) | From the start                                             | The document model was designed so most invariants fit in one document. Cost: an ecosystem of applications built around the absence of transactions |

**Decisions you have to make**

| Decision                                         | Deciding variable                                                                                     |
| ------------------------------------------------ | ----------------------------------------------------------------------------------------------------- |
| Transaction vs single-document atomic update     | Does the invariant genuinely span documents? If a schema change could co-locate them, do that instead |
| Transaction vs retryable write + idempotency key | Do you need isolation, or just exactly-once effect? The latter is far cheaper                         |
| Keep transactions within one shard               | Whether the documents share a shard-key value. Design for this deliberately                           |
| Retry policy                                     | Use the driver's `withTransaction()` callback; do not hand-roll                                       |

| Option                                                        | Buys you                           | Costs you                                                 | Choose when                                               |
| ------------------------------------------------------------- | ---------------------------------- | --------------------------------------------------------- | --------------------------------------------------------- |
| Single-doc atomic update (`$inc`, `$set` + version predicate) | No snapshot, no 2PC, no retry loop | Only one document                                         | Default. Redesign toward this                             |
| Replica-set transaction                                       | Real cross-document atomicity      | Snapshot pinning, conflict retries, 60 s cap              | Genuine multi-entity invariant, unsharded or single-shard |
| Cross-shard transaction                                       | Cross-shard atomicity              | 2PC latency, prepared-state blocking, high abort rate     | Rare, and a signal your shard key is wrong                |
| Application-level saga                                        | No distributed transaction; scales | Eventual consistency; compensating actions you must write | Cross-service, or cross-shard at volume                   |

**Best practices** (rule → failure it prevents)

- **Keep transactions short and touch as few documents as possible.** Prevents snapshot pinning that
  grows the whole node's cache, and prevents conflict-rate escalation.
- **Always use the driver's `withTransaction()` callback.** Prevents an incorrect retry loop that
  either fails to retry `TransientTransactionError` or retries `commitTransaction` unsafely on
  `UnknownTransactionCommitResult`.
- **Never do I/O (HTTP calls, queue publishes) inside a transaction body.** Prevents an external
  latency spike from pinning a snapshot for 30 s, and prevents the retry loop from re-issuing the
  side effect N times.
- **Design shard keys so transactions stay on one shard.** Prevents 2PC cost and prepared-state
  blocking on the hot path.
- **If your invariant is "at least N" or "at most N" across documents, force a conflict by writing to
  a shared document.** Prevents write skew, which snapshot isolation does not.
- **Don't raise `transactionLifetimeLimitSeconds`.** Prevents converting a transaction failure into a
  node-wide cache incident.

#### Failure Modes, Exception Handling & Production Issues

| Failure                              | Trigger                                       | Blast radius                                            | Detection signal                                        | Mitigation                                                                                  |
| ------------------------------------ | --------------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Write skew                           | Two txns read overlapping, write disjoint     | Invariant violated silently; no error                   | Only caught by reconciliation or an audit query         | Force conflict via a shared document, or model the invariant into one document              |
| Conflict storm                       | Many transactions on the same hot documents   | Retry amplification; throughput collapses under load    | `TransientTransactionError` rate; rising commit latency | Reduce transaction scope; shard the hot document; back off                                  |
| Snapshot pinning                     | Long transaction (or long `majority` read)    | Node-wide cache growth; eviction pressure for everyone  | Oldest-timestamp lag; cache dirty bytes                 | Enforce short transactions; `maxTimeMS`; never do I/O inside                                |
| 2PC coordinator failure              | Coordinator dies between prepare and decision | Participants hold prepared state; conflicting ops block | Long-running prepared transactions in `currentOp`       | Decision is persisted and recovered; keep transactions single-shard to avoid entirely       |
| `UnknownTransactionCommitResult`     | Network failure during commit                 | Ambiguous — may or may not have committed               | Error label on commit                                   | Retry `commitTransaction` (idempotent by transaction number); `withTransaction()` does this |
| Oplog burst from a large transaction | Transaction writing many/large documents      | Secondaries lag; oplog window shrinks                   | Replication lag spike correlated with the job           | Batch into many small transactions, or use unordered bulk writes with idempotency instead   |

**Exception handling.** MongoDB uses **error labels**, and the distinction is the whole API:
`TransientTransactionError` ⇒ retry the **entire** transaction; `UnknownTransactionCommitResult` ⇒
retry only `commitTransaction`, which is safe because commit is idempotent per transaction number.
Anything else is terminal for that transaction. Retrying the whole transaction on
`UnknownTransactionCommitResult` is a correctness bug (it may re-apply a committed transaction's
_effects_ if the body isn't idempotent); retrying only the commit on `TransientTransactionError` is
also wrong (there's nothing to commit). This is precisely why the callback API exists and why
hand-rolled loops are dangerous. Poison-pill risk: a transaction that always conflicts — because it
writes a single hot counter — will retry until the lifetime limit forever, burning CPU on every
attempt.

**Real production issues**

- **Public, cited:** MongoDB's transactions documentation states the production considerations
  directly — the 60 s default lifetime limit, the requirement to retry on
  `TransientTransactionError`, and the guidance to keep transactions short because they hold a
  snapshot. The vendor documenting these as _production considerations_ rather than as tuning options
  is itself the signal about how they're meant to be used.
- `Canonical failure pattern (not a specific incident)` — **The transaction with an HTTP call
  inside.** Symptom: cluster-wide latency degradation every afternoon; WiredTiger cache dirty bytes
  climbing; no obvious slow query. Root cause: a service opened a transaction, called a third-party
  API inside the body, and that API's p99 went from 200 ms to 25 s. Every in-flight transaction
  pinned a snapshot for 25 s, and the retry loop multiplied it. Fix: move the API call outside the
  transaction; write the result, then transact. Guardrail: a lint rule or architecture test
  forbidding network calls inside a `withTransaction` lambda, plus an alert on the
  oldest-active-transaction duration — because the database-side symptom (cache pressure) is several
  steps removed from the cause and nobody finds it by looking at slow queries.

#### Interview Questions

**Q:** MongoDB has transactions now. Should you use them the way you'd use them in PostgreSQL?

**L4 answer** — No. In MongoDB, a single-document update is already atomic, so most
read-modify-write patterns are handled by atomic operators (`$inc`, `$set` with a version predicate)
with none of the transaction cost. Transactions pin a WiredTiger snapshot, have a 60-second default
lifetime limit, require a full-transaction retry on conflict, and on sharded clusters use two-phase
commit. Use them for genuine cross-document invariants only.

**L5 answer** — Plus the modeling argument, which is the real answer. The document model's premise is
that entities that change together live together, so the atomicity boundary and the consistency
boundary coincide. If you find yourself reaching for transactions routinely, the schema is fighting
the engine — you've built a relational model in a document store and you'll pay for it in every
dimension: transaction cost, cross-shard 2PC, and the loss of the single-document atomicity that made
MongoDB fast.

There's also a correctness point people miss: MongoDB gives **snapshot isolation**, not
serializable. So a PostgreSQL habit that relies on `SERIALIZABLE` — or on `SELECT ... FOR UPDATE` to
serialize a check-then-act — does not translate. Snapshot isolation permits write skew: two
transactions read the same set, write disjoint documents, both commit, invariant broken, no error.
If the invariant is "at least one on-call engineer remains," you must force a conflict by writing to
a shared document. PostgreSQL's `SERIALIZABLE` would have caught it with an SSI abort; MongoDB will
not.

So my rule: transactions for genuine multi-entity atomicity, single-document operators as the
default, and any invariant across documents gets an explicit conflict point designed into the schema
rather than assumed from the isolation level.

---

**Q:** What's the difference between a retryable write and a transaction?

**L4 answer** — A retryable write is a single-document write that the driver may retry once on a
transient network or failover error; the server records the outcome keyed by session and transaction
number in `config.transactions`, so a retry returns the original result instead of re-applying. It
gives idempotence with no snapshot and no isolation cost. A transaction gives snapshot isolation and
atomicity across multiple documents, at much higher cost.

**L5 answer** — Plus: they share session infrastructure, which is why people conflate them, but they
solve orthogonal problems — _exactly-once effect_ versus _isolation_. Most of the time when someone
reaches for a transaction, what they actually needed was the former.

Concretely: "insert this order, and don't create two if the network hiccups" is a retryable-write
problem, or better, an upsert on a client-generated idempotency key — no transaction needed. "Insert
this order **and** decrement inventory, both or neither" is a transaction problem, and only if the
two documents can't be co-located.

The limits worth naming: retryable writes cover a specific error class and exactly one automatic
retry, so an application-level retry loop still needs its own idempotency key — the driver's
mechanism doesn't extend to your `for` loop. And retryable writes require a replica set or sharded
cluster (there's no session infrastructure on a standalone), which is one of several reasons
standalone `mongod` is a development-only topology.

---

**Q:** A transaction fails with `TransientTransactionError`. What do you do?

**L4 answer** — Retry the entire transaction from the beginning — not the individual operation. The
snapshot is gone, so the reads must be redone. Use the driver's `withTransaction()` callback, which
implements the correct retry semantics for both `TransientTransactionError` and
`UnknownTransactionCommitResult`.

**L5 answer** — Plus the two things that turn this from a retry into an incident.

First, **the callback must be side-effect-free**, because it will run again. Any queue publish,
email, HTTP call, or mutation of application state inside the transaction body executes once per
attempt. This is the single most common bug in MongoDB transaction code and it's silent — the
transaction is correct, the side effects are duplicated.

Second, **a rising `TransientTransactionError` rate is a design signal, not a transient**. Conflicts
mean multiple transactions are contending for the same documents, so retrying harder increases
contention — you get retry amplification and throughput _decreases_ under load, which is a
congestive collapse shape, not graceful degradation. The fix is to reduce contention: shrink the
transaction's write set, shard a hot counter across N documents, or move the contended value out of
the transaction entirely into a single-document atomic operator.

I'd also bound it: `withTransaction()` retries until the transaction lifetime limit by default, so a
permanently-conflicting transaction burns CPU for 60 s per attempt indefinitely. In production I'd add
an attempt cap and a metric, so the pathology surfaces as an alert rather than as unexplained CPU.

#### L5-Only Questions

**Q:** Explain write skew, why MongoDB permits it, and how you'd prevent it in a specific design.

**L5 answer** — Write skew: two transactions read an overlapping set, each makes a decision based on
what it read, then each writes to a _different_ document. Neither writes to a document the other
wrote, so there's no conflict to detect, both commit, and an invariant spanning the read set is
violated.

Canonical case: on-call rota with the invariant "at least one engineer on call." Alice and Bob are
both on call. Two transactions run concurrently: T1 reads the rota, sees two on call, sets
`alice.oncall = false`. T2 reads the same snapshot, sees two on call, sets `bob.oncall = false`.
Disjoint writes, no conflict, both commit. Zero engineers on call. Neither transaction did anything
wrong in isolation.

MongoDB permits it because snapshot isolation doesn't do predicate locking. Detecting write skew
requires either serializable isolation with an SSI certification phase (PostgreSQL's approach — track
read/write dependency cycles and abort one) or explicit predicate locks. Both cost throughput on
every transaction to prevent an anomaly most transactions can't hit, and MongoDB chose the cheaper
isolation level. PostgreSQL made the opposite choice available as an option, not a default — so this
isn't MongoDB being careless, it's the standard SI/serializable trade.

Three ways to prevent it, in order of preference:

1. **Model the invariant into one document.** Store the rota as a single document with an array of
   on-call engineers, and use a single-document update with a predicate:
   `updateOne({_id: rotaId, "oncall.1": {$exists: true}}, {$pull: {oncall: "alice"}})`. The predicate
   means "only if at least 2 remain." This is atomic without a transaction, has no skew, and is the
   fastest option. It's also the answer that says you understood the document model.
2. **Force a conflict inside the transaction** by having every participant write a shared document —
   e.g. `$inc` a version on the rota document. Now the two transactions do conflict, one gets
   `TransientTransactionError`, and retrying re-reads the true state. Correct, but you've hand-rolled
   the certification the isolation level didn't give you, and it's easy to forget on the next code
   path.
3. **Externalize the constraint** to something that serializes — a distributed lock, or a
   single-writer queue for rota mutations. Correct and slow; reserve it for genuinely complex
   multi-entity invariants.

I'd ship (1). The general lesson: in a document store, an invariant should live inside one document's
atomicity boundary, and when it can't, that's a schema-design question before it's an
isolation-level question.

---

**Q:** Order service must decrement inventory and create an order atomically. Inventory is sharded by
SKU, orders by customer. Design it.

**L5 answer** — As stated, this is a cross-shard transaction on the hot path — two shards, two-phase
commit, prepared-state blocking, elevated abort rate, and latency of two extra round trips plus
majority writes at each phase. It'll work at low volume and degrade badly at high volume, and the
degradation will be worst exactly at peak. I'd treat the requirement as negotiable and present three
designs.

**Option A — make it single-shard.** Change the shard key so both documents co-locate. That means
sharding orders by SKU (wrong — orders are queried by customer, and you'd destroy the dominant query)
or inventory by customer (nonsense — inventory isn't customer-scoped). So co-location isn't achievable
here. Worth stating explicitly, because it's the first thing to check, and ruling it out with a reason
is the substance of the answer.

**Option B — don't make it atomic; make it compensable.** A saga: reserve inventory (a single-document
atomic `$inc` with a predicate `{qty: {$gte: n}}` — atomic, no transaction, fails cleanly if
insufficient), then create the order, then confirm the reservation. If order creation fails, a
compensating job releases the reservation after a TTL. This is the design I'd ship. It gives you:

- No distributed transaction on the hot path.
- The inventory check-and-decrement is a single-document conditional update, which is exactly what the
  document model is good at and is genuinely atomic.
- A bounded inconsistency window (reservations held by a crashed process expire), which is a business
  parameter rather than a correctness hole.

Cost, stated honestly: inventory can be transiently over-reserved from the customer's perspective if
orders fail frequently, and you need the reaper job plus monitoring on stuck reservations. That's real
operational work, and it's cheaper than 2PC on every order.

**Option C — cross-shard transaction.** Keep it if the volume is genuinely low (order of tens per
second) and the team's operational tolerance for a saga is lower than for latency. It's simplest to
reason about and I wouldn't dismiss it for a modest business — but I'd put a ceiling on it and
instrument the abort rate so the migration to (B) is triggered by data rather than by an outage.

The framing I'd bring to the design review: "atomic" is usually a proxy for "no oversell and no
orphaned order," and reservations satisfy that requirement without distributed atomicity. Getting the
requirement restated in terms of the business invariant, rather than the mechanism, is what makes
option B available at all.

---

## 6. Schema Design

### 6.1 Embed vs Reference, and the Anti-Patterns

#### Concept

- **What it is** — The decision, for every relationship, whether the related data lives _inside_ the
  parent document (embedding) or in a separate document joined at read time (referencing).

- **What it solves** — It is the mechanism by which you trade read cost against write cost and
  document size. In a relational database, normalization is largely prescriptive; in MongoDB it is
  the primary performance lever and it is entirely yours.

- **What it replaced** — Third normal form as a default. Insufficient here specifically because
  MongoDB's join (`$lookup`) is not a first-class, index-optimized, planner-integrated operation the
  way a relational join is — it's a pipeline stage, it can't push predicates through as well, and on
  sharded clusters it has restrictions. Normalizing by reflex produces a schema whose reads require
  joins the engine isn't built to do well.

- **What it works with / ecosystem** — interacts with indexing (§2.1 — you can only index what's in
  the document), the 16 MB limit (§1.1), transactions (§5.1 — embedding makes cross-entity atomicity
  free), and sharding (§4.1 — embedding co-locates by construction).

- **Place in the world** — every MongoDB design review. **Wrong answer to**: highly connected data
  with many-to-many traversals of arbitrary depth — that's a graph database, and neither embedding
  nor referencing in MongoDB serves it well.

#### Architecture & Core Components

This subsection describes a design methodology rather than a runtime system, so the "components" are
the patterns themselves and the decision inputs.

```
                  ┌──────────────────────────────┐
                  │  cardinality of the relation │
                  └──────────────┬───────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        ▼                        ▼                        ▼
   one-to-few              one-to-many               one-to-squillions
   (< ~100, bounded)       (bounded, large-ish)      (unbounded)
        │                        │                        │
        ▼                        ▼                        ▼
     EMBED                  REFERENCE                REFERENCE from
   array in parent          child docs hold          the CHILD side only
                            parentId + index         (never an array in parent)
        │                        │                        │
        └───────────┬────────────┴────────────────────────┘
                    ▼
        ┌──────────────────────────────────────┐
        │ then adjust for:                      │
        │  • read/write ratio                   │
        │  • update locality (what changes      │
        │    together?)                         │
        │  • atomicity requirement              │
        │  • duplication tolerance (extended    │
        │    reference / subset patterns)       │
        └──────────────────────────────────────┘
```

| Pattern            | Single responsibility                                         |
| ------------------ | ------------------------------------------------------------- |
| Embed              | Co-locate data read together; make it atomic for free         |
| Reference          | Bound document size; avoid duplicating volatile data          |
| Extended reference | Duplicate the 2–3 fields you actually read, avoiding the join |
| Subset             | Embed the hot N (top 10 reviews), reference the rest          |
| Bucket             | Cap array growth by splitting into fixed-size buckets         |
| Computed           | Precompute an aggregate on write to avoid computing on read   |
| Outlier            | Special-case the 0.1% of documents that break the pattern     |

#### How Each Component Works

**Embedding**

- One read, one document, atomic updates for free, no join.
- Fails when: the array is unbounded (§1.1 — 16 MB), the embedded data is updated far more often than
  read (every update rewrites the parent's page), or the embedded data is independently queried (you
  can index into it, but you can't return just the child efficiently without `$unwind`).
- Cost that surprises people: the whole parent document is pulled through the WiredTiger cache on
  every read, even if you project one field. Embedding a 2 MB blob inflates the working set for
  everyone reading the parent.

**Referencing**

- Bounds document size, keeps volatile data in one place, allows independent querying.
- Fails when: the read path needs both, on every request. `$lookup` executes as a per-document lookup
  against the foreign collection's index — so an N-document result does N index lookups. It is not a
  hash join. Fine for N=20, bad for N=200 000.
- On sharded clusters, `$lookup` has version-dependent restrictions on the foreign collection; verify
  for your version rather than assuming.

**Extended reference**

- Duplicate the small subset of fields you actually display — store `{userId, userName, userAvatar}`
  on the comment rather than joining to `users`.
- Fails when: the duplicated field is volatile. A username change now requires a fan-out update.
- Deciding variable: `update_frequency_of_duplicated_field × fan_out_size` versus
  `join_cost × read_frequency`. Duplicate immutable or near-immutable fields; reference volatile ones.

**Subset**

- Embed the top N (most recent 10 comments), reference the full set.
- Buys: the common read is one document. Costs: writes must maintain both copies, which needs either
  a transaction or an idempotent reconciliation job.

**Bucket**

- `{deviceId, hourStart, readings: [...≤3600]}`. Caps array length structurally.
- The correct answer to time-series and to any unbounded append. MongoDB's native **time-series
  collections** (5.0+) implement this pattern in the engine, which is preferable to hand-rolling it
  when the data actually is time-series.

**The named anti-patterns** (MongoDB publishes these; worth knowing by name)

- **Massive arrays** — unbounded embedding. Hits 16 MB; also makes multikey indexes enormous.
- **Massive number of collections** — a collection per tenant. Each collection and index is a
  WiredTiger table with its own file handles and cache footprint; thousands of them degrade startup,
  cache, and backup.
- **Unnecessary indexes** — §2.1 write amplification.
- **Bloated documents** — pulling data through cache that nobody reads.
- **Separating data that's accessed together** — over-normalization; the `$lookup` tax.
- **Case-insensitive queries without a case-insensitive index** — a regex or `$toLower` in a
  predicate cannot use a standard index; use a **collation** with `strength: 2` on the index _and_
  the query, or store a normalized duplicate field.

#### Design Decisions, Tradeoffs & Best Practices

**Decisions the designers made**

| Decision                                                     | Alternative rejected                        | Why                                                                                                                                                                    |
| ------------------------------------------------------------ | ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Atomicity at the document boundary                           | Row-level atomicity + real joins            | Makes the common case (entities that change together, stored together) fast and atomic with no coordination. Cost: modeling mistakes are expensive and hard to reverse |
| `$lookup` as a pipeline stage, not a planner-integrated join | First-class join with hash/merge strategies | Keeps the query engine simple and the document model primary. Cost: joins are per-document index lookups and don't scale like a relational join                        |
| No foreign keys / referential integrity                      | Enforced references                         | Avoids distributed constraint checking. Cost: dangling references are an application concern, always                                                                   |

**Decisions you have to make**

| Decision                                  | Deciding variable                                                                                                  |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Embed or reference                        | Cardinality first (bounded?), then read/write ratio, then update locality                                          |
| Duplicate a field (extended reference)    | Volatility of that field × fan-out size                                                                            |
| Bucket or not                             | Whether the array is unbounded in time. If yes, always bucket                                                      |
| Collection per tenant vs `tenantId` field | Tenant count. Thousands of collections is an anti-pattern; a `tenantId` field with a compound index is the default |

| Option             | Buys you                                                | Costs you                                            | Choose when                                          |
| ------------------ | ------------------------------------------------------- | ---------------------------------------------------- | ---------------------------------------------------- |
| Embed              | 1 read, free atomicity, natural sharding co-location    | Document growth; whole-doc cache cost; 16 MB ceiling | Bounded cardinality, read together, written together |
| Reference          | Bounded size, single source of truth, independent query | `$lookup` per document on the read path              | Unbounded or independently-queried children          |
| Extended reference | No join on the hot read                                 | Fan-out update when the duplicate changes            | Duplicated fields are immutable or rarely change     |
| Subset             | Hot read is one document                                | Dual maintenance                                     | Clear hot/cold split in the child set                |
| Bucket             | Structural bound on growth                              | Read path needs `$slice`/aggregation                 | Any unbounded append; time-series                    |

**Best practices** (rule → failure it prevents)

- **Model from the query patterns, not from the entity relationships.** Prevents a normalized schema
  whose every read requires a `$lookup` the engine executes as N index lookups.
- **Never embed an array that grows with time or user activity.** Prevents the 16 MB wall, which is a
  write-failing, migration-requiring incident rather than a slow query.
- **Duplicate only immutable or near-immutable fields.** Prevents a fan-out update job that touches a
  million documents because someone changed their display name.
- **Use a `tenantId` field, not a collection per tenant, past ~100 tenants.** Prevents thousands of
  WiredTiger tables consuming file handles and cache and making backups and startup slow.
- **Add a schema validator once the shape stabilizes.** Prevents silent shape drift that breaks index
  coverage months later.
- **Store a normalized lowercase duplicate, or use an index collation, for case-insensitive search.**
  Prevents `$regex`/`$toLower` predicates that cannot use an index and silently become collection
  scans.

#### Failure Modes, Exception Handling & Production Issues

| Failure                         | Trigger                                      | Blast radius                                                            | Detection signal                                           | Mitigation                                                                                    |
| ------------------------------- | -------------------------------------------- | ----------------------------------------------------------------------- | ---------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| 16 MB wall                      | Unbounded embedded array                     | Writes to the most active documents fail permanently                    | `BSONObjectTooLarge`; document-size histogram              | Bucket pattern; migrate                                                                       |
| `$lookup` on a large result set | Over-normalized schema + a report            | N index lookups per query; latency scales with N                        | `explain` showing `$lookup` with high `nReturned` upstream | Denormalize the read path; or precompute                                                      |
| Fan-out update storm            | A volatile field was duplicated              | Millions of writes; replication lag; cache pressure                     | Write op spike with no traffic change                      | Reference volatile fields; if you must duplicate, do it async and accept eventual consistency |
| Bloated documents               | Blobs embedded alongside hot fields          | Working set inflated for every reader                                   | Doc size vs projected field size ratio                     | Split cold data out (separate collection or S3)                                               |
| Collection-per-tenant sprawl    | 5 000 tenants, 5 000 collections × 4 indexes | Slow startup, file-handle exhaustion, cache fragmentation, slow backups | `listCollections` count; open file descriptors             | `tenantId` field + compound index                                                             |
| Case-insensitive scan           | `$regex: /^x/i` or `$toLower` in `$match`    | COLLSCAN under an innocuous-looking query                               | `explain` COLLSCAN on an indexed field                     | Index collation `strength: 2`, matched by the query's collation                               |

**Exception handling.** Schema-design failures mostly do **not** surface as exceptions — they surface
as latency, cache pressure, and replication lag, which is what makes them dangerous. The two that do
throw are `BSONObjectTooLarge` (terminal, structural) and `DocumentValidationFailure` from a schema
validator (terminal for that write, and deliberately so — it's doing its job). Poison-pill risk lives
in any consumer that reads-modifies-writes a document that has grown past the limit; it will fail
forever and a naive retry spins.

**Real production issues**

- **Public, cited:** MongoDB's "Building with Patterns" blog series and the published "Schema Design
  Anti-Patterns" material name massive arrays, massive numbers of collections, unnecessary indexes,
  bloated documents, and separating data accessed together — the vendor's own list of what they see
  break in the field, which is stronger evidence than an anecdote.
- `Canonical failure pattern (not a specific incident)` — **The username denormalization.** Symptom:
  a routine "users can change their display name" feature ships; a week later, replication lag spikes
  for 40 minutes whenever a particular customer's admin edits their profile. Root cause: `userName`
  was embedded on every comment, activity-log entry, and notification as an extended reference; one
  user had 1.8 M associated documents, so a name change was a 1.8 M-document update. Fix: keep the
  reference and `$lookup` for the rare case, or accept eventual consistency and do the fan-out through
  a rate-limited background job. Guardrail: at design review, require a stated fan-out bound for every
  duplicated field — "how many documents does this change touch, at p99?" — because duplication
  decisions are made when the fan-out is 5 and paid when it's 5 million.

#### Interview Questions

**Q:** Embed or reference — how do you decide?

**L4 answer** — Start with cardinality. One-to-few and bounded: embed. One-to-many but unbounded:
reference from the child side, never as an array in the parent. Then adjust for read/write ratio
(data read together should live together), update locality (data written together should live
together), and atomicity (embedding gives it free). Document size is the hard constraint — 16 MB.

**L5 answer** — Plus the two inputs that actually decide the ambiguous cases.

**Update locality**, not just read locality. If the embedded array is updated 100× more often than
the parent is read, every update rewrites the parent's page and grows the update chain — you've
optimized a read that rarely happens at the cost of a write that happens constantly. So the question
isn't "are these read together," it's "are these _written_ together."

**Cache footprint.** The whole parent document is pulled through the WiredTiger cache on every read,
regardless of projection. Embedding a 500 KB payload alongside the three fields your list view
displays means your working set is 500 KB per document instead of 300 bytes, and the working set is
what determines whether you're memory-resident. This is the failure mode that doesn't show up in
`explain` at all — the plan is perfect and the cluster is slow.

The pattern I reach for most often is **extended reference**: don't choose between embedding the
child and joining to it, duplicate the 2–3 fields you actually render. The deciding variable is
volatility × fan-out — duplicate immutable things (SKU, ISIN, a category name), reference volatile
ones (a display name, a status). And I'd make the fan-out bound an explicit artifact of the design
review, because that's the number that turns a good decision into a bad one two years later.

---

**Q:** What's wrong with a collection per tenant?

**L4 answer** — Each collection and each of its indexes is a separate WiredTiger table with its own
file handle and cache footprint. At thousands of tenants you get slow startup, file-descriptor
pressure, cache fragmentation, slow backups, and an expensive `listCollections`. The default is a
`tenantId` field with `tenantId` as the prefix of every compound index.

**L5 answer** — Plus: the reason people propose it is real, and I'd acknowledge it before rejecting
it — collection-per-tenant gives you trivially clean deletion (drop the collection for GDPR),
per-tenant index tuning, and a hard isolation story that's easy to explain to auditors. Those are
genuine benefits and the shared-collection design has to answer them: deletion becomes a bulk delete
plus a `compact` (slower, and doesn't reclaim space immediately), and isolation becomes an
application-layer guarantee, which needs enforcement — I'd put the `tenantId` filter in a repository
layer that no query can bypass, and I'd test that.

The cost side is what kills it: WiredTiger table count is a real resource, and beyond a few thousand
collections the operational characteristics degrade in ways that are hard to reverse — you can't
easily merge 5 000 collections back into one on a live system.

Where it flips: if you have _tens_ of tenants and they're large with genuinely different access
patterns, collection-per-tenant is defensible. If you have thousands and they're small, it isn't. And
if the driver is data residency or hard isolation, the right mechanism is a **cluster** per tenant
tier or sharding **zones**, not a collection per tenant — those give you real physical separation,
which is what the requirement actually asked for.

---

**Q:** How does `$lookup` differ from a SQL join?

**L4 answer** — `$lookup` is an aggregation pipeline stage, not a planner-integrated join. It
executes as a lookup into the foreign collection for each input document, using the foreign
collection's index — so an N-document input does N lookups. There's no hash join or merge join
strategy, no join reordering, and the planner doesn't push predicates across the boundary the way a
relational optimizer does. Fine for small N, poor for large N.

**L5 answer** — Plus the design implication, which is the point of the question. Because join cost is
linear in input cardinality with no better strategy available, you cannot recover from an
over-normalized schema at query time the way you can in PostgreSQL. In a relational database, a
normalized schema plus a good optimizer is often the right default; in MongoDB, normalization is a
decision you pay for on every read, forever.

So the modeling rule inverts: model from access patterns, and accept duplication as the price of read
performance. If you find yourself writing a three-stage `$lookup` pipeline on a hot path, that's not a
query to optimize, it's a schema to change — either denormalize with an extended reference, or
precompute the joined shape with the computed pattern on write.

The version caveats matter too: `$lookup` gained `let`/sub-pipeline support in 3.6 (which lets you
filter inside the lookup rather than after), and behaviour on sharded foreign collections has changed
across versions. So "does `$lookup` work on sharded collections" is a version-specific question and
I'd check rather than assert.

#### L5-Only Questions

**Q:** Design the schema for a financial instrument reference-data platform: ~30 000 instruments
ingested daily from a vendor, 150+ attributes, attributes vary by instrument type, downstream
services need search by several attributes, and there's an audit requirement to know what changed and
when.

**L5 answer** — Four decisions, in order of how expensive they are to reverse.

**1. One collection or one per instrument type?** One collection, with an `instrumentType`
discriminator. Type-varying attributes are exactly what the document model exists for, and downstream
search across types (which is the stated requirement) would otherwise be a fan-out across
collections. I'd use a `$jsonSchema` validator with `oneOf` branching on `instrumentType` so each
type's required attributes are enforced — that recovers the type safety a per-type collection would
have given, without the query cost.

**2. Current state and history: same document or separate?** Separate collections. Current state in
`instruments`, immutable change records in `instrument_versions`. The reason is cache footprint: an
instrument with three years of daily changes embedded is a large document pulled through cache on
every read of the current state, which is the hot path. Also, `$push` onto an embedded history array
is unbounded growth, which is the 16 MB wall.

The audit collection is append-only with `{instrumentId, validFrom, changedFields, source, batchId}`.
I'd store the _delta_, not a full snapshot, unless the compliance requirement specifically demands
point-in-time reconstruction without replay — worth asking, because full snapshots are much larger
and the answer changes the design.

**3. How do downstream services search?** This is where I'd push back on keeping it in MongoDB.
"Search by several of 150+ attributes" is a combinatorial index problem — you cannot build compound
indexes for arbitrary combinations, and a wildcard index gives up sort support and is
planner-conservative. My design would be: MongoDB as the system of record with indexes on the 4–6
attributes that dominate real traffic (measured, not assumed), and a **projection into a search
engine** (OpenSearch/Atlas Search) for the ad-hoc multi-attribute case, fed by a **change stream** —
which is majority-committed by construction and therefore can't project a rolled-back write (§3.2).
That's a real architectural cost, so I'd only take it once the query-shape analysis shows the tail is
genuinely arbitrary rather than four shapes in a trench coat.

**4. Ingest idempotence.** 30 000/day from a vendor means retries and redelivery. The write should be
an upsert keyed by the vendor's natural identifier plus a version/asOf, so a redelivered batch
converges rather than duplicating — no transaction needed, single-document atomicity does it. I'd
make the audit write and the current-state write a transaction _only_ if the audit record is a
compliance artifact that must not diverge; otherwise change streams give you the audit trail for free
and remove the transaction entirely.

The biggest risk I'd flag: 150+ attributes with type-varying shape drifts. Without a validator and a
contract test against the vendor's schema, in eighteen months you'll have four generations of shape in
the collection and no index will cover reliably. That's a process guardrail, not a schema one, and
it's the one that actually decides whether this design survives.

---

**Q:** You inherit a MongoDB collection with 400 M documents averaging 8 KB, 11 indexes, and a p99
that has doubled in six months with no code changes. Give me your first week.

**L5 answer** — 3.2 TB of documents plus indexes on top. The "no code changes" detail is the most
informative thing in the question: it means the cause is a change in _data_, not in queries — growth
crossing a threshold. That immediately makes cache residency the leading hypothesis, and I'd try to
confirm or kill it in the first hour rather than starting a broad investigation.

**Day 1 — is it cache?** `wiredTiger.cache["bytes read into cache"]` rate at steady state, plus
`pages evicted by application threads`. If reads are missing cache, everything else is secondary: the
working set has outgrown RAM and every FETCH is a disk read. The confirming signal is that latency
degraded _smoothly with data growth_ rather than stepping. If confirmed, the immediate mitigations are
scale up (fastest, reversible) and check whether index size is the problem rather than document size
— with 11 indexes that's plausible, and dropping indexes is cheaper than adding RAM.

**Day 1–2 — what's actually hot?** Profiler at a sampled rate, aggregated by query shape, with
`keysExamined/docsExamined/nReturned` per shape. I want to know which shapes are the volume, which are
the latency, and whether the two overlap. Simultaneously `$indexStats` snapshotted to a time series
(not read once — the counters reset on restart).

**Day 2–3 — the archive question.** 400 M documents in a collection that grew steadily almost always
means cold data. If 70% of documents haven't been read in 90 days, moving them out shrinks the working
set by more than any tuning will, and it's the highest-leverage change available. I'd quantify it
before proposing it — a `createdAt` distribution plus the access pattern from the profiler. Archive
target depends on whether the cold data must remain queryable: a separate collection if occasionally,
S3 + Athena if rarely (that access pattern is exactly what per-TB-scanned pricing is good at — see the
comparison doc).

**Day 3–4 — index consolidation.** With `$indexStats` in hand, `hideIndex()` the candidates rather
than dropping them, so rollback is instant rather than a multi-hour rebuild on a 3.2 TB collection.
Measure write latency and replication lag before/after, since 11 indexes means every insert is 12 B+
tree writes and that's likely also contributing.

**Day 5 — write it down and set the guardrails.** Document-size histogram alert, cache-read-rate
alert, oplog window in seconds, and a per-shape `keysExamined/nReturned` dashboard. The reason to do
this in week one rather than later is that the next regression will also be gradual and invisible, and
the only thing that catches gradual is a trend line someone is looking at.

What I'd resist for at least the first week: sharding. It's the intervention people reach for at this
size, it's a one-way door, and three of the four likely causes above (cache, cold data, index count)
are cheaper and reversible. I'd want to have failed at those first, with numbers, before proposing it.

---

## Deliberately Deferred

These sections are not covered above. They're lower-yield for an SDE II / L4 loop and I'd add them in
a second pass rather than dilute the ones that matter:

| Topic                                                                                           | Why deferred                                             | When to add                           |
| ----------------------------------------------------------------------------------------------- | -------------------------------------------------------- | ------------------------------------- |
| Aggregation framework internals (`$group`/`$sort` spilling, SBE pipeline compilation, `$facet`) | Asked as query-writing, rarely as internals              | Before a data-platform-flavoured loop |
| Change streams (resume tokens, oplog dependency, `startAtOperationTime`)                        | Referenced in §3.2 and §6.1; deserves its own subsection | If the JD mentions event-driven / CDC |
| Time-series collections (5.0+) — bucketing, columnar internals                                  | Genuinely relevant to a Glue/telemetry background        | Before a time-series-heavy interview  |
| Atlas Search / Lucene integration                                                               | Product-specific                                         | Only if the JD names Atlas            |
| Security: SCRAM, x.509, client-side field-level encryption, queryable encryption                | Rarely asked at L4, common in bank interviews            | Before a financial-services loop      |
| Backup/restore: `mongodump` vs filesystem snapshot vs PITR                                      | Ops-flavoured                                            | Before an SRE-adjacent loop           |

---

## References

1. **`mongodb/mongo`** — https://github.com/mongodb/mongo — `src/mongo/db/query/` for the planner and
   plan cache; `src/mongo/db/repl/` for elections and rollback. Reading `plan_ranker.cpp` is the
   fastest way to make §2.2 concrete.
2. **`wiredtiger/wiredtiger`** — https://github.com/wiredtiger/wiredtiger — `src/btree/`, `src/evict/`,
   `src/txn/`. The eviction and reconciliation code is where §1.2 stops being hand-wavy.
3. **MongoDB Manual** — https://www.mongodb.com/docs/manual/ — specifically Limits & Thresholds,
   Replication, Sharding, Transactions, and the ESR rule under Performance Best Practices. This is the
   source for every number in this document.
4. **MongoDB "Building with Patterns"** —
   https://www.mongodb.com/blog/post/building-with-patterns-a-summary — the vendor's own schema
   pattern catalogue (bucket, subset, extended reference, computed, outlier). §6.1 is a compressed
   version of this with the tradeoffs made explicit.
5. **"Tunable Consistency in MongoDB" (VLDB 2019)** — the paper behind §3.2; read it for why write
   concern and read concern are orthogonal and what majority-commit actually costs.
6. **Kleppmann, _Designing Data-Intensive Applications_, ch. 7** — the authoritative treatment of
   snapshot isolation vs serializability and write skew, which is what §5.1 is built on.
