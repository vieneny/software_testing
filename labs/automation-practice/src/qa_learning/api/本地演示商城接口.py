"""Client for the repository's local, fully synthetic Demo Shop service."""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any

import requests

from qa_learning.api.接口客户端 import ApiClient


class DemoShopApi:
    def __init__(self, client: ApiClient) -> None:
        self.client = client

    @classmethod
    def from_env(cls) -> DemoShopApi:
        base_url = os.getenv("DEMO_SHOP_URL", "http://127.0.0.1:8000")
        return cls(ApiClient(base_url))

    def health(self) -> requests.Response:
        return self.client.get("/health")

    def list_products(
        self,
        *,
        keyword: str | None = None,
        limit: int | None = None,
    ) -> requests.Response:
        params = {
            key: value
            for key, value in {"keyword": keyword, "limit": limit}.items()
            if value is not None
        }
        return self.client.get("/api/products", params=params)

    def get_product(self, product_id: int) -> requests.Response:
        return self.client.get(f"/api/products/{product_id}")

    def create_order(
        self,
        payload: Mapping[str, Any],
        *,
        idempotency_key: str,
    ) -> requests.Response:
        return self.client.post(
            "/api/orders",
            json=dict(payload),
            headers={"Idempotency-Key": idempotency_key},
        )

    def get_order(self, order_id: int) -> requests.Response:
        return self.client.get(f"/api/orders/{order_id}")
