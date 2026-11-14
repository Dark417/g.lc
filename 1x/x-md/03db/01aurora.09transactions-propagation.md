# 03db.01aurora.09transactions-propagation Transactions In Application Code

> One public method or one `with` block = one transaction; propagation decides which rows survive a rollback.

## Index

- [1. Spring @Transactional](#1-spring-transactional)
  - [1.1 Rules](#11-rules)
  - [1.2 REQUIRED vs REQUIRES_NEW](#12-required-vs-requires_new)
  - [1.3 Named Transaction Managers](#13-named-transaction-managers)
- [2. psycopg 3](#2-psycopg-3)
- [3. Order + Stock + Audit In Code](#3-order--stock--audit-in-code)
- [Related](#related)

## 1. Spring @Transactional

Spring wraps the bean in a proxy that opens and commits the transaction around the call.

### 1.1 Rules

- Proxy-based
  - A call from inside the same bean skips the proxy (**self-invocation**)
  - Result: no transaction
  - So `AuroraAuditService` is a separate bean on purpose
- Rollback on unchecked exceptions only, by default

### 1.2 REQUIRED vs REQUIRES_NEW

| Propagation | Connection | Commits | Use for |
|---|---|---|---|
| `REQUIRED` (default) | Joins the caller's | With the caller | "This happened" records that must not exist if the change didn't |
| `REQUIRES_NEW` | Suspends the caller; a **second connection** | Independently, right away | Attempt logs that must survive the caller's rollback |

- `REQUIRED` catch
  - Inner failure marks the whole transaction rollback-only
  - Even if the caller catches it ⇒ `UnexpectedRollbackException` at commit
- `REQUIRES_NEW` catch
  - Two connections per request
  - ⚠️ Pool starvation if `pool size ≤ concurrent callers`
    - Every thread holds one connection and waits for a second

**Java**

```java
// service/_03db_01aurora/AuroraAuditService.java
// A separate bean: calls from AuroraOrderTx go through the proxy; a self-call would not.
@Transactional(transactionManager = AuroraConfig.WRITER_TX, propagation = Propagation.REQUIRED)
public void recordJoined(String action, String detail) {
    audit.append(action, detail); // commits or rolls back WITH the business change
}

@Transactional(transactionManager = AuroraConfig.WRITER_TX, propagation = Propagation.REQUIRES_NEW)
public void recordIndependent(String action, String detail) {
    audit.append(action, detail); // commits now on a SECOND connection
}
```

**Python**

```python
# app/infra/_03db_01aurora.py
def independent_tx(self) -> AbstractContextManager[PgOrderStore]:
    """REQUIRES_NEW analogue: a separate writer connection and transaction that commits on its own.

    Catch: opened while another writer_tx is open, it holds a second pooled connection (starvation risk).
    """
    return self.writer_tx(Isolation.READ_COMMITTED)
```

**Catch**

- The Python service opens the independent transaction **before** the business one
  - So a request never holds two pooled connections at once

### 1.3 Named Transaction Managers

- Several data sources ⇒ name the manager
  - `@Transactional(transactionManager = "auroraWriterTxManager")`
- Prevents a silent no-op `@Transactional` when several managers exist

**Java**

```java
// config/_03db_01aurora/AuroraConfig.java
// JdbcTransactionManager = DataSourceTransactionManager that also translates commit/rollback SQLExceptions.
// Catch: the JdbcTemplate joins the transaction only because it wraps the SAME DataSource object.
@Bean(name = WRITER_TX)
public JdbcTransactionManager auroraWriterTxManager(@Qualifier(WRITER_DS) DataSource writer) {
    return new JdbcTransactionManager(writer);
}

@Bean(name = WRITER_JDBC)
public NamedParameterJdbcTemplate auroraWriterJdbc(@Qualifier(WRITER_DS) DataSource writer) {
    return new NamedParameterJdbcTemplate(writer);
}
```

## 2. psycopg 3

- Pool connections in autocommit mode
- Transactions are explicit: `with conn.transaction():`
- Nested `conn.transaction()` = SAVEPOINT
- `SET TRANSACTION ISOLATION LEVEL …` as the first statement
  - So the level never leaks to the next pool user
  - Code: `writer_tx` in [08isolation-levels](01aurora.08isolation-levels.md)

## 3. Order + Stock + Audit In Code

One READ COMMITTED transaction: idempotent insert, `FOR UPDATE` on stock, an independent attempt row, a joined placed row.

→ `ORDER_ATTEMPT` commits on its own connection  
→ Insert order (idempotent)  
→ Lock stock row, check, decrement  
→ `ORDER_PLACED` joins the business transaction  
⇒ Insufficient stock rolls back the order and `ORDER_PLACED`; `ORDER_ATTEMPT` stays

**Java**

```java
// service/_03db_01aurora/AuroraOrderTx.java
@Transactional(transactionManager = AuroraConfig.WRITER_TX)
public Order placeOrder(NewOrder cmd) {
    audit.recordIndependent("ORDER_ATTEMPT", cmd.idempotencyKey()); // commits now on a second connection
    Optional<Order> created = orders.insertIdempotent(cmd);
    if (created.isEmpty()) {
        // Replay: an earlier attempt committed (its ack may have been lost in a failover). Do not reserve twice.
        return replayOf(cmd);
    }
    int onHand = inventory.lockStockForUpdate(cmd.sku()); // row lock until commit; concurrent buyers queue here
    if (onHand < cmd.quantity()) {
        throw new BusinessRuleException("insufficient stock for " + cmd.sku() + ": ...");
    }
    inventory.decrementStock(cmd.sku(), cmd.quantity());
    audit.recordJoined("ORDER_PLACED", "order " + created.get().id());
    return created.get();
}
```

**Python**

```python
# app/service/_03db_01aurora.py
def _place_once(self, cmd: NewOrder) -> Order:
    with self._repo.independent_tx() as audit:       # REQUIRES_NEW analogue, opened BEFORE the business tx
        audit.append_audit("ORDER_ATTEMPT", cmd.idempotency_key)
    with self._repo.writer_tx() as store:
        created = store.insert_idempotent(cmd)
        if created is None:
            return _replay_of(store, cmd)  # an earlier attempt committed; do not reserve stock twice
        on_hand = store.lock_stock_for_update(cmd.sku)  # row lock until commit
        if on_hand < cmd.quantity:
            # Raising inside the block rolls back the order insert; ORDER_ATTEMPT is already committed.
            raise BusinessRuleViolation(f"insufficient stock for {cmd.sku}: {on_hand} < {cmd.quantity}")
        store.decrement_stock(cmd.sku, cmd.quantity)
        store.append_audit("ORDER_PLACED", f"order {created.id}")  # REQUIRED analogue: same store
        return created
```

**Catch**

- Never retried from inside: after an error PostgreSQL rejects every statement until rollback (`25P02`)
- The service retries the whole method; see [10retries-idempotency](01aurora.10retries-idempotency.md)

## Related

- [00index](01aurora.00index.md)
- [06pools-rds-proxy](01aurora.06pools-rds-proxy.md): pool sizing vs nested connections
- [12locking](01aurora.12locking.md)
