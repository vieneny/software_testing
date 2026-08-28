import asyncio
import json

import httpx
import pytest
from fastapi.testclient import TestClient

from ai_middleware.app import create_app
from ai_middleware.config import Settings
from ai_middleware.models import (
    Citation,
    ContentAnalysisRequest,
    ContentAnalysisResult,
    KnowledgeAnswerRequest,
    KnowledgeAnswerResult,
    ModerationRequest,
    ModerationResult,
    ReplySuggestionRequest,
    ReplySuggestionResult,
    TicketClassificationRequest,
)
from ai_middleware.providers.base import (
    ProviderError,
    ProviderTransientError,
    ProviderUnavailableError,
)
from ai_middleware.providers.mock import MockProvider
from ai_middleware.providers.openai_compatible import (
    OpenAICompatibleConfig,
    OpenAICompatibleProvider,
)


class FlakyProvider(MockProvider):
    def __init__(self) -> None:
        self.calls = 0

    async def moderate(self, request: ModerationRequest):
        self.calls += 1
        if self.calls == 1:
            raise ProviderTransientError("synthetic transient failure")
        return await super().moderate(request)


class SlowProvider(MockProvider):
    async def classify_ticket(self, request: TicketClassificationRequest):
        await asyncio.sleep(0.2)
        return await super().classify_ticket(request)


class SecondChunkModerationFailureProvider(MockProvider):
    def __init__(self) -> None:
        self.analysis_calls = 0
        self.moderation_calls = 0

    async def analyze_content(self, request: ContentAnalysisRequest):
        self.analysis_calls += 1
        return await super().analyze_content(request)

    async def moderate(self, request: ModerationRequest):
        self.moderation_calls += 1
        if self.moderation_calls == 2:
            raise ProviderTransientError("synthetic second chunk failure")
        return await super().moderate(request)


class ManyCategoryProvider(MockProvider):
    model = "synthetic-model-" + "m" * 500

    async def moderate(self, request: ModerationRequest) -> ModerationResult:
        return ModerationResult(
            allowed=False,
            decision="review",
            risk_score=0.5,
            categories=[
                "a" + "长" * 600,
                *[f"z-category-{index:02d}" for index in range(30)],
                "z-category-00",
            ],
            matched_terms=[],
            reason="纯合成的多类别边界响应",
        )


class ForumTruncationSignalProvider(MockProvider):
    async def analyze_content(
        self, request: ContentAnalysisRequest
    ) -> ContentAnalysisResult:
        result = await super().analyze_content(request)
        return result.model_copy(update={"truncated": True})

    async def moderate(self, request: ModerationRequest) -> ModerationResult:
        return ModerationResult(
            allowed=False,
            decision="review",
            risk_score=0.5,
            categories=["单" * 600],
            matched_terms=[],
            reason="纯合成单项截断信号",
        )


class CustomerBoundaryProvider(ManyCategoryProvider):
    model = "synthetic\u0000model-" + "m" * 500

    async def analyze_content(
        self, request: ContentAnalysisRequest
    ) -> ContentAnalysisResult:
        return ContentAnalysisResult(
            summary="摘" * 3000,
            tags=["合成边界"],
            source_chars=len(request.text),
            truncated=True,
        )

    async def suggest_reply(
        self, request: ReplySuggestionRequest
    ) -> ReplySuggestionResult:
        return ReplySuggestionResult(
            suggestion="回" * 12_000,
            suggested_actions=[
                "动" * 600,
                *[f"合成步骤-{index:02d}" for index in range(30)],
                "合成步骤-00",
            ],
            must_verify=[
                "核" * 600,
                *[f"合成核验-{index:02d}" for index in range(30)],
            ],
            requires_human_review=True,
        )

    async def answer_knowledge(
        self, request: KnowledgeAnswerRequest
    ) -> KnowledgeAnswerResult:
        return KnowledgeAnswerResult(
            answer="纯合成知识回答",
            grounded=True,
            confidence=0.5,
            citations=[
                Citation(source_id="long", title="引" * 600),
                *[
                    Citation(
                        source_id=f"synthetic-{index:02d}",
                        title=f"合成知识-{index:02d}",
                    )
                    for index in range(30)
                ],
            ],
            must_verify=[],
        )


