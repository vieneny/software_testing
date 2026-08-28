from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


BACKEND_DIR = Path(__file__).resolve().parents[1]
BANK_DIR = BACKEND_DIR.parent


def settings_for(tmp_path: Path) -> Settings:
    return Settings(
        catalog_path=BANK_DIR / "data" / "questions.json",
        legacy_coverage_path=BANK_DIR / "data" / "legacy-coverage.json",
        database_path=tmp_path / "runtime" / "xiaolincoding-quality-test.db",
        frontend_dist=tmp_path / "missing-dist",
        cors_origins=("http://localhost:5173",),
        xiaolincoding_coverage_path=(
            BANK_DIR / "data" / "xiaolincoding-coverage.json"
        ),
    )


def test_real_snapshot_covers_all_21_xiaolincoding_pages(
    tmp_path: Path,
) -> None:
    with TestClient(create_app(settings_for(tmp_path))) as client:
        response = client.get("/api/quality/xiaolincoding-coverage")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["document_count"] == 21
    assert payload["mapped_document_count"] == 21
    assert payload["unmapped_documents"] == []
    assert payload["declared_question_count"] == 1_143
    assert payload["observed_question_count"] == 1_111
    assert payload["question_reference_count"] == 184
    assert sum(item["source_chars"] for item in payload["documents"]) == 672_610
    assert len({item["document_id"] for item in payload["documents"]}) == 21
    assert len({item["url"] for item in payload["documents"]}) == 21

    direct_pages = [
        item
        for item in payload["documents"]
        if item["coverage_mode"] == "direct-bank-reviewed"
    ]
    assert len(direct_pages) == 4
    assert sum(item["observed_question_count"] for item in direct_pages) == 368
    assert all(item["question_ids"] for item in direct_pages)


def test_snapshot_keeps_declared_and_observed_counts_separate(
    tmp_path: Path,
) -> None:
    with TestClient(create_app(settings_for(tmp_path))) as client:
        payload = client.get("/api/quality/xiaolincoding-coverage").json()

    git_page = next(
        item
        for item in payload["documents"]
        if item["document_id"] == "xiaolincoding-git"
    )
    assert git_page["declared_question_count"] == 24
    assert git_page["observed_question_count"] == 23
    assert any("不属于问题" in note for note in git_page["quality_notes"])
