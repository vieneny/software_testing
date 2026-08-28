from __future__ import annotations

from uuid import uuid4

from locust import HttpUser, between, task


class DemoShopUser(HttpUser):
    wait_time = between(0.5, 1.5)

    @task(4)
    def browse_products(self) -> None:
        with self.client.get(
            "/api/products", name="GET /api/products", catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"unexpected status: {response.status_code}")
            elif not response.json():
                response.failure("product list was empty")

    @task(1)
    def create_order(self) -> None:
        self.client.post(
            "/api/orders",
            name="POST /api/orders",
            headers={"Idempotency-Key": str(uuid4())},
            json={"items": [{"product_id": 1, "quantity": 1}]},
        )
