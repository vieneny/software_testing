from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest
import requests

from qa_learning.api.公开预订服务接口 import RestfulBookerApi
from qa_learning.api.响应数据契约 import (
    RESTFUL_BOOKER_AUTH_SCHEMA,
    RESTFUL_BOOKER_BOOKING_SCHEMA,
    RESTFUL_BOOKER_CREATE_SCHEMA,
)
from qa_learning.api.接口客户端 import ApiClient
from qa_learning.运行配置 import Settings


def _synthetic_booking(run_id: str) -> dict[str, Any]:
    return {
        "firstname": f"Learn{run_id}",
        "lastname": "Tester",
        "totalprice": 321,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2030-04-10",
            "checkout": "2030-04-12",
        },
        "additionalneeds": "Synthetic breakfast",
    }


@pytest.mark.api
@pytest.mark.external
@pytest.mark.e2e
def test_restful_booker_authenticated_crud_lifecycle(
    settings: Settings,
    public_api_guard: None,
) -> None:
    run_id = uuid4().hex[:8]
    booking = _synthetic_booking(run_id)
    booking_id: int | None = None
    token: str | None = None
    deleted = False

    with ApiClient(settings.restful_booker_url) as client:
        api = RestfulBookerApi(client)
        try:
            auth_response = api.authenticate()
            client.assert_status(auth_response, 200)
            token = client.assert_json_schema(
                auth_response,
                RESTFUL_BOOKER_AUTH_SCHEMA,
            )["token"]

            create_response = api.create_booking(booking)
            client.assert_status(create_response, 200)
            created = client.assert_json_schema(
                create_response,
                RESTFUL_BOOKER_CREATE_SCHEMA,
            )
            booking_id = created["bookingid"]
            assert created["booking"] == booking

            query_response = api.get_booking(booking_id)
            client.assert_status(query_response, 200)
            queried = client.assert_json_schema(
                query_response,
                RESTFUL_BOOKER_BOOKING_SCHEMA,
            )
            assert queried == booking

            updated_needs = f"Synthetic late checkout {run_id}"
            patch_response = api.patch_booking(
                booking_id,
                {"additionalneeds": updated_needs},
                token=token,
            )
            client.assert_status(patch_response, 200)
            patched = client.assert_json_schema(
                patch_response,
                RESTFUL_BOOKER_BOOKING_SCHEMA,
            )
            assert patched["additionalneeds"] == updated_needs
            assert patched["firstname"] == booking["firstname"]

            delete_response = api.delete_booking(booking_id, token=token)
            client.assert_status(delete_response, 201)
            deleted = True

            missing_response = api.get_booking(booking_id)
            client.assert_status(missing_response, 404)
        finally:
            if booking_id is not None and token is not None and not deleted:
                try:
                    api.delete_booking(booking_id, token=token)
                except requests.RequestException:
                    # Cleanup is best effort and must not hide the original failure.
                    pass
