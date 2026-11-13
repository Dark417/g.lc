"""Use cases on top of the OrderStore port.

- place_order: idempotent create built on ONE transaction (order + idempotency record + profile counters).
- Both items commit atomically, so there is no "in progress" idempotency state to recover from.
"""

import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from app.x03_02_dynamodb.domain import (
    CursorPage,
    IdempotencyKeyReuseError,
    IdempotencyRecord,
    Order,
    OrderRef,
    OrderStatus,
    OrderStore,
    OrderSummary,
    PlaceOrderCommand,
    PlaceOrderResult,
    PlaceStatus,
    iso,
    parse_iso,
    scoped_idempotency_key,
)

IDEMPOTENCY_RETENTION = timedelta(hours=24)  # must outlive the client's maximum retry window
MAX_PAGE = 100


def request_hash(cmd: PlaceOrderCommand) -> str:
    """Fields that define 'the same request'; excludes the key itself and server-generated values."""
    return hashlib.sha256(f"{cmd.customer_id}|{cmd.amount_cents}".encode()).hexdigest()


class PlaceOrderService:
    def __init__(self, store: OrderStore, retention: timedelta = IDEMPOTENCY_RETENTION) -> None:
        self.store = store
        self.retention = retention

    def place_order(self, cmd: PlaceOrderCommand) -> PlaceOrderResult:
        """Same key + same body -> the original order (replayed=True); same key + other body -> 422.

        Catch: retention must exceed the client's retry horizon, or a very late retry creates a duplicate.
        """
        now = datetime.now(timezone.utc)
        key = scoped_idempotency_key(cmd.customer_id, cmd.idempotency_key)
        digest = request_hash(cmd)
        order = Order.new_pending(cmd.customer_id, str(uuid.uuid4()), now, cmd.amount_cents)
        record = IdempotencyRecord(
            idempotency_key=key,
            request_hash=digest,
            customer_id=order.customer_id,
            order_id=order.order_id,
            order_created_at=iso(order.created_at),
            expires_at=int((now + self.retention).timestamp()),
        )
        attempt = self.store.place_order(order, record, now)
        if attempt.status is PlaceStatus.COMMITTED:
            return PlaceOrderResult(order, replayed=False)
        if attempt.status is PlaceStatus.KEY_ALREADY_USED and attempt.existing is not None:
            return self._replay(attempt.existing, digest, key)
        # ORDER_ALREADY_EXISTS: a fresh UUID collided; practically impossible, fail loudly.
        raise RuntimeError(f"unexpected place outcome {attempt.status}")

    def _replay(self, existing: IdempotencyRecord, digest: str, key: str) -> PlaceOrderResult:
        if existing.request_hash != digest:
            raise IdempotencyKeyReuseError(key)
        # Strong read: the order committed with the record. Returns the order's CURRENT state;
        # store a response snapshot in the record if byte-exact replay matters.
        ref = OrderRef(existing.customer_id, parse_iso(existing.order_created_at), existing.order_id)
        stored = self.store.get_order(ref, consistent=True)
        if stored is None:
            raise RuntimeError("idempotency record points to a missing order")
        return PlaceOrderResult(stored, replayed=True)

    def get_order(self, ref: OrderRef, consistent: bool) -> Order | None:
        return self.store.get_order(ref, consistent)

    def list_orders(self, customer_id: str, limit: int, cursor: str | None) -> CursorPage:
        """Pagination contract: send next_cursor back unchanged; None = no more pages. Page size capped."""
        return self.store.list_orders(customer_id, max(1, min(limit, MAX_PAGE)), cursor)

    def list_by_status(self, status: OrderStatus, limit: int) -> list[OrderSummary]:
        return self.store.list_by_status(status, max(1, min(limit, MAX_PAGE)))

    def change_status(self, ref: OrderRef, status: OrderStatus, expected_version: int) -> Order:
        return self.store.change_status(ref, status, expected_version)
