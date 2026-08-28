from datetime import datetime, timedelta

from app.application.ports.ai_gateway import AISummary
from app.interfaces.api.dependencies import get_ai_gateway
from app.main import app


def assert_utc_timestamp(value: str) -> None:
    assert value.endswith(("Z", "+00:00"))
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    assert parsed.utcoffset() == timedelta(0)


def create_question(client):
    response = client.post(
        "/api/v1/questions",
        json={
            "title": "如何设计一个可以重复执行的幂等接口测试？",
            "content": "我想验证重复提交不会创建多份数据，并学习如何检查数据库状态。",
            "author_name": "学习者001",
            "tags": ["API", "pytest", "api"],
        },
    )
    assert response.status_code == 201
    assert response.headers["x-request-id"]
    return response.json()


def test_question_full_flow(client):
    created = create_question(client)
    question_id = created["id"]
    assert created["tags"] == ["api", "pytest"]

    page = client.get("/api/v1/questions", params={"page": 1, "page_size": 10})
    assert page.status_code == 200
    assert page.json()["total"] == 1
    assert page.json()["items"][0]["answer_count"] == 0

    answer = client.post(
        f"/api/v1/questions/{question_id}/answers",
        json={"content": "可以使用幂等键并对同一请求连续发送三次。", "author_name": "学习者002"},
    )
    assert answer.status_code == 201

    vote = client.post(
        f"/api/v1/questions/{question_id}/votes",
        json={"voter_key": "synthetic-user-001", "value": 1},
    )
    assert vote.status_code == 200
    assert vote.json()["score"] == 1

    detail = client.get(f"/api/v1/questions/{question_id}")
    assert detail.status_code == 200
    assert detail.json()["view_count"] == 1
    assert len(detail.json()["answers"]) == 1


def test_same_vote_is_rejected_but_vote_can_be_changed(client):
    question_id = create_question(client)["id"]
    path = f"/api/v1/questions/{question_id}/votes"
    payload = {"voter_key": "synthetic-user-001", "value": 1}

    assert client.post(path, json=payload).status_code == 200
    duplicate = client.post(path, json=payload)
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "duplicate_vote"

    changed = client.post(path, json={**payload, "value": -1})
    assert changed.status_code == 200
    assert changed.json()["score"] == -1


def test_search_tag_filter_and_pagination_boundaries(client):
    first = create_question(client)
    second = client.post(
        "/api/v1/questions",
        json={
            "title": "如何设计 React 页面自动化测试并达到 100% 通过？",
            "content": "使用完全合成的数据练习页面定位、等待、下划线_和错误态验证。",
            "author_name": "学习者003",
            "tags": ["React", "UI", "100%"],
        },
    )
    assert second.status_code == 201

    keyword = client.get("/api/v1/questions", params={"keyword": "react"})
    assert keyword.status_code == 200
    assert [item["id"] for item in keyword.json()["items"]] == [second.json()["id"]]

    tag = client.get("/api/v1/questions", params={"tag": "PYTEST"})
    assert tag.status_code == 200
    assert [item["id"] for item in tag.json()["items"]] == [first["id"]]

    literal_wildcard = client.get("/api/v1/questions", params={"keyword": "100%"})
    assert [item["id"] for item in literal_wildcard.json()["items"]] == [second.json()["id"]]
    literal_tag = client.get("/api/v1/questions", params={"tag": "100%"})
    assert [item["id"] for item in literal_tag.json()["items"]] == [second.json()["id"]]
    no_wildcard_match = client.get("/api/v1/questions", params={"tag": "%"})
    assert no_wildcard_match.json()["total"] == 0

    combined = client.get(
        "/api/v1/questions",
        params={"keyword": "重复", "tag": "api", "page": 1, "page_size": 1},
    )
    assert combined.status_code == 200
    assert combined.json()["total"] == 1
    assert combined.json()["total_pages"] == 1

    for params in ({"page": 0}, {"page_size": 0}, {"page_size": 101}):
        invalid = client.get("/api/v1/questions", params=params)
        assert invalid.status_code == 422
        assert invalid.json()["error"]["code"] == "request_validation_failed"


def test_question_creation_supports_safe_idempotent_retry(client):
    payload = {
        "title": "如何验证创建接口的幂等重试？",
        "content": "使用同一幂等键重放完全相同的合成请求，并检查只创建一条数据。",
        "author_name": "学习者004",
        "tags": ["API", "幂等性"],
    }
    headers = {"Idempotency-Key": "question-create-retry-001"}

    created = client.post("/api/v1/questions", json=payload, headers=headers)
    replayed = client.post("/api/v1/questions", json=payload, headers=headers)

    assert created.status_code == 201
    assert created.headers["idempotency-replayed"] == "false"
    assert replayed.status_code == 200
    assert replayed.headers["idempotency-replayed"] == "true"
    assert replayed.json()["id"] == created.json()["id"]
    assert client.get("/api/v1/questions").json()["total"] == 1


