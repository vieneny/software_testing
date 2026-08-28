from datetime import UTC, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.application.ports.ai_gateway import AISummary
from app.domain.questions.entities import Answer, Question

SingleLineText = Annotated[str, StringConstraints(pattern=r"^[^\r\n]+$")]
TagText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=30, pattern=r"^[^\r\n]+$"),
]


def normalize_utc_datetime(value: datetime) -> datetime:
    """数据库无时区值按 UTC 解释，有时区值统一转换为 UTC。"""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


class QuestionCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: SingleLineText = Field(
        min_length=5,
        max_length=200,
        examples=["如何测试幂等接口？"],
    )
    content: str = Field(min_length=10, max_length=20_000)
    author_name: SingleLineText = Field(
        min_length=2,
        max_length=50,
        examples=["学习者001"],
    )
    tags: list[TagText] = Field(default_factory=list, max_length=5)


class AnswerCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    content: str = Field(min_length=5, max_length=20_000)
    author_name: SingleLineText = Field(min_length=2, max_length=50)


class VoteCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    voter_key: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[A-Za-z0-9._:-]+$",
        description="练习环境的合成用户标识",
    )
    value: Literal[-1, 1] = Field(description="赞成传 1，反对传 -1")


class QuestionStatusUpdate(BaseModel):
    status: Literal["open", "closed"] = Field(description="open 允许回答，closed 禁止新回答")


class AnswerAcceptanceUpdate(BaseModel):
    accepted: bool = Field(description="true 采纳该回答，false 取消采纳")


class AnswerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    question_id: str
    content: str
    author_name: str
    score: int
    is_accepted: bool
    created_at: datetime

    @classmethod
    def from_entity(cls, answer: Answer) -> "AnswerResponse":
        return cls(
            id=answer.id,
            question_id=answer.question_id,
            content=answer.content,
            author_name=answer.author_name,
            score=answer.score,
            is_accepted=answer.is_accepted,
            created_at=normalize_utc_datetime(answer.created_at),
        )


class QuestionSummaryResponse(BaseModel):
    id: str
    title: str
    excerpt: str
    author_name: str
    tags: list[str]
    status: str
    score: int
    view_count: int
    answer_count: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, question: Question) -> "QuestionSummaryResponse":
        excerpt = (
            question.content[:157] + "..."
            if len(question.content) > 160
            else question.content
        )
        return cls(
            id=question.id,
            title=question.title,
            excerpt=excerpt,
            author_name=question.author_name,
            tags=question.tags,
            status=question.status,
            score=question.score,
            view_count=question.view_count,
            answer_count=len(question.answers),
            created_at=normalize_utc_datetime(question.created_at),
            updated_at=normalize_utc_datetime(question.updated_at),
        )


class QuestionDetailResponse(BaseModel):
    id: str
    title: str
    content: str
    author_name: str
    tags: list[str]
    status: str
    score: int
    view_count: int
    created_at: datetime
    updated_at: datetime
    answers: list[AnswerResponse]

    @classmethod
    def from_entity(cls, question: Question) -> "QuestionDetailResponse":
        return cls(
            id=question.id,
            title=question.title,
            content=question.content,
            author_name=question.author_name,
            tags=question.tags,
            status=question.status,
            score=question.score,
            view_count=question.view_count,
            created_at=normalize_utc_datetime(question.created_at),
            updated_at=normalize_utc_datetime(question.updated_at),
            answers=[AnswerResponse.from_entity(item) for item in question.answers],
        )


class QuestionPageResponse(BaseModel):
    items: list[QuestionSummaryResponse]
    page: int
    page_size: int
    total: int
    total_pages: int


class VoteResponse(BaseModel):
    question_id: str
    score: int


class AISummaryResponse(BaseModel):
    question_id: str
    summary: str
    risk_hints: list[str]
    model: str

    @classmethod
    def from_entity(cls, question_id: str, result: AISummary) -> "AISummaryResponse":
        return cls(
            question_id=question_id,
            summary=result.summary,
            risk_hints=result.risk_hints,
            model=result.model,
        )


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    database: str
    ai_configured: bool
