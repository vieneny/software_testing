from __future__ import annotations

import requests
from jsonschema import validate


PRODUCT_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "price_cents", "stock"],
    "additionalProperties": False,
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "name": {"type": "string", "minLength": 1},
        "price_cents": {"type": "integer", "minimum": 0},
        "stock": {"type": "integer", "minimum": 0},
    },
}


def test_health_endpoint(api: requests.Session, base_url: str) -> None:
    response = api.get(f"{base_url}/health", timeout=3)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_products_matches_contract(
    api: requests.Session, base_url: str
) -> None:
    response = api.get(f"{base_url}/api/products", timeout=3)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert response.headers["cache-control"] == "no-store"
    products = response.json()
    assert products
    for product in products:
        validate(product, PRODUCT_SCHEMA)


def test_keyword_filters_products(api: requests.Session, base_url: str) -> None:
    response = api.get(
        f"{base_url}/api/products", params={"keyword": "马克杯"}, timeout=3
    )

    assert response.status_code == 200
    assert [product["name"] for product in response.json()] == ["星光马克杯"]


def test_unknown_product_returns_stable_error(
    api: requests.Session, base_url: str
) -> None:
    response = api.get(f"{base_url}/api/products/999999", timeout=3)

    assert response.status_code == 404
    assert response.json() == {"detail": "product_not_found"}


def test_limit_rejects_out_of_range_value(
    api: requests.Session, base_url: str
) -> None:
    response = api.get(
        f"{base_url}/api/products", params={"limit": 0}, timeout=3
    )

    assert response.status_code == 422
