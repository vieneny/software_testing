"""FastAPI application for the local software-testing interview bank."""

from __future__ import annotations

import secrets
import uuid
from pathlib import Path
from typing import Any
from urllib.parse import quote

from fastapi import FastAPI, HTTPException, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .catalog import CatalogRepository, compact_question
from .config import Settings, load_settings
from .interviews import (
    INTERVIEW_TEMPLATES,
    TARGET_ROLE_GROUPS,
    select_questions,
    template_by_id,
)
from .models import (
    InterviewAnswerUpdate,
    InterviewCreate,
    InterviewStatusUpdate,
    ProgressUpdate,
)
from .quality import SourceCoverageRepository
from .source_snapshots import (
    SourceSnapshotAssetNotFound,
    SourceSnapshotIntegrityError,
    SourceSnapshotRepository,
    SourceSnapshotUnavailable,
)
from .storage import LearningStore


def _validate_learner_id(value: str) -> str:
    value = value.strip()
    if not value or len(value) > 80 or any(char in value for char in "/\\\n\r\t"):
        raise HTTPException(status_code=422, detail="learner_id 只能是本地学习标识")
    return value


def _pagination(
    items: list[dict[str, Any]], page: int, page_size: int
) -> tuple[list[dict[str, Any]], int]:
    total = len(items)
    start = (page - 1) * page_size
    return items[start : start + page_size], total


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or load_settings()
    catalog = CatalogRepository(resolved.catalog_path, resolved.legacy_coverage_path)
    xiaolincoding_coverage = SourceCoverageRepository(
        resolved.xiaolincoding_coverage_path,
        set(catalog.by_id),
        source_label="小林 Coding",
        missing_filename="xiaolincoding-coverage.json",
    )
    store = LearningStore(resolved.database_path)
    source_snapshots = SourceSnapshotRepository(
        resolved.source_snapshots_manifest_path
    )

    app = FastAPI(
        title="软件测试面试题库 API",
        version="1.0.0",
        description=(
            "提供题库检索、学习进度、模拟面试、来源快照与覆盖审计能力。"
        ),
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )
    app.state.catalog = catalog
    app.state.xiaolincoding_coverage = xiaolincoding_coverage
    app.state.store = store
    app.state.source_snapshots = source_snapshots
    app.state.settings = resolved
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(resolved.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/v1/health", tags=["system"])
    def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "service": "interview-bank-api",
            "deployment_scope": "local-learning-only",
            "catalog_generated_at": catalog.payload.get("generated_at"),
            "question_count": len(catalog.questions),
            "legacy_coverage_count": len(catalog.coverage),
        }

    @app.get("/api/v1/meta", tags=["catalog"])
    def meta() -> dict[str, Any]:
        return catalog.meta()

    @app.get("/api/v1/modules", tags=["catalog"])
    def modules() -> dict[str, Any]:
        return {"items": catalog.modules(), "total": len(catalog.modules())}

    @app.get("/api/v1/sources", tags=["catalog"])
    def sources() -> dict[str, Any]:
        items: list[dict[str, Any]] = []
        for source in catalog.sources():
            snapshot = source_snapshots.find(
                source["id"], original_url=source.get("url")
            )
            items.append(
                {
                    **source,
                    "snapshot_status": (
                        snapshot["status"] if snapshot else "not_downloaded"
                    ),
                    "snapshot_api": (
                        f"/api/v1/sources/{source['id']}/snapshot"
                        if snapshot
                        else None
                    ),
                }
            )
        return {
            "items": items,
            "total": len(items),
            "snapshot_manifest": source_snapshots.summary(),
        }

    @app.get("/api/v1/source-snapshots", tags=["catalog"])
    def list_source_snapshots() -> dict[str, Any]:
        return {
            **source_snapshots.summary(),
            "items": source_snapshots.list_items(),
        }

    @app.get("/api/v1/sources/{source_id}/snapshot", tags=["catalog"])
    def get_source_snapshot(source_id: str) -> dict[str, Any]:
        if (
            not source_id
            or len(source_id) > 240
            or any(char in source_id for char in "/\\\n\r\t")
        ):
            raise HTTPException(status_code=422, detail="来源标识不合法")
        source_snapshots.refresh_if_changed()
        if source_snapshots.manifest_status == "invalid":
            raise HTTPException(
                status_code=503,
                detail={
                    "code": "snapshot_manifest_invalid",
                    "message": "本地来源快照清单无效",
                    "error": source_snapshots.manifest_error,
                },
            )
        source = catalog.get_source(source_id)
        snapshot = source_snapshots.find(
            source_id,
            original_url=source.get("url") if source else None,
        )
        if snapshot is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "snapshot_not_found",
                    "message": "该来源尚未下载到本地",
                    "source_id": source_id,
                    "manifest_status": source_snapshots.manifest_status,
                },
            )
        try:
            payload = source_snapshots.read(snapshot)
            payload["asset_base_url"] = (
                f"/api/v1/sources/{quote(source_id, safe='')}/assets"
            )
            return payload
        except SourceSnapshotUnavailable as exc:
            raise HTTPException(
                status_code=404 if exc.status == "missing" else 409,
                detail={
                    "code": "snapshot_unavailable",
                    "message": str(exc),
                    "source_id": snapshot["source_id"],
                    "status": exc.status,
                },
            ) from exc
        except SourceSnapshotIntegrityError as exc:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "snapshot_integrity_error",
                    "message": str(exc),
                    "source_id": snapshot["source_id"],
                },
            ) from exc

    @app.get(
        "/api/v1/sources/{source_id}/assets/{asset_id}",
        tags=["catalog"],
        response_class=Response,
    )
    def get_source_snapshot_asset(source_id: str, asset_id: str) -> Response:
        if (
            not source_id
            or len(source_id) > 240
            or any(char in source_id for char in "/\\\n\r\t")
        ):
            raise HTTPException(status_code=422, detail="来源标识不合法")
        if (
            not asset_id
            or len(asset_id) > 240
            or any(char in asset_id for char in "/\\\n\r\t")
        ):
            raise HTTPException(status_code=422, detail="图片标识不合法")

        source_snapshots.refresh_if_changed()
        if source_snapshots.manifest_status == "invalid":
            raise HTTPException(
                status_code=503,
                detail={
                    "code": "snapshot_manifest_invalid",
                    "message": "本地来源快照清单无效",
                    "error": source_snapshots.manifest_error,
                },
            )
        source = catalog.get_source(source_id)
        snapshot = source_snapshots.find(
            source_id,
            original_url=source.get("url") if source else None,
        )
        if snapshot is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "snapshot_not_found",
                    "message": "该来源尚未下载到本地",
                    "source_id": source_id,
                    "manifest_status": source_snapshots.manifest_status,
                },
            )
        try:
            content, asset = source_snapshots.read_asset(snapshot, asset_id)
        except SourceSnapshotAssetNotFound as exc:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "snapshot_asset_not_found",
                    "message": str(exc),
                    "source_id": snapshot["source_id"],
                    "asset_id": asset_id,
                },
            ) from exc
        except SourceSnapshotUnavailable as exc:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "snapshot_asset_unavailable",
                    "message": str(exc),
                    "source_id": snapshot["source_id"],
                    "asset_id": asset_id,
                    "status": exc.status,
                },
            ) from exc
        except SourceSnapshotIntegrityError as exc:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "snapshot_asset_integrity_error",
                    "message": str(exc),
                    "source_id": snapshot["source_id"],
                    "asset_id": asset_id,
                },
            ) from exc
        return Response(
            content=content,
            media_type=asset["content_type"],
            headers={
                "Cache-Control": "private, no-cache",
                "Content-Security-Policy": "default-src 'none'; sandbox",
                "X-Content-Type-Options": "nosniff",
            },
        )

    @app.get("/api/quality/xiaolincoding-coverage", tags=["quality"])
    def xiaolincoding_source_coverage() -> dict[str, Any]:
        return xiaolincoding_coverage.report()

    @app.get("/api/v1/questions", tags=["questions"])
    def list_questions(
        q: str | None = Query(default=None, max_length=120),
        module_id: str | None = Query(default=None, pattern=r"^(0[1-9]|10)$"),
        level: str | None = Query(default=None, pattern=r"^(基础|入门|进阶|高级)$"),
        kind: str | None = Query(
            default=None, pattern=r"^(知识题|场景题|项目题|行为题|实操题)$"
        ),
        origin: str | None = Query(default=None, max_length=40),
        role: str | None = Query(default=None, max_length=40),
        tag: str | None = Query(default=None, max_length=40),
        question_id: list[str] | None = Query(default=None),
        learner_id: str | None = Query(default=None, max_length=80),
        include_answer: bool = False,
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
    ) -> dict[str, Any]:
        normalized_level = "入门" if level == "基础" else level
        requested_question_ids: set[str] | None = None
        if question_id is not None:
            if len(question_id) > 500 or any(
                not value
                or len(value) > 100
                or any(char in value for char in "/\\\n\r\t")
                for value in question_id
            ):
                raise HTTPException(
                    status_code=422,
                    detail="question_id 数量或格式不合法",
                )
            requested_question_ids = set(question_id)
        filtered = catalog.filter_questions(
            q=q,
            module_id=module_id,
            level=normalized_level,
            kind=kind,
            origin=origin,
            role=role,
            tag=tag,
            question_ids=requested_question_ids,
        )
        page_items, total = _pagination(filtered, page, page_size)
        progress_by_id: dict[str, dict[str, Any]] = {}
        if learner_id:
            learner_id = _validate_learner_id(learner_id)
            progress_by_id = {
                item["question_id"]: item for item in store.get_progress(learner_id)
            }
        items: list[dict[str, Any]] = []
        for question in page_items:
            item = dict(question) if include_answer else compact_question(question)
            item["progress"] = progress_by_id.get(question["id"])
            items.append(item)
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size,
        }

    @app.get("/api/v1/questions/{question_id}", tags=["questions"])
    def get_question(
        question_id: str,
        learner_id: str | None = Query(default=None, max_length=80),
    ) -> dict[str, Any]:
        question = catalog.get_question(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="题目不存在")
        item = dict(question)
        item["progress"] = (
            store.get_question_progress(_validate_learner_id(learner_id), question_id)
            if learner_id
            else None
        )
        return item

    @app.get("/api/v1/legacy-coverage", tags=["catalog"])
    def legacy_coverage(
        source_id: str | None = Query(default=None, max_length=40),
        mapping_status: str | None = Query(default=None, max_length=50),
        q: str | None = Query(default=None, max_length=120),
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=50, ge=1, le=200),
    ) -> dict[str, Any]:
        filtered = catalog.filter_coverage(
            source_id=source_id, mapping_status=mapping_status, q=q
        )
        page_items, total = _pagination(filtered, page, page_size)
        return {
            "items": page_items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "statistics": catalog.coverage_payload.get("statistics", {}),
            "policy": catalog.coverage_payload.get("policy", {}),
        }

    @app.get("/api/v1/progress/{learner_id}", tags=["learning"])
    def get_progress(learner_id: str) -> dict[str, Any]:
        learner_id = _validate_learner_id(learner_id)
        items = store.get_progress(learner_id)
        return {
            "learner_id": learner_id,
            "items": items,
            "summary": store.progress_summary(learner_id),
        }

    @app.put(
        "/api/v1/progress/{learner_id}/{question_id}",
        tags=["learning"],
    )
    def update_progress(
        learner_id: str, question_id: str, update: ProgressUpdate
    ) -> dict[str, Any]:
        learner_id = _validate_learner_id(learner_id)
        if not catalog.get_question(question_id):
            raise HTTPException(status_code=404, detail="题目不存在")
        changes = update.model_dump(exclude_unset=True)
        if not changes:
            raise HTTPException(status_code=422, detail="至少提交一个学习进度字段")
        return store.upsert_progress(learner_id, question_id, changes)

    @app.get("/api/v1/interview-templates", tags=["interviews"])
    def interview_templates() -> dict[str, Any]:
        return {"items": INTERVIEW_TEMPLATES, "total": len(INTERVIEW_TEMPLATES)}

    def render_session(
        session: dict[str, Any], *, reveal_answers: bool = False
    ) -> dict[str, Any]:
        question_items: list[dict[str, Any]] = []
        for position, question_id in enumerate(session["question_ids"], start=1):
            question = catalog.get_question(question_id)
            if not question:
                continue
            item = dict(question) if reveal_answers else compact_question(question)
            item["interview_position"] = position
            item["submitted_answer"] = session["answers"].get(question_id)
            question_items.append(item)
        return {**session, "questions": question_items}

    @app.post(
        "/api/v1/interviews",
        tags=["interviews"],
        status_code=status.HTTP_201_CREATED,
    )
    def create_interview(request: InterviewCreate) -> dict[str, Any]:
        template = template_by_id(request.template_id)
        if not template:
            raise HTTPException(status_code=404, detail="模拟面试模板不存在")
        module_ids = request.module_ids or list(template["module_ids"])
        count = request.count or int(template["default_count"])
        seed = request.seed if request.seed is not None else secrets.randbelow(2**31)
        normalized_level = "入门" if request.level == "基础" else request.level
        question_ids = select_questions(
            catalog.questions,
            module_ids=module_ids,
            count=count,
            level=normalized_level,
            seed=seed,
            role_names=TARGET_ROLE_GROUPS.get(request.role or ""),
        )
        if not question_ids:
            raise HTTPException(status_code=422, detail="当前筛选条件没有可用题目")
        if len(question_ids) < count:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"当前岗位与难度组合只有 {len(question_ids)} 道题，"
                    f"少于请求的 {count} 道；请降低题数或调整难度"
                ),
            )
        session = store.create_session(
            session_id=str(uuid.uuid4()),
            learner_id=request.learner_id,
            template_id=request.template_id,
            question_ids=question_ids,
            seed=seed,
        )
        # The Vue client hides these answers until the learner clicks “揭示答案”.
        # Returning them here keeps that flow usable without an extra request.
        result = render_session(session, reveal_answers=True)
        result["requested_count"] = count
        result["actual_count"] = len(question_ids)
        result["role"] = request.role
        return result

    @app.get("/api/v1/interviews/{session_id}", tags=["interviews"])
    def get_interview(
        session_id: str, reveal_answers: bool = Query(default=False)
    ) -> dict[str, Any]:
        session = store.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="模拟面试会话不存在")
        return render_session(session, reveal_answers=reveal_answers)

    @app.put(
        "/api/v1/interviews/{session_id}/answers/{question_id}",
        tags=["interviews"],
    )
    def save_interview_answer(
        session_id: str, question_id: str, update: InterviewAnswerUpdate
    ) -> dict[str, Any]:
        session = store.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="模拟面试会话不存在")
        if session["status"] != "active":
            raise HTTPException(status_code=409, detail="该模拟面试已结束")
        if question_id not in session["question_ids"]:
            raise HTTPException(status_code=404, detail="该题不属于本次模拟面试")
        next_index = session["question_ids"].index(question_id) + 1
        updated = store.save_answer(
            session_id,
            question_id,
            answer=update.answer,
            self_score=update.self_score,
            notes=update.notes,
            next_index=next_index,
        )
        return render_session(updated)

    @app.put("/api/v1/interviews/{session_id}/status", tags=["interviews"])
    def update_interview_status(
        session_id: str, update: InterviewStatusUpdate
    ) -> dict[str, Any]:
        session = store.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="模拟面试会话不存在")
        updated = store.update_session_status(session_id, update.status)
        return render_session(updated, reveal_answers=update.status == "completed")

    if resolved.frontend_dist.exists():
        assets_dir = resolved.frontend_dist / "assets"
        if assets_dir.exists():
            app.mount(
                "/assets",
                StaticFiles(directory=assets_dir),
                name="frontend-assets",
            )

        @app.get("/", include_in_schema=False)
        def frontend_index() -> FileResponse:
            return FileResponse(resolved.frontend_dist / "index.html")

    else:

        @app.get("/", include_in_schema=False)
        def api_index() -> dict[str, str]:
            return {
                "name": "软件测试面试题库 API",
                "docs": "/api/docs",
                "health": "/api/v1/health",
            }

    return app


app = create_app()
