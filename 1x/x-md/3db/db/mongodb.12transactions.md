# 03db.04mongodb.12transactions Transactions

> Use multi-document transactions only when one document cannot hold the invariant, and retry by error label.

## Index

- [1. When You Need One](#1-when-you-need-one)
- [2. Retry Labels](#2-retry-labels)
- [3. Write Skew](#3-write-skew)
- [Related](#related)

## 1. When You Need One

Single-document writes are already atomic; good schemas need few transactions.

- Needed: order insert + stock decrement across two collections
- Cost: snapshot reads, locks held until commit, 60 s default lifetime, oplog entry up to 16 megabytes (MB)
- Requires a replica set or sharded cluster

```java
// infra/_03db_04mongodb/MongoTransactions.java
// Order + inventory decrement, both or neither, via the callback API. withTransaction retries the body on
// TransientTransactionError and the commit on UnknownTransactionCommitResult, up to ~120 s total.
// A non-Mongo exception (InsufficientStockException) aborts with NO retry.
public Order placeOrder(NewOrder o) {
    try (ClientSession session = client.startSession()) {
        return session.withTransaction(() -> placeOrderBody(session, o), TX_OPTIONS);
    }
}
```

```python
# app/infra/_03db_04mongodb.py
def place_order(self, o: NewOrder) -> Order:
    """Callback API: retries the body on TransientTransactionError and the commit on UnknownCommitResult."""
    with get_client().start_session() as s:
        return s.with_transaction(
            lambda session: self._place_order_body(session, o),
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
            read_preference=ReadPreference.PRIMARY,
            max_commit_time_ms=5000,
        )
```

## 2. Retry Labels

Two labels decide what to retry.

- `TransientTransactionError` ⇒ rerun the whole transaction body
- `UnknownTransactionCommitResult` ⇒ retry only the commit, since it may already have applied
- `withTransaction` does both automatically; the hand-rolled version shows the mechanics

```java
// infra/_03db_04mongodb/MongoTransactions.java
// The same transaction with the retry loop written out, to show what withTransaction does:
// - TransientTransactionError -> abort, back off, rerun the WHOLE body (new snapshot).
// - UnknownTransactionCommitResult -> retry ONLY commitTransaction (idempotent per txnNumber).
// - Attempt cap: a permanently conflicting transaction (hot counter) must surface, not spin for 120 s.
public Order placeOrderHandRolled(NewOrder o) {
    Retry backoff = Retry.defaults();
    try (ClientSession session = client.startSession()) {
        for (int attempt = 0; ; attempt++) {
            session.startTransaction(TX_OPTIONS);
            try {
                Order placed = placeOrderBody(session, o);
                commitWithRetry(session);
                return placed;
            } catch (MongoException e) {
                if (session.hasActiveTransaction()) {
                    session.abortTransaction();
                }
                boolean transientError = e.hasErrorLabel(MongoException.TRANSIENT_TRANSACTION_ERROR_LABEL);
                if (!transientError || attempt + 1 >= MAX_TX_ATTEMPTS) {
                    throw e;
                }
                Retry.sleep(backoff.backoff(attempt));
            } catch (RuntimeException e) {
                if (session.hasActiveTransaction()) {
                    session.abortTransaction(); // business error: abort, never retry
                }
                throw e;
            }
        }
    }
}
```

```python
# app/infra/_03db_04mongodb.py
def place_order_hand_rolled(self, o: NewOrder) -> Order:
    """What with_transaction does, written out, plus an attempt cap and backoff."""
    with get_client().start_session() as s:
        for attempt in range(MAX_TX_ATTEMPTS):
            s.start_transaction(
                read_concern=ReadConcern("snapshot"), write_concern=WriteConcern("majority"), max_commit_time_ms=5000
            )
            try:
                placed = self._place_order_body(s, o)
                _commit_with_retry(s)
                return placed
            except PyMongoError as e:
                if s.in_transaction:
                    s.abort_transaction()
                if not e.has_error_label("TransientTransactionError") or attempt + 1 >= MAX_TX_ATTEMPTS:
                    raise
                time.sleep(min(2.0, 0.05 * 2**attempt))  # back off: retrying harder adds contention
            except Exception:
                if s.in_transaction:
                    s.abort_transaction()  # business error: abort, never retry
                raise
    raise RuntimeError("unreachable")
```

```python
# app/infra/_03db_04mongodb.py
def _commit_with_retry(s: ClientSession) -> None:
    for attempt in range(MAX_TX_ATTEMPTS):
        try:
            s.commit_transaction()
            return
        except PyMongoError as e:
            if not e.has_error_label("UnknownTransactionCommitResult") or attempt + 1 >= MAX_TX_ATTEMPTS:
                raise  # TransientTransactionError here propagates to the outer loop
```

## 3. Write Skew

Snapshot isolation lets two transactions each read "2 on call" and both go off call.

- Fix: write to a shared document so the transactions conflict (WriteConflict ⇒ one retries)
- Same idea for reservations: conditional update on the stock row, not a read-then-write

```java
// infra/_03db_04mongodb/MongoTransactions.java
// Write skew, fixed WITHOUT a transaction: the invariant "at least one engineer on call" lives in ONE
// document, and the predicate "oncall.1 exists" (>= 2 on call) is checked atomically with the $pull.
// Two concurrent calls cannot both succeed when only two are on call. Snapshot isolation would allow it.
public boolean goOffCall(String rotaId, String engineer) {
    return rotas.updateOne(
            and(eq("_id", rotaId), eq("oncall", engineer), exists("oncall.1", true)),
            Updates.pull("oncall", engineer))
            .getModifiedCount() == 1;
}
```

```python
# app/infra/_03db_04mongodb.py
def go_off_call(self, rota_id: str, engineer: str) -> bool:
    """Write-skew fix without a transaction: the invariant lives in ONE document ("oncall.1" exists = >= 2)."""
    return (
        self.db[ROTAS]
        .update_one(
            {"_id": rota_id, "oncall": engineer, "oncall.1": {"$exists": True}},
            {"$pull": {"oncall": engineer}},
        )
        .modified_count
        == 1
    )
```

```java
// infra/_03db_04mongodb/MongoTransactions.java
// Saga step instead of a cross-shard transaction: reserve stock with a single-document conditional
// update (atomic, no 2PC), create the order separately, and release the reservation if that fails.
// A reaper job releases reservations whose holder crashed (TTL on reservedUntil).
public boolean reserveStock(String sku, int qty, String orderId, Instant reservedUntil) {
    return inventory.updateOne(
            and(eq("_id", sku), gte("qty", qty)),
            Updates.combine(
                    Updates.inc("qty", -qty),
                    Updates.push("reservations",
                            new Document("orderId", orderId).append("qty", qty).append("until", reservedUntil))))
            .getModifiedCount() == 1;
}
```

```python
# app/infra/_03db_04mongodb.py
def reserve_stock(self, sku: str, qty: int, order_id: str, reserved_until: datetime) -> bool:
    """Saga step instead of a cross-shard transaction: single-document conditional reserve."""
    return (
        self.db[INVENTORY]
        .update_one(
            {"_id": sku, "qty": {"$gte": qty}},
            {"$inc": {"qty": -qty}, "$push": {"reservations": {"orderId": order_id, "qty": qty, "until": reserved_until}}},
        )
        .modified_count
        == 1
    )
```

## Related

- [Index](04mongodb.00index.md)
- [Read and write concern](04mongodb.11read-write-concern.md)
- [Bulk writes and errors](04mongodb.05bulk-write.md)
