from __future__ import annotations

import base64
import hashlib
import json
import sys
from pathlib import Path

import pytest


SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import import_browser_snapshots as browser_import  # noqa: E402


def write_catalog(path: Path, sources: list[dict[str, object]]) -> None:
    path.write_text(
        json.dumps({"sources": sources}, ensure_ascii=False),
        encoding="utf-8",
    )


def source(source_id: str, url: str) -> dict[str, object]:
    return {
        "id": source_id,
        "title": f"{source_id} title",
        "platform": "Public docs",
        "url": url,
        "accessed_at": "2026-07-29",
    }


def test_json_import_preserves_other_manifest_items_and_writes_compatible_snapshot(
    tmp_path: Path,
) -> None:
    catalog_path = tmp_path / "questions.json"
    output_dir = tmp_path / "source-snapshots"
    content_dir = output_dir / "content"
    content_dir.mkdir(parents=True)
    imported_source = source("authorized-page", "https://example.com/authorized")
    other_source = source("existing-page", "https://example.com/existing")
    write_catalog(catalog_path, [imported_source, other_source])
    old_content = "# Existing\n"
    (content_dir / "existing-page.md").write_text(old_content, encoding="utf-8")
    existing_item = {
        "source_id": "existing-page",
        "aliases": [],
        "title": "Existing",
        "platform": "Public docs",
        "original_url": "https://example.com/existing",
        "local_path": "content/existing-page.md",
        "content_format": "markdown",
        "status": "downloaded",
        "content_hash": (
            "sha256:" + hashlib.sha256(old_content.encode("utf-8")).hexdigest()
        ),
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "custom_top_level": "preserve-me",
                "policy": {"scope": "existing"},
                "items": [existing_item],
            }
        ),
        encoding="utf-8",
    )
    export_path = tmp_path / "browser-export.json"
    export_path.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "source_id": "authorized-page",
                        "original_url": "https://example.com/authorized",
                        "title": "Authorized visible page",
                        "content_format": "markdown",
                        "captured_at": "2026-07-29T10:30:00+08:00",
                        "content": "## Visible section\n\nOnly visible public learning text.",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    manifest = browser_import.import_snapshots(
        input_path=export_path,
        catalog_path=catalog_path,
        output_dir=output_dir,
    )

    assert manifest["custom_top_level"] == "preserve-me"
    items = {item["source_id"]: item for item in manifest["items"]}
    assert items["existing-page"] == existing_item
    imported = items["authorized-page"]
    assert imported["status"] == "downloaded"
    assert imported["capture_method"] == "authenticated_browser_visible_text"
    assert imported["original_url"] == "https://example.com/authorized"
    assert imported["local_path"] == "content/authorized-page.md"
    assert imported["captured_at"] == "2026-07-29T02:30:00+00:00"
    assert "headers" not in imported
    assert "cookies" not in imported
    content = (output_dir / imported["local_path"]).read_text(encoding="utf-8")
    assert "Only visible public learning text." in content
    assert imported["content_hash"] == (
        "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()
    )
    assert imported["byte_count"] == len(content.encode("utf-8"))


def test_ndjson_input_is_supported(tmp_path: Path) -> None:
    catalog_path = tmp_path / "questions.json"
    output_dir = tmp_path / "snapshots"
    first = source("first", "https://example.com/first")
    second = source("second", "https://example.com/second")
    write_catalog(catalog_path, [first, second])
    export_path = tmp_path / "browser-export.ndjson"
    records = [
        {
            "source_id": "first",
            "original_url": "https://example.com/first",
            "content_format": "plain_text",
            "content": "First visible text.",
        },
        {
            "source_id": "second",
            "original_url": "https://example.com/second",
            "content_format": "text",
            "content": "Second visible text.",
        },
    ]
    export_path.write_text(
        "\n".join(json.dumps(record) for record in records) + "\n",
        encoding="utf-8",
    )

    manifest = browser_import.import_snapshots(
        input_path=export_path,
        catalog_path=catalog_path,
        output_dir=output_dir,
    )

    assert manifest["statistics"]["by_status"] == {"downloaded": 2}
    assert (output_dir / "content" / "first.md").is_file()
    assert (output_dir / "content" / "second.md").is_file()