def test_idempotency_key_cannot_be_reused_for_different_question(client):
    payload = {
        "title": "如何验证幂等键冲突？",
        "content": "第一次提交使用完全合成的原始正文，第二次修改正文。",
        "author_name": "学习者005",
        "tags": ["api"],
    }
    headers = {"Idempotency-Key": "question-create-conflict-001"}
    assert client.post("/api/v1/questions", json=payload, headers=headers).status_code == 201

    conflict = client.post(
        "/api/v1/questions",
        json={**payload, "content": "这是修改后的另一份合成正文，不能复用原来的幂等键。"},
        headers=headers,
    )

    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "idempotency_key_reused"
    assert client.get("/api/v1/questions").json()["total"] == 1


def test_answer_retry_is_idempotent_and_changed_payload_conflicts(client):
    question_id = create_question(client)["id"]
    path = f"/api/v1/questions/{question_id}/answers"
    payload = {
        "content": "这是用于验证回答重试的完全合成内容。",
        "author_name": "学习者006",
    }
    headers = {"Idempotency-Key": "answer-create-retry-001"}

    created = client.post(path, json=payload, headers=headers)
    replayed = client.post(path, json=payload, headers=headers)
    conflict = client.post(
        path,
        json={**payload, "content": "修改内容后不能继续复用同一个回答幂等键。"},
        headers=headers,
    )

    assert created.status_code == 201
    assert replayed.status_code == 200
    assert replayed.headers["idempotency-replayed"] == "true"
    assert replayed.json()["id"] == created.json()["id"]
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "idempotency_key_reused"
    assert len(client.get(f"/api/v1/questions/{question_id}").json()["answers"]) == 1


def test_closed_question_blocks_new_answers_and_can_be_reopened(client):
    question_id = create_question(client)["id"]

    closed = client.patch(
        f"/api/v1/questions/{question_id}/status",
        json={"status": "closed"},
    )
    blocked = client.post(
        f"/api/v1/questions/{question_id}/answers",
        json={"content": "关闭后不应创建这条合成回答。", "author_name": "学习者007"},
    )
    reopened = client.patch(
        f"/api/v1/questions/{question_id}/status",
        json={"status": "open"},
    )
    accepted = client.post(
        f"/api/v1/questions/{question_id}/answers",
        json={"content": "重新开放后允许创建这条合成回答。", "author_name": "学习者007"},
    )

    assert closed.status_code == 200
    assert closed.json()["status"] == "closed"
    assert blocked.status_code == 409
    assert blocked.json()["error"]["code"] == "question_closed"
    assert reopened.status_code == 200
    assert reopened.json()["status"] == "open"
    assert accepted.status_code == 201


def test_accepting_answer_is_single_choice_and_can_be_cancelled(client):
    question_id = create_question(client)["id"]
    answer_ids = []
    for index in range(2):
        response = client.post(
            f"/api/v1/questions/{question_id}/answers",
            json={
                "content": f"完全合成的候选回答 {index}，用于验证单选采纳。",
                "author_name": f"学习者01{index}",
            },
        )
        assert response.status_code == 201
        answer_ids.append(response.json()["id"])

    first = client.put(
        f"/api/v1/questions/{question_id}/answers/{answer_ids[0]}/acceptance",
        json={"accepted": True},
    )
    second = client.put(
        f"/api/v1/questions/{question_id}/answers/{answer_ids[1]}/acceptance",
        json={"accepted": True},
    )
    cancelled = client.put(
        f"/api/v1/questions/{question_id}/answers/{answer_ids[1]}/acceptance",
        json={"accepted": False},
    )

    assert first.status_code == 200
    assert [item["is_accepted"] for item in first.json()["answers"]] == [True, False]
    assert [item["is_accepted"] for item in second.json()["answers"]] == [False, True]
    assert [item["is_accepted"] for item in cancelled.json()["answers"]] == [False, False]


