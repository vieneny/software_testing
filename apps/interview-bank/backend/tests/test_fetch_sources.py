from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import pytest


SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import fetch_sources as snapshots  # noqa: E402


PUBLIC_ADDRESS = "93.184.216.34"


def public_resolver(
    host: str, port: int, *, type: int
) -> list[tuple[Any, ...]]:
    return [(2, type, 6, "", (PUBLIC_ADDRESS, port))]


class FakeClock:
    def __init__(self) -> None:
        self.current = 0.0
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.current

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.current += seconds


class FakeCrawler(snapshots.SourceSnapshotCrawler):
    def __init__(
        self,
        output_dir: Path,
        routes: dict[str, snapshots.FetchResponse | list[snapshots.FetchResponse]],
        clock: FakeClock,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            output_dir=output_dir,
            resolver=public_resolver,
            sleep=clock.sleep,
            monotonic=clock.monotonic,
            **kwargs,
        )
        self.routes = routes
        self.calls: list[str] = []

    def _request_once(
        self, url: str, *, max_bytes: int
    ) -> snapshots.FetchResponse:
        self.calls.append(url)
        configured = self.routes[url]
        if isinstance(configured, list):
            response = configured.pop(0)
        else:
            response = configured
        if len(response.body) > max_bytes:
            raise snapshots.SnapshotError(
                "too_large", f"响应超过 {max_bytes} 字节大小限制"
            )
        return response


def response(
    url: str,
    *,
    status: int = 200,
    content_type: str = "text/html; charset=utf-8",
    body: str = "",
    headers: dict[str, str] | None = None,
) -> snapshots.FetchResponse:
    result_headers = {"Content-Type": content_type}
    result_headers.update(headers or {})
    return snapshots.FetchResponse(
        url=url,
        status=status,
        headers=result_headers,
        body=body.encode("utf-8"),
    )


def binary_response(
    url: str,
    *,
    body: bytes,
    content_type: str,
    status: int = 200,
    headers: dict[str, str] | None = None,
) -> snapshots.FetchResponse:
    result_headers = {"Content-Type": content_type}
    result_headers.update(headers or {})
    return snapshots.FetchResponse(
        url=url,
        status=status,
        headers=result_headers,
        body=body,
    )


def test_html_is_converted_to_safe_offline_markdown() -> None:
    title, content = snapshots.convert_to_markdown(
        b"""
        <html><head><title>Testing &amp; Safety</title>
        <script>steal(document.cookie)</script></head>
        <body><h1>API Test</h1><p>Read <a href="https://outside.example/x">docs</a>.</p>
        <div hidden>secret</div><span aria-hidden>empty accessibility attribute</span>
        <img src="https://outside.example/a.png" alt="chart">
        <pre>if ok:\n    run()</pre></body></html>
        """,
        "text/html",
        "utf-8",
        "Fallback",
    )

    assert title == "Testing & Safety"
    assert "# API Test" in content
    assert "docs" in content
    assert "https://outside.example" not in content
    assert "document.cookie" not in content
    assert "secret" not in content
    assert "[图片：chart]" in content
    assert "    run()" in content


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1/private",
        "http://[::1]/private",
        "http://169.254.169.254/latest/meta-data",
        "https://service.local/data",
        "file:///etc/passwd",
        "https://user:secret@example.com/",
    ],
)
def test_private_or_credentialed_urls_are_blocked(url: str) -> None:
    with pytest.raises(snapshots.SnapshotError) as exc_info:
        snapshots.validate_public_url(url, resolver=public_resolver)

    assert exc_info.value.status == "blocked_url"


