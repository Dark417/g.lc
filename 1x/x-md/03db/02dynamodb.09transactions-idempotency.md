# 03db.02dynamodb.09transactions-idempotency Transactions And Idempotent Place Order

> `TransactWriteItems` semantics, cancellation reasons, and the idempotent "place order" use case built on one transaction.

## Index

- [1. TransactWriteItems](#1-transactwriteitems)
  - [1.1 Limits And Cost](#11-limits-and-cost)
  - [1.2 ClientRequestToken](#12-clientrequesttoken)
  - [1.3 Cancellation Reasons](#13-cancellation-reasons)
  - [1.4 Isolation](#14-isolation)
- [2. The Place-Order Transaction In Code](#2-the-place-order-transaction-in-code)
- [3. Idempotent Place Order Use Case](#3-idempotent-place-order-use-case)
- [Related](#related)

## 1. TransactWriteItems

A transaction is all-or-nothing across items, at twice the write cost.

- 🗣 Transactions exist (up to 100 items) but cost 2x and conflict under contention

### 1.1 Limits And Cost

- Up to 100 actions, 4 megabytes (MB) total
  - Source: Developer Guide, "Transactions"; raised from 25 in 2022
- Actions: Put, Update, Delete, ConditionCheck
- All succeed or none
- Items may span tables in the same account and Region
- No two actions may target the same item
- Cost: 2 Write Capacity Units (WCU) per kilobyte (KB) per item (prepare + commit)

### 1.2 ClientRequestToken

The token makes Software Development Kit (SDK)-level resends of one call idempotent.

- Same token within 10 minutes → treated as the same call, not applied twice
- Same token with different parameters → `IdempotentParameterMismatchException`
- `TransactionInProgressException` = same token still being applied ⇒ wait and resend
- Limit: 10 minutes covers SDK retries, not a client retrying tomorrow
  - Result: keep an idempotency record for the client's retry horizon

### 1.3 Cancellation Reasons

`TransactionCanceledException` carries one reason per action, in request order.

- Codes
  - `None`
  - `ConditionalCheckFailed`
  - `TransactionConflict`
  - `ThrottlingError`
  - `ValidationError`
  - `ItemCollectionSizeLimitExceeded`
  - `ProvisionedThroughputExceeded`
- `TransactionConflict` = another transaction or write touched the item
  - Result: retry with backoff
- `ConditionalCheckFailed` = business outcome
  - Result: do not retry blindly

→ Concurrent writes to the same items  
⇒ `TransactionConflict` reasons  
→ Backoff retry; shrink transactions; avoid hot items

### 1.4 Isolation

- Serializable between transactions and single-item writes
- A `Query` or `Scan` is read-committed only
  - It may return some items of a transaction and not others

## 2. The Place-Order Transaction In Code

One atomic write across 2 tables and 3 items: order (create-only) + idempotency record (create-only, or expired) + profile counters.

**Java**

```java
// infra/_03db_02dynamodb/DynamoDbShowcase.java
static final List<String> TX_LABELS = List.of("order", "idempotency", "profile");

public PlaceAttempt placeOrderTransaction(Order order, IdempotencyRecord record, Instant now) {
    TransactWriteItem putOrder = /* Put order, conditionExpression("attribute_not_exists(PK)") */;
    // TTL deletion is lazy (typically within days): an expired-but-present record must count as absent.
    TransactWriteItem putIdempotency = TransactWriteItem.builder().put(Put.builder()
            .tableName(props.idempotencyTable())
            .item(OrderItemMapper.toItem(record))
            .conditionExpression("attribute_not_exists(idempotencyKey) OR expiresAt < :now")
            .expressionAttributeValues(Map.of(":now", n(now.getEpochSecond())))
            // On failure, the stored record comes back inside the cancellation reason: no extra read.
            .returnValuesOnConditionCheckFailure(ReturnValuesOnConditionCheckFailure.ALL_OLD)
            .build()).build();
    TransactWriteItem bumpProfile = /* Update PROFILE: SET lastOrderAt ADD orderCount, totalSpentCents */;

    // Token (1-36 chars) from key + fresh orderId: a different request never reuses it,
    // while SDK-level resends of this request still dedupe.
    String token = UUID.nameUUIDFromBytes(
            (record.idempotencyKey() + "|" + order.orderId()).getBytes(StandardCharsets.UTF_8)).toString();
    TransactWriteItemsRequest req = TransactWriteItemsRequest.builder()
            .transactItems(putOrder, putIdempotency, bumpProfile) // order MUST match TX_LABELS
            .clientRequestToken(token)
            .build();
    try {
        retry.call(() -> client.transactWriteItems(req), DynamoDbShowcase::isRetryableTransactionFailure);
        return PlaceAttempt.committed();
    } catch (TransactionCanceledException e) {
        TxCancellation c = parseCancellation(e, TX_LABELS);
        if (c.failedWith("idempotency", "ConditionalCheckFailed")) {
            return PlaceAttempt.keyAlreadyUsed(OrderItemMapper.toIdempotencyRecord(c.itemOf("idempotency")));
        }
        if (c.failedWith("order", "ConditionalCheckFailed")) {
            return PlaceAttempt.orderAlreadyExists();
        }
        throw e; // ValidationError, retries exhausted on conflicts/throttling, ...
    }
}

// Reasons are positional: reasons[i] belongs to transactItems[i].
public static TxCancellation parseCancellation(TransactionCanceledException e, List<String> labels) {
    // ... for each e.cancellationReasons(): new Reason(i, labels.get(i), r.code(), r.message(), r.item())
}

static boolean isRetryableTransactionFailure(Throwable t) {
    if (t instanceof TransactionInProgressException) {
        return true; // same ClientRequestToken still being applied: wait and resend
    }
    return t instanceof TransactionCanceledException e && parseCancellation(e, TX_LABELS).retryable();
}
```

**Python**

```python
# app/infra/_03db_02dynamodb.py
_TRANSIENT_CODES = {"None", "TransactionConflict", "ThrottlingError", "ProvisionedThroughputExceeded"}

def parse_cancellation(e: ClientError, labels: list[str]) -> list[CancellationReason]:
    """botocore puts the modeled CancellationReasons list at the top level of e.response."""
    raw: list[dict[str, Any]] = e.response.get("CancellationReasons") or []
    # ... CancellationReason(index=i, label=labels[i], code=r["Code"], item=from_av(r["Item"]) if present)

def is_retryable_transaction_error(e: Exception) -> bool:
    # ... TransactionInProgressException -> True
    reasons = parse_cancellation(e, TX_LABELS)
    return bool(reasons) and all(r.code in _TRANSIENT_CODES for r in reasons) and any(r.code != "None" for r in reasons)

def place_order_transaction(self, order: Order, record: IdempotencyRecord, now: datetime) -> PlaceAttempt:
    items = [
        {"Put": {"TableName": self.orders_table, "Item": to_av(to_item(order)),
                 "ConditionExpression": "attribute_not_exists(PK)"}},
        {"Put": {
            "TableName": self.idempotency_table,
            "Item": to_av(idempotency_to_item(record)),
            "ConditionExpression": "attribute_not_exists(idempotencyKey) OR expiresAt < :now",
            "ExpressionAttributeValues": to_av({":now": int(now.timestamp())}),
            "ReturnValuesOnConditionCheckFailure": "ALL_OLD",  # stored record comes back in the reason
        }},
        {"Update": {...}},  # PROFILE counters
    ]  # order MUST match TX_LABELS
    token = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{record.idempotency_key}|{order.order_id}"))
    try:
        call_with_retry(
            lambda: self.client.transact_write_items(TransactItems=items, ClientRequestToken=token),
            is_retryable_transaction_error,
        )
        return PlaceAttempt(PlaceStatus.COMMITTED)
    except ClientError as e:
        if _error_code(e) != "TransactionCanceledException":
            raise
        reasons = parse_cancellation(e, TX_LABELS)
        idem = _failed_with(reasons, "idempotency", "ConditionalCheckFailed")
        if idem is not None:
            return PlaceAttempt(PlaceStatus.KEY_ALREADY_USED, idempotency_from_item(idem.item))
        if _failed_with(reasons, "order", "ConditionalCheckFailed"):
            return PlaceAttempt(PlaceStatus.ORDER_ALREADY_EXISTS)
        raise
```

**Catch**

- If the SDK model has no reasons (rare), treat the failure as non-retryable and surface it
- Enhanced Client transactions still throw the low-level `TransactionCanceledException`
  - `VersionedRecordExtension` also applies inside transactions (version=null ⇒ create-only)

## 3. Idempotent Place Order Use Case

The service turns the transaction outcome into "same key + same body ⇒ the original order".

→ Client sends an `Idempotency-Key`  
→ Scope it by caller: `customerId#key`, so two customers cannot collide  
→ Hash the fields that define "the same request"  
→ One transaction: order (`attribute_not_exists(PK)`) + idempotency record (`attribute_not_exists` or expired)  
→ Record exists with same hash → strong-read and return the stored order (`replayed=true`)  
→ Record exists with a different hash → Hypertext Transfer Protocol (HTTP) 422

- Both items commit atomically
  - Result: no "in progress" idempotency state to recover from
- `ClientRequestToken` only covers 10 minutes of identical calls; the record covers the client's horizon
- Retention here: 24 h (`x.dynamodb.idempotency-retention`)

**Java**

```java
// service/_03db_02dynamodb/OrderService.java
public PlaceOrderResult placeOrder(PlaceOrderCommand cmd) {
    Instant now = clock.instant().truncatedTo(ChronoUnit.MILLIS); // keys store millis; keep the record equal
    String scopedKey = OrderKeys.scopedIdempotencyKey(cmd.customerId(), cmd.idempotencyKey());
    String hash = requestHash(cmd);
    Order order = Order.newPending(cmd.customerId(), UUID.randomUUID().toString(), now, cmd.amountCents());
    IdempotencyRecord record = new IdempotencyRecord(
            scopedKey, hash, order.customerId(), order.orderId(), OrderKeys.iso(order.createdAt()),
            now.plus(idempotencyRetention).getEpochSecond());

    PlaceAttempt attempt = store.placeOrder(order, record, now);
    return switch (attempt.status()) {
        case COMMITTED -> new PlaceOrderResult(order, false);
        case KEY_ALREADY_USED -> replay(attempt.existing(), hash, scopedKey);
        // A fresh UUID collided with an existing order: practically impossible; fail loudly.
        case ORDER_ALREADY_EXISTS -> throw new IllegalStateException("order id collision");
    };
}

private PlaceOrderResult replay(IdempotencyRecord existing, String hash, String scopedKey) {
    if (!existing.requestHash().equals(hash)) {
        throw new IdempotencyKeyReuseException(scopedKey); // HTTP 422
    }
    // Strong read: the order committed in the same transaction as the record, so it must exist.
    // ... store.getOrder(ref, true)
}
```

**Python**

```python
# app/service/_03db_02dynamodb.py
IDEMPOTENCY_RETENTION = timedelta(hours=24)  # must outlive the client's maximum retry window

def request_hash(cmd: PlaceOrderCommand) -> str:
    """Fields that define 'the same request'; excludes the key itself and server-generated values."""
    return hashlib.sha256(f"{cmd.customer_id}|{cmd.amount_cents}".encode()).hexdigest()

class PlaceOrderService:
    def place_order(self, cmd: PlaceOrderCommand) -> PlaceOrderResult:
        now = datetime.now(timezone.utc)
        key = scoped_idempotency_key(cmd.customer_id, cmd.idempotency_key)
        digest = request_hash(cmd)
        order = Order.new_pending(cmd.customer_id, str(uuid.uuid4()), now, cmd.amount_cents)
        record = IdempotencyRecord(idempotency_key=key, request_hash=digest, ...,
                                   expires_at=int((now + self.retention).timestamp()))
        attempt = self.store.place_order(order, record, now)
        if attempt.status is PlaceStatus.COMMITTED:
            return PlaceOrderResult(order, replayed=False)
        if attempt.status is PlaceStatus.KEY_ALREADY_USED and attempt.existing is not None:
            return self._replay(attempt.existing, digest, key)
        raise RuntimeError(f"unexpected place outcome {attempt.status}")
```

**Catch**

→ Client retries after a timeout with no idempotency record  
⇒ Duplicate create: two orders for one request  
→ Idempotency record + order in one transaction

→ Retention shorter than the client's retry horizon  
⇒ A very late retry creates a duplicate  
→ Keep the record at least as long as the client may retry

- Replay returns the order's current state
  - Store a response snapshot in the record if byte-exact replay matters
- Time To Live (TTL) deletion is lazy ⇒ condition `attribute_not_exists(k) OR expiresAt < :now` ([10streams-ttl](02dynamodb.10streams-ttl.md))

## Related

- [00index](02dynamodb.00index.md)
- [06conditions-updates](02dynamodb.06conditions-updates.md)
- [08batch-ops](02dynamodb.08batch-ops.md#5-batch-vs-transaction)
