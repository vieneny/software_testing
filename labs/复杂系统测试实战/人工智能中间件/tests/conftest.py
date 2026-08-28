from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from ai_middleware.app import create_app
from ai_middleware.config import Settings
from ai_middleware.providers.mock import MockProvider


@pytest.fixture
def client() -> Iterator[TestClient]:
    app = create_app(settings=Settings(), provider=MockProvider())
    with TestClient(app) as test_client:
        yield test_client
