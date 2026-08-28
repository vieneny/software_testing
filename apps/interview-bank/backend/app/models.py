"""Pydantic request models used by the local learning API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


ProgressStatus = Literal["not_started", "learning", "review", "mastered"]
TargetRole = Literal[
    "软件测试工程师",
    "自动化测试工程师",
    "测试开发工程师",
    "AI 测试工程师",
    "性能测试工程师",
]


class ProgressUpdate(BaseModel):
    status: ProgressStatus | None = None
    favorite: bool | None = None
    note: str | None = Field(default=None, max_length=5000)
    score: int | None = Field(default=None, ge=0, le=5)


class InterviewCreate(BaseModel):
    learner_id: str = Field(default="local-learner", min_length=1, max_length=80)
    template_id: str = Field(default="standard", min_length=1, max_length=50)
    count: int | None = Field(default=None, ge=1, le=50)
    module_ids: list[str] = Field(default_factory=list, max_length=10)
    level: Literal["基础", "入门", "进阶", "高级"] | None = None
    role: TargetRole | None = None
    seed: int | None = None

    @field_validator("learner_id")
    @classmethod
    def learner_id_is_local_identifier(cls, value: str) -> str:
        value = value.strip()
        if not value or any(char in value for char in "/\\\n\r\t"):
            raise ValueError("learner_id 只能是本地学习标识")
        return value

    @field_validator("module_ids")
    @classmethod
    def module_ids_are_valid(cls, values: list[str]) -> list[str]:
        normalized = [str(value).zfill(2) for value in values]
        if any(value not in {f"{index:02d}" for index in range(1, 11)} for value in normalized):
            raise ValueError("module_ids 必须位于 01 到 10")
        return list(dict.fromkeys(normalized))


class InterviewAnswerUpdate(BaseModel):
    answer: str = Field(default="", max_length=20_000)
    self_score: int | None = Field(default=None, ge=0, le=5)
    notes: str = Field(default="", max_length=5000)


class InterviewStatusUpdate(BaseModel):
    status: Literal["active", "completed", "abandoned"]
