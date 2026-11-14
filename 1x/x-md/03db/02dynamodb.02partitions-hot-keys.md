# 03db.02dynamodb.02partitions-hot-keys Partitions, Capacity, And Hot Keys

> How partitions cap throughput, why one hot key throttles a quiet table, and how write sharding spreads it.

## Index

- [1. Partitions And Capacity Units](#1-partitions-and-capacity-units)
  - [1.1 Partition Limits](#11-partition-limits)
  - [1.2 Capacity Units](#12-capacity-units)
- [2. Splitting And Adaptive Capacity](#2-splitting-and-adaptive-capacity)
- [3. Hot Partition](#3-hot-partition)
- [4. Write Sharding And Scatter-Gather](#4-write-sharding-and-scatter-gather)
- [Related](#related)

## 1. Partitions And Capacity Units

A partition is the unit of both storage and throughput, so its limits are the limits of any single key.

### 1.1 Partition Limits

- Up to 3,000 Read Capacity Units (RCU) and 1,000 Write Capacity Units (WCU) per partition
  - Source: Developer Guide, "Partition key design"
- About 10 gigabytes (GB) per partition
  - Order of magnitude; DynamoDB splits beyond it

### 1.2 Capacity Units

- **1 RCU**: one strong read/s of up to 4 kilobytes (KB), or two eventual reads/s
- **1 WCU**: one write/s of up to 1 KB
- Transactional read or write = 2 units
- Size rounds up
  - A 4.1 KB strong read = 2 RCU

## 2. Splitting And Adaptive Capacity

DynamoDB reshapes partitions under load, but neither mechanism can split one item.

- **Splitting**
  - DynamoDB splits a partition when it grows past storage limits
  - Also when it stays hot ("split for heat")
  - Split for heat helps only when the heat spreads across many Sort Key (SK) values
    - Result: one single item can never exceed one partition's limit
- **Adaptive capacity**
  - Lets a hot partition borrow unused table throughput
  - Applied instantly (Developer Guide, "Burst and adaptive capacity")
  - Limit: still capped by the per-partition maximum
    - Result: it fixes uneven keys, not a single hot key

## 3. Hot Partition

A hot partition is one Partition Key (PK) taking most of the traffic.

→ One PK takes most of the traffic  
⇒ `ProvisionedThroughputExceededException` / `ThrottlingException` on that key  
⇒ The rest of the table sits idle

- Detect
  - `ThrottledRequests` while table capacity is unused
  - CloudWatch Contributor Insights top keys
- Fix
  - Write sharding (below)
  - Cache reads
  - Redesign the key
- Typical trigger in this repo: `GSI1PK=STATUS#PENDING`
  - Every new order writes it ⇒ one Global Secondary Index (GSI) partition takes all order writes (max 1,000 WCU)
  - GSI throttling back-pressures base-table writes ([04indexes-gsi-lsi](02dynamodb.04indexes-gsi-lsi.md))

## 4. Write Sharding And Scatter-Gather

Write sharding spreads one logical key over N physical keys; reads then fan out over all N.

- Example: `STATUS#PENDING` → `STATUS#PENDING#0` … `STATUS#PENDING#9`
- Suffix choice
  - **Calculated suffix** (hash of order id): a single item stays findable
  - **Random suffix**: best spread, but reads must fan out
- Reads become scatter-gather
  - Query N shards, merge
- Cost: N queries per read
  - Pick N from peak writes / 1,000 WCU

**Java**

```java
// domain/_03db_02dynamodb/OrderKeys.java
// Calculated suffix (CRC32 of orderId) so Java and Python writers agree and one order maps to one shard.
public static String gsi1PkSharded(OrderStatus status, String orderId, int shards) {
    return gsi1Pk(status) + "#" + shardOf(orderId, shards);
}

public static int shardOf(String orderId, int shards) {
    CRC32 crc = new CRC32();
    crc.update(orderId.getBytes(StandardCharsets.UTF_8));
    return (int) (crc.getValue() % shards);
}
```

```java
// infra/_03db_02dynamodb/DynamoDbShowcase.java
public boolean putOrderShardedStatus(Order order, int shards) {
    Map<String, AttributeValue> item = OrderItemMapper.toItem(order);
    if (!order.status().isTerminal()) {
        item.put("GSI1PK", s(OrderKeys.gsi1PkSharded(order.status(), order.orderId(), shards)));
    }
    // ... putItem with attribute_not_exists(PK)
}

// Query all N shards in parallel, merge by GSI1SK (createdAt), keep the oldest `limit`.
// Each shard returns at most `limit`, so the merged top-`limit` is exact.
public List<OrderSummary> scatterGatherByStatus(OrderStatus status, int shards, int limit) {
    ExecutorService pool = Executors.newFixedThreadPool(Math.min(shards, 16));
    // ...
    for (int shard = 0; shard < shards; shard++) {
        String shardKey = OrderKeys.gsi1PkShard(status, shard);
        futures.add(pool.submit(() -> client.query(r -> r
                .tableName(props.ordersTable())
                .indexName(props.gsi1Name())
                .keyConditionExpression("GSI1PK = :pk")
                .expressionAttributeValues(Map.of(":pk", s(shardKey)))
                .scanIndexForward(true)
                .limit(limit)).items()));
    }
    // ... collect, then:
    return merged.stream()
            .sorted(Comparator.comparing(OrderSummary::createdAt))
            .limit(limit)
            .collect(Collectors.toList());
}
```

**Python**

```python
# app/domain/_03db_02dynamodb.py
def shard_of(order_id: str, shards: int) -> int:
    """CRC32 suffix: identical to the Java OrderKeys.shardOf, so both writers agree on the shard."""
    return zlib.crc32(order_id.encode("utf-8")) % shards
```

```python
# app/infra/_03db_02dynamodb.py
def scatter_gather_by_status(self, status: OrderStatus, shards: int, limit: int) -> list[OrderSummary]:
    def query_shard(shard: int) -> list[OrderSummary]:
        resp = self.client.query(
            TableName=self.orders_table,
            IndexName=self.gsi1,
            KeyConditionExpression="GSI1PK = :pk",
            ExpressionAttributeValues=to_av({":pk": gsi1_pk_shard(status, shard)}),
            ScanIndexForward=True,
            Limit=limit,
        )
        return [summary_from_item(from_av(i)) for i in resp.get("Items", [])]

    with ThreadPoolExecutor(max_workers=min(shards, 16)) as pool:
        merged = [s for part in pool.map(query_shard, range(shards)) for s in part]
    return sorted(merged, key=lambda s: s.created_at)[:limit]
```

**Catch**

- Sharding is a variant of the `.tf` key design
  - All writers and readers must use the same N and suffix function
  - Pick one scheme per table, not both
- N queries per read
  - N x latency tail (latency = slowest shard)
  - N x request cost

## Related

- [00index](02dynamodb.00index.md)
- [04indexes-gsi-lsi](02dynamodb.04indexes-gsi-lsi.md)
- [11capacity-modes](02dynamodb.11capacity-modes.md)
