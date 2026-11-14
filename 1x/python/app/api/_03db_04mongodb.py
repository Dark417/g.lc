"""Thin REST adapter, mounted at /mongodb by app.main when "mongodb" is in X_ENABLED.

- POST /orders runs the order + inventory transaction; insufficient stock = 409.
- Lists return an opaque next_cursor (keyset); version is the optimistic-lock token (409 on conflict).
- The service is built lazily on first request: importing this module opens no connection.
"""

from dataclasses import asdict
from functools import lru_cache
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.domain._03db_04mongodb import (
    MAX_ITEMS,
    InsufficientStockError,
    LineItem,
    NewOrder,
    Order,
    OrderNotFoundError,
    OrderStatus,
    VersionConflictError,
)
from app.infra._03db_04mongodb import MongoOrderStore, MongoShowcase, MongoTransactions
from app.service._03db_04mongodb import MongoOrderService

router = APIRouter()


@lru_cache
def get_service() -> MongoOrderService:
    return MongoOrderService(MongoOrderStore(MongoShowcase(), MongoTransactions()))


Service = Annotated[MongoOrderService, Depends(get_service)]


class LineItemRequest(BaseModel):
    sku: str = Field(min_length=1)
    qty: int = Field(gt=0)
    price_cents: int = Field(ge=0)


class PlaceOrderRequest(BaseModel):
    customer_id: str = Field(min_length=1)
    customer_name: str | None = None
    items: list[LineItemRequest] = Field(min_length=1, max_length=MAX_ITEMS)
    note: str | None = None


class ChangeStatusRequest(BaseModel):
    status: OrderStatus
    expected_version: int = Field(gt=0)


def _order_json(order: Order) -> dict[str, Any]:
    data = asdict(order)
    data["created_at"] = order.created_at.isoformat()
    data["updated_at"] = order.updated_at.isoformat() if order.updated_at else None
    return data


def _bad_request(e: ValueError) -> HTTPException:
    return HTTPException(status.HTTP_400_BAD_REQUEST, str(e))


@router.post("/orders", status_code=status.HTTP_201_CREATED)
def place_order(body: PlaceOrderRequest, service: Service) -> dict[str, Any]:
    items = tuple(LineItem(i.sku, i.qty, i.price_cents) for i in body.items)
    try:
        placed = service.place_order(NewOrder(body.customer_id, body.customer_name, items, body.note))
    except InsufficientStockError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e)) from e
    return _order_json(placed)


@router.get("/orders/{order_id}")
def get_order(order_id: str, service: Service) -> dict[str, Any]:
    try:
        return _order_json(service.get_order(order_id))
    except OrderNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e)) from e
    except ValueError as e:
        raise _bad_request(e) from e


@router.get("/customers/{customer_id}/orders")
def list_orders(
    customer_id: str,
    service: Service,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    cursor: str | None = None,
) -> dict[str, Any]:
    try:
        page = service.list_customer_orders(customer_id, limit, cursor)
    except ValueError as e:
        raise _bad_request(e) from e
    return {"items": [_order_json(o) for o in page.items], "next_cursor": page.next_cursor}


@router.put("/orders/{order_id}/status")
def change_status(order_id: str, body: ChangeStatusRequest, service: Service) -> dict[str, Any]:
    try:
        return _order_json(service.change_status(order_id, body.status, body.expected_version))
    except OrderNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e)) from e
    except VersionConflictError as e:
        current = _order_json(e.current) if e.current else None
        raise HTTPException(status.HTTP_409_CONFLICT, {"error": str(e), "current": current}) from e
    except ValueError as e:
        raise _bad_request(e) from e


@router.get("/reports/revenue")
def revenue(
    service: Service,
    days: Annotated[int, Query(ge=1, le=366)] = 30,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> list[dict[str, Any]]:
    return [asdict(r) for r in service.revenue_report(days, limit)]


@router.post("/admin/indexes")
def ensure_indexes(service: Service) -> list[str]:
    return service.ensure_indexes()


@router.get("/explain/customer-orders")
def explain_customer_orders(customer_id: str, service: Service) -> dict[str, Any]:
    plan = service.explain_customer_orders(customer_id)
    return {**asdict(plan), "keys_per_result": plan.keys_per_result}
