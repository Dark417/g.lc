"""Domain for the MongoDB slice: models, errors, port. No pymongo imports here.

Order document shape (one document per order, see app/infra/_03db_04mongodb.py):
- items embedded (bounded, <= 100), customer_name copied from the customer (extended reference)
- money as int minor units (cents), never float
- version = optimistic-lock token
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Protocol

MAX_ITEMS = 100  # bounds the embedded array: 16 MB document cap, multikey index size


class OrderStatus(StrEnum):
    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

    @property
    def is_terminal(self) -> bool:
        return self in (OrderStatus.DELIVERED, OrderStatus.CANCELLED)


@dataclass(frozen=True)
class LineItem:
    sku: str
    qty: int
    price_cents: int

    def __post_init__(self) -> None:
        if not self.sku or self.qty <= 0 or self.price_cents < 0:
            raise ValueError("sku required, qty > 0, price_cents >= 0")

    @property
    def subtotal_cents(self) -> int:
        return self.qty * self.price_cents


@dataclass(frozen=True)
class NewOrder:
    customer_id: str
    customer_name: str | None
    items: tuple[LineItem, ...]
    note: str | None = None

    def __post_init__(self) -> None:
        if not self.customer_id:
            raise ValueError("customer_id required")
        if not 1 <= len(self.items) <= MAX_ITEMS:
            raise ValueError(f"1..{MAX_ITEMS} items required")

    @property
    def total_cents(self) -> int:
        return sum(i.subtotal_cents for i in self.items)


@dataclass(frozen=True)
class Order:
    id: str  # ObjectId hex
    customer_id: str
    customer_name: str | None
    status: OrderStatus
    items: tuple[LineItem, ...]
    total_cents: int
    note: str | None
    created_at: datetime  # millisecond precision (BSON Date)
    updated_at: datetime | None
    version: int


@dataclass(frozen=True)
class OrderPage:
    items: list[Order]
    next_cursor: str | None  # None = no more pages


@dataclass(frozen=True)
class CustomerRevenue:
    customer_id: str
    customer_name: str | None
    revenue_cents: int
    order_count: int


@dataclass(frozen=True)
class StockLevel:
    sku: str
    qty: int


@dataclass(frozen=True)
class OrderChange:
    operation_type: str
    order_id: str | None
    status: OrderStatus | None  # None for deletes
    resume_token: str  # JSON of the event _id; persist AFTER handling


@dataclass(frozen=True)
class BulkSummary:
    inserted: int
    matched: int
    modified: int
    upserted: int
    deleted: int
    errors: list[str] = field(default_factory=list)  # "index:code:message"; successful ops stay applied


@dataclass(frozen=True)
class QueryPlanSummary:
    winning_stage: str
    index_name: str | None
    keys_examined: int
    docs_examined: int
    n_returned: int
    execution_millis: int
    blocking_sort: bool
    covered: bool

    @property
    def keys_per_result(self) -> float:
        return float(self.keys_examined) if self.n_returned == 0 else self.keys_examined / self.n_returned


class VersionConflictError(Exception):
    def __init__(self, order_id: str, expected_version: int, current: Order | None) -> None:
        super().__init__(f"order {order_id} is not at version {expected_version}")
        self.current = current


class InsufficientStockError(Exception):
    """Raised inside a transaction body: a non-PyMongo exception aborts with_transaction without a retry."""

    def __init__(self, sku: str, requested: int) -> None:
        super().__init__(f"insufficient stock for {sku} (requested {requested})")


class OrderNotFoundError(Exception):
    def __init__(self, order_id: str) -> None:
        super().__init__(f"order {order_id} not found")


class OrderStore(Protocol):
    """Port; the adapter is MongoOrderStore in app/infra/_03db_04mongodb.py."""

    def place_order(self, order: NewOrder) -> Order: ...

    def find_order(self, order_id: str) -> Order | None: ...

    def list_customer_orders(self, customer_id: str, limit: int, cursor: str | None) -> OrderPage: ...

    def change_status(self, order_id: str, status: OrderStatus, expected_version: int) -> Order: ...

    def revenue_by_customer(self, since: datetime, limit: int) -> list[CustomerRevenue]: ...

    def explain_customer_orders(self, customer_id: str) -> QueryPlanSummary: ...

    def ensure_indexes(self) -> list[str]: ...
