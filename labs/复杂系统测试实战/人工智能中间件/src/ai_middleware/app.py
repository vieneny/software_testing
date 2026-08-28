"""FastAPI 应用工厂与 HTTP 契约。"""

from __future__ import annotations

import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from ai_middleware.config import Settings
from ai_middleware.models import (
    ContentAnalysisRequest,
    ContentAnalysisResult,
    CustomerServiceSuggestRequest,
    CustomerServiceSuggestResponse,
    ErrorDetail,
    ErrorResponse,
    ForumProcessingMetadata,
    ForumProviderMetadata,
    ForumSummaryRequest,
    ForumSummaryResponse,
    HealthResponse,
    KnowledgeAnswerRequest,
    KnowledgeAnswerResult,
    ModerationRequest,
    ModerationResult,
    ReadyResponse,
    ReplySuggestionRequest,
    ReplySuggestionResult,
    SuccessResponse,
    TicketClassificationRequest,
    TicketClassificationResult,
)
from ai_middleware.providers.base import AIProvider
from ai_middleware.providers.mock import MockProvider
from ai_middleware.providers.openai_compatible import (
    OpenAICompatibleConfig,
    OpenAICompatibleProvider,
)
from ai_middleware.service import AIService, MiddlewareError

REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
CONTROL_CHARACTER_PATTERN = re.compile(r"[\x00-\x1f\x7f-\x9f]")
FORUM_CHUNK_SIZE = 10_000
FORUM_CHUNK_OVERLAP = 128
FORUM_SUMMARY_MAX_CHARS = 800
FORUM_MODEL_MAX_CHARS = 200
FORUM_RISK_HINT_MAX_COUNT = 20
FORUM_RISK_HINT_MAX_CHARS = 500
ERROR_RESPONSES = {
    400: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
    422: {"model": ErrorResponse},
    500: {"model": ErrorResponse},
    502: {"model": ErrorResponse},
    503: {"model": ErrorResponse},
    504: {"model": ErrorResponse},
}


def _build_provider(settings: Settings) -> AIProvider:
    if settings.provider == "mock":
        return MockProvider()
    return OpenAICompatibleProvider(
        OpenAICompatibleConfig(
            base_url=settings.openai_base_url,
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            allowed_hosts=settings.openai_allowed_hosts,
            network_enabled=settings.openai_network_enabled,
            timeout_ms=settings.openai_timeout_ms,
            max_output_tokens=settings.openai_max_output_tokens,
            max_response_bytes=settings.openai_max_response_bytes,
        )
    )


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", uuid4().hex)


def _split_unicode_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """按 Unicode 字符带重叠切分，避免多字符风险词在边界处被拆散。"""

    if not 0 <= overlap < chunk_size:
        raise ValueError("overlap 必须大于等于 0 且小于 chunk_size")

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks


def _aggregate_forum_summaries(summaries: list[str]) -> tuple[str, bool]:
    if len(summaries) == 1:
        combined = summaries[0]
    else:
        combined = "\n".join(
            f"[分块 {index}/{len(summaries)}] {summary}"
            for index, summary in enumerate(summaries, start=1)
        )
    if len(combined) <= FORUM_SUMMARY_MAX_CHARS:
        return combined, False
    return combined[: FORUM_SUMMARY_MAX_CHARS - 1].rstrip() + "…", True


def _bounded_nonempty_text(
    value: str,
    *,
    max_chars: int,
    fallback: str,
) -> tuple[str, bool]:
    without_controls = CONTROL_CHARACTER_PATTERN.sub(" ", value)
    normalized = re.sub(r"\s+", " ", without_controls).strip() or fallback
    if len(normalized) <= max_chars:
        return normalized, False
    return normalized[: max_chars - 1].rstrip() + "…", True


def _aggregate_forum_risk_hints(candidates: list[str]) -> tuple[list[str], bool]:
    unique_hints: list[str] = []
    seen: set[str] = set()
    any_entry_truncated = False
    for candidate in candidates:
        hint, entry_truncated = _bounded_nonempty_text(
            candidate,
            max_chars=FORUM_RISK_HINT_MAX_CHARS,
            fallback="未命名风险",
        )
        any_entry_truncated = any_entry_truncated or entry_truncated
        if hint not in seen:
            seen.add(hint)
            unique_hints.append(hint)

    if not unique_hints:
        return [], any_entry_truncated

    review_hint = "离线规则结果仅供分流，发布前必须人工复核"
    if len(unique_hints) < FORUM_RISK_HINT_MAX_COUNT:
        return [*unique_hints, review_hint], any_entry_truncated

    # 预留人工复核与封顶提示，确保输出不会超过论坛消费者的 20 项硬限制。
    selected = unique_hints[: FORUM_RISK_HINT_MAX_COUNT - 2]
    return [
        *selected,
        review_hint,
        "风险提示已达到20项上限，完整风险类别必须人工复核",
    ], True


