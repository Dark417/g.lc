# 03db.01aurora.10retries-idempotency Retries And Idempotency

> Retry the whole transaction from outside it, only on transient SQLSTATEs, and only for writes an idempotency key makes safe.

## Index

- [1. Retry Rule](#1-retry-rule)
- [2. Retryable SQLSTATEs](#2-retryable-sqlstates)
  - [2.1 Classification In Code](#21-classification-in-code)
- [3. Retry At The Transaction Boundary](#3-retry-at-the-transaction-boundary)
- [4. Idempotent Create](#4-idempotent-create)
- [5. Retry-Safe Optimistic Update](#5-retry-safe-optimistic-update)
- [6. What Is Not Retried](#6-what-is-not-retried)
- [Related](#related)

## 1. Retry Rule

→ Retry wraps the **whole** transaction, from outside it  
⇒ Retrying a statement inside an aborted transaction fails with `25P02`  
→ Each attempt is a fresh transaction on a fresh or validated connection  
→ Writes carry an idempotency key (unique column + `ON CONFLICT DO NOTHING`)  
⇒ A commit whose ack was lost (connection dropped during COMMIT) is replayed safely

- 🗣 "Retries belong outside the transaction, and only work when the write is idempotent."

## 2. Retryable SQLSTATEs

Transient = a fresh transaction may succeed.

| SQLSTATE | Meaning | Why retry helps |
|---|---|---|
| `40001` | Serialization failure | database (DB) chose this transaction as the victim |
| `40P01` | Deadlock | Same |
| `08xxx`, `57P01`–`57P03` | Connection lost, shutdown / starting up (failover) | New connection reaches the new writer; commit outcome may be unknown ⇒ idempotency key |
| `25006` | Read-only transaction on the writer pool | Stale Domain Name System (DNS) after failover; connection evicted, retry gets a new one |
| `55P03` | Lock timeout | Contention may have cleared |

- Not retried
  - Constraint violations (`23xxx`)
  - Syntax / bugs (`42xxx`)
  - Pool-wait timeout without a SQLSTATE: load shedding, don't amplify
  - Python also: `QueryCanceled` (`statement_timeout`)

### 2.1 Classification In Code

**Java**

```java
// infra/_03db_01aurora/AuroraErrors.java
// Spring wraps SQLException in DataAccessException; the SQLSTATE is found by walking the cause chain.
public static boolean isRetryable(Throwable t) {
    String state = sqlState(t);
    if (state == null) {
        return false; // e.g. pool saturated: shed load, don't amplify
    }
    return state.equals(SERIALIZATION_FAILURE)   // 40001
            || state.equals(DEADLOCK_DETECTED)   // 40P01
            || state.startsWith("08")
            || SHUTDOWN.contains(state)          // 57P01, 57P02, 57P03
            || state.equals(READ_ONLY_TRANSACTION) // 25006
            || state.equals(LOCK_NOT_AVAILABLE);   // 55P03
}
```

**Python**

```python
# app/infra/_03db_01aurora.py
_RETRYABLE_STATES = {"40001", "40P01", "25006", "55P03", "57P01", "57P02", "57P03"}

def is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, PoolTimeout):
        return False  # saturated: shed load
    if isinstance(exc, (errors.SerializationFailure, errors.DeadlockDetected)):
        return True
    if isinstance(exc, psycopg.Error):
        state = exc.sqlstate
        if state is None:
            return isinstance(exc, psycopg.OperationalError)  # client-side connection loss
        return state in _RETRYABLE_STATES or state.startswith("08")
    return False
```

## 3. Retry At The Transaction Boundary

The service sits outside the transactions so it can retry them.

- Budget meant to span an Aurora failover (Amazon Web Services (AWS): typically < 60 s, often < 30 s)
  - 8 attempts, 200 milliseconds (ms) base, 8 s cap, full jitter
- Each attempt can also wait `connectionTimeout` (3 s) for a connection
  - Keep the Hypertext Transfer Protocol (HTTP) deadline above the retry budget

**Java**

```java
// service/_03db_01aurora/AuroraOrderService.java
private final Retry retry = new Retry(8, Duration.ofMillis(200), Duration.ofSeconds(8));

// Each call of `attempt` = a fresh transaction through the AuroraOrderTx proxy.
public <T> T withRetry(String operation, Supplier<T> attempt) {
    if (TransactionSynchronizationManager.isActualTransactionActive()) {
        // retrying inside an aborted transaction only yields 25P02
        throw new IllegalStateException(operation + ": retry must wrap the transaction, not run inside one");
    }
    return retry.call(attempt, AuroraErrors::isRetryable);
}

public Order placeOrder(NewOrder cmd) {
    requireKey(cmd); // key must be unique per logical request (client UUID), not per user/session
    return withRetry("placeOrder", () -> tx.placeOrder(cmd));
}
```

**Python**

```python
# app/service/_03db_01aurora.py
RETRY_ATTEMPTS = 8
RETRY_BASE_S = 0.2
RETRY_CAP_S = 8.0

def _with_retry(self, fn: Callable[[], T]) -> T:
    """Each call of fn opens a fresh transaction. Catch: never call it from inside an open transaction block."""
    return call_with_retry(fn, is_retryable, max_attempts=RETRY_ATTEMPTS, base=RETRY_BASE_S, cap=RETRY_CAP_S)

def place_order(self, cmd: NewOrder) -> Order:
    _require_key(cmd)
    return self._with_retry(lambda: self._place_once(cmd))
```

**Catch**

- Retry budget must span the failover window, but stay under the request deadline
- Creates without a key (`createOrderOnce` / `create_order_once`) are **not** retried
  - A lost commit ack leaves the client unsure whether the order exists

## 4. Idempotent Create

Trick: `INSERT … ON CONFLICT DO NOTHING RETURNING` + fallback SELECT = idempotent create in one round trip.

**Java**

```java
// infra/_03db_01aurora/AuroraJdbcRepository.java
// Empty result = the key already exists; the caller re-reads by key.
@Override
public Optional<Order> insertIdempotent(NewOrder o) {
    Objects.requireNonNull(o.idempotencyKey(), "idempotencyKey is required for an idempotent insert");
    String sql = "INSERT INTO x_order (customer_id, sku, quantity, amount_cents, idempotency_key, attrs) "
            + "VALUES (:customerId, :sku, :quantity, :amountCents, :idempotencyKey, CAST(:attrs AS jsonb)) "
            + "ON CONFLICT (idempotency_key) DO NOTHING "
            + "RETURNING " + ORDER_COLUMNS;
    return writer.query(sql, orderParams(o), this::mapOrder).stream().findFirst();
}
```

```java
// service/_03db_01aurora/AuroraOrderTx.java
// Same key with a different body is a client bug, not a replay: reject.
private static Order checkSameRequest(Order existing, NewOrder cmd) {
    boolean same = existing.customerId().equals(cmd.customerId())
            && existing.sku().equals(cmd.sku())
            && existing.quantity() == cmd.quantity()
            && existing.amountCents() == cmd.amountCents();
    if (!same) {
        throw new BusinessRuleException("idempotency key " + cmd.idempotencyKey() + " reused with a different request");
    }
    return existing;
}
```

**Python**

```python
# app/infra/_03db_01aurora.py
def insert_idempotent(self, order: NewOrder) -> Order | None:
    """ON CONFLICT (idempotency_key) DO NOTHING RETURNING; None = key exists (re-read by key)."""
    if not order.idempotency_key:
        raise ValueError("idempotency_key is required for an idempotent insert")
    row = self._conn.execute(
        "INSERT INTO x_order (customer_id, sku, quantity, amount_cents, idempotency_key, attrs) "
        "VALUES (%(customer_id)s, %(sku)s, %(quantity)s, %(amount_cents)s, %(key)s, %(attrs)s) "
        f"ON CONFLICT (idempotency_key) DO NOTHING RETURNING {ORDER_COLUMNS}",
        _order_params(order),
    ).fetchone()
    return _order(row) if row else None
```

```sql
-- resources/_03db_01aurora/schema.sql
idempotency_key TEXT UNIQUE,  -- NULLs allowed (NULLS DISTINCT), set => one row per request
```

**Catch**

- On conflict, RETURNING yields nothing ⇒ caller re-reads by key
- Under REPEATABLE READ / SERIALIZABLE a conflicting row the snapshot can't see raises `40001`
  - Retry; the next attempt's re-read finds it
- In READ COMMITTED the re-read takes a new snapshot, so it sees a row committed a moment ago

## 5. Retry-Safe Optimistic Update

- A retry after a lost commit ack sees `version + 1` ⇒ a false conflict
- So on attempts > 1, a conflict whose current state equals the requested state counts as success

**Java**

```java
// service/_03db_01aurora/AuroraOrderService.java
public Order changeStatus(long id, int expectedVersion, OrderStatus status) {
    AtomicInteger attempts = new AtomicInteger();
    return withRetry("changeStatus", () -> {
        int n = attempts.incrementAndGet();
        try {
            return tx.changeStatus(id, expectedVersion, status);
        } catch (VersionConflictException e) {
            if (n > 1) { // our own earlier attempt may have committed
                Order current = orders.findById(id).orElseThrow(() -> new OrderNotFoundException(id));
                if (current.status() == status && current.version() == expectedVersion + 1) {
                    return current;
                }
            }
            throw e;
        }
    });
}
```

**Python**

```python
# app/service/_03db_01aurora.py  (inside change_status)
def attempt() -> Order:
    nonlocal attempts
    attempts += 1
    try:
        with self._repo.writer_tx() as store:
            updated = store.update_status_if_version(order_id, expected_version, status)
            store.append_audit("STATUS_CHANGED", f"order {order_id} -> {status} v{updated.version}")
            return updated
    except VersionConflict:
        if attempts > 1:
            with self._repo.writer_tx() as store:
                current = store.find_by_id(order_id)
            if current and current.status is status and current.version == expected_version + 1:
                return current
        raise
```

**Catch**

- A concurrent writer making the identical change is indistinguishable from our own replay
  - Same outcome, so accepted

## 6. What Is Not Retried

Each operation is retried only when a replay is harmless.

| Operation | Retried | Why |
|---|---|---|
| `placeOrder` / `restock` / `delete` | Yes | Key, "set to N" upsert, idempotent delete |
| `enqueueJob` | No | No dedup key ⇒ lost ack + retry enqueues twice |
| `claimJobs` / `completeJob` | Yes | Lease expires; DONE keeps `locked_by` |
| `failJob` | No | Lost ack ⇒ lease expires, reaper requeues (same end state) |
| `createOrderOnce` | No | No key |

- Details: [13skip-locked-queue](01aurora.13skip-locked-queue.md), [11crud-batch-upsert](01aurora.11crud-batch-upsert.md)

**Defeaters to volunteer**

→ The key is scoped per user instead of per request  
⇒ A legitimate second order is rejected  
→ Use a client-generated Universally Unique Identifier (UUID) per logical request

→ A retry runs inside the failed transaction  
⇒ `25P02 current transaction is aborted`, never succeeds  
→ Retry the whole transaction from outside

## Related

- [00index](01aurora.00index.md)
- [03failover-dns](01aurora.03failover-dns.md)
- [09transactions-propagation](01aurora.09transactions-propagation.md)
- [99interview](01aurora.99interview.md): Q3, Q9
