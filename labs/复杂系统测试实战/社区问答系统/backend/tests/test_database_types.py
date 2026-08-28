from sqlalchemy.dialects import mysql, sqlite

from app.infrastructure.database.models import AnswerModel, QuestionModel


def test_question_and_answer_content_use_longtext_only_on_mysql():
    mysql_dialect = mysql.dialect()
    sqlite_dialect = sqlite.dialect()

    for column in (QuestionModel.content, AnswerModel.content):
        assert column.type.compile(dialect=mysql_dialect) == "LONGTEXT"
        assert column.type.compile(dialect=sqlite_dialect) == "TEXT"
