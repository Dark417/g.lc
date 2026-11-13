"""Thin HTTP adapter for the Aurora slice, mounted at /aurora by app/main.py when X_ENABLED contains "aurora".

- Idempotency-Key header -> retried, deduplicated create; no header -> single attempt.
- If-Match: <version> -> optimistic update; the ETag response header carries the new version.
- Domain errors map to status codes in DomainErrorRoute (APIRouter cannot register exception handlers).
- The service (and its pools) is created on the first request, never at import.
"""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import asdict
from datetime import timedelta
from functools import lru_cache
from typing import Annotated, Any

import psycopg
from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.routing import APIRoute
from psycopg_pool import PoolTimeout
from pydantic import BaseModel, Field

from app.x03_01_aurora.domain import (
    BusinessRuleViolation,
    LeaseLost,
    NewOrder,
    OrderNotFound,
    OrderStatus,
    VersionConflict,
)
from app.x03_01_aurora.infra import AuroraPools, AuroraRepository, is_retryable
from app.x03_01_aurora.service import AuroraOrderService


class DomainErrorRoute(APIRoute):
    """Translate domain and database errors for every route of this router."""

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        handler = super().get_route_handler()

        async def wrapped(request: Request) -> Response:
            try:
                return await handler(request)
            except OrderNotFound as e:
                raise HTTPException(status_code=404, detail=str(e)) from e
            except (VersionConflict, LeaseLost) as e:
                raise HTTPException(status_code=409, detail=str(e)) from e
            except BusinessRuleViolation as e:
                raise HTTPException(status_code=422, detail=str(e)) from e
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e)) from e
            except PoolTimeout as e:
                # Pool saturated or database unreachable: not retried server-side (shed load); client may retry later.
                raise HTTPException(
                    status_code=503, detail="database busy or unreachable"
                ) from e
            except psycopg.Error as e:
                # Retries exhausted on a transient error => 503: the client may retry later with the same key.
                status = 503 if is_retryable(e) else 500
                raise HTTPException(
                    status_code=status,
                    detail=f"database error {e.sqlstate or ''}".strip(),
                ) from e

        return wrapped


router = APIRouter(route_class=DomainErrorRoute)


@lru_cache
def get_service() -> AuroraOrderService:
    """One service (and one pair of lazy pools) per process, built on the first request."""
    return AuroraOrderService(AuroraRepository(AuroraPools()))


Service = Annotated[AuroraOrderService, Depends(get_service)]


class OrderRequest(BaseModel):
    customer_id: str = Field(min_length=1)
    sku: str = Field(min_length=1)
    quantity: int = Field(gt=0)
    amount_cents: int = Field(ge=0)
    attrs: dict[str, Any] = Field(default_factory=dict)

    def to_command(self, idempotency_key: str | None) -> NewOrder:
        return NewOrder(
            customer_id=self.customer_id,
            sku=self.sku,
            quantity=self.quantity,
            amount_cents=self.amount_cents,
            idempotency_key=idempotency_key,
            attrs=self.attrs,
        )


class StatusRequest(BaseModel):
    status: OrderStatus


class StockRequest(BaseModel):
    on_hand: int = Field(ge=0)


class JobRequest(BaseModel):
    kind: str = Field(min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)


def _out(obj: Any) -> Any:
    """Dataclasses (and lists of them) -> JSON-ready dicts."""
    if isinstance(obj, list):
        return [jsonable_encoder(asdict(o)) for o in obj]
    return jsonable_encoder(asdict(obj))


# ---------------------------------------------------------------- orders


@router.post("/orders", status_code=201)
def create_order(
    svc: Service,
    body: OrderRequest,
    response: Response,
    idempotency_key: str | None = Header(default=None),
) -> dict[str, Any]:
    if idempotency_key is None:
        order = svc.create_order_once(body.to_command(None))
    else:
        order = svc.place_order(body.to_command(idempotency_key))
    response.headers["ETag"] = f'"{order.version}"'
    return _out(order)


