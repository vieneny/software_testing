from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.questions.service import QuestionService
from app.core.config import get_settings
from app.infrastructure.ai.http_client import HttpAIGateway
from app.infrastructure.database.question_repository import SqlAlchemyQuestionRepository
from app.infrastructure.database.session import get_session

SessionDependency = Annotated[Session, Depends(get_session)]


def get_question_service(session: SessionDependency) -> QuestionService:
    return QuestionService(SqlAlchemyQuestionRepository(session))


def get_ai_gateway() -> HttpAIGateway:
    settings = get_settings()
    return HttpAIGateway(
        base_url=settings.ai_base_url,
        summary_path=settings.ai_summary_path,
        timeout=settings.ai_timeout_seconds,
    )


QuestionServiceDependency = Annotated[QuestionService, Depends(get_question_service)]
AIClientDependency = Annotated[HttpAIGateway, Depends(get_ai_gateway)]
