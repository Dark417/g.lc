# 03db.04mongodb.01document-model-bson Document Model And Binary JavaScript Object Notation (BSON)

> A document is one typed, length-prefixed Binary JavaScript Object Notation (BSON) object of at most 16 megabytes (MB): know what that costs before you model.

## Index

- [1. BSON](#1-bson)
  - [1.1 Layout](#11-layout)
  - [1.2 Types And Sort Order](#12-types-and-sort-order)
  - [1.3 Field Names Are Stored Every Time](#13-field-names-are-stored-every-time)
- [2. ObjectId And Custom Ids](#2-objectid-and-custom-ids)
- [3. The 16 MB Cap](#3-the-16-mb-cap)
- [4. Money And Numeric Types](#4-money-and-numeric-types)
- [5. Schema Validation](#5-schema-validation)
- [6. Decisions And Best Practices](#6-decisions-and-best-practices)
- [7. Failure Modes](#7-failure-modes)
- [Related](#related)

## 1. BSON

BSON is binary JavaScript Object Notation (JSON) with real types and length prefixes; one document = one BSON object.

- Version anchor: MongoDB 8.0 docs unless a version tag says otherwise
- What it solves over JSON
  - JSON has no int64, binary, date, or decimal type
  - JSON numbers are all Institute of Electrical and Electronics Engineers (IEEE) 754 doubles ⇒ lossy
  - JSON has no length prefixes ⇒ a parser scans linearly to find field n
  - BSON lets the server read one field of a 200 kilobytes (KB) document without parsing it all
- What it replaced
  - Fixed-schema rows: a Data Definition Language (DDL) migration per shape change
  - Relational escape hatches for variable shape
    - Entity-Attribute-Value (EAV) tables: unindexable, join-explosive
    - Sparse wide tables: hundreds of NULL columns
    - `TEXT` blob: opaque to the query engine
- Fits: catalogs, Content Management System (CMS), per-tenant config, event/audit stores, Internet of Things (IoT) payloads, vendor-dictated shapes
- Wrong answer to
  - Multi-entity JOIN + aggregation over the whole corpus → warehouse (Athena / Redshift)
  - Domains where a broken referential invariant is an incident: no foreign keys, no cascades, at any version
- ⚠️ Defeater: if every document has the same 40 fields, you paid the flexibility tax for nothing

### 1.1 Layout

```text
document  ┌──────────┬────────────────────────────┬──────┐
          │ int32    │ element*                   │ 0x00 │
          │ totalLen │                            │ EOO  │
          └──────────┴────────────────────────────┴──────┘
element   ┌────────┬──────────────────┬────────────────────┐
          │ 1 byte │ cstring          │ value (nested =    │
          │ type   │ field name       │ length-prefixed)   │
          └────────┴──────────────────┴────────────────────┘
```

The length prefix is what lets a reader skip a whole subtree.

| Component | Job |
| --- | --- |
| Length prefix (int32, little-endian) | Skip a document or subtree without parsing |
| Type byte | Picks the value encoding and the cross-type sort order |
| Field-name cstring | Self-describing key; why documents are storage-heavy |
| `ObjectId` | Default `_id`; roughly monotonic 12-byte id |
| Canonical type order | Total order over mixed types, for indexes and `$sort` |

- Arrays are encoded as documents with keys `"0"`, `"1"`, `"2"`
  - Result: array elements carry key overhead
  - Result: positional operators (`$`, `$[]`, `$[i]`) exist
- A corrupt prefix fails at parse as `InvalidBSON`, never silently
- WiredTiger stores the BSON bytes opaquely; only the query layer interprets them
- Flow: driver → serialize → wire protocol (`OP_MSG`) → mongod → query layer / WiredTiger row-store

### 1.2 Types And Sort Order

BSON adds the types JSON lacks and defines one order across all of them.

- Added types: `Date`, `Binary`, `ObjectId`, `Decimal128`, `Int32` / `Int64`, `Regex`, `Timestamp` (replication)
- Canonical order, low → high (MongoDB "Comparison/Sort Order", 8.0)
  - `MinKey < Null < Numbers < String < Object < Array`
  - `< BinData < ObjectId < Boolean < Date < Timestamp < Regex < MaxKey`
- The four numeric types collapse into ONE sort class
  - `1` (int32) equals `1.0` (double) for queries and indexes
  - ⚠️ Not equal for `$type` filters
- Dates are millisecond precision
  - Truncate in the app before writing, or memory and storage disagree
  - The keyset cursor ([08pagination](04mongodb.08pagination.md)) depends on that equality

**Java**

```java
// infra/_03db_04mongodb/OrderDocuments.java
/** BSON Date is millisecond precision: truncate BEFORE writing so the in-memory value equals the stored one. */
public static Instant nowMillis() {
    return Instant.now().truncatedTo(ChronoUnit.MILLIS);
}

/** Numbers may arrive as int32 or int64 (mongosh writes int32/double): read through Number. */
static long num(Document d, String key) {
    Object v = d.get(key);
    return v == null ? 0L : ((Number) v).longValue();
}

static Instant instant(Document d, String key) {
    Date date = d.getDate(key); // the driver decodes BSON Date as java.util.Date
    return date == null ? null : date.toInstant();
}
```

**Python**

```python
# app/infra/_03db_04mongodb.py
def now_millis() -> datetime:
    """BSON Date is millisecond precision: truncate BEFORE writing so memory equals storage."""
    t = datetime.now(timezone.utc)
    return t.replace(microsecond=t.microsecond // 1000 * 1000)
```

**Catch**

- Java `Instant.now()` has micro/nanosecond precision; the stored value does not
- PyMongo returns naive datetimes unless the client sets `tz_aware=True` (`get_client` does)
- Python `int` is written as int32 or int64 by size; read through `int(...)`, never assume

### 1.3 Field Names Are Stored Every Time

There is no per-collection schema dictionary; every document repeats every key.

- 100 M documents × `transactionSettlementDate` (24 bytes) ≈ 2.4 gigabytes (GB) of names before compression
- Snappy block compression recovers most of it on disk
- It does NOT recover it in
  - WiredTiger cache page images (decompressed)
  - Network payloads
- Deciding variable: `document_count × name_bytes` vs WiredTiger cache size
  - Order of magnitude: 10⁸ docs × 30 fields × 15-byte names ≈ 45 GB resident if all hot
  - Below ~10⁸ documents, shortening names is premature
- If you must: map short names in the codec layer (`@BsonProperty`), keep readable app names

## 2. ObjectId And Custom Ids

`ObjectId` is a free, unique, roughly increasing 12-byte id; it is not a clock.

- Layout (since 3.4)
  - 4-byte big-endian Unix seconds
  - 5-byte per-process random value
  - 3-byte counter, randomly initialized
- You can read creation time to one-second resolution: `ObjectId.getTimestamp()`
- "Roughly monotonic" is the whole story
  - Within a second: no order
  - Across processes: no order
  - Clock skew can invert order across seconds
  - Result: `sort({_id: 1})` is a stable pagination key, not an event-ordering key
- Monotonic inserts land on the right edge of the `_id` B+ tree
  - Single replica set: good cache locality, one hot leaf page
  - Sharded with ranged `_id` key: one shard takes 100% of inserts ([13sharding](04mongodb.13sharding.md))
- `_id` is immutable: changing it fails with code 66

| Option | Buys | Costs | Choose when |
| --- | --- | --- | --- |
| `ObjectId` `_id` | Free unique id, insert locality, embedded timestamp | Meaningless to the business | Default |
| Natural key (International Securities Identification Number (ISIN), `tenantId+date`) | One fewer unique index; free idempotent upserts | Immutable forever; rule change = rewrite | Key is truly immutable and you upsert by it |
| Hashed `_id` | Even shard distribution | No `_id` range queries; no insert locality | Sharded, insert-heavy, no range scans |

**Java**

```java
// infra/_03db_04mongodb/OrderDocuments.java
public static ObjectId objectId(String hex) {
    if (hex == null || !ObjectId.isValid(hex)) {
        throw new IllegalArgumentException("not an ObjectId: " + hex);
    }
    return new ObjectId(hex);
}
```

**Python**

```python
# app/infra/_03db_04mongodb.py
def object_id(hex_id: str) -> ObjectId:
    try:
        return ObjectId(hex_id)
    except (InvalidId, TypeError) as e:
        raise ValueError(f"not an ObjectId: {hex_id}") from e
```

**Catch**

- A malformed id is the caller's error ⇒ Hypertext Transfer Protocol (HTTP) 400, not 500
- The ledger in this slice uses the payment id as `_id` on purpose: retries converge ([11read-write-concern](04mongodb.11read-write-concern.md))

## 3. The 16 MB Cap

One document is hard-capped at 16 MB (MongoDB Limits & Thresholds, 8.0).

- Why the cap exists
  - Bounds server memory per operation
  - Bounds the wire payload
  - Bounds one oplog entry
  - Lets the server materialize a whole document ⇒ single-document updates are atomic with no transaction
- Hitting it means the model is wrong
  - Split the growing array into a child collection
  - Or bucket it ([03schema-design](04mongodb.03schema-design.md#4-bucket))
- Design budget: an order of magnitude lower (~1 MB)
  - Real constraint is the cache: reading one field of a 5 MB doc pulls 5 MB of pages
- Measure with `$bsonSize`; alert at ~4 MB p99, a quarter of the cap

**Java**

```java
// infra/_03db_04mongodb/MongoAdmin.java
// Document-size distribution via $bsonSize: alert at ~4 MB p99, a quarter of the 16 MB cap, so there is
// time for a migration. Full scan: run it on a secondary / analytics node with allowDiskUse.
public Document documentSizeStats(String collection) {
    return ConsistencyProfiles.analytics(db, collection).aggregate(List.of(
                    Aggregates.project(new Document("size", new Document("$bsonSize", "$$ROOT"))),
                    Aggregates.group(null,
                            Accumulators.avg("avgBytes", "$size"),
                            Accumulators.max("maxBytes", "$size"),
                            Accumulators.sum("docs", 1))))
            .allowDiskUse(true)
            .first();
}
```

**Python**

```python
# app/infra/_03db_04mongodb.py
def document_size_stats(self, collection: str) -> Doc:
    """$bsonSize distribution; alert near 4 MB p99. Full scan: analytics member, allowDiskUse."""
    pipeline: list[Doc] = [
        {"$project": {"size": {"$bsonSize": "$$ROOT"}}},
        {"$group": {"_id": None, "avgBytes": {"$avg": "$size"}, "maxBytes": {"$max": "$size"}, "docs": {"$sum": 1}}},
    ]
    return next(analytics_collection(self.db, collection).aggregate(pipeline, allowDiskUse=True), {})
```

**Catch**

- `BSONObjectTooLarge` (code 10334) fails WRITES, not reads; retrying sends the same bytes
- A read-modify-write consumer on an oversized doc fails forever; a naive retry spins (poison pill)
- Guardrail layers
  - Write time: `$jsonSchema` `maxItems` on growable arrays (fails fast at the producer)
  - Continuous: the size histogram above, on a secondary
  - Structural: bucket pattern; the only layer that holds once monitors get muted
- ⚠️ A per-write `$bsonSize` check in app code is bypassable and duplicates the validator

## 4. Money And Numeric Types

Never store money as a double; this slice uses int64 cents.

- `double` cannot represent 0.1; errors accumulate in `$sum`
- Options
  - int64 minor units + currency code: exact in every driver, loud when wrong ✅ default
  - `Decimal128`: IEEE-754-2008 decimal, 34 significant digits
- `Decimal128` sharp edges
  - Java maps to `BigDecimal`; JavaScript (JS) has no native decimal (easy to `Number()` away)
  - One double operand widens the whole expression to double, silently
  - One legacy double document poisons a `$sum`
- Choose `Decimal128` only for sub-minor-unit precision: Foreign Exchange (FX) rates, bond unit prices
- Never store two numeric types in one field across documents
  - Prevents astonishing sort/range results and `$type` filters that miss rows

**Java**

```java
// domain/_03db_04mongodb/LineItem.java
/**
 * One embedded line item: bounded (an order has tens of items, not millions), read and written with its order.
 * - Money is int64 minor units (cents): exact in every driver, loud when wrong; never a double.
 */
public record LineItem(String sku, int qty, long priceCents) {
    // ...
    public long subtotalCents() {
        return qty * priceCents;
    }
}
```

**Python**

```python
# app/domain/_03db_04mongodb.py
@dataclass(frozen=True)
class LineItem:
    sku: str
    qty: int
    price_cents: int

    @property
    def subtotal_cents(self) -> int:
        return self.qty * self.price_cents
```

**Catch**

- `recomputeTotal` multiplies int64 by int64 server-side; a `$mul` by 0.9 would produce a double

## 5. Schema Validation

A `$jsonSchema` validator makes the server enforce shape for every producer.

- Prevents slow drift: one producer writes `status: "ACTIVE"`, another `status: {code: 1}`
  - Surfaces months later as an index that no longer covers
- `validationLevel`
  - `strict`: every insert and update checked
  - `moderate`: existing invalid docs may stay invalid; new and valid docs are checked
- `validationAction: "error"` rejects; `"warn"` only logs
- Failure = `DocumentValidationFailure` (code 121), terminal for that write
- Limit: cannot express "total document bytes", only array cardinality

**Java**

```java
// infra/_03db_04mongodb/MongoShowcase.java
public void applyOrderValidator() {
    Document schema = Document.parse("""
            { $jsonSchema: {
                bsonType: "object",
                required: ["customerId", "status", "items", "totalCents", "createdAt", "version"],
                properties: {
                  customerId: { bsonType: "string" },
                  status:     { enum: ["PENDING", "PAID", "SHIPPED", "DELIVERED", "CANCELLED"] },
                  items:      { bsonType: "array", minItems: 1, maxItems: 100, /* ... */ },
                  totalCents: { bsonType: ["int", "long"] },
                  createdAt:  { bsonType: "date" },
                  version:    { bsonType: ["int", "long"] }
            } } }""");
    try {
        db.createCollection(OrderDocuments.ORDERS, new CreateCollectionOptions().validationOptions(
                new ValidationOptions().validator(schema)
                        .validationLevel(ValidationLevel.MODERATE)
                        .validationAction(ValidationAction.ERROR)));
    } catch (MongoCommandException e) {
        if (e.getErrorCode() != MongoErrors.NAMESPACE_EXISTS) {
            throw e;
        }
        // Collection exists: change the validator in place.
        db.runCommand(new Document("collMod", OrderDocuments.ORDERS)
                .append("validator", schema)
                .append("validationLevel", "moderate")
                .append("validationAction", "error"));
    }
}
```

**Python**

```python
# app/infra/_03db_04mongodb.py
def apply_order_validator(self) -> None:
    """$jsonSchema validator, moderate level: existing invalid docs are skipped, new writes are checked."""
    schema = {"$jsonSchema": {"bsonType": "object", "required": [...], "properties": {...}}}  # same as Java
    try:
        self.db.create_collection(ORDERS, validator=schema, validationLevel="moderate", validationAction="error")
    except CollectionInvalid:  # already exists: change the validator in place
        self.db.command("collMod", ORDERS, validator=schema, validationLevel="moderate", validationAction="error")
```

**Catch**

- `bsonType: ["int", "long"]` accepts both; mongosh literals are int32 unless `NumberLong(...)`
- Type-varying documents: branch with `oneOf` on a discriminator (`instrumentType`)
- Add the validator once the shape stabilizes, not on day one of a prototype

## 6. Decisions And Best Practices

The designers fixed some trade-offs; you own the rest.

| Designers chose | Rejected | Cost you pay |
| --- | --- | --- |
| Self-describing documents | Schema dictionary (Avro-style) | Storage; no compile-time contract |
| 16 MB hard cap | Unbounded documents | Unbounded arrays become a design-time problem |
| Binary with length prefixes | Text JSON on disk | Not human-readable; needs a driver |
| Arrays as integer-keyed docs | Native array encoding | Per-element key overhead |

| You decide | Deciding variable |
| --- | --- |
| Custom `_id` vs `ObjectId` | Immutable, unique business key you also query by? |
| Short vs descriptive names | `docs × name bytes` vs cache; premature below ~10⁸ docs |
| Embed vs reference | Cardinality and update locality ([03schema-design](04mongodb.03schema-design.md)) |
| int64 cents vs `Decimal128` | Need sub-minor-unit precision? Default int64 |

- Best practices (rule → failure prevented)
  - Bound every growing array → `BSONObjectTooLarge` on the hottest documents
  - One numeric type per field → wrong sort/range results, missed `$type` rows
  - Validator on stable shapes → silent shape drift breaking index coverage
  - No business meaning in `ObjectId` time → ordering bugs from skew
  - Sanitize `$` and `.` in third-party keys at ingest → paths unaddressable by dot notation (accepted since 5.0)
- Raw vendor payload next to the normalized doc?
  - For: audit and replay without refetching
  - Against: 2–3× doc size pulled through cache on every normalized read
  - ✅ Split: raw in Simple Storage Service (S3; write-once, read-rarely), key stored on the hot doc

## 7. Failure Modes

| Failure | Trigger | Detect | Fix |
| --- | --- | --- | --- |
| `BSONObjectTooLarge` | Unbounded array crosses 16 MB | Error 10334; size p99 trending up | Bucket pattern; child collection |
| Working-set blowup | Wide docs × huge count | `bytes read into cache` rising | Shorter hot names; project less; more Random-Access Memory (RAM) |
| Silent precision loss | Money as double; `$toDouble` in `$sum` | Reconciliation break only | int64 cents; `Decimal128` end-to-end |
| Mixed-type field | Two producers, two types | `keysExamined ≫ nReturned` | Validator + backfill |
| `$` / `.` in keys | Raw third-party JSON | Field readable, not queryable | Escape at ingest |

- Canonical pattern: the unbounded comment array
  - Symptom: writes fail on a few documents, the most popular ones
  - Cause: `comments: []` embedded with no cap
  - Fix: buckets `{parentId, seq, comments: [≤500]}` + index `{parentId: 1, seq: -1}`
  - Guardrail: size histogram alert at 4 MB, not 16 MB
- Exception handling
  - Size and validation errors are terminal
  - `WriteConflict` is retried internally outside transactions; inside one it is `TransientTransactionError` ([12transactions](04mongodb.12transactions.md))

## Related

- [00index](04mongodb.00index.md)
- [02wiredtiger-storage](04mongodb.02wiredtiger-storage.md)
- [03schema-design](04mongodb.03schema-design.md)
