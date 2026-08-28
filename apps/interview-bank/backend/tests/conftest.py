from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


BACKEND_DIR = Path(__file__).resolve().parents[1]
BANK_DIR = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import Settings  # noqa: E402
from app.main import create_app  # noqa: E402


@pytest.fixture()
def client(tmp_path: Path) -> TestClient:
    settings = Settings(
        catalog_path=BANK_DIR / "data" / "questions.json",
        legacy_coverage_path=BANK_DIR / "data" / "legacy-coverage.json",
        database_path=tmp_path / "runtime" / "test.db",
        frontend_dist=tmp_path / "missing-dist",
        cors_origins=("http://localhost:5173",),
    )
    with TestClient(create_app(settings)) as test_client:
        yield test_client
