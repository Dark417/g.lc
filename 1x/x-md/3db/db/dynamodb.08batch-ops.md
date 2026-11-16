# 03db.02dynamodb.08batch-ops Batch Writes And Reads

> `BatchWriteItem` and `BatchGetItem` for bulk work: not atomic, partial success, resend leftovers with backoff.

## Index

- [1. Batch Limits And Semantics](#1-batch-limits-and-semantics)
- [2. Unprocessed Retry Loop](#2-unprocessed-retry-loop)
- [3. Batch Write In Code](#3-batch-write-in-code)
- [4. Batch Get In Code](#4-batch-get-in-code)
- [5. Batch Vs Transaction](#5-batch-vs-transaction)
- [Related](#related)

## 1. Batch Limits And Semantics

Batches save round trips but give up atomicity and conditions.

- `BatchWriteItem`: up to 25 puts/deletes, 16 megabytes (MB)
- `BatchGetItem`: up to 100 keys, 16 MB
  - Source: Developer Guide, "Service quotas"
- Not atomic, no conditions
- Duplicate keys inside one batch → `ValidationException`
- BatchGet results come back in no particular order
  - Missing keys are simply absent; re-key by Partition Key (PK)+Sort Key (SK) if needed

## 2. Unprocessed Retry Loop

Partial success is normal under throttling; a 200 response can still carry leftovers.

- Partial success returns `UnprocessedItems` / `UnprocessedKeys`

→ Resend only those  
→ Sleep with exponential backoff + full jitter  
→ Give up after N attempts and surface the leftovers

→ `UnprocessedItems` ignored  
⇒ Partial batch dropped: missing items, no error  
→ Loop with backoff; alert on leftovers

## 3. Batch Write In Code

**Java**

```java
// infra/_03db_02dynamodb/DynamoDbShowcase.java
static final int BATCH_WRITE_MAX = 25;

public void batchPutOrders(List<Order> orders) {
    for (List<Order> chunk : chunks(orders, BATCH_WRITE_MAX)) {
        requireUniqueKeys(chunk.stream().map(Order::ref).toList()); // duplicates -> ValidationException
        List<WriteRequest> writes = /* ... PutRequest per order */;
        Map<String, List<WriteRequest>> pending = Map.of(props.ordersTable(), writes);
        for (int attempt = 0; !pending.isEmpty(); attempt++) {
            if (attempt == 5) {
                int left = pending.values().stream().mapToInt(List::size).sum();
                throw new IllegalStateException(left + " items still unprocessed after retries");
            }
            if (attempt > 0) {
                Retry.sleep(retry.backoff(attempt)); // full-jitter backoff
            }
            final Map<String, List<WriteRequest>> request = pending;
            BatchWriteItemResponse resp = client.batchWriteItem(r -> r.requestItems(request));
            pending = resp.hasUnprocessedItems() ? resp.unprocessedItems() : Map.of();
        }
    }
}
```

```java
// infra/_03db_02dynamodb/EnhancedClientShowcase.java
// WriteBatch exposes unprocessed beans per table; no chunking or retry for you.
WriteBatch.Builder<OrderItem> batch = WriteBatch.builder(OrderItem.class).mappedTableResource(orders);
pending.forEach(batch::addPutItem);
BatchWriteResult result = enhanced.batchWriteItem(r -> r.writeBatches(batch.build()));
pending = result.unprocessedPutItemsForTable(orders);
```

**Python**

```python
# app/infra/_03db_02dynamodb.py
def batch_put_orders(self, orders: list[Order]) -> None:
    for chunk in _chunks(orders, BATCH_WRITE_MAX):
        keys = {(o.ref.pk, o.ref.sk) for o in chunk}
        if len(keys) != len(chunk):
            raise ValueError("duplicate key in one batch")
        pending: dict[str, list[Any]] = {
            self.orders_table: [{"PutRequest": {"Item": to_av(to_item(o))}} for o in chunk]
        }
        for attempt in range(MAX_BATCH_ATTEMPTS):
            if attempt > 0:
                time.sleep(backoff(attempt))
            resp = self.client.batch_write_item(RequestItems=pending)
            pending = resp.get("UnprocessedItems") or {}
            if not pending:
                break
        if pending:
            left = sum(len(v) for v in pending.values())
            raise RuntimeError(f"{left} items still unprocessed after retries")

def batch_put_orders_resource(self, orders: list[Order]) -> None:
    """batch_writer buffers 25 items per call and re-queues UnprocessedItems automatically."""
    with self.table.batch_writer(overwrite_by_pkeys=["PK", "SK"]) as writer:  # dedupes keys per buffer
        for o in orders:
            writer.put_item(Item=to_item(o))
```

**Catch**

- `batch_writer` re-queue has no backoff of its own
  - Relies on the client's retry config; still not atomic
- Batch writes take no conditions
  - Result: the Enhanced Client `@DynamoDbVersionAttribute` check is not enforced (bulk loads only)

## 4. Batch Get In Code

**Java**

```java
// infra/_03db_02dynamodb/DynamoDbShowcase.java
public List<Order> batchGetOrders(List<OrderRef> refs, boolean consistentRead) {
    // ... dedupe refs by PK|SK (duplicate keys -> ValidationException), chunk by 100
    Map<String, KeysAndAttributes> pending = Map.of(props.ordersTable(),
            KeysAndAttributes.builder().keys(keys).consistentRead(consistentRead).build());
    for (int attempt = 0; !pending.isEmpty(); attempt++) {
        // ... give up at 5, backoff when attempt > 0
        BatchGetItemResponse resp = client.batchGetItem(r -> r.requestItems(request));
        resp.responses().getOrDefault(props.ordersTable(), List.of())
                .forEach(i -> found.add(OrderItemMapper.toOrder(i)));
        pending = resp.hasUnprocessedKeys() ? resp.unprocessedKeys() : Map.of();
    }
    return found;
}
```

**Python**

```python
# app/infra/_03db_02dynamodb.py
def batch_get_orders(self, refs: list[OrderRef], consistent: bool = False) -> list[Order]:
    unique = list({(r.pk, r.sk): r for r in refs}.values())  # duplicate keys -> ValidationException
    found: list[Order] = []
    for chunk in _chunks(unique, BATCH_GET_MAX):
        pending: dict[str, Any] = {
            self.orders_table: {"Keys": [to_av(key_of(r)) for r in chunk], "ConsistentRead": consistent}
        }
        for attempt in range(MAX_BATCH_ATTEMPTS):
            if attempt > 0:
                time.sleep(backoff(attempt))
            resp = self.client.batch_get_item(RequestItems=pending)
            found.extend(from_item(from_av(i)) for i in resp.get("Responses", {}).get(self.orders_table, []))
            pending = resp.get("UnprocessedKeys") or {}
            if not pending:
                break
        if pending:
            raise RuntimeError("keys still unprocessed after retries")
    return found
```

**Catch**

- Java `batchGetItemPaginator` and the Enhanced `batchGetItem` iterable follow `UnprocessedKeys`
  - But with no backoff between calls ⇒ under heavy throttling prefer the low-level loop
- boto3 has no `batch_reader` helper; this loop is the pattern

## 5. Batch Vs Transaction

| Option | Max items | Atomic, conditions | Cost | Failure shape |
|---|---|---|---|---|
| BatchWriteItem | 25 | No, no | 1x | `UnprocessedItems` |
| TransactWriteItems | 100 | Yes, yes | 2x | Whole call, per-action reasons |

Pick: batch for bulk loads, transactions for invariants ([09transactions-idempotency](02dynamodb.09transactions-idempotency.md)).

## Related

- [00index](02dynamodb.00index.md)
- [09transactions-idempotency](02dynamodb.09transactions-idempotency.md)
- [11capacity-modes](02dynamodb.11capacity-modes.md)
