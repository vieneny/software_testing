"""A tiny in-memory shop API for the repository's public learning labs.

The names, prices, rules and data in this module are entirely fictional. The
application is intentionally small: learners can focus on test design and test
engineering instead of infrastructure setup.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Query, Response, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field


app = FastAPI(
    title="Demo Shop API",
    version="1.0.0",
    description="Synthetic API used by the software-testing learning repository.",
)

STATIC_DIR = Path(__file__).parent / "static"

PRODUCTS = {
    1: {"id": 1, "name": "云朵笔记本", "price_cents": 2590, "stock": 20},
    2: {"id": 2, "name": "星光马克杯", "price_cents": 3900, "stock": 8},
    3: {"id": 3, "name": "旅行贴纸包", "price_cents": 1200, "stock": 50},
}


class Product(BaseModel):
    id: int
    name: str
    price_cents: int = Field(ge=0)
    stock: int = Field(ge=0)


class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, le=10)


class OrderCreate(BaseModel):
    items: list[OrderItemIn] = Field(min_length=1, max_length=20)


class OrderItemOut(BaseModel):
    product_id: int
    quantity: int
    unit_price_cents: int


class Order(BaseModel):
    id: int
    status: str
    items: list[OrderItemOut]
    total_cents: int


_order_ids = itertools.count(1001)
_orders: dict[int, Order] = {}
_idempotency_records: dict[str, tuple[str, int]] = {}


def _payload_fingerprint(payload: OrderCreate) -> str:
    normalized = json.dumps(
        payload.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "演示商城首页.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/products", response_model=list[Product])
def list_products(
    response: Response,
    keyword: str | None = Query(default=None, max_length=50),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[Product]:
    response.headers["Cache-Control"] = "no-store"
    products = [Product(**item) for item in PRODUCTS.values()]
    if keyword:
        normalized_keyword = keyword.casefold().strip()
        products = [
            product
            for product in products
            if normalized_keyword in product.name.casefold()
        ]
    return products[:limit]


@app.get("/api/products/{product_id}", response_model=Product)
def get_product(product_id: int) -> Product:
    product = PRODUCTS.get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="product_not_found")
    return Product(**product)


@app.post("/api/orders", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    idempotency_key: str = Header(
        min_length=8, max_length=128, alias="Idempotency-Key"
    ),
) -> Order:
    fingerprint = _payload_fingerprint(payload)
    previous = _idempotency_records.get(idempotency_key)
    if previous:
        previous_fingerprint, order_id = previous
        if previous_fingerprint != fingerprint:
            raise HTTPException(
                status_code=409,
                detail="idempotency_key_reused_with_different_payload",
            )
        return _orders[order_id]

    output_items: list[OrderItemOut] = []
    for item in payload.items:
        product = PRODUCTS.get(item.product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="product_not_found")
        if item.quantity > product["stock"]:
            raise HTTPException(status_code=409, detail="insufficient_stock")
        output_items.append(
            OrderItemOut(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price_cents=product["price_cents"],
            )
        )

    order_id = next(_order_ids)
    total_cents = sum(
        item.quantity * item.unit_price_cents for item in output_items
    )
    order = Order(
        id=order_id,
        status="created",
        items=output_items,
        total_cents=total_cents,
    )
    _orders[order_id] = order
    _idempotency_records[idempotency_key] = (fingerprint, order_id)
    return order


@app.get("/api/orders/{order_id}", response_model=Order)
def get_order(order_id: int) -> Order:
    order = _orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="order_not_found")
    return order
