"""Domain for the DynamoDB slice: models, key design, ports. No boto3 imports here.

Key design (mirrors the header of terraform/03.02.dynamodb.tf):
- PK = CUSTOMER#<customerId>, SK = ORDER#<createdAtIso>#<orderId> | PROFILE
- GSI1PK = STATUS#<status>, GSI1SK = <createdAtIso>
- Sort keys compare as strings byte by byte, so timestamps MUST be fixed width (see iso()).
"""

import zlib
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import StrEnum
from typing import Protocol

CUSTOMER_PREFIX = "CUSTOMER#"
ORDER_PREFIX = "ORDER#"
PROFILE_SK = "PROFILE"
STATUS_PREFIX = "STATUS#"
ENTITY_ORDER = "ORDER"


class OrderStatus(StrEnum):
    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

    @property
    def is_terminal(self) -> bool:
        # Terminal statuses drop out of GSI1 (sparse index): the writer REMOVEs GSI1PK/GSI1SK.
        return self in (OrderStatus.DELIVERED, OrderStatus.CANCELLED)


# ---------------------------------------------------------------- key design


def iso(t: datetime) -> str:
    """Fixed-width UTC timestamp with millis.

    datetime.isoformat() drops zero microseconds ("...00+00:00" vs "...00.123+00:00"), which breaks
    string ordering of sort keys. Always 'YYYY-MM-DDTHH:MM:SS.mmmZ'.
    """
    t = t.astimezone(timezone.utc)
    return t.strftime("%Y-%m-%dT%H:%M:%S.") + f"{t.microsecond // 1000:03d}Z"


def parse_iso(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)


def truncate_to_millis(t: datetime) -> datetime:
    return t.replace(microsecond=(t.microsecond // 1000) * 1000)


def pk_customer(customer_id: str) -> str:
    return CUSTOMER_PREFIX + customer_id


def sk_order(created_at: datetime, order_id: str) -> str:
    return f"{ORDER_PREFIX}{iso(created_at)}#{order_id}"


def sk_order_bound(t: datetime) -> str:
    """BETWEEN bound: 'ORDER#<iso>' sorts before every 'ORDER#<iso>#<id>' -> BETWEEN acts as [from, to)."""
    return ORDER_PREFIX + iso(t)


def gsi1_pk(status: OrderStatus) -> str:
    return STATUS_PREFIX + status.value


def gsi1_sk(created_at: datetime) -> str:
    return iso(created_at)


def shard_of(order_id: str, shards: int) -> int:
    """CRC32 suffix: identical to the Java OrderKeys.shardOf, so both writers agree on the shard."""
    return zlib.crc32(order_id.encode("utf-8")) % shards


def gsi1_pk_sharded(status: OrderStatus, order_id: str, shards: int) -> str:
    return f"{gsi1_pk(status)}#{shard_of(order_id, shards)}"


def gsi1_pk_shard(status: OrderStatus, shard: int) -> str:
    return f"{gsi1_pk(status)}#{shard}"


def scoped_idempotency_key(customer_id: str, client_key: str) -> str:
    """Scope by caller so two customers can't collide on the same client key."""
    return f"{customer_id}#{client_key}"


# ---------------------------------------------------------------- models


@dataclass(frozen=True)
class OrderRef:
    """Full primary key of one order item."""

    customer_id: str
    created_at: datetime
    order_id: str

    @property
    def pk(self) -> str:
        return pk_customer(self.customer_id)

    @property
    def sk(self) -> str:
        return sk_order(self.created_at, self.order_id)


@dataclass(frozen=True)
class Order:
    """Order item. version = optimistic-lock counter (1 on create); expires_at = TTL epoch seconds or None."""

    customer_id: str
    order_id: str
    created_at: datetime
    status: OrderStatus
    amount_cents: int
    version: int = 1
    expires_at: int | None = None

    @staticmethod
    def new_pending(customer_id: str, order_id: str, created_at: datetime, amount_cents: int) -> "Order":
        return Order(customer_id, order_id, truncate_to_millis(created_at), OrderStatus.PENDING, amount_cents)

    @property
    def ref(self) -> OrderRef:
        return OrderRef(self.customer_id, self.created_at, self.order_id)

    def with_status(self, status: OrderStatus) -> "Order":
        return replace(self, status=status)


@dataclass(frozen=True)
class OrderSummary:
    """GSI1 item: keys + INCLUDE projection (orderId, customerId, amountCents). No status/version."""

    customer_id: str
    order_id: str
    created_at: datetime
    amount_cents: int


@dataclass(frozen=True)
class CursorPage:
    """next_cursor is None ONLY when there are no more pages; a short/empty page is not the end."""

    items: list[Order]
    next_cursor: str | None


@dataclass(frozen=True)
class ProfileStats:
    customer_id: str
    order_count: int
    total_spent_cents: int
    last_order_at: str | None


@dataclass(frozen=True)
class IdempotencyRecord:
    """x-idempotency item. request_hash detects key reuse with a different body; expires_at = TTL."""

    idempotency_key: str
    request_hash: str
    customer_id: str
    order_id: str
    order_created_at: str
    expires_at: int


class PlaceStatus(StrEnum):
    COMMITTED = "COMMITTED"
    KEY_ALREADY_USED = "KEY_ALREADY_USED"
    ORDER_ALREADY_EXISTS = "ORDER_ALREADY_EXISTS"


@dataclass(frozen=True)
class PlaceAttempt:
    status: PlaceStatus
    existing: IdempotencyRecord | None = None


@dataclass(frozen=True)
class PlaceOrderCommand:
    idempotency_key: str
    customer_id: str
    amount_cents: int


@dataclass(frozen=True)
class PlaceOrderResult:
    order: Order
    replayed: bool


class ChangeType(StrEnum):
    INSERT = "INSERT"
    MODIFY = "MODIFY"
    REMOVE = "REMOVE"


@dataclass(frozen=True)
class OrderChange:
    """Parsed stream record (NEW_AND_OLD_IMAGES). before=None on INSERT, after=None on REMOVE."""

    event_id: str
    sequence_number: str
    type: ChangeType
    before: Order | None
    after: Order | None
    ttl_expiry: bool

    @property
    def status_changed(self) -> bool:
        return self.before is not None and self.after is not None and self.before.status != self.after.status


# ---------------------------------------------------------------- errors + port


class VersionConflictError(Exception):
    """Optimistic-lock failure; current = winner's item (from ALL_OLD), None when the order is missing."""

    def __init__(self, current: Order | None) -> None:
        super().__init__("order not found" if current is None else f"version conflict, current {current.version}")
        self.current = current


class IdempotencyKeyReuseError(Exception):
    """Same key, different request body: reject (HTTP 422), never replay someone else's result."""


class OrderStore(Protocol):
    """Port used by the service; implemented by infra.DynamoDbOrderStore."""

    def place_order(self, order: Order, record: IdempotencyRecord, now: datetime) -> PlaceAttempt: ...

    def get_order(self, ref: OrderRef, consistent: bool) -> Order | None: ...

    def list_orders(self, customer_id: str, limit: int, cursor: str | None) -> CursorPage: ...

    def list_by_status(self, status: OrderStatus, limit: int) -> list[OrderSummary]: ...

    def change_status(self, ref: OrderRef, status: OrderStatus, expected_version: int) -> Order: ...
