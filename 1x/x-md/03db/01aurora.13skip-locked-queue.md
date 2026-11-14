# 03db.01aurora.13skip-locked-queue Job Queue With SKIP LOCKED And Leases

> `FOR UPDATE SKIP LOCKED` lets N workers claim different rows without waiting; a lease plus a reaper recovers crashed workers.

## Index

- [1. SKIP LOCKED](#1-skip-locked)
- [2. Lease Pattern](#2-lease-pattern)
- [3. Schema](#3-schema)
- [4. Claim](#4-claim)
- [5. Complete, Fail, Reap](#5-complete-fail-reap)
- [6. Limits](#6-limits)
- [Related](#related)

## 1. SKIP LOCKED

`FOR UPDATE SKIP LOCKED` (PostgreSQL 9.5+) skips rows another transaction locked instead of waiting.

- Result: N workers each grab different rows
- So a table works as a job queue

## 2. Lease Pattern

The pattern used in the code separates claiming from processing.

→ Claim = one short transaction: lock with SKIP LOCKED, set `RUNNING`, `locked_by`, `locked_until`  
→ Process outside the transaction  
→ Complete only if `locked_by` still matches  
⇒ 0 rows = lease lost  
→ A reaper resets expired leases to `READY`

- Delivery is at least once ⇒ job handlers must be idempotent

## 3. Schema

```sql
-- resources/_03db_01aurora/schema.sql
CREATE TABLE IF NOT EXISTS x_job (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    kind         TEXT        NOT NULL,
    payload      JSONB       NOT NULL,
    status       TEXT        NOT NULL DEFAULT 'READY',       -- READY, RUNNING, DONE, FAILED
    attempts     INT         NOT NULL DEFAULT 0,
    run_after    TIMESTAMPTZ NOT NULL DEFAULT now(),         -- retry backoff: not claimable before this
    locked_by    TEXT,
    locked_until TIMESTAMPTZ,                                -- lease expiry, reaper requeues after it
    last_error   TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Partial index: the claim query only scans READY rows, so DONE history does not slow it down.
CREATE INDEX IF NOT EXISTS x_job_ready_idx ON x_job (run_after, id) WHERE status = 'READY';
CREATE INDEX IF NOT EXISTS x_job_running_lease_idx ON x_job (locked_until) WHERE status = 'RUNNING';
```

## 4. Claim

Claim up to `limit` jobs in **one** statement.

**Java**

```java
// infra/_03db_01aurora/AuroraJdbcRepository.java
// Catch: process AFTER this statement commits (never hold the row lock while working).
@Override
public List<Job> claim(String workerId, int limit, Duration lease) {
    String sql = "WITH next AS ("
            + "  SELECT id FROM x_job WHERE status = 'READY' AND run_after <= now()"
            + "  ORDER BY run_after, id LIMIT :limit FOR UPDATE SKIP LOCKED) "  // other workers' rows skipped
            + "UPDATE x_job j SET status = 'RUNNING', locked_by = :worker, attempts = j.attempts + 1, "
            + "  locked_until = now() + (:leaseSeconds * interval '1 second') "
            + "FROM next WHERE j.id = next.id "
            + "RETURNING j.id, j.kind, j.payload, j.status, j.attempts, j.locked_by, j.locked_until";
    MapSqlParameterSource params = new MapSqlParameterSource()
            .addValue("limit", limit)
            .addValue("worker", workerId)
            .addValue("leaseSeconds", lease.toSeconds());
    return writer.query(sql, params, this::mapJob);
}
```

**Python**

```python
# app/infra/_03db_01aurora.py
def claim(self, worker_id: str, limit: int, lease: timedelta) -> list[Job]:
    """Catch: run it in autocommit (or a tiny transaction) and process afterwards; at-least-once delivery."""
    rows = self._conn.execute(
        "WITH next AS ("
        "  SELECT id FROM x_job WHERE status = 'READY' AND run_after <= now()"
        "  ORDER BY run_after, id LIMIT %(limit)s FOR UPDATE SKIP LOCKED) "
        "UPDATE x_job j SET status = 'RUNNING', locked_by = %(worker)s, attempts = j.attempts + 1, "
        "  locked_until = now() + %(lease)s "  # timedelta adapts to interval
        "FROM next WHERE j.id = next.id "
        "RETURNING j.id, j.kind, j.payload, j.status, j.attempts, j.locked_by, j.locked_until",
        {"limit": limit, "worker": worker_id, "lease": lease},
    ).fetchall()
    return [_job(r) for r in rows]
```

**Catch**

- Claim is retried
  - A lost ack leaves jobs `RUNNING` under our lease; they return to `READY` when it expires
- Enqueue is **not** retried: `x_job` has no dedup key
  - A lost ack + retry enqueues twice

## 5. Complete, Fail, Reap

All three are guarded by lease ownership or expiry.

**Java**

```java
// infra/_03db_01aurora/AuroraJdbcRepository.java
// DONE keeps locked_by so a retried complete is a no-op success.
@Override
public void complete(long jobId, String workerId) {
    int rows = writer.update(
            "UPDATE x_job SET status = 'DONE', locked_until = NULL "
                    + "WHERE id = :id AND locked_by = :worker AND status IN ('RUNNING', 'DONE')",
            Map.of("id", jobId, "worker", workerId));
    if (rows == 0) {
        throw new LeaseLostException(jobId, workerId); // lease expired, another worker re-claimed
    }
}

// Back to READY after retryDelay (backoff), or FAILED once attempts reach maxAttempts.
@Override
public void fail(long jobId, String workerId, String error, Duration retryDelay, int maxAttempts) {
    int rows = writer.update(
            "UPDATE x_job SET status = CASE WHEN attempts >= :max THEN 'FAILED' ELSE 'READY' END, "
                    + "run_after = now() + (:delaySeconds * interval '1 second'), "
                    + "locked_by = NULL, locked_until = NULL, last_error = :error "
                    + "WHERE id = :id AND locked_by = :worker AND status = 'RUNNING'",
            /* params */ ...);
    if (rows == 0) {
        throw new LeaseLostException(jobId, workerId);
    }
}

// Reaper: run periodically from any one node.
@Override
public int requeueExpired(int maxAttempts) {
    return writer.update(
            "UPDATE x_job SET status = CASE WHEN attempts >= :max THEN 'FAILED' ELSE 'READY' END, "
                    + "locked_by = NULL, locked_until = NULL, last_error = 'lease expired' "
                    + "WHERE status = 'RUNNING' AND locked_until < now()",
            Map.of("max", maxAttempts));
}
```

**Python**

```python
# app/infra/_03db_01aurora.py
def complete(self, job_id: int, worker_id: str) -> None:
    """Complete if still the lease owner; DONE keeps locked_by so a retried complete is a no-op."""
    cur = self._conn.execute(
        "UPDATE x_job SET status = 'DONE', locked_until = NULL "
        "WHERE id = %s AND locked_by = %s AND status IN ('RUNNING', 'DONE')",
        (job_id, worker_id),
    )
    if cur.rowcount == 0:
        raise LeaseLost(f"job {job_id} is not leased by {worker_id}")

def requeue_expired(self, max_attempts: int) -> int:
    """Reaper. Catch: lease must exceed the slowest legitimate job."""
    cur = self._conn.execute(
        "UPDATE x_job SET status = CASE WHEN attempts >= %s THEN 'FAILED' ELSE 'READY' END, "
        "locked_by = NULL, locked_until = NULL, last_error = 'lease expired' "
        "WHERE status = 'RUNNING' AND locked_until < now()",
        (max_attempts,),
    )
    return cur.rowcount
```

**Catch**

- `complete` 0 rows = the lease expired and another worker re-claimed
  - Our work may be duplicated ⇒ idempotent handlers
- `fail` is not retried: a lost ack is harmless because the lease expires anyway
- Lease must exceed the slowest legitimate job
  - Else a live worker loses its job to a second worker

→ Worker crashed after claiming  
⇒ Stuck job: `RUNNING` with past `locked_until`  
→ Lease + reaper; idempotent handler

## 6. Limits

- Polling load and index churn
- Beyond thousands of jobs/s, use Simple Queue Service (SQS) or Kafka
- Gap: LISTEN/NOTIFY wake-ups and an outbox relay are out of scope for this slice

## Related

- [00index](01aurora.00index.md)
- [12locking](01aurora.12locking.md)
- [10retries-idempotency](01aurora.10retries-idempotency.md)
- [99interview](01aurora.99interview.md): Q6
