from typing import Any
from uuid import uuid4

import httpx

from app.application.ports.ai_gateway import AIGateway, AISummary
from app.core.errors import UpstreamError
from app.core.request_id import normalize_request_id

AI_TITLE_MAX_CHARS = 300
AI_CONTENT_MAX_CHARS = 10_000
AI_ANSWER_MAX_COUNT = 100
AI_ANSWER_MAX_CHARS = 5_000
AI_PAYLOAD_MAX_CHARS = 20_000
AI_SUMMARY_MAX_CHARS = 10_000
AI_MODEL_MAX_CHARS = 200
AI_RISK_HINT_MAX_COUNT = 20
AI_RISK_HINT_MAX_CHARS = 500


def build_summary_payload(
    *,
    title: str,
    content: str,
    answers: list[str],
) -> dict[str, Any]:
    """按中间件契约创建只用于 AI 的确定性前缀副本。

    Python ``len`` 与 Pydantic 对字符串的长度校验都按 Unicode 码点计算，
    因此这里不按 UTF-8 字节截断。问题标题和正文优先于按时间排序的回答。
    """
    ai_title = title[:AI_TITLE_MAX_CHARS]
    ai_content = content[:AI_CONTENT_MAX_CHARS]
    remaining = AI_PAYLOAD_MAX_CHARS - len(ai_title) - len(ai_content)
    ai_answers: list[str] = []

    for answer in answers[:AI_ANSWER_MAX_COUNT]:
        if remaining <= 0:
            break
        answer_budget = min(AI_ANSWER_MAX_CHARS, remaining)
        ai_answer = answer[:answer_budget]
        if not ai_answer:
            continue
        ai_answers.append(ai_answer)
        remaining -= len(ai_answer)

    return {
        "title": ai_title,
        "content": ai_content,
        "answers": ai_answers,
    }


def parse_summary_response(data: Any, *, expected_request_id: str) -> AISummary:
    """严格验证 AI 中间件 2xx 响应，禁止隐式类型转换。"""
    if not isinstance(data, dict):
        raise UpstreamError("ai-middleware", "AI 摘要服务返回格式不正确")

    api_version = data.get("api_version")
    response_request_id = data.get("request_id")
    summary = data.get("summary")
    model = data.get("model")
    hints = data.get("risk_hints")
    if (
        api_version != "v1"
        or not isinstance(response_request_id, str)
        or response_request_id != expected_request_id
        or not isinstance(summary, str)
        or not summary.strip()
        or len(summary) > AI_SUMMARY_MAX_CHARS
        or not isinstance(model, str)
        or not model.strip()
        or len(model) > AI_MODEL_MAX_CHARS
        or not isinstance(hints, list)
        or len(hints) > AI_RISK_HINT_MAX_COUNT
    ):
        raise UpstreamError("ai-middleware", "AI 摘要服务返回格式不正确")

    normalized_hints: list[str] = []
    for hint in hints:
        if (
            not isinstance(hint, str)
            or not hint.strip()
            or len(hint) > AI_RISK_HINT_MAX_CHARS
        ):
            raise UpstreamError("ai-middleware", "AI 摘要服务返回格式不正确")
        normalized_hints.append(hint.strip())

    return AISummary(
        summary=summary.strip(),
        risk_hints=normalized_hints,
        model=model.strip(),
    )


class HttpAIGateway(AIGateway):
    def __init__(
        self,
        *,
        base_url: str,
        summary_path: str,
        timeout: float,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.summary_path = summary_path
        self.timeout = timeout
        self.transport = transport

    async def summarize_question(
        self,
        *,
        title: str,
        content: str,
        answers: list[str],
        request_id: str | None = None,
    ) -> AISummary:
        payload = build_summary_payload(title=title, content=content, answers=answers)
        canonical_request_id = normalize_request_id(request_id) or str(uuid4())
        request_headers = {"X-Request-ID": canonical_request_id}
        try:
            async with httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                transport=self.transport,
            ) as client:
                response = await client.post(
                    self.summary_path,
                    json=payload,
                    headers=request_headers,
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise UpstreamError("ai-middleware", "AI 摘要服务暂时不可用") from exc

        try:
            data: Any = response.json()
        except ValueError as exc:
            raise UpstreamError("ai-middleware", "AI 摘要服务返回格式不正确") from exc

        return parse_summary_response(data, expected_request_id=canonical_request_id)