def test_transient_provider_error_is_retried() -> None:
    provider = FlakyProvider()
    app = create_app(settings=Settings(), provider=provider)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/moderation",
            json={
                "text": "公开合成文本",
                "execution": {"timeout_ms": 1000, "max_retries": 1},
            },
        )

    assert response.status_code == 200
    assert response.json()["provider"]["attempts"] == 2
    assert provider.calls == 2


def test_timeout_has_retryable_error_contract() -> None:
    app = create_app(settings=Settings(), provider=SlowProvider())

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post(
            "/api/v1/tickets/classify",
            json={
                "subject": "合成慢请求",
                "content": "这个请求只用于测试超时。",
                "execution": {"timeout_ms": 100, "max_retries": 0},
            },
        )

    assert response.status_code == 504
    body = response.json()
    assert body["error"]["code"] == "provider_timeout"
    assert body["error"]["retryable"] is True
    assert body["error"]["details"] == {"timeout_ms": 100, "attempts": 1}


def test_forum_chunk_failure_returns_no_partial_success() -> None:
    provider = SecondChunkModerationFailureProvider()
    app = create_app(settings=Settings(), provider=provider)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/forum/summarize",
            json={
                "title": "合成多块失败测试",
                "content": "稳" * 10_000,
                "answers": ["第二块合成内容"],
                "execution": {"timeout_ms": 1000, "max_retries": 0},
            },
        )

    assert response.status_code == 503
    body = response.json()
    assert body["error"]["code"] == "provider_temporarily_unavailable"
    assert body["error"]["retryable"] is True
    assert body["error"]["details"] == {
        "attempts": 1,
        "operation": "moderation",
        "chunk_index": 2,
        "chunk_count": 2,
        "partial_result_returned": False,
    }
    assert "summary" not in body
    assert provider.analysis_calls == 2
    assert provider.moderation_calls == 2


