from math import ceil
from typing import Annotated

from fastapi import APIRouter, Header, Query, Request, Response
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.request_id import get_request_id
from app.interfaces.api.dependencies import (
    AIClientDependency,
    QuestionServiceDependency,
    SessionDependency,
)
from app.interfaces.api.schemas import (
    AISummaryResponse,
    AnswerAcceptanceUpdate,
    AnswerCreate,
    AnswerResponse,
    HealthResponse,
    QuestionCreate,
    QuestionDetailResponse,
    QuestionPageResponse,
    QuestionStatusUpdate,
    QuestionSummaryResponse,
    VoteCreate,
    VoteResponse,
)

api_router = APIRouter()

IdempotencyKeyHeader = Annotated[
    str | None,
    Header(
        alias="Idempotency-Key",
        min_length=8,
        max_length=128,
        pattern=r"^[A-Za-z0-9._:-]+$",
        description="同一业务请求重试时复用；修改内容后必须换新键",
    ),
]


@api_router.get("/health", response_model=HealthResponse, tags=["系统"])
def health(session: SessionDependency) -> HealthResponse:
    settings = get_settings()
    try:
        session.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise AppError(
            code="database_unavailable",
            message="数据库暂时不可用",
            status_code=503,
        ) from exc
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version="0.1.0",
        database="up",
        ai_configured=bool(settings.ai_base_url),
    )


@api_router.get("/questions", response_model=QuestionPageResponse, tags=["问题"])
def list_questions(
    service: QuestionServiceDependency,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: str | None = Query(default=None, max_length=100),
    tag: str | None = Query(default=None, max_length=30),
) -> QuestionPageResponse:
    questions, total = service.list_questions(
        page=page, page_size=page_size, keyword=keyword, tag=tag
    )
    return QuestionPageResponse(
        items=[QuestionSummaryResponse.from_entity(item) for item in questions],
        page=page,
        page_size=page_size,
        total=total,
        total_pages=ceil(total / page_size) if total else 0,
    )


@api_router.post(
    "/questions",
    response_model=QuestionDetailResponse,
    status_code=201,
    responses={
        200: {
            "model": QuestionDetailResponse,
            "description": "幂等重放，返回首次创建的问题",
        }
    },
    tags=["问题"],
)
def create_question(
    payload: QuestionCreate,
    response: Response,
    service: QuestionServiceDependency,
    idempotency_key: IdempotencyKeyHeader = None,
) -> QuestionDetailResponse:
    question, replayed = service.create_question(
        **payload.model_dump(),
        idempotency_key=idempotency_key,
    )
    if idempotency_key is not None:
        response.headers["Idempotency-Replayed"] = str(replayed).lower()
    if replayed:
        response.status_code = 200
    return QuestionDetailResponse.from_entity(question)


@api_router.get(
    "/questions/{question_id}", response_model=QuestionDetailResponse, tags=["问题"]
)
def get_question(
    question_id: str, service: QuestionServiceDependency
) -> QuestionDetailResponse:
    return QuestionDetailResponse.from_entity(service.get_question(question_id))


@api_router.post(
    "/questions/{question_id}/answers",
    response_model=AnswerResponse,
    status_code=201,
    responses={
        200: {
            "model": AnswerResponse,
            "description": "幂等重放，返回首次创建的回答",
        }
    },
    tags=["回答"],
)
def add_answer(
    question_id: str,
    payload: AnswerCreate,
    response: Response,
    service: QuestionServiceDependency,
    idempotency_key: IdempotencyKeyHeader = None,
) -> AnswerResponse:
    answer, replayed = service.add_answer(
        question_id,
        **payload.model_dump(),
        idempotency_key=idempotency_key,
    )
    if idempotency_key is not None:
        response.headers["Idempotency-Replayed"] = str(replayed).lower()
    if replayed:
        response.status_code = 200
    return AnswerResponse.from_entity(answer)


@api_router.patch(
    "/questions/{question_id}/status",
    response_model=QuestionDetailResponse,
    tags=["问题"],
)
def update_question_status(
    question_id: str,
    payload: QuestionStatusUpdate,
    service: QuestionServiceDependency,
) -> QuestionDetailResponse:
    question = service.update_status(question_id, payload.status)
    return QuestionDetailResponse.from_entity(question)


@api_router.put(
    "/questions/{question_id}/answers/{answer_id}/acceptance",
    response_model=QuestionDetailResponse,
    tags=["回答"],
)
def update_answer_acceptance(
    question_id: str,
    answer_id: str,
    payload: AnswerAcceptanceUpdate,
    service: QuestionServiceDependency,
) -> QuestionDetailResponse:
    question = service.set_answer_acceptance(
        question_id,
        answer_id,
        accepted=payload.accepted,
    )
    return QuestionDetailResponse.from_entity(question)


@api_router.post(
    "/questions/{question_id}/votes", response_model=VoteResponse, tags=["投票"]
)
def cast_vote(
    question_id: str,
    payload: VoteCreate,
    service: QuestionServiceDependency,
) -> VoteResponse:
    question = service.cast_vote(question_id, **payload.model_dump())
    return VoteResponse(question_id=question.id, score=question.score)


@api_router.post(
    "/questions/{question_id}/ai-summary",
    response_model=AISummaryResponse,
    tags=["人工智能"],
)
async def create_ai_summary(
    question_id: str,
    request: Request,
    service: QuestionServiceDependency,
    ai_gateway: AIClientDependency,
) -> AISummaryResponse:
    question = service.get_question(question_id, increase_views=False)
    result = await ai_gateway.summarize_question(
        title=question.title,
        content=question.content,
        answers=[item.content for item in question.answers],
        request_id=get_request_id(request),
    )
    return AISummaryResponse.from_entity(question_id, result)
