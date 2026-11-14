# 03db.02dynamodb.04indexes-gsi-lsi Indexes: Global Secondary Index (GSI) And Local Secondary Index (LSI)

> How global and local secondary indexes differ, sparse indexes, projections, and Global Secondary Index (GSI) back-pressure.

## Index

- [1. GSI](#1-gsi)
  - [1.1 Mechanism](#11-mechanism)
  - [1.2 Projection And Sparse Index](#12-projection-and-sparse-index)
  - [1.3 Back-Pressure](#13-back-pressure)
- [2. Local Secondary Index (LSI)](#2-local-secondary-index-lsi)
- [3. Comparison And Default](#3-comparison-and-default)
- [4. GSI Query In Code](#4-gsi-query-in-code)
- [Related](#related)

## 1. GSI

A **GSI** (global secondary index) is a second table, keyed differently, maintained by DynamoDB.

### 1.1 Mechanism

- Updated asynchronously
  - Result: eventually consistent reads only
- Own partitions and own capacity
- Default quota: 20 per table (Developer Guide, "Service quotas")
- GSI keys need not be unique

### 1.2 Projection And Sparse Index

- Projection decides what is copied
  - `KEYS_ONLY`
  - `INCLUDE`
  - `ALL`
- `x-orders` uses `INCLUDE` with `orderId`, `customerId`, `amountCents`
- Project only what the pattern needs (`INCLUDE`)
  - Prevents: write amplification on every base write
- **Sparse index**: items without the GSI key attribute are not indexed
  - Result: REMOVE `GSI1PK` when an order is done, and it drops out of "pending"
  - Trick: sparse GSI as a work queue (only items with `GSI1PK` are indexed)

### 1.3 Back-Pressure

A throttled GSI throttles writes to the base table.

→ GSI capacity or key skew below the base table  
⇒ Base writes throttled; GSI throttle metrics rise  
→ Shard the GSI key; provision GSI ≥ base; or on-demand

- Size or shard the GSI like the base table
- Shard low-cardinality GSI keys (status, date)
  - Prevents: GSI back-pressure throttling base writes
- Sharding mechanics: [02partitions-hot-keys](02dynamodb.02partitions-hot-keys.md#4-write-sharding-and-scatter-gather)

## 2. Local Secondary Index (LSI)

An **LSI** (local secondary index) keeps the same Partition Key (PK) with a different sort key.

- Supports strong reads
- Must be created with the table; cannot be added later
- Max 5 per table
- Item collection (all items with one PK, plus LSI copies) capped at 10 gigabytes (GB)
  - Result: a growing customer can hit `ItemCollectionSizeLimitExceededException`
- Shares the base partition's throughput

## 3. Comparison And Default

| Index | Keys | Consistency | Capacity | Added later |
|---|---|---|---|---|
| GSI | Any PK + Sort Key (SK) | Eventual only | Own | Yes, online backfill |
| LSI | Same PK, other SK | Strong or eventual | Shares base | No, table creation only |

Pick: GSI, unless you need strong reads on an alternate sort order and the collection stays under 10 GB.

## 4. GSI Query In Code

`x-orders` GSI1 serves "all PENDING orders, oldest first".

**Java**

```java
// infra/_03db_02dynamodb/DynamoDbShowcase.java
// Returns only keys + the INCLUDE projection. ConsistentRead=true is rejected on a GSI.
public List<OrderSummary> queryByStatus(OrderStatus status, int limit) {
    QueryResponse resp = client.query(r -> r
            .tableName(props.ordersTable())
            .indexName(props.gsi1Name())
            .keyConditionExpression("GSI1PK = :pk")
            .expressionAttributeValues(Map.of(":pk", s(OrderKeys.gsi1Pk(status))))
            .scanIndexForward(true) // ascending GSI1SK (createdAt) = oldest first
            .limit(limit));
    return resp.items().stream().map(OrderItemMapper::toSummary).toList();
}
```

```java
// infra/_03db_02dynamodb/OrderItem.java
@DynamoDbSecondaryPartitionKey(indexNames = "GSI1") // index names in annotations are compile-time constants
@DynamoDbAttribute("GSI1PK")
public String getGsi1Pk() { return gsi1Pk; }

// infra/_03db_02dynamodb/EnhancedClientShowcase.java
// Projected-out attributes come back as null fields on the bean.
public List<OrderItem> queryByStatus(OrderStatus status, int limit) {
    SdkIterable<Page<OrderItem>> pages = gsi1.query(QueryEnhancedRequest.builder()
            .queryConditional(QueryConditional.keyEqualTo(
                    Key.builder().partitionValue(OrderKeys.gsi1Pk(status)).build()))
            .limit(limit)
            .build());
    return pages.iterator().next().items();
}
```

**Python**

```python
# app/infra/_03db_02dynamodb.py
def query_by_status(self, status: OrderStatus, limit: int) -> list[OrderSummary]:
    resp = self.client.query(
        TableName=self.orders_table,
        IndexName=self.gsi1,
        KeyConditionExpression="GSI1PK = :pk",
        ExpressionAttributeValues=to_av({":pk": gsi1_pk(status)}),
        ScanIndexForward=True,
        Limit=limit,
    )
    return [summary_from_item(from_av(i)) for i in resp.get("Items", [])]

def to_item(order: Order) -> Item:
    # ...
    if not order.status.is_terminal:  # GSI1 keys only for non-terminal statuses (sparse index)
        item["GSI1PK"] = gsi1_pk(order.status)
        item["GSI1SK"] = gsi1_sk(order.created_at)
```

**Catch**

- Never use a GSI read for uniqueness or to decide a write
  - Re-read the base item (strong) first
  - GSI lag is usually small but unbounded under GSI throttling
- `status` / `version` are not projected into GSI1
  - Never act on them from an index read

## Related

- [00index](02dynamodb.00index.md)
- [05single-table-design](02dynamodb.05single-table-design.md)
- [02partitions-hot-keys](02dynamodb.02partitions-hot-keys.md)
