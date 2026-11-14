# 03db.04mongodb.06indexes Indexes

> An index turns a collection scan into a tree seek; selectivity, not existence, decides the cost.

## Index

- [1. How An Index Works](#1-how-an-index-works)
  - [1.1 B+ Tree, KeyString, RecordId](#11-b-tree-keystring-recordid)
  - [1.2 Compound Prefix And Sort Direction](#12-compound-prefix-and-sort-direction)
  - [1.3 Limits And Clustered Collections](#13-limits-and-clustered-collections)
- [2. Index Types](#2-index-types)
  - [2.1 Multikey](#21-multikey)
  - [2.2 Partial, Sparse, Time To Live (TTL)](#22-partial-sparse-time-to-live-ttl)
  - [2.3 Unique, Collation, Hashed](#23-unique-collation-hashed)
  - [2.4 Wildcard, Text, 2dsphere](#24-wildcard-text-2dsphere)
  - [2.5 The Index Set In Code](#25-the-index-set-in-code)
- [3. Text Search In Code](#3-text-search-in-code)
- [4. Lifecycle: Build, Hide, Drop](#4-lifecycle-build-hide-drop)
- [5. Decisions And Best Practices](#5-decisions-and-best-practices)
- [6. Failure Modes](#6-failure-modes)
- [Related](#related)

## 1. How An Index Works

Every index is a separate B+ tree mapping a key to a document handle.

### 1.1 B+ Tree, KeyString, RecordId

- **Plain idea**: a sorted lookup table from field values to "where the document is"
- **KeyString**: order-preserving byte encoding of the indexed Binary JavaScript Object Notation (BSON) values
  - Byte order = BSON canonical sort order ⇒ comparison is `memcmp`
  - Since 4.2 it removed the old 1024-byte index key limit
    - Limit: a 4 kilobytes (KB) key still wrecks page fanout ⇒ taller tree, more page reads
- **RecordId**: stable 64-bit handle to the document in the collection's row-store
  - Decoupled from physical location ⇒ a rewritten document does not touch secondary indexes
- **FETCH**: the second hop from RecordId to the document
- **Covered query**: every needed field is in the index ⇒ FETCH is skipped
- What it solves
  - `O(n)` scan → `O(log n)` descent plus a bounded range walk
  - `$sort` is free when index order matches ⇒ no in-memory blocking sort (100 megabytes (MB) limit)
- What is MongoDB-specific: paths into nested documents and inside arrays (multikey)

```text
find({status:"OPEN", ts:{$gt:T}}).sort({ts:1})
        |
        v  planner picks IXSCAN on {status:1, ts:1}
+------------------------------+
| INDEX (WiredTiger B+ tree)   |
| key = KeyString(status, ts)  |
| val = RecordId               |
+--------------+---------------+
               | RecordId  <- the FETCH hop
               v
+------------------------------+
| COLLECTION (row-store)       |
| key = RecordId, val = BSON   |
+------------------------------+
covered query: all fields in the index => FETCH elided
```

Notice the second hop: each non-covered result is one more random read into the collection tree.

- Index pages use prefix compression, not block compression
  - Why: index pages are traversed constantly; decompressing on every descent is too costly
- Every index competes for the same WiredTiger cache as documents
- Every index is an extra B+ tree write on every insert ⇒ write amplification

### 1.2 Compound Prefix And Sort Direction

- Keys are ordered left to right
- **Prefix rule**: `{a:1, b:1, c:1}` serves `{a}`, `{a,b}`, `{a,b,c}`
  - Not `{b}` or `{b,c}`
- Contiguous bounds only up to the first non-equality predicate
  - Everything after a range is a residual filter ⇒ `totalKeysExamined` inflates
- Field order rule = Equality, Sort, Range (ESR): see [07query-planner-explain](04mongodb.07query-planner-explain.md#3-esr-rule)
- Sort direction matters only for multi-field sorts
  - `{a:1, b:1}` serves `sort({a:1,b:1})` and `sort({a:-1,b:-1})` (walk backwards)
  - Not `sort({a:1, b:-1})`

| Query on `{a:1,b:1,c:1}` | Uses index? | Quality |
|---|---|---|
| `find({a:1})` | Yes, prefix | Fully bounded |
| `find({b:2})` | No | COLLSCAN or wasteful full index scan |
| `find({a:1, c:3})` | `a` only | `c` filters keys, not bounds |
| `find({a:1}).sort({b:1})` | Yes | Sort free inside `a=1` |
| `find({a:{$gt:1}, b:2})` | `a` only | ESR violation; fix = `{b:1, a:1}` |

- Same fields in another order = another index with other capabilities
  - "We already index those fields" does not answer "is this query fast"

### 1.3 Limits And Clustered Collections

- 64 indexes per collection, 32 fields per compound index (Limits & Thresholds, 8.0)
- **Clustered collection** (5.3+, `clusteredIndex` on `_id`)
  - Removes the FETCH hop for `_id` lookups
  - Cost: only `_id`; secondary indexes store the full `_id` ⇒ larger
  - Choose when `_id` point reads dominate and secondary indexes are few
  - Contrast InnoDB: always clustered; every secondary lookup = two descents

| Designer decision | Rejected | Cost |
|---|---|---|
| Secondary index → RecordId (non-clustered) | Clustered on `_id` like InnoDB | Every non-covered query pays a second lookup |
| Multikey (index into arrays) | Force normalization | Index size ∝ array length; no covering |
| Prefix compression on index pages | Block compression | Worse ratio than collection data |
| Clustered collections opt-in (5.3+) | Non-clustered only | Bigger secondary indexes |

## 2. Index Types

Each type has one mechanism and one defeater worth knowing.

### 2.1 Multikey

- Any document with an array at the indexed path ⇒ one entry per element
- The index is then flagged multikey permanently
- Defeaters
  - At most one array field per compound index
    - Both arrays in one document ⇒ `CannotIndexParallelArrays` (code 171)
  - Cannot cover a query: the array cannot be rebuilt from entries
  - Flag is not cleared when arrays disappear; only a rebuild clears it
  - Sort on a multikey field can still need a blocking sort
    - Index order is over elements, not documents
- Size = documents × average array length
  - A 12-element `tags` array ⇒ index 12x a scalar index
  - Index-to-data ratios above 1:1 from one multikey index are possible
- Correctness trap: per-element bounds
  - `{scores: {$gt: 80, $lt: 90}}` matches `[95, 85]`
    - Some element satisfies each predicate independently
  - `$elemMatch` requires one element to satisfy both; bounds are tighter
  - Passes tests with single-element arrays, fails in production
- Design move: index a bounded derived scalar (`primaryTag`, `tagCount`) instead

### 2.2 Partial, Sparse, Time To Live (TTL)

- **Partial** (`partialFilterExpression`): indexes only matching documents
  - Planner uses it only if it can prove the query implies the filter
  - Proof is syntactic and conservative
    - `{status:"OPEN"}` partial does not serve `{status: {$in: ["OPEN","NEW"]}}`
    - Never serves `{status: {$ne: "CLOSED"}}`
  - Win case: state machine where ~98% of rows are terminal and never queried
    - Not a 2x win: the difference between fitting in cache and not
  - Deciding variable: does every query on the path carry the predicate?
- **Sparse**: skips documents missing the field
  - Cannot serve a sort that must include missing-field documents
  - Largely superseded by partial
- **TTL** (`expireAfterSeconds`): a background thread deletes expired documents
  - Runs every ~60 s, on the primary only; deletes replicate via the oplog
  - Not prompt: documents can live minutes past expiry under load
    - Not a security control; readers still filter
  - Field must be a `Date` (or array of `Date`)
    - Wrong type ⇒ silently never expires
  - `expireAfterSeconds: 0` on a `purgeAt` field = "delete at this time"
  - Soft delete pattern: `deletedAt` + TTL on purge time + partial unique on `{deletedAt: {$exists: false}}`

### 2.3 Unique, Collation, Hashed

- **Unique**: constraint enforced by the index; violation = `DuplicateKey` (11000)
  - Missing/null counts as one value ⇒ only one document may lack the field
    - Usually you wanted partial + unique
  - Sharded: must be prefixed by the shard key, or it cannot be enforced globally
- **Collation** (`locale: "en", strength: 2`): case-insensitive comparison
  - The query must pass the same collation to use the index
  - `$regex /^x/i` or `$toLower` in a predicate cannot use a normal index ⇒ COLLSCAN
  - Alternative: store a normalized lowercase duplicate field
  - ⚠️ DocumentDB does not support collation
- **Hashed**: indexes `hash(value)`
  - No range queries, no sort help
  - Used for even shard distribution ([13sharding](04mongodb.13sharding.md))

### 2.4 Wildcard, Text, 2dsphere

- **Wildcard** (`$**` or `meta.$**`, 4.2+): indexes every path
  - For truly unknown or per-tenant custom fields
  - Bigger, slower, planner-conservative, no sort help
  - Compound with normal fields: limited support added later; verify per version
  - Not a substitute for knowing your access patterns
- **Text**: term index with stemming and stop words
  - One per collection; `weights` per field
  - Crude score, not Lucene relevance ⇒ use OpenSearch / Atlas Search if relevance is the product
  - `$text` cannot be hinted; limited combination with `$or`
- **2dsphere**: GeoJSON on a sphere (S2 cells)
  - `2d` (planar, legacy) and `2dsphere` are not interchangeable
- **Hidden** (`hidden: true`): maintained but invisible to the planner

### 2.5 The Index Set In Code

One idempotent method creates every index; each index names the query it serves.

**Java**

```java
// infra/_03db_04mongodb/MongoShowcase.java
public List<String> ensureIndexes() {
    List<String> names = new ArrayList<>();
    // E = customerId, S = createdAt desc, then _id desc as the keyset tiebreaker.
    names.add(orders.createIndex(
            Indexes.compoundIndex(Indexes.ascending("customerId"), Indexes.descending("createdAt"),
                    Indexes.descending("_id")),
            new IndexOptions().name(IDX_CUSTOMER_CREATED)));
    // Partial: only PENDING orders are indexed (a few % of the collection) -> small, cache-resident.
    // The planner uses it ONLY when the query provably implies status == "PENDING".
    names.add(orders.createIndex(
            Indexes.compoundIndex(Indexes.ascending("status"), Indexes.ascending("createdAt")),
            new IndexOptions().name(IDX_PENDING).partialFilterExpression(eq("status", OrderStatus.PENDING.name()))));
    // Multikey: one index entry per array element; can never cover a query.
    names.add(orders.createIndex(Indexes.ascending("items.sku"), new IndexOptions().name(IDX_ITEMS_SKU)));
    // Text: one per collection; term matching with a crude score, not relevance ranking.
    names.add(orders.createIndex(Indexes.text("note"), new IndexOptions().name(IDX_NOTE_TEXT)));
    // TTL: background thread deletes when purgeAt < now (runs ~every 60 s, primary only). Date type only.
    names.add(orders.createIndex(Indexes.ascending("purgeAt"),
            new IndexOptions().name(IDX_PURGE_TTL).expireAfter(0L, TimeUnit.SECONDS)));
    // Unique + case-insensitive: queries must pass the SAME collation to use it.
    names.add(customers.createIndex(Indexes.ascending("email"), new IndexOptions()
            .name(IDX_EMAIL_CI).unique(true)
            .collation(Collation.builder().locale("en").collationStrength(CollationStrength.SECONDARY).build())));
    // ... order_events {orderId: 1, count: 1} for the bucket pattern
    return names;
}
```

**Python**

```python
# app/infra/_03db_04mongodb.py
def ensure_indexes(self) -> list[str]:
    """Idempotent index set; each index names the query it serves (ESR = Equality, Sort, Range)."""
    orders = self.db[ORDERS]
    return [
        # E = customerId, S = createdAt desc, _id desc = keyset tiebreaker
        orders.create_index(
            [("customerId", ASCENDING), ("createdAt", DESCENDING), ("_id", DESCENDING)],
            name=IDX_CUSTOMER_CREATED,
        ),
        # Partial: only PENDING orders; used only when the query provably implies status == PENDING
        orders.create_index(
            [("status", ASCENDING), ("createdAt", ASCENDING)],
            name=IDX_PENDING,
            partialFilterExpression={"status": OrderStatus.PENDING.value},
        ),
        orders.create_index([("items.sku", ASCENDING)], name=IDX_ITEMS_SKU),  # multikey: never covers
        orders.create_index([("note", TEXT)], name=IDX_NOTE_TEXT),  # one text index per collection
        orders.create_index([("purgeAt", ASCENDING)], name=IDX_PURGE_TTL, expireAfterSeconds=0),  # Date only
        self.db[CUSTOMERS].create_index(
            [("email", ASCENDING)],
            name=IDX_EMAIL_CI,
            unique=True,
            collation=Collation(locale="en", strength=CollationStrength.SECONDARY),  # queries must match it
        ),
        # ... order_events [("orderId", 1), ("count", 1)]
    ]
```

**Catch**

- `createIndex` with the same name and spec is a no-op; same name, other spec ⇒ error 86
- Spring `@Indexed` annotations apply only with `auto-index-creation=true`
  - Prefer explicit index code run from a migration job (Mongock, mongosh)
- Never let a fleet of app instances race to build indexes on a large collection at startup
- PyMongo key lists are tuples, not dicts (dict order mistakes are silent)

## 3. Text Search In Code

`$text` sorted by `textScore` needs the text index and returns a crude relevance order.

**Java**

```java
// infra/_03db_04mongodb/MongoShowcase.java
// $text search sorted by relevance score. Catch: needs the text index; cannot be hinted.
public List<Order> searchNotes(String terms, int limit) {
    return orders.find(text(terms))
            .projection(Projections.metaTextScore("score"))
            .sort(metaTextScore("score"))
            .limit(limit)
            .maxTime(maxTimeMs, TimeUnit.MILLISECONDS)
            .map(OrderDocuments::toOrder)
            .into(new ArrayList<>());
}
```

**Python**

```python
# app/infra/_03db_04mongodb.py
def search_notes(self, terms: str, limit: int) -> list[Order]:
    """$text sorted by textScore; needs the text index, cannot be hinted."""
    cur = (
        self.orders.find({"$text": {"$search": terms}}, {"score": {"$meta": "textScore"}})
        .sort([("score", {"$meta": "textScore"})])
        .limit(limit)
        .max_time_ms(self.max_time_ms)
    )
    return [to_order(d) for d in cur]
```

**Catch**

- If relevance ranking is the product, project into OpenSearch / Atlas Search via a change stream
- Only anchored `^abc` regex prefixes use a normal index; `/abc/` scans

## 4. Lifecycle: Build, Hide, Drop

Builds are online but not free; drops are fast but rebuilds are slow.

- **Builds since 4.2**: one hybrid method
  - Exclusive lock only briefly at start and end; collection writable between
  - `{background: true}` is deprecated / ignored
- On a replica set the build runs on all members
  - Primary commits after a majority finish ⇒ duration = slowest member
  - "Online" is about availability, not resources: disk and cache saturate
  - A long build can push a secondary off the oplog window ([10replica-sets-oplog](04mongodb.10replica-sets-oplog.md))
- **Hide before drop**: hidden index is still maintained, ignored by the planner
  - Regression ⇒ unhide instantly
  - Drop + rebuild on a multi-terabyte (TB) collection = hours
- **`$indexStats`**: per-index `accesses.ops` since last restart
  - Counters reset on restart ⇒ snapshot into a time series over 35+ days
  - Monthly batch jobs hide in a single reading

**Java**

```java
// infra/_03db_04mongodb/MongoShowcase.java
// Hide before drop: the planner ignores a hidden index but it is still maintained, so un-hiding is
// instant. Dropping and rebuilding a multi-TB index is hours.
public void setIndexHidden(String indexName, boolean hidden) {
    db.runCommand(new Document("collMod", OrderDocuments.ORDERS)
            .append("index", new Document("name", indexName).append("hidden", hidden)));
}

// $indexStats: per-index access counters since the last restart. Snapshot them over 35+ days before
// trusting "unused": monthly jobs and restarts both fool a single reading.
public List<String> unusedIndexes() {
    List<String> unused = new ArrayList<>();
    for (Document s : orders.aggregate(List.of(new Document("$indexStats", new Document())))) {
        long ops = OrderDocuments.num(s.get("accesses", Document.class), "ops");
        if (ops == 0 && !"_id_".equals(s.getString("name"))) {
            unused.add(s.getString("name"));
        }
    }
    return unused;
}
```

**Python**

```python
# app/infra/_03db_04mongodb.py
def set_index_hidden(self, index_name: str, hidden: bool) -> None:
    """Hide before drop: still maintained, ignored by the planner, un-hide is instant."""
    self.db.command("collMod", ORDERS, index={"name": index_name, "hidden": hidden})

def unused_indexes(self) -> list[str]:
    """$indexStats counters reset on restart: snapshot them over 35+ days before trusting "unused"."""
    return [
        s["name"]
        for s in self.db[ORDERS].aggregate([{"$indexStats": {}}])
        if int(s["accesses"]["ops"]) == 0 and s["name"] != "_id_"
    ]
```

**Catch**

- `$indexStats` is per node: aggregate across members (secondary reads count too)
- An index used but owned by nobody you can name is often a Business Intelligence (BI) tool
- Redundancy check: `{a:1}` is subsumed by `{a:1,b:1}`
  - `{a:1,b:1}` and `{b:1,a:1}` are not redundant

## 5. Decisions And Best Practices

| Decision | Deciding variable |
|---|---|
| Which compound indexes | Query shapes × selectivity; follow ESR |
| How many indexes | Write amplification: one B+ tree write per index per insert |
| Index an array field | Average and p99 array length (10 000 elements = 10 000 entries) |
| Partial vs full | Predicate in ≥95% of queries and cuts the set ≥10x ⇒ partial |
| Hashed vs range shard key | See [13sharding](04mongodb.13sharding.md) |

| Option | Buys | Costs | Choose when |
|---|---|---|---|
| One wide compound | Serves many prefixes | Large keys, rigid order | Shapes share a stable prefix |
| Several narrow | Precise, small | Nx write cost; more plan candidates | Distinct access patterns |
| Wildcard | Query any field | Bigger, slower, no sort help | Truly ad-hoc / custom fields |
| Covering | Skips FETCH (often 2–5x fewer page reads, order of magnitude) | Index holds projected fields; impossible if multikey | Hot read, small projection |

- Rules (rule → failure it prevents)
  - Every production query has an `explain("executionStats")` with `keysExamined / nReturned` near 1
    - Prevents: an "IXSCAN" that is really a wide range scan plus post-filter
  - Past ~8 indexes on a write-hot collection, add one only by dropping one
    - Prevents: write amplification that surfaces as replication lag
  - `$indexStats` (over weeks) before dropping
    - Prevents: dropping the monthly job's index
  - TTL only on `Date` fields, verified with a canary document
    - Prevents: a TTL that never deletes and silent growth
  - Prefix unique indexes with the shard key on sharded collections
    - Prevents: discovering at shard time that uniqueness is unenforceable
  - Rolling or scheduled builds on very large collections
    - Prevents: "online" build saturating the primary
- `ordered: true` bulk inserts abort at the first `DuplicateKey`
  - Resend re-applies earlier writes ⇒ use `ordered: false` and reconcile ([05bulk-write](04mongodb.05bulk-write.md))

## 6. Failure Modes

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Multikey explosion | High-cardinality array indexed | `indexSizes` ≫ `size` in collStats | Index a bounded derived field |
| `CannotIndexParallelArrays` | Two array paths in one compound | Write error 171 | One array per compound index |
| TTL never fires | Field is a string, not `Date` | Count grows; `ttl.deletedDocuments` flat | Fix type + backfill; validator |
| Partial index unused | Predicate not provably a subset | `explain` COLLSCAN despite index | Match predicate exactly or full index |
| Blocking sort fails | `sort()` on unindexed field | Error 292; SORT stage with memLimit | Index the sort; `allowDiskUse` (aggregation) |

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Write amplification | 12 indexes on insert-hot collection | Secondary lag; insert p99 | Consolidate via `$indexStats` |
| Build saturates node | Build on multi-TB collection | Disk saturation; possible election | Rolling build; off-peak |
| Index exists, does not help | `{tenantId:1}` + post-filter + in-memory sort | 2.1 M keys for 20 results | ESR compound `{tenantId, status, createdAt}` |
| Case-insensitive scan | `$regex /^x/i` or `$toLower` | COLLSCAN on indexed field | Collation index + same query collation |

- Exception handling
  - `DuplicateKey` (11000): terminal for that write unless the intent was an upsert
  - `CannotIndexParallelArrays`: terminal, structural
  - `ExceededMemoryLimit` on a blocking sort: terminal for that query shape; a design signal
- Historical (MongoDB 4.2 release notes): before KeyString, oversized keys failed inserts (`failIndexKeyTooLong`)
  - Earlier configurations silently left documents out of the index ⇒ incomplete results, no error
- Canonical failure pattern (not a specific incident): "the index that exists and doesn't help"
  → Dashboard query takes 8 s; `explain` shows IXSCAN; team blames the network  
  ⇒ `{tenantId:1}` with post-filter on `status` and in-memory sort on `createdAt`  
  ⇒ `totalKeysExamined` 2.1 M for `nReturned` 20  
  → Fix: `{tenantId:1, status:1, createdAt:-1}`  
  → Guardrail: Continuous Integration (CI) runs `explain` per registered shape, fails if keys/returned > 10

## Related

- [00index](04mongodb.00index.md)
- [07query-planner-explain](04mongodb.07query-planner-explain.md)
- [08pagination](04mongodb.08pagination.md)
- [13sharding](04mongodb.13sharding.md)
