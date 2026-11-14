# 03db.01aurora.08isolation-levels Isolation Levels

> Pick isolation on purpose: READ COMMITTED default, REPEATABLE READ for snapshots, SERIALIZABLE for cross-row invariants.

## Index

- [1. The Three Levels](#1-the-three-levels)
- [2. READ COMMITTED Detail](#2-read-committed-detail)
- [3. SERIALIZABLE = SSI](#3-serializable--ssi)
  - [3.1 Write Skew Guard In Code](#31-write-skew-guard-in-code)
- [4. Readers And REPEATABLE READ](#4-readers-and-repeatable-read)
  - [4.1 Snapshot Report In Code](#41-snapshot-report-in-code)
- [Related](#related)

## 1. The Three Levels

PostgreSQL implements three; READ UNCOMMITTED behaves as READ COMMITTED.

| Level | Snapshot | Prevents | Still allows | Error to retry |
|---|---|---|---|---|
| READ COMMITTED (default) | New snapshot per statement | Dirty reads | Non-repeatable reads, lost update in read-modify-write | none (blocked UPDATE re-checks the new row) |
| REPEATABLE READ | One snapshot per transaction (snapshot isolation) | Non-repeatable reads, phantoms (stronger than American National Standards Institute (ANSI)) | Write skew | `40001` when updating a row changed after the snapshot |
| SERIALIZABLE | Snapshot + Serializable Snapshot Isolation (SSI) conflict tracking | All anomalies incl. write skew | False-positive aborts | `40001` on a dangerous read-write dependency cycle |

Pick: READ COMMITTED, unless several queries must agree (REPEATABLE READ) or an invariant spans rows (SERIALIZABLE).

## 2. READ COMMITTED Detail

- A blocked UPDATE waits for the other writer
- Then it re-evaluates its WHERE on the new row version
- Safe: `UPDATE stock SET n = n - 1 WHERE n > 0`
- Loses updates: `SELECT n`, then `UPDATE SET n = <app value>`
- Code for both sides: [12locking](01aurora.12locking.md)

## 3. SERIALIZABLE = SSI

Serializable Snapshot Isolation (Ports & Grittner, Very Large Data Bases (VLDB) 2012).

- Reads take SIREAD predicate locks (no blocking)
- Two concurrent transactions with rw-dependencies both ways ⇒ one aborts with `40001`
- Index-backed predicates lock index ranges
- A sequential scan locks the whole table
  - Result: more false positives
- The application **must** retry the whole transaction
  - See [10retries-idempotency](01aurora.10retries-idempotency.md)
- Example write skew the code shows
  - Two orders for one customer
  - Each checks "open total + mine ≤ limit"
  - REPEATABLE READ ⇒ both see the old total, both insert ⇒ limit exceeded
  - SERIALIZABLE ⇒ one gets `40001`; the retry sees the other order and rejects

### 3.1 Write Skew Guard In Code

**Java**

```java
// service/_03db_01aurora/AuroraOrderTx.java
// Under RC or RR two concurrent calls both read the old total and both insert (write skew);
// SERIALIZABLE (SSI) aborts one with 40001. Correctness depends on the caller retrying 40001.
@Transactional(transactionManager = AuroraConfig.WRITER_TX, isolation = Isolation.SERIALIZABLE)
public Order placeOrderWithinCreditLimit(NewOrder cmd, long creditLimitCents) {
    Optional<Order> existing = orders.findByIdempotencyKey(cmd.idempotencyKey());
    if (existing.isPresent()) {
        return checkSameRequest(existing.get(), cmd); // replay after a lost commit ack
    }
    long open = orders.sumOpenAmountCents(cmd.customerId());
    if (open + cmd.amountCents() > creditLimitCents) {
        throw new BusinessRuleException("credit limit exceeded: ...");
    }
    // A concurrent insert of the same key our snapshot cannot see raises 40001 here, not a silent no-op.
    return orders.insertIdempotent(cmd).orElseGet(() -> replayOf(cmd));
}
```

```java
// infra/_03db_01aurora/AuroraJdbcRepository.java
// Under SERIALIZABLE this read takes SIREAD locks on the index range;
// with no index on customer_id it would lock the whole table (many false-positive 40001s).
@Override
public long sumOpenAmountCents(String customerId) {
    Long sum = writer.queryForObject(
            "SELECT COALESCE(SUM(amount_cents), 0) FROM x_order WHERE customer_id = :c AND status IN ('NEW', 'PAID')",
            Map.of("c", customerId), Long.class);
    return sum == null ? 0L : sum;
}
```

```java
// service/_03db_01aurora/AuroraOrderService.java
// 40001 is the expected outcome under contention; retry makes it correct.
public Order placeOrderWithinCreditLimit(NewOrder cmd) {
    requireKey(cmd);
    return withRetry("placeOrderWithinCreditLimit", () -> tx.placeOrderWithinCreditLimit(cmd, CREDIT_LIMIT_CENTS));
}
```

**Python**

```python
# app/service/_03db_01aurora.py
def _place_within_limit_once(self, cmd: NewOrder) -> Order:
    """SERIALIZABLE (SSI) detects the read-write cycle and aborts one with SerializationFailure (40001)."""
    with self._repo.writer_tx(Isolation.SERIALIZABLE) as store:
        existing = store.find_by_idempotency_key(cmd.idempotency_key)
        if existing is not None:
            return _check_same_request(existing, cmd)
        open_cents = store.sum_open_amount_cents(cmd.customer_id)
        if open_cents + cmd.amount_cents > CREDIT_LIMIT_CENTS:
            raise BusinessRuleViolation(f"credit limit exceeded: ...")
        created = store.insert_idempotent(cmd)
        return created if created is not None else _replay_of(store, cmd)
```

```python
# app/infra/_03db_01aurora.py
@contextmanager
def writer_tx(self, isolation: Isolation = Isolation.READ_COMMITTED) -> Iterator[PgOrderStore]:
    """BEGIN on enter, COMMIT on clean exit, ROLLBACK on exception."""
    with (
        self._connection(self._pools.writer(), evict_on_read_only=True) as conn,
        conn.transaction(),
    ):
        if isolation is not Isolation.READ_COMMITTED:
            # first statement: scopes the level to this transaction; never leaks to the next pool user
            conn.execute(f"SET TRANSACTION ISOLATION LEVEL {isolation.value}")  # enum constant
        yield PgOrderStore(conn)
```

**Catch**

- Correctness now depends on the retry
- The `(customer_id, created_at, id)` index narrows SIREAD locks to one customer's range
- When SERIALIZABLE hurts more than it helps: see [99interview](01aurora.99interview.md) Q11
  - Lock a parent row, materialize the invariant, or use a constraint

## 4. Readers And REPEATABLE READ

- Readers are hot standbys: SERIALIZABLE is not available there
- Use REPEATABLE READ for consistent read-only reports
- Trick: `SERIALIZABLE READ ONLY DEFERRABLE` runs a consistent report with no abort risk
  - Writer only

### 4.1 Snapshot Report In Code

Two queries, one snapshot: count/sum and the latest rows agree while writes continue.

**Java**

```java
// service/_03db_01aurora/AuroraOrderTx.java
// Catch: the snapshot itself may lag the writer (replica).
@Transactional(transactionManager = AuroraConfig.READER_TX, readOnly = true, isolation = Isolation.REPEATABLE_READ)
public CustomerSummary customerSummary(String customerId) {
    long[] countAndSum = orders.countAndSumOnReader(customerId);
    List<Order> latest = orders.latestOnReader(customerId, 5);
    return new CustomerSummary(customerId, countAndSum[0], countAndSum[1], latest);
}
```

```java
// config/_03db_01aurora/AuroraConfig.java
// enforceReadOnly sends SET TRANSACTION READ ONLY. Catch: SERIALIZABLE not available on replicas.
@Bean(name = READER_TX)
public JdbcTransactionManager auroraReaderTxManager(@Qualifier(READER_DS) DataSource reader) {
    JdbcTransactionManager tm = new JdbcTransactionManager(reader);
    tm.setEnforceReadOnly(true);
    return tm;
}
```

**Python**

```python
# app/infra/_03db_01aurora.py
@contextmanager
def reader_tx(self, isolation: Isolation = Isolation.REPEATABLE_READ) -> Iterator[PgOrderStore]:
    """Catch: may lag the writer; SERIALIZABLE is downgraded to REPEATABLE READ on replicas."""
    level = Isolation.REPEATABLE_READ if isolation is Isolation.SERIALIZABLE else isolation
    with (
        self._connection(self._pools.reader(), evict_on_read_only=False) as conn,
        conn.transaction(),
    ):
        conn.execute(f"SET TRANSACTION ISOLATION LEVEL {level.value}, READ ONLY")  # enum constant
        yield PgOrderStore(conn)
```

```python
# app/service/_03db_01aurora.py
def customer_summary(self, customer_id: str) -> CustomerSummary:
    def attempt() -> CustomerSummary:
        with self._repo.reader_tx(Isolation.REPEATABLE_READ) as replica:
            count, total = replica.count_and_sum(customer_id)
            latest = replica.latest(customer_id, 5)
        return CustomerSummary(customer_id=customer_id, order_count=count, total_cents=total, latest=latest)

    return self._with_retry(attempt)
```

**Catch**

- Outside a transaction each query sees a different moment
- REPEATABLE READ is the strongest level on readers

## Related

- [00index](01aurora.00index.md)
- [07mvcc-vacuum](01aurora.07mvcc-vacuum.md)
- [12locking](01aurora.12locking.md)
- [99interview](01aurora.99interview.md): Q5, Q11
