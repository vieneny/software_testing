import pytest

from ai_middleware.models import (
    ContentAnalysisRequest,
    KnowledgeAnswerRequest,
    KnowledgeDocument,
    ModerationRequest,
    TicketClassificationRequest,
)
from ai_middleware.providers.mock import MockProvider


@pytest.mark.asyncio
async def test_same_input_produces_same_output() -> None:
    provider = MockProvider()
    request = ContentAnalysisRequest(text="API 测试。API 测试需要断言。")

    first = await provider.analyze_content(request)
    second = await provider.analyze_content(request)

    assert first == second


@pytest.mark.asyncio
async def test_violence_rule_blocks() -> None:
    result = await MockProvider().moderate(
        ModerationRequest(text="这是用于安全测试的合成炸弹关键词。")
    )

    assert result.decision == "block"
    assert result.allowed is False
    assert result.risk_score == 0.9


@pytest.mark.asyncio
async def test_security_ticket_is_p0() -> None:
    result = await MockProvider().classify_ticket(
        TicketClassificationRequest(
            subject="安全漏洞",
            content="公开演示环境出现越权风险。",
        )
    )

    assert result.category == "security"
    assert result.priority == "P0"


@pytest.mark.asyncio
async def test_knowledge_answer_does_not_invent_without_overlap() -> None:
    result = await MockProvider().answer_knowledge(
        KnowledgeAnswerRequest(
            question="量子计算问题",
            documents=[
                KnowledgeDocument(
                    source_id="synthetic",
                    title="演示退款",
                    content="测试订单可申请退款。",
                )
            ],
        )
    )

    assert result.grounded is False
    assert result.confidence == 0
    assert result.citations == []
