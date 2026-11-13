"""Use cases for the Aurora slice: transaction boundaries, retries, read routing.

- Every `with repo.writer_tx(...)` block is one transaction; retries wrap the WHOLE block from outside.
  Retrying inside a failed transaction only yields InFailedSqlTransaction (25P02).
- Retried writes carry an idempotency key, so a commit whose ack was lost (failover) is replayed safely.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
from typing import Any, TypeVar

from app.shared.retry import call_with_retry
from app.x03_01_aurora.domain import (
    BatchResult,
    BusinessRuleViolation,
    CustomerSummary,
    Isolation,
    Job,
    NewOrder,
    Order,
    OrderNotFound,
    OrderStatus,
    OrderStore,
    Page,
    StockLevel,
    TransactionalStore,
    VersionConflict,
)
from app.x03_01_aurora.infra import decode_cursor, is_retryable

T = TypeVar("T")

CREDIT_LIMIT_CENTS = 100_000  # demo invariant for the SERIALIZABLE example; a real limit lives in a customer table
IMPORT_CHUNK_SIZE = 500
MAX_PAGE_SIZE = 100
JOB_MAX_ATTEMPTS = 5

# Retry budget meant to span an Aurora failover (AWS: typically < 60 s, often < 30 s).
RETRY_ATTEMPTS = 8
RETRY_BASE_S = 0.2
RETRY_CAP_S = 8.0


class AuroraOrderService:
    def __init__(self, repo: TransactionalStore) -> None:
        self._repo = repo

    # ================================================================ retry at the transaction boundary

    def _with_retry(self, fn: Callable[[], T]) -> T:
        """Each call of fn opens a fresh transaction; retried on 40001/40P01/08xxx/57P0x/25006/55P03 with full jitter.

        When to use: around transactional use cases whose writes are idempotent.
        Catch: never call it from inside an open transaction block.
        """
        return call_with_retry(
            fn,
            is_retryable,
            max_attempts=RETRY_ATTEMPTS,
            base=RETRY_BASE_S,
            cap=RETRY_CAP_S,
        )

    # ================================================================ create

    def create_order_once(self, cmd: NewOrder) -> Order:
        """No idempotency key => single attempt; a lost commit ack leaves the client unsure."""
        with self._repo.writer_tx() as store:
            return store.insert(cmd)

    def place_order(self, cmd: NewOrder) -> Order:
        """Create + reserve stock atomically, retried safely thanks to the idempotency key."""
        _require_key(cmd)
        return self._with_retry(lambda: self._place_once(cmd))

    def _place_once(self, cmd: NewOrder) -> Order:
        """One attempt = an independent attempt-log transaction, then one READ COMMITTED business transaction.

        - REQUIRES_NEW analogue: the ORDER_ATTEMPT row commits in its own transaction and survives a rollback below.
          It is opened BEFORE the business transaction, so a request never holds two pooled connections at once.
        - REQUIRED analogue: ORDER_PLACED uses the same store, so it commits or rolls back with the order.
        """
        with self._repo.independent_tx() as audit:
            audit.append_audit("ORDER_ATTEMPT", cmd.idempotency_key)
        with self._repo.writer_tx() as store:
            created = store.insert_idempotent(cmd)
            if created is None:
                return _replay_of(
                    store, cmd
                )  # an earlier attempt committed; do not reserve stock twice
            on_hand = store.lock_stock_for_update(cmd.sku)  # row lock until commit
            if on_hand < cmd.quantity:
                # Raising inside the block rolls back the order insert; ORDER_ATTEMPT is already committed.
                raise BusinessRuleViolation(
                    f"insufficient stock for {cmd.sku}: {on_hand} < {cmd.quantity}"
                )
            store.decrement_stock(cmd.sku, cmd.quantity)
            store.append_audit("ORDER_PLACED", f"order {created.id}")
            return created

    def place_order_within_credit_limit(self, cmd: NewOrder) -> Order:
        """SERIALIZABLE write-skew guard; 40001 under contention is expected and the retry makes it correct."""
        _require_key(cmd)
        return self._with_retry(lambda: self._place_within_limit_once(cmd))

    def _place_within_limit_once(self, cmd: NewOrder) -> Order:
        """Read open total, check, insert: under READ COMMITTED / REPEATABLE READ two concurrent calls both pass.

        SERIALIZABLE (SSI) detects the read-write cycle and aborts one with SerializationFailure (40001);
        the retry re-reads and sees the other order. Catch: correctness depends on that retry.
        """
        with self._repo.writer_tx(Isolation.SERIALIZABLE) as store:
            assert cmd.idempotency_key is not None
            existing = store.find_by_idempotency_key(cmd.idempotency_key)
            if existing is not None:
                return _check_same_request(existing, cmd)
            open_cents = store.sum_open_amount_cents(cmd.customer_id)
            if open_cents + cmd.amount_cents > CREDIT_LIMIT_CENTS:
                raise BusinessRuleViolation(
                    f"credit limit exceeded: open {open_cents} + {cmd.amount_cents} > {CREDIT_LIMIT_CENTS}"
                )
            created = store.insert_idempotent(cmd)
            return created if created is not None else _replay_of(store, cmd)

    # ================================================================ optimistic update, retry-safe

    def change_status(
        self, order_id: int, expected_version: int, status: OrderStatus
    ) -> Order:
        """Version-guarded update + audit in one transaction.

        Catch: a retry after a lost commit ack sees version+1; on attempts > 1 a conflict whose current state equals
        the requested state counts as success (indistinguishable from an identical concurrent change).
        """
        attempts = 0

        def attempt() -> Order:
            nonlocal attempts
            attempts += 1
            try:
                with self._repo.writer_tx() as store:
                    updated = store.update_status_if_version(
                        order_id, expected_version, status
                    )
                    store.append_audit(
                        "STATUS_CHANGED",
                        f"order {order_id} -> {status} v{updated.version}",
                    )
                    return updated
            except VersionConflict:
                if attempts > 1:
                    with self._repo.writer_tx() as store:
                        current = store.find_by_id(order_id)
                    if (
                        current
                        and current.status is status
                        and current.version == expected_version + 1
                    ):
                        return current
                raise

        return self._with_retry(attempt)

    def delete_order(self, order_id: int) -> bool:
        """Idempotent delete, retried freely."""

        def attempt() -> bool:
            with self._repo.writer_tx() as store:
                return store.delete(order_id)

        return self._with_retry(attempt)

    # ================================================================ batch with partial failure

    def import_orders(self, rows: list[NewOrder]) -> BatchResult:
        """Chunks of IMPORT_CHUNK_SIZE; each chunk = one transaction, retried (keys make replays no-ops).

        A chunk that still fails is reported and the others stay committed.
        """
        inserted = 0
        failures: list[str] = []
        for start in range(0, len(rows), IMPORT_CHUNK_SIZE):
            chunk = rows[start : start + IMPORT_CHUNK_SIZE]

            def attempt(chunk: list[NewOrder] = chunk) -> int:
                with self._repo.writer_tx() as store:
                    return store.batch_insert(chunk)

            try:
                inserted += self._with_retry(attempt)
            except Exception as e:  # noqa: BLE001 - report per chunk, keep going
                state = getattr(e, "sqlstate", None)
                failures.append(
                    f"rows {start}..{start + len(chunk) - 1}: {state or ''} {type(e).__name__}".strip()
                )
        return BatchResult(requested=len(rows), inserted=inserted, failures=failures)

    # ================================================================ reads: routing + read-after-write

    def get_order(
        self, order_id: int, strong: bool = False, min_version: int | None = None
    ) -> Order:
        """Reader first; writer when strong, when the reader misses, or when its version < min_version.

        Catch: every fallback is writer load; without min_version a stale-but-present row is returned.
        """

        def attempt() -> Order:
            if not strong:
                with self._repo.reader_tx(Isolation.READ_COMMITTED) as replica:
                    found = replica.find_by_id(order_id)
                if found is not None and (
                    min_version is None or found.version >= min_version
                ):
                    return found
                # miss or stale: replica lag, not necessarily absence
            with self._repo.writer_tx() as store:
                order = store.find_by_id(order_id)
            if order is None:
                raise OrderNotFound(f"order {order_id} not found")
            return order

        return self._with_retry(attempt)

    def list_by_keyset(
        self, customer_id: str, cursor: str | None, size: int
    ) -> Page[Order]:
        """Keyset page from the reader. Contract: pass `next` back verbatim; None = last page."""
        if cursor:
            decode_cursor(
                cursor
            )  # reject a malformed cursor (400) before borrowing a connection
        n = _clamp(size)
        return self._with_retry(
            lambda: self._on_reader(lambda s: s.page_by_keyset(customer_id, cursor, n))
        )

    def list_by_offset(self, customer_id: str, page: int, size: int) -> Page[Order]:
        """OFFSET page from the reader, kept for comparison: cost grows with page number."""
        n = _clamp(size)
        return self._with_retry(
            lambda: self._on_reader(
                lambda s: s.page_by_offset(customer_id, max(0, page), n)
            )
        )

    def search(self, containment: dict[str, Any], limit: int) -> list[Order]:
        """JSONB containment search on the reader."""
        n = _clamp(limit)
        return self._with_retry(
            lambda: self._on_reader(lambda s: s.find_by_attrs(containment, n))
        )

    def customer_summary(self, customer_id: str) -> CustomerSummary:
        """Two queries in one REPEATABLE READ snapshot on the reader, so count/sum agree with the latest rows."""

        def attempt() -> CustomerSummary:
            with self._repo.reader_tx(Isolation.REPEATABLE_READ) as replica:
                count, total = replica.count_and_sum(customer_id)
                latest = replica.latest(customer_id, 5)
            return CustomerSummary(
                customer_id=customer_id,
                order_count=count,
                total_cents=total,
                latest=latest,
            )

        return self._with_retry(attempt)

    # ================================================================ upsert

    def restock(self, sku: str, on_hand: int) -> StockLevel:
        """'Set stock to N' upsert: idempotent, so retried."""

        def attempt() -> StockLevel:
            with self._repo.writer_tx() as store:
                return store.upsert_stock(sku, on_hand)

        return self._with_retry(attempt)

    # ================================================================ job queue

    def enqueue_job(self, kind: str, payload: dict[str, Any]) -> int:
        """Not retried: no dedup key on jobs, so a lost ack + retry would enqueue twice."""
        with self._repo.writer_tx() as store:
            return store.enqueue(kind, payload)

    def claim_jobs(self, worker_id: str, limit: int, lease: timedelta) -> list[Job]:
        """Retried: a lost ack leaves jobs under our lease, and they return to READY when it expires."""

        def attempt() -> list[Job]:
            with self._repo.writer_tx() as store:
                return store.claim(worker_id, _clamp(limit), lease)

        return self._with_retry(attempt)

    def complete_job(self, job_id: int, worker_id: str) -> None:
        """Retried: DONE keeps locked_by, so a replayed complete is a no-op success."""

        def attempt() -> None:
            with self._repo.writer_tx() as store:
                store.complete(job_id, worker_id)

        self._with_retry(attempt)

    def fail_job(self, job_id: int, worker_id: str, error: str) -> None:
        """Not retried: a lost ack just lets the lease expire, and the reaper requeues (same end state)."""
        with self._repo.writer_tx() as store:
            store.fail(
                job_id, worker_id, error, timedelta(seconds=30), JOB_MAX_ATTEMPTS
            )

    def requeue_expired_jobs(self) -> int:
        """Reaper for expired leases; idempotent."""

        def attempt() -> int:
            with self._repo.writer_tx() as store:
                return store.requeue_expired(JOB_MAX_ATTEMPTS)

        return self._with_retry(attempt)

    # ================================================================ ops

    def replica_lag(self) -> dict[str, int]:
        return self._repo.replica_lag_ms()

    def apply_schema(self) -> None:
        self._repo.apply_schema()

    # ================================================================ helpers

    def _on_reader(self, fn: Callable[[OrderStore], T]) -> T:
        with self._repo.reader_tx(Isolation.READ_COMMITTED) as replica:
            return fn(replica)


def _require_key(cmd: NewOrder) -> None:
    if not cmd.idempotency_key:
        raise ValueError("Idempotency-Key is required for retried writes")


def _clamp(size: int) -> int:
    return min(max(1, size), MAX_PAGE_SIZE)


def _replay_of(store: OrderStore, cmd: NewOrder) -> Order:
    assert cmd.idempotency_key is not None
    existing = store.find_by_idempotency_key(cmd.idempotency_key)
    if existing is None:
        raise RuntimeError(f"conflict on {cmd.idempotency_key} but no row")
    return _check_same_request(existing, cmd)


def _check_same_request(existing: Order, cmd: NewOrder) -> Order:
    """Same key with a different body is a client bug, not a replay."""
    same = (
        existing.customer_id == cmd.customer_id
        and existing.sku == cmd.sku
        and existing.quantity == cmd.quantity
        and existing.amount_cents == cmd.amount_cents
    )
    if not same:
        raise BusinessRuleViolation(
            f"idempotency key {cmd.idempotency_key} reused with a different request"
        )
    return existing
