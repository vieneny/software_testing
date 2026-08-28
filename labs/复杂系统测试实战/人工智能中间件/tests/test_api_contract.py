from fastapi.testclient import TestClient


def test_health_and_request_id_contract(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Request-ID": "forum-req-001"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "forum-req-001"
    assert response.json() == {
        "api_version": "v1",
        "service_version": "0.1.0",
        "request_id": "forum-req-001",
        "status": "ok",
    }


def test_invalid_request_id_is_replaced(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Request-ID": "invalid id with spaces"})

    request_id = response.json()["request_id"]
    assert request_id != "invalid id with spaces"
    assert response.headers["X-Request-ID"] == request_id
    assert len(request_id) == 32


def test_moderation_is_deterministic(client: TestClient) -> None:
    payload = {"text": "请勿在帖子中发送身份证或银行卡信息", "context": "forum"}

    first = client.post("/api/v1/moderation", json=payload)
    second = client.post("/api/v1/moderation", json=payload)

    assert first.status_code == 200
    assert first.json()["result"] == second.json()["result"]
    assert first.json()["result"]["decision"] == "review"
    assert first.json()["result"]["categories"] == ["privacy"]
    assert first.json()["provider"]["name"] == "mock"


def test_content_summary_and_tags(client: TestClient) -> None:
    response = client.post(
        "/api/v1/content/analyze",
        json={
            "text": "本文使用 FastAPI 演示接口测试。随后介绍性能测试与安全测试。",
            "max_summary_chars": 80,
            "max_tags": 3,
        },
    )

    assert response.status_code == 200
    result = response.json()["result"]
    assert result["summary"]
    assert "接口测试" in result["tags"]
    assert len(result["tags"]) <= 3


def test_ticket_classification_and_priority(client: TestClient) -> None:
    response = client.post(
        "/api/v1/tickets/classify",
        json={
            "subject": "重复扣款",
            "content": "合成用户说订单重复扣款，当前无法使用支付功能。",
            "channel": "android",
        },
    )

    assert response.status_code == 200
    result = response.json()["result"]
    assert result["category"] == "billing"
    assert result["priority"] == "P1"


def test_grounded_answer_has_citation(client: TestClient) -> None:
    response = client.post(
        "/api/v1/knowledge/answer",
        json={
            "question": "测试环境订单如何申请退款？",
            "documents": [
                {
                    "source_id": "public-demo-refund-v1",
                    "title": "公开演示商城退款说明",
                    "content": "测试订单可在订单详情页点击申请退款，状态会变为审核中。",
                },
                {
                    "source_id": "public-demo-login-v1",
                    "title": "公开演示商城登录说明",
                    "content": "演示账号只能使用固定验证码登录。",
                },
            ],
        },
    )

    assert response.status_code == 200
    result = response.json()["result"]
    assert result["grounded"] is True
    assert result["citations"] == [
        {"source_id": "public-demo-refund-v1", "title": "公开演示商城退款说明"}
    ]
    assert result["must_verify"]


def test_ungrounded_answer_refuses_to_guess(client: TestClient) -> None:
    response = client.post(
        "/api/v1/knowledge/answer",
        json={
            "question": "火星天气是什么？",
            "documents": [
                {
                    "source_id": "synthetic-login",
                    "title": "演示登录",
                    "content": "测试账号使用固定验证码。",
                }
            ],
        },
    )

    assert response.status_code == 200
    assert response.json()["result"]["grounded"] is False
    assert response.json()["result"]["citations"] == []


def test_reply_suggestion_requires_human_review(client: TestClient) -> None:
    response = client.post(
        "/api/v1/agents/reply-suggestions",
        json={
            "ticket_id": "SYNTHETIC-001",
            "customer_message": "演示订单显示重复扣款。",
            "category": "billing",
            "priority": "P1",
        },
    )

    assert response.status_code == 200
    result = response.json()["result"]
    assert result["requires_human_review"] is True
    assert result["must_verify"]
    assert "退款" not in result["suggestion"]


def test_forum_fastapi_compatibility_contract(client: TestClient) -> None:
    response = client.post(
        "/api/v1/forum/summarize",
        headers={"X-Request-ID": "forum-contract-001"},
        json={
            "title": "如何学习接口测试",
            "content": "我使用公开演示接口练习 HTTP 状态码和断言。",
            "answers": ["可以先写正常、异常和边界场景。"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert {
        "api_version",
        "request_id",
        "summary",
        "risk_hints",
        "model",
        "provider",
        "processing",
    } == set(body)
    assert body["request_id"] == "forum-contract-001"
    assert body["summary"]
    assert body["risk_hints"] == []
    assert body["model"].startswith("mock/")
    assert body["provider"]["analysis_calls"] == 1
    assert body["provider"]["moderation_calls"] == 1
    assert body["provider"]["total_attempts"] == 2
    assert body["processing"]["chunk_count"] == 1
    assert body["processing"]["chunk_overlap"] == 128
    assert body["processing"]["input_truncated"] is False


def test_forum_tail_risk_is_detected_and_multichunk_result_is_stable(
    client: TestClient,
) -> None:
    payload = {
        "title": "尾部风险测试",
        "content": "安" * 10_000,
        # 该风险词在组合文本的第 10000 个字符之后。
        "answers": ["纯合成炸弹风险词"],
    }

    first = client.post("/api/v1/forum/summarize", json=payload)
    second = client.post("/api/v1/forum/summarize", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    first_body = first.json()
    second_body = second.json()
    assert first_body["processing"]["source_chars"] > 10_000
    assert first_body["processing"]["chunk_count"] == 2
    assert first_body["processing"]["input_truncated"] is False
    assert first_body["provider"]["analysis_calls"] == 2
    assert first_body["provider"]["moderation_calls"] == 2
    assert first_body["provider"]["total_attempts"] == 4
    assert "chunk=2;decision=block" in first_body["risk_hints"]
    assert "chunk=2;category=violence" in first_body["risk_hints"]
    assert {
        "summary": first_body["summary"],
        "risk_hints": first_body["risk_hints"],
        "model": first_body["model"],
        "provider": first_body["provider"],
        "processing": first_body["processing"],
    } == {
        "summary": second_body["summary"],
        "risk_hints": second_body["risk_hints"],
        "model": second_body["model"],
        "provider": second_body["provider"],
        "processing": second_body["processing"],
    }


def test_forum_overlap_detects_risk_term_split_at_chunk_boundary(
    client: TestClient,
) -> None:
    title = "边界风险"
    prefix = f"标题：{title}\n正文："
    filler = "安" * (9999 - len(prefix))
    content = f"{filler}炸弹"
    combined = f"{prefix}{content}"
    assert combined.index("炸弹") == 9999

    response = client.post(
        "/api/v1/forum/summarize",
        json={"title": title, "content": content, "answers": []},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["processing"]["chunk_count"] == 2
    assert body["processing"]["chunk_overlap"] == 128
    assert "chunk=2;decision=block" in body["risk_hints"]
    assert "chunk=2;category=violence" in body["risk_hints"]


def test_customer_service_spring_contract(client: TestClient) -> None:
    response = client.post(
        "/api/v1/customer-service/suggest",
        headers={"X-Request-ID": "java-customer-002"},
        json={
            "tenant_code": "demo",
            "ticket_id": "SYNTHETIC-002",
            "title": "演示账号无法登录",
            "description": "纯合成描述：公开演示账号收不到验证码，无法使用。",
            "category": "ACCOUNT",
            "priority": "HIGH",
            "customer_level": "VIP",
            "tone": "professional",
            "language": "zh-CN",
            "knowledge_context": [
                {
                    "title": "公开演示账号登录故障排查",
                    "category": "ACCOUNT",
                    "content": "演示账号收不到验证码时，先核对测试环境认证服务状态。",
                }
            ],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["summary"]
    assert body["suggested_reply"]
    assert body["suggested_category"] == "ACCOUNT"
    assert body["suggested_priority"] == "HIGH"
    assert 0 <= body["confidence"] <= 1
    assert body["risk_flags"] == ["HIGH_PRIORITY"]
    assert body["knowledge_references"] == ["公开演示账号登录故障排查"]
    assert body["degraded"] is False
    assert body["degradation_reason"] is None
    assert body["suggested_actions"]
    assert body["must_verify"]
    assert body["model"].startswith("mock/")
    assert body["request_id"] == "java-customer-002"


def test_customer_service_early_contract_remains_compatible(client: TestClient) -> None:
    response = client.post(
        "/api/v1/customer-service/suggest",
        json={
            "ticket_id": "SYNTHETIC-LEGACY-001",
            "subject": "登录失败",
            "customer_message": "公开演示账号收不到验证码，无法使用。",
            "channel": "web",
            "context": ["演示环境版本 1.0"],
        },
    )

    assert response.status_code == 200
    assert response.json()["suggested_category"] == "ACCOUNT"
    assert response.json()["suggested_reply"]


def test_customer_service_maps_p0_to_java_urgent(client: TestClient) -> None:
    response = client.post(
        "/api/v1/customer-service/suggest",
        json={
            "tenant_code": "demo",
            "ticket_id": "SYNTHETIC-URGENT-001",
            "title": "公开演示环境安全漏洞",
            "description": "纯合成场景：测试账号出现越权风险。",
            "category": "SECURITY",
            # 历史别名仍可作为输入，但输出必须遵循 Java 领域枚举。
            "priority": "CRITICAL",
            "customer_level": "NORMAL",
            "tone": "professional",
            "language": "zh-CN",
            "knowledge_context": [],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["suggested_category"] == "SECURITY"
    assert body["suggested_priority"] == "URGENT"
    assert "HIGH_PRIORITY" in body["risk_flags"]


def test_validation_errors_use_unified_error_model(client: TestClient) -> None:
    response = client.post(
        "/api/v1/tickets/classify",
        headers={"X-Request-ID": "bad-contract-001"},
        json={"subject": "", "content": "x", "unknown": "not-allowed"},
    )

    assert response.status_code == 422
    assert response.headers["X-Request-ID"] == "bad-contract-001"
    body = response.json()
    assert body["api_version"] == "v1"
    assert body["request_id"] == "bad-contract-001"
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["retryable"] is False
    assert body["error"]["details"]["fields"]


def test_404_uses_unified_error_model(client: TestClient) -> None:
    response = client.get("/does-not-exist")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "http_error"
    assert response.headers["X-Request-ID"] == response.json()["request_id"]


def test_openapi_contains_all_required_routes(client: TestClient) -> None:
    paths = client.get("/openapi.json").json()["paths"]

    assert {
        "/health",
        "/ready",
        "/api/v1/moderation",
        "/api/v1/content/analyze",
        "/api/v1/tickets/classify",
        "/api/v1/knowledge/answer",
        "/api/v1/agents/reply-suggestions",
        "/api/v1/forum/summarize",
        "/api/v1/customer-service/suggest",
    } <= set(paths)
