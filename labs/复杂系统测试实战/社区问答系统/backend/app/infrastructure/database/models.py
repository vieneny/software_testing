from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.questions.entities import utc_now
from app.infrastructure.database.base import Base


def cross_dialect_long_text():
    """SQLite 使用 TEXT，MySQL 使用可容纳大型 Unicode 正文的 LONGTEXT。"""
    return Text().with_variant(mysql.LONGTEXT(), "mysql")


class QuestionModel(Base):
    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    content: Mapped[str] = mapped_column(cross_dialect_long_text(), nullable=False)
    author_name: Mapped[str] = mapped_column(String(50), nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open", index=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )

    answers: Mapped[list["AnswerModel"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="AnswerModel.created_at",
    )
    votes: Mapped[list["VoteModel"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint("score >= -1000000", name="ck_question_score_lower_bound"),
        Index("ix_questions_status_created_at", "status", "created_at"),
    )


class AnswerModel(Base):
    __tablename__ = "answers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    question_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(cross_dialect_long_text(), nullable=False)
    author_name: Mapped[str] = mapped_column(String(50), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_accepted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )

    question: Mapped[QuestionModel] = relationship(back_populates="answers")


class VoteModel(Base):
    __tablename__ = "question_votes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    question_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    voter_key: Mapped[str] = mapped_column(String(64), nullable=False)
    value: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )

    question: Mapped[QuestionModel] = relationship(back_populates="votes")

    __table_args__ = (
        UniqueConstraint("question_id", "voter_key", name="uq_vote_question_voter"),
        CheckConstraint("value IN (-1, 1)", name="ck_vote_value"),
    )


class IdempotencyRecordModel(Base):
    """保存写请求结果，使网络重试不会重复创建业务数据。"""

    __tablename__ = "idempotency_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope: Mapped[str] = mapped_column(String(100), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(36), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )

    __table_args__ = (
        UniqueConstraint("scope", "idempotency_key", name="uq_idempotency_scope_key"),
        Index("ix_idempotency_records_created_at", "created_at"),
    )


def model_metadata_snapshot() -> dict[str, Any]:
    """给架构测试提供一个无需连接数据库的元数据快照。"""
    return {
        "tables": sorted(Base.metadata.tables),
        "question_indexes": [index.name for index in QuestionModel.__table__.indexes],
    }
