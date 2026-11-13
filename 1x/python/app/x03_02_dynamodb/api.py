"""Thin REST adapter, mounted at /dynamodb by app.main when "dynamodb" is in X_ENABLED.

- POST /orders requires Idempotency-Key: a replay returns 200 with the original order, a new order 201.
- Lists return an opaque next_cursor; version is the optimistic-lock token.
- The service is built lazily on first request: importing this module makes no AWS call.
"""

from dataclasses import asdict
from datetime import datetime
from functools import lru_cache
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, status
from pydantic import BaseModel, Field

from app.x03_02_dynamodb.domain import (
    IdempotencyKeyReuseError,
    Order,
    OrderRef,
    OrderStatus,
    PlaceOrderCommand,
    VersionConflictError,
)
from app.x03_02_dynamodb.infra import DynamoDbOrderStore, DynamoDbShowcase
from app.x03_02_dynamodb.service import PlaceOrderService

router = APIRouter()


@lru_cache
def get_service() -> PlaceOrderService:
    return PlaceOrderService(DynamoDbOrderStore(DynamoDbShowcase()))


Service = Annotated[PlaceOrderService, Depends(get_service)]


class PlaceOrderRequest(BaseModel):
    customer_id: str = Field(min_length=1)
    amount_cents: int = Field(gt=0)


class ChangeStatusRequest(BaseModel):
    status: OrderStatus
    expected_version: int = Field(gt=0)


def _order_json(order: Order) -> dict[str, Any]:
    data = asdict(order)
    data["created_at"] = order.created_at.isoformat()
    return data


@router.post("/orders")
def place_order(
    body: PlaceOrderRequest,
    response: Response,
    service: Service,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1)],
) -> dict[str, Any]:
    try:
        result = service.place_order(PlaceOrderCommand(idempotency_key, body.customer_id, body.amount_cents))
    except IdempotencyKeyReuseError as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(e)) from e
    response.status_code = status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED
    return _order_json(result.order)


@router.get("/customers/{customer_id}/orders")
def list_orders(
    customer_id: str, service: Service, limit: int = 20, cursor: str | None = None
) -> dict[str, Any]:
    try:
        page = service.list_orders(customer_id, limit, cursor)
    except ValueError as e:  # malformed or foreign cursor
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e)) from e
    return {"items": [_order_json(o) for o in page.items], "next_cursor": page.next_cursor}


@router.get("/customers/{customer_id}/orders/{order_id}")
def get_order(
    customer_id: str,
    order_id: str,
    service: Service,
    created_at: Annotated[datetime, Query()],
    consistent: bool = False,
) -> dict[str, Any]:
    order = service.get_order(OrderRef(customer_id, created_at, order_id), consistent)
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "order not found")
    return _order_json(order)


@router.put("/customers/{customer_id}/orders/{order_id}/status")
def change_status(
    customer_id: str,
    order_id: str,
    body: ChangeStatusRequest,
    service: Service,
    created_at: Annotated[datetime, Query()],
) -> dict[str, Any]:
    try:
        order = service.change_status(OrderRef(customer_id, created_at, order_id), body.status, body.expected_version)
    except VersionConflictError as e:
        if e.current is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "order not found") from e
        raise HTTPException(
            status.HTTP_409_CONFLICT, {"error": "version conflict", "current": _order_json(e.current)}
        ) from e
    return _order_json(order)


@router.get("/orders/by-status/{order_status}")
def by_status(order_status: OrderStatus, service: Service, limit: int = 20) -> list[dict[str, Any]]:
    items = service.list_by_status(order_status, limit)
    return [{**asdict(s), "created_at": s.created_at.isoformat()} for s in items]
