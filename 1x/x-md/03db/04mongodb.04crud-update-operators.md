# 03db.04mongodb.04crud-update-operators Create, Read, Update, Delete (CRUD) And Update Operators

> Change documents in place with atomic operators instead of read-modify-write.

## Index

- [1. Insert And Find](#1-insert-and-find)
- [2. Atomic Update Operators](#2-atomic-update-operators)
- [3. Positional And Array Filters](#3-positional-and-array-filters)
- [4. Pipeline Updates And Counters](#4-pipeline-updates-and-counters)
- [5. Queue Claim And Optimistic Lock](#5-queue-claim-and-optimistic-lock)
- [6. Delete](#6-delete)
- [Related](#related)

## 1. Insert And Find

Single-document writes are atomic; that is the unit to design around.

- `_id` is an `ObjectId` by default: 4-byte timestamp + random + counter ⇒ roughly time-ordered
- `$elemMatch` makes several conditions apply to the **same** array element

```java
// infra/_03db_04mongodb/MongoShowcase.java
// Embed + extended reference: items live inside the order, the customer's name is copied onto it.
// One insert, one document, atomic by construction. Catch: insertOne mutates nothing else; a crash
// after it but before a follow-up write leaves no partial order.
public Order insertOrder(NewOrder o) {
    Instant now = OrderDocuments.nowMillis();
    Document doc = OrderDocuments.newOrderDocument(new ObjectId(), o, now);
    orders.insertOne(doc);
    return OrderDocuments.toOrder(doc);
}
```

```python
# app/infra/_03db_04mongodb.py
def insert_order(self, o: NewOrder) -> Order:
    """Embed items + copy the customer name: one document, atomic by construction."""
    doc = new_order_document(ObjectId(), o, now_millis())
    self.orders.insert_one(doc)  # also sets doc["_id"] if missing (PyMongo mutates the dict)
    return to_order(doc)
```

```java
// infra/_03db_04mongodb/MongoShowcase.java
// $elemMatch: ONE array element must satisfy both predicates. Without it, {items.sku: X, items.qty: {$gte: n}}
// matches when different elements satisfy each part. Projection drops the free-text note.
public List<Order> findOpenOrdersWithSku(String sku, int minQty, int limit) {
    return orders.find(and(
                    in("status", OrderStatus.PENDING.name(), OrderStatus.PAID.name()),
                    elemMatch("items", and(eq("sku", sku), gte("qty", minQty)))))
            .projection(Projections.exclude("note"))
            .sort(orderBy(descending("createdAt"), descending("_id"))) // _id = tiebreaker, stable order
            .limit(limit)
            .maxTime(maxTimeMs, TimeUnit.MILLISECONDS)
            .map(OrderDocuments::toOrder)
            .into(new ArrayList<>());
}
```

```python
# app/infra/_03db_04mongodb.py
def find_open_orders_with_sku(self, sku: str, min_qty: int, limit: int) -> list[Order]:
    """$elemMatch: ONE element must satisfy both predicates (not "some element each")."""
    cur = (
        self.orders.find(
            {
                "status": {"$in": [OrderStatus.PENDING.value, OrderStatus.PAID.value]},
                "items": {"$elemMatch": {"sku": sku, "qty": {"$gte": min_qty}}},
            },
            {"note": 0},  # projection is the 2nd positional argument
        )
        .sort([("createdAt", DESCENDING), ("_id", DESCENDING)])  # list of tuples, not a dict
        .limit(limit)
        .max_time_ms(self.max_time_ms)
    )
    return [to_order(d) for d in cur]
```

## 2. Atomic Update Operators

Operators run inside the document lock, so concurrent writers never lose updates.

- `$push`, `$inc`, `$set`, `$currentDate` combine into one atomic update
- `findOneAndUpdate` with `ReturnDocument.AFTER` returns the new state in the same round trip

```java
// infra/_03db_04mongodb/MongoShowcase.java
// $push + $inc + $currentDate in ONE atomic update; the filter bounds the array ("items.99" must not exist).
// Returns the document AFTER the update: no read-after-write round trip.
public Optional<Order> addItem(String orderId, LineItem item) {
    Document after = orders.findOneAndUpdate(
            and(eq("_id", OrderDocuments.objectId(orderId)),
                    eq("status", OrderStatus.PENDING.name()),
                    exists("items." + (NewOrder.MAX_ITEMS - 1), false)),
            Updates.combine(
                    Updates.push("items", OrderDocuments.itemDocument(item)),
                    Updates.inc("totalCents", item.subtotalCents()),
                    Updates.inc("version", 1L),
                    Updates.currentDate("updatedAt")),
            new FindOneAndUpdateOptions().returnDocument(ReturnDocument.AFTER));
    return Optional.ofNullable(after).map(OrderDocuments::toOrder);
}
```

```python
# app/infra/_03db_04mongodb.py
def add_item(self, order_id: str, item: LineItem) -> Order | None:
    """$push + $inc + $currentDate in one atomic update; the filter bounds the array."""
    d = self.orders.find_one_and_update(
        {
            "_id": object_id(order_id),
            "status": OrderStatus.PENDING.value,
            f"items.{MAX_ITEMS - 1}": {"$exists": False},
        },
        {
            "$push": {"items": item_document(item)},
            "$inc": {"totalCents": item.subtotal_cents, "version": 1},
            "$currentDate": {"updatedAt": True},
        },
        return_document=ReturnDocument.AFTER,
    )
    return to_order(d) if d else None
```

## 3. Positional And Array Filters

Update one array element by match, or many by named filter.

- `$` = first element matched by the query filter
- `$[name]` + `arrayFilters` = every element matching the named condition

```java
// infra/_03db_04mongodb/MongoShowcase.java
// Positional $: updates the FIRST element matched by the query, so the array field must be in the filter.
// The total is then recomputed by a pipeline update instead of trusting client arithmetic.
public Optional<Order> incrementItemQty(String orderId, String sku, int by) {
    UpdateResult r = orders.updateOne(
            and(eq("_id", OrderDocuments.objectId(orderId)), eq("items.sku", sku)),
            Updates.combine(Updates.inc("items.$.qty", by), Updates.inc("version", 1L)));
    return r.getMatchedCount() == 0 ? Optional.empty() : recomputeTotal(orderId);
}
```

```python
# app/infra/_03db_04mongodb.py
def increment_item_qty(self, order_id: str, sku: str, by: int) -> Order | None:
    """Positional $: the first element matched by the QUERY, so the array field must be in the filter."""
    r = self.orders.update_one(
        {"_id": object_id(order_id), "items.sku": sku},
        {"$inc": {"items.$.qty": by, "version": 1}},
    )
    return self.recompute_total(order_id) if r.matched_count else None
```

```java
// infra/_03db_04mongodb/MongoShowcase.java
// Filtered positional $[i] + arrayFilters: touch every element matching a named filter.
public long markBackordered(String orderId, Set<String> skus) {
    return orders.updateOne(
            eq("_id", OrderDocuments.objectId(orderId)),
            Updates.set("items.$[i].backordered", true),
            new UpdateOptions().arrayFilters(List.of(in("i.sku", skus))))
            .getModifiedCount();
}
```

```python
# app/infra/_03db_04mongodb.py
def mark_backordered(self, order_id: str, skus: set[str]) -> int:
    """Filtered positional $[i] + array_filters: every element matching the named filter."""
    return self.orders.update_one(
        {"_id": object_id(order_id)},
        {"$set": {"items.$[i].backordered": True}},
        array_filters=[{"i.sku": {"$in": sorted(skus)}}],
    ).modified_count
```

## 4. Pipeline Updates And Counters

An update can be an aggregation pipeline, so a field can be computed from other fields.

- `recomputeTotal` sums the items array on the server, no read needed
- Counter document + `$inc` + upsert = a gap-free-ish sequence
  - Catch: one hot document serializes all writers; prefer ObjectId or Universally Unique Identifier (UUID) unless a human-readable number is required

```java
// infra/_03db_04mongodb/MongoShowcase.java
// Pipeline update (4.2+): the new value is computed from other fields of the same document, server-side.
// Integer arithmetic only: $multiply on int64 stays int64; one double operand would widen everything.
public Optional<Order> recomputeTotal(String orderId) {
    List<Bson> pipeline = List.of(Document.parse("""
            { $set: { totalCents: { $sum: { $map: { input: "$items",
                        in: { $multiply: ["$$this.qty", "$$this.priceCents"] } } } },
                      updatedAt: "$$NOW" } }"""));
    Document after = orders.findOneAndUpdate(eq("_id", OrderDocuments.objectId(orderId)), pipeline,
            new FindOneAndUpdateOptions().returnDocument(ReturnDocument.AFTER));
    return Optional.ofNullable(after).map(OrderDocuments::toOrder);
}
```

```python
# app/infra/_03db_04mongodb.py
def recompute_total(self, order_id: str) -> Order | None:
    """Pipeline update (4.2+): compute from other fields server-side; int arithmetic stays int."""
    pipeline = [
        {
            "$set": {
                "totalCents": {
                    "$sum": {"$map": {"input": "$items", "in": {"$multiply": ["$$this.qty", "$$this.priceCents"]}}}
                },
                "updatedAt": "$$NOW",
            }
        }
    ]
    d = self.orders.find_one_and_update(
        {"_id": object_id(order_id)}, pipeline, return_document=ReturnDocument.AFTER
    )
    return to_order(d) if d else None
```

```java
// infra/_03db_04mongodb/MongoShowcase.java
// Atomic counter: findOneAndUpdate + upsert + $inc returns the new value in one round trip.
// Catch: one hot document serializes every caller (write conflicts); shard the counter if it is hot.
public long nextSequence(String name) {
    Document d = db.getCollection(OrderDocuments.COUNTERS).findOneAndUpdate(
            eq("_id", name),
            Updates.combine(Updates.inc("seq", 1L), Updates.setOnInsert("createdAt", OrderDocuments.nowMillis())),
            new FindOneAndUpdateOptions().upsert(true).returnDocument(ReturnDocument.AFTER));
    return OrderDocuments.num(d, "seq");
}
```

```python
# app/infra/_03db_04mongodb.py
def next_sequence(self, name: str) -> int:
    """Atomic counter: upsert + $inc returns the new value. A hot counter serializes callers."""
    d = self.db[COUNTERS].find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}, "$setOnInsert": {"createdAt": now_millis()}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return int(d["seq"])
```

## 5. Queue Claim And Optimistic Lock

`findOneAndUpdate` turns a collection into a work queue; a version field turns updates into compare-and-set.

- Claim: filter `status=PENDING`, sort oldest, set `status=PROCESSING` + worker ⇒ two workers never get the same order
- Optimistic lock: filter includes `version = expected`; zero matches ⇒ someone else won

```java
// infra/_03db_04mongodb/MongoShowcase.java
// Work-queue claim: find the oldest unclaimed PENDING order and claim it atomically. Two workers can
// never claim the same order because the filter (claimedBy absent) and the $set are one atomic step.
public Optional<Order> claimOldestPending(String worker) {
    Document d = orders.findOneAndUpdate(
            and(eq("status", OrderStatus.PENDING.name()), exists("claimedBy", false)),
            Updates.combine(Updates.set("claimedBy", worker), Updates.currentDate("claimedAt")),
            new FindOneAndUpdateOptions()
                    .sort(ascending("createdAt"))       // served by the partial pending index
                    .returnDocument(ReturnDocument.AFTER));
    return Optional.ofNullable(d).map(OrderDocuments::toOrder);
}
```

```python
# app/infra/_03db_04mongodb.py
def claim_oldest_pending(self, worker: str) -> Order | None:
    """Work-queue claim: filter + $set are one atomic step, so two workers never claim the same order."""
    d = self.orders.find_one_and_update(
        {"status": OrderStatus.PENDING.value, "claimedBy": {"$exists": False}},
        {"$set": {"claimedBy": worker}, "$currentDate": {"claimedAt": True}},
        sort=[("createdAt", ASCENDING)],  # served by the partial pending index
        return_document=ReturnDocument.AFTER,
    )
    return to_order(d) if d else None
```

```java
// infra/_03db_04mongodb/MongoShowcase.java
// Optimistic lock: the version is part of the filter; no match = someone else won (or no such order).
// No transaction needed: a single-document update is atomic.
public Order changeStatusWithVersion(String orderId, OrderStatus status, long expectedVersion) {
    ObjectId id = OrderDocuments.objectId(orderId);
    Document after = orders.findOneAndUpdate(
            and(eq("_id", id), eq("version", expectedVersion)),
            Updates.combine(
                    Updates.set("status", status.name()),
                    Updates.inc("version", 1L),
                    Updates.currentDate("updatedAt")),
            new FindOneAndUpdateOptions().returnDocument(ReturnDocument.AFTER));
    if (after != null) {
        return OrderDocuments.toOrder(after);
    }
    // Disambiguate with one read: missing order vs. version moved (return the winner's state).
    Order current = findOrder(orderId).orElseThrow(() -> new OrderNotFoundException(orderId));
    throw new VersionConflictException(orderId, expectedVersion, current);
}
```

```python
# app/infra/_03db_04mongodb.py
def change_status_with_version(self, order_id: str, status: OrderStatus, expected_version: int) -> Order:
    """Optimistic lock: version in the filter; no match = someone else won, or no such order."""
    d = self.orders.find_one_and_update(
        {"_id": object_id(order_id), "version": expected_version},
        {"$set": {"status": status.value}, "$inc": {"version": 1}, "$currentDate": {"updatedAt": True}},
        return_document=ReturnDocument.AFTER,
    )
    if d:
        return to_order(d)
    current = self.find_order(order_id)  # one read to tell "missing" from "version moved"
    if current is None:
        raise OrderNotFoundError(order_id)
    raise VersionConflictError(order_id, expected_version, current)
```

## 6. Delete

Prefer soft delete for business data and Time To Live (TTL) indexes for expiring data.

- Soft delete keeps audit history; every read filter must exclude `deletedAt`
- `deleteMany` on a range is fine for batch cleanup; TTL is cheaper for rolling expiry

```java
// infra/_03db_04mongodb/MongoShowcase.java
// Soft delete: mark now, let the TTL index purge 30 days later. Catch: TTL deletion runs every ~60 s
// and can lag under load, so readers must still filter deletedAt.
public boolean softDelete(String orderId) {
    Instant now = OrderDocuments.nowMillis();
    return orders.updateOne(
            and(eq("_id", OrderDocuments.objectId(orderId)), exists("deletedAt", false)),
            Updates.combine(Updates.set("deletedAt", now), Updates.set("purgeAt", now.plus(SOFT_DELETE_RETENTION))))
            .getModifiedCount() == 1;
}
```

```python
# app/infra/_03db_04mongodb.py
def soft_delete(self, order_id: str) -> bool:
    """Mark now; the TTL index purges later (TTL runs ~every 60 s, readers still filter deletedAt)."""
    now = now_millis()
    return (
        self.orders.update_one(
            {"_id": object_id(order_id), "deletedAt": {"$exists": False}},
            {"$set": {"deletedAt": now, "purgeAt": now + SOFT_DELETE_RETENTION}},
        ).modified_count
        == 1
    )
```

```java
// infra/_03db_04mongodb/MongoShowcase.java
public long deleteCancelledBefore(Instant cutoff) {
    return orders.deleteMany(and(eq("status", OrderStatus.CANCELLED.name()), lt("createdAt", cutoff)))
            .getDeletedCount();
}
```

```python
# app/infra/_03db_04mongodb.py
def delete_cancelled_before(self, cutoff: datetime) -> int:
    return self.orders.delete_many(
        {"status": OrderStatus.CANCELLED.value, "createdAt": {"$lt": cutoff}}
    ).deleted_count
```

## Related

- [Index](04mongodb.00index.md)
- [Bulk writes](04mongodb.05bulk-write.md)
- [Transactions](04mongodb.12transactions.md)
