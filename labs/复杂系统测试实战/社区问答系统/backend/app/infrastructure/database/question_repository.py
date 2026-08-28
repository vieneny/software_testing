from uuid import uuid4

from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.domain.questions.entities import Answer, Question, utc_now
from app.domain.questions.repository import (
    IdempotencyKeyConflictError,
    QuestionClosedError,
)
from app.infrastructure.database.models import (
    AnswerModel,
    IdempotencyRecordModel,
    QuestionModel,
    VoteModel,
)


class SqlAlchemyQuestionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    @staticmethod
    def _answer_to_domain(model: AnswerModel) -> Answer:
        return Answer(
            id=model.id,
            question_id=model.question_id,
            content=model.content,
            author_name=model.author_name,
            score=model.score,
            is_accepted=model.is_accepted,
            created_at=model.created_at,
        )

    @classmethod
    def _question_to_domain(cls, model: QuestionModel) -> Question:
        return Question(
            id=model.id,
            title=model.title,
            content=model.content,
            author_name=model.author_name,
            tags=list(model.tags or []),
            status=model.status,
            score=model.score,
            view_count=model.view_count,
            created_at=model.created_at,
            updated_at=model.updated_at,
            answers=[cls._answer_to_domain(item) for item in model.answers],
        )

    @staticmethod
    def _escape_like(value: str) -> str:
        return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

    def list(
        self,
        *,
        page: int,
        page_size: int,
        keyword: str | None,
        tag: str | None,
    ) -> tuple[list[Question], int]:
        filters = []
        if keyword:
            pattern = f"%{self._escape_like(keyword)}%"
            filters.append(
                or_(
                    QuestionModel.title.ilike(pattern, escape="\\"),
                    QuestionModel.content.ilike(pattern, escape="\\"),
                )
            )
        if tag:
            escaped_tag = self._escape_like(tag)
            filters.append(
                cast(QuestionModel.tags, String).ilike(
                    f'%"{escaped_tag}"%',
                    escape="\\",
                )
            )

        count_statement = select(func.count(QuestionModel.id)).where(*filters)
        total = int(self.session.scalar(count_statement) or 0)
        statement = (
            select(QuestionModel)
            .options(selectinload(QuestionModel.answers))
            .where(*filters)
            .order_by(QuestionModel.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        models = self.session.scalars(statement).all()
        return [self._question_to_domain(item) for item in models], total

    def _find_idempotency_record(
        self,
        scope: str,
        idempotency_key: str,
    ) -> IdempotencyRecordModel | None:
        return self.session.scalar(
            select(IdempotencyRecordModel).where(
                IdempotencyRecordModel.scope == scope,
                IdempotencyRecordModel.idempotency_key == idempotency_key,
            )
        )

    @staticmethod
    def _assert_same_fingerprint(
        record: IdempotencyRecordModel,
        fingerprint: str,
    ) -> None:
        if record.fingerprint != fingerprint:
            raise IdempotencyKeyConflictError

    def _store_idempotency_record(
        self,
        *,
        scope: str,
        idempotency_key: str,
        fingerprint: str,
        resource_id: str,
    ) -> None:
        self.session.add(
            IdempotencyRecordModel(
                id=str(uuid4()),
                scope=scope,
                idempotency_key=idempotency_key,
                fingerprint=fingerprint,
                resource_id=resource_id,
            )
        )

    def create(
        self,
        question: Question,
        *,
        idempotency_key: str | None = None,
        fingerprint: str | None = None,
    ) -> tuple[Question, bool]:
        scope = "questions:create"
        if idempotency_key is not None and fingerprint is not None:
            record = self._find_idempotency_record(scope, idempotency_key)
            if record is not None:
                self._assert_same_fingerprint(record, fingerprint)
                existing = self._get_model(record.resource_id)
                if existing is None:
                    raise RuntimeError("幂等记录关联的问题不存在")
                return self._question_to_domain(existing), True

        model = QuestionModel(
            id=question.id,
            title=question.title,
            content=question.content,
            author_name=question.author_name,
            tags=question.tags,
            status=question.status,
            score=question.score,
            view_count=question.view_count,
            created_at=question.created_at,
            updated_at=question.updated_at,
        )
        self.session.add(model)
        if idempotency_key is not None and fingerprint is not None:
            self._store_idempotency_record(
                scope=scope,
                idempotency_key=idempotency_key,
                fingerprint=fingerprint,
                resource_id=question.id,
            )
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            if idempotency_key is None or fingerprint is None:
                raise
            record = self._find_idempotency_record(scope, idempotency_key)
            if record is None:
                raise
            self._assert_same_fingerprint(record, fingerprint)
            existing = self._get_model(record.resource_id)
            if existing is None:
                raise RuntimeError("幂等记录关联的问题不存在") from None
            return self._question_to_domain(existing), True
        model.answers = []
        return self._question_to_domain(model), False

    def _get_model(self, question_id: str) -> QuestionModel | None:
        statement = (
            select(QuestionModel)
            .options(selectinload(QuestionModel.answers))
            .where(QuestionModel.id == question_id)
        )
        return self.session.scalar(statement)

    def _get_model_for_update(self, question_id: str) -> QuestionModel | None:
        statement = (
            select(QuestionModel)
            .options(selectinload(QuestionModel.answers))
            .where(QuestionModel.id == question_id)
            .with_for_update()
        )
        return self.session.scalar(statement)

    def get(self, question_id: str, *, increase_views: bool = False) -> Question | None:
        model = self._get_model(question_id)
        if model is None:
            return None
        if increase_views:
            model.view_count += 1
            self.session.commit()
        return self._question_to_domain(model)

    def add_answer(
        self,
        question_id: str,
        answer: Answer,
        *,
        idempotency_key: str | None = None,
        fingerprint: str | None = None,
    ) -> tuple[Answer | None, bool]:
        scope = f"questions:{question_id}:answers"
        if idempotency_key is not None and fingerprint is not None:
            record = self._find_idempotency_record(scope, idempotency_key)
            if record is not None:
                self._assert_same_fingerprint(record, fingerprint)
                existing = self.session.get(AnswerModel, record.resource_id)
                if existing is None:
                    raise RuntimeError("幂等记录关联的回答不存在")
                return self._answer_to_domain(existing), True

        question = self.session.scalar(
            select(QuestionModel)
            .where(QuestionModel.id == question_id)
            .with_for_update()
        )
        if question is None:
            return None, False
        if question.status != "open":
            raise QuestionClosedError
        model = AnswerModel(
            id=answer.id,
            question_id=question_id,
            content=answer.content,
            author_name=answer.author_name,
            score=answer.score,
            is_accepted=answer.is_accepted,
            created_at=answer.created_at,
        )
        self.session.add(model)
        if idempotency_key is not None and fingerprint is not None:
            self._store_idempotency_record(
                scope=scope,
                idempotency_key=idempotency_key,
                fingerprint=fingerprint,
                resource_id=answer.id,
            )
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            if idempotency_key is None or fingerprint is None:
                raise
            record = self._find_idempotency_record(scope, idempotency_key)
            if record is None:
                raise
            self._assert_same_fingerprint(record, fingerprint)
            existing = self.session.get(AnswerModel, record.resource_id)
            if existing is None:
                raise RuntimeError("幂等记录关联的回答不存在") from None
            return self._answer_to_domain(existing), True
        return self._answer_to_domain(model), False

    def update_status(self, question_id: str, status: str) -> Question | None:
        statement = (
            select(QuestionModel)
            .options(selectinload(QuestionModel.answers))
            .where(QuestionModel.id == question_id)
            .with_for_update()
        )
        question = self.session.scalar(statement)
        if question is None:
            return None
        if question.status != status:
            question.status = status
            question.updated_at = utc_now()
            self.session.commit()
        return self._question_to_domain(question)

    def set_answer_acceptance(
        self,
        question_id: str,
        answer_id: str,
        accepted: bool,
    ) -> tuple[Question | None, bool]:
        statement = (
            select(QuestionModel)
            .options(selectinload(QuestionModel.answers))
            .where(QuestionModel.id == question_id)
            .with_for_update()
        )
        question = self.session.scalar(statement)
        if question is None:
            return None, False

        target = next((item for item in question.answers if item.id == answer_id), None)
        if target is None:
            return self._question_to_domain(question), False

        if accepted:
            for item in question.answers:
                item.is_accepted = item.id == answer_id
        else:
            target.is_accepted = False
        question.updated_at = utc_now()
        self.session.commit()
        return self._question_to_domain(question), True

    def cast_vote(
        self, question_id: str, voter_key: str, value: int
    ) -> tuple[Question | None, bool]:
        # 先锁问题行，再读取用户投票和更新聚合分数。MySQL 中不同 voter 的并发写入
        # 因此也会串行执行，避免两条 Vote 已落库但 score 丢失一次增量；同一 voter
        # 的并发首投会在第二个事务取得锁后读到已有记录，而不是撞唯一约束返回 500。
        question = self._get_model_for_update(question_id)
        if question is None:
            return None, False
        vote = self.session.scalar(
            select(VoteModel).where(
                VoteModel.question_id == question_id,
                VoteModel.voter_key == voter_key,
            )
        )
        if vote is not None and vote.value == value:
            return self._question_to_domain(question), False
        if vote is None:
            vote = VoteModel(
                id=str(uuid4()),
                question_id=question_id,
                voter_key=voter_key,
                value=value,
            )
            self.session.add(vote)
            question.score += value
        else:
            question.score += value - vote.value
            vote.value = value
        self.session.commit()
        return self._question_to_domain(question), True
