from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


BACKEND_DIR = Path(__file__).resolve().parents[1]
BANK_DIR = BACKEND_DIR.parent


def _client(tmp_path: Path, manifest_path: Path) -> TestClient:
    settings = Settings(
        catalog_path=BANK_DIR / "data" / "questions.json",
        legacy_coverage_path=BANK_DIR / "data" / "legacy-coverage.json",
        database_path=tmp_path / "runtime" / "test.db",
        frontend_dist=tmp_path / "missing-dist",
        cors_origins=("http://localhost:5173",),
        source_snapshots_manifest_path=manifest_path,
    )
    return TestClient(create_app(settings))


def _write_manifest(path: Path, items: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "generated_at": "2026-07-29",
                "items": items,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_missing_manifest_and_snapshot_return_explicit_local_status(
    client: TestClient,
) -> None:
    listing = client.get("/api/v1/source-snapshots")
    assert listing.status_code == 200
    assert listing.json()["status"] == "not_configured"
    assert listing.json()["total"] == 0

    missing = client.get(
        "/api/v1/sources/xiaolincoding-testdev-2026/snapshot",
        follow_redirects=False,
    )
    assert missing.status_code == 404
    assert missing.headers.get("location") is None
    assert missing.json()["detail"] == {
        "code": "snapshot_not_found",
        "message": "该来源尚未下载到本地",
        "source_id": "xiaolincoding-testdev-2026",
        "manifest_status": "not_configured",
    }


def test_snapshot_is_read_locally_by_source_id_and_alias(tmp_path: Path) -> None:
    manifest_path = tmp_path / "source-snapshots" / "manifest.json"
    page_path = manifest_path.parent / "pages" / "testdev.md"
    page_path.parent.mkdir(parents=True)
    content = "# 测试开发\n\n这是下载到本地的公开学习快照。"
    page_path.write_text(content, encoding="utf-8")
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    _write_manifest(
        manifest_path,
        [
            {
                "source_id": "xiaolincoding-testdev-2026",
                "aliases": ["xiaolincoding-testdev-navigation"],
                "title": "小林 Coding 测试开发导航",
                "platform": "小林 Coding",
                "original_url": "https://xiaolincoding.com/interview/test_dev.html",
                "captured_at": "2026-07-29",
                "status": "downloaded",
                "content_format": "markdown",
                "local_path": "pages/testdev.md",
                "content_hash": f"sha256:{digest}",
                "copyright_notice": "仅供个人学习核验。",
            }
        ],
    )

    with _client(tmp_path, manifest_path) as client:
        listing = client.get("/api/v1/source-snapshots").json()
        assert listing["status"] == "ready"
        assert listing["total"] == 1
        assert listing["available"] == 1
        assert "content" not in listing["items"][0]

        direct = client.get(
            "/api/v1/sources/xiaolincoding-testdev-2026/snapshot",
            follow_redirects=False,
        )
        alias = client.get(
            "/api/v1/sources/xiaolincoding-testdev-navigation/snapshot",
            follow_redirects=False,
        )

    assert direct.status_code == 200
    assert alias.status_code == 200
    assert direct.headers.get("location") is None
    direct_payload = direct.json()
    alias_payload = alias.json()
    assert direct_payload.pop("asset_base_url") == (
        "/api/v1/sources/xiaolincoding-testdev-2026/assets"
    )
    assert alias_payload.pop("asset_base_url") == (
        "/api/v1/sources/xiaolincoding-testdev-navigation/assets"
    )
    assert direct_payload == alias_payload
    payload = direct.json()
    assert payload["source_id"] == "xiaolincoding-testdev-2026"
    assert payload["title"] == "小林 Coding 测试开发导航"
    assert payload["platform"] == "小林 Coding"
    assert payload["original_url"].startswith("https://")
    assert payload["captured_at"] == "2026-07-29"
    assert payload["status"] == "available"
    assert payload["content_format"] == "markdown"
    assert payload["content"] == content
    assert payload["content_hash"] == f"sha256:{digest}"
    assert payload["local_path"] == "pages/testdev.md"
    assert payload["char_count"] == len(content)
    assert payload["copyright_notice"] == "仅供个人学习核验。"


def test_catalog_source_can_match_snapshot_by_original_url(tmp_path: Path) -> None:
    manifest_path = tmp_path / "source-snapshots" / "manifest.json"
    page_path = manifest_path.parent / "pages" / "nowcoder.txt"
    page_path.parent.mkdir(parents=True)
    page_path.write_text("本地牛客公开页面摘要", encoding="utf-8")
    _write_manifest(
        manifest_path,
        [
            {
                "source_id": "downloaded-nowcoder-page",
                "original_url": "https://www.nowcoder.com/experience/680/",
                "local_path": "pages/nowcoder.txt",
            }
        ],
    )

    with _client(tmp_path, manifest_path) as client:
        response = client.get(
            "/api/v1/sources/nowcoder-2026-07/snapshot",
            follow_redirects=False,
        )

    assert response.status_code == 200
    assert response.headers.get("location") is None
    assert response.json()["source_id"] == "downloaded-nowcoder-page"
    assert response.json()["content"] == "本地牛客公开页面摘要"


def test_snapshot_reader_rejects_path_traversal_and_hash_mismatch(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "source-snapshots" / "manifest.json"
    outside = tmp_path / "outside.md"
    outside.write_text("不能通过快照 API 读取", encoding="utf-8")
    inside = manifest_path.parent / "inside.md"
    inside.parent.mkdir(parents=True, exist_ok=True)
    inside.write_text("本地正文", encoding="utf-8")
    _write_manifest(
        manifest_path,
        [
            {
                "source_id": "unsafe-traversal",
                "local_path": "../outside.md",
            },
            {
                "source_id": "hash-mismatch",
                "local_path": "inside.md",
                "content_hash": "sha256:" + ("0" * 64),
            },
        ],
    )

    with _client(tmp_path, manifest_path) as client:
        traversal = client.get("/api/v1/sources/unsafe-traversal/snapshot")
        mismatch = client.get("/api/v1/sources/hash-mismatch/snapshot")

    assert traversal.status_code == 409
    assert traversal.json()["detail"]["code"] == "snapshot_integrity_error"
    assert "越出允许目录" in traversal.json()["detail"]["message"]
    assert "不能通过快照 API 读取" not in traversal.text
    assert mismatch.status_code == 409
    assert mismatch.json()["detail"]["code"] == "snapshot_integrity_error"
    assert "哈希校验失败" in mismatch.json()["detail"]["message"]


def test_manifest_failure_status_and_invalid_manifest_are_clear(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "source-snapshots" / "manifest.json"
    _write_manifest(
        manifest_path,
        [
            {
                "source_id": "blocked-page",
                "status": "failed",
                "error": "站点拒绝公开抓取，未保存正文",
            }
        ],
    )
    with _client(tmp_path, manifest_path) as client:
        unavailable = client.get("/api/v1/sources/blocked-page/snapshot")
    assert unavailable.status_code == 409
    assert unavailable.json()["detail"]["status"] == "failed"
    assert "未保存正文" in unavailable.json()["detail"]["message"]

    manifest_path.write_text("{not-json", encoding="utf-8")
    with _client(tmp_path, manifest_path) as client:
        listing = client.get("/api/v1/source-snapshots")
        detail = client.get("/api/v1/sources/blocked-page/snapshot")
    assert listing.status_code == 200
    assert listing.json()["status"] == "invalid"
    assert detail.status_code == 503
    assert detail.json()["detail"]["code"] == "snapshot_manifest_invalid"


@pytest.mark.parametrize(
    ("crawler_status", "error"),
    [
        ("no_url", "该资料没有公开 URL"),
        ("not_requested", None),
        ("robots_unavailable", "无法安全读取 robots.txt"),
        ("robots_denied", "robots.txt 禁止抓取"),
        ("access_denied", "页面要求登录"),
        ("rate_limited", "页面返回 HTTP 429"),
        ("http_error", "页面返回 HTTP 500"),
        ("access_limited", "页面要求验证码"),
        ("unsupported_content_type", "响应不是支持的文本格式"),
        ("empty_content", "页面没有可离线阅读的正文"),
        ("processing_error", "正文处理失败"),
    ],
)
def test_crawler_failure_status_is_preserved_for_api_and_manifest_listing(
    tmp_path: Path,
    crawler_status: str,
    error: str | None,
) -> None:
    manifest_path = tmp_path / "source-snapshots" / "manifest.json"
    item: dict[str, object] = {
        "source_id": "crawler-failure",
        "status": crawler_status,
        "local_path": None,
    }
    if error is not None:
        item["error"] = error
    _write_manifest(manifest_path, [item])

    with _client(tmp_path, manifest_path) as client:
        listing = client.get("/api/v1/source-snapshots")
        detail = client.get("/api/v1/sources/crawler-failure/snapshot")

    assert listing.status_code == 200
    assert listing.json()["items"][0]["status"] == crawler_status
    assert listing.json()["items"][0]["error"] == error
    assert detail.status_code == 409
    assert detail.json()["detail"]["code"] == "snapshot_unavailable"
    assert detail.json()["detail"]["status"] == crawler_status
    expected_message = error or f"本地来源快照状态为 {crawler_status}"
    assert detail.json()["detail"]["message"] == expected_message


def test_registered_local_asset_is_returned_without_redirect(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "source-snapshots" / "manifest.json"
    page_path = manifest_path.parent / "content" / "source.md"
    asset_path = manifest_path.parent / "assets" / "diagram.png"
    page_path.parent.mkdir(parents=True)
    asset_path.parent.mkdir(parents=True)
    page_content = """# 本地图片来源

![流程图](../assets/diagram.png)

[普通资料链接](../assets/diagram.png)

![未登记](../assets/not-registered.png)

```markdown
![代码示例](../assets/diagram.png)
```
"""
    asset_content = b"\x89PNG\r\n\x1a\nsynthetic-public-diagram"
    page_path.write_text(page_content, encoding="utf-8")
    asset_path.write_bytes(asset_content)
    _write_manifest(
        manifest_path,
        [
            {
                "source_id": "source-with-image",
                "aliases": ["coverage-with-image"],
                "status": "downloaded",
                "capture_method": "public_crawler",
                "local_path": "content/source.md",
                "content_hash": (
                    "sha256:"
                    + hashlib.sha256(page_content.encode("utf-8")).hexdigest()
                ),
                "assets": [
                    {
                        "asset_id": "diagram-01",
                        "local_path": "assets/diagram.png",
                        "mime_type": "image/png",
                        "status": "downloaded",
                        "content_hash": (
                            "sha256:" + hashlib.sha256(asset_content).hexdigest()
                        ),
                        "byte_count": len(asset_content),
                        "alt_text": "P95 流程图",
                        "caption": "性能证据链",
                        "width": 640,
                        "height": 480,
                        "original_url": "https://example.com/diagram.png",
                        "capture_method": "public_crawler",
                    }
                ],
            }
        ],
    )

    with _client(tmp_path, manifest_path) as client:
        snapshot = client.get(
            "/api/v1/sources/coverage-with-image/snapshot",
            follow_redirects=False,
        )
        asset = client.get(
            "/api/v1/sources/coverage-with-image/assets/diagram-01",
            follow_redirects=False,
        )
        missing = client.get(
            "/api/v1/sources/coverage-with-image/assets/not-registered",
            follow_redirects=False,
        )

    assert snapshot.status_code == 200
    assert snapshot.json()["asset_base_url"] == (
        "/api/v1/sources/coverage-with-image/assets"
    )
    assert snapshot.json()["capture_method"] == "public_crawler"
    assert "![流程图](snapshot-asset:diagram-01)" in snapshot.json()["content"]
    assert "[普通资料链接](../assets/diagram.png)" in snapshot.json()["content"]
    assert "![未登记](../assets/not-registered.png)" in snapshot.json()["content"]
    assert "![代码示例](../assets/diagram.png)" in snapshot.json()["content"]
    assert snapshot.json()["content_hash"] == (
        "sha256:" + hashlib.sha256(page_content.encode("utf-8")).hexdigest()
    )
    assert page_path.read_text(encoding="utf-8") == page_content
    assert snapshot.json()["assets"] == [
        {
            "asset_id": "diagram-01",
            "local_path": "assets/diagram.png",
            "content_type": "image/png",
            "content_hash": "sha256:" + hashlib.sha256(asset_content).hexdigest(),
            "byte_count": len(asset_content),
            "alt": "P95 流程图",
            "caption": "性能证据链",
            "width": 640,
            "height": 480,
            "original_url": "https://example.com/diagram.png",
            "status": "available",
            "capture_method": "public_crawler",
            "error": None,
        }
    ]
    assert asset.status_code == 200
    assert asset.content == asset_content
    assert asset.headers["content-type"] == "image/png"
    assert asset.headers["x-content-type-options"] == "nosniff"
    assert "default-src 'none'" in asset.headers["content-security-policy"]
    assert asset.headers.get("location") is None
    assert missing.status_code == 404
    assert missing.headers.get("location") is None
    assert missing.json()["detail"]["code"] == "snapshot_asset_not_found"


def test_asset_reader_rejects_traversal_and_symlink_escape(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "source-snapshots" / "manifest.json"
    outside = tmp_path / "outside.png"
    outside_content = b"\x89PNG\r\n\x1a\nmust-not-be-read"
    outside.write_bytes(outside_content)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    symlink_path = manifest_path.parent / "escaped.png"
    try:
        symlink_path.symlink_to(outside)
    except OSError:
        pytest.skip("当前文件系统不支持创建符号链接")
    common = {
        "content_type": "image/png",
        "content_hash": "sha256:" + hashlib.sha256(outside_content).hexdigest(),
        "byte_count": len(outside_content),
    }
    _write_manifest(
        manifest_path,
        [
            {
                "source_id": "unsafe-assets",
                "status": "downloaded",
                "assets": [
                    {
                        "asset_id": "parent-traversal",
                        "local_path": "../outside.png",
                        **common,
                    },
                    {
                        "asset_id": "symlink-escape",
                        "local_path": "escaped.png",
                        **common,
                    },
                ],
            }
        ],
    )

    with _client(tmp_path, manifest_path) as client:
        traversal = client.get(
            "/api/v1/sources/unsafe-assets/assets/parent-traversal"
        )
        symlink = client.get(
            "/api/v1/sources/unsafe-assets/assets/symlink-escape"
        )

    for response in (traversal, symlink):
        assert response.status_code == 409
        assert response.json()["detail"]["code"] == (
            "snapshot_asset_integrity_error"
        )
        assert "越出允许目录" in response.json()["detail"]["message"]
        assert outside_content not in response.content


def test_asset_reader_rejects_hash_size_and_mime_mismatch(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "source-snapshots" / "manifest.json"
    asset_root = manifest_path.parent / "assets"
    asset_root.mkdir(parents=True)
    png_content = b"\x89PNG\r\n\x1a\nasset"
    (asset_root / "hash.png").write_bytes(png_content)
    (asset_root / "size.png").write_bytes(png_content)
    (asset_root / "active.svg").write_text(
        "<svg><script>alert(1)</script></svg>", encoding="utf-8"
    )
    _write_manifest(
        manifest_path,
        [
            {
                "source_id": "invalid-assets",
                "status": "downloaded",
                "assets": [
                    {
                        "asset_id": "bad-hash",
                        "local_path": "assets/hash.png",
                        "content_type": "image/png",
                        "content_hash": "sha256:" + ("0" * 64),
                        "byte_count": len(png_content),
                    },
                    {
                        "asset_id": "bad-size",
                        "local_path": "assets/size.png",
                        "content_type": "image/png",
                        "content_hash": (
                            "sha256:" + hashlib.sha256(png_content).hexdigest()
                        ),
                        "byte_count": len(png_content) + 1,
                    },
                    {
                        "asset_id": "active-svg",
                        "local_path": "assets/active.svg",
                        "content_type": "image/svg+xml",
                        "content_hash": "sha256:unused",
                        "byte_count": 36,
                    },
                ],
            }
        ],
    )

    with _client(tmp_path, manifest_path) as client:
        bad_hash = client.get(
            "/api/v1/sources/invalid-assets/assets/bad-hash"
        )
        bad_size = client.get(
            "/api/v1/sources/invalid-assets/assets/bad-size"
        )
        bad_mime = client.get(
            "/api/v1/sources/invalid-assets/assets/active-svg"
        )

    assert bad_hash.status_code == 409
    assert "哈希校验失败" in bad_hash.json()["detail"]["message"]
    assert bad_size.status_code == 409
    assert "byte_count 校验失败" in bad_size.json()["detail"]["message"]
    assert bad_mime.status_code == 409
    assert "MIME 类型不受支持" in bad_mime.json()["detail"]["message"]


def test_failed_crawler_asset_keeps_status_and_is_not_served(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "source-snapshots" / "manifest.json"
    page_path = manifest_path.parent / "content" / "failed-image.md"
    page_path.parent.mkdir(parents=True)
    page_content = "# 图片抓取失败但正文可读"
    page_path.write_text(page_content, encoding="utf-8")
    _write_manifest(
        manifest_path,
        [
            {
                "source_id": "failed-image-source",
                "status": "downloaded",
                "local_path": "content/failed-image.md",
                "content_hash": (
                    "sha256:"
                    + hashlib.sha256(page_content.encode("utf-8")).hexdigest()
                ),
                "assets": [
                    {
                        "asset_id": "blocked-image",
                        "original_url": "https://cdn.example/private.png",
                        "local_path": None,
                        "mime_type": None,
                        "status": "robots_denied",
                        "content_hash": None,
                        "byte_count": 0,
                        "alt_text": "受限图片",
                        "capture_method": "public_crawler",
                        "error": "robots.txt 禁止抓取图片",
                    }
                ],
            }
        ],
    )

    with _client(tmp_path, manifest_path) as client:
        snapshot = client.get("/api/v1/sources/failed-image-source/snapshot")
        asset = client.get(
            "/api/v1/sources/failed-image-source/assets/blocked-image"
        )

    assert snapshot.status_code == 200
    assert snapshot.json()["assets"][0]["status"] == "robots_denied"
    assert snapshot.json()["assets"][0]["alt"] == "受限图片"
    assert asset.status_code == 404
    assert asset.json()["detail"]["code"] == "snapshot_asset_unavailable"
    assert asset.json()["detail"]["status"] == "robots_denied"
    assert "robots.txt 禁止抓取图片" in asset.json()["detail"]["message"]


def test_manifest_mtime_reload_exposes_assets_without_app_restart(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "source-snapshots" / "manifest.json"
    page_path = manifest_path.parent / "content" / "reload.md"
    page_path.parent.mkdir(parents=True)
    page_content = "# 导入前"
    page_path.write_text(page_content, encoding="utf-8")
    base_item: dict[str, object] = {
        "source_id": "browser-import",
        "status": "downloaded",
        "local_path": "content/reload.md",
        "content_hash": (
            "sha256:" + hashlib.sha256(page_content.encode("utf-8")).hexdigest()
        ),
        "assets": [],
    }
    _write_manifest(manifest_path, [base_item])

    with _client(tmp_path, manifest_path) as client:
        before = client.get("/api/v1/sources/browser-import/snapshot")
        assert before.status_code == 200
        assert before.json()["assets"] == []

        previous_mtime = manifest_path.stat().st_mtime_ns
        asset_content = b"\x89PNG\r\n\x1a\nbrowser-import"
        asset_path = manifest_path.parent / "assets" / "imported.png"
        asset_path.parent.mkdir(parents=True)
        asset_path.write_bytes(asset_content)
        updated_item = {
            **base_item,
            "assets": [
                {
                    "asset_id": "imported",
                    "local_path": "assets/imported.png",
                    "content_type": "image/png",
                    "content_hash": (
                        "sha256:" + hashlib.sha256(asset_content).hexdigest()
                    ),
                    "byte_count": len(asset_content),
                }
            ],
        }
        _write_manifest(manifest_path, [updated_item])
        os.utime(
            manifest_path,
            ns=(
                manifest_path.stat().st_atime_ns,
                max(manifest_path.stat().st_mtime_ns, previous_mtime + 1),
            ),
        )

        after = client.get("/api/v1/sources/browser-import/snapshot")
        asset = client.get(
            "/api/v1/sources/browser-import/assets/imported",
            follow_redirects=False,
        )

    assert after.status_code == 200
    assert [item["asset_id"] for item in after.json()["assets"]] == ["imported"]
    assert asset.status_code == 200
    assert asset.content == asset_content