def test_same_origin_robots_rules_are_evaluated_for_each_path(
    tmp_path: Path,
) -> None:
    clock = FakeClock()
    robots_url = "https://docs.example/robots.txt"
    public_url = "https://docs.example/public"
    private_url = "https://docs.example/private"
    crawler = FakeCrawler(
        tmp_path,
        {
            robots_url: response(
                robots_url,
                content_type="text/plain",
                body="User-agent: *\nDisallow: /private\nCrawl-delay: 2\n",
            ),
            public_url: response(
                public_url,
                body=(
                    "<html><title>Public guide</title><body><main>"
                    + "<p>Testing evidence and workflow.</p>" * 30
                    + "</main></body></html>"
                ),
            ),
        },
        clock,
        delay_seconds=0.25,
        retries=0,
    )

    downloaded = crawler.snapshot_item(
        {
            "id": "public-guide",
            "title": "Guide",
            "platform": "Docs",
            "url": public_url,
            "accessed_at": "2026-07-29",
        }
    )
    denied = crawler.snapshot_item(
        {
            "id": "private-guide",
            "title": "Private",
            "platform": "Docs",
            "url": private_url,
            "accessed_at": "2026-07-29",
        }
    )

    assert downloaded["status"] == "downloaded"
    assert denied["status"] == "robots_denied"
    assert crawler.calls.count(robots_url) == 1
    assert private_url not in crawler.calls
    assert any(delay >= 2 for delay in clock.sleeps)


def test_redirected_robots_file_is_followed_before_deciding(
    tmp_path: Path,
) -> None:
    clock = FakeClock()
    robots_url = "https://docs.example/robots.txt"
    policy_url = "https://docs.example/policy/robots.txt"
    page_url = "https://docs.example/blocked"
    crawler = FakeCrawler(
        tmp_path,
        {
            robots_url: response(
                robots_url,
                status=301,
                headers={"Location": "/policy/robots.txt"},
            ),
            policy_url: response(
                policy_url,
                content_type="text/plain",
                body="User-agent: *\nDisallow: /blocked\n",
            ),
        },
        clock,
        retries=0,
        delay_seconds=0,
    )

    item = crawler.snapshot_item(
        {
            "id": "blocked",
            "title": "Blocked",
            "platform": "Docs",
            "url": page_url,
        }
    )

    assert item["status"] == "robots_denied"
    assert crawler.calls == [robots_url, policy_url]


def test_robots_redirect_that_only_adds_a_trailing_slash_is_not_a_loop(
    tmp_path: Path,
) -> None:
    clock = FakeClock()
    robots_url = "https://docs.example/robots.txt"
    redirected_url = "https://docs.example/robots.txt/"
    page_url = "https://docs.example/guide"
    crawler = FakeCrawler(
        tmp_path,
        {
            robots_url: response(
                robots_url,
                status=301,
                headers={"Location": "/robots.txt/"},
            ),
            redirected_url: response(
                redirected_url,
                content_type="text/plain",
                body="User-agent: *\nDisallow: /guide\n",
            ),
        },
        clock,
        retries=0,
        delay_seconds=0,
    )

    item = crawler.snapshot_item(
        {
            "id": "guide",
            "title": "Guide",
            "platform": "Docs",
            "url": page_url,
        }
    )

    assert item["status"] == "robots_denied"
    assert crawler.calls == [robots_url, redirected_url]


def test_snapshot_contract_content_hash_and_no_external_link(
    tmp_path: Path,
) -> None:
    clock = FakeClock()
    robots_url = "https://example.com/robots.txt"
    page_url = "https://example.com/testing"
    crawler = FakeCrawler(
        tmp_path,
        {
            robots_url: response(
                robots_url,
                content_type="text/plain",
                body="User-agent: *\nAllow: /\n",
            ),
            page_url: response(
                page_url,
                body=(
                    "<html><title>Testing Handbook</title><body><article>"
                    "<h1>Contract tests</h1>"
                    '<p>Use <a href="https://vendor.example/">evidence</a>.</p>'
                    + "<p>Public learning content.</p>" * 30
                    + "</article></body></html>"
                ),
            ),
        },
        clock,
        retries=0,
        delay_seconds=0,
    )

    item = crawler.snapshot_item(
        {
            "id": "testing-handbook",
            "title": "Fallback title",
            "platform": "Docs",
            "url": page_url,
            "accessed_at": "2026-07-29",
        },
        aliases=["coverage-testing-handbook"],
    )

    assert item["status"] == "downloaded"
    assert item["aliases"] == ["coverage-testing-handbook"]
    assert item["content_format"] == "markdown"
    assert item["local_path"] == "content/testing-handbook.md"
    assert item["copyright_notice"]
    local_file = tmp_path / item["local_path"]
    local_content = local_file.read_text(encoding="utf-8")
    assert "https://vendor.example" not in local_content
    assert page_url in local_content
    assert item["content_hash"] == (
        "sha256:" + hashlib.sha256(local_content.encode("utf-8")).hexdigest()
    )
    assert item["char_count"] == len(local_content)


