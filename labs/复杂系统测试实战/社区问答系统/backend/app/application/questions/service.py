import hashlib
import json

from app.core.errors import ConflictError, NotFoundError
from app.domain.questions.entities import Answer, Question, normalize_tags, validate_vote
from app.domain.questions.repository import (
    IdempotencyKeyConflictError,
    QuestionClosedError,
    QuestionRepository,
)


def _request_fingerprint(payload: dict[str, object]) -> str:
    canonical_json = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


class QuestionService:
    def __init__(self, repository: QuestionRepository) -> None:
        self.repository = repository

    def list_questions(
        self,
        *,
        page: int,
        page_size: int,
        keyword: str | None = None,
        tag: str | None = None,
    ) -> tuple[list[Question], int]:
        normalized_keyword = keyword.strip() if keyword and keyword.strip() else None
        normalized_tag = tag.strip().lower() if tag and tag.strip() else None
        return self.repository.list(
            page=page,
            page_size=page_size,
            keyword=normalized_keyword,
            tag=normalized_tag,
        )

    def create_question(
        self,
        *,
        title: str,
        content: str,
        author_name: str,
        tags: list[str],
        idempotency_key: str | None = None,
    ) -> tuple[Question, bool]:
        question = Question(
            title=title.strip(),
            content=content.strip(),
            author_name=author_name.strip(),
            tags=normalize_tags(tags),
        )
        fingerprint = _request_fingerprint(
            {
                "title": question.title,
                "content": question.content,
                "author_name": question.author_name,
                "tags": question.tags,
            }
        )
        try:
            return self.repository.create(
                question,
                idempotency_key=idempotency_key,
                fingerprint=fingerprint,
            )
        except IdempotencyKeyConflictError as exc:
            raise ConflictError(
                "idempotency_key_reused",
                "该幂等键已用于不同的发布内容，请修改内容后使用新的幂等键",
            ) from exc

    def get_question(self, question_id: str, *, increase_views: bool = True) -> Question:
        question = self.repository.get(question_id, increase_views=increase_views)
        if question is None:
            raise NotFoundError("问题", question_id)
        return question

    def add_answer(
        self,
        question_id: str,
        *,
        content: str,
        author_name: str,
        idempotency_key: str | None = None,
    ) -> tuple[Answer, bool]:
        answer = Answer(
            question_id=question_id,
            content=content.strip(),
            author_name=author_name.strip(),
        )
        fingerprint = _request_fingerprint(
            {
                "question_id": question_id,
                "content": answer.content,
                "author_name": answer.author_name,
            }
        )
        try:
            saved, replayed = self.repository.add_answer(
                question_id,
                answer,
                idempotency_key=idempotency_key,
                fingerprint=fingerprint,
            )
        except IdempotencyKeyConflictError as exc:
            raise ConflictError(
                "idempotency_key_reused",
                "该幂等键已用于不同的回答内容，请修改内容后使用新的幂等键",
            ) from exc
        except QuestionClosedError as exc:
            raise ConflictError(
                "question_closed",
                "问题已关闭，暂时不能提交新回答",
                {"question_id": question_id},
            ) from exc
        if saved is None:
            raise NotFoundError("问题", question_id)
        return saved, replayed

    def update_status(self, question_id: str, status: str) -> Question:
        if status not in {"open", "closed"}:
            raise ConflictError("invalid_question_status", "问题状态只能是 open 或 closed")
        question = self.repository.update_status(question_id, status)
        if question is None:
            raise NotFoundError("问题", question_id)
        return question

    def set_answer_acceptance(
        self,
        question_id: str,
        answer_id: str,
        *,
        accepted: bool,
    ) -> Question:
        question, answer_found = self.repository.set_answer_acceptance(
            question_id,
            answer_id,
            accepted,
        )
        if question is None:
            raise NotFoundError("问题", question_id)
        if not answer_found:
            raise NotFoundError("回答", answer_id)
        return question

    def cast_vote(self, question_id: str, *, voter_key: str, value: int) -> Question:
        try:
            validate_vote(value)
        except ValueError as exc:
            raise ConflictError("invalid_vote", str(exc)) from exc
        question, changed = self.repository.cast_vote(question_id, voter_key.strip(), value)
        if question is None:
            raise NotFoundError("问题", question_id)
        if not changed:
            raise ConflictError(
                "duplicate_vote",
                "该用户已投过相同的票",
                {"question_id": question_id},
            )
        return question
