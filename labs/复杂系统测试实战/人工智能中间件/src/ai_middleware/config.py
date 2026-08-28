"""只从环境变量读取配置，不读取业务请求体，也不记录密钥。"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from urllib.parse import urlparse

SUPPORTED_PROVIDERS = {"mock", "openai-compatible"}


def _read_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name, str(default)).strip().lower()
    if raw in {"1", "true", "yes", "on"}:
        return True
    if raw in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} 必须是 true 或 false")


def _read_int(name: str, default: int, minimum: int, maximum: int) -> int:
    raw = os.getenv(name, str(default))
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} 必须是整数") from exc
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} 必须在 {minimum} 到 {maximum} 之间")
    return value


def _read_hosts(raw: str) -> tuple[str, ...]:
    return tuple(sorted({item.strip().lower() for item in raw.split(",") if item.strip()}))


@dataclass(frozen=True, slots=True)
class Settings:
    """应用配置。

    `openai_api_key` 被排除在 repr 之外，避免调试输出意外泄漏。
    """

    provider: str = "mock"
    service_version: str = "0.1.0"
    api_version: str = "v1"
    default_timeout_ms: int = 1500
    default_max_retries: int = 1
    max_input_chars: int = 10_000
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "replace-me"
    openai_api_key: str = field(default="", repr=False)
    openai_allowed_hosts: tuple[str, ...] = ("api.openai.com",)
    openai_network_enabled: bool = False
    openai_timeout_ms: int = 10_000
    openai_max_output_tokens: int = 1_000
    openai_max_response_bytes: int = 1_000_000

    @classmethod
    def from_env(cls) -> Settings:
        settings = cls(
            provider=os.getenv("AI_PROVIDER", "mock").strip().lower(),
            service_version=os.getenv("AI_SERVICE_VERSION", "0.1.0").strip(),
            default_timeout_ms=_read_int("AI_DEFAULT_TIMEOUT_MS", 1500, 100, 30_000),
            default_max_retries=_read_int("AI_DEFAULT_MAX_RETRIES", 1, 0, 3),
            max_input_chars=_read_int("AI_MAX_INPUT_CHARS", 10_000, 100, 100_000),
            openai_base_url=os.getenv(
                "AI_OPENAI_BASE_URL", "https://api.openai.com/v1"
            ).strip(),
            openai_model=os.getenv("AI_OPENAI_MODEL", "replace-me").strip(),
            openai_api_key=os.getenv("AI_OPENAI_API_KEY", ""),
            openai_allowed_hosts=_read_hosts(
                os.getenv("AI_OPENAI_ALLOWED_HOSTS", "api.openai.com")
            ),
            openai_network_enabled=_read_bool(
                "AI_OPENAI_NETWORK_ENABLED",
                False,
            ),
            openai_timeout_ms=_read_int(
                "AI_OPENAI_TIMEOUT_MS",
                10_000,
                100,
                60_000,
            ),
            openai_max_output_tokens=_read_int(
                "AI_OPENAI_MAX_OUTPUT_TOKENS",
                1_000,
                64,
                8_192,
            ),
            openai_max_response_bytes=_read_int(
                "AI_OPENAI_MAX_RESPONSE_BYTES",
                1_000_000,
                1_024,
                5_000_000,
            ),
        )
        settings.validate()
        return settings

    def validate(self) -> None:
        if self.provider not in SUPPORTED_PROVIDERS:
            raise ValueError(
                f"AI_PROVIDER 只支持 {', '.join(sorted(SUPPORTED_PROVIDERS))}"
            )
        if not self.service_version:
            raise ValueError("AI_SERVICE_VERSION 不能为空")
        if self.provider != "openai-compatible":
            return

        parsed = urlparse(self.openai_base_url)
        host = (parsed.hostname or "").lower()
        if parsed.scheme != "https":
            raise ValueError("OpenAI-compatible base URL 必须使用 HTTPS")
        if not host or host not in self.openai_allowed_hosts:
            raise ValueError("OpenAI-compatible host 不在 AI_OPENAI_ALLOWED_HOSTS 中")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("OpenAI-compatible base URL 不允许凭据、查询串或片段")
        if not self.openai_network_enabled:
            return
        if not self.openai_api_key.strip():
            raise ValueError("启用 OpenAI-compatible 网络调用时必须设置 AI_OPENAI_API_KEY")
        if not self.openai_model or self.openai_model == "replace-me":
            raise ValueError("启用 OpenAI-compatible 网络调用时必须设置 AI_OPENAI_MODEL")
