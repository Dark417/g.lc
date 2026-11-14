"""Domain models and ports for the Aurora slice (no driver or SDK imports).

- OrderStore = one unit of work bound to one connection and one transaction.
- TransactionalStore = opens units of work on the writer or reader endpoint with an isolation level.
"""

from __future__ import annotations

from contextlib import AbstractContextManager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any, Generic, Protocol, TypeVar

T = TypeVar("T")


class OrderStatus(StrEnum):
    NEW = "NEW"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


class JobStatus(StrEnum):
    READY = "READY"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"


class Isolation(StrEnum):
    """PostgreSQL isolation levels; the value is the SQL spelling (never user input)."""

    READ_COMMITTED = "READ COMMITTED"
    REPEATABLE_READ = "REPEATABLE READ"
    SERIALIZABLE = "SERIALIZABLE"


@dataclass(frozen=True)
class NewOrder:
    """Create command. idempotency_key: unique per logical request, so a retried create returns the same row."""

    customer_id: str
    sku: str
    quantity: int
    amount_cents: int
    idempotency_key: str | None = None
    attrs: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("quantity must be > 0")
        if self.amount_cents < 0:
            raise ValueError("amount_cents must be >= 0")


@dataclass(frozen=True)
class Order:
    """Persisted order. version = optimistic-lock counter and read-your-writes token."""

    id: int
    customer_id: str
    sku: str
    quantity: int
    amount_cents: int
    status: OrderStatus
    version: int
    idempotency_key: str | None
    attrs: dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class Page(Generic[T]):
    """One page; next is an opaque token (keyset cursor or page number), None on the last page."""

    items: list[T]
    next: str | None


@dataclass(frozen=True)
class Job:
    id: int
    kind: str
    payload: dict[str, Any]
    status: JobStatus
    attempts: int
    locked_by: str | None
    locked_until: datetime | None


@dataclass(frozen=True)
class StockLevel:
    sku: str
    on_hand: int
    updated_at: datetime


@dataclass(frozen=True)
class CustomerSummary:
    customer_id: str
    order_count: int
    total_cents: int
    latest: list[Order]


@dataclass(frozen=True)
class BatchResult:
    """Chunked import outcome: each chunk is one transaction; failures lists failed chunk ranges."""

    requested: int
    inserted: int
    failures: list[str]


class OrderNotFound(Exception):
    """No such order (HTTP 404)."""


class VersionConflict(Exception):
    """Optimistic lock failed: the row changed since it was read (HTTP 409)."""


class LeaseLost(Exception):
    """Worker no longer owns the job lease (HTTP 409)."""


class BusinessRuleViolation(Exception):
    """Invariant would break: insufficient stock, credit limit, reused key (HTTP 422). Not retryable."""


class OrderStore(Protocol):
    """Unit of work on one connection. Writes commit when the enclosing transaction block exits cleanly."""

    # CRUD + idempotent create
    def insert(self, order: NewOrder) -> Order: ...
    def insert_idempotent(self, order: NewOrder) -> Order | None: ...
    def find_by_id(self, order_id: int) -> Order | None: ...
    def find_by_idempotency_key(self, key: str) -> Order | None: ...
    def delete(self, order_id: int) -> bool: ...

    # batch + upsert
    def batch_insert(self, orders: list[NewOrder]) -> int: ...
    def upsert_stock(self, sku: str, on_hand: int) -> StockLevel: ...

    # pagination
    def page_by_offset(self, customer_id: str, page: int, size: int) -> Page[Order]: ...
    def page_by_keyset(
        self, customer_id: str, cursor: str | None, size: int
    ) -> Page[Order]: ...

    # locking
    def update_status_if_version(
        self, order_id: int, expected_version: int, status: OrderStatus
    ) -> Order: ...
    def lock_stock_for_update(self, sku: str) -> int: ...
    def decrement_stock(self, sku: str, quantity: int) -> None: ...
    def decrement_stock_if_available(self, sku: str, quantity: int) -> bool: ...
    def sum_open_amount_cents(self, customer_id: str) -> int: ...

    # job queue
    def enqueue(self, kind: str, payload: dict[str, Any]) -> int: ...
    def claim(self, worker_id: str, limit: int, lease: timedelta) -> list[Job]: ...
    def complete(self, job_id: int, worker_id: str) -> None: ...
    def fail(
        self,
        job_id: int,
        worker_id: str,
        error: str,
        retry_delay: timedelta,
        max_attempts: int,
    ) -> None: ...
    def requeue_expired(self, max_attempts: int) -> int: ...

    # JSONB + reports
    def find_by_attrs(self, containment: dict[str, Any], limit: int) -> list[Order]: ...
    def count_and_sum(self, customer_id: str) -> tuple[int, int]: ...
    def latest(self, customer_id: str, limit: int) -> list[Order]: ...

    # audit
    def append_audit(self, action: str, detail: str | None) -> None: ...


class TransactionalStore(Protocol):
    """Opens units of work. writer = cluster endpoint, reader = reader endpoint (may lag)."""

    def writer_tx(
        self, isolation: Isolation = Isolation.READ_COMMITTED
    ) -> AbstractContextManager[OrderStore]: ...
    def reader_tx(
        self, isolation: Isolation = Isolation.REPEATABLE_READ
    ) -> AbstractContextManager[OrderStore]: ...
    def independent_tx(self) -> AbstractContextManager[OrderStore]: ...
    def apply_schema(self) -> None: ...
    def replica_lag_ms(self) -> dict[str, int]: ...
