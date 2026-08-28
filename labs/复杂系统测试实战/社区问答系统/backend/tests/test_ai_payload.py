import asyncio
import json

import httpx
import pytest

from app.core.errors import UpstreamError
from app.infrastructure.ai.http_client import (
    AI_ANSWER_MAX_CHARS,
    AI_ANSWER_MAX_COUNT,
    AI_CONTENT_MAX_CHARS,
    AI_MODEL_MAX_CHARS,
    AI_PAYLOAD_MAX_CHARS,
    AI_RISK_HINT_MAX_CHARS,
    AI_RISK_HINT_MAX_COUNT,
    AI_SUMMARY_MAX_CHARS,
    HttpAIGateway,
    build_summary_payload,
)

CONTRACT_REQUEST_ID = "ai-contract-test-001"
VALID_AI_RESPONSE = {
    "api_version": "v1",
    "request_id": CONTRACT_REQUEST_ID,
    "summary": "摘要",
    "risk_hints": [],
    "model": "mock/model",
}


def payload_char_count(payload):
    return (
        len(payload["title"])
        + len(payload["content"])
        + sum(len(item) for item in payload["answers"])
    )


def test_ai_payload_uses_unicode_character_budget_without_changing_source():
    title = "题" * 200
    content = "🧪" * (AI_CONTENT_MAX_CHARS + 1)
    answers = ["答" * (AI_ANSWER_MAX_CHARS + 1), "解" * 5000, "末尾回答"]

    payload = build_summary_payload(title=title, content=content, answers=answers)

    assert len(payload["content"]) == AI_CONTENT_MAX_CHARS
    assert payload["content"] == "🧪" * AI_CONTENT_MAX_CHARS
    assert [len(item) for item in payload["answers"]] == [5000, 4800]
    assert payload["answers"][0] == answers[0][:AI_ANSWER_MAX_CHARS]
    assert payload_char_count(payload) == AI_PAYLOAD_MAX_CHARS
    assert len(content) == AI_CONTENT_MAX_CHARS + 1
    assert len(answers[0]) == AI_ANSWER_MAX_CHARS + 1


def test_ai_payload_keeps_first_one_hundred_answers_in_original_order():
    answers = [f"回答-{index:03d}" for index in range(AI_ANSWER_MAX_COUNT + 1)]

    payload = build_summary_payload(title="测试标题", content="测试正文", answers=answers)

    assert payload["answers"] == answers[:AI_ANSWER_MAX_COUNT]
    assert len(payload["answers"]) == AI_ANSWER_MAX_COUNT
    assert payload_char_count(payload) <= AI_PAYLOAD_MAX_CHARS


def test_ai_payload_drops_answers_when_question_context_uses_total_budget():
    payload = build_summary_payload(
        title="标" * 300,
        content="正" * AI_PAYLOAD_MAX_CHARS,
        answers=["答" * 5000, "解" * 5000, "不应进入 AI 副本"],
    )

    assert len(payload["title"]) == 300
    assert len(payload["content"]) == AI_CONTENT_MAX_CHARS
    assert [len(item) for item in payload["answers"]] == [5000, 4700]
    assert payload_char_count(payload) == AI_PAYLOAD_MAX_CHARS


def test_http_gateway_sends_bounded_payload_and_request_id():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["payload"] = json.loads(request.content)
        captured["request_id"] = request.headers["X-Request-ID"]
        return httpx.Response(
            200,
            json={
                "api_version": "v1",
                "request_id": request.headers["X-Request-ID"],
                "summary": "确定性摘要",
                "risk_hints": [],
                "model": "mock/model",
            },
        )

    gateway = HttpAIGateway(
        base_url="http://ai.test",
        summary_path="/api/v1/forum/summarize",
        timeout=1,
        transport=httpx.MockTransport(handler),
    )
    result = asyncio.run(
        gateway.summarize_question(
            title="题" * 200,
            content="🧪" * 20_000,
            answers=["答" * 6_000, "解" * 6_000],
            request_id="ai-budget-test-001",
        )
    )

    assert result.summary == "确定性摘要"
    assert captured["request_id"] == "ai-budget-test-001"
    assert len(captured["payload"]["content"]) == AI_CONTENT_MAX_CHARS
    assert payload_char_count(captured["payload"]) == AI_PAYLOAD_MAX_CHARS


@pytest.mark.parametrize(
    "upstream_payload",
    [
        [],
        None,
        {},
        {key: value for key, value in VALID_AI_RESPONSE.items() if key != "api_version"},
        {**VALID_AI_RESPONSE, "api_version": "v2"},
        {**VALID_AI_RESPONSE, "api_version": 1},
        {key: value for key, value in VALID_AI_RESPONSE.items() if key != "request_id"},
        {**VALID_AI_RESPONSE, "request_id": "different-request-id"},
        {**VALID_AI_RESPONSE, "request_id": 123},
        {**VALID_AI_RESPONSE, "summary": ""},
        {**VALID_AI_RESPONSE, "summary": "   "},
        {**VALID_AI_RESPONSE, "summary": "S" * (AI_SUMMARY_MAX_CHARS + 1)},
        {**VALID_AI_RESPONSE, "model": ""},
        {**VALID_AI_RESPONSE, "model": 123},
        {**VALID_AI_RESPONSE, "model": "M" * (AI_MODEL_MAX_CHARS + 1)},
        {**VALID_AI_RESPONSE, "risk_hints": "不是列表"},
        {**VALID_AI_RESPONSE, "risk_hints": ["有效", 123]},
        {**VALID_AI_RESPONSE, "risk_hints": [""]},
        {
            **VALID_AI_RESPONSE,
            "risk_hints": ["H" * (AI_RISK_HINT_MAX_CHARS + 1)],
        },
        {
            **VALID_AI_RESPONSE,
            "risk_hints": ["风险"] * (AI_RISK_HINT_MAX_COUNT + 1),
        },
    ],
)
def test_invalid_success_response_becomes_safe_upstream_error(upstream_payload):
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=upstream_payload)

    gateway = HttpAIGateway(
        base_url="http://ai.test",
        summary_path="/api/v1/forum/summarize",
        timeout=1,
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(UpstreamError) as captured:
        asyncio.run(
            gateway.summarize_question(
                title="测试标题",
                content="测试正文内容",
                answers=[],
                request_id=CONTRACT_REQUEST_ID,
            )
        )

    assert captured.value.status_code == 502
    assert captured.value.code == "upstream_service_error"
    assert captured.value.message == "AI 摘要服务返回格式不正确"
    assert repr(upstream_payload) not in str(captured.value)


def test_valid_success_response_is_strictly_normalized():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "api_version": "v1",
                "request_id": request.headers["X-Request-ID"],
                "summary": "  有效摘要  ",
                "risk_hints": ["  并发风险  ", "数据一致性"],
                "model": "  mock/model  ",
                "extra_forward_compatible_field": True,
            },
        )

    gateway = HttpAIGateway(
        base_url="http://ai.test",
        summary_path="/api/v1/forum/summarize",
        timeout=1,
        transport=httpx.MockTransport(handler),
    )
    result = asyncio.run(
        gateway.summarize_question(
            title="测试标题",
            content="测试正文内容",
            answers=[],
            request_id=CONTRACT_REQUEST_ID,
        )
    )

    assert result.summary == "有效摘要"
    assert result.risk_hints == ["并发风险", "数据一致性"]
    assert result.model == "mock/model"