def test_unsupported_content_type_is_recorded_without_writing_file(
    tmp_path: Path,
) -> None:
    clock = FakeClock()
    robots_url = "https://example.com/robots.txt"
    pdf_url = "https://example.com/guide.pdf"
    crawler = FakeCrawler(
        tmp_path,
        {
            robots_url: response(
                robots_url,
                content_type="text/plain",
                body="User-agent: *\nAllow: /\n",
            ),
            pdf_url: response(
                pdf_url,
                content_type="application/pdf",
                body="%PDF example",
            ),
        },
        clock,
        retries=0,
        delay_seconds=0,
    )

    item = crawler.snapshot_item(
        {
            "id": "pdf-guide",
            "title": "PDF",
            "platform": "Docs",
            "url": pdf_url,
        }
    )

    assert item["status"] == "unsupported_content_type"
    assert item["local_path"] is None
    assert not (tmp_path / "content" / "pdf-guide.md").exists()


def test_transient_http_status_is_retried(tmp_path: Path) -> None:
    clock = FakeClock()
    robots_url = "https://example.com/robots.txt"
    page_url = "https://example.com/retry"
    crawler = FakeCrawler(
        tmp_path,
        {
            robots_url: response(
                robots_url,
                content_type="text/plain",
                body="User-agent: *\nAllow: /\n",
            ),
            page_url: [
                response(page_url, status=503, body="try later"),
                response(
                    page_url,
                    body="<html><body>" + "<p>Recovered content.</p>" * 40 + "</body></html>",
                ),
            ],
        },
        clock,
        retries=1,
        delay_seconds=0,
    )

    item = crawler.snapshot_item(
        {
            "id": "retry-guide",
            "title": "Retry",
            "platform": "Docs",
            "url": page_url,
        }
    )

    assert item["status"] == "downloaded"
    assert crawler.calls.count(page_url) == 2


def test_login_or_captcha_shell_is_not_saved(tmp_path: Path) -> None:
    clock = FakeClock()
    robots_url = "https://example.com/robots.txt"
    page_url = "https://example.com/login"
    crawler = FakeCrawler(
        tmp_path,
        {
            robots_url: response(
                robots_url,
                content_type="text/plain",
                body="User-agent: *\nAllow: /\n",
            ),
            page_url: response(
                page_url,
                body="<html><body><p>请先登录并完成验证码</p></body></html>",
            ),
        },
        clock,
        retries=0,
        delay_seconds=0,
    )

    item = crawler.snapshot_item(
        {
            "id": "login-only",
            "title": "Login",
            "platform": "Community",
            "url": page_url,
        }
    )

    assert item["status"] == "access_limited"
    assert item["local_path"] is None