def test_acceptance_rejects_answer_from_another_question(client):
    first_question = create_question(client)["id"]
    second_question = client.post(
        "/api/v1/questions",
        json={
            "title": "第二个用于归属校验的问题是什么？",
            "content": "这是一条完全合成的问题，用于验证回答不能跨问题采纳。",
            "author_name": "学习者012",
            "tags": [],
        },
    ).json()["id"]
    answer = client.post(
        f"/api/v1/questions/{second_question}/answers",
        json={"content": "属于第二个问题的合成回答。", "author_name": "学习者013"},
    ).json()

    response = client.put(
        f"/api/v1/questions/{first_question}/answers/{answer['id']}/acceptance",
        json={"accepted": True},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "resource_not_found"
    assert response.json()["error"]["details"]["resource"] == "回答"


def test_write_inputs_reject_unsafe_or_oversized_identifiers(client):
    base = {
        "title": "如何验证输入边界是否统一？",
        "content": "这里使用完全合成的数据验证标签、昵称和幂等键输入边界。",
        "author_name": "学习者014",
        "tags": [],
    }

    invalid_cases = [
        ({**base, "title": "第一行\n第二行标题"}, {}),
        ({**base, "author_name": "学习者\n伪造日志"}, {}),
        ({**base, "tags": ["T" * 31]}, {}),
        ({**base, "tags": ["a", "b", "c", "d", "e", "f"]}, {}),
        (base, {"Idempotency-Key": "short"}),
    ]
    for payload, headers in invalid_cases:
        response = client.post("/api/v1/questions", json=payload, headers=headers)
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "request_validation_failed"
        assert "伪造日志" not in response.text
        assert '"short"' not in response.text


def test_validation_error_does_not_echo_submitted_content(client):
    sensitive_marker = "synthetic-secret-marker-must-not-be-reflected"
    response = client.post(
        "/api/v1/questions",
        json={
            "title": "短",
            "content": sensitive_marker,
            "author_name": "A",
            "tags": [],
        },
    )

    assert response.status_code == 422
    assert sensitive_marker not in response.text
    details = response.json()["error"]["details"]
    assert all(set(item) == {"type", "loc", "msg"} for item in details)


def test_openapi_documents_idempotency_and_question_lifecycle(client):
    schema = client.get("/openapi.json").json()
    create_operation = schema["paths"]["/api/v1/questions"]["post"]
    header = next(
        item
        for item in create_operation["parameters"]
        if item["name"] == "Idempotency-Key"
    )

    assert header["in"] == "header"
    string_schema = next(
        item for item in header["schema"]["anyOf"] if item.get("type") == "string"
    )
    assert string_schema["minLength"] == 8
    assert string_schema["maxLength"] == 128
    assert {"200", "201", "422"} <= set(create_operation["responses"])
    assert "patch" in schema["paths"]["/api/v1/questions/{question_id}/status"]
    assert (
        "put"
        in schema["paths"][
            "/api/v1/questions/{question_id}/answers/{answer_id}/acceptance"
        ]
    )


def test_persisted_question_and_answer_timestamps_are_utc(client):
    created = create_question(client)
    question_id = created["id"]
    answer = client.post(
        f"/api/v1/questions/{question_id}/answers",
        json={"content": "这是用于验证持久化时间格式的合成回答。", "author_name": "学习者002"},
    )
    assert answer.status_code == 201

    page = client.get("/api/v1/questions").json()
    persisted_summary = page["items"][0]
    detail = client.get(f"/api/v1/questions/{question_id}").json()

    for timestamp in (
        persisted_summary["created_at"],
        persisted_summary["updated_at"],
        detail["created_at"],
        detail["updated_at"],
        detail["answers"][0]["created_at"],
        answer.json()["created_at"],
    ):
        assert_utc_timestamp(timestamp)


def test_missing_question_and_validation_use_unified_error_model(client):
    missing = client.get("/api/v1/questions/not-found")
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "resource_not_found"
    assert missing.json()["error"]["request_id"]
    assert missing.headers["x-trace-id"]
    assert missing.headers["x-request-id"] == missing.json()["error"]["request_id"]
    assert missing.json()["error"]["trace_id"] == missing.json()["error"]["request_id"]

    invalid = client.post(
        "/api/v1/questions",
        json={"title": "短", "content": "短", "author_name": "A", "tags": []},
    )
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "request_validation_failed"


def test_ai_summary_contract_and_request_id_are_forwarded(client):
    question_id = create_question(client)["id"]
    captured = {}

    class FakeAIGateway:
        async def summarize_question(
            self,
            *,
            title: str,
            content: str,
            answers: list[str],
            request_id: str | None = None,
        ) -> AISummary:
            captured.update(
                title=title,
                content=content,
                answers=answers,
                request_id=request_id,
            )
            return AISummary(
                summary="该问题关注幂等接口的重复请求验证。",
                risk_hints=["并发竞争", "唯一约束"],
                model="mock/deterministic-rules@2026.07",
            )

    app.dependency_overrides[get_ai_gateway] = FakeAIGateway
    try:
        response = client.post(
            f"/api/v1/questions/{question_id}/ai-summary",
            headers={"X-Request-ID": "forum-ai-test-001"},
        )
    finally:
        app.dependency_overrides.pop(get_ai_gateway, None)

    assert response.status_code == 200
    assert response.json()["risk_hints"] == ["并发竞争", "唯一约束"]
    assert captured["request_id"] == "forum-ai-test-001"
    assert captured["answers"] == []
