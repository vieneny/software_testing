from __future__ import annotations

import json
import logging
from typing import Any

import pytest
import requests

from qa_learning.api.接口客户端 import ApiClient


def _response(
    *,
    method: str = "GET",
    url: str = "https://example.invalid/resource",
    status: int = 200,
    payload: Any = None,
) -> requests.Response:
    response = requests.Response()
    response.status_code = status
    response.url = url
    response.headers["Content-Type"] = "application/json"
    response._content = json.dumps(payload).encode("utf-8")
    response.request = requests.Request(method, url).prepare()
    return response


class RecordingSession:
    def __init__(self, response: requests.Response) -> None:
        self.response = response
        self.calls: list[dict[str, Any]] = []
        self.closed = False

    def request(self, **kwargs: Any) -> requests.Response:
        self.calls.append(kwargs)
        return self.response

    def close(self) -> None:
        self.closed = True


@pytest.mark.api
def test_client_always_supplies_an_explicit_timeout() -> None:
    session = RecordingSession(_response(payload={"ok": True}))
    client = ApiClient(
        "https://example.invalid",
        timeout=(1.0, 2.0),
        session=session,  # type: ignore[arg-type]
    )

    client.get("/resource")

    assert session.calls[0]["timeout"] == (1.0, 2.0)


@pytest.mark.api
def test_client_rejects_unbounded_timeout() -> None:
    session = RecordingSession(_response(payload={"ok": True}))
    client = ApiClient(
        "https://example.invalid",
        session=session,  # type: ignore[arg-type]
    )

    with pytest.raises(ValueError, match="timeout=None"):
        client.get("/resource", timeout=None)


@pytest.mark.api
def test_logs_redact_request_and_response_secrets(
    caplog: pytest.LogCaptureFixture,
) -> None:
    session = RecordingSession(
        _response(
            payload={
                "access_token": "server-token-value",
                "profile": {"password": "server-password"},
            }
        )
    )
    client = ApiClient(
        "https://example.invalid",
        session=session,  # type: ignore[arg-type]
    )

    with caplog.at_level(logging.INFO, logger="qa_learning.api"):
        client.post(
            "/login",
            headers={
                "Authorization": "Bearer request-token",
                "X-Trace-ID": "visible-trace",
            },
            json={"username": "learner", "password": "request-password"},
        )

    assert "visible-trace" in caplog.text
    assert "request-token" not in caplog.text
    assert "request-password" not in caplog.text
    assert "server-token-value" not in caplog.text
    assert "server-password" not in caplog.text
    assert "***REDACTED***" in caplog.text


@pytest.mark.api
def test_status_failure_is_diagnostic_but_redacted() -> None:
    response = _response(
        status=500,
        payload={"message": "synthetic failure", "token": "do-not-leak"},
    )
    client = ApiClient("https://example.invalid")

    with pytest.raises(AssertionError) as captured:
        client.assert_status(response, {200, 201})

    message = str(captured.value)
    assert "expected one of [200, 201], got 500" in message
    assert "synthetic failure" in message
    assert "do-not-leak" not in message


@pytest.mark.api
def test_schema_assertion_returns_validated_payload() -> None:
    response = _response(payload={"id": 7, "name": "合成商品"})
    schema = {
        "type": "object",
        "required": ["id", "name"],
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
        },
        "additionalProperties": False,
    }
    client = ApiClient("https://example.invalid")

    payload = client.assert_json_schema(response, schema)

    assert payload == {"id": 7, "name": "合成商品"}


@pytest.mark.api
def test_schema_failure_reports_the_json_path() -> None:
    response = _response(payload={"id": "not-an-integer"})
    schema = {
        "type": "object",
        "required": ["id"],
        "properties": {"id": {"type": "integer"}},
    }
    client = ApiClient("https://example.invalid")

    with pytest.raises(AssertionError, match=r"path=id"):
        client.assert_json_schema(response, schema)


@pytest.mark.api
def test_absolute_request_path_is_rejected() -> None:
    client = ApiClient("https://example.invalid")

    with pytest.raises(ValueError, match="path must be relative"):
        client.get("https://different.example.invalid/resource")
