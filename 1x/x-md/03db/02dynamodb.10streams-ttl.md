# 03db.02dynamodb.10streams-ttl Streams, Time To Live (TTL), And Point-In-Time Recovery (PITR)

> The per-item change log, lazy Time To Live (TTL) expiry, how the two combine for archiving, and point-in-time restore.

## Index

- [1. Streams](#1-streams)
  - [1.1 Record Shape](#11-record-shape)
  - [1.2 Stream Handler In Code](#12-stream-handler-in-code)
- [2. TTL](#2-ttl)
  - [2.1 TTL Write And Expired Filter In Code](#21-ttl-write-and-expired-filter-in-code)
- [3. Streams Plus TTL](#3-streams-plus-ttl)
- [4. Point-In-Time Recovery (PITR)](#4-point-in-time-recovery-pitr)
- [Related](#related)

## 1. Streams

DynamoDB Streams is an ordered change log per item key (per partition), with records kept 24 hours.

- View types
  - `KEYS_ONLY`
  - `NEW_IMAGE`
  - `OLD_IMAGE`
  - `NEW_AND_OLD_IMAGES` (`x-orders` uses this)
- Each change appears once in the stream
  - Limit: consumers (Lambda, Kinesis Client Library (KCL)) retry batches ⇒ processing is at-least-once
  - Result: make the handler idempotent (key by `eventID` or item version)
- Uses
  - Outbox / Change Data Capture (CDC)
  - Search indexing (e.g. OpenSearch for full-text or geo)
  - Aggregates
  - Cross-Region fan-out

### 1.1 Record Shape

- `eventName`: `INSERT` / `MODIFY` / `REMOVE`
- `Keys`, `NewImage`, `OldImage`, `SequenceNumber`
- INSERT has only `NewImage`; REMOVE only `OldImage`; MODIFY both
- Same shape from `GetRecords` and in the Lambda event

### 1.2 Stream Handler In Code

**Java**

```java
// infra/_03db_02dynamodb/StreamRecordHandler.java
static final String TTL_PRINCIPAL = "dynamodb.amazonaws.com"; // TTL deletes, userIdentity.type = "Service"

public Optional<OrderChange> handle(Record record) {
    StreamRecord ddb = record.dynamodb();
    Map<String, AttributeValue> keys = ddb.hasKeys() ? ddb.keys() : Map.of();
    if (!OrderItemMapper.isOrder(keys)) {
        return Optional.empty(); // PROFILE and other items ignored
    }
    Order before = ddb.hasOldImage() && !ddb.oldImage().isEmpty() ? OrderItemMapper.toOrder(ddb.oldImage()) : null;
    Order after = ddb.hasNewImage() && !ddb.newImage().isEmpty() ? OrderItemMapper.toOrder(ddb.newImage()) : null;
    Identity who = record.userIdentity();
    boolean ttl = record.eventName() == OperationType.REMOVE
            && who != null && "Service".equals(who.type()) && TTL_PRINCIPAL.equals(who.principalId());
    return Optional.of(new OrderChange(record.eventID(), ddb.sequenceNumber(),
            OrderChange.Type.valueOf(record.eventNameAsString()), before, after, ttl));
}
```

**Python**

```python
# app/infra/_03db_02dynamodb.py
def handle_stream_record(record: dict[str, Any]) -> OrderChange | None:
    ddb = record.get("dynamodb", {})
    keys = from_av(ddb.get("Keys", {}))
    if not str(keys.get("SK", "")).startswith(ORDER_PREFIX):
        return None
    before = from_item(from_av(ddb["OldImage"])) if ddb.get("OldImage") else None
    after = from_item(from_av(ddb["NewImage"])) if ddb.get("NewImage") else None
    identity = record.get("userIdentity") or {}
    ttl = (
        record.get("eventName") == "REMOVE"
        and identity.get("type") == "Service"
        and identity.get("principalId") == TTL_PRINCIPAL
    )
    return OrderChange(event_id=str(record.get("eventID", "")),
                       sequence_number=str(ddb.get("SequenceNumber", "")),
                       type=ChangeType(record["eventName"]), before=before, after=after, ttl_expiry=ttl)
```

**Catch**

- `sampleModifyRecord` / `sample_modify_record` build a MODIFY record by hand
  - Documents the shape; makes the handler testable without Amazon Web Services (AWS)
  - Real records also carry `eventSource "aws:dynamodb"`, `awsRegion`, `SizeBytes`, `ApproximateCreationDateTime`
- Streams keep 24 h ⇒ a consumer down longer loses changes
  - Use Kinesis Data Streams for DynamoDB for longer retention
- Only the record shape is coded; real consumption (Lambda / KCL) is a gap

## 2. TTL

TTL deletes items in the background once a Number attribute (`expiresAt`, epoch seconds) has passed.

- A background process deletes items after that time
- Deletion is not exact: typically within a few days (Developer Guide, "Time to Live")
  - Result: expired items still appear in reads; filter on `expiresAt > :now`
- No Write Capacity Unit (WCU) charge for TTL deletes
- Uses: carts, sessions, idempotency records, soft-deleted orders

→ Relying on TTL deletion time  
⇒ Expired items returned in results  
→ Filter `expiresAt > :now`; treat expired as absent in conditions

### 2.1 TTL Write And Expired Filter In Code

**Java**

```java
// infra/_03db_02dynamodb/DynamoDbShowcase.java
public long expireOrderAfter(OrderRef ref, Duration ttl) {
    long expiresAt = Instant.now().plus(ttl).getEpochSecond(); // SECONDS, not millis
    client.updateItem(r -> r
            .tableName(props.ordersTable())
            .key(key(ref.pk(), ref.sk()))
            .updateExpression("SET expiresAt = :exp")
            .conditionExpression("attribute_exists(PK)") // don't create a stub item for a missing order
            .expressionAttributeValues(Map.of(":exp", n(expiresAt))));
    return expiresAt;
}

// Filter runs after the read: you still pay for expired items.
public List<Order> queryLiveOrders(String customerId, Instant now) {
    QueryRequest req = QueryRequest.builder()
            .tableName(props.ordersTable())
            .keyConditionExpression("PK = :pk AND begins_with(SK, :prefix)")
            .filterExpression("attribute_not_exists(expiresAt) OR expiresAt > :now")
            // ... :pk, :prefix, :now = now.getEpochSecond()
            .build();
    return client.queryPaginator(req).items().stream().map(OrderItemMapper::toOrder).toList();
}
```

**Python**

```python
# app/infra/_03db_02dynamodb.py
def expire_order_after(self, ref: OrderRef, ttl: timedelta) -> int:
    expires_at = int((datetime.now(timezone.utc) + ttl).timestamp())
    self.client.update_item(
        TableName=self.orders_table,
        Key=to_av(key_of(ref)),
        UpdateExpression="SET expiresAt = :exp",
        ConditionExpression="attribute_exists(PK)",  # don't create a stub item for a missing order
        ExpressionAttributeValues=to_av({":exp": expires_at}),
    )
    return expires_at
```

**Catch**

- Epoch millis would mean "expires in 50,000 years" (never in practice)
- `Limit` counts items before the filter ⇒ a page can come back short
- Filter whenever expiry has business meaning (an expired session must not authenticate)

## 3. Streams Plus TTL

TTL deletes flow through the stream, so they can be archived.

→ TTL deletes an item whose `expiresAt` has passed  
→ Stream emits a `REMOVE` record with the old image  
→ Record carries `userIdentity.principalId = dynamodb.amazonaws.com`  
⇒ Archive only those records (e.g. to Simple Storage Service (S3)) by consuming them

## 4. Point-In-Time Recovery (PITR)

- Restore to any second in the last 35 days
- Separate from streams
- Enabled on `x-orders` in Terraform

## Related

- [00index](02dynamodb.00index.md)
- [09transactions-idempotency](02dynamodb.09transactions-idempotency.md)
- [07query-pagination-scan](02dynamodb.07query-pagination-scan.md)
