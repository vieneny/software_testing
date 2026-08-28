from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.request_id import get_request_id


class AppError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class NotFoundError(AppError):
    def __init__(self, resource: str, resource_id: str) -> None:
        super().__init__(
            code="resource_not_found",
            message=f"{resource}不存在",
            status_code=404,
            details={"resource": resource, "resource_id": resource_id},
        )


class ConflictError(AppError):
    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(code=code, message=message, status_code=409, details=details)


class UpstreamError(AppError):
    def __init__(self, service: str, message: str) -> None:
        super().__init__(
            code="upstream_service_error",
            message=message,
            status_code=502,
            details={"service": service},
        )


def _error_body(
    code: str,
    message: str,
    request_id: str,
    details: dict[str, Any] | list[Any] | None = None,
) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
            "request_id": request_id,
            "trace_id": request_id,
        }
    }


def _safe_validation_details(exc: RequestValidationError) -> list[dict[str, Any]]:
    """保留可定位字段，避免把用户正文、昵称或请求头原样回显。"""
    return [
        {
            "type": item.get("type", "validation_error"),
            "loc": list(item.get("loc", ())),
            "msg": item.get("msg", "输入不合法"),
        }
        for item in exc.errors()
    ]


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        request_id = get_request_id(request)
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.code, exc.message, request_id, exc.details),
            headers={"X-Request-ID": request_id, "X-Trace-ID": request_id},
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        request_id = get_request_id(request)
        return JSONResponse(
            status_code=422,
            content=_error_body(
                "request_validation_failed",
                "请求参数校验失败",
                request_id,
                _safe_validation_details(exc),
            ),
            headers={"X-Request-ID": request_id, "X-Trace-ID": request_id},
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        request_id = get_request_id(request)
        message = "请求的接口不存在" if exc.status_code == 404 else "HTTP 请求处理失败"
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(
                "route_not_found" if exc.status_code == 404 else "http_error",
                message,
                request_id,
            ),
            headers={"X-Request-ID": request_id, "X-Trace-ID": request_id},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, _: Exception) -> JSONResponse:
        request_id = get_request_id(request)
        return JSONResponse(
            status_code=500,
            content=_error_body(
                "internal_server_error",
                "服务内部错误",
                request_id,
            ),
            headers={"X-Request-ID": request_id, "X-Trace-ID": request_id},
        )
