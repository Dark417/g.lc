# Design Schema — NoSQL (10 worked interview questions)

> Companion to `knowledge/nosql-schema-design.md`. Each question follows the 8-step method: assumptions → entities → **access patterns** → store → keys → example items → indexes → invariants/failure/evolution. Drill: cover the answer, produce the AP table and key table from the prompt alone in 8 minutes, then compare. Numbers marked `(assume)` are interview assumptions; store limits are from official docs as of 2026-01.

## INDEX

1. [E-commerce orders (DynamoDB single table)](#1-e-commerce-orders)
2. [Appointment booking with no double-booking](#2-appointment-booking)
3. [Chat / messaging (Cassandra or DynamoDB)](#3-chat--messaging)
4. [Product catalog with variable attributes (MongoDB)](#4-product-catalog-with-variable-attributes)
5. [IoT telemetry time-series (bucket pattern)](#5-iot-telemetry-time-series)
6. [Social graph + feed (adjacency list, fan-out)](#6-social-graph--feed)
7. [Multi-tenant SaaS hierarchy (folders/documents)](#7-multi-tenant-saas-hierarchy)
8. [Leaderboard + rate limiter (Redis)](#8-leaderboard--rate-limiter)
9. [Idempotent event/audit store for a pipeline](#9-idempotent-event--audit-store)
10. [Flash-sale inventory (contention)](#10-flash-sale-inventory)
11. [Cross-question drill sheet](#11-cross-question-drill-sheet)
12. [References](#12-references)

---

## 1. E-commerce Orders

```
  CUST#c1 ┬ META
          ├ ORDER#2026-08-27T10:00#o9   ← list by customer, newest first
          └ ORDER#2026-08-28T09:12#o10
  ORDER#o10 ┬ META  (summary duplicated)
            ├ ITEM#001
            └ ITEM#002
  GSI1: OPENORDER#<shard> / <createdAt>   (sparse)
```

**Interviewer:** "Design the data model for orders, customers, and line items. Customers see their order history; ops sees open orders."

- Assumptions `(assume)`: 5M customers, 200k orders/day (~2.3/s avg, 10× peak ≈ 25/s), 5 items/order, retention 7 years, consumer traffic read-heavy 20:1.
- Entities: Customer, Order, OrderItem, Product (snapshot), Payment (out of scope).

| AP# | Operation                                | Inputs            | Result    | Freq      | Consistency          |
| --- | ---------------------------------------- | ----------------- | --------- | --------- | -------------------- |
| 1   | Create order with items                  | customerId, items | orderId   | 25/s peak | strong, idempotent   |
| 2   | Get order + items                        | orderId           | 1 + ≤ 50  | 200/s     | strong (post-create) |
| 3   | List customer orders newest-first, paged | customerId        | 20/page   | 300/s     | eventual ok          |
| 4   | List open orders for ops                 | status            | thousands | 5/s       | eventual             |
| 5   | Update order status                      | orderId, from, to | —         | 100/s     | strong CAS           |

- Store: DynamoDB single table — all APs key-addressable; no ad-hoc queries (reporting → Streams → warehouse).

| Entity                | PK          | SK                      | GSI1PK                                | GSI1SK  |
| --------------------- | ----------- | ----------------------- | ------------------------------------- | ------- |
| Customer              | `CUST#c1`   | `META`                  | —                                     | —       |
| Order (customer view) | `CUST#c1`   | `ORDER#<iso>#<orderId>` | —                                     | —       |
| Order (order view)    | `ORDER#o10` | `META`                  | `OPENORDER#<shard>` (only while open) | `<iso>` |
| Item                  | `ORDER#o10` | `ITEM#<seq>`            | —                                     | —       |

```json
{ "PK": "ORDER#o10", "SK": "META", "type": "Order", "v": 1,
  "customerId": "c1", "status": "PLACED", "total": 129.90, "createdAt": "2026-08-28T09:12:00Z",
  "GSI1PK": "OPENORDER#7", "GSI1SK": "2026-08-28T09:12:00Z", "version": 3 }
{ "PK": "ORDER#o10", "SK": "ITEM#001", "type": "OrderItem", "productId": "p5",
  "nameSnapshot": "Widget", "unitPrice": 12.99, "qty": 2 }
```

- AP1: `TransactWriteItems` = order (customer view) + order (order view) + N items + `IDEM#<key>` marker with `attribute_not_exists`; `ClientRequestToken` = idempotency key. Cost ≈ (2 + N + 1) × 2 WCU (transactions double).
- AP2: `Query PK=ORDER#o10` → META + items in one call, `ConsistentRead=true`.
- AP3: `Query PK=CUST#c1, begins_with(SK,'ORDER#'), ScanIndexForward=false, Limit=20`.
- AP4: sparse GSI1 sharded 0..15 (a single `OPEN` value is a hot partition); ops polls 16 shards in parallel. On fulfillment, `REMOVE GSI1PK` so the item leaves the index.
- AP5: `UpdateItem` condition `status = :from AND version = :v`.
- Failure/scale: B2B customer with 1M orders → bucket SK by month (`ORDER#2026-08#...`) and page per bucket; item cap 400 KB fine since items are separate. Product name changes must **not** propagate — snapshot is domain-correct.
- Evolution: adding "gift message" is additive; adding "orders by status per customer" → new GSI `CUST#c1#STATUS#x` keyed off existing attrs, backfill required.
- 🗣 "The order page is one `Query`; history is one `Query`; open orders are a sharded sparse index; everything else is a Streams consumer."

---

## 2. Appointment Booking

```
  PROVIDER#p1 ┬ SLOT#2026-09-01T10:00   {status: FREE}
              ├ SLOT#2026-09-01T10:15   {status: BOOKED, apptId}
  APPT#a7     ─ META                    (customer, provider, start, end, status)
  GSI1: CUST#c1 / APPT#<start>          customer's appointments
```

**Interviewer:** "Design the schema for a clinic booking system. Two people must never book the same slot."

- Assumptions `(assume)`: 10k providers, 15-minute granularity, appointments 15–60 min, 50 bookings/s peak, cancellation allowed, 2-year history.
- Entities: Provider, Schedule (rules), Slot (materialized cell), Appointment, Customer.

| AP# | Operation                           | Inputs                                  | Freq  | Consistency                      |
| --- | ----------------------------------- | --------------------------------------- | ----- | -------------------------------- |
| 1   | List free slots for provider on day | providerId, day                         | 500/s | eventual ok (re-checked on book) |
| 2   | Book slot(s)                        | providerId, start, duration, customerId | 50/s  | strong, atomic                   |
| 3   | Cancel                              | apptId                                  | 10/s  | strong                           |
| 4   | List customer's upcoming appts      | customerId                              | 100/s | eventual                         |
| 5   | Provider's day view                 | providerId, day                         | 200/s | strong preferred                 |

- Store: DynamoDB — conditional writes give the no-double-booking guarantee without locks.

| Entity      | PK            | SK                 | GSI1PK    | GSI1SK             |
| ----------- | ------------- | ------------------ | --------- | ------------------ |
| Slot cell   | `PROVIDER#p1` | `SLOT#<iso start>` | —         | —                  |
| Appointment | `APPT#a7`     | `META`             | `CUST#c1` | `APPT#<iso start>` |
| Provider    | `PROVIDER#p1` | `META`             | —         | —                  |

- Slot materialization: a nightly job (or on schedule change) writes FREE cells for the next 90 days from the provider's rules; day view = `Query PK=PROVIDER#p1, SK between SLOT#2026-09-01T00:00 and SLOT#2026-09-01T23:59`.
- Booking a 45-minute appointment = 3 cells: `TransactWriteItems` with three `UpdateItem`s, each conditioned `status = FREE`, plus `PutItem APPT#a7` with `attribute_not_exists`; `ClientRequestToken` for retry safety. Any cell already booked → whole transaction cancels; read `CancellationReasons` to tell the user which.
- Cancel: transaction sets cells back to FREE (condition `apptId = :a`) and `APPT` status CANCELLED.
- Why cells, not intervals: overlap checks on intervals need a range read + conditional write with a race window; cells make the invariant a per-item CAS.
- Hot key: a popular provider is one partition, but bookings/s per provider are tiny; day-view reads are one `Query` — fine. Generating 90 days × 96 cells × 10k providers ≈ 86M items — acceptable; add TTL on past cells (30 days).
- Alternative (state the tradeoff): compute availability from rules + booked appointments at read time — fewer items, but booking then needs a conditional write on an "interval index" item per provider-day (`bookedRanges` list, CAS on version) — simpler storage, contended per provider-day. Pick cells when providers have dense schedules, the version-list when sparse.
- Time zones: store UTC instants; provider IANA zone on the provider item; DST handled at cell generation.
- 🗣 "Booking is a transaction of conditional updates on materialized 15-minute cells — the invariant is enforced by the store, not by application locking."

---

## 3. Chat / Messaging

```
  Cassandra:  messages_by_channel ((channel_id, bucket), message_id DESC)
  DynamoDB:   PK=CHAN#c#<bucket>  SK=<ULID>      + CHAN#c META {latestBucket}
  read: newest bucket first, walk back until page full
```

**Interviewer:** "Design message storage for channels ranging from 2 members to millions."

- Assumptions `(assume)`: 1M messages/s aggregate, median channel small, top channels 5k msg/s, 90% of reads are "latest 50 messages," history is retained forever.
- Entities: Channel, Message, Member, ReadCursor.

| AP# | Operation                  | Inputs              | Freq   | Consistency                        |
| --- | -------------------------- | ------------------- | ------ | ---------------------------------- |
| 1   | Append message             | channelId, msg      | 1M/s   | at-least-once, ordered per channel |
| 2   | Latest N messages          | channelId           | 2M/s   | read-your-write for sender         |
| 3   | Page backwards from cursor | channelId, beforeId | 200k/s | eventual                           |
| 4   | Get message by id          | messageId           | 50k/s  | eventual                           |
| 5   | Unread count / cursor      | userId, channelId   | 1M/s   | eventual                           |

- Store: Cassandra/ScyllaDB (append-dominant, multi-DC, no per-partition hard cap) or DynamoDB if managed is required. Design is identical.

```sql
CREATE TABLE messages_by_channel (
  channel_id bigint, bucket int, message_id bigint,
  author_id bigint, content text, attachments list<text>,
  PRIMARY KEY ((channel_id, bucket), message_id)
) WITH CLUSTERING ORDER BY (message_id DESC)
  AND compaction = {'class': 'TimeWindowCompactionStrategy', 'compaction_window_size': 10, 'compaction_window_unit': 'DAYS'};
```

- `message_id` = Snowflake/ULID (time-sortable, unique); `bucket` = 10-day window derived from the id's timestamp (Discord's published scheme). Latest-N = read newest bucket; if fewer than N, read previous bucket. A `channel_meta` row stores `latest_bucket` and `first_bucket` so reads don't probe empty buckets.
- AP4 needs a second table `messages_by_id (message_id) → channel_id, bucket` — table-per-query.
- AP5: `read_cursor ((user_id), channel_id) → last_read_message_id`; unread count = compare ids, or a Redis counter incremented per fan-out for small channels only.
- Hot partition: 5k msg/s on one channel-bucket is above a comfortable single partition (order of magnitude thousands/s). Mitigation: shorter buckets for hot channels (per-channel bucket size stored in meta), or a shard suffix with N-way merge on read. Cache the newest bucket in Redis for the "latest 50" path.
- Ordering: guaranteed within a partition by clustering; across buckets by the time-ordered id. Defeater: two writers with skewed clocks can interleave out of causal order — acceptable for chat, mention it.
- Deletes: edit-in-place or tombstone per message; heavy deletes in one bucket → tombstone scans; TWCS + rarely deleting mitigates.
- 🗣 "Partition by (channel, time bucket), cluster by a time-sortable id, keep channel meta pointing at the newest bucket, and cache the newest bucket for the 90% read."

---

## 4. Product Catalog with Variable Attributes

```
  products: { _id, sku, category, title, price, brand,
              attrs: [{k:"screenSize", v:6.1}, {k:"color", v:"black"}],  ← attribute pattern
              variants: [{sku, color, size, stock}] (bounded ≤ 50),
              v: 2 }
  indexes: {category:1, price:1}, {"attrs.k":1, "attrs.v":1}, {sku:1} unique
```

**Interviewer:** "Design a catalog where a laptop has 40 spec fields and a t-shirt has 5, and users filter by any spec."

- Assumptions `(assume)`: 20M products, 200 categories, 500 writes/s (feed updates), 20k reads/s, faceted search required.
- Entities: Product, Variant, Category, Attribute definition, Inventory (separate system).

| AP# | Operation                                | Inputs                 | Freq  | Consistency |
| --- | ---------------------------------------- | ---------------------- | ----- | ----------- |
| 1   | Get product page                         | productId/sku          | 15k/s | eventual ok |
| 2   | Browse category sorted by price, paged   | categoryId             | 3k/s  | eventual    |
| 3   | Filter by arbitrary spec within category | categoryId, {k,v}…     | 2k/s  | eventual    |
| 4   | Faceted counts                           | categoryId, filters    | 2k/s  | eventual    |
| 5   | Upsert product from feed                 | sku, full doc          | 500/s | idempotent  |
| 6   | Update stock on variant                  | sku, variantSku, delta | 1k/s  | atomic      |

- Store: MongoDB for the document (AP1, 2, 5, 6); OpenSearch/Atlas Search for AP3–4 via change streams. State it: facets on the OLTP collection do not scale — that's a search-engine job.
- Document design: polymorphic by `category`; common scalars top-level and indexed; per-category specs in the **attribute pattern** array so one compound multikey index `{attrs.k, attrs.v}` serves any-key filters (vs. 200 sparse indexes). Bound `attrs` (≤ 100) and `variants` (≤ 50); beyond that use the outlier pattern (`hasMoreVariants: true` + `variants` collection).
- AP2: index `{category:1, price:1}` — ESR: equality on category, sort on price. Page with `price > last AND _id > lastId` keyset, never `skip`.
- AP5: `replaceOne({sku}, doc, {upsert:true})` — idempotent by construction; include `feedVersion` and condition `feedVersion < incoming` to reject out-of-order feeds.
- AP6: `updateOne({sku, "variants.sku": vs, "variants.stock": {$gte: n}}, {$inc: {"variants.$.stock": -n}})` — single-document atomic decrement with the positional operator; failure = out of stock. For real inventory at scale, move stock out of the catalog doc (write-hot field in a read-hot document = rewrite churn).
- Validation: `$jsonSchema` on required top-level fields; `validationLevel: moderate` during migrations; `v` field for schema versioning.
- Sharding (if needed): hashed `sku` or `{category, sku}`; category alone is low-cardinality with jumbo-chunk risk.
- Evolution: new spec keys need no schema change (attribute pattern); renaming a common scalar = expand/contract with `v` bump.
- 🗣 "Polymorphic documents with the attribute pattern for filters, one multikey index instead of hundreds, and facets pushed to search via change streams."

---

## 5. IoT Telemetry Time-Series

```
  Mongo bucket:  { sensorId, hourStart, count, readings:[{ts,val}…≤3600], min, max, sum }
  DynamoDB:      PK=SENSOR#s#2026-08-28  SK=<ts>          TTL 90d
  Cassandra:     ((sensor_id, day), ts DESC) TWCS
```

**Interviewer:** "Store readings from 1M sensors at 1/s; serve last-24h charts and current value; keep 90 days."

- Assumptions `(assume)`: 1M writes/s, reads: 10k dashboards/s asking last 24h (downsampled) + 50k/s "current value," 90-day retention, occasional monthly analytics.
- Entities: Sensor, Reading, Bucket (materialized), Rollup.

| AP# | Operation         | Inputs              | Freq       | Consistency               |
| --- | ----------------- | ------------------- | ---------- | ------------------------- |
| 1   | Ingest reading    | sensorId, ts, value | 1M/s       | at-least-once, idempotent |
| 2   | Current value     | sensorId            | 50k/s      | recent (≤ 1 s stale)      |
| 3   | Last 24 h series  | sensorId            | 10k/s      | eventual                  |
| 4   | Expire after 90 d | —                   | background | —                         |
| 5   | Monthly analytics | many sensors        | batch      | —                         |

- Store: Cassandra/Scylla or DynamoDB for the raw series (append at 1M/s is the deciding number — a single Postgres won't); Redis or a `latest` item for AP2; S3/Delta via stream for AP5. MongoDB bucket pattern is the answer if the interviewer wants Mongo.
- Key design (DynamoDB): `PK=SENSOR#s#<day>`, `SK=<ts>`; 86,400 items/day/sensor ≈ well under 10 GB; 1 write/s/sensor is far under the 1,000 WCU partition cap, so no sharding. Writes are naturally idempotent (`PutItem` on the same `(PK,SK)` overwrites) — replay-safe.
- AP2: `SENSOR#s / LATEST` item updated with condition `ts < :new` (rejects out-of-order late data), or Redis `SET sensor:s:latest` with the same guard in Lua.
- AP3: query today + yesterday partitions; for charts, read a pre-aggregated `ROLLUP#5m` series (Streams → Lambda writes 5-minute min/max/avg) so 24 h = 288 points, not 86,400.
- AP4: TTL attribute = ts + 90 d; DynamoDB TTL deletes are free and asynchronous (within ~48 h, `DynamoDB docs, 2026-01`) — filter expired-but-present items on read. Cassandra: cell TTL + TWCS drops whole SSTables without tombstone scanning.
- Mongo bucket variant: one document per sensor-hour, `$push` readings with `$inc count`, pre-computed `min/max/sum`; 3,600 readings ≈ 100 KB — under 16 MB; upsert on `{sensorId, hourStart}`. Index entries drop 3,600× vs. per-reading documents.
- Cost line (DynamoDB): 1M WCU/s on-demand is order of magnitude $1M+/month — say it, and say that at this scale self-run Cassandra/Scylla or Kafka→S3 ingestion with a hot-window store is what actually gets built.
- 🗣 "Partition by sensor and day, sort by time, write-time rollups for charts, a guarded `latest` item for current value, TTL for retention."

---

## 6. Social Graph + Feed

```
  USER#a ┬ META
         ├ FOLLOWS#b        (a → b)          GSI1: FOLLOWER#b / USER#a  (reverse)
         └ FEED#<ts>#<postId>  (materialized inbox, fan-out on write)
  POST#p ─ META
```

**Interviewer:** "Design follow relationships and a home timeline."

- Assumptions `(assume)`: 50M users, avg 200 follows, max 20M followers (celebrity), 5k posts/s, 500k timeline reads/s, timeline = last 100 posts from followees.
- Entities: User, Follow (edge), Post, FeedEntry.

| AP# | Operation                         | Inputs            | Freq   | Consistency        |
| --- | --------------------------------- | ----------------- | ------ | ------------------ |
| 1   | Follow / unfollow                 | a, b              | 2k/s   | strong             |
| 2   | Is a following b?                 | a, b              | 100k/s | strong             |
| 3   | List followees / followers, paged | userId            | 20k/s  | eventual           |
| 4   | Post                              | authorId, content | 5k/s   | strong             |
| 5   | Home timeline latest 100          | userId            | 500k/s | eventual (seconds) |
| 6   | Follower count                    | userId            | 100k/s | eventual           |

- Store: DynamoDB (edges, feed inboxes) + Redis (hot timelines, counts) + Streams → fan-out workers.

| Entity      | PK       | SK                        | GSI1PK       | GSI1SK   |
| ----------- | -------- | ------------------------- | ------------ | -------- |
| Follow edge | `USER#a` | `FOLLOWS#b`               | `FOLLOWER#b` | `USER#a` |
| Feed entry  | `USER#a` | `FEED#<ts>#<postId>`      | —            | —        |
| Post        | `POST#p` | `META`                    | `AUTHOR#u`   | `<ts>`   |
| Counters    | `USER#b` | `COUNT#followers#<shard>` | —            | —        |

- AP2 is a `GetItem` on the edge (strong). AP3 forward = `Query PK=USER#a begins_with FOLLOWS#`; reverse via GSI1 (eventual — a just-followed user may not appear for ms).
- AP5 fan-out on write: post → Streams → worker reads followers via GSI1 pages → `BatchWriteItem` feed entries (25 per batch). Celebrity with 20M followers = 20M writes per post — cap: users above F followers (`assume` 10k) are **not** fanned out; their posts are merged at read time (hybrid, the published Twitter approach). Feed entries carry TTL (30 d) and are trimmed to the newest 1,000 per user by the worker.
- AP6: sharded counter items, `ADD` atomic increments; sum on read or cached in Redis.
- Timeline read: Redis `ZSET feed:{userId}` as the hot copy (top 1,000), DynamoDB inbox as fallback/rebuild source; merge in celebrity posts from `AUTHOR#u` GSI for the user's followed celebrities (bounded — most users follow few).
- Hot partition: `USER#celebrity` partition holds 20M GSI1 entries → far beyond 10 GB — must not hold followers under one PK in the base table; the GSI1 partition `FOLLOWER#b` also becomes huge — shard it (`FOLLOWER#b#<hash(a)%64>`) and page 64-way in the fan-out worker.
- Unfollow: delete edge; existing feed entries from b remain until TTL or a lazy filter — state the staleness choice.
- 🗣 "Adjacency list with a reversed GSI for the graph, fan-out on write into per-user inboxes with a celebrity cutoff, Redis for the hot timeline."

---

## 7. Multi-Tenant SaaS Hierarchy

```
  TENANT#t ┬ META
           ├ NODE#root        {parent: null}
           ├ NODE#f1          {parent: root, type: folder}
           └ NODE#d9          {parent: f1, type: doc, path: "/root/f1/"}
  GSI1: TENANT#t#PARENT#f1 / <name>     children listing
  GSI2: TENANT#t#OWNER#u  / <updatedAt>  my documents
```

**Interviewer:** "Design storage for a Google-Drive-like product: tenants, folders, documents, sharing."

- Assumptions `(assume)`: 100k tenants, largest tenant 5M nodes, depth ≤ 20, 10k reads/s, 1k writes/s, per-tenant isolation required, move/rename common.
- Entities: Tenant, Node (folder|doc), Permission, Version (content in S3).

| AP# | Operation                               | Inputs                    | Freq  | Consistency |
| --- | --------------------------------------- | ------------------------- | ----- | ----------- |
| 1   | List children of folder, sorted by name | tenant, folderId          | 5k/s  | strong-ish  |
| 2   | Get node + breadcrumb                   | tenant, nodeId            | 3k/s  | strong      |
| 3   | Move node                               | tenant, nodeId, newParent | 200/s | strong      |
| 4   | Rename                                  | tenant, nodeId            | 200/s | strong      |
| 5   | My docs, recent first                   | tenant, userId            | 1k/s  | eventual    |
| 6   | Can user X access node?                 | tenant, user, node        | 10k/s | strong      |

- Store: DynamoDB; tenant prefix on every key gives isolation and lets a tenant be exported/deleted by prefix. Very large tenants get sharded prefixes.
- Node item: `PK=TENANT#t, SK=NODE#<id>`, attrs `parentId`, `name`, `type`, `ancestors: [root, f1]` (bounded by depth ≤ 20 — embed is safe), `version`.
- AP1 via GSI1 `TENANT#t#PARENT#f1 / <name>`. Defeater: a folder with 1M children is a hot GSI partition — page it; if a tenant does that, shard by `#<hash(name)%8>`.
- AP2: one `GetItem`; breadcrumb from the embedded `ancestors` list — no recursive reads.
- AP3 move: `UpdateItem` node (condition `version = :v`) setting `parentId`, `ancestors`; **descendants' `ancestors` are stale** → background job via Streams rewrites descendants (bounded by subtree size), and reads that need exact paths for descendants recompute from `parentId` chain if `pathVersion` is behind. State it as the known eventual part.
- Alternative for AP3: materialized `path` string with `begins_with` on a GSI — moves rewrite every descendant synchronously (unbounded transaction) → rejected for large subtrees; adjacency (`parentId`) + async ancestor cache is the durable choice.
- AP6 permissions: `PK=TENANT#t, SK=PERM#<nodeId>#<principal>`; check node, then ancestors (from embedded list, ≤ 20 `BatchGetItem`) for inherited grants; cache resolved ACL in Redis with node-version in the key.
- Isolation: IAM condition `dynamodb:LeadingKeys` on `TENANT#t` prefixes for per-tenant credentials (`DynamoDB docs, 2026-01`) — say this for "how do you guarantee isolation."
- 🗣 "Adjacency list with a bounded ancestor cache embedded per node, a children GSI, async re-pathing on move, and tenant-prefixed keys enforced by IAM."

---

## 8. Leaderboard + Rate Limiter

```
  ZSET  lb:{game}:{season}         score → userId          top-N, rank
  HASH  user:{u}:stats             cumulative
  Lua   ratelimit:{tenant}:{route}  sliding window (ZSET of timestamps)
  Durable mirror: DynamoDB SCORE#game / USER#u {score}   ← rebuild source
```

**Interviewer:** "Design a real-time leaderboard for a game with 50M players, and an API rate limiter."

- Assumptions `(assume)`: 100k score updates/s, 200k rank reads/s, top-100 and "my rank ± 5" views, seasons reset weekly; rate limit 1,000 req/min per tenant across 50 API nodes.
- Entities: Player, Score (per season), Season, Tenant quota.

| AP# | Operation               | Inputs            | Freq   | Consistency    |
| --- | ----------------------- | ----------------- | ------ | -------------- |
| 1   | Submit score (keep max) | game, user, score | 100k/s | atomic         |
| 2   | Top 100                 | game              | 50k/s  | ≤ 1 s stale ok |
| 3   | My rank + neighbours    | game, user        | 150k/s | ≤ 1 s stale ok |
| 4   | Reset season            | game              | weekly | —              |
| 5   | Rate-limit check        | tenant, route     | 500k/s | atomic         |

- Store: Redis Cluster for AP1–5 hot path; DynamoDB as durable score record (Redis is rebuildable).
- AP1: `ZADD lb:{g}:{s} GT score user` (GT keeps the max) — one command, atomic. Mirror asynchronously via a stream or write DynamoDB first then Redis (score durability matters for prizes; Redis for ranking). Tie-break: `score * 2^20 + (2^20 − ageSeconds)` so earlier achievement ranks higher within the same score, if required.
- AP2: `ZREVRANGE 0 99 WITHSCORES`. AP3: `ZREVRANK` + `ZREVRANGE rank-5 rank+5`.
- Big-key risk: 50M members in one ZSET ≈ order of magnitude several GB on one shard; commands are O(log n) so latency is fine, but memory and resharding are the problem. Mitigation: per-region or per-league ZSETs (natural partition), or score-band sharding with rank = sum of counts in higher bands + rank within band (`ZCARD` per band). Season reset = new key, old key `UNLINK` (non-blocking), never `DEL` on a giant key.
- AP5 sliding window in Lua on `rl:{tenant}:{route}` ZSET: `ZREMRANGEBYSCORE key 0 now-60000; local n = ZCARD; if n < limit then ZADD key now uuid; PEXPIRE key 60000; return 1 else return 0`. Atomic across 50 API nodes because it runs on one shard; `{tenant}` tag keeps keys co-located. Memory = one entry per allowed request — for 1,000/min it's fine; for 1M/min use token bucket state in a HASH instead (constant memory).
- Fail policy: Redis down → fail-open with local per-node fallback limit (limit/50) for user-facing; fail-closed for abuse-sensitive routes. Say it explicitly.
- 🗣 "ZSET with `GT` for max-score semantics, rank in O(log n), shard by league or score band before the key gets big; rate limiting is one Lua script per tenant tag."

---

## 9. Idempotent Event / Audit Store

```
  Producer (at-least-once) ─▶ EVENT#<aggregateId> / <version>#<eventId>   cond: attribute_not_exists
                                └ Streams ─▶ projections (OpenSearch, Aurora), each idempotent on (aggregateId, version)
  DEDUP#<eventId>  TTL 7d   (for producers that can't carry a version)
```

**Interviewer:** "A pipeline delivers vendor records at-least-once. Store the events so consumers get each exactly once in order per instrument, and keep a queryable audit trail."

- Assumptions `(assume)`: 40k records/day today, 100× headroom; per-instrument ordering matters; audit queries: "history of instrument X," "what changed on date D"; 7-year retention.
- Entities: Instrument (aggregate), Event (immutable), Projection state, Dedup marker. This is the anchor project — say so.

| AP# | Operation                      | Inputs                                 | Freq        | Consistency        |
| --- | ------------------------------ | -------------------------------------- | ----------- | ------------------ |
| 1   | Append event (dedup)           | aggregateId, eventId, version, payload | 50/s → 5k/s | strong, idempotent |
| 2   | History for aggregate, ordered | aggregateId                            | 100/s       | strong             |
| 3   | Events by day (audit)          | date                                   | 10/s        | eventual           |
| 4   | Current state of aggregate     | aggregateId                            | 1k/s        | strong             |
| 5   | Replay to rebuild a projection | range                                  | rare        | —                  |

- Store: DynamoDB for events + current-state item; Streams for fan-out; Aurora/OpenSearch as projections (the existing polyglot split, justified per consumer).

| Entity        | PK                | SK                                 | GSI1PK           | GSI1SK           |
| ------------- | ----------------- | ---------------------------------- | ---------------- | ---------------- |
| Event         | `INSTR#i`         | `EVT#<version 0-padded>#<eventId>` | `DAY#2026-08-28` | `<ts>#<eventId>` |
| Current state | `INSTR#i`         | `STATE`                            | —                | —                |
| Dedup marker  | `DEDUP#<eventId>` | `META` (TTL)                       | —                | —                |

- AP1: `TransactWriteItems`: put event with `attribute_not_exists(PK)` (same version twice fails), update `STATE` with condition `version = :expected − 1` (enforces per-instrument order; out-of-order arrival → cancel, park in a retry queue keyed by aggregate), put `DEDUP#eventId` with `attribute_not_exists`. Retry of a duplicate delivery fails cleanly — that is the exactly-once _effect_.
- Answer to the open Glue question (records failing validation): they never reach this table — quarantine to a `REJECT#<runId>` partition (or S3 + a `REJECT` item with reason) with a sparse GSI `REJECTED#<day>`, retryable reasons re-driven by a job, terminal ones surfaced to a review queue. Say quarantine, not drop.
- AP2: `Query PK=INSTR#i begins_with EVT#` — ordered by 0-padded version (lexical = numeric). AP3 via GSI1 by day; the `DAY#` partition is low-cardinality at 5k/s → shard `DAY#<d>#<hash%16>`.
- Projections: Streams → Lambda; each sink write is `upsert where version < incoming` (Aurora `ON CONFLICT ... WHERE`, OpenSearch external versioning) so at-least-once stream delivery is safe; a nightly reconciliation compares `STATE.version` with each projection.
- Replay (AP5): read events by `INSTR#` prefix per aggregate or by `DAY#` range, feed the same idempotent projector. Streams retention is 24 h, so replay reads the table, not Streams.
- Retention: 7 years of events — cold tier via Streams → S3/Delta (that's the lakehouse); TTL nothing in the hot table until the cold copy is verified.
- 🗣 "Events are immutable, keyed by aggregate and version, written with existence and version conditions in one transaction — duplicates and out-of-order deliveries fail the condition instead of corrupting state."

---

## 10. Flash-Sale Inventory

```
  SKU#x ┬ STOCK#0  {qty: 250}      ─┐
        ├ STOCK#1  {qty: 250}       ├ sharded stock, conditional decrement
        ├ …                         │
        └ STOCK#7  {qty: 250}      ─┘
  RESERVATION#<orderId>  {sku, qty, expiresAt TTL}
```

**Interviewer:** "10,000 units, 1M people click buy in the first minute. Never oversell."

- Assumptions `(assume)`: 20k buy attempts/s peak on one SKU, ≤ 5 units per order, reservation held 10 minutes pending payment, slight under-sell acceptable, over-sell not.
- Entities: SKU stock, Reservation, Order (downstream).

| AP# | Operation                     | Inputs          | Freq       | Consistency        |
| --- | ----------------------------- | --------------- | ---------- | ------------------ |
| 1   | Reserve n units               | sku, orderId, n | 20k/s      | strong, atomic     |
| 2   | Confirm / release reservation | orderId         | 2k/s       | strong             |
| 3   | Display remaining             | sku             | 100k/s     | eventual (seconds) |
| 4   | Expire unpaid reservations    | —               | background | —                  |

- Store: DynamoDB with sharded conditional writes; Redis in front only for AP3 and admission control.
- Why sharding: one stock item is capped near 1,000 WCU/s; 20k/s attempts need ≥ 20 shards even if most fail — pick 32 (`assume`), stock split evenly, remainder to shard 0.
- AP1 sequence: 1) API picks shard `hash(orderId) % 32`; 2) `TransactWriteItems`: `UpdateItem STOCK#s` condition `qty >= :n` `SET qty = qty − :n`, plus `PutItem RESERVATION#orderId` with `attribute_not_exists` and TTL; 3) on `ConditionalCheckFailed`, try up to 2 other shards (random); 4) all fail → "sold out (retry later)"; 5) `ClientRequestToken` = orderId so client retries never double-reserve.
- Under-sell tolerance: stock stranded in shards while others show empty is the cost; a rebalancer moves stock between shards when a shard is empty and total > 0 (transaction: decrement donor, increment recipient). State the trade: exactness vs. throughput; at low volume use one item.
- AP2 confirm: transaction sets reservation `CONFIRMED` (condition `status = PENDING`) — stock already decremented. Release/expiry: reservation TTL → Streams (TTL deletes appear in Streams with `userIdentity.type = Service`, `DynamoDB docs, 2026-01`) → worker increments the originating shard (recorded in the reservation) with condition on a `released` marker to make it idempotent.
- AP3: Redis counter decremented alongside (approximate) or sum of shards every second by a job; label as approximate.
- Admission control: Redis token bucket lets ~2× stock worth of requests through per second; the rest get a queue position — protects DynamoDB from 1M/s and makes the sold-out UX deterministic. This is the boring answer that usually wins the round.
- Failure: transaction conflict storms on a shard → backoff with jitter; a shard's counter drifting from reservations → reconciliation job sums reservations vs. decrements.
- 🗣 "Conditional decrement on sharded stock items in a transaction with the reservation, idempotent by order id, TTL-driven release, and a token bucket in front so the store sees a bounded rate."

---

## 11. Cross-Question Drill Sheet

| #            | The number to say                 | The invariant mechanism            | The hot-key answer                      | The "what if AP changes" answer     |
| ------------ | --------------------------------- | ---------------------------------- | --------------------------------------- | ----------------------------------- |
| 1 Orders     | 1,000 WCU/partition; 100-item txn | txn + idempotency marker           | bucket SK by month for B2B              | new GSI + backfill                  |
| 2 Booking    | 15-min cells; 3 cells = 1 txn     | `status = FREE` condition per cell | provider partition is small             | rules-based availability alt        |
| 3 Chat       | 10-day buckets; ULID ids          | ordering by clustering             | shorter buckets / shard for hot channel | table-per-query                     |
| 4 Catalog    | 16 MB doc; one multikey index     | single-doc `$inc` with `$gte`      | hashed `sku` shard key                  | attribute pattern absorbs new specs |
| 5 IoT        | 86,400 items/day/sensor; TTL free | `ts < :new` on LATEST              | none at 1/s; rollups for reads          | S3 for analytics                    |
| 6 Feed       | 25/batch; celebrity cutoff        | edge `GetItem` strong              | shard `FOLLOWER#b#<n>`                  | hybrid pull at read                 |
| 7 Drive      | depth ≤ 20 ancestors              | `version` CAS on move              | shard children GSI                      | async re-path via Streams           |
| 8 Redis      | O(log n) ZSET; 16,384 slots       | Lua atomicity                      | league/score-band shards                | HASH token bucket                   |
| 9 Events     | 24 h Streams; 0-padded version    | existence + version conditions     | shard `DAY#` GSI                        | replay from table                   |
| 10 Inventory | 32 shards; 10-min TTL             | `qty >= :n` per shard              | sharding is the design                  | rebalancer                          |

Exit criteria: for any row, produce the AP table, key table, and the invariant sentence in under 8 minutes without notes.

---

## 12. References

1. AWS — DynamoDB best practices (partition keys, sparse indexes, transactions, TTL in Streams) — https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html
2. Alex DeBrie — DynamoDB single-table design and modeling examples — https://www.alexdebrie.com/posts/dynamodb-single-table/
3. Discord Engineering — "How Discord Stores Trillions of Messages" (2023) — https://discord.com/blog/how-discord-stores-trillions-of-messages
4. MongoDB — Building with Patterns (attribute, bucket, outlier, subset) — https://www.mongodb.com/docs/manual/data-modeling/design-patterns/
5. Redis — Rate limiting patterns and sorted sets — https://redis.io/docs/latest/develop/data-types/sorted-sets/
6. Twitter/X Engineering — timeline fan-out and the hybrid celebrity approach (Raffi Krikorian, "Timelines at Scale", InfoQ 2013) — https://www.infoq.com/presentations/Twitter-Timeline-Scalability/
