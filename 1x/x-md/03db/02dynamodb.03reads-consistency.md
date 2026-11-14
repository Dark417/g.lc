# 03db.02dynamodb.03reads-consistency Strong Vs Eventual Reads

> What each read mode costs, where it is allowed, and how to get read-your-write without a second read.

## Index

- [1. Eventual Reads](#1-eventual-reads)
- [2. Strong Reads](#2-strong-reads)
- [3. Read-Your-Write Without A Strong Read](#3-read-your-write-without-a-strong-read)
- [4. GetItem In Code](#4-getitem-in-code)
- [Related](#related)

## 1. Eventual Reads

Eventual is the default and can be served by any of the three replicas.

- Cost: 0.5 Read Capacity Units (RCU) per 4 kilobytes (KB)
- May return a value older than the last acknowledged write
- Use by default; strong only where read-after-write matters
  - Prevents: paying 2x for nothing

## 2. Strong Reads

`ConsistentRead=true` goes to the partition leader and returns the latest acknowledged write.

- Cost: 1 RCU per 4 KB = 2x
- Only on the base table and Local Secondary Indexes (LSIs)
  - Result: a Global Secondary Index (GSI) query with `ConsistentRead=true` is a `ValidationException`
- Higher latency
- Fails if the leader is unreachable (rare)

## 3. Read-Your-Write Without A Strong Read

The write itself can return the new item, so no follow-up read is needed.

→ Ask for `ReturnValues=ALL_NEW` on the write  
⇒ No second read at all

- Same rule in best practices: use `ReturnValues` instead of read-after-write
- Example: `UPDATED_NEW` in [06conditions-updates](02dynamodb.06conditions-updates.md#2-update-expressions)

## 4. GetItem In Code

Both stacks expose the consistency flag per call.

**Java**

```java
// infra/_03db_02dynamodb/DynamoDbShowcase.java
// consistentRead=false (default): 0.5 RCU per 4 KB, may miss the latest write.
// consistentRead=true: 1 RCU per 4 KB (2x), served by the partition leader; base table and LSI only.
public Optional<Order> getOrder(OrderRef ref, boolean consistentRead) {
    GetItemResponse resp = client.getItem(r -> r
            .tableName(props.ordersTable())
            .key(key(ref.pk(), ref.sk()))
            .consistentRead(consistentRead));
    if (!resp.hasItem() || resp.item().isEmpty()) {
        return Optional.empty(); // missing item = empty response, not an exception
    }
    return Optional.of(OrderItemMapper.toOrder(resp.item()));
}
```

```java
// infra/_03db_02dynamodb/EnhancedClientShowcase.java
public Optional<Order> getOrder(OrderRef ref, boolean consistentRead) {
    OrderItem item = orders.getItem(GetItemEnhancedRequest.builder()
            .key(Key.builder().partitionValue(ref.pk()).sortValue(ref.sk()).build())
            .consistentRead(consistentRead)
            .build());
    return Optional.ofNullable(item).map(OrderItem::toOrder); // null for a missing item
}
```

**Python**

```python
# app/infra/_03db_02dynamodb.py
def get_order(self, ref: OrderRef, consistent: bool = False) -> Order | None:
    resp = self.client.get_item(
        TableName=self.orders_table, Key=to_av(key_of(ref)), ConsistentRead=consistent
    )
    # missing item = response without "Item", not an error
    return from_item(from_av(resp["Item"])) if "Item" in resp else None

def get_order_resource(self, ref: OrderRef, consistent: bool = False) -> Order | None:
    """Table API: already-deserialized values, numbers as Decimal."""
    resp = self.table.get_item(Key=key_of(ref), ConsistentRead=consistent)
    return from_item(resp["Item"]) if "Item" in resp else None
```

**Catch**

→ Eventual read or GSI read right after a write  
⇒ Stale read: the read misses the new value  
→ Use `ConsistentRead` on the base table, or `ReturnValues` on the write

- The idempotent replay path uses a strong read on purpose ([09transactions-idempotency](02dynamodb.09transactions-idempotency.md))

## Related

- [00index](02dynamodb.00index.md)
- [04indexes-gsi-lsi](02dynamodb.04indexes-gsi-lsi.md)
- [01architecture](02dynamodb.01architecture.md#3-write-and-read-paths)
