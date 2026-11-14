# 03db.02dynamodb.07query-pagination-scan Query, Pagination, And Scan

> Key-condition queries, `LastEvaluatedKey` pagination as an opaque cursor, and why Scan stays out of request paths.

## Index

- [1. Query On Keys](#1-query-on-keys)
  - [1.1 Prefix And Range](#11-prefix-and-range)
  - [1.2 Query In Code](#12-query-in-code)
- [2. Pagination](#2-pagination)
  - [2.1 Rules](#21-rules)
  - [2.2 Opaque Cursor](#22-opaque-cursor)
  - [2.3 Paginator For Internal Loops](#23-paginator-for-internal-loops)
- [3. Scan And Parallel Scan](#3-scan-and-parallel-scan)
- [Related](#related)

## 1. Query On Keys

A Query reads one item collection (one Partition Key (PK)), optionally narrowed by a sort-key condition.

### 1.1 Prefix And Range

- Key conditions are applied before the read
  - You pay only for matching items (unlike filters)
- `begins_with(SK, "ORDER#")` skips the `PROFILE` item
- `ScanIndexForward=false` = descending Sort Key (SK) = newest first
- `SK BETWEEN ORDER#<from> AND ORDER#<to>` is inclusive
  - Every SK ends with `#<orderId>` ⇒ behaves as `[from, to)`
  - Only correct because timestamps are fixed-width ([05single-table-design](02dynamodb.05single-table-design.md#4-sort-keys-compare-as-strings))
- `ProjectionExpression` fetches only needed attributes
  - Limit: Read Capacity Unit (RCU) is charged on the full item size, not the projected size

### 1.2 Query In Code

**Java**

```java
// infra/_03db_02dynamodb/DynamoDbShowcase.java
public List<Order> queryOrdersByPrefix(String customerId, int limit) {
    QueryResponse resp = client.query(r -> r
            .tableName(props.ordersTable())
            .keyConditionExpression("PK = :pk AND begins_with(SK, :prefix)")
            .expressionAttributeValues(Map.of(
                    ":pk", s(OrderKeys.customerPk(customerId)),
                    ":prefix", s(OrderKeys.ORDER_PREFIX)))
            .scanIndexForward(false) // descending SK = newest first
            .limit(limit));          // one page: at most Limit items or 1 MB
    return resp.items().stream().map(OrderItemMapper::toOrder).toList();
}

public List<Order> queryOrdersBetween(String customerId, Instant from, Instant to) {
    QueryRequest req = QueryRequest.builder()
            .tableName(props.ordersTable())
            .keyConditionExpression("PK = :pk AND SK BETWEEN :from AND :to")
            .expressionAttributeValues(Map.of(
                    ":pk", s(OrderKeys.customerPk(customerId)),
                    ":from", s(OrderKeys.orderSkBound(from)),
                    ":to", s(OrderKeys.orderSkBound(to))))
            .build();
    // paginator follows LastEvaluatedKey until the range is exhausted
    return client.queryPaginator(req).items().stream().map(OrderItemMapper::toOrder).toList();
}
```

**Python**

```python
# app/infra/_03db_02dynamodb.py
def query_orders_resource(
    self, customer_id: str, limit: int, start: datetime | None = None, end: datetime | None = None
) -> list[Order]:
    """Key(...) is for KeyConditionExpression only; Attr(...) is for filters/conditions."""
    pk_cond = Key("PK").eq(pk_customer(customer_id))
    if start is not None and end is not None:
        cond = pk_cond & Key("SK").between(sk_order_bound(start), sk_order_bound(end))
    else:
        cond = pk_cond & Key("SK").begins_with(ORDER_PREFIX)
    resp = self.table.query(KeyConditionExpression=cond, ScanIndexForward=False, Limit=limit)
    return [from_item(i) for i in resp.get("Items", [])]
```

**Catch**

- `Limit` is per page; one call returns at most `Limit` items or 1 megabyte (MB), whichever comes first

## 2. Pagination

Each response is one page; `LastEvaluatedKey` is the only end-of-data signal.

- 🗣 "A short page is not the last page; only a missing LastEvaluatedKey is."

### 2.1 Rules

- Each page is at most 1 MB
- Loop until `LastEvaluatedKey` is absent
  - Prevents: silent data loss when a page is short
- `Limit` caps items evaluated before the filter
  - Result: a page can be empty yet have a next key
- Pass `LastEvaluatedKey` back as `ExclusiveStartKey`
- Cursors are stable under inserts (keyset), unlike OFFSET
- No total count
  - `Select=COUNT` still reads every item

→ Short or empty page treated as the end  
⇒ Pagination stops early; missing results  
→ Loop until `LastEvaluatedKey` is absent

### 2.2 Opaque Cursor

Expose `LastEvaluatedKey` to Application Programming Interface (API) clients as an opaque base64 cursor.

- Validate it on the way back in
  - PK must match the caller ⇒ a client cannot jump partitions
- Sign or encrypt it if keys are sensitive
  - base64 is not secrecy
- Page size is capped at 100 in the service: bounded latency and RCU per call

**Java**

```java
// infra/_03db_02dynamodb/CursorCodec.java
public static String encode(Map<String, AttributeValue> lastEvaluatedKey) {
    if (lastEvaluatedKey == null || lastEvaluatedKey.isEmpty()) {
        return null; // no more pages
    }
    Map<String, String> plain = new TreeMap<>();
    lastEvaluatedKey.forEach((name, value) -> plain.put(name, value.s())); // all x-orders keys are type S
    return Base64.getUrlEncoder().withoutPadding().encodeToString(JSON.writeValueAsBytes(plain));
}

public static Map<String, AttributeValue> decode(
        String cursor, Set<String> expectedNames, String pkName, String expectedPk) {
    // ... base64url -> Map<String, String>, "malformed cursor" on failure
    if (!plain.keySet().equals(expectedNames)) {
        throw new IllegalArgumentException("cursor keys do not match this query");
    }
    if (expectedPk != null && !expectedPk.equals(plain.get(pkName))) {
        throw new IllegalArgumentException("cursor belongs to another partition");
    }
    // ... back to AttributeValue.fromS
}
```

```java
// infra/_03db_02dynamodb/DynamoDbShowcase.java
public CursorPage<Order> queryOrdersPage(String customerId, int limit, String cursor) {
    String pk = OrderKeys.customerPk(customerId);
    Map<String, AttributeValue> startKey = CursorCodec.decode(cursor, CursorCodec.TABLE_KEYS, "PK", pk);
    QueryRequest.Builder req = QueryRequest.builder()
            .tableName(props.ordersTable())
            .keyConditionExpression("PK = :pk AND begins_with(SK, :prefix)")
            .expressionAttributeValues(Map.of(":pk", s(pk), ":prefix", s(OrderKeys.ORDER_PREFIX)))
            .scanIndexForward(false)
            .limit(limit);
    if (startKey != null) {
        req.exclusiveStartKey(startKey);
    }
    QueryResponse resp = client.query(req.build());
    List<Order> items = resp.items().stream().map(OrderItemMapper::toOrder).toList();
    String next = resp.hasLastEvaluatedKey() ? CursorCodec.encode(resp.lastEvaluatedKey()) : null;
    return new CursorPage<>(items, next);
}
```

**Python**

```python
# app/infra/_03db_02dynamodb.py
def encode_cursor(last_evaluated_key: Item | None) -> str | None:
    if not last_evaluated_key:
        return None
    raw = json.dumps(last_evaluated_key, sort_keys=True, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")

def decode_cursor(cursor: str | None, expected_names: frozenset[str], pk_name: str, expected_pk: str) -> Item | None:
    if not cursor:
        return None
    # ... pad + urlsafe_b64decode + json.loads; ValueError("malformed cursor")
    if not isinstance(key, dict) or set(key) != expected_names:
        raise ValueError("cursor keys do not match this query")
    if key.get(pk_name) != expected_pk:
        raise ValueError("cursor belongs to another partition")
    return key

def query_orders_page(self, customer_id: str, limit: int, cursor: str | None) -> CursorPage:
    pk = pk_customer(customer_id)
    start_key = decode_cursor(cursor, TABLE_KEYS, "PK", pk)
    kwargs: dict[str, Any] = {
        "TableName": self.orders_table,
        "KeyConditionExpression": "PK = :pk AND begins_with(SK, :prefix)",
        "ExpressionAttributeValues": to_av({":pk": pk, ":prefix": ORDER_PREFIX}),
        "ScanIndexForward": False,
        "Limit": limit,
    }
    if start_key:
        kwargs["ExclusiveStartKey"] = to_av(start_key)
    resp = self.client.query(**kwargs)
    items = [from_item(from_av(i)) for i in resp.get("Items", [])]
    lek = resp.get("LastEvaluatedKey")
    return CursorPage(items=items, next_cursor=encode_cursor(from_av(lek)) if lek else None)
```

**Catch**

- Enhanced Client: `PageIterable.items()` silently fetches every page
  - Use `iterator().next()` for one API page; `Page.lastEvaluatedKey()` feeds `CursorCodec`

### 2.3 Paginator For Internal Loops

The Software Development Kit (SDK) paginator follows `LastEvaluatedKey` for you, lazily.

- Use for jobs and small item collections
- Never to build an unbounded API response

**Java**

```java
// infra/_03db_02dynamodb/DynamoDbShowcase.java
public List<Order> queryAllOrders(String customerId) {
    // ... same key condition, no Limit
    List<Order> all = new ArrayList<>();
    for (QueryResponse page : client.queryPaginator(req)) {
        page.items().forEach(i -> all.add(OrderItemMapper.toOrder(i)));
    }
    return all;
}
```

**Python**

```python
# app/infra/_03db_02dynamodb.py
def query_all_orders(self, customer_id: str, page_size: int = 100) -> list[Order]:
    pages = self.client.get_paginator("query").paginate(
        TableName=self.orders_table,
        KeyConditionExpression="PK = :pk AND begins_with(SK, :prefix)",
        ExpressionAttributeValues=to_av({":pk": pk_customer(customer_id), ":prefix": ORDER_PREFIX}),
        PaginationConfig={"PageSize": page_size},  # sets Limit per request
    )
    return [from_item(from_av(i)) for page in pages for i in page.get("Items", [])]
```

**Catch**

- Each page is a separate request
  - The result is not a snapshot; concurrent writes may show up
- boto3's `StartingToken` is botocore's own format, not the raw key
  - Don't hand it to API clients; use `query_orders_page`

## 3. Scan And Parallel Scan

Scan reads the whole table and filters afterwards, so you pay for everything scanned.

- Filter applied after read ⇒ full RCU cost
  - You pay for `ScannedCount`, not `Count`
- Parallel scan (`Segment` / `TotalSegments`) only for offline jobs
  - Backfills, migrations
  - Each worker loops its own `LastEvaluatedKey`
- Prefer a Global Secondary Index (GSI), or "Export to Simple Storage Service (S3)" for analytics

→ Missing access pattern  
⇒ Scan in request path: RCU spikes, slow API  
→ Add a GSI; export to S3 for analytics

**Java**

```java
// infra/_03db_02dynamodb/DynamoDbShowcase.java
public long scanAllOrders(Consumer<Order> sink) {
    ScanRequest req = ScanRequest.builder()
            .tableName(props.ordersTable())
            .filterExpression("entityType = :order")
            .expressionAttributeValues(Map.of(":order", s(OrderKeys.ENTITY_ORDER)))
            .build();
    long scanned = 0;
    for (ScanResponse page : client.scanPaginator(req)) {
        scanned += page.scannedCount(); // what you pay for
        page.items().forEach(i -> sink.accept(OrderItemMapper.toOrder(i)));
    }
    return scanned;
}

public List<Order> parallelScan(int totalSegments) {
    // ... one pool thread per segment; each runs:
    Map<String, AttributeValue> startKey = null;
    do {
        ScanRequest.Builder req = ScanRequest.builder()
                .tableName(props.ordersTable())
                .segment(seg)
                .totalSegments(totalSegments)
                .filterExpression("entityType = :order")
                .expressionAttributeValues(Map.of(":order", s(OrderKeys.ENTITY_ORDER)));
        if (startKey != null) {
            req.exclusiveStartKey(startKey);
        }
        ScanResponse page = client.scan(req.build());
        page.items().forEach(i -> out.add(OrderItemMapper.toOrder(i)));
        startKey = page.hasLastEvaluatedKey() && !page.lastEvaluatedKey().isEmpty()
                ? page.lastEvaluatedKey() : null;
    } while (startKey != null);
    // ... wait for all futures, shutdownNow()
}
```

**Python**

```python
# app/infra/_03db_02dynamodb.py
def parallel_scan(self, total_segments: int) -> list[Order]:
    def scan_segment(segment: int) -> list[Order]:
        out: list[Order] = []
        kwargs: dict[str, Any] = {
            "TableName": self.orders_table,
            "Segment": segment,
            "TotalSegments": total_segments,
            "FilterExpression": "entityType = :order",
            "ExpressionAttributeValues": to_av({":order": ENTITY_ORDER}),
        }
        while True:
            resp = self.client.scan(**kwargs)
            out.extend(from_item(from_av(i)) for i in resp.get("Items", []))
            lek = resp.get("LastEvaluatedKey")
            if not lek:
                return out
            kwargs["ExclusiveStartKey"] = lek

    # shares the client (thread-safe), not a resource
    with ThreadPoolExecutor(max_workers=total_segments) as pool:
        results = list(pool.map(scan_segment, range(total_segments)))
    return [o for seg in results for o in seg]
```

**Catch**

- N workers burn N times the throughput at once
  - Can throttle live traffic; cap N and rate-limit
- Python `scan_all_orders` is a generator to keep memory flat

## Related

- [00index](02dynamodb.00index.md)
- [05single-table-design](02dynamodb.05single-table-design.md)
- [10streams-ttl](02dynamodb.10streams-ttl.md)
