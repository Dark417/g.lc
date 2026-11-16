# 03db.01aurora.07mvcc-vacuum Multi-Version Concurrency Control (MVCC) And Vacuum

> PostgreSQL keeps old row versions so readers never block writers; VACUUM must clean them, and long transactions stop it.

## Index

- [1. Multi-Version Concurrency Control (MVCC)](#1-multi-version-concurrency-control-mvcc)
- [2. Cost: Bloat And Vacuum](#2-cost-bloat-and-vacuum)
  - [2.1 Dead Tuples In Code](#21-dead-tuples-in-code)
- [3. Transaction Identifier (ID) Wraparound](#3-transaction-identifier-id-wraparound)
- [4. Heap-Only Tuple (HOT) Updates](#4-heap-only-tuple-hot-updates)
- [Related](#related)

## 1. Multi-Version Concurrency Control (MVCC)

Every row version carries the transactions that created and deleted it.

- `xmin`: creator transaction
- `xmax`: deleter transaction
- UPDATE = write a new version, mark the old one dead
- A snapshot decides which versions a statement sees
- Result: readers never block writers; writers never block readers

## 2. Cost: Bloat And Vacuum

Dead versions accumulate until something reclaims them.

- VACUUM marks dead space reusable
- Autovacuum runs it in the background
- VACUUM can only remove versions older than the oldest running snapshot (**xmin horizon**)
  - Result: a transaction left open for hours blocks cleanup for the whole cluster
- Terraform sets `idle_in_transaction_session_timeout = 60 s`
  - Kills forgotten transactions
  - [`modules/03db_01aurora/main.tf`](../../terraform/modules/03db_01aurora/main.tf)
- Keep transactions short, no network calls inside
  - Prevents lock pile-ups and vacuum blocking

### 2.1 Dead Tuples In Code

A DELETE is cheap to retry, but it leaves work for VACUUM.

**Java**

```java
// infra/_03db_01aurora/AuroraJdbcRepository.java
// Naturally idempotent, so safe to retry.
// Catch: MVCC leaves the old row version as a dead tuple until VACUUM reclaims it.
@Override
public boolean delete(long id) {
    return writer.update("DELETE FROM x_order WHERE id = :id", Map.of("id", id)) == 1;
}
```

**Python**

```python
# app/infra/_03db_01aurora.py
def delete(self, order_id: int) -> bool:
    """Idempotent DELETE. Catch: the old row version stays as a dead tuple until VACUUM."""
    return self._conn.execute("DELETE FROM x_order WHERE id = %s", (order_id,)).rowcount == 1
```

**Catch**

→ Long or idle transactions block vacuum  
⇒ Dead tuples rise (`n_dead_tup`)  
⇒ Table bloat, slower scans  
→ `idle_in_transaction_session_timeout`, autovacuum tuning

## 3. Transaction Identifier (ID) Wraparound

- Transaction IDs are 32-bit
- VACUUM "freezes" old rows
- If it falls behind, Postgres stops writes to prevent wraparound
- Watch `age(datfrozenxid)`

## 4. Heap-Only Tuple (HOT) Updates

- UPDATE-heavy hot rows also create versions
- **HOT updates** avoid index writes when no indexed column changes

## Related

- [00index](01aurora.00index.md)
- [08isolation-levels](01aurora.08isolation-levels.md): snapshots per statement vs per transaction
