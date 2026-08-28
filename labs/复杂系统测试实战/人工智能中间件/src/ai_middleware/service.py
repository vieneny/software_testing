"""Provider 调用编排：统一超时、有限重试与错误语义。"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from ai_middleware.config import Settings
from ai_middleware.models import ExecutionPolicy, ProviderMetadata
from ai_middleware.providers.base import (
    AIProvider,
    ProviderError,
    ProviderTransientError,
    ProviderUnavailableError,
)


class MiddlewareError(RuntimeError):
    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        retryable: bool,
        details: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.retryable = retryable
        self.details = details or {}


@dataclass(frozen=True, slots=True)
class ProviderCallResult[ResultT]:
    value: ResultT
    metadata: ProviderMetadata


class AIService:
    def __init__(self, provider: AIProvider, settings: Settings) -> None:
        self.provider = provider
        self.settings = settings

    async def execute[ResultT](
        self,
        operation: Callable[[], Awaitable[ResultT]],
        policy: ExecutionPolicy,
    ) -> ProviderCallResult[ResultT]:
        timeout_ms = (
            policy.timeout_ms
            if policy.timeout_ms is not None
            else self.settings.default_timeout_ms
        )
        max_retries = (
            policy.max_retries
            if policy.max_retries is not None
            else self.settings.default_max_retries
        )
        total_attempts = max_retries + 1

        for attempt in range(1, total_attempts + 1):
            try:
                value = await asyncio.wait_for(
                    operation(),
                    timeout=timeout_ms / 1000,
                )
                return ProviderCallResult(
                    value=value,
                    metadata=ProviderMetadata(
                        name=self.provider.name,
                        model=self.provider.model,
                        version=self.provider.version,
                        attempts=attempt,
                    ),
                )
            except TimeoutError as exc:
                if attempt >= total_attempts:
                    raise MiddlewareError(
                        status_code=504,
                        code="provider_timeout",
                        message="AI Provider 在约定时间内未返回",
                        retryable=True,
                        details={
                            "timeout_ms": timeout_ms,
                            "attempts": attempt,
                        },
                    ) from exc
            except ProviderTransientError as exc:
                if attempt >= total_attempts:
                    raise MiddlewareError(
                        status_code=503,
                        code="provider_temporarily_unavailable",
                        message="AI Provider 暂时不可用",
                        retryable=True,
                        details={"attempts": attempt},
                    ) from exc
            except ProviderUnavailableError as exc:
                raise MiddlewareError(
                    status_code=503,
                    code="provider_unavailable",
                    message=str(exc),
                    retryable=False,
                ) from exc
            except ProviderError as exc:
                raise MiddlewareError(
                    status_code=502,
                    code="provider_error",
                    message="AI Provider 返回不可恢复错误",
                    retryable=False,
                ) from exc

            # 只有明确的临时错误或超时才会走到这里；短退避避免放大故障。
            await asyncio.sleep(min(0.05 * 2 ** (attempt - 1), 0.2))

        raise AssertionError("retry loop must return or raise")
