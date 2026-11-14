# 03db.04mongodb.08pagination Pagination

> Page by a stable sort key, never by skip, once the collection is large.

## Index

- [1. Skip Is Linear](#1-skip-is-linear)
- [2. Keyset Cursor](#2-keyset-cursor)
- [Related](#related)

## 1. Skip Is Linear

`skip(n)` walks and discards n index entries on every request.

- Page 10,000 × 20 rows = 200,000 entries walked per call ⇒ latency grows with page number
- Rows inserted between calls shift pages ⇒ duplicates and gaps
- Fine for small admin lists only

```java
// infra/_03db_04mongodb/MongoShowcase.java
// Anti-pattern kept for contrast: skip(N) walks and discards N index keys per page, and rows shift
// under concurrent inserts (duplicates / gaps between pages).
public List<Order> listCustomerOrdersBySkip(String customerId, int page, int size) {
    return orders.find(eq("customerId", customerId))
            .sort(orderBy(descending("createdAt"), descending("_id")))
            .skip(page * size)
            .limit(size)
            .maxTime(maxTimeMs, TimeUnit.MILLISECONDS)
            .map(OrderDocuments::toOrder)
            .into(new ArrayList<>());
}
```

```python
# app/infra/_03db_04mongodb.py
def list_customer_orders_by_skip(self, customer_id: str, page: int, size: int) -> list[Order]:
    """Anti-pattern for contrast: skip(N) walks N keys per page; rows shift under concurrent inserts."""
    cur = (
        self.orders.find({"customerId": customer_id})
        .sort([("createdAt", DESCENDING), ("_id", DESCENDING)])
        .skip(page * size)
        .limit(size)
        .max_time_ms(self.max_time_ms)
    )
    return [to_order(d) for d in cur]
```

## 2. Keyset Cursor

Remember the last `(createdAt, _id)` and seek past it.

- Sort on `createdAt desc, _id desc`; `_id` breaks ties so the order is total
- Filter: `createdAt < last` OR (`createdAt = last` AND `_id < lastId`)
- Index `{customerId:1, createdAt:-1, _id:-1}` makes each page one index seek
- The cursor is opaque base64 so clients cannot build it by hand

```java
// infra/_03db_04mongodb/MongoShowcase.java
// Keyset pagination on (createdAt, _id): each page is one bounded index seek, O(page) not O(offset).
// Fetch limit+1 to know whether a next page exists without a count query.
public OrderPage listCustomerOrders(String customerId, int limit, String cursor) {
    OrderCursor after = OrderCursor.decode(cursor);
    Bson filter = eq("customerId", customerId);
    if (after != null) {
        filter = and(filter, or(
                lt("createdAt", after.createdAt()),
                and(eq("createdAt", after.createdAt()), lt("_id", after.id()))));
    }
    List<Document> rows = orders.find(filter)
            .sort(orderBy(descending("createdAt"), descending("_id"))) // must match the index direction
            .limit(limit + 1)
            .maxTime(maxTimeMs, TimeUnit.MILLISECONDS)
            .into(new ArrayList<>());
    boolean more = rows.size() > limit;
    List<Order> page = rows.stream().limit(limit).map(OrderDocuments::toOrder).toList();
    String next = null;
    if (more) {
        Document last = rows.get(limit - 1);
        next = new OrderCursor(OrderDocuments.instant(last, "createdAt"), last.getObjectId("_id")).encode();
    }
    return new OrderPage(page, next);
}
```

```python
# app/infra/_03db_04mongodb.py
def list_customer_orders(self, customer_id: str, limit: int, cursor: str | None) -> OrderPage:
    """Keyset on (createdAt, _id): one bounded index seek per page; fetch limit+1 to detect a next page."""
    flt: Doc = {"customerId": customer_id}
    after = decode_cursor(cursor)
    if after:
        ts, oid = after
        flt["$or"] = [{"createdAt": {"$lt": ts}}, {"createdAt": ts, "_id": {"$lt": oid}}]
    rows = list(
        self.orders.find(flt)
        .sort([("createdAt", DESCENDING), ("_id", DESCENDING)])  # must match the index direction
        .limit(limit + 1)
        .max_time_ms(self.max_time_ms)
    )
    page = rows[:limit]
    nxt = encode_cursor(page[-1]["createdAt"], page[-1]["_id"]) if len(rows) > limit else None
    return OrderPage([to_order(d) for d in page], nxt)
```

```java
// infra/_03db_04mongodb/OrderCursor.java
public String encode() {
    String raw = createdAt.toEpochMilli() + "." + id.toHexString();
    return Base64.getUrlEncoder().withoutPadding().encodeToString(raw.getBytes(StandardCharsets.UTF_8));
}
```

```python
# app/infra/_03db_04mongodb.py
def encode_cursor(created_at: datetime, oid: ObjectId) -> str:
    """Keyset cursor = sort key of the last row: (createdAt millis, _id). _id breaks createdAt ties."""
    raw = f"{int(created_at.timestamp() * 1000)}.{oid}"
    return base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")
```

## Related

- [Index](04mongodb.00index.md)
- [Query planner](04mongodb.07query-planner-explain.md)
- [Aurora pagination](01aurora.14pagination.md)
