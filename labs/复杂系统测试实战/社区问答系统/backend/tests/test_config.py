import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_ai_timeout_defaults_to_end_to_end_budget_and_can_be_overridden(monkeypatch):
    monkeypatch.delenv("AI_TIMEOUT_SECONDS", raising=False)
    defaults = Settings(_env_file=None)
    assert defaults.ai_timeout_seconds == 25.0

    monkeypatch.setenv("AI_TIMEOUT_SECONDS", "31")
    overridden = Settings(_env_file=None)
    assert overridden.ai_timeout_seconds == 31.0


@pytest.mark.parametrize("invalid_timeout", ["0", "-1", "121"])
def test_ai_timeout_rejects_unbounded_values(monkeypatch, invalid_timeout):
    monkeypatch.setenv("AI_TIMEOUT_SECONDS", invalid_timeout)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
