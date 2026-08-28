from typing import Protocol

from app.domain.questions.entities import Answer, Question


class IdempotencyKeyConflictError(Exception):
    """同一幂等键被用于不同的规范化请求。"""


class QuestionClosedError(Exception):
    """关闭的问题不再接受新回答。"""


class QuestionRepository(Protocol):
    def list(
        self,
        *,
        page: int,
        page_size: int,
        keyword: str | None,
        tag: str | None,
    ) -> tuple[list[Question], int]: ...

    def create(
        self,
        question: Question,
        *,
        idempotency_key: str | None = None,
        fingerprint: str | None = None,
    ) -> tuple[Question, bool]: ...

    def get(self, question_id: str, *, increase_views: bool = False) -> Question | None: ...

    def add_answer(
        self,
        question_id: str,
        answer: Answer,
        *,
        idempotency_key: str | None = None,
        fingerprint: str | None = None,
    ) -> tuple[Answer | None, bool]: ...

    def update_status(self, question_id: str, status: str) -> Question | None: ...

    def set_answer_acceptance(
        self,
        question_id: str,
        answer_id: str,
        accepted: bool,
    ) -> tuple[Question | None, bool]: ...

    def cast_vote(
        self, question_id: str, voter_key: str, value: int
    ) -> tuple[Question | None, bool]: ...
