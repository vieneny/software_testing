"""Service object for the public JSONPlaceholder learning API."""

from __future__ import annotations

from typing import Any

import requests

from qa_learning.api.接口客户端 import ApiClient


class JsonPlaceholderApi:
    """Business-readable operations without hiding HTTP responses."""

    def __init__(self, client: ApiClient) -> None:
        self.client = client

    def list_posts(self, *, user_id: int | None = None) -> requests.Response:
        params = {"userId": user_id} if user_id is not None else None
        return self.client.get("/posts", params=params)

    def get_post(self, post_id: int) -> requests.Response:
        return self.client.get(f"/posts/{post_id}")

    def list_post_comments(self, post_id: int) -> requests.Response:
        return self.client.get(f"/posts/{post_id}/comments")

    def create_post(
        self,
        *,
        user_id: int,
        title: str,
        body: str,
    ) -> requests.Response:
        payload: dict[str, Any] = {
            "userId": user_id,
            "title": title,
            "body": body,
        }
        return self.client.post("/posts", json=payload)
