"""Application path and runtime configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
BANK_DIR = BACKEND_DIR.parent


@dataclass(frozen=True)
class Settings:
    catalog_path: Path
    legacy_coverage_path: Path
    database_path: Path
    frontend_dist: Path
    cors_origins: tuple[str, ...]
    xiaolincoding_coverage_path: Path | None = None
    source_snapshots_manifest_path: Path | None = None


def load_settings() -> Settings:
    runtime_dir = BACKEND_DIR / ".runtime"
    raw_origins = os.getenv(
        "INTERVIEW_BANK_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000,http://127.0.0.1:8000",
    )
    return Settings(
        catalog_path=Path(
            os.getenv("INTERVIEW_BANK_CATALOG", str(BANK_DIR / "data" / "questions.json"))
        ).resolve(),
        legacy_coverage_path=Path(
            os.getenv(
                "INTERVIEW_BANK_LEGACY_COVERAGE",
                str(BANK_DIR / "data" / "legacy-coverage.json"),
            )
        ).resolve(),
        database_path=Path(
            os.getenv("INTERVIEW_BANK_DB", str(runtime_dir / "interview-bank.db"))
        ).resolve(),
        frontend_dist=Path(
            os.getenv("INTERVIEW_BANK_FRONTEND_DIST", str(BANK_DIR / "frontend" / "dist"))
        ).resolve(),
        cors_origins=tuple(origin.strip() for origin in raw_origins.split(",") if origin.strip()),
        xiaolincoding_coverage_path=Path(
            os.getenv(
                "INTERVIEW_BANK_XIAOLINCODING_COVERAGE",
                str(BANK_DIR / "data" / "xiaolincoding-coverage.json"),
            )
        ).resolve(),
        source_snapshots_manifest_path=Path(
            os.getenv(
                "INTERVIEW_BANK_SOURCE_SNAPSHOTS_MANIFEST",
                str(BANK_DIR / "data" / "source-snapshots" / "manifest.json"),
            )
        ).resolve(),
    )