def test_forum_many_categories_are_stably_bounded_for_consumer() -> None:
    app = create_app(settings=Settings(), provider=ManyCategoryProvider())
    payload = {
        "title": "多类别边界测试",
        "content": "完全合成且不对应真实业务的数据。",
        "answers": [],
    }

    with TestClient(app) as client:
        first = client.post("/api/v1/forum/summarize", json=payload)
        second = client.post("/api/v1/forum/summarize", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    first_body = first.json()
    second_body = second.json()
    hints = first_body["risk_hints"]
    assert len(hints) == 20
    assert len(set(hints)) == 20
    assert all(1 <= len(hint) <= 500 for hint in hints)
    assert any(len(hint) == 500 for hint in hints)
    assert first_body["processing"]["risk_hints_truncated"] is True
    assert first_body["processing"]["model_truncated"] is True
    assert 1 <= len(first_body["summary"]) <= 10_000
    assert 1 <= len(first_body["model"]) <= 200
    assert 1 <= len(first_body["provider"]["model"]) <= 200
    assert {
        "summary": first_body["summary"],
        "risk_hints": first_body["risk_hints"],
        "model": first_body["model"],
        "provider": first_body["provider"],
        "processing": first_body["processing"],
    } == {
        "summary": second_body["summary"],
        "risk_hints": second_body["risk_hints"],
        "model": second_body["model"],
        "provider": second_body["provider"],
        "processing": second_body["processing"],
    }


def test_forum_provider_truncation_signals_are_preserved() -> None:
    app = create_app(settings=Settings(), provider=ForumTruncationSignalProvider())

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/forum/summarize",
            json={
                "title": "截断信号测试",
                "content": "完全合成的短文本。",
                "answers": [],
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert len(body["risk_hints"]) < 20
    assert any(len(hint) == 500 for hint in body["risk_hints"])
    assert body["processing"]["summary_truncated"] is True
    assert body["processing"]["risk_hints_truncated"] is True


def test_customer_response_is_bounded_for_java_consumer() -> None:
    app = create_app(settings=Settings(), provider=CustomerBoundaryProvider())

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/customer-service/suggest",
            headers={"X-Request-ID": "customer-boundary-001"},
            json={
                "tenant_code": "demo",
                "ticket_id": "SYNTHETIC-BOUNDARY-001",
                "title": "合成客服边界测试",
                "description": "只用于测试消费者契约。",
                "category": "OTHER",
                "priority": "MEDIUM",
                "customer_level": "NORMAL",
                "tone": "professional",
                "language": "zh-CN",
                "knowledge_context": [
                    {
                        "title": "合成知识",
                        "category": "OTHER",
                        "content": "这是一条完全合成的知识内容。",
                    }
                ],
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["request_id"] == "customer-boundary-001"
    assert 1 <= len(body["summary"]) <= 2000
    assert len(body["summary"]) == 2000
    assert 1 <= len(body["suggested_reply"]) <= 10_000
    assert len(body["suggested_reply"]) == 10_000
    assert len(body["risk_flags"]) <= 20
    assert len(set(body["risk_flags"])) == len(body["risk_flags"])
    assert all(1 <= len(item) <= 100 for item in body["risk_flags"])
    assert "HUMAN_REVIEW_REQUIRED" in body["risk_flags"]
    assert "RISK_FLAGS_TRUNCATED" in body["risk_flags"]
    assert len(body["knowledge_references"]) <= 20
    assert len(set(body["knowledge_references"])) == len(
        body["knowledge_references"]
    )
    assert all(1 <= len(item) <= 500 for item in body["knowledge_references"])
    assert len(body["suggested_actions"]) <= 20
    assert all(1 <= len(item) <= 500 for item in body["suggested_actions"])
    assert 1 <= len(body["must_verify"]) <= 20
    assert all(1 <= len(item) <= 500 for item in body["must_verify"])
    assert 1 <= len(body["model"]) <= 200
    assert "\u0000" not in body["model"]


def test_openai_compatible_is_offline_until_explicitly_enabled() -> None:
    provider = OpenAICompatibleProvider(
        OpenAICompatibleConfig(
            base_url="https://api.openai.com/v1",
            model="placeholder",
            api_key="secret-not-for-network",
            allowed_hosts=("api.openai.com",),
        )
    )
    app = create_app(settings=Settings(), provider=provider)

    with TestClient(app) as client:
        ready = client.get("/ready")
        call = client.post("/api/v1/moderation", json={"text": "合成文本"})

    assert ready.status_code == 503
    assert ready.json()["status"] == "not_ready"
    assert call.status_code == 503
    assert call.json()["error"]["code"] == "provider_unavailable"
    assert "secret-not-for-network" not in repr(provider.config)


@pytest.mark.asyncio
async def test_openai_compatible_uses_allowlisted_endpoint_and_validates_json() -> None:
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["authorization"] = request.headers["authorization"]
        captured["payload"] = json.loads(request.content)
        return httpx.Response(
            200,
            headers={"Content-Type": "application/json"},
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "category": "billing",
                                    "priority": "P1",
                                    "confidence": 0.87,
                                    "reasons": ["合成测试：命中重复扣款语义"],
                                },
                                ensure_ascii=False,
                            )
                        }
                    }
                ]
            },
        )

    provider = OpenAICompatibleProvider(
        OpenAICompatibleConfig(
            base_url="https://api.openai.com/v1/",
            model="synthetic-compatible-model",
            api_key="test-token-not-a-real-secret",
            allowed_hosts=("api.openai.com",),
            network_enabled=True,
        ),
        transport=httpx.MockTransport(handler),
    )

    result = await provider.classify_ticket(
        TicketClassificationRequest(
            subject="合成订单重复扣款",
            content="只用于离线 MockTransport 契约测试。",
        )
    )

    assert provider.ready is True
    assert str(captured["url"]) == "https://api.openai.com/v1/chat/completions"
    assert captured["authorization"] == "Bearer test-token-not-a-real-secret"
    payload = captured["payload"]
    assert isinstance(payload, dict)
    assert payload["model"] == "synthetic-compatible-model"
    assert payload["temperature"] == 0
    assert result.category == "billing"
    assert result.priority == "P1"