@router.post("/orders/credit-checked", status_code=201)
def create_order_within_credit_limit(
    svc: Service,
    body: OrderRequest,
    response: Response,
    idempotency_key: str = Header(),
) -> dict[str, Any]:
    order = svc.place_order_within_credit_limit(body.to_command(idempotency_key))
    response.headers["ETag"] = f'"{order.version}"'
    return _out(order)


@router.get("/orders/{order_id}")
def get_order(
    svc: Service,
    order_id: int,
    strong: bool = False,
    min_version: int | None = None,
) -> dict[str, Any]:
    return _out(svc.get_order(order_id, strong=strong, min_version=min_version))


@router.patch("/orders/{order_id}/status")
def change_status(
    svc: Service,
    order_id: int,
    body: StatusRequest,
    response: Response,
    if_match: str = Header(),
) -> dict[str, Any]:
    order = svc.change_status(order_id, int(if_match.strip().strip('"')), body.status)
    response.headers["ETag"] = f'"{order.version}"'
    return _out(order)


@router.delete("/orders/{order_id}", status_code=204)
def delete_order(svc: Service, order_id: int) -> Response:
    if not svc.delete_order(order_id):
        raise OrderNotFound(f"order {order_id} not found")
    return Response(status_code=204)


@router.post("/orders/import")
def import_orders(svc: Service, rows: list[OrderRequest]) -> dict[str, Any]:
    return _out(svc.import_orders([r.to_command(None) for r in rows]))


@router.post("/orders/search")
def search_orders(
    svc: Service, containment: dict[str, Any], limit: int = 20
) -> list[dict[str, Any]]:
    return _out(svc.search(containment, limit))


@router.get("/customers/{customer_id}/orders")
def list_orders_keyset(
    svc: Service, customer_id: str, cursor: str | None = None, size: int = 20
) -> dict[str, Any]:
    return _out(svc.list_by_keyset(customer_id, cursor, size))


@router.get("/customers/{customer_id}/orders/offset")
def list_orders_offset(
    svc: Service, customer_id: str, page: int = 0, size: int = 20
) -> dict[str, Any]:
    return _out(svc.list_by_offset(customer_id, page, size))


@router.get("/customers/{customer_id}/summary")
def customer_summary(svc: Service, customer_id: str) -> dict[str, Any]:
    return _out(svc.customer_summary(customer_id))


# ---------------------------------------------------------------- inventory


@router.put("/inventory/{sku}")
def restock(svc: Service, sku: str, body: StockRequest) -> dict[str, Any]:
    return _out(svc.restock(sku, body.on_hand))


# ---------------------------------------------------------------- jobs


@router.post("/jobs", status_code=201)
def enqueue_job(svc: Service, body: JobRequest) -> dict[str, int]:
    return {"id": svc.enqueue_job(body.kind, body.payload)}


@router.post("/jobs/claim")
def claim_jobs(
    svc: Service, worker_id: str, limit: int = 10, lease_seconds: int = 60
) -> list[dict[str, Any]]:
    return _out(svc.claim_jobs(worker_id, limit, timedelta(seconds=lease_seconds)))


@router.post("/jobs/{job_id}/complete", status_code=204)
def complete_job(svc: Service, job_id: int, worker_id: str) -> Response:
    svc.complete_job(job_id, worker_id)
    return Response(status_code=204)


@router.post("/jobs/{job_id}/fail", status_code=204)
def fail_job(svc: Service, job_id: int, worker_id: str, error: str = "") -> Response:
    svc.fail_job(job_id, worker_id, error)
    return Response(status_code=204)


@router.post("/jobs/requeue-expired")
def requeue_expired_jobs(svc: Service) -> dict[str, int]:
    return {"requeued": svc.requeue_expired_jobs()}


# ---------------------------------------------------------------- ops


@router.get("/replica-lag")
def replica_lag(svc: Service) -> dict[str, int]:
    return svc.replica_lag()


@router.post("/admin/schema", status_code=204)
def apply_schema(svc: Service) -> Response:
    svc.apply_schema()
    return Response(status_code=204)