def test_unregistered_or_non_exact_url_is_rejected_before_any_write(
    tmp_path: Path,
) -> None:
    catalog_path = tmp_path / "questions.json"
    output_dir = tmp_path / "snapshots"
    output_dir.mkdir()
    write_catalog(
        catalog_path,
        [source("registered", "https://example.com/page?view=public")],
    )
    old_manifest = '{"items":[]}\n'
    (output_dir / "manifest.json").write_text(old_manifest, encoding="utf-8")
    export_path = tmp_path / "browser-export.json"
    export_path.write_text(
        json.dumps(
            [
                {
                    "source_id": "registered",
                    "original_url": "https://example.com/page",
                    "content_format": "markdown",
                    "content": "Visible content",
                }
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(browser_import.ImportValidationError, match="不完全一致"):
        browser_import.import_snapshots(
            input_path=export_path,
            catalog_path=catalog_path,
            output_dir=output_dir,
        )

    assert (output_dir / "manifest.json").read_text(encoding="utf-8") == old_manifest
    assert not (output_dir / "content").exists()


@pytest.mark.parametrize(
    ("catalog_id", "extra_field"),
    [
        ("../escape", None),
        ("safe-id", {"local_path": "../../escape.md"}),
        ("safe-id", {"headers": {"Cookie": "secret"}}),
        ("safe-id", {"cookies": [{"name": "session", "value": "secret"}]}),
    ],
)
def test_path_or_session_metadata_is_rejected(
    tmp_path: Path,
    catalog_id: str,
    extra_field: dict[str, object] | None,
) -> None:
    catalog_path = tmp_path / "questions.json"
    output_dir = tmp_path / "snapshots"
    url = "https://example.com/page"
    write_catalog(catalog_path, [source(catalog_id, url)])
    record: dict[str, object] = {
        "source_id": catalog_id,
        "original_url": url,
        "content_format": "markdown",
        "content": "Visible text",
    }
    if extra_field:
        record.update(extra_field)
    export_path = tmp_path / "browser-export.json"
    export_path.write_text(json.dumps([record]), encoding="utf-8")

    with pytest.raises(browser_import.ImportValidationError):
        browser_import.import_snapshots(
            input_path=export_path,
            catalog_path=catalog_path,
            output_dir=output_dir,
        )

    assert not output_dir.exists()
    assert not (tmp_path / "escape.md").exists()


def test_item_and_total_size_limits_are_enforced_before_write(
    tmp_path: Path,
) -> None:
    catalog_path = tmp_path / "questions.json"
    output_dir = tmp_path / "snapshots"
    write_catalog(
        catalog_path,
        [
            source("first", "https://example.com/first"),
            source("second", "https://example.com/second"),
        ],
    )
    export_path = tmp_path / "browser-export.json"
    export_path.write_text(
        json.dumps(
            [
                {
                    "source_id": "first",
                    "original_url": "https://example.com/first",
                    "content_format": "text",
                    "content": "12345",
                },
                {
                    "source_id": "second",
                    "original_url": "https://example.com/second",
                    "content_format": "text",
                    "content": "67890",
                },
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(browser_import.ImportValidationError, match="总上限"):
        browser_import.import_snapshots(
            input_path=export_path,
            catalog_path=catalog_path,
            output_dir=output_dir,
            max_item_bytes=5,
            max_total_bytes=9,
        )

    assert not output_dir.exists()


def test_executable_markup_is_rejected(tmp_path: Path) -> None:
    catalog_path = tmp_path / "questions.json"
    output_dir = tmp_path / "snapshots"
    write_catalog(catalog_path, [source("page", "https://example.com/page")])
    export_path = tmp_path / "browser-export.json"
    export_path.write_text(
        json.dumps(
            [
                {
                    "source_id": "page",
                    "original_url": "https://example.com/page",
                    "content_format": "markdown",
                    "content": "<script>alert(document.cookie)</script>",
                }
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(browser_import.ImportValidationError, match="危险"):
        browser_import.import_snapshots(
            input_path=export_path,
            catalog_path=catalog_path,
            output_dir=output_dir,
        )

    assert not output_dir.exists()


def test_base64_asset_is_hashed_saved_and_referenced_locally(
    tmp_path: Path,
) -> None:
    catalog_path = tmp_path / "questions.json"
    output_dir = tmp_path / "snapshots"
    write_catalog(catalog_path, [source("page", "https://example.com/page")])
    png = b"\x89PNG\r\n\x1a\nbrowser-visible-image"
    export_path = tmp_path / "browser-export.json"
    export_path.write_text(
        json.dumps(
            [
                {
                    "source_id": "page",
                    "original_url": "https://example.com/page",
                    "content_format": "markdown",
                    "content": (
                        "Architecture:\n\n{{asset:diagram}}\n\n"
                        "![legacy](../assets/page/diagram.png)"
                    ),
                    "assets": [
                        {
                            "asset_id": "diagram",
                            "original_url": "https://cdn.example.com/diagram.png",
                            "mime_type": "image/png",
                            "alt_text": "Architecture diagram",
                            "base64": base64.b64encode(png).decode("ascii"),
                            "file_path": "missing-but-not-read.png",
                        }
                    ],
                }
            ]
        ),
        encoding="utf-8",
    )

    manifest = browser_import.import_snapshots(
        input_path=export_path,
        catalog_path=catalog_path,
        output_dir=output_dir,
    )

    item = manifest["items"][0]
    assert item["capture_method"] == "authenticated_browser_visible_text"
    assert len(item["assets"]) == 1
    asset = item["assets"][0]
    assert asset["capture_method"] == "authenticated_browser_visible_asset"
    assert asset["content_hash"] == (
        "sha256:" + hashlib.sha256(png).hexdigest()
    )
    assert (output_dir / asset["local_path"]).read_bytes() == png
    markdown = (output_dir / item["local_path"]).read_text(encoding="utf-8")
    assert "![Architecture diagram](snapshot-asset:diagram)" in markdown
    assert "![legacy](snapshot-asset:diagram)" in markdown
    assert "../assets/" not in markdown
    assert "https://cdn.example.com/diagram.png" not in markdown
    assert "file_path" not in asset
    assert "base64" not in asset


def test_relative_asset_file_is_allowed_but_traversal_and_symlinks_are_rejected(
    tmp_path: Path,
) -> None:
    catalog_path = tmp_path / "questions.json"
    output_dir = tmp_path / "snapshots"
    write_catalog(catalog_path, [source("page", "https://example.com/page")])
    export_assets = tmp_path / "export-assets"
    export_assets.mkdir()
    png_path = export_assets / "diagram.png"
    png_path.write_bytes(b"\x89PNG\r\n\x1a\nlocal-file")
    export_path = tmp_path / "browser-export.json"

    def write_export(file_path: str) -> None:
        export_path.write_text(
            json.dumps(
                [
                    {
                        "source_id": "page",
                        "original_url": "https://example.com/page",
                        "content_format": "text",
                        "content": "Visible text",
                        "assets": [
                            {
                                "asset_id": "diagram",
                                "original_url": "https://cdn.example.com/diagram.png",
                                "mime_type": "image/png",
                                "file_path": file_path,
                            }
                        ],
                    }
                ]
            ),
            encoding="utf-8",
        )

    write_export("export-assets/diagram.png")
    manifest = browser_import.import_snapshots(
        input_path=export_path,
        catalog_path=catalog_path,
        output_dir=output_dir,
    )
    assert manifest["items"][0]["assets"][0]["status"] == "downloaded"

    write_export("../outside.png")
    with pytest.raises(browser_import.ImportValidationError, match="路径穿越"):
        browser_import.import_snapshots(
            input_path=export_path,
            catalog_path=catalog_path,
            output_dir=tmp_path / "other-output",
        )

    symlink_path = export_assets / "linked.png"
    try:
        symlink_path.symlink_to(png_path)
    except OSError as error:
        if getattr(error, "winerror", None) == 1314:
            pytest.skip("当前 Windows 用户没有创建符号链接的权限")
        raise
    write_export("export-assets/linked.png")
    with pytest.raises(browser_import.ImportValidationError, match="符号链接"):
        browser_import.import_snapshots(
            input_path=export_path,
            catalog_path=catalog_path,
            output_dir=tmp_path / "symlink-output",
        )


@pytest.mark.parametrize(
    ("asset", "message"),
    [
        (
            {
                "asset_id": "private",
                "original_url": "http://127.0.0.1/secret.png",
                "mime_type": "image/png",
                "base64": "iVBORw0KGgpmYWtl",
            },
            "非公网",
        ),
        (
            {
                "asset_id": "svg",
                "original_url": "https://cdn.example.com/x.svg",
                "mime_type": "image/svg+xml",
                "base64": "PHN2Zz48L3N2Zz4=",
            },
            "SVG",
        ),
        (
            {
                "asset_id": "spoofed",
                "original_url": "https://cdn.example.com/x.png",
                "mime_type": "image/png",
                "base64": "bm90LWEtcG5n",
            },
            "文件签名",
        ),
    ],
)
def test_unsafe_asset_url_svg_or_spoofed_mime_is_rejected(
    tmp_path: Path,
    asset: dict[str, object],
    message: str,
) -> None:
    catalog_path = tmp_path / "questions.json"
    output_dir = tmp_path / "snapshots"
    write_catalog(catalog_path, [source("page", "https://example.com/page")])
    export_path = tmp_path / "browser-export.json"
    export_path.write_text(
        json.dumps(
            [
                {
                    "source_id": "page",
                    "original_url": "https://example.com/page",
                    "content_format": "markdown",
                    "content": "Visible text",
                    "assets": [asset],
                }
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(browser_import.ImportValidationError, match=message):
        browser_import.import_snapshots(
            input_path=export_path,
            catalog_path=catalog_path,
            output_dir=output_dir,
        )

    assert not output_dir.exists()


def test_asset_size_and_count_limits_are_enforced_before_write(
    tmp_path: Path,
) -> None:
    catalog_path = tmp_path / "questions.json"
    output_dir = tmp_path / "snapshots"
    write_catalog(catalog_path, [source("page", "https://example.com/page")])
    png = base64.b64encode(b"\x89PNG\r\n\x1a\n12345").decode("ascii")
    export_path = tmp_path / "browser-export.json"
    export_path.write_text(
        json.dumps(
            [
                {
                    "source_id": "page",
                    "original_url": "https://example.com/page",
                    "content_format": "markdown",
                    "content": "Visible text",
                    "assets": [
                        {
                            "asset_id": "one",
                            "original_url": "https://cdn.example.com/1.png",
                            "mime_type": "image/png",
                            "base64": png,
                        },
                        {
                            "asset_id": "two",
                            "original_url": "https://cdn.example.com/2.png",
                            "mime_type": "image/png",
                            "base64": png,
                        },
                    ],
                }
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(browser_import.ImportValidationError, match="图片数"):
        browser_import.import_snapshots(
            input_path=export_path,
            catalog_path=catalog_path,
            output_dir=output_dir,
            max_assets_per_record=1,
        )

    assert not output_dir.exists()


def test_import_removes_external_markdown_links_and_images(
    tmp_path: Path,
) -> None:
    catalog_path = tmp_path / "questions.json"
    output_dir = tmp_path / "snapshots"
    write_catalog(catalog_path, [source("page", "https://example.com/page")])
    export_path = tmp_path / "browser-export.json"
    export_path.write_text(
        json.dumps(
            [
                {
                    "source_id": "page",
                    "original_url": "https://example.com/page",
                    "content_format": "markdown",
                    "content": (
                        "[official link](https://outside.example/docs)\n\n"
                        "![remote chart](https://outside.example/chart.png)"
                    ),
                }
            ]
        ),
        encoding="utf-8",
    )

    manifest = browser_import.import_snapshots(
        input_path=export_path,
        catalog_path=catalog_path,
        output_dir=output_dir,
    )

    content = (output_dir / manifest["items"][0]["local_path"]).read_text(
        encoding="utf-8"
    )
    assert "official link" in content
    assert "[外部图片未导入：remote chart]" in content
    assert "outside.example" not in content