def test_coverage_document_ids_become_source_aliases(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    coverage = {
        "documents": [
            {
                "document_id": "xiaolincoding-testdev-navigation",
                "url": "https://xiaolincoding.com/interview/test_dev.html",
            }
        ]
    }
    (data_dir / "xiaolincoding-coverage.json").write_text(
        json.dumps(coverage), encoding="utf-8"
    )
    sources = [
        {
            "id": "xiaolincoding-testdev-2026",
            "url": "https://xiaolincoding.com/interview/test_dev.html#top",
        }
    ]

    aliases = snapshots.load_aliases(tmp_path, sources)

    assert aliases == {
        "xiaolincoding-testdev-2026": ["xiaolincoding-testdev-navigation"]
    }


def test_manifest_uses_paths_relative_to_manifest_directory(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "source-snapshots"
    catalog_path = tmp_path / "questions.json"
    catalog_path.write_text("{}", encoding="utf-8")
    item = snapshots.empty_item(
        {
            "id": "local-source",
            "title": "Local",
            "platform": "Local",
            "url": None,
        },
        [],
    )

    manifest = snapshots.write_manifest(
        output_dir, catalog_path=catalog_path, items=[item]
    )
    persisted = json.loads(
        (output_dir / "manifest.json").read_text(encoding="utf-8")
    )

    assert manifest["schema_version"] == "1.0"
    assert persisted["catalog_path"] == "../questions.json"
    assert persisted["statistics"]["by_status"] == {"no_url": 1}
    assert persisted["items"][0]["source_id"] == "local-source"


def test_resume_reuses_terminal_status_but_retries_transient_status(
    tmp_path: Path,
) -> None:
    denied = {"status": "access_denied", "local_path": None}
    transient = {"status": "network_error", "local_path": None}
    downloaded = {
        "status": "downloaded",
        "local_path": "content/guide.md",
    }
    (tmp_path / "content").mkdir()
    (tmp_path / "content" / "guide.md").write_text("guide", encoding="utf-8")

    assert snapshots.should_reuse(denied, tmp_path) is True
    assert snapshots.should_reuse(transient, tmp_path) is False
    assert snapshots.should_reuse(downloaded, tmp_path) is True


def test_html_image_is_downloaded_and_markdown_only_references_local_asset(
    tmp_path: Path,
) -> None:
    clock = FakeClock()
    robots_url = "https://docs.example/robots.txt"
    page_url = "https://docs.example/guide"
    image_url = "https://docs.example/images/chart.png"
    png = b"\x89PNG\r\n\x1a\nsafe-image"
    crawler = FakeCrawler(
        tmp_path,
        {
            robots_url: response(
                robots_url,
                content_type="text/plain",
                body="User-agent: *\nAllow: /\n",
            ),
            page_url: response(
                page_url,
                body=(
                    "<html><title>Guide</title><body><article>"
                    "<h1>Evidence</h1><img src='/images/chart.png' alt='P95 chart'>"
                    + "<p>Visible test guidance.</p>" * 30
                    + "</article></body></html>"
                ),
            ),
            image_url: binary_response(
                image_url, body=png, content_type="image/png"
            ),
        },
        clock,
        retries=0,
        delay_seconds=0,
    )

    item = crawler.snapshot_item(
        {
            "id": "image-guide",
            "title": "Image guide",
            "platform": "Docs",
            "url": page_url,
        }
    )

    assert item["status"] == "downloaded"
    assert len(item["assets"]) == 1
    asset = item["assets"][0]
    assert asset["status"] == "downloaded"
    assert asset["original_url"] == image_url
    assert asset["mime_type"] == "image/png"
    assert asset["content_hash"] == (
        "sha256:" + hashlib.sha256(png).hexdigest()
    )
    assert (tmp_path / asset["local_path"]).read_bytes() == png
    markdown = (tmp_path / item["local_path"]).read_text(encoding="utf-8")
    assert f"![P95 chart](snapshot-asset:{asset['asset_id']})" in markdown
    assert image_url not in markdown


def test_picture_prefers_srcset_candidate_and_rejects_svg(
    tmp_path: Path,
) -> None:
    clock = FakeClock()
    robots_url = "https://docs.example/robots.txt"
    page_url = "https://docs.example/guide"
    svg_url = "https://docs.example/images/diagram.svg"
    crawler = FakeCrawler(
        tmp_path,
        {
            robots_url: response(
                robots_url,
                content_type="text/plain",
                body="User-agent: *\nAllow: /\n",
            ),
            page_url: response(
                page_url,
                body=(
                    "<html><body><picture>"
                    "<source srcset='/images/small.svg 1x, /images/diagram.svg 2x'>"
                    "<img src='/images/fallback.png' alt='Architecture'>"
                    "</picture>"
                    + "<p>Visible content.</p>" * 30
                    + "</body></html>"
                ),
            ),
            svg_url: binary_response(
                svg_url,
                body=b"<svg><script>alert(1)</script></svg>",
                content_type="image/svg+xml",
            ),
        },
        clock,
        retries=0,
        delay_seconds=0,
    )

    item = crawler.snapshot_item(
        {
            "id": "picture-guide",
            "title": "Picture",
            "platform": "Docs",
            "url": page_url,
        }
    )

    assert item["status"] == "downloaded"
    assert item["assets"][0]["original_url"] == svg_url
    assert item["assets"][0]["status"] == "unsafe_svg"
    assert not (tmp_path / "assets").exists()
    markdown = (tmp_path / item["local_path"]).read_text(encoding="utf-8")
    assert "[图片未缓存：Architecture]" in markdown
    assert ".svg" not in markdown


def test_image_fetch_respects_cross_origin_robots(
    tmp_path: Path,
) -> None:
    clock = FakeClock()
    page_robots = "https://docs.example/robots.txt"
    image_robots = "https://cdn.example/robots.txt"
    page_url = "https://docs.example/guide"
    denied_image_url = "https://cdn.example/private/image.png"
    crawler = FakeCrawler(
        tmp_path,
        {
            page_robots: response(
                page_robots,
                content_type="text/plain",
                body="User-agent: *\nAllow: /\n",
            ),
            image_robots: response(
                image_robots,
                content_type="text/plain",
                body="User-agent: *\nDisallow: /private/\n",
            ),
            page_url: response(
                page_url,
                body=(
                    f"<html><body><img src='{denied_image_url}' alt='Denied'>"
                    + "<p>Text.</p>" * 50
                    + "</body></html>"
                ),
            ),
        },
        clock,
        retries=0,
        delay_seconds=0,
        max_asset_bytes=12,
    )

    item = crawler.snapshot_item(
        {
            "id": "robots-image",
            "title": "Robots image",
            "platform": "Docs",
            "url": page_url,
        }
    )

    assert item["assets"][0]["status"] == "robots_denied"
    assert denied_image_url not in crawler.calls
    assert not (tmp_path / "assets").exists()


def test_image_redirect_is_revalidated_and_size_limit_stops_write(
    tmp_path: Path,
) -> None:
    clock = FakeClock()
    page_robots = "https://docs.example/robots.txt"
    cdn_robots = "https://cdn.example/robots.txt"
    image_robots = "https://images.example/robots.txt"
    page_url = "https://docs.example/guide"
    old_image_url = "https://cdn.example/chart.png"
    final_image_url = "https://images.example/chart.png"
    oversized_url = "https://docs.example/oversized.png"
    png = b"\x89PNG\r\n\x1a\nredirected"
    crawler = FakeCrawler(
        tmp_path,
        {
            page_robots: response(
                page_robots,
                content_type="text/plain",
                body="User-agent: *\nAllow: /\n",
            ),
            cdn_robots: response(
                cdn_robots,
                content_type="text/plain",
                body="User-agent: *\nAllow: /\n",
            ),
            image_robots: response(
                image_robots,
                content_type="text/plain",
                body="User-agent: *\nAllow: /\n",
            ),
            page_url: response(
                page_url,
                body=(
                    f"<html><body><img src='{old_image_url}' alt='Redirected'>"
                    f"<img src='{oversized_url}' alt='Too large'>"
                    + "<p>Text.</p>" * 50
                    + "</body></html>"
                ),
            ),
            old_image_url: response(
                old_image_url,
                status=302,
                headers={"Location": final_image_url},
            ),
            final_image_url: binary_response(
                final_image_url, body=png, content_type="image/png"
            ),
            oversized_url: binary_response(
                oversized_url,
                body=b"\x89PNG\r\n\x1a\n" + b"x" * 100,
                content_type="image/png",
            ),
        },
        clock,
        retries=0,
        delay_seconds=0,
        max_asset_bytes=32,
    )

    item = crawler.snapshot_item(
        {
            "id": "redirected-image",
            "title": "Redirected image",
            "platform": "Docs",
            "url": page_url,
        }
    )

    assets = {asset["alt_text"]: asset for asset in item["assets"]}
    assert assets["Redirected"]["status"] == "downloaded"
    assert assets["Redirected"]["original_url"] == old_image_url
    assert assets["Redirected"]["final_url"] == final_image_url
    assert assets["Too large"]["status"] == "too_large"
    assert assets["Too large"]["local_path"] is None
    assert image_robots in crawler.calls


def test_xiaolincoding_vuepress_fixture_extracts_only_article_content() -> None:
    source_html = (
        FIXTURES_DIR / "xiaolincoding-vuepress-page.html"
    ).read_text(encoding="utf-8")

    title, content, candidates = snapshots.convert_html_with_images(
        source_html, "Fallback"
    )

    assert title == "业务测试面试题 | 小林 Coding"
    assert "# 业务测试面试题" in content
    assert "## 登录测试" in content
    assert "# #" not in content
    assert "正文介绍测试策略" in content
    assert "安全资料" in content
    assert "outside.example" not in content
    for chrome_text in (
        "首页",
        "面试题导航",
        "Java 面试题",
        "本页目录",
        "赞助广告",
        "编辑此页",
        "上一篇",
        "站点页脚",
    ):
        assert chrome_text not in content
    assert [candidate.original_url for candidate in candidates] == [
        "/images/business-large.webp",
        "/images/login-flow.png",
    ]


def test_xiaolincoding_fixture_does_not_download_chrome_images(
    tmp_path: Path,
) -> None:
    clock = FakeClock()
    page_url = "https://xiaolincoding.example/interview/business.html"
    robots_url = "https://xiaolincoding.example/robots.txt"
    picture_url = "https://xiaolincoding.example/images/business-large.webp"
    flow_url = "https://xiaolincoding.example/images/login-flow.png"
    source_html = (
        FIXTURES_DIR / "xiaolincoding-vuepress-page.html"
    ).read_text(encoding="utf-8")
    webp = b"RIFF\x08\x00\x00\x00WEBPfixture"
    png = b"\x89PNG\r\n\x1a\nfixture"
    crawler = FakeCrawler(
        tmp_path,
        {
            robots_url: response(
                robots_url,
                content_type="text/plain",
                body="User-agent: *\nAllow: /\n",
            ),
            page_url: response(page_url, body=source_html),
            picture_url: binary_response(
                picture_url, body=webp, content_type="image/webp"
            ),
            flow_url: binary_response(
                flow_url, body=png, content_type="image/png"
            ),
        },
        clock,
        retries=0,
        delay_seconds=0,
        max_assets_per_source=2,
    )

    item = crawler.snapshot_item(
        {
            "id": "xiaolincoding-business-fixture",
            "title": "Business testing",
            "platform": "小林 Coding",
            "url": page_url,
        }
    )

    assert item["status"] == "downloaded"
    assert len(item["assets"]) == 2
    assert {asset["status"] for asset in item["assets"]} == {"downloaded"}
    assert all(asset["status"] != "asset_count_limit" for asset in item["assets"])
    assert crawler.calls == [
        robots_url,
        page_url,
        picture_url,
        flow_url,
    ]
    markdown = (tmp_path / item["local_path"]).read_text(encoding="utf-8")
    assert "# #" not in markdown
    assert "全站 Logo" not in markdown
    assert "侧栏图片" not in markdown
    assert "广告图片" not in markdown
    assert "snapshot-asset:" in markdown