def _bounded_unique_items(
    values: list[str],
    *,
    max_count: int,
    max_chars: int,
) -> tuple[list[str], bool]:
    result: list[str] = []
    seen: set[str] = set()
    adjusted = False
    for value in values:
        without_controls = CONTROL_CHARACTER_PATTERN.sub(" ", value)
        normalized = re.sub(r"\s+", " ", without_controls).strip()
        if not normalized:
            adjusted = True
            continue
        bounded, truncated = _bounded_nonempty_text(
            normalized,
            max_chars=max_chars,
            fallback="未命名项目",
        )
        adjusted = adjusted or truncated
        if bounded in seen:
            continue
        seen.add(bounded)
        if len(result) >= max_count:
            adjusted = True
            continue
        result.append(bounded)
    return result, adjusted


def _error_response(
    *,
    request: Request,
    api_version: str,
    status_code: int,
    code: str,
    message: str,
    retryable: bool,
    details: dict[str, object] | None = None,
) -> JSONResponse:
    body = ErrorResponse(
        api_version=api_version,
        request_id=_request_id(request),
        error=ErrorDetail(
            code=code,
            message=message,
            retryable=retryable,
            details=details or {},
        ),
    )
    return JSONResponse(status_code=status_code, content=body.model_dump(mode="json"))


def _service(request: Request) -> AIService:
    return request.app.state.ai_service


ServiceDependency = Annotated[AIService, Depends(_service)]


