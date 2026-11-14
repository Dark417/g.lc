# 03db.04mongodb.03schema-design Schema Design

> Model for the queries you run: embed what is read together, reference what grows without bound.

## Index

- [1. Embed Or Reference](#1-embed-or-reference)
- [2. Bounded Arrays And Outliers](#2-bounded-arrays-and-outliers)
- [3. Schema Validation](#3-schema-validation)
- [Related](#related)

## 1. Embed Or Reference

Design starts from access patterns, not from entities.

- **Embed** when the child is read with the parent and stays bounded
  - Order + line items: one read, one atomic write
  - Limit: a document caps at 16 megabytes (MB); arrays over ~1,000 items slow updates (order of magnitude)
- **Reference** when the child is shared, large, or unbounded
  - Customer ↔ orders: thousands of orders per customer ⇒ separate collection
- **Extended reference**: copy the few fields you display (customer name) into the child
  - Read stays one query
  - Catch: a rename must fan out to every copy

```java
// infra/_03db_04mongodb/MongoShowcase.java
// Extended-reference fan-out: the duplicated name must be updated everywhere it was copied.
// When: the copied field is near-immutable. Catch: fan-out = documents touched per change; at 1M orders
// per customer this is a replication-lag event, so run it async and rate-limited.
public long renameCustomerEverywhere(String customerId, String newName) {
    customers.updateOne(eq("_id", customerId), Updates.set("name", newName));
    return orders.updateMany(eq("customerId", customerId), Updates.set("customerName", newName))
            .getModifiedCount();
}
```

```python
# app/infra/_03db_04mongodb.py
def rename_customer_everywhere(self, customer_id: str, new_name: str) -> int:
    """Extended-reference fan-out: every copied name must change. Bound the fan-out at design time."""
    self.db[CUSTOMERS].update_one({"_id": customer_id}, {"$set": {"name": new_name}})
    return self.orders.update_many({"customerId": customer_id}, {"$set": {"customerName": new_name}}).modified_count
```

## 2. Bounded Arrays And Outliers

Arrays that can grow forever are the most common schema bug.

- Cap the array in the update filter (`items.99` must not exist) or with `$slice`
- **Outlier pattern**: keep the newest N events inline, overflow to a side collection
- **Bucket pattern**: group time-series points into one document per hour or device

```java
// infra/_03db_04mongodb/MongoShowcase.java
// Bucket pattern: append to the open bucket (count < 200) or upsert a new one. Caps array growth
// structurally, so no document ever approaches 16 MB. Catch: under a race two buckets can open at once;
// harmless because readers sort by firstAt and the count bound still holds per bucket.
public void appendOrderEvent(String orderId, String event) {
    Instant now = OrderDocuments.nowMillis();
    db.getCollection(OrderDocuments.ORDER_EVENTS).updateOne(
            and(eq("orderId", orderId), lt("count", BUCKET_SIZE)),
            Updates.combine(
                    Updates.push("events", new Document("at", now).append("event", event)),
                    Updates.inc("count", 1),
                    Updates.setOnInsert("firstAt", now)),
            new UpdateOptions().upsert(true));
}
```

```python
# app/infra/_03db_04mongodb.py
def append_order_event(self, order_id: str, event: str) -> None:
    """Bucket pattern: append to the open bucket (count < 200) or upsert a new one; caps array growth."""
    now = now_millis()
    self.db[ORDER_EVENTS].update_one(
        {"orderId": order_id, "count": {"$lt": BUCKET_SIZE}},
        {"$push": {"events": {"at": now, "event": event}}, "$inc": {"count": 1}, "$setOnInsert": {"firstAt": now}},
        upsert=True,
    )
```

## 3. Schema Validation

Flexible schema does not mean no schema: `$jsonSchema` validators enforce shape on write.

- `validationLevel: moderate` checks inserts and already-valid documents only ⇒ safe rollout on old data
- `validationAction: error` rejects; `warn` only logs
- Catch: validators run on the server; the app still needs domain checks for good error messages

```java
// infra/_03db_04mongodb/MongoShowcase.java
// $jsonSchema validator: types and required fields enforced by the server, for every producer.
// When: the shape has stabilized. Catch: it cannot express "total document bytes"; moderate level
// skips existing invalid documents so you can tighten the schema without a backfill first.
public void applyOrderValidator() {
    Document schema = Document.parse("""
            { $jsonSchema: {
                bsonType: "object",
                required: ["customerId", "status", "items", "totalCents", "createdAt", "version"],
                properties: {
                  customerId: { bsonType: "string" },
                  status:     { enum: ["PENDING", "PAID", "SHIPPED", "DELIVERED", "CANCELLED"] },
                  items:      { bsonType: "array", minItems: 1, maxItems: 100,
                                items: { bsonType: "object", required: ["sku", "qty", "priceCents"],
                                         properties: { qty: { bsonType: ["int", "long"], minimum: 1 },
                                                       priceCents: { bsonType: ["int", "long"] } } } },
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

```python
# app/infra/_03db_04mongodb.py
def apply_order_validator(self) -> None:
    """$jsonSchema validator, moderate level: existing invalid docs are skipped, new writes are checked."""
    schema = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["customerId", "status", "items", "totalCents", "createdAt", "version"],
            "properties": {
                "customerId": {"bsonType": "string"},
                "status": {"enum": [s.value for s in OrderStatus]},
                "items": {
                    "bsonType": "array",
                    "minItems": 1,
                    "maxItems": MAX_ITEMS,
                    "items": {
                        "bsonType": "object",
                        "required": ["sku", "qty", "priceCents"],
                        "properties": {
                            "qty": {"bsonType": ["int", "long"], "minimum": 1},
                            "priceCents": {"bsonType": ["int", "long"]},
                        },
                    },
                },
                "totalCents": {"bsonType": ["int", "long"]},
                "createdAt": {"bsonType": "date"},
                "version": {"bsonType": ["int", "long"]},
            },
        }
    }
    try:
        self.db.create_collection(ORDERS, validator=schema, validationLevel="moderate", validationAction="error")
    except CollectionInvalid:  # already exists: change the validator in place
        self.db.command("collMod", ORDERS, validator=schema, validationLevel="moderate", validationAction="error")
```

## Related

- [Index](04mongodb.00index.md)
- [Document model](04mongodb.01document-model-bson.md)
- [Create, Read, Update, Delete (CRUD) and update operators](04mongodb.04crud-update-operators.md)
