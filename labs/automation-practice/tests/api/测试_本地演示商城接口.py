from __future__ import annotations

import os
from uuid import uuid4

import pytest

from qa_learning.api.响应数据契约 import (
    DEMO_SHOP_ORDER_SCHEMA,
    DEMO_SHOP_PRODUCT_LIST_SCHEMA,
)
from qa_learning.api.本地演示商城接口 import DemoShopApi


def _require_demo_shop() -> None:
    if not os.getenv("DEMO_SHOP_URL"):
        pytest.skip("set DEMO_SHOP_URL after starting labs/demo-shop to run this local exercise")


@pytest.mark.api
@pytest.mark.smoke
def test_local_demo_shop_product_contract() -> None:
    _require_demo_shop()
    api = DemoShopApi.from_env()
    try:
        response = api.list_products(keyword="马克杯", limit=5)

        api.client.assert_status(response, 200)
        products = api.client.assert_json_schema(
            response,
            DEMO_SHOP_PRODUCT_LIST_SCHEMA,
        )
        assert [product["name"] for product in products] == ["星光马克杯"]
    finally:
        api.client.close()


@pytest.mark.api
@pytest.mark.challenge
def test_local_demo_shop_idempotent_order() -> None:
    _require_demo_shop()
    api = DemoShopApi.from_env()
    payload = {"items": [{"product_id": 1, "quantity": 2}]}
    key = str(uuid4())
    try:
        first_response = api.create_order(payload, idempotency_key=key)
        second_response = api.create_order(payload, idempotency_key=key)

        api.client.assert_status(first_response, 201)
        api.client.assert_status(second_response, 201)
        first = api.client.assert_json_schema(
            first_response,
            DEMO_SHOP_ORDER_SCHEMA,
        )
        second = api.client.assert_json_schema(
            second_response,
            DEMO_SHOP_ORDER_SCHEMA,
        )
        assert first["id"] == second["id"]
        assert first["total_cents"] == 5180
    finally:
        api.client.close()
