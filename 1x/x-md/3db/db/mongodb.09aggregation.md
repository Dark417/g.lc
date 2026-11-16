# 03db.04mongodb.09aggregation Aggregation Pipeline

> Push computation to the server as a pipeline of stages; put filters first so indexes still apply.

## Index

- [1. Stages And Order](#1-stages-and-order)
- [2. Facets And Windows](#2-facets-and-windows)
- [3. Materialized Views](#3-materialized-views)
- [Related](#related)

## 1. Stages And Order

A pipeline streams documents through stages: `$match` → `$group` → `$sort` → `$limit`.

- `$match` and `$sort` at the front can use indexes; after `$group` they cannot
- Each stage has a 100 megabytes (MB) memory limit; `allowDiskUse` spills (default on since 6.0)
- `$lookup` is a left outer join; it is slow without an index on the foreign field

```java
// infra/_03db_04mongodb/MongoShowcase.java
// $match first (index-eligible) -> $unwind -> $group -> $sort+$limit (top-k, memory-bounded)
// -> $lookup AFTER the limit (10 lookups, not one per order) -> $project.
public List<CustomerRevenue> revenueByCustomer(Instant since, int limit) {
    List<Bson> pipeline = List.of(
            Aggregates.match(and(in("status", "PAID", "SHIPPED", "DELIVERED"), gte("createdAt", since))),
            Aggregates.unwind("$items"),
            Aggregates.group("$customerId",
                    Accumulators.sum("revenueCents",
                            new Document("$multiply", List.of("$items.qty", "$items.priceCents"))),
                    Accumulators.addToSet("orderIds", "$_id")),
            Aggregates.addFields(new Field<>("orderCount", new Document("$size", "$orderIds"))),
            Aggregates.sort(descending("revenueCents")),
            Aggregates.limit(limit),
            Aggregates.lookup(OrderDocuments.CUSTOMERS, "_id", "_id", "customer"),
            Aggregates.unwind("$customer", new UnwindOptions().preserveNullAndEmptyArrays(true)),
            Aggregates.project(Projections.fields(
                    Projections.computed("customerId", "$_id"),
                    Projections.computed("customerName", "$customer.name"),
                    Projections.include("revenueCents", "orderCount"))));
    List<CustomerRevenue> out = new ArrayList<>();
    for (Document d : orders.aggregate(pipeline).allowDiskUse(true).maxTime(maxTimeMs, TimeUnit.MILLISECONDS)) {
        out.add(new CustomerRevenue(d.getString("customerId"), d.getString("customerName"),
                OrderDocuments.num(d, "revenueCents"), (int) OrderDocuments.num(d, "orderCount")));
    }
    return out;
}
```

```python
# app/infra/_03db_04mongodb.py
def revenue_by_customer(self, since: datetime, limit: int) -> list[CustomerRevenue]:
    """$match first -> $unwind -> $group -> $sort+$limit (top-k) -> $lookup after the limit -> $project."""
    pipeline: list[Doc] = [
        {"$match": {"status": {"$in": ["PAID", "SHIPPED", "DELIVERED"]}, "createdAt": {"$gte": since}}},
        {"$unwind": "$items"},
        {
            "$group": {
                "_id": "$customerId",
                "revenueCents": {"$sum": {"$multiply": ["$items.qty", "$items.priceCents"]}},
                "orderIds": {"$addToSet": "$_id"},
            }
        },
        {"$addFields": {"orderCount": {"$size": "$orderIds"}}},
        {"$sort": {"revenueCents": -1}},
        {"$limit": limit},
        {"$lookup": {"from": CUSTOMERS, "localField": "_id", "foreignField": "_id", "as": "customer"}},
        {"$unwind": {"path": "$customer", "preserveNullAndEmptyArrays": True}},
        {
            "$project": {
                "_id": 0,
                "customerId": "$_id",
                "customerName": "$customer.name",
                "revenueCents": 1,
                "orderCount": 1,
            }
        },
    ]
    rows = self.orders.aggregate(pipeline, allowDiskUse=True, maxTimeMS=self.max_time_ms)
    return [
        CustomerRevenue(r["customerId"], r.get("customerName"), int(r["revenueCents"]), int(r["orderCount"]))
        for r in rows
    ]
```

## 2. Facets And Windows

One pass can produce several summaries, or running values across ordered rows.

- `$facet` runs sub-pipelines on the same input, e.g. counts per status plus totals
- `$setWindowFields` (5.0+) computes running totals and moving averages

```java
// infra/_03db_04mongodb/MongoShowcase.java
// $facet: several sub-pipelines over ONE input in one round trip (counts by status + latest 5 + total).
// Catch: the facet output is one document, so it must stay under 16 MB.
public Document statusFacets(String customerId) {
    return orders.aggregate(List.of(
                    Aggregates.match(eq("customerId", customerId)),
                    Aggregates.facet(
                            new Facet("byStatus", Aggregates.group("$status", Accumulators.sum("n", 1))),
                            new Facet("latest", Aggregates.sort(descending("createdAt")), Aggregates.limit(5),
                                    Aggregates.project(Projections.include("status", "totalCents", "createdAt"))),
                            new Facet("total", Aggregates.count("n")))))
            .maxTime(maxTimeMs, TimeUnit.MILLISECONDS)
            .first();
}
```

```python
# app/infra/_03db_04mongodb.py
def status_facets(self, customer_id: str) -> Doc:
    """$facet: several sub-pipelines over one input in one round trip; output must stay < 16 MB."""
    pipeline: list[Doc] = [
        {"$match": {"customerId": customer_id}},
        {
            "$facet": {
                "byStatus": [{"$group": {"_id": "$status", "n": {"$sum": 1}}}],
                "latest": [
                    {"$sort": {"createdAt": -1}},
                    {"$limit": 5},
                    {"$project": {"status": 1, "totalCents": 1, "createdAt": 1}},
                ],
                "total": [{"$count": "n"}],
            }
        },
    ]
    return next(self.orders.aggregate(pipeline, maxTimeMS=self.max_time_ms), {})
```

```java
// infra/_03db_04mongodb/MongoShowcase.java
// $setWindowFields (5.0+): running total per customer without a self-join.
public List<Document> runningTotals(String customerId) {
    return orders.aggregate(List.of(
                    Aggregates.match(eq("customerId", customerId)),
                    Document.parse("""
                            { $setWindowFields: { partitionBy: "$customerId", sortBy: { createdAt: 1 },
                                output: { runningTotalCents: { $sum: "$totalCents",
                                          window: { documents: ["unbounded", "current"] } } } } }"""),
                    Aggregates.project(Projections.include("createdAt", "totalCents", "runningTotalCents"))))
            .maxTime(maxTimeMs, TimeUnit.MILLISECONDS)
            .into(new ArrayList<>());
}
```

```python
# app/infra/_03db_04mongodb.py
def running_totals(self, customer_id: str) -> list[Doc]:
    """$setWindowFields (5.0+): running total without a self-join."""
    pipeline: list[Doc] = [
        {"$match": {"customerId": customer_id}},
        {
            "$setWindowFields": {
                "partitionBy": "$customerId",
                "sortBy": {"createdAt": 1},
                "output": {
                    "runningTotalCents": {"$sum": "$totalCents", "window": {"documents": ["unbounded", "current"]}}
                },
            }
        },
        {"$project": {"createdAt": 1, "totalCents": 1, "runningTotalCents": 1}},
    ]
    return list(self.orders.aggregate(pipeline, maxTimeMS=self.max_time_ms))
```

## 3. Materialized Views

`$merge` writes results into a collection, so dashboards read precomputed rows.

- Incremental: aggregate only the new window and merge on the key
- `$out` replaces the whole collection; `$merge` upserts row by row

```java
// infra/_03db_04mongodb/MongoShowcase.java
// $merge: materialize a daily revenue rollup (upsert per day) instead of recomputing it on every read.
// Run it on a schedule; readers hit the small daily_revenue collection.
public void materializeDailyRevenue(Instant since) {
    orders.aggregate(List.of(
                    Aggregates.match(and(in("status", "PAID", "SHIPPED", "DELIVERED"), gte("createdAt", since))),
                    Document.parse("""
                            { $group: { _id: { $dateTrunc: { date: "$createdAt", unit: "day" } },
                                        revenueCents: { $sum: "$totalCents" }, orders: { $sum: 1 } } }"""),
                    Aggregates.merge(OrderDocuments.DAILY_REVENUE, new MergeOptions()
                            .whenMatched(MergeOptions.WhenMatched.REPLACE)
                            .whenNotMatched(MergeOptions.WhenNotMatched.INSERT))))
            .allowDiskUse(true)
            .toCollection(); // $merge runs only when the result is consumed or toCollection() is called
}
```

```python
# app/infra/_03db_04mongodb.py
def materialize_daily_revenue(self, since: datetime) -> None:
    """$merge a daily rollup (upsert per day); readers hit the small daily_revenue collection."""
    pipeline: list[Doc] = [
        {"$match": {"status": {"$in": ["PAID", "SHIPPED", "DELIVERED"]}, "createdAt": {"$gte": since}}},
        {
            "$group": {
                "_id": {"$dateTrunc": {"date": "$createdAt", "unit": "day"}},
                "revenueCents": {"$sum": "$totalCents"},
                "orders": {"$sum": 1},
            }
        },
        {"$merge": {"into": DAILY_REVENUE, "whenMatched": "replace", "whenNotMatched": "insert"}},
    ]
    self.orders.aggregate(pipeline, allowDiskUse=True)  # $merge runs as part of the command
```

## Related

- [Index](04mongodb.00index.md)
- [Indexes](04mongodb.06indexes.md)
- [Tradeoffs](04mongodb.98tradeoffs.md)
