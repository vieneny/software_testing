import re
from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import FastAPI, Request, Response

REQUEST_ID_HEADER = "X-Request-ID"
TRACE_ID_HEADER = "X-Trace-ID"
_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")


def normalize_request_id(value: str | None) -> str | None:
    if value is None or _REQUEST_ID_PATTERN.fullmatch(value) is None:
        return None
    return value


def resolve_request_id(request: Request) -> str:
    return (
        normalize_request_id(request.headers.get(REQUEST_ID_HEADER))
        or normalize_request_id(request.headers.get(TRACE_ID_HEADER))
        or str(uuid4())
    )


def get_request_id(request: Request) -> str:
    request_id = getattr(request.state, "request_id", None)
    return normalize_request_id(request_id) or resolve_request_id(request)


def register_request_id_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def attach_request_id(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = resolve_request_id(request)
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        response.headers[TRACE_ID_HEADER] = request_id
        return response
