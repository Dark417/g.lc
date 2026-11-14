# 03db.02dynamodb.06conditions-updates Condition And Update Expressions

> The condition expression is DynamoDB's concurrency primitive: create-only, optimistic lock, guarded state change.

## Index

- [1. Condition Expressions](#1-condition-expressions)
  - [1.1 Patterns](#11-patterns)
  - [1.2 Failure](#12-failure)
  - [1.3 Create-Only Put In Code](#13-create-only-put-in-code)
- [2. Update Expressions](#2-update-expressions)
- [3. Optimistic Lock](#3-optimistic-lock)
- [4. Limits](#4-limits)
- [Related](#related)

## 1. Condition Expressions

A write carries a predicate; the partition leader checks it atomically with the write.

- 🗣 "Every correctness guarantee in DynamoDB is a condition expression."
- Every non-idempotent write carries a condition
  - Prevents: lost updates and duplicate creates

### 1.1 Patterns

- **Create-only**: `attribute_not_exists(PK)`
  - Checked against the one item with the full key (Partition Key (PK) + Sort Key (SK)), not the whole partition
- **Optimistic lock**: `version = :expected`, then `SET version = version + :one`
- **Guarded state change**: `#status = :pending`
- **Idempotency record**: `attribute_not_exists(idempotencyKey) OR expiresAt < :now`
  - See [09transactions-idempotency](02dynamodb.09transactions-idempotency.md)

### 1.2 Failure

- Raises `ConditionalCheckFailedException`
- Still consumes write capacity
- `ReturnValuesOnConditionCheckFailure=ALL_OLD` returns the current item
  - Result: no extra read to see who won

### 1.3 Create-Only Put In Code

A plain `PutItem` silently replaces the whole item; create-only makes it an insert.

**Java**

```java
// infra/_03db_02dynamodb/DynamoDbShowcase.java
public boolean putOrderCreateOnly(Order order) {
    try {
        client.putItem(PutItemRequest.builder()
                .tableName(props.ordersTable())
                .item(OrderItemMapper.toItem(order))
                .conditionExpression("attribute_not_exists(PK)") // the ONE item with this PK+SK
                .returnValuesOnConditionCheckFailure(ReturnValuesOnConditionCheckFailure.ALL_OLD)
                .build());
        return true;
    } catch (ConditionalCheckFailedException e) {
        return false; // e.item() = the order that already exists
    }
}
```

```java
// infra/_03db_02dynamodb/EnhancedClientShowcase.java
// version=null makes VersionedRecordExtension add attribute_not_exists(version) and write 1;
// the explicit attribute_not_exists(PK) is ANDed with it.
public boolean putCreateOnly(Order order) {
    try {
        orders.putItem(PutItemEnhancedRequest.builder(OrderItem.class)
                .item(OrderItem.from(order, null))
                .conditionExpression(Expression.builder().expression("attribute_not_exists(PK)").build())
                .build());
        return true;
    } catch (ConditionalCheckFailedException e) {
        return false;
    }
}
```

**Python**

```python
# app/infra/_03db_02dynamodb.py
def put_order_create_only(self, order: Order) -> bool:
    try:
        self.client.put_item(
            TableName=self.orders_table,
            Item=to_av(to_item(order)),
            ConditionExpression="attribute_not_exists(PK)",
            ReturnValuesOnConditionCheckFailure="ALL_OLD",  # existing item in e.response["Item"]
        )
        return True
    except ClientError as e:
        if _error_code(e) == "ConditionalCheckFailedException":
            return False
        raise

def put_order_create_only_resource(self, order: Order) -> bool:
    """Table API: plain values + Attr condition builder (placeholders auto-made)."""
    try:
        self.table.put_item(Item=to_item(order), ConditionExpression=Attr("PK").not_exists())
        return True
    except ClientError as e:
        if _error_code(e) == "ConditionalCheckFailedException":
            return False
        raise
```

**Catch**

- Enhanced Client: a plain `putItem(bean)` with a non-null version is a conditional overwrite, not an insert
- boto3: the exception class lives on `table.meta.client.exceptions`; matching the error code is simpler

## 2. Update Expressions

One `UpdateItem` can mix all clause kinds and upserts the item if missing.

- `SET a = :v`
- `SET n = if_not_exists(n, :zero) + :one`
- `ADD counter :n` (numbers and sets only)
- `REMOVE attr`
- `DELETE set :values` (remove elements from a set)
- `ReturnValues=UPDATED_NEW` = only touched attributes, after the change
  - No read-after-write

**Java**

```java
// infra/_03db_02dynamodb/DynamoDbShowcase.java
public ProfileStats recordOrderOnProfile(String customerId, long amountCents, Instant at) {
    UpdateItemResponse resp = client.updateItem(r -> r
            .tableName(props.ordersTable())
            .key(key(OrderKeys.customerPk(customerId), OrderKeys.PROFILE_SK))
            .updateExpression("SET lastOrderAt = :at, displayName = if_not_exists(displayName, :anon) "
                    + "ADD orderCount :one, totalSpentCents :amount "
                    + "REMOVE pendingCartId")
            .expressionAttributeValues(Map.of(
                    ":at", s(OrderKeys.iso(at)),
                    ":anon", s("anonymous"),
                    ":one", n(1),
                    ":amount", n(amountCents)))
            .returnValues(ReturnValue.UPDATED_NEW));
    return OrderItemMapper.toProfileStats(customerId, resp.attributes());
}
```

**Python**

```python
# app/infra/_03db_02dynamodb.py
def record_order_on_profile(self, customer_id: str, amount_cents: int, at: datetime) -> ProfileStats:
    resp = self.client.update_item(
        TableName=self.orders_table,
        Key=to_av({"PK": pk_customer(customer_id), "SK": PROFILE_SK}),
        UpdateExpression=(
            "SET lastOrderAt = :at, displayName = if_not_exists(displayName, :anon) "
            "ADD orderCount :one, totalSpentCents :amount "
            "REMOVE pendingCartId"
        ),
        ExpressionAttributeValues=to_av({":at": iso(at), ":anon": "anonymous", ":one": 1, ":amount": amount_cents}),
        ReturnValues="UPDATED_NEW",
    )
    return self._profile_stats(customer_id, from_av(resp.get("Attributes", {})))
```

**Catch**

- `ADD` is not idempotent
  - Result: a blind retry after a timeout double-counts
  - Guard with a condition or a transaction
- Trick: store counters on a parent item and update them in the same transaction as the child

## 3. Optimistic Lock

A `version` attribute plus a condition prevents lost updates without holding any lock.

→ Read-modify-write with no condition  
⇒ Lost update: values silently overwritten  
→ `version` condition; `ALL_OLD` on failure

- Update with `version = :expected` and `SET version = version + 1`
- On `ConditionalCheckFailedException`
  - Re-read, re-apply, retry, or return Hypertext Transfer Protocol (HTTP) 409
- Terminal statuses REMOVE `GSI1PK` / `GSI1SK`
  - Result: the order leaves the "pending" Global Secondary Index (GSI; sparse index)
- Trick: version attribute + `ALL_OLD` on failure = conflict resolution without a read

**Java**

```java
// infra/_03db_02dynamodb/DynamoDbShowcase.java
public Order changeStatusWithVersion(OrderRef ref, OrderStatus newStatus, long expectedVersion) {
    // ... values :new, :expected, :one
    String update = newStatus.isTerminal()
            ? "SET #status = :new, #version = #version + :one REMOVE GSI1PK, GSI1SK"
            : "SET #status = :new, #version = #version + :one, GSI1PK = :gsiPk";
    try {
        UpdateItemResponse resp = client.updateItem(r -> r
                .tableName(props.ordersTable())
                .key(key(ref.pk(), ref.sk()))
                .updateExpression(update)
                .conditionExpression("attribute_exists(PK) AND #version = :expected")
                .expressionAttributeNames(Map.of("#status", "status", "#version", "version"))
                .expressionAttributeValues(values)
                .returnValues(ReturnValue.ALL_NEW)
                .returnValuesOnConditionCheckFailure(ReturnValuesOnConditionCheckFailure.ALL_OLD));
        return OrderItemMapper.toOrder(resp.attributes());
    } catch (ConditionalCheckFailedException e) {
        // No item in the exception = attribute_exists(PK) failed = the order does not exist.
        throw new VersionConflictException(e.hasItem() && !e.item().isEmpty()
                ? OrderItemMapper.toOrder(e.item()) : null);
    }
}
```

```java
// infra/_03db_02dynamodb/OrderItem.java
@DynamoDbVersionAttribute // VersionedRecordExtension adds "version = :old" and increments
public Long getVersion() { return version; }

// infra/_03db_02dynamodb/EnhancedClientShowcase.java
// Default null handling = full-state update: null attributes are REMOVEd (terminal status drops GSI1PK/GSI1SK).
public Order updateWithVersionAttribute(Order current, OrderStatus newStatus) {
    OrderItem changed = OrderItem.from(current.withStatus(newStatus), current.version());
    try {
        OrderItem saved = orders.updateItem(UpdateItemEnhancedRequest.builder(OrderItem.class)
                .item(changed)
                .returnValuesOnConditionCheckFailure(ReturnValuesOnConditionCheckFailure.ALL_OLD)
                .build());
        return saved.toOrder();
    } catch (ConditionalCheckFailedException e) {
        // ... map e.item() to the winner, throw VersionConflictException
    }
}
```

**Python**

```python
# app/infra/_03db_02dynamodb.py
def change_status_with_version_resource(self, ref: OrderRef, status: OrderStatus, expected_version: int) -> Order:
    """Attr builders; boto3 merges its generated placeholders with ours."""
    names = {"#status": "status", "#version": "version"}
    values: Item = {":new": status.value, ":one": 1}
    if status.is_terminal:
        update = "SET #status = :new, #version = #version + :one REMOVE GSI1PK, GSI1SK"
    else:
        update = "SET #status = :new, #version = #version + :one, GSI1PK = :gsiPk"
        values[":gsiPk"] = gsi1_pk(status)
    try:
        resp = self.table.update_item(
            Key=key_of(ref),
            UpdateExpression=update,
            ConditionExpression=Attr("PK").exists() & Attr("version").eq(expected_version),
            ExpressionAttributeNames=names,
            ExpressionAttributeValues=values,
            ReturnValues="ALL_NEW",
            ReturnValuesOnConditionCheckFailure="ALL_OLD",
        )
        return from_item(resp["Attributes"])
    except ClientError as e:
        if _error_code(e) == "ConditionalCheckFailedException":
            old = e.response.get("Item")  # still AttributeValue: error responses are not deserialized
            raise VersionConflictError(from_item(from_av(old)) if old else None) from e
        raise
```

**Catch**

- Enhanced Client with `IgnoreNullsMode.SCALAR_ONLY` skips nulls
  - Result: the order would stay in the "pending" index
- For commutative changes (counters), `ADD` avoids the lock entirely, but is not idempotent
- Expose version as an Entity Tag (ETag) + `If-Match` in the Application Programming Interface (API)

## 4. Limits

One condition covers one item.

⇒ Cross-item invariants need a transaction ([09transactions-idempotency](02dynamodb.09transactions-idempotency.md))

## Related

- [00index](02dynamodb.00index.md)
- [09transactions-idempotency](02dynamodb.09transactions-idempotency.md)
- [04indexes-gsi-lsi](02dynamodb.04indexes-gsi-lsi.md#12-projection-and-sparse-index)
