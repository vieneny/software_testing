"""JSON Schemas shared by the API service objects and practice tests."""

from __future__ import annotations

from typing import Any

JSON_SCHEMA: dict[str, Any] = {"$schema": "https://json-schema.org/draft/2020-12/schema"}

JSONPLACEHOLDER_POST_SCHEMA: dict[str, Any] = {
    **JSON_SCHEMA,
    "type": "object",
    "required": ["id", "userId", "title", "body"],
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "userId": {"type": "integer", "minimum": 1},
        "title": {"type": "string"},
        "body": {"type": "string"},
    },
    "additionalProperties": False,
}

JSONPLACEHOLDER_POST_LIST_SCHEMA: dict[str, Any] = {
    **JSON_SCHEMA,
    "type": "array",
    "items": JSONPLACEHOLDER_POST_SCHEMA,
}

RESTFUL_BOOKER_AUTH_SCHEMA: dict[str, Any] = {
    **JSON_SCHEMA,
    "type": "object",
    "required": ["token"],
    "properties": {"token": {"type": "string", "minLength": 1}},
    "additionalProperties": False,
}

RESTFUL_BOOKER_BOOKING_SCHEMA: dict[str, Any] = {
    **JSON_SCHEMA,
    "type": "object",
    "required": [
        "firstname",
        "lastname",
        "totalprice",
        "depositpaid",
        "bookingdates",
        "additionalneeds",
    ],
    "properties": {
        "firstname": {"type": "string", "minLength": 1},
        "lastname": {"type": "string", "minLength": 1},
        "totalprice": {"type": "integer", "minimum": 0},
        "depositpaid": {"type": "boolean"},
        "bookingdates": {
            "type": "object",
            "required": ["checkin", "checkout"],
            "properties": {
                "checkin": {"type": "string", "format": "date"},
                "checkout": {"type": "string", "format": "date"},
            },
            "additionalProperties": False,
        },
        "additionalneeds": {"type": "string"},
    },
    "additionalProperties": False,
}

RESTFUL_BOOKER_CREATE_SCHEMA: dict[str, Any] = {
    **JSON_SCHEMA,
    "type": "object",
    "required": ["bookingid", "booking"],
    "properties": {
        "bookingid": {"type": "integer", "minimum": 1},
        "booking": RESTFUL_BOOKER_BOOKING_SCHEMA,
    },
    "additionalProperties": False,
}

DEMO_SHOP_PRODUCT_SCHEMA: dict[str, Any] = {
    **JSON_SCHEMA,
    "type": "object",
    "required": ["id", "name", "price_cents", "stock"],
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "name": {"type": "string", "minLength": 1},
        "price_cents": {"type": "integer", "minimum": 0},
        "stock": {"type": "integer", "minimum": 0},
    },
    "additionalProperties": False,
}

DEMO_SHOP_PRODUCT_LIST_SCHEMA: dict[str, Any] = {
    **JSON_SCHEMA,
    "type": "array",
    "minItems": 1,
    "items": DEMO_SHOP_PRODUCT_SCHEMA,
}

DEMO_SHOP_ORDER_SCHEMA: dict[str, Any] = {
    **JSON_SCHEMA,
    "type": "object",
    "required": ["id", "status", "items", "total_cents"],
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "status": {"const": "created"},
        "items": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["product_id", "quantity", "unit_price_cents"],
                "properties": {
                    "product_id": {"type": "integer", "minimum": 1},
                    "quantity": {"type": "integer", "minimum": 1},
                    "unit_price_cents": {"type": "integer", "minimum": 0},
                },
                "additionalProperties": False,
            },
        },
        "total_cents": {"type": "integer", "minimum": 0},
    },
    "additionalProperties": False,
}