@pytest.mark.asyncio
async def test_openai_compatible_transient_status_is_retryable() -> None:
    provider = OpenAICompatibleProvider(
        OpenAICompatibleConfig(
            base_url="https://models.example.test/v1",
            model="synthetic-compatible-model",
            api_key="test-token-not-a-real-secret",
            allowed_hosts=("models.example.test",),
            network_enabled=True,
        ),
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                429,
                headers={"Content-Type": "application/json"},
                json={"error": {"message": "synthetic rate limit"}},
            )
        ),
    )

    with pytest.raises(ProviderTransientError, match="429"):
        await provider.moderate(ModerationRequest(text="公开合成文本"))


@pytest.mark.asyncio
async def test_openai_compatible_rejects_redirect_and_untrusted_citation() -> None:
    redirecting_provider = OpenAICompatibleProvider(
        OpenAICompatibleConfig(
            base_url="https://models.example.test/v1",
            model="synthetic-compatible-model",
            api_key="test-token-not-a-real-secret",
            allowed_hosts=("models.example.test",),
            network_enabled=True,
        ),
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                307,
                headers={"Location": "https://untrusted.example/collect"},
            )
        ),
    )

    with pytest.raises(ProviderError, match="重定向"):
        await redirecting_provider.moderate(ModerationRequest(text="公开合成文本"))

    def untrusted_citation_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"Content-Type": "application/json"},
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "answer": "这是合成回答。",
                                    "grounded": True,
                                    "confidence": 0.8,
                                    "citations": [
                                        {
                                            "source_id": "not-in-request",
                                            "title": "不存在的资料",
                                        }
                                    ],
                                    "must_verify": ["人工核对"],
                                },
                                ensure_ascii=False,
                            )
                        }
                    }
                ]
            },
        )

    knowledge_provider = OpenAICompatibleProvider(
        OpenAICompatibleConfig(
            base_url="https://models.example.test/v1",
            model="synthetic-compatible-model",
            api_key="test-token-not-a-real-secret",
            allowed_hosts=("models.example.test",),
            network_enabled=True,
        ),
        transport=httpx.MockTransport(untrusted_citation_handler),
    )
    with pytest.raises(ProviderError, match="请求资料之外"):
        await knowledge_provider.answer_knowledge(
            KnowledgeAnswerRequest(
                question="合成退款如何处理？",
                documents=[
                    {
                        "source_id": "allowed-source",
                        "title": "合成资料",
                        "content": "演示订单只能在测试环境申请。",
                    }
                ],
            )
        )


@pytest.mark.asyncio
async def test_openai_compatible_configuration_failure_never_sends_request() -> None:
    request_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal request_count
        request_count += 1
        return httpx.Response(200, json={})

    provider = OpenAICompatibleProvider(
        OpenAICompatibleConfig(
            base_url="https://untrusted.example/v1",
            model="synthetic-compatible-model",
            api_key="test-token-not-a-real-secret",
            allowed_hosts=("models.example.test",),
            network_enabled=True,
        ),
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(ProviderUnavailableError, match="白名单"):
        await provider.moderate(ModerationRequest(text="公开合成文本"))
    assert request_count == 0


def test_insecure_openai_compatible_url_is_rejected() -> None:
    settings = Settings(
        provider="openai-compatible",
        openai_base_url="http://untrusted.example/v1",
        openai_allowed_hosts=("api.openai.com",),
    )

    try:
        settings.validate()
    except ValueError as exc:
        assert "HTTPS" in str(exc)
    else:
        raise AssertionError("不安全的 HTTP 地址必须被拒绝")
