"""Provider 抽象；业务路由不依赖具体模型厂商。"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ai_middleware.models import (
    ContentAnalysisRequest,
    ContentAnalysisResult,
    KnowledgeAnswerRequest,
    KnowledgeAnswerResult,
    ModerationRequest,
    ModerationResult,
    ReplySuggestionRequest,
    ReplySuggestionResult,
    TicketClassificationRequest,
    TicketClassificationResult,
)


class ProviderError(RuntimeError):
    """Provider 基础异常。"""


class ProviderTransientError(ProviderError):
    """可安全重试的临时失败。"""


class ProviderUnavailableError(ProviderError):
    """Provider 未配置、被禁用或无法服务。"""


class AIProvider(ABC):
    name: str
    model: str
    version: str

    @property
    @abstractmethod
    def ready(self) -> bool:
        """Provider 是否可以处理请求。"""

    @property
    def readiness_reason(self) -> str | None:
        return None if self.ready else "provider unavailable"

    @abstractmethod
    async def moderate(self, request: ModerationRequest) -> ModerationResult:
        """审核文本。"""

    @abstractmethod
    async def analyze_content(
        self, request: ContentAnalysisRequest
    ) -> ContentAnalysisResult:
        """生成摘要与标签。"""

    @abstractmethod
    async def classify_ticket(
        self, request: TicketClassificationRequest
    ) -> TicketClassificationResult:
        """工单分类与优先级判断。"""

    @abstractmethod
    async def answer_knowledge(
        self, request: KnowledgeAnswerRequest
    ) -> KnowledgeAnswerResult:
        """只依据传入资料回答。"""

    @abstractmethod
    async def suggest_reply(
        self, request: ReplySuggestionRequest
    ) -> ReplySuggestionResult:
        """生成需要人工确认的坐席回复建议。"""
