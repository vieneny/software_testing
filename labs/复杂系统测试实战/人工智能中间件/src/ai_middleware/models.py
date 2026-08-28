"""HTTP 与 Provider 共用的严格数据模型。"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ExecutionPolicy(StrictModel):
    timeout_ms: int | None = Field(default=None, ge=100, le=30_000)
    max_retries: int | None = Field(default=None, ge=0, le=3)


class ProviderMetadata(StrictModel):
    name: str
    model: str
    version: str
    attempts: int = Field(ge=1, le=4)


class ErrorDetail(StrictModel):
    code: str
    message: str
    retryable: bool
    details: dict[str, object] = Field(default_factory=dict)


class ErrorResponse(StrictModel):
    api_version: str
    request_id: str
    error: ErrorDetail


class HealthResponse(StrictModel):
    api_version: str
    service_version: str
    request_id: str
    status: Literal["ok"]


class ReadyResponse(StrictModel):
    api_version: str
    service_version: str
    request_id: str
    status: Literal["ready", "not_ready"]
    provider: str
    reason: str | None = None


class SuccessResponse[ResultT](StrictModel):
    api_version: str
    request_id: str
    result: ResultT
    provider: ProviderMetadata


class ModerationRequest(StrictModel):
    text: str = Field(min_length=1, max_length=10_000)
    context: Literal["forum", "customer_service", "general"] = "general"
    execution: ExecutionPolicy = Field(default_factory=ExecutionPolicy)


class ModerationResult(StrictModel):
    allowed: bool
    decision: Literal["allow", "review", "block"]
    risk_score: float = Field(ge=0, le=1)
    categories: list[str]
    matched_terms: list[str]
    reason: str


class ContentAnalysisRequest(StrictModel):
    text: str = Field(min_length=1, max_length=10_000)
    max_summary_chars: int = Field(default=300, ge=50, le=2000)
    max_tags: int = Field(default=5, ge=1, le=10)
    execution: ExecutionPolicy = Field(default_factory=ExecutionPolicy)


class ContentAnalysisResult(StrictModel):
    summary: str
    tags: list[str]
    source_chars: int
    truncated: bool


class TicketClassificationRequest(StrictModel):
    subject: str = Field(min_length=1, max_length=300)
    content: str = Field(min_length=1, max_length=10_000)
    channel: Literal["web", "ios", "android", "api", "email", "other"] = "other"
    execution: ExecutionPolicy = Field(default_factory=ExecutionPolicy)


class TicketClassificationResult(StrictModel):
    category: Literal["account", "billing", "technical", "security", "product", "other"]
    priority: Literal["P0", "P1", "P2", "P3"]
    confidence: float = Field(ge=0, le=1)
    reasons: list[str]


class KnowledgeDocument(StrictModel):
    source_id: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=300)
    content: str = Field(min_length=1, max_length=5000)


class KnowledgeAnswerRequest(StrictModel):
    question: str = Field(min_length=1, max_length=2000)
    documents: list[KnowledgeDocument] = Field(min_length=1, max_length=20)
    execution: ExecutionPolicy = Field(default_factory=ExecutionPolicy)


class Citation(StrictModel):
    source_id: str
    title: str


class KnowledgeAnswerResult(StrictModel):
    answer: str
    grounded: bool
    confidence: float = Field(ge=0, le=1)
    citations: list[Citation]
    must_verify: list[str]


class ReplySuggestionRequest(StrictModel):
    ticket_id: str = Field(min_length=1, max_length=100)
    customer_message: str = Field(min_length=1, max_length=10_000)
    category: Literal[
        "account", "billing", "technical", "security", "product", "other"
    ] = "other"
    priority: Literal["P0", "P1", "P2", "P3"] = "P2"
    context: list[Annotated[str, Field(min_length=1, max_length=1000)]] = Field(
        default_factory=list, max_length=10
    )
    tone: Literal["professional", "empathetic", "concise"] = "empathetic"
    execution: ExecutionPolicy = Field(default_factory=ExecutionPolicy)


class ReplySuggestionResult(StrictModel):
    suggestion: str
    suggested_actions: list[str]
    must_verify: list[str]
    requires_human_review: bool


class ForumSummaryRequest(StrictModel):
    title: str = Field(min_length=1, max_length=300)
    content: str = Field(min_length=1, max_length=10_000)
    answers: list[Annotated[str, Field(min_length=1, max_length=5000)]] = Field(
        default_factory=list, max_length=100
    )
    execution: ExecutionPolicy = Field(default_factory=ExecutionPolicy)

    @model_validator(mode="after")
    def validate_total_size(self) -> ForumSummaryRequest:
        total = len(self.title) + len(self.content) + sum(map(len, self.answers))
        if total > 20_000:
            raise ValueError("title、content 与 answers 总长度不能超过 20000 字符")
        return self


class ForumProviderMetadata(StrictModel):
    name: str = Field(min_length=1, max_length=200)
    model: str = Field(min_length=1, max_length=200)
    version: str = Field(min_length=1, max_length=200)
    analysis_calls: int = Field(ge=1)
    moderation_calls: int = Field(ge=1)
    total_attempts: int = Field(ge=2)


class ForumProcessingMetadata(StrictModel):
    source_chars: int = Field(ge=1)
    chunk_size: int = Field(ge=1)
    chunk_overlap: int = Field(ge=0)
    chunk_count: int = Field(ge=1)
    input_truncated: Literal[False] = False
    summary_truncated: bool
    risk_hints_truncated: bool
    model_truncated: bool


class ForumSummaryResponse(StrictModel):
    api_version: str
    request_id: str
    summary: str = Field(min_length=1, max_length=10_000)
    risk_hints: list[Annotated[str, Field(min_length=1, max_length=500)]] = Field(
        max_length=20
    )
    model: str = Field(min_length=1, max_length=200)
    provider: ForumProviderMetadata
    processing: ForumProcessingMetadata


class CustomerKnowledgeContext(StrictModel):
    title: str = Field(min_length=1, max_length=300)
    category: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1, max_length=5000)


class CustomerServiceSuggestRequest(StrictModel):
    tenant_code: str = Field(default="demo", min_length=1, max_length=100)
    ticket_id: str = Field(min_length=1, max_length=100)
    title: str | None = Field(default=None, min_length=1, max_length=300)
    description: str | None = Field(default=None, min_length=1, max_length=10_000)
    category: str = Field(default="OTHER", min_length=1, max_length=100)
    priority: str = Field(default="MEDIUM", min_length=1, max_length=50)
    customer_level: str = Field(default="NORMAL", min_length=1, max_length=50)
    tone: str = Field(default="professional", min_length=1, max_length=50)
    language: str = Field(default="zh-CN", min_length=1, max_length=20)
    knowledge_context: list[CustomerKnowledgeContext] = Field(
        default_factory=list, max_length=20
    )

    # 早期学习契约的兼容字段；新 Java 客户端应使用 title/description。
    subject: str | None = Field(default=None, min_length=1, max_length=300)
    customer_message: str | None = Field(default=None, min_length=1, max_length=10_000)
    channel: Literal["web", "ios", "android", "api", "email", "other"] = "other"
    context: list[Annotated[str, Field(min_length=1, max_length=1000)]] = Field(
        default_factory=list, max_length=10
    )
    execution: ExecutionPolicy = Field(default_factory=ExecutionPolicy)

    @model_validator(mode="after")
    def validate_compatible_content(self) -> CustomerServiceSuggestRequest:
        if not (self.description or self.customer_message):
            raise ValueError("description 与兼容字段 customer_message 至少提供一个")
        total = sum(
            len(value)
            for value in (
                self.title or "",
                self.description or "",
                self.subject or "",
                self.customer_message or "",
                *self.context,
                *(item.content for item in self.knowledge_context),
            )
        )
        if total > 30_000:
            raise ValueError("客服请求文本总长度不能超过 30000 字符")
        return self


class CustomerServiceSuggestResponse(StrictModel):
    summary: str = Field(min_length=1, max_length=2000)
    suggested_reply: str = Field(min_length=1, max_length=10_000)
    suggested_category: Literal[
        "ACCOUNT", "BILLING", "TECHNICAL", "SECURITY", "PRODUCT", "OTHER"
    ]
    suggested_priority: Literal["URGENT", "HIGH", "MEDIUM", "LOW"]
    confidence: float = Field(ge=0, le=1)
    risk_flags: list[Annotated[str, Field(min_length=1, max_length=100)]] = Field(
        max_length=20
    )
    knowledge_references: list[
        Annotated[str, Field(min_length=1, max_length=500)]
    ] = Field(max_length=20)
    degraded: bool
    degradation_reason: str | None = Field(default=None, max_length=500)

    # 统一链路元数据；Java record 默认可忽略这些附加字段。
    api_version: Literal["v1"]
    request_id: str = Field(pattern=r"^[A-Za-z0-9._:-]{1,128}$")
    suggested_actions: list[
        Annotated[str, Field(min_length=1, max_length=500)]
    ] = Field(max_length=20)
    must_verify: list[Annotated[str, Field(min_length=1, max_length=500)]] = Field(
        min_length=1, max_length=20
    )
    model: str = Field(min_length=1, max_length=200)
