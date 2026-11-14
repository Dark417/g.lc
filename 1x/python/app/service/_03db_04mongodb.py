"""Thin use cases over the OrderStore port: limits and defaults live here, driver code does not.

- Page size is capped so one request cannot pull an unbounded result through the WiredTiger cache.
"""

from datetime import datetime, timedelta, timezone

from app.domain._03db_04mongodb import (
    CustomerRevenue,
    NewOrder,
    Order,
    OrderNotFoundError,
    OrderPage,
    OrderStatus,
    OrderStore,
    QueryPlanSummary,
)

MAX_PAGE = 100
MAX_REPORT_ROWS = 100


class MongoOrderService:
    def __init__(self, store: OrderStore) -> None:
        self.store = store

    def place_order(self, order: NewOrder) -> Order:
        return self.store.place_order(order)

    def get_order(self, order_id: str) -> Order:
        order = self.store.find_order(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        return order

    def list_customer_orders(self, customer_id: str, limit: int, cursor: str | None) -> OrderPage:
        return self.store.list_customer_orders(customer_id, max(1, min(limit, MAX_PAGE)), cursor)

    def change_status(self, order_id: str, status: OrderStatus, expected_version: int) -> Order:
        return self.store.change_status(order_id, status, expected_version)

    def revenue_report(self, days: int, limit: int) -> list[CustomerRevenue]:
        since = datetime.now(timezone.utc) - timedelta(days=max(1, days))
        return self.store.revenue_by_customer(since, max(1, min(limit, MAX_REPORT_ROWS)))

    def explain_customer_orders(self, customer_id: str) -> QueryPlanSummary:
        return self.store.explain_customer_orders(customer_id)

    def ensure_indexes(self) -> list[str]:
        return self.store.ensure_indexes()
