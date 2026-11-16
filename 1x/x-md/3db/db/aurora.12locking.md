# 03db.01aurora.12locking Pessimistic, Atomic, And Optimistic Locking

> Three ways to protect read-check-write: lock the row, fold the check into one UPDATE, or detect conflicts with a version.

## Index

- [1. Pessimistic: SELECT FOR UPDATE](#1-pessimistic-select-for-update)
- [2. Atomic Conditional UPDATE](#2-atomic-conditional-update)
- [3. Optimistic: Version Column](#3-optimistic-version-column)
- [4. Choosing](#4-choosing)
- [Related](#related)

## 1. Pessimistic: SELECT FOR UPDATE

`SELECT … FOR UPDATE` takes a row lock until the transaction ends.

- Use for read-check-write on a row
  - Reserve stock, debit balance
- Holds the lock across app logic ⇒ keep the transaction short
- Lock rows in a stable order (by key) or risk deadlock `40P01`
- Bound waits with `SET LOCAL lock_timeout` ⇒ `55P03` instead of hanging

**Java**

```java
// infra/_03db_01aurora/AuroraJdbcRepository.java
@Override
public int lockStockForUpdate(String sku) {
    requireTransaction("lockStockForUpdate"); // outside a tx the lock would end at statement end
    writer.getJdbcTemplate().execute("SET LOCAL lock_timeout = '2s'"); // LOCAL: reverts at commit/rollback
    try {
        Integer onHand = writer.queryForObject(
                "SELECT on_hand FROM x_inventory WHERE sku = :sku FOR UPDATE", Map.of("sku", sku), Integer.class);
        return Objects.requireNonNull(onHand);
    } catch (EmptyResultDataAccessException e) {
        throw new BusinessRuleException("unknown sku " + sku);
    }
}

// Meant to follow lockStockForUpdate in the same transaction.
// Catch: alone it is a blind write; CHECK (on_hand >= 0) is the last guard.
@Override
public void decrementStock(String sku, int quantity) {
    requireTransaction("decrementStock");
    writer.update("UPDATE x_inventory SET on_hand = on_hand - :q, updated_at = now() WHERE sku = :sku",
            Map.of("q", quantity, "sku", sku));
}
```

**Python**

```python
# app/infra/_03db_01aurora.py
LOCK_TIMEOUT = "2s"  # SET LOCAL before FOR UPDATE: 55P03 instead of an endless wait

def lock_stock_for_update(self, sku: str) -> int:
    """Catch: must be inside `with conn.transaction()` (autocommit would release the lock at once)."""
    self._require_transaction("lock_stock_for_update")
    self._conn.execute(f"SET LOCAL lock_timeout = '{LOCK_TIMEOUT}'")  # constant, not user input
    row = self._conn.execute(
        "SELECT on_hand FROM x_inventory WHERE sku = %s FOR UPDATE", (sku,)
    ).fetchone()
    if row is None:
        raise BusinessRuleViolation(f"unknown sku {sku}")
    return int(row["on_hand"])
```

**Catch**

→ Long transaction holds `FOR UPDATE`  
⇒ Lock pile-up: `pg_locks` waits, `55P03`  
→ Short transactions, `lock_timeout`

→ Two transactions lock rows in opposite order  
⇒ Deadlock `40P01`  
→ Lock in key order; retry

## 2. Atomic Conditional UPDATE

Simpler when it fits: one statement `UPDATE … SET n = n - k WHERE n >= k`.

- Check and write in one statement
- No explicit lock, no transaction needed
- Safe under READ COMMITTED
  - After a concurrent update, the WHERE is re-evaluated on the newest row version
- Trick: replaces `SELECT FOR UPDATE` for simple counters

**Java**

```java
// infra/_03db_01aurora/AuroraJdbcRepository.java
@Override
public boolean decrementStockIfAvailable(String sku, int quantity) {
    return writer.update(
            "UPDATE x_inventory SET on_hand = on_hand - :q, updated_at = now() WHERE sku = :sku AND on_hand >= :q",
            Map.of("q", quantity, "sku", sku)) == 1; // 0 rows = not enough stock
}
```

**Python**

```python
# app/infra/_03db_01aurora.py
def decrement_stock_if_available(self, sku: str, quantity: int) -> bool:
    """Atomic conditional UPDATE: READ COMMITTED re-checks WHERE on the new row."""
    cur = self._conn.execute(
        "UPDATE x_inventory SET on_hand = on_hand - %s, updated_at = now() WHERE sku = %s AND on_hand >= %s",
        (quantity, sku, quantity),
    )
    return cur.rowcount == 1
```

**Catch**

- Only works when the check is expressible in WHERE
- The lost-update anti-pattern it replaces
  - `SELECT n`, then `UPDATE SET n = <app value>` under READ COMMITTED

## 3. Optimistic: Version Column

`UPDATE … WHERE id = ? AND version = ?` succeeds only if nobody changed the row since the read.

- 0 rows ⇒ someone else changed it ⇒ conflict (Hypertext Transfer Protocol (HTTP) 409); client re-reads
- No lock held between read and write
  - Good for human edit flows

**Java**

```java
// infra/_03db_01aurora/AuroraJdbcRepository.java
@Override
public Order updateStatusIfVersion(long id, int expectedVersion, OrderStatus newStatus) {
    String sql = "UPDATE x_order SET status = :status, version = version + 1, updated_at = now() "
            + "WHERE id = :id AND version = :expected RETURNING " + ORDER_COLUMNS;
    Map<String, Object> params = Map.of("status", newStatus.name(), "id", id, "expected", expectedVersion);
    Optional<Order> updated = writer.query(sql, params, this::mapOrder).stream().findFirst();
    if (updated.isPresent()) {
        return updated.get();
    }
    // 0 rows is ambiguous (deleted vs changed): a follow-up read tells 404 from 409
    Order current = findById(id).orElseThrow(() -> new OrderNotFoundException(id));
    throw new VersionConflictException("order " + id + " is at version " + current.version() + ", expected " + expectedVersion);
}
```

```java
// service/_03db_01aurora/AuroraOrderTx.java
// Audit row joins the same transaction (both or neither); conflict => API returns 409.
@Transactional(transactionManager = AuroraConfig.WRITER_TX)
public Order changeStatus(long id, int expectedVersion, OrderStatus status) {
    Order updated = orders.updateStatusIfVersion(id, expectedVersion, status);
    audit.recordJoined("STATUS_CHANGED", "order " + id + " -> " + status + " v" + updated.version());
    return updated;
}
```

**Python**

```python
# app/infra/_03db_01aurora.py
def update_status_if_version(self, order_id: int, expected_version: int, status: OrderStatus) -> Order:
    """UPDATE ... WHERE id AND version RETURNING; no row => re-read to tell 404 from 409."""
    row = self._conn.execute(
        "UPDATE x_order SET status = %s, version = version + 1, updated_at = now() "
        f"WHERE id = %s AND version = %s RETURNING {ORDER_COLUMNS}",
        (status.value, order_id, expected_version),
    ).fetchone()
    if row:
        return _order(row)
    current = self.find_by_id(order_id)
    if current is None:
        raise OrderNotFound(f"order {order_id} not found")
    raise VersionConflict(f"order {order_id} is at version {current.version}, expected {expected_version}")
```

**Catch**

- A retry after a lost commit ack reports a false conflict
  - Handled in [10retries-idempotency](01aurora.10retries-idempotency.md) §5
- Trick: the version doubles as a read-your-writes token ([02endpoints-replica-lag](01aurora.02endpoints-replica-lag.md))

## 4. Choosing

| Option | Holds lock | Strength | Weakness | Choose when |
|---|---|---|---|---|
| `FOR UPDATE` | Until commit | Serializes a hot row | Deadlocks, pile-ups | High contention, short critical section |
| Conditional UPDATE | One statement | One round trip, no read | Check must fit WHERE | Counters, stock, balances |
| Version column | None | No blocking during think time | Conflicts under contention | Low contention, human edits |

Pick: conditional UPDATE, unless the check needs app logic (FOR UPDATE) or a human edits between read and write (version).

## Related

- [00index](01aurora.00index.md)
- [08isolation-levels](01aurora.08isolation-levels.md)
- [09transactions-propagation](01aurora.09transactions-propagation.md): `placeOrder` uses FOR UPDATE
- [99interview](01aurora.99interview.md): Q8
