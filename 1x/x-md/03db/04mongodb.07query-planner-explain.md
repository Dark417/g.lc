# 03db.04mongodb.07query-planner-explain Query Planner And Explain

> Read the plan before adding an index: the stage names tell you where the time goes.

## Index

- [1. How The Planner Picks](#1-how-the-planner-picks)
- [2. Hints And Hidden Indexes](#2-hints-and-hidden-indexes)
- [3. Profiler And Health](#3-profiler-and-health)
- [Related](#related)

## 1. How The Planner Picks

The planner races candidate plans and caches the winner per query shape.

- Candidate plans run in parallel for a trial period; the first to return 101 results (or finish) wins
- The plan cache is keyed by query shape; it is evicted on index changes or restarts
- Read `explain("executionStats")`
  - `IXSCAN` then `FETCH` = good
  - `COLLSCAN` = no usable index
  - `SORT` = in-memory sort (100 megabytes (MB) limit)
  - `totalDocsExamined` much larger than `nReturned` = poor selectivity

```java
// infra/_03db_04mongodb/MongoShowcase.java
// explain("executionStats") and the four numbers that matter. Run it on production-shaped data:
// the planner's trial stops at 101 results, so small fixtures pick different plans.
public QueryPlanSummary explainCustomerOrders(String customerId) {
    Document plan = orders.find(eq("customerId", customerId))
            .sort(orderBy(descending("createdAt"), descending("_id")))
            .limit(20)
            .explain(ExplainVerbosity.EXECUTION_STATS);
    Document stats = plan.get("executionStats", Document.class);
    Document winning = plan.get("queryPlanner", Document.class).get("winningPlan", Document.class);
    List<String> stages = new ArrayList<>();
    String index = collectStages(winning, stages);
    return new QueryPlanSummary(
            stages.isEmpty() ? "UNKNOWN" : stages.get(0),
            index,
            OrderDocuments.num(stats, "totalKeysExamined"),
            OrderDocuments.num(stats, "totalDocsExamined"),
            OrderDocuments.num(stats, "nReturned"),
            OrderDocuments.num(stats, "executionTimeMillis"),
            stages.contains("SORT"),
            !stages.contains("FETCH") && stages.contains("IXSCAN"));
}
```

```python
# app/infra/_03db_04mongodb.py
def explain_customer_orders(self, customer_id: str) -> QueryPlanSummary:
    """explain with executionStats: keysExamined / nReturned is the evidence, not the stage name."""
    plan = self.db.command(
        "explain",
        {
            "find": ORDERS,
            "filter": {"customerId": customer_id},
            "sort": {"createdAt": -1, "_id": -1},
            "limit": 20,
        },
        verbosity="executionStats",
    )
    stats = plan["executionStats"]
    stages: list[str] = []
    index = _collect_stages(plan["queryPlanner"]["winningPlan"], stages)
    return QueryPlanSummary(
        winning_stage=stages[0] if stages else "UNKNOWN",
        index_name=index,
        keys_examined=int(stats["totalKeysExamined"]),
        docs_examined=int(stats["totalDocsExamined"]),
        n_returned=int(stats["nReturned"]),
        execution_millis=int(stats["executionTimeMillis"]),
        blocking_sort="SORT" in stages,
        covered="IXSCAN" in stages and "FETCH" not in stages,
    )
```

## 2. Hints And Hidden Indexes

Force a plan only to test; hide an index before dropping it.

- `hint()` pins an index; a plan pinned in code goes stale when data shifts
- Hidden index: maintained but ignored by the planner ⇒ instant rollback if latency rises
- `$indexStats` shows indexes with zero ops since restart, which are candidates to drop

```java
// infra/_03db_04mongodb/MongoShowcase.java
// hint(): pin the plan for a shape where a wrong pick breaches the SLO (e.g. multi-tenant skew).
// Catch: you now own the choice forever; a renamed index fails the query, a better new index is ignored.
public List<Order> customerOrdersHinted(String customerId, int limit) {
    return orders.find(eq("customerId", customerId))
            .sort(orderBy(descending("createdAt"), descending("_id")))
            .hintString(IDX_CUSTOMER_CREATED)
            .limit(limit)
            .maxTime(maxTimeMs, TimeUnit.MILLISECONDS)
            .map(OrderDocuments::toOrder)
            .into(new ArrayList<>());
}
```

```python
# app/infra/_03db_04mongodb.py
def customer_orders_hinted(self, customer_id: str, limit: int) -> list[Order]:
    """hint(): pin the plan where a wrong pick breaches the SLO; you own the choice from now on."""
    cur = (
        self.orders.find({"customerId": customer_id})
        .sort([("createdAt", DESCENDING), ("_id", DESCENDING)])
        .hint(IDX_CUSTOMER_CREATED)
        .limit(limit)
        .max_time_ms(self.max_time_ms)
    )
    return [to_order(d) for d in cur]
```

```java
// infra/_03db_04mongodb/MongoShowcase.java
// Hide before drop: the planner ignores a hidden index but it is still maintained, so un-hiding is
// instant. Dropping and rebuilding a multi-TB index is hours.
public void setIndexHidden(String indexName, boolean hidden) {
    db.runCommand(new Document("collMod", OrderDocuments.ORDERS)
            .append("index", new Document("name", indexName).append("hidden", hidden)));
}
```

```java
// infra/_03db_04mongodb/MongoShowcase.java
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

```python
# app/infra/_03db_04mongodb.py
def unused_indexes(self) -> list[str]:
    """$indexStats counters reset on restart: snapshot them over 35+ days before trusting "unused"."""
    return [
        s["name"]
        for s in self.db[ORDERS].aggregate([{"$indexStats": {}}])
        if int(s["accesses"]["ops"]) == 0 and s["name"] != "_id_"
    ]
```

## 3. Profiler And Health

Sample slow queries in production instead of logging all of them.

- Profiler level 1 + `slowms` + `sampleRate` captures slow operations at low cost
- WiredTiger cache: dirty share over ~20% or eviction by app threads ⇒ write stalls
- Average document size feeds the working-set estimate: working set should fit in Random-Access Memory (RAM)

```java
// infra/_03db_04mongodb/MongoAdmin.java
// Profiler at slowms for a sampled window, not permanently (it writes system.profile on every slow op).
public Document enableSampledProfiler(int slowMs, double sampleRate) {
    return db.runCommand(new Document("profile", 1).append("slowms", slowMs).append("sampleRate", sampleRate));
}
```

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

## Related

- [Index](04mongodb.00index.md)
- [Indexes](04mongodb.06indexes.md)
- [Pagination](04mongodb.08pagination.md)
