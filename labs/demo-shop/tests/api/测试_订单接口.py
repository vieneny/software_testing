from __future__ import annotations

from uuid import uuid4

import requests


def _create_order(
    api: requests.Session,
    base_url: str,
    payload: dict[str, object],
    idempotency_key: str,
) -> requests.Response:
    return api.post(
        f"{base_url}/api/orders",
        json=payload,
        headers={"Idempotency-Key": idempotency_key},
        timeout=3,
    )


def test_create_then_query_order(api: requests.Session, base_url: str) -> None:
    payload = {"items": [{"product_id": 1, "quantity": 2}]}
    response = _create_order(api, base_url, payload, str(uuid4()))

    assert response.status_code == 201
    order = response.json()
    assert order["status"] == "created"
    assert order["total_cents"] == 5180

    query_response = api.get(f"{base_url}/api/orders/{order['id']}", timeout=3)
    assert query_response.status_code == 200
    assert query_response.json() == order


def test_same_idempotency_key_returns_same_order(
    api: requests.Session, base_url: str
) -> None:
    key = str(uuid4())
    payload = {"items": [{"product_id": 2, "quantity": 1}]}

    first = _create_order(api, base_url, payload, key)
    second = _create_order(api, base_url, payload, key)

    assert first.status_code == second.status_code == 201
    assert first.json()["id"] == second.json()["id"]


def test_reusing_key_with_different_payload_is_rejected(
    api: requests.Session, base_url: str
) -> None:
    key = str(uuid4())
    first = _create_order(
        api, base_url, {"items": [{"product_id": 1, "quantity": 1}]}, key
    )
    second = _create_order(
        api, base_url, {"items": [{"product_id": 1, "quantity": 2}]}, key
    )

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["detail"] == "idempotency_key_reused_with_different_payload"


def test_quantity_above_stock_is_rejected(
    api: requests.Session, base_url: str
) -> None:
    response = _create_order(
        api,
        base_url,
        {"items": [{"product_id": 2, "quantity": 9}]},
        str(uuid4()),
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "insufficient_stock"}


def test_invalid_quantity_is_rejected_by_schema(
    api: requests.Session, base_url: str
) -> None:
    response = _create_order(
        api,
        base_url,
        {"items": [{"product_id": 1, "quantity": 0}]},
        str(uuid4()),
    )

    assert response.status_code == 422


def test_missing_idempotency_key_is_rejected(
    api: requests.Session, base_url: str
) -> None:
    response = api.post(
        f"{base_url}/api/orders",
        json={"items": [{"product_id": 1, "quantity": 1}]},
        timeout=3,
    )

    assert response.status_code == 422
