# NoSQL Schema Design — Principles, Patterns, and the Interview Method

> Scope: how to design data models for **DynamoDB**, **MongoDB**, **Cassandra/wide-column**, and **Redis** when an interviewer says "design the schema" or "which store, and why." Relational design lives in `knowledge/relational-schema-design.md`; this file is the mirror image. Numbers are anchored to official docs (`DynamoDB docs, 2026-01` etc.) or hedged as order of magnitude.

## INDEX

1. [Foundations](#1-foundations)
   1.1 [Query-First Modeling (the paradigm shift)](#11-query-first-modeling)
   1.2 [Partition Key Design & Hot Partitions](#12-partition-key-design--hot-partitions)
   1.3 [Embed vs. Reference (denormalization discipline)](#13-embed-vs-reference)
2. [Store-Specific Patterns](#2-store-specific-patterns)
   2.1 [DynamoDB Single-Table Design](#21-dynamodb-single-table-design)
   2.2 [MongoDB Document Patterns](#22-mongodb-document-patterns)
   2.3 [Cassandra / Wide-Column & Time-Series](#23-cassandra--wide-column--time-series)
   2.4 [Redis as a Data Model (not just a cache)](#24-redis-as-a-data-model)
3. [Correctness & Evolution](#3-correctness--evolution)
   3.1 [Consistency, Conditional Writes & Transactions](#31-consistency-conditional-writes--transactions)
   3.2 [Schema Evolution Without a Schema](#32-schema-evolution-without-a-schema)
   3.3 [The Interview Method (8 steps)](#33-the-interview-method)
4. [References](#4-references)

---

## 1. Foundations

```
 Relational:  Entities → Normalize → Tables → Indexes → (queries come later)
 NoSQL:       Queries  → Access patterns → Keys → Items/Docs → (entities are implied)
                 ▲ the arrow is reversed; everything else follows from this
```

### 1.1 Query-First Modeling

```
  Access pattern list          Key schema             Item shape
  ┌─────────────────────┐      ┌───────────┐          ┌──────────────────┐
  │ AP1 get order by id │ ──▶  │ PK / SK   │  ──▶     │ denormalized doc │
  │ AP2 orders by cust  │      │ GSI1      │          │ (dup is fine)    │
  │ AP3 items in order  │      │ ...       │          └──────────────────┘
  └─────────────────────┘      └───────────┘
```

#### Concept

- **What it is** — you enumerate every read and write the application will make _before_ choosing keys, then shape the data so each access pattern is one key lookup or one contiguous range read.
  → In relational design the schema is derived from the domain and queries are answered later by the planner + joins. In NoSQL there is no planner and (usually) no join, so the query _is_ the schema.
  → 🗣 "In NoSQL I design the table for the queries, not for the entities — the entities are a byproduct."
- **What problem it solves** — predictable latency at any table size.
  → A key lookup on a partitioned store costs the same at 1 GB and 10 TB; a relational join's cost grows with data and index depth and depends on the planner's mood.
  ◆ Defeater: the price is that an _unanticipated_ access pattern is a schema change (new GSI, backfill, or scan), not a new `WHERE` clause.
- **What it replaced** — normalized 3NF + ad-hoc SQL for workloads where (a) write volume exceeded a single primary, (b) latency SLOs were tighter than a multi-join plan could hold, or (c) the shape of records varied per row.
  → Prior art insufficiency was specific: vertical scaling of the primary hit a wall; sharding a relational DB by hand pushes the join problem into application code anyway.
- **What it works with** — sits behind an API layer that owns the access-pattern list; composes with an event stream (DynamoDB Streams, MongoDB change streams, CDC) to feed derived stores (OpenSearch, analytics). Conflicts with "let analysts run arbitrary queries" — that goes to a warehouse via CDC, never to the OLTP NoSQL table.
- **Place in the world** — every large consumer backend (Amazon retail on DynamoDB, Netflix on Cassandra, most SaaS on MongoDB). Wrong answer for: reporting/BI, workloads with many-way joins on unknown filters, and anything where the access patterns are unknown at design time (an early-stage product with a pivoting UI is often better on Postgres).

#### Architecture & Core Components

```
 [Access-pattern registry] ─▶ [Key schema] ─▶ [Item/doc layout] ─▶ [Secondary indexes]
         (doc/spreadsheet)      (PK,SK,GSIs)     (denormalized)       (each = 1 more AP)
```

- **Access-pattern registry** — the artifact; single responsibility: be the exhaustive list of operations with expected cardinality and frequency.
- **Key schema** — maps each read AP to a `(partition, range)` pair.
- **Item layout** — decides what is duplicated so each AP is a single request.
- **Secondary indexes** — cover APs the primary key cannot; each one is a write amplification decision.

#### How Each Component Works

**Access-pattern registry**

- Data structure: a table `AP# | Operation | Key inputs | Expected result size | Frequency (r/s) | Consistency need`.
- Lifecycle: written before the first item; updated on every feature; reviewed when an index is added.
- Protocol: an AP with no key inputs is a scan — flag it; either add an index or move it to the analytics path.

**Key schema**

- Algorithm: for each AP, ask "what do I _have_ when I make this call?" That value (or a composite of it) becomes the partition key; what I want _ordered by_ becomes the sort key.
- State owned: none at runtime — it's a design artifact realized as table/GSI definitions in Terraform.

**Item layout**

- Algorithm: for every read AP, mark which attributes it needs; any attribute needed by a read AP on a different key gets duplicated into that item.
- Failure branch: duplicated attributes need a write fan-out (transaction or stream-driven updater) or an accepted staleness window.

**Secondary indexes**

- DynamoDB GSI: an async, eventually consistent copy of a projection keyed differently (`DynamoDB docs, 2026-01`: GSI reads are eventually consistent only; LSI supports strong reads but shares the base partition key and a 10 GB per-partition-key limit).
- MongoDB index: B-tree on the same document, strongly consistent, but every index is written synchronously on each insert/update.

#### Design Decisions, Tradeoffs & Best Practices

- Designers' decision: push join cost to write time (denormalize) so read time is O(1). Rejected alternative: server-side joins, because they are unbounded in a partitioned system.
- Your decisions: how many APs to cover with the primary key vs. GSIs (deciding variable: read/write ratio — write-heavy tables tolerate fewer indexes); how much staleness a duplicated field can carry (deciding variable: cost of a user seeing the old value).

| Option                    | Buys you                 | Costs you                                        | Choose when                                  |
| ------------------------- | ------------------------ | ------------------------------------------------ | -------------------------------------------- |
| Denormalize into one item | 1 read per AP            | write fan-out, size limits                       | read-heavy, bounded child cardinality        |
| Reference + second read   | no duplication           | 2 round trips, N+1 risk                          | unbounded children, frequently updated child |
| Add GSI/secondary index   | new AP without migration | write amplification, eventual staleness (Dynamo) | AP is frequent and cannot be served by PK    |
| Scan + filter             | zero design work         | O(table) cost, throttles neighbors               | never in the hot path; ok for one-off ops    |

- Best practices:
  - Write the AP registry before any key. Prevents: discovering AP7 in week 3 and needing a table rebuild.
  - Every AP must be answered by ≤ 1 request in the hot path. Prevents: N+1 fan-out that turns a 5 ms page into 500 ms.
  - Record the _frequency_ per AP. Prevents: building a GSI (paid on every write) for a report that runs once a day.

#### Failure Modes, Exception Handling & Production Issues

| Failure                  | Trigger                                      | Blast radius                                    | Detection signal                                                         | Mitigation                                                           |
| ------------------------ | -------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------ | -------------------------------------------------------------------- |
| Uncovered access pattern | new feature needs a filter not in any key    | feature ships as a scan → throttles whole table | `ScannedCount ≫ Count`, consumed capacity spike                          | add GSI + backfill; or CDC to search/analytics store                 |
| Stale duplicate          | denormalized field updated in one place only | users see inconsistent values                   | reconciliation job diff count > 0                                        | stream-driven updater or transaction; or stop duplicating that field |
| Item bloat               | unbounded list embedded                      | writes fail at size cap                         | `ValidationException: Item size` (Dynamo) / `BSONObjectTooLarge` (Mongo) | move children to their own items keyed by parent                     |

- Exception handling: size-limit errors are terminal (retry cannot fix); throttling (`ProvisionedThroughputExceededException`) is retryable with backoff; conditional-check failures are business signals, not errors.
- Canonical failure pattern (not a specific incident): a team ports a normalized schema table-per-entity onto DynamoDB, then implements joins in Lambda; p99 climbs with each new entity; fix is re-modeling around APs and collapsing into one table with composite keys; guardrail is the AP registry as a required design-review artifact.

#### Interview Questions

**Q:** How do you start designing a NoSQL schema?

**L4 answer** — List every access pattern (reads and writes) with inputs, result size, and frequency. Pick a partition key from what the caller _has_ and a sort key from what they want ordered/ranged. Denormalize so each hot-path AP is one request. Add secondary indexes only for APs the primary key can't serve.

**L5 answer** — Same, plus: classify APs by consistency need (which must read-your-writes, which can be stale), because in DynamoDB that decides GSI vs. base table; estimate write amplification per index against the read/write ratio; and mark which APs are analytics in disguise and route them via CDC to a warehouse rather than pretending the OLTP table can serve them. State up front which future AP would force a migration, so the interviewer knows you see the one-way door.

**Q:** Why can't I just normalize like in SQL?

**L4 answer** — There is no join across partitions, so normalized data means N round trips per page. The store scales by making each request touch one partition; normalization defeats that.

**L5 answer** — Also: normalization protects update anomalies; NoSQL trades that protection for read locality, so you must replace it with either transactional multi-item writes (bounded, Dynamo ≤ 100 items) or an asynchronous updater plus a reconciliation job. If the duplicated field changes often and is read rarely, normalization _is_ still the right call within NoSQL — the rule is "duplicate what's read-hot and write-cold."

**Q:** When is NoSQL the wrong choice?

**L4 answer** — Unknown or ad-hoc query patterns, heavy multi-entity reporting, strong multi-row invariants across many entities, small data that fits one Postgres.

**L5 answer** — Also: when the team's velocity depends on schema flexibility at the _query_ layer rather than the _storage_ layer (Postgres + JSONB gives per-row flexibility and a planner). And when the write rate is under ~10k/s and the dataset under ~1 TB — order of magnitude where a single well-tuned Postgres primary with read replicas is boring and sufficient; NoSQL's operational and modeling cost isn't paid back.

**Q:** How do you handle a query you didn't plan for?

**L4 answer** — If frequent: add a GSI/secondary index and backfill. If rare: scan off-peak or serve from an analytics replica.

**L5 answer** — Decide by frequency × latency need. Frequent + low latency → new index, with a backfill plan that tolerates the index being incomplete (GSI backfill is not atomic; reads during backfill miss items). Infrequent → CDC into OpenSearch/warehouse; never add a GSI whose only consumer is a weekly job because you pay its write cost on every item forever.

#### L5-Only Questions

**Q:** How do you decide the boundary between what the NoSQL table serves and what goes to a search/analytics store?

Any AP with unbounded filters, free text, or aggregation over > one partition goes out via the change stream. Keep in the OLTP table only APs that are key-addressable with a bounded result. The deciding variable is whether the AP can be expressed as `partition = X AND sort BETWEEN a AND b`. The cost is eventual consistency on the derived store (stream lag; DynamoDB Streams retains 24 h, `DynamoDB docs, 2026-01`) — state the SLO for that lag and monitor it.

**Q:** What's the review checklist you'd enforce on a team's NoSQL design doc?

AP registry complete with frequencies; every hot AP ≤ 1 request; partition key cardinality estimate and hot-key analysis; per-index write amplification; item size bound with growth assumption; staleness budget for every duplicated attribute; migration story for the two most likely future APs; and the cost line (WCU/RCU or cluster size) at target scale.

---

### 1.2 Partition Key Design & Hot Partitions

```
   hash(PK) ─▶ partition A [■■■■■■■■■■] 1000 WCU/3000 RCU cap each (DynamoDB)
              partition B [■■        ]
              partition C [■         ]   ← imbalance = throttling on A, waste on B,C
```

#### Concept

- **What it is** — the partition key determines which physical shard holds an item; good design spreads load evenly _across time and across keys_.
  → Every partitioned store (DynamoDB, Cassandra, MongoDB sharded, Kafka) has the same rule: throughput is per-partition, so the hottest key bounds the system.
- **What problem it solves** — horizontal scale without coordination: the router hashes the key and goes to one node.
  ◆ Defeater: scale is only linear if keys are uniform. One celebrity user, one "today" bucket, one tenant = one partition = one node's ceiling.
- **What it replaced** — manual application-level sharding and single-primary vertical scaling.
- **What it works with** — hash-based routing (DynamoDB, Cassandra, Mongo hashed shard key) or range-based routing (Mongo ranged shard key, HBase); adaptive capacity (DynamoDB) partially masks skew but does not remove the per-partition ceiling.
- **Place in the world** — the #1 source of NoSQL production incidents. Wrong answer to: data with an inherently monotonic key you _must_ range-scan globally (use a bucket prefix or a different store).

#### Architecture & Core Components

```
 Client ─▶ Router (hash(PK) → partition) ─▶ Partition (own storage + throughput ceiling)
                                              │
                                        [adaptive capacity / rebalancer — control plane]
```

- **Router** — maps key → partition; stateless.
- **Partition** — owns a key range; enforces the throughput ceiling.
- **Rebalancer** — splits hot partitions over minutes, not milliseconds.

#### How Each Component Works

**Router** — consistent hashing (Cassandra token ring, Murmur3) or internal hash (DynamoDB). Input: partition key bytes. Output: node/partition id. No state beyond the ring map.

**Partition** — DynamoDB: each partition serves up to 3,000 RCU and 1,000 WCU per second and holds ≤ 10 GB (`DynamoDB docs, 2026-01`). Cassandra: recommended partition size order of magnitude ≤ 100 MB / ≤ 100k rows (community guidance, not a hard limit; large partitions degrade compaction and repair).

**Rebalancer** — DynamoDB adaptive capacity boosts a hot partition instantly up to the _table's_ remaining capacity and splits a persistently hot partition in the background (`DynamoDB docs, 2026-01`); it cannot split a _single_ hot key — that key stays capped at 1,000 WCU/s.

#### Design Decisions, Tradeoffs & Best Practices

- Designers' decision: hash the key (uniformity) over range the key (locality). Rejected: global ordering, because it centralizes writes on the tail.
- Your decisions: which attribute becomes PK (deciding variable: cardinality ≥ 10× partition count and even access distribution); whether to add a write shard suffix (deciding variable: any single key expected > ~1,000 writes/s).

| Option                                         | Buys you                           | Costs you                         | Choose when                                 |
| ---------------------------------------------- | ---------------------------------- | --------------------------------- | ------------------------------------------- |
| Natural high-cardinality key (userId, orderId) | even spread, simple                | none                              | default                                     |
| Composite key (tenantId#userId)                | tenant grouping for range reads    | big tenants become hot            | tenants are similar in size                 |
| Write sharding (key#0..N)                      | breaks hot key across N partitions | N parallel reads to reassemble    | counters, "today" buckets, celebrity fan-in |
| Time bucket in key (device#2026-08)            | bounded partition growth           | cross-bucket reads at month edges | time-series appends                         |

- Best practices:
  - Never use a low-cardinality or monotonic attribute (status, date, auto-increment) as the whole PK. Prevents: one hot partition absorbing 100% of writes.
  - Estimate the top-1 key's write rate at peak; if > ~1,000/s (Dynamo) shard it with a random or calculated suffix. Prevents: throttling that adaptive capacity cannot fix.
  - Bucket time-series by a period sized so a bucket stays under the size cap. Prevents: a partition growing forever until compaction/repair fails.

#### Failure Modes, Exception Handling & Production Issues

| Failure                     | Trigger                          | Blast radius                                                   | Detection signal                                                      | Mitigation                       |
| --------------------------- | -------------------------------- | -------------------------------------------------------------- | --------------------------------------------------------------------- | -------------------------------- |
| Hot key                     | one key > partition ceiling      | that key's users throttled; neighbors ok after adaptive split  | `ThrottledRequests` with flat `ConsumedCapacity` well under table max | write sharding; cache hot reads  |
| Hot partition (skewed hash) | many mid-hot keys land together  | throttling despite spare table capacity                        | CloudWatch Contributor Insights top keys                              | adaptive capacity (auto), re-key |
| Large partition             | unbounded append to one PK       | Cassandra compaction/repair stalls; Dynamo 10 GB LSI limit hit | partition size metrics, `nodetool tablestats` max partition           | time/size bucketing              |
| Sequential key scan-write   | batch loader writes ordered keys | one partition at a time saturates                              | write throughput far below provisioned                                | randomize load order             |

- Exception handling: throttle exceptions are retryable with exponential backoff + jitter; SDKs retry by default — which _hides_ skew as latency. Alert on retry count, not only errors.
- Cited pattern: AWS's own "Best practices for partition keys" doc documents the sharding approaches above and the adaptive-capacity limits (`DynamoDB docs, 2026-01`). Canonical failure pattern (not a specific incident): a leaderboard keyed on `gameId` with one viral game → single partition throttles at 1,000 WCU/s while the table has 40,000 WCU provisioned; fix is `gameId#shard` with shard = `hash(userId) % 16`; guardrail is a design-review rule requiring a top-key write estimate.

#### Interview Questions

**Q:** How do you choose a partition key?

**L4 answer** — High cardinality, evenly accessed, and something the caller has at request time. Avoid status/date/tenant as the sole key.

**L5 answer** — Also quantify: cardinality relative to partition count, and the top key's expected peak rate against the per-partition ceiling. Distinguish _storage_ skew (a big tenant) from _throughput_ skew (a viral key) — bucketing fixes the first, sharding the second. And note that adaptive capacity changes the calculus: mild skew across keys is now tolerated; a single hot key is still not.

**Q:** Your table is throttling but consumed capacity is far below provisioned. What's happening?

**L4 answer** — A hot partition or hot key: one partition hit its per-partition ceiling while others idle. Find the top keys (Contributor Insights) and shard or cache them.

**L5 answer** — Also check whether it's a GSI throttling and backpressuring the base table (GSI capacity is separate and a throttled GSI throttles base-table writes), and whether the SDK's retries are masking it as latency. Fix order: cache reads for that key today, add write sharding for that entity type tomorrow, and add a top-key estimate to the design template so it doesn't recur.

**Q:** How do you store time-series data without a hot partition?

**L4 answer** — Put a time bucket in the partition key (`device#2026-08-28`) and the timestamp in the sort key. Queries for a window read one or a few buckets.

**L5 answer** — Size the bucket so the largest device's bucket stays under the partition cap and so the common query window spans ≤ 2–3 buckets. Newest bucket is still hot if devices are few and chatty — add a shard suffix then. Set TTL on old buckets (DynamoDB TTL deletes are free of WCU, `DynamoDB docs, 2026-01`) and route historical analysis to S3 via Streams.

**Q:** What's the difference between a hot key and a hot partition?

**L4 answer** — Hot key: one item/key exceeds the ceiling. Hot partition: several keys hashed together exceed it. Sharding fixes the first; the store's rebalancer fixes the second.

**L5 answer** — The distinction decides the fix: adaptive capacity/splits solve hot partitions automatically within minutes; nothing server-side solves a hot key because a key can't be split. Design must assume a hot key can appear at any time from user behavior, so entity types with fan-in (counters, popular parents) get sharded at design time.

#### L5-Only Questions

**Q:** Design write sharding for a global counter and explain the read cost.

Key `counter#<name>#<shard>`, shard = random 0..N-1 on write (uniform) or `hash(userId) % N` (deterministic, lets you read a user's own contribution). Read = N parallel `GetItem`s summed, or a periodic aggregator writes `counter#<name>#total` with acceptable staleness. N is chosen from peak write rate ÷ ~1,000; the read cost is N× RCU, so N is the smallest that clears the ceiling. Defeater: N is fixed in the key — changing it needs a re-key of existing items or a versioned prefix.

**Q:** What differs between DynamoDB and Cassandra partition sizing concerns?

DynamoDB caps at 10 GB per partition (and per LSI collection) and enforces throughput caps per partition; oversize is a hard error path. Cassandra has no hard cap but large partitions inflate compaction, repair, and read latency; the failure is gradual and shows up as GC pressure and tombstone-heavy reads. So on DynamoDB you bucket for _throughput_; on Cassandra you bucket for _partition size_ and tombstone hygiene.

---

### 1.3 Embed vs. Reference

```
  EMBED                              REFERENCE
  { order: {..., items:[{},{}]} }    { order: {...} }   { item: {orderId,...} }
   1 read, dup risk, size cap         2 reads, no dup, unbounded children ok
```

#### Concept

- **What it is** — the choice, per relationship, of storing child data inside the parent record (embed) or as separate records keyed by the parent (reference/adjacency).
  → 🗣 "Embed what you read together and that's bounded; reference what's unbounded or updated independently."
- **What problem it solves** — the N+1 read problem in a store without joins.
  ◆ Defeater: embedding turns every child update into a parent rewrite (and in MongoDB, a document rewrite that can move the doc) — embed only write-cold children.
- **What it replaced** — foreign keys + joins. Foreign keys were insufficient because there is no cross-partition join and no referential integrity enforcement in these stores.
- **What it works with** — composite sort keys (DynamoDB "item collections"), MongoDB subdocuments/arrays, Cassandra clustering columns. Conflicts with: unbounded arrays, `$push` without a cap, many-to-many where both sides are large.
- **Place in the world** — every document model decision. Wrong answer to: an entity referenced from many parents (embedding it N times means N updates).

#### Architecture & Core Components

```
 Parent item ──(embed)── child subdoc / list           [one physical record]
 Parent item ──(ref)──── child item (PK=parent, SK=child#id)   [same partition, separate records]
 Parent item ──(ref)──── child item (PK=child)          [different partition; 2nd read]
```

- **Embedded child** — lives and dies with the parent.
- **Co-located reference** — separate item, same partition key; read together with one `Query`.
- **Remote reference** — separate partition; needs a second read or an index.

#### How Each Component Works

**Embedded child** — stored inline (BSON subdocument / DynamoDB map or list). Read cost 0 extra. Update cost: whole-document rewrite in Mongo if size grows past allocated space (WiredTiger rewrites the document; no in-place growth guarantee). Lifecycle: bounded by parent's size cap — 16 MB per BSON doc (`MongoDB docs, 2026-01`), 400 KB per DynamoDB item (`DynamoDB docs, 2026-01`).

**Co-located reference (item collection)** — DynamoDB: `PK=ORDER#123`, `SK=ITEM#001…`; one `Query(PK)` returns parent + children in sort order. Cassandra: same idea with clustering columns. State: each child is independently updatable; ordering by SK is free.

**Remote reference** — `SK` holds the foreign id; read requires a second `GetItem`/`BatchGetItem` (≤ 100 items per batch, `DynamoDB docs, 2026-01`) or a GSI keyed on the child that projects the parent attributes needed.

#### Design Decisions, Tradeoffs & Best Practices

- Designers' decision (Mongo): rich nested documents as the unit of atomicity — a single-document write is always atomic, which is why embedding is the _default_ recommendation there.
- Your decisions: embed vs. co-locate vs. remote per edge (deciding variables: child cardinality bound, child update frequency, whether child is read without parent).

| Option                                                   | Buys you                             | Costs you                                                 | Choose when                                       |
| -------------------------------------------------------- | ------------------------------------ | --------------------------------------------------------- | ------------------------------------------------- |
| Embed                                                    | 1 read, atomic parent+child write    | size cap, rewrite on child update, child unreadable alone | ≤ ~100 children, read with parent, rarely updated |
| Co-locate (same partition)                               | 1 Query, independent child writes    | partition grows with children                             | unbounded-ish children, need sort order           |
| Remote reference                                         | no dup, child shared by many parents | 2 reads / GSI                                             | many-to-many, child has its own lifecycle         |
| Extended reference (copy a few parent fields into child) | child readable alone with context    | staleness on those fields                                 | child listed in UIs without parent fetch          |

- Best practices:
  - Cap embedded arrays (Mongo `$push` with `$slice`; Dynamo list with app-side bound). Prevents: unbounded growth to the size cap and a write outage.
  - Embed only fields that change less often than the parent is read. Prevents: write amplification on hot children.
  - For many-to-many, store both directions as separate items/GSI, not embedded arrays on both sides. Prevents: double-write drift.

#### Failure Modes, Exception Handling & Production Issues

| Failure                     | Trigger                                        | Blast radius                         | Detection signal           | Mitigation                                           |
| --------------------------- | ---------------------------------------------- | ------------------------------------ | -------------------------- | ---------------------------------------------------- |
| Unbounded array             | `$push`/`list_append` without cap              | doc hits 16 MB / 400 KB, writes fail | doc size p99 trending up   | bucket pattern or co-locate                          |
| Read amplification          | remote refs in a list view                     | N+1 GetItems per page                | request count per page ≫ 1 | extended reference or GSI projection                 |
| Drift on extended reference | parent field changes, child copies not updated | stale names/prices shown             | reconciliation diff        | change-stream updater; or don't copy volatile fields |

- Exception handling: size errors are terminal — need remodel; missing referenced child is a data-integrity gap the app must handle (no FK) — treat as "deleted" and log.
- Canonical failure pattern (not a specific incident): comments embedded in a post document; a viral post's comment array crosses 16 MB and every new comment fails; fix is a comments collection keyed by `postId` with pagination; guardrail is the rule "embed only bounded cardinality" enforced at design review.

#### Interview Questions

**Q:** Embed or reference — how do you decide?

**L4 answer** — Embed when the child is bounded, read with the parent, and rarely updated alone. Reference when it's unbounded, shared, or independently updated.

**L5 answer** — Add the quantitative gates: cardinality bound vs. the store's size cap with 3–5 years of growth; child update rate vs. parent read rate (embed if update ≪ read); and whether any AP reads the child without the parent (then it needs its own key regardless). Mention that in DynamoDB "reference" usually means co-location under the same PK, which keeps the 1-request property — the embed/reference dichotomy is really a three-way choice there.

**Q:** How do you model one-to-many in DynamoDB?

**L4 answer** — Same partition key for parent and children, sort key prefix distinguishes types (`META`, `ITEM#…`). One `Query` fetches both; `begins_with(SK, 'ITEM#')` fetches only children.

**L5 answer** — Also handle the large-fan-out case: if children per parent can exceed the 10 GB partition or ~1,000 writes/s, split by time bucket in the SK or shard the PK. And note the read side: `Query` returns 1 MB per page — a parent with 50k children needs pagination and probably a summary item.

**Q:** How do you model many-to-many?

**L4 answer** — Adjacency list: an item for each edge in both directions (`PK=USER#u, SK=GROUP#g` and, via a GSI with keys swapped, `PK=GROUP#g, SK=USER#u`). One index serves the reverse direction.

**L5 answer** — Also decide what's projected on the edge (extended reference: name, role) versus fetched; the projected fields are the staleness budget. If edges have heavy attributes on both sides, keep the edge thin and batch-get the nodes (≤ 100 per batch). Point out that a GSI is eventually consistent, so "add user to group then list group members" can miss the new member for milliseconds–seconds; if the UI needs read-your-write, write both directions explicitly in a transaction instead of relying on the GSI.

**Q:** What's the MongoDB "subset" pattern?

**L4 answer** — Embed only the most recent/most-read N children (e.g., last 10 reviews) in the parent; keep the full set in another collection. Fast common read, bounded doc.

**L5 answer** — The cost is dual-write on every child insert (append to the subset, trim, and insert into the full collection) — do it in a transaction or accept that the subset lags. Choose N from the UI's first-page size. It's the document-store equivalent of a materialized "top-N" view.

#### L5-Only Questions

**Q:** A product is referenced by thousands of order line items and its name changes. Where does the name live?

Copy the name into the line item at order time _intentionally_ — it's a historical snapshot (what the customer bought), not a live reference. Store `productId` too. Do not propagate updates. This reframes "drift" as correct domain behavior; the defeater is fields that must be live (current price for a cart), which stay referenced.

**Q:** How do you page through 100k children of one parent without scanning?

Sort key is a monotonically increasing value (timestamp or ULID); use `Query` with `Limit` and `ExclusiveStartKey`; DynamoDB returns `LastEvaluatedKey`. If the children exceed a partition's size/throughput ceiling, bucket the SK and page bucket by bucket. Never offset-paginate — there is no offset in these stores.

---

## 2. Store-Specific Patterns

```
   DynamoDB   ──  single table, PK/SK overloading, GSIs           (key-value + wide-column)
   MongoDB    ──  rich documents, embed/subset/bucket, indexes     (document)
   Cassandra  ──  query-per-table, partition + clustering          (wide-column, write-optimized)
   Redis      ──  data structures as the schema                    (in-memory, ephemeral-ish)
```

### 2.1 DynamoDB Single-Table Design

```
  PK             SK              GSI1PK       GSI1SK        attrs…
  CUST#42        META            —            —             name, email
  CUST#42        ORDER#2026-08-01#o1  ORDER#o1  STATUS#PAID  total
  ORDER#o1       ITEM#001        —            —             sku, qty
  (one table; entity type encoded in key prefixes; GSIs re-key the same items)
```

#### Concept

- **What it is** — all entities live in one table; generic `PK`/`SK` attributes hold typed prefixes; GSIs with generic `GSI1PK/GSI1SK` overload those same attributes to serve other access patterns.
  → 🗣 "One table, one round trip per access pattern, indexes overloaded to serve the rest."
- **What problem it solves** — fetching a heterogeneous graph of related items (customer + orders + items) in one request by co-locating them under one partition key.
  ◆ Defeater: it's a _read-side_ optimization. It makes the table opaque, couples all entities' throughput and index limits (20 GSIs per table by default, `DynamoDB docs, 2026-01`), and makes analytics/export awkward. AWS itself now presents multi-table as legitimate when entities are unrelated (`DynamoDB docs, 2026-01`).
- **What it replaced** — table-per-entity with application-side joins.
- **What it works with** — DynamoDB Streams → Lambda for derived data; Terraform for table/GSI definitions; an application-layer repository that owns key construction. Conflicts with ORMs and with teams that expect to `SELECT * FROM orders`.
- **Place in the world** — serverless and high-scale AWS services. Wrong answer to: few, unrelated entities (use one table each), or an evolving domain where access patterns change weekly.

#### Architecture & Core Components

```
 [Key builder (app)] ─▶ [Base table PK/SK] ─▶ [Item collections (per PK)]
                            │
                            ├─▶ [GSI1 (overloaded)]  async, eventually consistent
                            └─▶ [Streams] ─▶ [Lambda] ─▶ derived views / OpenSearch
```

- **Key builder** — the only code that knows prefixes; single responsibility: turn (entityType, ids) into keys.
- **Base table** — strongly consistent reads available; primary AP surface.
- **GSI** — a re-keyed, projected copy; one extra AP each.
- **Streams** — ordered-per-key change log for fan-out.

#### How Each Component Works

**Key builder** — deterministic string concat with `#` separators and zero-padded/ISO-formatted sortable components; state: none; failure: a change in format is a data migration.

**Base table / item collection** — all items sharing a PK form an item collection stored contiguously by SK; `Query` reads a range in SK order; per-partition ceilings from §1.2 apply to the whole collection.

**GSI** — asynchronously replicated; sparse (items missing the GSI key attribute are excluded — used deliberately for "only open orders"); projection `KEYS_ONLY|INCLUDE|ALL` decides read cost vs. write/storage cost; own capacity; can be added after creation and backfilled.

**Streams** — 24 h retention, per-item ordering, at-least-once to consumers (`DynamoDB docs, 2026-01`); consumers must be idempotent.

#### Design Decisions, Tradeoffs & Best Practices

- Designers' decision: a fixed key schema with unlimited attribute flexibility — flexibility is in the value, rigidity is in the key.
- Your decisions: single vs. multi table (deciding variable: do entities get read together?); GSI projection (deciding variable: read attribute set vs. write cost); SK format (deciding variable: what ranges you need).

| Option          | Buys you                                | Costs you                                | Choose when                              |
| --------------- | --------------------------------------- | ---------------------------------------- | ---------------------------------------- |
| Single table    | 1 request for related graphs            | opacity, shared limits, harder analytics | related entities read together           |
| Multi table     | clarity, isolated capacity, easy export | joins in app                             | unrelated entities, or analytics-heavy   |
| GSI `KEYS_ONLY` | cheap writes/storage                    | second read for attrs                    | index used for existence/counting        |
| GSI `ALL`       | 1 read                                  | full write amplification                 | index is a hot read path                 |
| Sparse GSI      | free filtering by presence              | must manage attribute presence           | "active only", "unprocessed only" queues |

- Best practices:
  - Prefix every key with the entity type. Prevents: key collisions between entity types sharing a table.
  - Make SK components sortable (ISO-8601, zero-padded numbers, ULID). Prevents: lexical ordering bugs (`ORDER#10` before `ORDER#9`).
  - Put version/entity-type as attributes, not only in keys. Prevents: un-parseable items after a prefix format change.
  - Never `Scan` in the request path; filter expressions run _after_ the read and still cost full RCU. Prevents: paying for and throttling on data you discard.

#### Failure Modes, Exception Handling & Production Issues

| Failure                   | Trigger                               | Blast radius                     | Detection signal           | Mitigation                                               |
| ------------------------- | ------------------------------------- | -------------------------------- | -------------------------- | -------------------------------------------------------- |
| GSI throttle backpressure | GSI under-provisioned vs. base writes | base-table writes throttled      | GSI `WriteThrottleEvents`  | size GSI capacity ≥ base for `ALL` projection; on-demand |
| GSI stale read            | write then immediately query GSI      | missing/old item briefly         | user-visible flicker       | base-table read for read-your-write paths                |
| Hot item collection       | one parent's children dominate        | that PK throttles                | Contributor Insights       | shard or bucket SK; move hot child type out              |
| Key format change         | prefix scheme changed                 | all items unreadable by new code | 100% miss rate post-deploy | dual-read old/new; versioned key format                  |

- Exception handling: `ConditionalCheckFailedException` = business outcome (already exists/version mismatch), never retried blindly; `TransactionCanceledException` carries per-item reasons; throttles retried with backoff. Poison pill: a Streams consumer that throws on a malformed item blocks that shard until fixed — use a DLQ (Lambda `DestinationConfig`) and bisect batch on error.
- Canonical failure pattern (not a specific incident): a `STATUS` GSI (`GSI1PK=STATUS#PENDING`) accumulates millions of items under one partition value — the classic low-cardinality GSI hot partition; fix is `STATUS#PENDING#<shard>` or sparse-attribute + time bucket; guardrail is the cardinality check applied to GSI keys, not just base keys.

#### Interview Questions

**Q:** Walk me through a single-table design for customers, orders, and order items.

**L4 answer** — `PK=CUST#id, SK=META` for the customer; `PK=CUST#id, SK=ORDER#<iso date>#<orderId>` for orders (list orders by customer, newest last via `ScanIndexForward=false`); `PK=ORDER#id, SK=ITEM#<n>` for items. GSI1 with `GSI1PK=ORDER#id, GSI1SK=META` gets an order by id without the customer. Three requests max for the full graph; the common "order page" is one `Query`.

**L5 answer** — Also: put order `META` in the `ORDER#id` partition too (duplicate a summary) so the order page is exactly one `Query`; note the write is then a transaction of 2 items. State the hot-partition risk: a B2B customer with 1M orders — bucket the SK by month and accept multi-bucket pagination. Mention the sparse GSI for open orders (`GSI2PK=OPENORDER#<shard>`) and TTL on items you don't need after fulfillment. Give the WCU line: one order with 5 items ≈ 7 writes ≈ 7 WCU plus GSI `ALL` projection ×2.

**Q:** Single table or multiple tables?

**L4 answer** — Single when the entities are read together and you want one round trip; multiple when they're unrelated or when analytics/export simplicity matters more.

**L5 answer** — Also weigh operational coupling: one table means one set of GSI limits, one capacity pool, one backup, one blast radius. AWS's current guidance accepts multi-table for unrelated entities. My default: single table per bounded context, not per company.

**Q:** How do GSIs differ from LSIs?

**L4 answer** — LSI: same PK, different SK, strongly consistent reads, must exist at table creation, shares the 10 GB per-PK limit. GSI: any PK/SK, eventual consistency, own capacity, can be added later.

**L5 answer** — Practical rule: LSI is rarely worth the 10 GB item-collection cap; use it only when you need a strongly consistent alternate sort on a small collection. For everything else GSI, and design read-your-write paths to hit the base table. Note GSI backfill is async — a newly added GSI is unusable until `IndexStatus=ACTIVE` and even then early reads may be incomplete during backfill.

**Q:** How do you do a "list all orders with status=PENDING" query?

**L4 answer** — Sparse GSI: only pending orders carry `GSI2PK=PENDING`; query the GSI. On fulfillment, remove the attribute and the item leaves the index.

**L5 answer** — The single value `PENDING` is a hot partition at scale; shard it (`PENDING#<0..15>`) and query all shards in parallel, or bucket by created-date. If the consumer is a worker pool, this is a queue in disguise — consider SQS fed from Streams instead of polling a GSI.

#### L5-Only Questions

**Q:** Design the migration when a key prefix scheme must change.

Add `schemaVersion` attribute; deploy readers that accept both formats; write new items in the new format; run a Streams-driven or batch job that rewrites old items (write new, delete old, in a transaction per item); watch a "v1 items remaining" metric; remove the dual-read path when zero. Cost: 2× writes during migration; capacity must be raised. The defeater is any external system that stored raw keys (URLs, other tables) — inventory those first.

**Q:** How do you keep a derived OpenSearch index consistent with the table?

Streams → Lambda → bulk index, idempotent on `(pk, sk, version)`; ignore events older than the indexed version. Accept lag; expose `updatedAt` so UIs can show staleness. Reconciliation job nightly compares counts/hash per partition. If Streams lag exceeds SLO, degrade search to base-table lookups for the user's own recent writes.

---

### 2.2 MongoDB Document Patterns

```
   { _id, ...scalar, embedded:{...}, recent:[...N], v:3 }
        │              │              │             └ schema version
        │              │              └ subset / bucket (bounded array)
        │              └ embed (bounded, read-together)
        └ natural or ObjectId; shard key must be immutable
```

#### Concept

- **What it is** — the document model plus a catalog of named patterns (embed, subset, extended reference, bucket, outlier, computed, attribute, polymorphic, schema versioning) for shaping documents to access patterns.
  → 🗣 "Mongo's atomic unit is the document, so I model the write transaction boundary as the document boundary."
- **What problem it solves** — variable-shape records and read-together aggregates without joins, with per-document atomicity.
  ◆ Defeater: "schemaless" means the schema moved into application code; without JSON-schema validation and a version field, you get silent shape drift.
- **What it replaced** — EAV tables and wide sparse relational tables for variable attributes.
- **What it works with** — secondary indexes (B-tree, compound, multikey on arrays, text, TTL), change streams, aggregation pipeline (`$lookup` exists but is a per-shard join, not a substitute for design), sharding by an immutable key. Conflicts with: cross-document invariants at high frequency (multi-document transactions exist since 4.0 replica set / 4.2 sharded, `MongoDB docs, 2026-01`, but cost more and hold locks).
- **Place in the world** — catalogs, CMS, user profiles, event/IoT storage. Wrong answer to: ledger-style multi-row invariants, heavy analytics joins.

#### Architecture & Core Components

```
 [Collection] ─ documents ─ [indexes: _id, compound, multikey, TTL]
      │
      ├─ [validator: $jsonSchema]     control plane
      ├─ [shard key → chunks → shards] control plane
      └─ [change stream]              async
```

- **Document** — atomic write unit, ≤ 16 MB.
- **Index** — synchronous B-tree per index; multikey indexes fan out per array element.
- **Validator** — optional schema enforcement at write.
- **Shard key** — routes documents; immutable after insert (mutable only under conditions since 4.2).

#### How Each Component Works

**Document** — BSON; WiredTiger stores by `_id` with document-level concurrency; an update that grows the doc may rewrite it; arrays are ordered and indexable.

**Indexes** — B-tree; compound index order matters (ESR rule: Equality, Sort, Range fields in that order for the planner to use the index for both filter and sort, `MongoDB docs, 2026-01`); multikey index entry per array element — an array of 1,000 tags = 1,000 index entries per doc; TTL index deletes by a date field in a background thread (not instantaneous).

**Validator** — `$jsonSchema` evaluated on insert/update; `validationLevel: moderate` allows old docs to violate until touched — the migration-friendly setting.

**Shard key** — hashed (uniform, no range queries by key) or ranged (locality, monotonic keys create a hot chunk); chunks split/migrate by the balancer.

#### Design Decisions, Tradeoffs & Best Practices

| Pattern            | Buys you                                      | Costs you                 | Choose when                   |
| ------------------ | --------------------------------------------- | ------------------------- | ----------------------------- |
| Embed              | 1 read, atomic                                | size cap, rewrite         | bounded, read-together        |
| Subset             | fast first page, bounded doc                  | dual write                | top-N children                |
| Extended reference | avoid `$lookup` in lists                      | copy staleness            | list views need parent labels |
| Bucket             | bounded time-series docs, fewer index entries | bucket boundary logic     | IoT/events                    |
| Outlier            | normal docs stay small                        | `hasExtra` flag branching | rare huge parents             |
| Computed           | no aggregation on read                        | update on write           | counts/averages read often    |
| Attribute          | index arbitrary key/values                    | awkward queries           | sparse variable attributes    |
| Schema versioning  | safe evolution                                | reader branches           | any long-lived collection     |

- Best practices:
  - Always store `schemaVersion`. Prevents: undetectable mixed-shape collections after a migration is half done.
  - Bound every array (`$push` + `$slice`). Prevents: 16 MB failure and multikey index blow-up.
  - Choose shard key on cardinality + query locality + immutability. Prevents: scatter-gather on every query (bad key) or jumbo chunks (monotonic key).
  - Design compound indexes with ESR. Prevents: in-memory sorts that fail at the 100 MB sort limit (`MongoDB docs, 2026-01`; `allowDiskUse` is a mitigation, not a fix).

#### Failure Modes, Exception Handling & Production Issues

| Failure                  | Trigger                                           | Blast radius                         | Detection signal                            | Mitigation                               |
| ------------------------ | ------------------------------------------------- | ------------------------------------ | ------------------------------------------- | ---------------------------------------- |
| Multikey index explosion | large arrays indexed                              | write latency, index size ≫ data     | index size metric                           | attribute pattern or separate collection |
| Scatter-gather query     | query lacks shard key                             | every shard hit; p99 = slowest shard | `explain` shows `SHARD_MERGE` on all shards | include shard key or add targeted index  |
| Jumbo chunk              | monotonic ranged shard key or low-cardinality key | balancer can't move; one shard hot   | `sh.status()` jumbo flag                    | hashed key or compound key               |
| Document rewrite churn   | growing embedded arrays                           | write amplification, fragmentation   | doc size growth, page cache misses          | bucket/subset                            |

- Exception handling: `WriteConflict` in transactions is retryable (driver retries transiently); `DuplicateKey` is a business signal; document-too-large is terminal.
- Canonical failure pattern (not a specific incident): a `_id: ObjectId` ranged shard key — ObjectId is time-prefixed, so all inserts hit the last chunk; fix is `{ _id: "hashed" }` or a compound `{tenant, _id}`; guardrail is the "no monotonic ranged shard key" review rule (documented in MongoDB's shard-key docs).

#### Interview Questions

**Q:** Design a product catalog where products have different attributes per category.

**L4 answer** — One `products` collection, polymorphic documents with a `category` discriminator and a `specs` subdocument per category; JSON-schema validator per category if needed; index on `category` + common filter fields.

**L5 answer** — For filterable sparse attributes use the attribute pattern (`attrs: [{k:"screen", v:"6.1"}]`, index on `attrs.k, attrs.v`) instead of hundreds of sparse indexes. Bound the attribute array. Route faceted search to a search engine (Atlas Search/OpenSearch) via change streams rather than building facet counts on the OLTP collection. Store `schemaVersion` because specs evolve per category independently.

**Q:** When would you use `$lookup`?

**L4 answer** — Occasional joins for admin/reporting or low-volume paths; not in hot paths, since it's effectively a nested loop per document.

**L5 answer** — And on a sharded cluster `$lookup` against a sharded "from" collection is supported only in newer versions and still fans out. My rule: if a `$lookup` appears in a hot path, the model is wrong — apply extended reference or embed.

**Q:** How do you pick a shard key?

**L4 answer** — High cardinality, even distribution, present in most queries, and immutable. Hashed for uniform inserts, ranged for locality.

**L5 answer** — Also: compound keys (`{tenantId, createdAt}`) to get tenant locality without a hot chunk; check "does the top tenant exceed a shard?" (then hash within tenant). Say out loud that the key is a one-way door in practice — resharding exists (5.0+) but is expensive.

**Q:** How do multi-document transactions change your design?

**L4 answer** — They let you keep invariants across documents, but they're slower and hold locks; prefer designing so the invariant lives inside one document.

**L5 answer** — Use them for rare, bounded operations (transfer between two accounts). Avoid for high-frequency fan-out; transaction lifetime default 60 s (`transactionLifetimeLimitSeconds`, `MongoDB docs, 2026-01`) and write conflicts abort under contention. Design the hot path to single-document atomicity with `findOneAndUpdate` and version fields.

#### L5-Only Questions

**Q:** Migrate a collection from embedded comments to a separate collection with zero downtime.

Add `schemaVersion`; deploy readers that handle both (read embedded if present else query comments); deploy writers that write to the new collection only; run a background job that moves comments per post and sets `v=2`, using `findOneAndUpdate` with `v=1` condition to avoid racing writers; monitor `v=1` count → 0; remove dual-read. Defeater: a post updated concurrently by the migrator and a user — the conditional update loses and the migrator retries.

**Q:** Explain the bucket pattern's index economics.

Per-reading documents create one index entry per reading; bucketing 1 hour of readings into one document with `{sensorId, hourStart}` cuts index entries by the bucket size (e.g., 3,600×) and lets a 24-hour query hit 24 documents. Cost: writes become `$push` updates that grow the doc (bounded by the bucket), and a query for a 5-minute window over-fetches the hour. Choose bucket size so the doc stays well under 16 MB at peak rate and the common query spans few buckets.

---

### 2.3 Cassandra / Wide-Column & Time-Series

```
  TABLE events_by_device ( device_id, day, ts, payload,
      PRIMARY KEY ((device_id, day), ts) ) WITH CLUSTERING ORDER BY (ts DESC)
                          └ partition key      └ clustering column = on-disk order
```

#### Concept

- **What it is** — a write-optimized, masterless, partitioned store where each table is designed for exactly one query; the primary key = (partition key) + clustering columns that fix on-disk order within the partition.
  → 🗣 "In Cassandra, one query, one table — duplicate the data into as many tables as you have queries."
- **What problem it solves** — sustained high write throughput with linear scale and multi-DC replication.
  ◆ Defeater: reads that don't hit a partition + clustering prefix require `ALLOW FILTERING` = full scan; secondary indexes are local-per-node and scatter.
- **What it replaced** — sharded relational for append-heavy telemetry/timelines.
- **What it works with** — LSM storage (memtable → SSTables → compaction), tunable consistency (`ONE/QUORUM/ALL`), TTL per cell, materialized views (experimental-ish; many operators avoid), Kafka upstream. Conflicts with: read-modify-write patterns (no CAS except lightweight transactions, which are Paxos and ~4× cost), deletes at scale (tombstones).
- **Place in the world** — Netflix, Apple, Discord (messages, until they moved to ScyllaDB — public engineering post, Discord blog 2023). Wrong answer to: anything needing ad-hoc queries or frequent updates/deletes of the same row.

#### Architecture & Core Components

```
 Client ─▶ Coordinator ─▶ replicas (RF=3) ── memtable ─▶ SSTables ─▶ compaction [async]
                │                                    └ tombstones on delete/TTL
            token ring (Murmur3) [control plane]
```

- **Coordinator** — any node; routes by token, waits for consistency level.
- **Replica** — owns a token range copy; append-only writes.
- **Compaction** — merges SSTables, purges tombstones after `gc_grace_seconds`.

#### How Each Component Works

**Partition & clustering** — partition hashed to token; rows within partition stored sorted by clustering columns; range queries only on clustering prefix, only within one partition (or `IN` on a few partitions).

**Write path** — commit log + memtable, flush to immutable SSTable; no read-before-write, hence write speed; last-write-wins by cell timestamp (clock skew = data loss risk, order of magnitude ms).

**Tombstones** — deletes and TTL expiries write markers; reads scanning many tombstones get slow and abort past `tombstone_failure_threshold` (default 100,000, `Cassandra docs, 2026-01`).

#### Design Decisions, Tradeoffs & Best Practices

| Option                       | Buys you                       | Costs you                               | Choose when                |
| ---------------------------- | ------------------------------ | --------------------------------------- | -------------------------- |
| Time bucket in partition key | bounded partitions             | multi-partition reads at boundaries     | append streams             |
| Table per query              | O(1) reads                     | write fan-out ×N tables                 | ≥ 2 distinct query shapes  |
| Materialized view            | server-managed denormalization | consistency issues, operational caveats | rarely; prefer app-managed |
| `QUORUM` R+W                 | strong-ish read-your-write     | latency, less availability              | user-facing state          |
| `ONE`                        | speed                          | stale reads                             | metrics/logs               |

- Best practices:
  - Bound partitions by time or count (order of magnitude ≤ 100 MB). Prevents: compaction/repair stalls and heap pressure.
  - Avoid delete-heavy tables or use TTL + `TimeWindowCompactionStrategy` for time-series. Prevents: tombstone-scan timeouts.
  - Write to all query tables in a logged batch _only_ when they share a partition, else app-level fan-out with idempotent writes. Prevents: coordinator overload from large multi-partition batches.

#### Failure Modes, Exception Handling & Production Issues

| Failure           | Trigger                            | Blast radius                    | Detection signal                          | Mitigation                              |
| ----------------- | ---------------------------------- | ------------------------------- | ----------------------------------------- | --------------------------------------- |
| Tombstone storm   | mass delete/expiry then range read | read timeouts on that table     | `TombstoneOverwhelmingException` warnings | TWCS, smaller partitions, avoid deletes |
| Wide partition    | unbounded clustering rows          | repair/compaction slow, node GC | max partition size metric                 | bucket                                  |
| Clock skew LWW    | node clocks drift                  | silently lost updates           | none direct — reconcile                   | NTP, client timestamps                  |
| Read repair storm | inconsistent replicas + many reads | latency                         | read repair metrics                       | run repairs on schedule                 |

- Exception handling: `WriteTimeout` may still have written (not idempotent-safe unless the write is naturally idempotent); `Unavailable` is retryable when nodes return. Poison pill: a single giant partition read that times out repeatedly.
- Cited: Discord's 2023 post on migrating trillions of messages describes hot-partition and GC pain from large channels and bucketing by `(channel_id, bucket)`; that bucketing scheme is the reference design for chat timelines.

#### Interview Questions

**Q:** Model a device telemetry table for "last 24 h of readings for a device."

**L4 answer** — `PRIMARY KEY ((device_id, day), ts)` with `CLUSTERING ORDER BY (ts DESC)`; read today's and yesterday's partitions; TTL on cells.

**L5 answer** — Choose the bucket from write rate: 1 reading/s → 86,400 rows/day, fine; 100/s → hourly buckets. Use TWCS so expired buckets drop as whole SSTables without tombstone scans. State the multi-partition read cost at day boundaries and that a "latest reading" lookup should be a separate small table (`latest_by_device`) to avoid touching the wide one.

**Q:** Why is there no join, and how do you cope?

**L4 answer** — Joins would need cross-node coordination that kills the linear-scale property. You denormalize: one table per query and write to all of them.

**L5 answer** — Also: keep the fan-out idempotent and ordered per key by driving it from a single producer (or Kafka) so partial failures can be replayed; reconcile with a periodic job. Don't use materialized views for this in production without knowing your version's caveats.

**Q:** What's the tombstone problem?

**L4 answer** — Deletes are markers kept until `gc_grace_seconds` (default 10 days); range reads have to skip them; too many and reads time out.

**L5 answer** — Design to avoid: TTL with TWCS, append-only tables, small partitions, and never "queue" patterns (insert-then-delete) on Cassandra — that's the canonical anti-pattern from the DataStax docs.

**Q:** Compare Cassandra and DynamoDB for this workload.

**L4 answer** — Same data model (partition + sort); DynamoDB is managed with hard per-partition limits and pay-per-request; Cassandra is self-run, tunable consistency, multi-DC, no hard caps but operational cost.

**L5 answer** — Deciding variables: operational capacity of the team (DynamoDB default), multi-region active-active with tunable consistency (Cassandra/Scylla), cost at very high steady throughput (self-run wins at scale, order of magnitude), and the need for LWT-style conditional writes (DynamoDB's conditional writes are cheaper and simpler than Cassandra LWT).

#### L5-Only Questions

**Q:** Design chat message storage for channels with 1 to 10M messages.

`messages_by_channel ((channel_id, bucket), message_id)` with bucket = 10-day window (Discord's published choice) or by message count; `message_id` a Snowflake/ULID for time order; a small `channel_meta` table storing the newest bucket so reads don't probe empty buckets. Hot channel = hot partition even with buckets; mitigation is caching the newest bucket in Redis and accepting that one channel's write rate is bounded by one partition (~thousands/s, order of magnitude).

**Q:** How do you handle strong read-your-write on Cassandra?

`QUORUM` for both reads and writes with RF=3 gives overlap (R+W > RF); latency cost is the slowest of 2 replicas; availability drops with one DC down unless `LOCAL_QUORUM`. Defeater: LWW timestamps — two writers with skewed clocks still lose updates; use LWT for the rare compare-and-set paths and accept ~4× write latency.

---

### 2.4 Redis as a Data Model

```
   STRING  user:42:session  →  token         (TTL)
   HASH    user:42          →  {name, email}
   ZSET    leaderboard:g1   →  {score: userId}
   LIST/STREAM events        →  append log
```

#### Concept

- **What it is** — an in-memory data-structure server; the "schema" is the choice of data type per key and the key naming convention.
  → 🗣 "In Redis the data structure _is_ the index — I pick the type by the operation I need in O(1) or O(log n)."
- **What problem it solves** — sub-millisecond reads/writes for hot state, counters, rankings, rate limits, sessions.
  ◆ Defeater: memory-bound and single-threaded per shard; durability is opt-in (AOF/RDB) and weaker than a disk store; a big key or a `KEYS *` blocks the shard.
- **What it replaced** — memcached (no structures) and DB-backed counters/sessions.
- **What it works with** — cache-aside in front of DynamoDB/Postgres; Redis Cluster hash slots (16,384) for sharding; Lua scripts for atomic multi-key logic (same slot). Conflicts with: being the system of record for anything you can't rebuild.
- **Place in the world** — everywhere as cache, sessions, rate limiters, leaderboards, pub/sub. Wrong answer to: durable ledgers, large blobs, range scans over millions of keys.

#### Architecture & Core Components

```
 Client ─▶ [key → hash slot → shard] ─▶ single-threaded event loop ─▶ in-memory structures
                                             └ AOF/RDB persistence [async]
```

- **Hash slot router** — `CRC16(key) mod 16384`; `{tag}` forces co-location.
- **Event loop** — executes commands serially; big-O of each command is the latency budget.
- **Persistence** — periodic snapshot or append log; not a durability guarantee at sub-second.

#### How Each Component Works

**Data types** — STRING (counters via `INCR`), HASH (small objects, field-level update), ZSET (skiplist + hash, O(log n) rank), SET (membership), LIST, STREAM (consumer groups), HyperLogLog (~0.81% error cardinality, `Redis docs, 2026-01`), Bitmap.

**Expiry** — lazy + active sampling deletion; keys expire approximately, not exactly.

**Cluster** — keys in a multi-key command must share a slot (use `{userId}` tags); resharding moves slots live.

#### Design Decisions, Tradeoffs & Best Practices

| Need                 | Type                      | Buys you                     | Costs you                                                             |
| -------------------- | ------------------------- | ---------------------------- | --------------------------------------------------------------------- |
| Counter / rate limit | STRING `INCR` + `EXPIRE`  | atomic O(1)                  | fixed-window burst at edges (use sliding ZSET or token bucket in Lua) |
| Ranking              | ZSET                      | O(log n) rank/range          | memory ~2× a hash                                                     |
| Object cache         | HASH or serialized STRING | field updates vs. one blob   | HASH loses per-field TTL                                              |
| Queue                | STREAM                    | consumer groups, ack, replay | trimming discipline                                                   |
| Unique visitors      | HyperLogLog               | 12 KB per key                | approximate                                                           |

- Best practices:
  - Key naming `type:id:field` with TTL on everything cache-like. Prevents: unbounded memory growth and eviction storms.
  - No key > order of magnitude MBs; no `KEYS`, `SMEMBERS` on huge sets in prod; use `SCAN`. Prevents: event-loop stalls that spike p99 for every tenant.
  - Multi-key atomicity via Lua on same-slot keys. Prevents: check-then-set races (rate limiter overshoot).

#### Failure Modes, Exception Handling & Production Issues

| Failure               | Trigger                    | Blast radius                          | Detection signal             | Mitigation                                               |
| --------------------- | -------------------------- | ------------------------------------- | ---------------------------- | -------------------------------------------------------- |
| Big key               | one huge ZSET/LIST         | shard stalls on read/delete           | `--bigkeys`, slowlog         | split by shard suffix; `UNLINK`                          |
| Eviction storm        | memory full, `allkeys-lru` | cache hit rate collapse → DB overload | evicted_keys metric          | size memory; TTL discipline                              |
| Cache stampede        | hot key expires            | thundering herd on DB                 | DB QPS spike at TTL boundary | jittered TTL, single-flight lock, stale-while-revalidate |
| Data loss on failover | async replication, AOF lag | last ~1 s of writes lost              | —                            | don't make Redis the source of truth                     |

- Exception handling: `MOVED/ASK` redirects handled by cluster-aware clients; `OOM command not allowed` when memory full with `noeviction` — a hard error. Poison pill: a STREAM consumer that never `XACK`s grows the PEL forever.
- Canonical failure pattern (not a specific incident): a session cache without TTL fills memory; eviction policy `volatile-lru` evicts nothing (no TTLs) → writes fail; fix is TTL on all session keys and `allkeys-lru`; guardrail is a lint on key writes without `EX`.

#### Interview Questions

**Q:** Design a leaderboard.

**L4 answer** — ZSET per game: `ZADD leaderboard:g1 score userId`; rank via `ZREVRANK`, top-N via `ZREVRANGE`. Persist scores in a durable store and rebuild the ZSET on loss.

**L5 answer** — A global viral game's ZSET becomes a big key on one shard; shard by score bands or user hash and merge top-N, or accept one shard per game and size accordingly. Ties: encode timestamp in the score's fractional part. Snapshot per day into a durable table for history; the ZSET is a rebuildable view.

**Q:** Rate limiter — how?

**L4 answer** — Fixed window: `INCR key:minute` + `EXPIRE`; reject over N. Simple, but bursts at window edges.

**L5 answer** — Sliding window with ZSET of timestamps (`ZREMRANGEBYSCORE`, `ZCARD`, `ZADD` in one Lua script) or token bucket state in a HASH updated by Lua; per-tenant keys with `{tenant}` tags for slot locality; fail-open vs. fail-closed decision when Redis is unavailable, stated explicitly (fail-open for user-facing, fail-closed for abuse-prone endpoints).

**Q:** Cache-aside vs write-through?

**L4 answer** — Cache-aside: read miss → DB → populate; simplest, tolerates cache loss. Write-through: write to cache and DB together; fresher, more coupling.

**L5 answer** — In practice: cache-aside + invalidate-on-write, with stampede protection (single-flight, jittered TTL), and versioned keys for read-your-write. Write-through only when the cache is a required hot-path store (sessions). Mention the dual-write ordering bug: update DB then delete cache — a concurrent reader can repopulate stale data; mitigate with short TTL or delayed double-delete.

**Q:** When is Redis the wrong answer?

**L4 answer** — Data you can't afford to lose, data larger than memory, range queries across many keys.

**L5 answer** — Also when access is not key-addressable, when you need multi-key transactions across slots, and when the "cache" would hide a schema problem in the source store — fix the model first, cache second.

#### L5-Only Questions

**Q:** Design an idempotency-key store for a payments API.

`SET idem:{tenant}:{key} <response-hash> NX EX 86400` — atomic reserve; on success proceed and later `SET` the final response; on `NX` failure return the stored response or 409-in-progress. Redis alone isn't durable enough for money — mirror to DynamoDB with a conditional `PutItem` as the source of truth and use Redis as the fast front. TTL = the client's max retry horizon.

**Q:** How do you keep a Redis Cluster balanced with a multi-tenant key space?

Never put all of a tenant behind one hash tag unless the tenant is small; tag by `{tenant:shard}` for big tenants. Monitor per-slot memory and QPS; reshard slots live when a shard exceeds 60–70% of memory (order of magnitude headroom). Big-key scanner in CI/ops. Hot-key mitigation: client-side local cache for read-mostly hot keys.

---

## 3. Correctness & Evolution

```
   Write correctness:  conditional write (CAS) ─▶ transaction (bounded) ─▶ saga (unbounded)
   Read correctness:   strong (base table) ─▶ eventual (GSI/replica/derived)
   Evolution:          version field ─▶ dual-read ─▶ lazy/batch migrate ─▶ cutover
```

### 3.1 Consistency, Conditional Writes & Transactions

```
   PutItem(cond: attribute_not_exists(PK))   → create-once
   UpdateItem(cond: version = :v) SET version = :v+1 → optimistic lock
   TransactWriteItems([...≤100 items])       → all-or-nothing across partitions
```

#### Concept

- **What it is** — the toolkit for invariants without a relational transaction: conditional writes (compare-and-set on one item), bounded multi-item transactions, and versioning.
  → 🗣 "I put the invariant inside one item where I can, use a conditional write to enforce it, and reach for a transaction only across a bounded set."
- **What problem it solves** — double-booking, lost updates, duplicate creation, cross-item atomicity.
  ◆ Defeater: DynamoDB transactions are limited to 100 items / 4 MB and cost 2× (`DynamoDB docs, 2026-01`); they don't span accounts/regions; and they're not isolation for _reads_ unless you use `TransactGetItems`. MongoDB transactions hold locks and abort on conflict.
- **What it replaced** — relational ACID across arbitrary rows; the prior art didn't scale across partitions.
- **What it works with** — idempotency keys, outbox pattern via Streams/change streams, sagas for cross-service flows. Conflicts with: designs that expect serializable multi-row reads.
- **Place in the world** — booking, inventory, payments, uniqueness constraints. Wrong answer to: ledgers needing global serializability (use a relational store or a purpose-built ledger).

#### Architecture & Core Components

```
 Client ─▶ [Conditional write] ─▶ item  (fails → ConditionalCheckFailed)
 Client ─▶ [TransactWrite: N conditional puts/updates/deletes] ─▶ 2-phase inside DynamoDB
 Streams ─▶ [Outbox relay] ─▶ downstream (idempotent)
```

- **Conditional write** — single-item CAS; the workhorse.
- **Transaction** — bounded multi-item atomicity with per-item conditions.
- **Outbox relay** — turns a committed write into a reliably delivered event.

#### How Each Component Works

**Conditional write** — server evaluates the condition expression against the current item under the item's write lock; on failure returns the exception (optionally with the current item via `ReturnValuesOnConditionCheckFailure`, `DynamoDB docs, 2026-01`). Idempotent if the condition encodes the desired end state.

**TransactWriteItems** — DynamoDB runs a two-phase protocol internally; all items succeed or `TransactionCanceledException` lists per-item reasons; concurrent transactions on the same items serialize; a `ClientRequestToken` makes the whole transaction idempotent for 10 minutes.

**Uniqueness via marker item** — to enforce "email unique," write a `PK=EMAIL#x` marker item in the same transaction as the user, with `attribute_not_exists`. This is how you get a unique constraint without an index.

**MongoDB** — `findOneAndUpdate` with a filter on the current version is the CAS; multi-document transactions use snapshot isolation on a replica set, abort on write conflict, retry via the driver's callback API.

#### Design Decisions, Tradeoffs & Best Practices

| Option                            | Buys you                       | Costs you                    | Choose when                             |
| --------------------------------- | ------------------------------ | ---------------------------- | --------------------------------------- |
| Single-item CAS                   | 1 WCU, no coordination         | invariant must fit one item  | default                                 |
| Marker item + transaction         | uniqueness across items        | 2× cost, 100-item bound      | unique constraints, parent+child create |
| Saga (compensations)              | unbounded scope, cross-service | eventual, compensating logic | multi-service workflows                 |
| Read-then-write without condition | simplicity                     | lost updates                 | never in contended paths                |

- Best practices:
  - Every write that depends on prior state carries a condition (version or existence). Prevents: lost updates under concurrency.
  - Use `ClientRequestToken`/idempotency keys on transactions and on any retried side effect. Prevents: double charge on retry after timeout.
  - Read from the base table (or `ConsistentRead=true`) on read-your-write paths; GSIs only for eventually consistent lists. Prevents: "I just created it and it's not there."

#### Failure Modes, Exception Handling & Production Issues

| Failure                    | Trigger                               | Blast radius                                 | Detection signal            | Mitigation                                  |
| -------------------------- | ------------------------------------- | -------------------------------------------- | --------------------------- | ------------------------------------------- |
| Lost update                | unconditional overwrite               | silent data loss                             | audit/version gap           | version attribute + condition               |
| Transaction conflict storm | many txns on same item                | `TransactionConflict` cancellations, latency | cancellation reasons metric | reduce contention (shard counters), backoff |
| Ghost event                | write succeeded, event publish failed | downstream missing data                      | reconciliation              | outbox via Streams, not dual publish        |
| Duplicate creation         | retry after timeout without condition | duplicate rows                               | uniqueness check            | `attribute_not_exists` / idempotency token  |

- Exception handling: `ConditionalCheckFailed` → business branch; `TransactionCanceled` → inspect `CancellationReasons` (some are retryable conflicts, some are condition failures); throttle → backoff.
- Canonical failure pattern (not a specific incident): service writes item then publishes SNS in code; a crash between the two leaves consumers without the event; fix is Streams→Lambda as the outbox; guardrail is "no side-effect publish after a DB write in request code."

#### Interview Questions

**Q:** Prevent double-booking of an appointment slot in DynamoDB.

**L4 answer** — Slot item `PK=PROVIDER#p, SK=SLOT#2026-09-01T10:00`; `PutItem` with `attribute_not_exists(PK)`; second writer gets `ConditionalCheckFailed`.

**L5 answer** — Also create the appointment record atomically via `TransactWriteItems` (slot marker + appointment item + customer index entry), with `ClientRequestToken` so client retries don't double-book. Cancellation = transaction that deletes the marker and sets status; overlapping variable-length slots need the marker per granular unit (e.g., 15-minute cells) — N markers in one transaction.

**Q:** Implement optimistic locking.

**L4 answer** — Store `version`; read it; update with condition `version = :read` and `SET version = :read + 1`; on failure re-read and retry or surface conflict.

**L5 answer** — Bound retries, and distinguish contention (retry) from semantic conflict (surface to user). For high-contention items (counters), optimistic locking thrashes — use atomic `ADD` or shard instead. Java: the Enhanced Client's `@DynamoDbVersionAttribute` does this transparently.

**Q:** When do you use DynamoDB transactions vs. a saga?

**L4 answer** — Transactions for ≤ 100 items in one table/account/region in a single request; sagas when the workflow crosses services or needs long-running steps.

**L5 answer** — Also: transactions cost 2× and serialize on contended items — use them for creates and state transitions, not for hot counters. Sagas need compensations designed per step and an idempotent step executor (Step Functions or a state item with conditional transitions).

**Q:** How do you enforce a unique constraint?

**L4 answer** — Marker item keyed by the unique value, written with `attribute_not_exists` in the same transaction as the main item.

**L5 answer** — Normalize the value (lowercase email) before keying; on update of the unique field, transaction = delete old marker + put new marker + update main; keep markers in the same table for transaction scope. This doubles item count for that attribute — accept it; it's the price of no unique index.

#### L5-Only Questions

**Q:** Design inventory decrement under flash-sale load.

Sharded stock: `SKU#x#shard0..N` each holding a slice; decrement with condition `qty >= :n` on a random shard, on failure try another shard, on all-fail return sold-out (with a small over-rejection tolerance). Aggregate visible stock asynchronously. Prevents one-item contention at 1,000 WCU/s; cost is imprecise sold-out timing. For strict correctness at low volume, a single item with conditional decrement is enough — say which regime you're in.

**Q:** What consistency does a GSI-backed "my recent orders" page have, and how do you fix the UX?

Eventual; typically sub-second but unbounded under load. Fix: after a write, render the new order from the write response (client-side merge) or read the customer's item collection from the base table with `ConsistentRead=true` for the first N seconds; show "processing" state derived from the write path, not the index.

---

### 3.2 Schema Evolution Without a Schema

```
   v1 items ──(dual-read)── app ──(write v2)──▶ v2 items
        └──── background migrator (conditional rewrite) ────▶
```

#### Concept

- **What it is** — the discipline of versioning item shapes and migrating lazily or in the background, because the store won't enforce or migrate a schema for you.
  → 🗣 "Schemaless means every reader is a migrator; I make that explicit with a version field and a dual-read window."
- **What problem it solves** — changing shapes without downtime or a table rebuild.
  ◆ Defeater: without a version field you cannot tell whether a missing attribute means "old shape" or "null" — that ambiguity is a bug factory.
- **What it replaced** — `ALTER TABLE` + migrations (Liquibase/Flyway). Those were insufficient because there is no global schema to alter; changes are per-item.
- **What it works with** — Liquibase-style changelogs still useful for _table/index_ definitions (Terraform for DynamoDB tables/GSIs, `mongosh` scripts for indexes/validators); drift tests between the app's schema classes and the validator.
- **Place in the world** — any table older than the team that built it. Wrong answer to: nothing — it's mandatory.

#### Architecture & Core Components

```
 [schemaVersion attr] ─▶ [reader: upcast v1→vN in memory] ─▶ domain object
                                    └ [writer: always writes vN]
 [migrator job: scan/stream, conditional rewrite, metrics]  [control plane]
```

- **Version attribute** — the discriminator.
- **Upcaster** — pure function per version step.
- **Migrator** — optional; converts remaining items on a schedule.

#### How Each Component Works

**Upcaster** — chain `v1→v2→v3`; applied on read; writes always emit latest; unit-tested with fixtures per version.

**Migrator** — DynamoDB: parallel `Scan` segments or Streams replay; each rewrite conditional on `schemaVersion = :old` to avoid clobbering concurrent writes; rate-limited to stay under capacity headroom. MongoDB: `updateMany` in batches with a `{v: old}` filter; validator at `moderate` level during migration.

**Index changes** — DynamoDB: add GSI (async backfill), dual-read until `ACTIVE` and complete, then switch; delete old GSI. MongoDB: build index in background (rolling on replica sets), then change queries.

#### Design Decisions, Tradeoffs & Best Practices

| Option                         | Buys you                         | Costs you                                    | Choose when         |
| ------------------------------ | -------------------------------- | -------------------------------------------- | ------------------- |
| Lazy (on read/write)           | zero migration job               | mixed shapes forever, upcaster lives forever | rarely-touched data |
| Background batch               | finite window, delete upcaster   | capacity cost, coordination                  | most cases          |
| New table + backfill + cutover | clean slate, key change possible | dual-write period, cutover risk              | key schema changes  |

- Best practices:
  - Additive changes only within a version; breaking changes bump the version. Prevents: readers misinterpreting attributes.
  - Migrator writes are conditional on old version. Prevents: overwriting a concurrent user update with a stale migrated copy.
  - Keep a "items at old version" metric and an exit criterion. Prevents: upcaster code that never gets deleted.

#### Failure Modes, Exception Handling & Production Issues

| Failure                         | Trigger                               | Blast radius        | Detection signal           | Mitigation                                  |
| ------------------------------- | ------------------------------------- | ------------------- | -------------------------- | ------------------------------------------- |
| Reader crash on unknown version | new writer deployed before reader     | 500s on reads       | error rate by version      | deploy readers first (expand/contract)      |
| Migrator throttles prod         | unbounded scan rate                   | user-facing latency | throttle metrics           | rate limit; run on-demand capacity headroom |
| Half-migrated GSI               | queries switched before backfill done | missing results     | count mismatch base vs GSI | gate switch on backfill completion check    |

- Exception handling: unknown version → fail loudly (don't guess); migration conflicts → retry with re-read.
- Canonical failure pattern (not a specific incident): a rename `userName→username` done by a writer deploy while old readers still run; half the fleet reads null names; fix is expand (write both) → migrate → contract (drop old); guardrail is the expand/contract rule in the deploy checklist.

#### Interview Questions

**Q:** How do you add a field?

**L4 answer** — Additive: new writes include it; readers treat absence as default. No migration needed unless a query depends on it (then backfill so the index/filter sees it).

**L5 answer** — If a GSI keys on the new field, absent = not indexed (sparse), so a backfill is required for completeness; run it conditionally and gate the feature on "backfill complete." Note that "absent" and "default" must be equivalent in the domain or you need the version bump.

**Q:** How do you rename or restructure a field with zero downtime?

**L4 answer** — Expand/contract: deploy readers that accept both, writers that write both, migrate, then remove the old.

**L5 answer** — Add the version bump and conditional migrator; order deployments readers → writers → migrator → cleanup; keep a rollback that only requires redeploying the old writer (data stays readable by both). State the extra write cost during the window.

**Q:** How do you change a partition key?

**L4 answer** — You can't in place; create a new table with the new key, backfill from Streams/scan, dual-write during cutover, then switch reads.

**L5 answer** — Sequence: create new table + Streams consumer that mirrors writes from old to new (idempotent); backfill scan for history; verify counts/hashes per partition; flip reads behind a flag; keep dual-write for a rollback window; stop old writes; delete old table after retention. Defeater: anything else consuming the old Streams ARN.

**Q:** Where does something like Liquibase fit with NoSQL?

**L4 answer** — For the parts that _are_ declarative: tables, GSIs, capacity, validators, indexes — codified in Terraform or scripts. Item-shape migrations are application jobs.

**L5 answer** — Add a drift test: the app's item-shape definitions (Pydantic/Java records) versus the validator/GSI definitions in IaC, run in CI — the same idea as a Liquibase-vs-StructType drift test on a lakehouse. It's the mechanical guardrail that replaces the missing schema enforcement.

#### L5-Only Questions

**Q:** Design the observability for a long-running migration.

Metrics: items remaining by version, migrator throughput, conditional-failure rate (contention signal), consumed vs. provisioned capacity, downstream Streams lag. Dashboards per table; alert when remaining-count plateaus or contention rate > threshold. A "dry run" mode that counts without writing validates the upcaster before any write.

**Q:** Argue for and against lazy migration in a table with 5 billion items.

For: no capacity spend, no job to babysit. Against: mixed shapes indefinitely, every reader carries the upcaster, analytics exports see both shapes, and a later version bump multiplies branches. My default at that scale: lazy for cold items plus a slow background sweep at a fixed WCU budget, with a hard deadline to delete the upcaster.

---

### 3.3 The Interview Method

```
  1 clarify ─▶ 2 entities ─▶ 3 ACCESS PATTERNS ─▶ 4 store choice ─▶ 5 keys
                                      ▲ the step relational design doesn't have
  6 item shapes ─▶ 7 indexes ─▶ 8 invariants + failure modes ─▶ wrap
```

#### Concept

- **What it is** — an 8-step spoken procedure that turns "design the schema" into a structured 10-minute answer.
- **What problem it solves** — the interviewer wants to see the _method_, not a memorized table; the method proves you can do it for a system they didn't tell you about.
- **What it replaced** — the relational method (entities → normalize → tables → relations → indexes). Insufficient for NoSQL because it never asks "what is the request?" before drawing.
- **What it works with** — the §11 hygiene checklist from the system-design generator (idempotency, retries, caching) — schema is one section of that answer.
- **Place in the world** — Amazon SDE II design rounds (they ask "what's your DynamoDB key" directly); Google L4 (they ask "how does this hold up at 100×"). Wrong answer to: nothing; but skip steps when the interviewer signals.

#### Architecture & Core Components

```
 Step   Output artifact                     Time
 1      assumptions list                    1 min
 2      entity list (nouns) + cardinality   1 min
 3      AP table (r/w, inputs, freq)        2 min   ◀ spend the time here
 4      store choice + why                  1 min
 5      key table (PK, SK, GSIs)            2 min
 6      example items (3–5)                 1 min
 7      index/projection decisions          1 min
 8      invariants (CAS/txn) + hot key + evolution   1–2 min
```

#### How Each Component Works

1. **Clarify** — scale (items, writes/s, reads/s), consistency needs, multi-tenancy, retention. Give assumed answers if not provided.
2. **Entities** — list nouns; note which have unbounded children (they'll need their own keys).
3. **Access patterns** — write the table aloud; number them; mark hot-path vs. background; mark which need read-your-write.
4. **Store** — default DynamoDB for key-addressable OLTP on AWS; MongoDB for rich variable documents; Cassandra for extreme append + multi-DC; Redis for hot ephemeral; Postgres if APs are unknown or join-heavy. Say the deciding variable.
5. **Keys** — for each AP: "caller has X → PK; wants ordered by Y → SK"; group entities under shared PK when read together; overload a GSI for the reverse direction.
6. **Item shapes** — write 3–5 example items with real prefixes so the interviewer sees the collections form.
7. **Indexes** — one per remaining AP; projection choice; note sparse indexes.
8. **Invariants & failure** — conditional writes for uniqueness/booking; hot-key check on the top entity; size-cap check on embedded lists; how a new AP would be added; one sentence on migration.

- Transition lines to say: "Before I pick keys, let me list access patterns — that's what drives the design here." / "This AP is analytics; I'd serve it from a derived store, not this table." / "The hot-key risk is X; here's the shard scheme if it materializes."

#### Design Decisions, Tradeoffs & Best Practices

- Spend the time on step 3; an interviewer who sees a complete AP table forgives a missed GSI, never the reverse.
- State one deliberate limitation and its mitigation rather than claiming the design handles everything.
- Best practices:
  - Draw the key table, not an ER diagram. Prevents: the "you designed a relational schema and put it in DynamoDB" verdict.
  - Say the per-partition limits and item size caps once, with numbers. Prevents: hand-wavy scale claims.
  - Anchor to real experience where it fits (the instrument-enrichment pipeline writing Aurora + DynamoDB + OpenSearch: DynamoDB for key lookups, OpenSearch for search, Postgres for relational reporting — the polyglot split _is_ the answer to "which store").

#### Failure Modes, Exception Handling & Production Issues

| Failure (in the interview) | Trigger                      | Detection                                         | Mitigation                                    |
| -------------------------- | ---------------------------- | ------------------------------------------------- | --------------------------------------------- |
| Entity-first drift         | starts drawing boxes         | interviewer asks "how do you get X?" and you scan | restart from AP table                         |
| No numbers                 | "it scales"                  | interviewer probes limits                         | say 1,000 WCU / 400 KB / 16 MB / 100-item txn |
| Over-design                | GSI for every conceivable AP | "what does that cost?"                            | tie each index to a numbered, frequent AP     |
| Ignoring consistency       | GSI for read-your-write      | "user just created it, where is it?"              | base-table read path                          |

- Canonical pattern (interview, not incident): candidate models a many-to-many with embedded arrays on both sides; interviewer asks about a user in 10k groups; candidate has no answer. Fix: adjacency list + GSI.

#### Interview Questions

**Q:** Design the data model for an ordering system.

**L4 answer** — Clarify scale; entities customer/order/item/product; APs: create order, get order, list orders by customer by date, list open orders, get product; DynamoDB single table with `CUST#`, `ORDER#`, `ITEM#` prefixes, GSI for order-by-id and sparse GSI for open orders; conditional create; product snapshot copied into items.

**L5 answer** — Add: WCU/RCU estimate at target scale; B2B big-customer bucketing; Streams to OpenSearch for search/reporting and to the warehouse; transaction for order+items+idempotency marker; TTL for cart items; what changes at 10× (shard open-orders GSI, move analytics off).

**Q:** Design the data model for an appointment/booking system.

**L4 answer** — Entities provider/slot/appointment/customer; APs: list available slots by provider by day, book, cancel, list my appointments; `PK=PROVIDER#p, SK=SLOT#<iso>`; booking = conditional put; GSI `CUST#c / APPT#<iso>` for the customer view.

**L5 answer** — Model availability as generated slot items (write-time expansion of a schedule) vs. computed from rules at read time — pick generated for simplicity and conditional-write safety; overlapping durations via granular cells in one transaction; reminders via TTL + Streams; time-zone stored as IANA id with UTC instants.

**Q:** Which store and why?

**L4 answer** — Name the deciding variable: key-addressable OLTP at scale → DynamoDB; rich variable documents → MongoDB; ad-hoc/joins → Postgres; hot ephemeral → Redis.

**L5 answer** — Give the polyglot answer with the boundary and the propagation mechanism (CDC/Streams), the consistency each consumer gets, and the operational cost line. State what would flip it (e.g., "if reporting becomes the primary use, this moves to Postgres").

**Q:** What would you do differently at 100× scale?

**L4 answer** — Shard hot keys, bucket time-series, move analytics off the OLTP table, add caching for hot reads.

**L5 answer** — Also re-examine the top-3 APs' partition distribution with real telemetry, add write sharding _before_ it's needed for fan-in entities, move to on-demand or autoscaled capacity with alarms on throttles, and put a cost ceiling on GSI projections (switch `ALL` → `INCLUDE`).

#### L5-Only Questions

**Q:** Defend polyglot persistence for the instrument-enrichment platform (Aurora + DynamoDB + OpenSearch).

Aurora for relational reporting and referential integrity on canonical records; DynamoDB for key-addressable low-latency reads by instrument id; OpenSearch for text/faceted search. Propagation from the pipeline is at-least-once, so every sink write is idempotent on `(instrumentId, version)`. Cost: three consistency models and a reconciliation job; the alternative (Aurora only + read replicas) is right below a threshold of read QPS and search complexity — name that threshold as the flip condition.

**Q:** An interviewer says "just use Postgres." How do you respond?

Agree where it's true: if the AP set is unknown or write rate < ~10k/s and data < ~1 TB (order of magnitude), Postgres with JSONB is the boring right answer. Then name the specific number that would break it for this system (write rate on one primary, or p99 under join load, or partition growth) and show the NoSQL design is the response to that number, not a preference.

---

## 4. References

1. AWS — DynamoDB Developer Guide: best practices for partition keys, single-table design, transactions, GSIs — https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html
2. Alex DeBrie — _The DynamoDB Book_ companion posts and single-table design write-up — https://www.alexdebrie.com/posts/dynamodb-single-table/
3. MongoDB — Data Modeling / Building with Patterns series (embed, subset, bucket, outlier, computed, attribute, schema versioning) — https://www.mongodb.com/docs/manual/data-modeling/
4. DataStax / Apache Cassandra — data modeling and anti-patterns (tombstones, queues, wide partitions) — https://cassandra.apache.org/doc/latest/cassandra/developing/data-modeling/
5. Discord Engineering — "How Discord Stores Trillions of Messages" (2023): channel bucketing, hot-partition lessons — https://discord.com/blog/how-discord-stores-trillions-of-messages
6. Redis — data types and cluster spec — https://redis.io/docs/latest/develop/data-types/
