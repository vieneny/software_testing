"""Small, deliberately explicit HTTP client used by the API learning track."""

from __future__ import annotations

import json
import logging
from collections.abc import Iterable, Mapping
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests
from jsonschema import ValidationError
from jsonschema.validators import validator_for

Timeout = float | tuple[float, float]

_REDACTED = "***REDACTED***"
_SENSITIVE_KEYS = frozenset(
    {
        "api_key",
        "authorization",
        "cookie",
        "password",
        "proxy_authorization",
        "refresh_token",
        "secret",
        "set_cookie",
        "token",
        "x_api_key",
    }
)


def _normalized_key(value: object) -> str:
    return str(value).strip().lower().replace("-", "_")


def _is_sensitive_key(value: object) -> bool:
    key = _normalized_key(value)
    return (
        key in _SENSITIVE_KEYS
        or key.endswith("_password")
        or key.endswith("_secret")
        or key.endswith("_token")
    )


def redact(value: Any) -> Any:
    """Return a copy suitable for logs and assertion messages."""

    if isinstance(value, Mapping):
        return {
            str(key): _REDACTED if _is_sensitive_key(key) else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, tuple):
        return tuple(redact(item) for item in value)
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def _safe_url(url: str) -> str:
    parts = urlsplit(url)
    safe_query = [
        (key, _REDACTED if _is_sensitive_key(key) else value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
    ]
    return urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urlencode(safe_query), parts.fragment)
    )


def _safe_response_preview(response: requests.Response, limit: int = 800) -> str:
    try:
        payload = redact(response.json())
    except ValueError:
        return f"<non-JSON response omitted; {len(response.content)} bytes>"

    rendered = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if len(rendered) <= limit:
        return rendered
    return f"{rendered[:limit]}…"


class ApiClient:
    """A thin requests wrapper that keeps test infrastructure behaviour visible.

    The client intentionally does not call ``raise_for_status`` and does not
    retry automatically. API tests need to inspect negative responses, and a
    hidden retry can turn a useful failure into a false pass.
    """

    def __init__(
        self,
        base_url: str,
        *,
        timeout: Timeout = (3.05, 10.0),
        session: requests.Session | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        if not base_url.strip():
            raise ValueError("base_url must not be empty")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        self.logger = logger or logging.getLogger("qa_learning.api")

    def __enter__(self) -> ApiClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        self.session.close()

    def request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> requests.Response:
        if kwargs.get("timeout", self.timeout) is None:
            raise ValueError("timeout=None is not allowed; choose an explicit timeout")
        kwargs.setdefault("timeout", self.timeout)

        url = self._build_url(path)
        request_summary = {
            "headers": redact(kwargs.get("headers", {})),
            "json": redact(kwargs.get("json")),
            "params": redact(kwargs.get("params", {})),
        }
        if "data" in kwargs:
            request_summary["data"] = redact(kwargs["data"])
        if "files" in kwargs:
            request_summary["files"] = "<file content omitted>"

        self.logger.info(
            "HTTP request method=%s url=%s details=%s",
            method.upper(),
            _safe_url(url),
            request_summary,
        )
        response = self.session.request(method=method, url=url, **kwargs)
        self.logger.info(
            "HTTP response method=%s url=%s status=%s body=%s",
            method.upper(),
            _safe_url(response.url or url),
            response.status_code,
            _safe_response_preview(response),
        )
        return response

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("DELETE", path, **kwargs)

    def assert_status(
        self,
        response: requests.Response,
        expected: int | Iterable[int],
    ) -> requests.Response:
        expected_values = (
            {expected} if isinstance(expected, int) else {int(item) for item in expected}
        )
        if response.status_code not in expected_values:
            expected_text = ", ".join(str(item) for item in sorted(expected_values))
            raise AssertionError(
                "unexpected HTTP status: "
                f"expected one of [{expected_text}], got {response.status_code}; "
                f"url={_safe_url(response.url or '<unknown>')}; "
                f"body={_safe_response_preview(response)}"
            )
        return response

    def assert_json_schema(
        self,
        response: requests.Response,
        schema: Mapping[str, Any],
    ) -> Any:
        try:
            payload = response.json()
        except ValueError as error:
            raise AssertionError(
                f"response from {_safe_url(response.url or '<unknown>')} is not valid JSON"
            ) from error

        validator_class = validator_for(schema)
        validator_class.check_schema(schema)
        validator = validator_class(schema)
        errors = sorted(validator.iter_errors(payload), key=lambda item: list(item.path))
        if errors:
            first_error: ValidationError = errors[0]
            path = ".".join(str(item) for item in first_error.absolute_path) or "<root>"
            raise AssertionError(
                "JSON schema validation failed: "
                f"path={path}; message={first_error.message}; "
                f"url={_safe_url(response.url or '<unknown>')}"
            )
        return payload

    def _build_url(self, path: str) -> str:
        if path.startswith(("http://", "https://")):
            raise ValueError("path must be relative; configure a separate ApiClient")
        return f"{self.base_url}/{path.lstrip('/')}"
