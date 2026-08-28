"""Service object for the public Restful Booker practice API."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import requests

from qa_learning.api.接口客户端 import ApiClient


class RestfulBookerApi:
    """Expose the booking lifecycle while leaving assertions in the tests."""

    def __init__(self, client: ApiClient) -> None:
        self.client = client

    def authenticate(
        self,
        *,
        username: str = "admin",
        password: str = "password123",
    ) -> requests.Response:
        return self.client.post(
            "/auth",
            json={"username": username, "password": password},
        )

    def create_booking(self, booking: Mapping[str, Any]) -> requests.Response:
        return self.client.post("/booking", json=dict(booking))

    def get_booking(self, booking_id: int) -> requests.Response:
        return self.client.get(f"/booking/{booking_id}")

    def find_bookings(
        self,
        *,
        firstname: str | None = None,
        lastname: str | None = None,
    ) -> requests.Response:
        params = {
            key: value
            for key, value in {
                "firstname": firstname,
                "lastname": lastname,
            }.items()
            if value is not None
        }
        return self.client.get("/booking", params=params)

    def update_booking(
        self,
        booking_id: int,
        booking: Mapping[str, Any],
        *,
        token: str,
    ) -> requests.Response:
        return self.client.put(
            f"/booking/{booking_id}",
            json=dict(booking),
            headers=self._token_cookie(token),
        )

    def patch_booking(
        self,
        booking_id: int,
        changes: Mapping[str, Any],
        *,
        token: str,
    ) -> requests.Response:
        return self.client.patch(
            f"/booking/{booking_id}",
            json=dict(changes),
            headers=self._token_cookie(token),
        )

    def delete_booking(self, booking_id: int, *, token: str) -> requests.Response:
        return self.client.delete(
            f"/booking/{booking_id}",
            headers=self._token_cookie(token),
        )

    @staticmethod
    def _token_cookie(token: str) -> dict[str, str]:
        return {"Cookie": f"token={token}"}
