from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(slots=True)
class Answer:
    content: str
    author_name: str
    id: str = field(default_factory=lambda: str(uuid4()))
    question_id: str = ""
    score: int = 0
    is_accepted: bool = False
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class Question:
    title: str
    content: str
    author_name: str
    tags: list[str]
    id: str = field(default_factory=lambda: str(uuid4()))
    status: str = "open"
    score: int = 0
    view_count: int = 0
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
    answers: list[Answer] = field(default_factory=list)


def normalize_tags(tags: list[str]) -> list[str]:
    normalized: list[str] = []
    for tag in tags:
        clean = tag.strip().lower()
        if clean and clean not in normalized:
            normalized.append(clean)
    return normalized[:5]


def validate_vote(value: int) -> None:
    if value not in (-1, 1):
        raise ValueError("投票值只能是 1 或 -1")