def create_app(
    *,
    settings: Settings | None = None,
    provider: AIProvider | None = None,
) -> FastAPI:
    resolved_settings = settings or Settings.from_env()
    resolved_settings.validate()
    resolved_provider = provider or _build_provider(resolved_settings)

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        # 真实 Provider 可在这里创建连接池，并在 yield 后安全关闭。
        yield

    application = FastAPI(
        title="学习用 AI 中间件",
        summary="论坛 FastAPI 与客服 Spring Boot 的离线 AI 契约骨架",
        description=(
            "默认 Provider 为完全离线的确定性规则。输入不会持久化；"
            "OpenAI-compatible 只有在显式启用网络并通过安全配置校验后才会外发请求。"
        ),
        version=resolved_settings.service_version,
        lifespan=lifespan,
    )
    application.state.settings = resolved_settings
    application.state.ai_service = AIService(resolved_provider, resolved_settings)

    @application.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        incoming = request.headers.get("X-Request-ID", "")
        request.state.request_id = (
            incoming if REQUEST_ID_PATTERN.fullmatch(incoming) else uuid4().hex
        )
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    @application.exception_handler(MiddlewareError)
    async def middleware_error_handler(
        request: Request, exc: MiddlewareError
    ) -> JSONResponse:
        return _error_response(
            request=request,
            api_version=resolved_settings.api_version,
            status_code=exc.status_code,
            code=exc.code,
            message=exc.message,
            retryable=exc.retryable,
            details=exc.details,
        )

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        fields = [
            {
                "location": ".".join(map(str, error["loc"])),
                "message": error["msg"],
                "type": error["type"],
            }
            for error in exc.errors()
        ]
        return _error_response(
            request=request,
            api_version=resolved_settings.api_version,
            status_code=422,
            code="validation_error",
            message="请求参数不符合接口契约",
            retryable=False,
            details={"fields": fields},
        )

    @application.exception_handler(StarletteHTTPException)
    async def http_error_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        return _error_response(
            request=request,
            api_version=resolved_settings.api_version,
            status_code=exc.status_code,
            code="http_error",
            message=str(exc.detail),
            retryable=False,
        )

    @application.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
        # 不把异常、提示词、密钥或输入正文回显给调用方。
        return _error_response(
            request=request,
            api_version=resolved_settings.api_version,
            status_code=500,
            code="internal_error",
            message="服务发生未预期错误",
            retryable=False,
        )

    @application.get(
        "/health",
        response_model=HealthResponse,
        tags=["运行状态"],
    )
    async def health(request: Request) -> HealthResponse:
        return HealthResponse(
            api_version=resolved_settings.api_version,
            service_version=resolved_settings.service_version,
            request_id=_request_id(request),
            status="ok",
        )

    @application.get(
        "/ready",
        response_model=ReadyResponse,
        responses={503: {"model": ReadyResponse}},
        tags=["运行状态"],
    )
    async def ready(request: Request) -> ReadyResponse | JSONResponse:
        body = ReadyResponse(
            api_version=resolved_settings.api_version,
            service_version=resolved_settings.service_version,
            request_id=_request_id(request),
            status="ready" if resolved_provider.ready else "not_ready",
            provider=resolved_provider.name,
            reason=resolved_provider.readiness_reason,
        )
        if resolved_provider.ready:
            return body
        return JSONResponse(status_code=503, content=body.model_dump(mode="json"))

    @application.post(
        "/api/v1/moderation",
        response_model=SuccessResponse[ModerationResult],
        responses=ERROR_RESPONSES,
        tags=["通用能力"],
    )
    async def moderate(
        payload: ModerationRequest,
        request: Request,
        service: ServiceDependency,
    ) -> SuccessResponse[ModerationResult]:
        call = await service.execute(
            lambda: service.provider.moderate(payload),
            payload.execution,
        )
        return SuccessResponse(
            api_version=resolved_settings.api_version,
            request_id=_request_id(request),
            result=call.value,
            provider=call.metadata,
        )

    @application.post(
        "/api/v1/content/analyze",
        response_model=SuccessResponse[ContentAnalysisResult],
        responses=ERROR_RESPONSES,
        tags=["通用能力"],
    )
    async def analyze_content(
        payload: ContentAnalysisRequest,
        request: Request,
        service: ServiceDependency,
    ) -> SuccessResponse[ContentAnalysisResult]:
        call = await service.execute(
            lambda: service.provider.analyze_content(payload),
            payload.execution,
        )
        return SuccessResponse(
            api_version=resolved_settings.api_version,
            request_id=_request_id(request),
            result=call.value,
            provider=call.metadata,
        )

    @application.post(
        "/api/v1/tickets/classify",
        response_model=SuccessResponse[TicketClassificationResult],
        responses=ERROR_RESPONSES,
        tags=["客服能力"],
    )
    async def classify_ticket(
        payload: TicketClassificationRequest,
        request: Request,
        service: ServiceDependency,
    ) -> SuccessResponse[TicketClassificationResult]:
        call = await service.execute(
            lambda: service.provider.classify_ticket(payload),
            payload.execution,
        )
        return SuccessResponse(
            api_version=resolved_settings.api_version,
            request_id=_request_id(request),
            result=call.value,
            provider=call.metadata,
        )

    @application.post(
        "/api/v1/knowledge/answer",
        response_model=SuccessResponse[KnowledgeAnswerResult],
        responses=ERROR_RESPONSES,
        tags=["客服能力"],
    )
    async def answer_knowledge(
        payload: KnowledgeAnswerRequest,
        request: Request,
        service: ServiceDependency,
    ) -> SuccessResponse[KnowledgeAnswerResult]:
        call = await service.execute(
            lambda: service.provider.answer_knowledge(payload),
            payload.execution,
        )
        return SuccessResponse(
            api_version=resolved_settings.api_version,
            request_id=_request_id(request),
            result=call.value,
            provider=call.metadata,
        )

    @application.post(
        "/api/v1/agents/reply-suggestions",
        response_model=SuccessResponse[ReplySuggestionResult],
        responses=ERROR_RESPONSES,
        tags=["客服能力"],
    )
    async def suggest_reply(
        payload: ReplySuggestionRequest,
        request: Request,
        service: ServiceDependency,
    ) -> SuccessResponse[ReplySuggestionResult]:
        call = await service.execute(
            lambda: service.provider.suggest_reply(payload),
            payload.execution,
        )
        return SuccessResponse(
            api_version=resolved_settings.api_version,
            request_id=_request_id(request),
            result=call.value,
            provider=call.metadata,
        )

    @application.post(
        "/api/v1/forum/summarize",
        response_model=ForumSummaryResponse,
        responses=ERROR_RESPONSES,
        tags=["兼容路由"],
    )
    async def forum_summarize(
        payload: ForumSummaryRequest,
        request: Request,
        service: ServiceDependency,
    ) -> ForumSummaryResponse:
        answer_text = "\n".join(
            f"回答 {index + 1}：{answer}" for index, answer in enumerate(payload.answers)
        )
        combined = f"标题：{payload.title}\n正文：{payload.content}"
        if answer_text:
            combined += f"\n{answer_text}"
        chunks = _split_unicode_text(
            combined,
            FORUM_CHUNK_SIZE,
            FORUM_CHUNK_OVERLAP,
        )
        summaries: list[str] = []
        risk_candidates: list[str] = []
        total_attempts = 0
        any_analysis_truncated = False
        first_provider_metadata = None

        for chunk_index, chunk in enumerate(chunks, start=1):
            analysis_payload = ContentAnalysisRequest(
                text=chunk,
                max_summary_chars=500,
                max_tags=5,
                execution=payload.execution,
            )
            moderation_payload = ModerationRequest(
                text=chunk,
                context="forum",
                execution=payload.execution,
            )
            try:
                analysis = await service.execute(
                    lambda analysis_request=analysis_payload: (
                        service.provider.analyze_content(analysis_request)
                    ),
                    payload.execution,
                )
            except MiddlewareError as exc:
                raise MiddlewareError(
                    status_code=exc.status_code,
                    code=exc.code,
                    message=exc.message,
                    retryable=exc.retryable,
                    details={
                        **exc.details,
                        "operation": "analysis",
                        "chunk_index": chunk_index,
                        "chunk_count": len(chunks),
                        "partial_result_returned": False,
                    },
                ) from exc

            try:
                moderation = await service.execute(
                    lambda moderation_request=moderation_payload: (
                        service.provider.moderate(moderation_request)
                    ),
                    payload.execution,
                )
            except MiddlewareError as exc:
                raise MiddlewareError(
                    status_code=exc.status_code,
                    code=exc.code,
                    message=exc.message,
                    retryable=exc.retryable,
                    details={
                        **exc.details,
                        "operation": "moderation",
                        "chunk_index": chunk_index,
                        "chunk_count": len(chunks),
                        "partial_result_returned": False,
                    },
                ) from exc

            summaries.append(analysis.value.summary)
            any_analysis_truncated = (
                any_analysis_truncated or analysis.value.truncated
            )
            total_attempts += analysis.metadata.attempts + moderation.metadata.attempts
            if first_provider_metadata is None:
                first_provider_metadata = analysis.metadata

            if moderation.value.decision != "allow":
                risk_candidates.append(
                    f"chunk={chunk_index};decision={moderation.value.decision}"
                )
                risk_candidates.extend(
                    f"chunk={chunk_index};category={category}"
                    for category in sorted(set(moderation.value.categories))
                )

        summary, summary_truncated = _aggregate_forum_summaries(summaries)
        summary, summary_bounded = _bounded_nonempty_text(
            summary,
            max_chars=10_000,
            fallback="未生成摘要，请人工查看原文。",
        )
        summary_truncated = (
            summary_truncated or summary_bounded or any_analysis_truncated
        )
        risk_hints, risk_hints_truncated = _aggregate_forum_risk_hints(
            risk_candidates
        )
        if first_provider_metadata is None:
            raise AssertionError("non-empty forum input must produce at least one chunk")

        provider_name, provider_name_truncated = _bounded_nonempty_text(
            first_provider_metadata.name,
            max_chars=200,
            fallback="unknown-provider",
        )
        provider_model, provider_model_truncated = _bounded_nonempty_text(
            first_provider_metadata.model,
            max_chars=200,
            fallback="unknown-model",
        )
        provider_version, provider_version_truncated = _bounded_nonempty_text(
            first_provider_metadata.version,
            max_chars=200,
            fallback="unknown-version",
        )
        model_label, model_label_truncated = _bounded_nonempty_text(
            f"{provider_name}/{provider_model}@{provider_version}",
            max_chars=FORUM_MODEL_MAX_CHARS,
            fallback="unknown-provider/unknown-model@unknown-version",
        )
        model_truncated = any(
            (
                provider_name_truncated,
                provider_model_truncated,
                provider_version_truncated,
                model_label_truncated,
            )
        )

        return ForumSummaryResponse(
            api_version=resolved_settings.api_version,
            request_id=_request_id(request),
            summary=summary,
            risk_hints=risk_hints,
            model=model_label,
            provider=ForumProviderMetadata(
                name=provider_name,
                model=provider_model,
                version=provider_version,
                analysis_calls=len(chunks),
                moderation_calls=len(chunks),
                total_attempts=total_attempts,
            ),
            processing=ForumProcessingMetadata(
                source_chars=len(combined),
                chunk_size=FORUM_CHUNK_SIZE,
                chunk_overlap=FORUM_CHUNK_OVERLAP,
                chunk_count=len(chunks),
                input_truncated=False,
                summary_truncated=summary_truncated,
                risk_hints_truncated=risk_hints_truncated,
                model_truncated=model_truncated,
            ),
        )

    @application.post(
        "/api/v1/customer-service/suggest",
        response_model=CustomerServiceSuggestResponse,
        responses=ERROR_RESPONSES,
        tags=["兼容路由"],
    )
    async def customer_service_suggest(
        payload: CustomerServiceSuggestRequest,
        request: Request,
        service: ServiceDependency,
    ) -> CustomerServiceSuggestResponse:
        title = payload.title or payload.subject or "客户咨询"
        description = payload.description or payload.customer_message or ""
        classification_payload = TicketClassificationRequest(
            subject=title,
            content=description,
            channel=payload.channel,
            execution=payload.execution,
        )
        classification = await service.execute(
            lambda: service.provider.classify_ticket(classification_payload),
            payload.execution,
        )

        category_aliases = {
            "ACCOUNT": "account",
            "BILLING": "billing",
            "PAYMENT": "billing",
            "TECHNICAL": "technical",
            "SECURITY": "security",
            "PRODUCT": "product",
            "OTHER": "other",
        }
        internal_category = classification.value.category
        if internal_category == "other":
            internal_category = category_aliases.get(payload.category.upper(), "other")

        priority_aliases = {
            "CRITICAL": "P0",
            "URGENT": "P0",
            "P0": "P0",
            "HIGH": "P1",
            "P1": "P1",
            "MEDIUM": "P2",
            "P2": "P2",
            "LOW": "P3",
            "P3": "P3",
        }
        incoming_priority = priority_aliases.get(payload.priority.upper(), "P2")
        priority_rank = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
        internal_priority = min(
            (classification.value.priority, incoming_priority),
            key=priority_rank.__getitem__,
        )

        tone = payload.tone.lower()
        if tone not in {"professional", "empathetic", "concise"}:
            tone = "professional"

        reply_payload = ReplySuggestionRequest(
            ticket_id=payload.ticket_id,
            customer_message=description,
            category=internal_category,
            priority=internal_priority,
            context=[
                *payload.context,
                *(item.content[:1000] for item in payload.knowledge_context),
            ][:10],
            tone=tone,
            execution=payload.execution,
        )
        reply = await service.execute(
            lambda: service.provider.suggest_reply(reply_payload),
            payload.execution,
        )

        customer_text = f"{title}\n{description}"[:10_000]
        analysis_payload = ContentAnalysisRequest(
            text=customer_text,
            max_summary_chars=300,
            max_tags=5,
            execution=payload.execution,
        )
        analysis = await service.execute(
            lambda: service.provider.analyze_content(analysis_payload),
            payload.execution,
        )
        moderation_payload = ModerationRequest(
            text=customer_text,
            context="customer_service",
            execution=payload.execution,
        )
        moderation = await service.execute(
            lambda: service.provider.moderate(moderation_payload),
            payload.execution,
        )

        knowledge_references: list[str] = []
        if payload.knowledge_context:
            knowledge_payload = KnowledgeAnswerRequest(
                question=f"{title}\n{description}",
                documents=[
                    {
                        "source_id": f"knowledge-{index + 1}",
                        "title": item.title,
                        "content": item.content,
                    }
                    for index, item in enumerate(payload.knowledge_context)
                ],
                execution=payload.execution,
            )
            knowledge = await service.execute(
                lambda: service.provider.answer_knowledge(knowledge_payload),
                payload.execution,
            )
            knowledge_references = [
                citation.title for citation in knowledge.value.citations
            ]

        summary, summary_adjusted = _bounded_nonempty_text(
            analysis.value.summary,
            max_chars=2000,
            fallback="未生成摘要，请坐席人工查看工单原文。",
        )
        summary_adjusted = summary_adjusted or analysis.value.truncated
        suggested_reply, reply_adjusted = _bounded_nonempty_text(
            reply.value.suggestion,
            max_chars=10_000,
            fallback="您好，您的问题已记录，请等待人工坐席进一步核实。",
        )
        suggested_actions, actions_adjusted = _bounded_unique_items(
            reply.value.suggested_actions,
            max_count=20,
            max_chars=500,
        )
        knowledge_references, references_adjusted = _bounded_unique_items(
            knowledge_references,
            max_count=20,
            max_chars=500,
        )

        model_label, model_adjusted = _bounded_nonempty_text(
            f"{reply.metadata.name}/{reply.metadata.model}@{reply.metadata.version}",
            max_chars=200,
            fallback="unknown-provider/unknown-model@unknown-version",
        )

        must_verify_candidates = [
            *reply.value.must_verify,
            "所有 AI 输出发送前必须由授权坐席人工核验。",
        ]
        if summary_adjusted:
            must_verify_candidates.append(
                "摘要已被 Provider 或响应边界截断，必须回看完整工单。"
            )
        if reply_adjusted:
            must_verify_candidates.append(
                "回复建议已按10000字符上限截断，发送前必须人工重写或核对。"
            )
        if actions_adjusted:
            must_verify_candidates.append(
                "部分建议操作因输出边界被省略，必须人工补充处置步骤。"
            )
        if references_adjusted:
            must_verify_candidates.append(
                "部分知识引用因输出边界被省略，必须回查原始知识内容。"
            )
        if model_adjusted:
            must_verify_candidates.append(
                "Provider 模型标识已按响应边界规范化，请通过服务日志核对版本。"
            )

        must_verify, must_verify_adjusted = _bounded_unique_items(
            must_verify_candidates,
            max_count=20,
            max_chars=500,
        )
        if must_verify_adjusted:
            verification_limit_hint = (
                "人工核验项已达到20项上限，请按最高风险执行完整人工复核。"
            )
            must_verify = [
                *[
                    item
                    for item in must_verify
                    if item != verification_limit_hint
                ][:19],
                verification_limit_hint,
            ]

        risk_flag_candidates = [
            f"CONTENT_{category.upper()}"
            for category in sorted(set(moderation.value.categories))
        ]
        if moderation.value.decision != "allow":
            risk_flag_candidates.append("HUMAN_REVIEW_REQUIRED")
        if internal_priority in {"P0", "P1"}:
            risk_flag_candidates.append("HIGH_PRIORITY")
        if summary_adjusted:
            risk_flag_candidates.append("SUMMARY_TRUNCATED")
        if reply_adjusted:
            risk_flag_candidates.append("SUGGESTED_REPLY_TRUNCATED")
        if actions_adjusted:
            risk_flag_candidates.append("SUGGESTED_ACTIONS_TRUNCATED")
        if references_adjusted:
            risk_flag_candidates.extend(
                ["KNOWLEDGE_REFERENCES_TRUNCATED", "HUMAN_REVIEW_REQUIRED"]
            )
        if must_verify_adjusted:
            risk_flag_candidates.append("MUST_VERIFY_TRUNCATED")
        if model_adjusted:
            risk_flag_candidates.append("MODEL_ID_TRUNCATED")

        risk_flags, risk_flags_adjusted = _bounded_unique_items(
            sorted(risk_flag_candidates),
            max_count=20,
            max_chars=100,
        )
        if risk_flags_adjusted:
            required_flags = ["HUMAN_REVIEW_REQUIRED", "RISK_FLAGS_TRUNCATED"]
            risk_flags = [
                *[
                    flag for flag in risk_flags if flag not in required_flags
                ][:18],
                *required_flags,
            ]

        external_category = {
            "account": "ACCOUNT",
            "billing": "BILLING",
            "technical": "TECHNICAL",
            "security": "SECURITY",
            "product": "PRODUCT",
            "other": "OTHER",
        }[internal_category]
        external_priority = {
            "P0": "URGENT",
            "P1": "HIGH",
            "P2": "MEDIUM",
            "P3": "LOW",
        }[internal_priority]
        return CustomerServiceSuggestResponse(
            summary=summary,
            suggested_reply=suggested_reply,
            suggested_category=external_category,
            suggested_priority=external_priority,
            confidence=classification.value.confidence,
            risk_flags=sorted(set(risk_flags)),
            knowledge_references=knowledge_references,
            degraded=False,
            degradation_reason=None,
            api_version=resolved_settings.api_version,
            request_id=_request_id(request),
            suggested_actions=suggested_actions,
            must_verify=must_verify,
            model=model_label,
        )

    return application


app = create_app()
