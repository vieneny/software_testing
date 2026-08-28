from uuid import UUID


def test_health_contains_database_status(client):
    response = client.get(
        "/api/v1/health",
        headers={
            "X-Request-ID": "health-request-001",
            "X-Trace-ID": "lower-priority-trace",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["database"] == "up"
    assert response.json()["ai_configured"] is True
    assert "ai_base_url" not in response.json()
    assert "localhost:8090" not in response.text
    assert response.headers["x-request-id"] == "health-request-001"
    assert response.headers["x-trace-id"] == "health-request-001"


def test_trace_id_is_compatible_and_invalid_request_id_is_not_reflected(client):
    compatible = client.get(
        "/api/v1/health",
        headers={"X-Trace-ID": "legacy-trace-001"},
    )
    assert compatible.headers["x-request-id"] == "legacy-trace-001"
    assert compatible.headers["x-trace-id"] == "legacy-trace-001"

    invalid = client.get(
        "/api/v1/health",
        headers={"X-Request-ID": "contains spaces and must not be reflected"},
    )
    generated = invalid.headers["x-request-id"]
    UUID(generated)
    assert generated == invalid.headers["x-trace-id"]
    assert "contains spaces" not in invalid.headers.values()

    maximal = "A" * 120 + "._:-safe"
    accepted = client.get("/api/v1/health", headers={"X-Request-ID": maximal})
    assert len(maximal) == 128
    assert accepted.headers["x-request-id"] == maximal

    too_long = client.get("/api/v1/health", headers={"X-Request-ID": "A" * 129})
    UUID(too_long.headers["x-request-id"])
    assert too_long.headers["x-request-id"] != "A" * 129


def test_unknown_route_uses_correlated_error_model(client):
    response = client.get(
        "/api/v1/not-a-real-route",
        headers={"X-Request-ID": "missing-route-001"},
    )

    assert response.status_code == 404
    assert response.headers["x-request-id"] == "missing-route-001"
    assert response.json()["error"]["code"] == "route_not_found"
    assert response.json()["error"]["request_id"] == "missing-route-001"
