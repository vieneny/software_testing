from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_meta_modules_and_sources(client: TestClient) -> None:
    health = client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert health.json()["question_count"] == 470
    assert health.json()["legacy_coverage_count"] == 160

    meta = client.get("/api/v1/meta").json()
    assert meta["statistics"]["reviewed_core_questions"] == 172
    assert meta["statistics"]["curated_questions"] == 298
    assert "privacy_policy" not in meta
    assert meta["facets"]["roles"]["性能测试"] >= 59

    modules = client.get("/api/v1/modules").json()
    assert modules["total"] == 10
    assert sum(item["question_count"] for item in modules["items"]) == 470

    sources = client.get("/api/v1/sources").json()
    assert sources["total"] == 101
    assert all("usage" in item for item in sources["items"])


def test_question_filter_pagination_and_detail(client: TestClient) -> None:
    response = client.get(
        "/api/v1/questions",
        params={"module_id": "09", "page_size": 100},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 21
    assert all(item["module_id"] == "09" for item in payload["items"])
    assert all("answer" not in item for item in payload["items"])

    performance_role = client.get(
        "/api/v1/questions",
        params={"role": "性能测试", "page_size": 100},
    ).json()
    assert performance_role["total"] >= 22
    assert all(
        "性能测试" in item["roles"] for item in performance_role["items"]
    )

    full = client.get(
        "/api/v1/questions",
        params={"origin": "curated-2026", "include_answer": "true", "page_size": 100},
    ).json()
    assert full["total"] == 24
    assert all(item["answer"] and item["explanation"] for item in full["items"])

    selected_ids = [item["id"] for item in full["items"][:3]]
    selected_page = client.get(
        "/api/v1/questions",
        params={
            "question_id": selected_ids,
            "include_answer": "true",
            "page_size": 2,
        },
    ).json()
    assert selected_page["total"] == 3
    assert len(selected_page["items"]) == 2
    assert {item["id"] for item in selected_page["items"]} <= set(selected_ids)

    supplemental = client.get(
        "/api/v1/questions",
        params={
            "origin": "supplemental-reviewed",
            "include_answer": "true",
            "page_size": 100,
        },
    ).json()
    assert supplemental["total"] == 52
    assert all(
        item["answer"] and item["explanation"]
        for item in supplemental["items"]
    )

    xiaolincoding = client.get(
        "/api/v1/questions",
        params={
            "origin": "xiaolincoding-reviewed",
            "include_answer": "true",
            "page_size": 100,
        },
    ).json()
    assert xiaolincoding["total"] == 62
    assert all(
        item["answer"] and item["explanation"]
        for item in xiaolincoding["items"]
    )

    first_edition = client.get(
        "/api/v1/questions",
        params={
            "origin": "personal-latest-reviewed",
            "include_answer": "true",
            "page_size": 100,
        },
    ).json()
    assert first_edition["total"] == 160
    assert len(first_edition["items"]) == 100
    assert all(
        item["answer"] and item["answer_strategy"] and item["explanation"]
        for item in first_edition["items"]
    )

    question_id = full["items"][0]["id"]
    detail = client.get(f"/api/v1/questions/{question_id}")
    assert detail.status_code == 200
    assert detail.json()["id"] == question_id
    assert detail.json()["answer"]

    missing = client.get("/api/v1/questions/not-found")
    assert missing.status_code == 404


def test_search_covers_answers_and_natural_chinese_wording(client: TestClient) -> None:
    natural = client.get(
        "/api/v1/questions",
        params={"q": "音频上传", "include_answer": "true", "page_size": 20},
    )
    assert natural.status_code == 200
    assert "2026-functional-audio-upload" in {
        item["id"] for item in natural.json()["items"]
    }

    answer_text = client.get(
        "/api/v1/questions",
        params={"q": "single-flight", "include_answer": "true", "page_size": 20},
    )
    assert answer_text.status_code == 200
    assert "2026-automation-token-refresh" in {
        item["id"] for item in answer_text.json()["items"]
    }


def test_personal_latest_coverage_is_queryable(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/legacy-coverage",
        params={"source_id": "personal-latest-outline", "page_size": 200},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 160
    assert len(payload["items"]) == 160
    assert all("question_intent" in item for item in payload["items"])
    assert all("answer" not in item for item in payload["items"])
    assert all(
        item["answer_policy"] == "reviewed-answer-in-personal-latest-bank"
        for item in payload["items"]
    )

    strong_legacy_search = client.get(
        "/api/v1/questions",
        params={"q": "无法重现的BUG", "page_size": 20},
    ).json()
    assert any(
        item["origin"] == "personal-latest-reviewed"
        and "无法重现" in item["title"]
        for item in strong_legacy_search["items"]
    )

    first_edition_search = client.get(
        "/api/v1/questions",
        params={"q": "杯子功能测试思路", "page_size": 20},
    ).json()
    assert any(
        item["origin"] == "personal-latest-reviewed"
        and "杯子" in item["title"]
        for item in first_edition_search["items"]
    )


def test_progress_is_persisted_and_merged(client: TestClient) -> None:
    question_id = "core-01-01"
    first = client.put(
        f"/api/v1/progress/alice/{question_id}",
        json={"status": "learning", "favorite": True, "note": "复习风险测试", "score": 3},
    )
    assert first.status_code == 200
    assert first.json()["favorite"] is True

    second = client.put(
        f"/api/v1/progress/alice/{question_id}",
        json={"status": "mastered", "score": 5},
    )
    assert second.status_code == 200
    assert second.json()["status"] == "mastered"
    assert second.json()["note"] == "复习风险测试"
    assert second.json()["favorite"] is True

    progress = client.get("/api/v1/progress/alice").json()
    assert progress["summary"]["mastered"] == 1
    assert progress["summary"]["favorites"] == 1
    detail = client.get(
        f"/api/v1/questions/{question_id}", params={"learner_id": "alice"}
    ).json()
    assert detail["progress"]["score"] == 5


def test_progress_validation(client: TestClient) -> None:
    assert (
        client.put(
            "/api/v1/progress/alice/not-found", json={"status": "learning"}
        ).status_code
        == 404
    )
    assert (
        client.put(
            "/api/v1/progress/alice/core-01-01", json={"score": 9}
        ).status_code
        == 422
    )
    assert (
        client.put("/api/v1/progress/alice/core-01-01", json={}).status_code == 422
    )


def test_mock_interview_full_lifecycle(client: TestClient) -> None:
    templates = client.get("/api/v1/interview-templates").json()
    assert {item["id"] for item in templates["items"]} >= {
        "quick",
        "standard",
        "full",
        "automation",
        "ai-testing",
    }

    created = client.post(
        "/api/v1/interviews",
        json={
            "learner_id": "alice",
            "template_id": "standard",
            "count": 8,
            "seed": 20260729,
        },
    )
    assert created.status_code == 201
    session = created.json()
    assert session["actual_count"] == 8
    assert len({item["module_id"] for item in session["questions"]}) == 8
    assert all("answer" in item for item in session["questions"])

    session_id = session["id"]
    question_id = session["question_ids"][0]
    answered = client.put(
        f"/api/v1/interviews/{session_id}/answers/{question_id}",
        json={"answer": "先说明风险和范围。", "self_score": 4, "notes": "补充证据链"},
    )
    assert answered.status_code == 200
    assert answered.json()["answers"][question_id]["self_score"] == 4
    assert answered.json()["current_index"] == 1

    completed = client.put(
        f"/api/v1/interviews/{session_id}/status",
        json={"status": "completed"},
    )
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"
    assert completed.json()["completed_at"]
    assert all("answer" in item for item in completed.json()["questions"])

    blocked = client.put(
        f"/api/v1/interviews/{session_id}/answers/{question_id}",
        json={"answer": "不能覆盖已结束会话"},
    )
    assert blocked.status_code == 409


def test_interview_filters_and_errors(client: TestClient) -> None:
    missing = client.post(
        "/api/v1/interviews", json={"template_id": "not-found"}
    )
    assert missing.status_code == 404

    beginner = client.post(
        "/api/v1/interviews",
        json={
            "template_id": "quick",
            "level": "基础",
            "count": 3,
            "seed": 11,
        },
    )
    assert beginner.status_code == 201
    assert all(item["level"] == "入门" for item in beginner.json()["questions"])

    ai_only = client.post(
        "/api/v1/interviews",
        json={
            "template_id": "ai-testing",
            "module_ids": ["09"],
            "level": "高级",
            "count": 5,
            "seed": 7,
        },
    )
    assert ai_only.status_code == 201
    assert all(item["module_id"] == "09" for item in ai_only.json()["questions"])
    assert all(item["level"] == "高级" for item in ai_only.json()["questions"])

    performance_role = client.post(
        "/api/v1/interviews",
        json={
            "template_id": "standard",
            "role": "性能测试工程师",
            "count": 8,
            "seed": 29,
        },
    )
    assert performance_role.status_code == 201
    performance_payload = performance_role.json()
    assert performance_payload["role"] == "性能测试工程师"
    assert all(
        {"性能测试", "稳定性测试", "SRE"}.intersection(item["roles"])
        for item in performance_payload["questions"]
    )

    insufficient_role_pool = client.post(
        "/api/v1/interviews",
        json={
            "template_id": "ai-testing",
            "role": "AI 测试工程师",
            "level": "入门",
            "count": 3,
            "seed": 29,
        },
    )
    assert insufficient_role_pool.status_code == 422
    assert "当前筛选条件没有可用题目" in insufficient_role_pool.json()["detail"]
