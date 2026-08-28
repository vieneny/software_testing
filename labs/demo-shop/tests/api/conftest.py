from __future__ import annotations

import os

import pytest
import requests


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("DEMO_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


@pytest.fixture
def api(base_url: str) -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/json",
            "User-Agent": "software-testing-learning-lab/1.0",
        }
    )
    yield session
    session.close()


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    api_marker = pytest.mark.api
    for item in items:
        if "/tests/api/" in str(item.path).replace("\\", "/"):
            item.add_marker(api_marker)
