#!/usr/bin/env python3
"""导入用户已授权浏览器导出的可见文本，不接触浏览器会话或认证材料。

输入只允许：

* ``source_id``：必须已经登记在 ``questions.json``；
* ``original_url``：必须与该来源登记 URL 逐字相同；
* ``content``：UTF-8 纯文本或 Markdown；
* ``content_format``：``plain_text``、``text`` 或 ``markdown``；
* 可选 ``title``、``captured_at``；
* 可选 ``assets``：每张图片使用 ``asset_id``、公网 ``original_url``、
  ``mime_type``，并提供 base64 或导出文件同目录树内的相对 ``file_path``。

Cookie、headers、local_path 等字段会被拒绝，而不是忽略或写入 manifest。
导入器只读取用户明确提供的本地 JSON/NDJSON 和图片文件，不连接浏览器、
不读取登录态，也不会发起任何网络请求。正文中的图片占位最终转换为
``snapshot-asset:<asset_id>``，真实文件只写入本地 ``source-snapshots/assets``。
"""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import ipaddress
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import urlsplit

from fetch_sources import (
    BANK_DIR,
    DEFAULT_CATALOG,
    DEFAULT_OUTPUT,
    SAFE_SOURCE_ID,
    SUPPORTED_IMAGE_TYPES,
    atomic_write_bytes,
    atomic_write_text,
    copyright_notice,
    empty_item,
    load_aliases,
    load_json,
    image_signature_matches,
    markdown_alt,
    safe_file_name,
    utc_now,
)


DEFAULT_MAX_ITEM_BYTES = 5_000_000
DEFAULT_MAX_TOTAL_BYTES = 20_000_000
DEFAULT_MAX_INPUT_BYTES = 50_000_000
DEFAULT_MAX_RECORDS = 500
DEFAULT_MAX_ASSET_BYTES = 5_000_000
DEFAULT_MAX_ASSET_TOTAL_BYTES = 20_000_000
DEFAULT_MAX_ASSETS_PER_RECORD = 20
DEFAULT_MAX_ASSETS_TOTAL = 100
ALLOWED_RECORD_KEYS = {
    "assets",
    "captured_at",
    "content",
    "content_format",
    "original_url",
    "source_id",
    "title",
}
ALLOWED_ASSET_KEYS = {
    "alt_text",
    "asset_id",
    "base64",
    "file_path",
    "mime_type",
    "original_url",
}
ALLOWED_CONTENT_FORMATS = {"markdown", "plain_text", "text"}
DANGEROUS_MARKUP_RE = re.compile(
    r"<\s*/?\s*(?:script|style|iframe|object|embed|svg|form|input|button|"
    r"meta|link|a|img|picture|source|audio|video)\b|"
    r"javascript\s*:|data\s*:\s*text/html",
    re.IGNORECASE,
)
CONTROL_CHARACTER_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
EXTERNAL_MARKDOWN_IMAGE_RE = re.compile(
    r"!\[([^\]]*)\]\(\s*https?://[^)\s]+(?:\s+[^)]*)?\)",
    re.IGNORECASE,
)
EXTERNAL_MARKDOWN_LINK_RE = re.compile(
    r"(?<!!)\[([^\]]+)\]\(\s*https?://[^)\s]+(?:\s+[^)]*)?\)",
    re.IGNORECASE,
)


class ImportValidationError(ValueError):
    """导出文件不满足本地快照导入契约。"""


def read_limited(path: Path, max_bytes: int) -> bytes:
    if not path.is_file():
        raise ImportValidationError(f"导出文件不存在或不是普通文件：{path}")
    declared_size = path.stat().st_size
    if declared_size > max_bytes:
        raise ImportValidationError(
            f"导出文件 {declared_size} 字节，超过输入上限 {max_bytes}"
        )
    with path.open("rb") as stream:
        payload = stream.read(max_bytes + 1)
    if len(payload) > max_bytes:
        raise ImportValidationError(f"导出文件超过输入上限 {max_bytes}")
    return payload


def parse_records(
    input_path: Path,
    *,
    max_input_bytes: int = DEFAULT_MAX_INPUT_BYTES,
    max_records: int = DEFAULT_MAX_RECORDS,
) -> list[dict[str, Any]]:
    raw = read_limited(input_path, max_input_bytes)
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ImportValidationError("导出文件必须是 UTF-8 JSON/NDJSON") from exc
    suffix = input_path.suffix.lower()
    records: Any
    if suffix in {".ndjson", ".jsonl"}:
        records = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ImportValidationError(
                    f"NDJSON 第 {line_number} 行不是有效 JSON"
                ) from exc
            records.append(record)
    else:
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ImportValidationError("导出文件不是有效 JSON") from exc
        if isinstance(payload, list):
            records = payload
        elif isinstance(payload, dict) and set(payload) == {"items"}:
            records = payload["items"]
        else:
            raise ImportValidationError(
                "JSON 顶层必须是数组，或仅包含 items 数组的对象"
            )
    if not isinstance(records, list) or not records:
        raise ImportValidationError("导出文件至少需要一条记录")
    if len(records) > max_records:
        raise ImportValidationError(
            f"记录数 {len(records)} 超过上限 {max_records}"
        )
    normalized: list[dict[str, Any]] = []
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise ImportValidationError(f"第 {index} 条记录必须是对象")
        normalized.append(record)
    return normalized


def normalize_captured_at(value: Any) -> str:
    if value is None or value == "":
        return utc_now()
    if not isinstance(value, str) or len(value) > 64:
        raise ImportValidationError("captured_at 必须是带时区的 ISO-8601 字符串")
    candidate = value.strip()
    if candidate.endswith("Z"):
        candidate = f"{candidate[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ImportValidationError(
            "captured_at 必须是带时区的 ISO-8601 字符串"
        ) from exc
    if parsed.tzinfo is None:
        raise ImportValidationError("captured_at 必须包含时区")
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def normalize_content(value: Any, content_format: Any) -> tuple[str, int]:
    if not isinstance(content_format, str) or content_format not in ALLOWED_CONTENT_FORMATS:
        raise ImportValidationError(
            "content_format 只允许 markdown、plain_text 或 text"
        )
    if not isinstance(value, str):
        raise ImportValidationError("content 必须是字符串")
    content = value.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not content:
        raise ImportValidationError("content 不能为空")
    if CONTROL_CHARACTER_RE.search(content):
        raise ImportValidationError("content 含有不允许的控制字符")
    if DANGEROUS_MARKUP_RE.search(content):
        raise ImportValidationError("content 含有脚本、可执行 HTML 或危险协议")
    return content, len(content.encode("utf-8"))


def validate_public_asset_url(url: Any) -> str:
    if not isinstance(url, str) or len(url) > 4_096:
        raise ImportValidationError("图片 original_url 必须是合理长度的 URL")
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ImportValidationError("图片 original_url 只允许公网 http/https")
    if parsed.username or parsed.password:
        raise ImportValidationError("图片 original_url 禁止包含用户凭据")
    host = parsed.hostname.rstrip(".").lower()
    if host == "localhost" or host.endswith(
        (".localhost", ".local", ".internal", ".lan", ".corp", ".home", ".test")
    ):
        raise ImportValidationError("图片 original_url 禁止本机或局域网主机")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        if (
            address.is_private
            or address.is_loopback
            or address.is_link_local
            or address.is_reserved
            or address.is_multicast
            or address.is_unspecified
        ):
            raise ImportValidationError("图片 original_url 禁止非公网 IP")
    return url


def safe_asset_file_path(value: Any, input_root: Path) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ImportValidationError("图片 file_path 必须是导出目录内的相对路径")
    if "\\" in value or re.match(r"^[A-Za-z]:", value):
        raise ImportValidationError("图片 file_path 禁止 Windows 绝对路径或反斜杠")
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise ImportValidationError("图片 file_path 禁止绝对路径或路径穿越")
    resolved_root = input_root.resolve()
    candidate = resolved_root / relative
    cursor = resolved_root
    for part in relative.parts:
        cursor /= part
        if cursor.is_symlink():
            raise ImportValidationError("图片 file_path 禁止符号链接")
    resolved = candidate.resolve()
    if not resolved.is_relative_to(resolved_root):
        raise ImportValidationError("图片 file_path 越过导出文件所在目录")
    return resolved


def validate_assets(
    value: Any,
    *,
    input_root: Path,
    max_assets: int,
    max_asset_bytes: int,
) -> tuple[list[dict[str, Any]], int]:
    if value is None:
        return [], 0
    if not isinstance(value, list):
        raise ImportValidationError("assets 必须是数组")
    if len(value) > max_assets:
        raise ImportValidationError(f"单条来源图片数超过上限 {max_assets}")
    validated: list[dict[str, Any]] = []
    seen: set[str] = set()
    total_bytes = 0
    for index, asset in enumerate(value, start=1):
        if not isinstance(asset, dict):
            raise ImportValidationError(f"第 {index} 个 asset 必须是对象")
        unknown = set(asset) - ALLOWED_ASSET_KEYS
        if unknown:
            raise ImportValidationError(
                f"asset {index} 包含不允许字段：{', '.join(sorted(unknown))}"
            )
        required = {"asset_id", "original_url", "mime_type"}
        missing = required - set(asset)
        if missing:
            raise ImportValidationError(
                f"asset {index} 缺少字段：{', '.join(sorted(missing))}"
            )
        asset_id = asset.get("asset_id")
        if not isinstance(asset_id, str) or not SAFE_SOURCE_ID.fullmatch(asset_id):
            raise ImportValidationError(
                f"asset {index} 的 asset_id 非法，禁止路径分隔符或路径穿越"
            )
        if asset_id in seen:
            raise ImportValidationError(f"assets 包含重复 asset_id：{asset_id}")
        seen.add(asset_id)
        original_url = validate_public_asset_url(asset.get("original_url"))
        mime_type = asset.get("mime_type")
        if not isinstance(mime_type, str):
            raise ImportValidationError(f"asset {asset_id} 缺少有效 mime_type")
        mime_type = mime_type.strip().lower()
        if mime_type == "image/svg+xml":
            raise ImportValidationError(
                f"asset {asset_id} 是 SVG；为避免脚本和外部引用，导入器拒绝保存"
            )
        if mime_type not in SUPPORTED_IMAGE_TYPES:
            raise ImportValidationError(
                f"asset {asset_id} 图片类型不受支持：{mime_type}"
            )
        encoded = asset.get("base64")
        file_path = asset.get("file_path")
        if encoded is None and file_path is None:
            raise ImportValidationError(
                f"asset {asset_id} 必须提供 base64 或 file_path"
            )
        safe_path: Path | None = None
        if file_path is not None:
            safe_path = safe_asset_file_path(file_path, input_root)
        if encoded is not None:
            if not isinstance(encoded, str):
                raise ImportValidationError(f"asset {asset_id} 的 base64 必须是字符串")
            try:
                content = base64.b64decode(encoded, validate=True)
            except (binascii.Error, ValueError) as exc:
                raise ImportValidationError(
                    f"asset {asset_id} 的 base64 无效"
                ) from exc
        else:
            assert safe_path is not None
            if safe_path.is_symlink() or not safe_path.is_file():
                raise ImportValidationError(
                    f"asset {asset_id} 的 file_path 必须是非符号链接普通文件"
                )
            if safe_path.stat().st_size > max_asset_bytes:
                raise ImportValidationError(
                    f"asset {asset_id} 超过单图上限 {max_asset_bytes}"
                )
            content = read_limited(safe_path, max_asset_bytes)
        if not content:
            raise ImportValidationError(f"asset {asset_id} 内容为空")
        if len(content) > max_asset_bytes:
            raise ImportValidationError(
                f"asset {asset_id} 超过单图上限 {max_asset_bytes}"
            )
        if not image_signature_matches(content, mime_type):
            raise ImportValidationError(
                f"asset {asset_id} 内容与 mime_type 文件签名不一致"
            )
        alt_text = asset.get("alt_text") or "图片"
        if (
            not isinstance(alt_text, str)
            or not alt_text.strip()
            or len(alt_text) > 500
            or CONTROL_CHARACTER_RE.search(alt_text)
        ):
            raise ImportValidationError(f"asset {asset_id} 的 alt_text 无效")
        total_bytes += len(content)
        validated.append(
            {
                "asset_id": asset_id,
                "original_url": original_url,
                "mime_type": mime_type,
                "alt_text": alt_text.strip(),
                "content": content,
            }
        )
    return validated, total_bytes


def validate_records(
    records: Iterable[Mapping[str, Any]],
    catalog_sources: Iterable[Mapping[str, Any]],
    *,
    max_item_bytes: int = DEFAULT_MAX_ITEM_BYTES,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
    input_root: Path,
    max_asset_bytes: int = DEFAULT_MAX_ASSET_BYTES,
    max_asset_total_bytes: int = DEFAULT_MAX_ASSET_TOTAL_BYTES,
    max_assets_per_record: int = DEFAULT_MAX_ASSETS_PER_RECORD,
    max_assets_total: int = DEFAULT_MAX_ASSETS_TOTAL,
) -> list[dict[str, Any]]:
    catalog_by_id = {
        str(source.get("id") or ""): source for source in catalog_sources
    }
    validated: list[dict[str, Any]] = []
    seen: set[str] = set()
    total_bytes = 0
    total_asset_bytes = 0
    total_asset_count = 0
    for index, record in enumerate(records, start=1):
        unknown_keys = set(record) - ALLOWED_RECORD_KEYS
        if unknown_keys:
            raise ImportValidationError(
                f"第 {index} 条包含不允许字段：{', '.join(sorted(unknown_keys))}"
            )
        required = {"source_id", "original_url", "content", "content_format"}
        missing = required - set(record)
        if missing:
            raise ImportValidationError(
                f"第 {index} 条缺少字段：{', '.join(sorted(missing))}"
            )
        source_id = record.get("source_id")
        original_url = record.get("original_url")
        if not isinstance(source_id, str) or not SAFE_SOURCE_ID.fullmatch(source_id):
            raise ImportValidationError(
                f"第 {index} 条 source_id 非法，禁止路径分隔符或路径穿越"
            )
        if source_id in seen:
            raise ImportValidationError(f"导出文件包含重复 source_id：{source_id}")
        seen.add(source_id)
        catalog_source = catalog_by_id.get(source_id)
        if catalog_source is None:
            raise ImportValidationError(f"source_id 未在 questions.json 登记：{source_id}")
        registered_url = catalog_source.get("url")
        if (
            not isinstance(original_url, str)
            or not isinstance(registered_url, str)
            or original_url != registered_url
        ):
            raise ImportValidationError(
                f"{source_id} 的 original_url 与 questions.json 登记值不完全一致"
            )
        title = record.get("title")
        if title is None:
            title = str(catalog_source.get("title") or source_id)
        if (
            not isinstance(title, str)
            or not title.strip()
            or len(title) > 500
            or "\n" in title
            or "\r" in title
            or CONTROL_CHARACTER_RE.search(title)
            or DANGEROUS_MARKUP_RE.search(title)
        ):
            raise ImportValidationError(f"{source_id} 的 title 无效")
        content, content_bytes = normalize_content(
            record.get("content"), record.get("content_format")
        )
        if content_bytes > max_item_bytes:
            raise ImportValidationError(
                f"{source_id} 正文 {content_bytes} 字节，超过单条上限 {max_item_bytes}"
            )
        total_bytes += content_bytes
        if total_bytes > max_total_bytes:
            raise ImportValidationError(
                f"正文合计超过总上限 {max_total_bytes} 字节"
            )
        assets, asset_bytes = validate_assets(
            record.get("assets"),
            input_root=input_root,
            max_assets=max_assets_per_record,
            max_asset_bytes=max_asset_bytes,
        )
        total_asset_bytes += asset_bytes
        total_asset_count += len(assets)
        if total_asset_bytes > max_asset_total_bytes:
            raise ImportValidationError(
                f"图片合计超过总上限 {max_asset_total_bytes} 字节"
            )
        if total_asset_count > max_assets_total:
            raise ImportValidationError(
                f"图片总数超过上限 {max_assets_total}"
            )
        validated.append(
            {
                "source_id": source_id,
                "original_url": original_url,
                "title": title.strip(),
                "content": content,
                "input_content_format": record["content_format"],
                "captured_at": normalize_captured_at(record.get("captured_at")),
                "content_bytes": content_bytes,
                "assets": assets,
                "catalog_source": catalog_source,
            }
        )
    return validated


def item_identifier(item: Mapping[str, Any]) -> str:
    for key in ("source_id", "id", "document_id", "documentId"):
        if item.get(key):
            return str(item[key])
    return ""


def load_existing_items(
    output_dir: Path,
    catalog_sources: list[Mapping[str, Any]],
    aliases: Mapping[str, list[str]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest_path = output_dir / "manifest.json"
    if not manifest_path.is_file():
        return (
            {},
            [
                empty_item(source, aliases.get(str(source.get("id")), ()))
                for source in catalog_sources
            ],
        )
    manifest = load_json(manifest_path)
    items = manifest.get("items")
    if not isinstance(items, list):
        raise ImportValidationError("现有 manifest 的 items 必须是数组")
    copied_items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            raise ImportValidationError("现有 manifest 含有非对象条目")
        identifier = item_identifier(item)
        if not identifier or identifier in seen:
            raise ImportValidationError("现有 manifest 含有空 ID 或重复 ID")
        seen.add(identifier)
        copied_items.append(dict(item))
    known = {item_identifier(item) for item in copied_items}
    for source in catalog_sources:
        source_id = str(source.get("id") or "")
        if source_id not in known:
            copied_items.append(empty_item(source, aliases.get(source_id, ())))
    return manifest, copied_items


def build_imported_item(
    record: Mapping[str, Any],
    *,
    output_dir: Path,
    aliases: Iterable[str],
    existing_item: Mapping[str, Any] | None,
) -> tuple[dict[str, Any], Path, str, list[tuple[Path, bytes]]]:
    source_id = str(record["source_id"])
    title = str(record["title"])
    original_url = str(record["original_url"])
    captured_at = str(record["captured_at"])
    notice = copyright_notice(original_url)
    input_format = str(record["input_content_format"])
    content = EXTERNAL_MARKDOWN_IMAGE_RE.sub(
        lambda match: f"[外部图片未导入：{match.group(1) or '图片'}]",
        str(record["content"]),
    )
    content = EXTERNAL_MARKDOWN_LINK_RE.sub(
        lambda match: match.group(1),
        content,
    )
    asset_metadata: list[dict[str, Any]] = []
    asset_writes: list[tuple[Path, bytes]] = []
    unreferenced: list[str] = []
    for asset in record.get("assets") or []:
        asset_id = str(asset["asset_id"])
        mime_type = str(asset["mime_type"])
        extension = SUPPORTED_IMAGE_TYPES[mime_type]
        local_path = Path("assets") / source_id / f"{asset_id}{extension}"
        local_reference = f"snapshot-asset:{asset_id}"
        default_alt = str(asset["alt_text"])
        local_markdown = f"![{markdown_alt(default_alt)}]({local_reference})"
        marker = f"{{{{asset:{asset_id}}}}}"
        referenced = marker in content
        content = content.replace(marker, local_markdown)
        asset_scheme_pattern = re.compile(
            rf"!\[([^\]]*)\]\(\s*asset://{re.escape(asset_id)}\s*\)"
        )
        if asset_scheme_pattern.search(content):
            referenced = True
            content = asset_scheme_pattern.sub(
                lambda match: (
                    f"![{markdown_alt(match.group(1) or default_alt)}]"
                    f"({local_reference})"
                ),
                content,
            )
        old_relative_pattern = re.compile(
            rf"!\[([^\]]*)\]\(\s*\.\./assets/"
            rf"{re.escape(source_id)}/{re.escape(asset_id)}"
            rf"(?:\.png|\.jpg|\.jpeg|\.webp|\.gif)\s*\)",
            re.IGNORECASE,
        )
        if old_relative_pattern.search(content):
            referenced = True
            content = old_relative_pattern.sub(
                lambda match: (
                    f"![{markdown_alt(match.group(1) or default_alt)}]"
                    f"({local_reference})"
                ),
                content,
            )
        if not referenced:
            unreferenced.append(local_markdown)
        asset_content = bytes(asset["content"])
        digest = hashlib.sha256(asset_content).hexdigest()
        asset_metadata.append(
            {
                "asset_id": asset_id,
                "original_url": asset["original_url"],
                "local_path": local_path.as_posix(),
                "mime_type": mime_type,
                "status": "downloaded",
                "content_hash": f"sha256:{digest}",
                "byte_count": len(asset_content),
                "alt_text": default_alt,
                "capture_method": "authenticated_browser_visible_asset",
                "license": None,
                "copyright_notice": copyright_notice(str(asset["original_url"])),
                "error": None,
            }
        )
        asset_writes.append((output_dir / local_path, asset_content))
    if unreferenced:
        content = (
            f"{content.rstrip()}\n\n## 本地图片\n\n"
            + "\n\n".join(unreferenced)
        )
    document = (
        f"# {title}\n\n"
        f"> {notice}\n\n"
        "> 抓取方式：用户已授权浏览器中可见文本的本地导入；"
        "未保存 Cookie、请求头或浏览器会话。\n\n"
        f"{content.rstrip()}\n"
    )
    encoded = document.encode("utf-8")
    content_hash = hashlib.sha256(encoded).hexdigest()
    local_path = Path("content") / safe_file_name(source_id)
    old_aliases_value = (
        existing_item.get("aliases", [])
        if isinstance(existing_item, Mapping)
        else []
    )
    old_aliases = (
        old_aliases_value
        if isinstance(old_aliases_value, (list, tuple, set))
        else []
    )
    merged_aliases = sorted(
        {
            str(alias)
            for alias in [*old_aliases, *aliases]
            if isinstance(alias, str) and alias
        }
    )
    catalog_source = record["catalog_source"]
    item = {
        "source_id": source_id,
        "aliases": merged_aliases,
        "title": title,
        "platform": str(catalog_source.get("platform") or ""),
        "original_url": original_url,
        "final_url": original_url,
        "local_path": local_path.as_posix(),
        "content_type": "text/markdown; charset=utf-8",
        "content_format": "markdown",
        "input_content_format": input_format,
        "capture_method": "authenticated_browser_visible_text",
        "captured_at": captured_at,
        "accessed_at": catalog_source.get("accessed_at"),
        "status": "downloaded",
        "http_status": None,
        "content_hash": f"sha256:{content_hash}",
        "char_count": len(document),
        "byte_count": len(encoded),
        "assets": asset_metadata,
        "license": (
            existing_item.get("license")
            if isinstance(existing_item, Mapping)
            else None
        ),
        "copyright_notice": notice,
        "error": None,
    }
    return item, output_dir / local_path, document, asset_writes


def write_updated_manifest(
    output_dir: Path,
    *,
    catalog_path: Path,
    existing_manifest: Mapping[str, Any],
    items: list[Mapping[str, Any]],
) -> dict[str, Any]:
    sorted_items = sorted(items, key=item_identifier)
    counts: dict[str, int] = {}
    for item in sorted_items:
        status = str(item.get("status") or "unknown")
        counts[status] = counts.get(status, 0) + 1
    manifest = dict(existing_manifest)
    policy = dict(manifest.get("policy") or {})
    policy.update(
        {
            "authenticated_import": "visible-text-only-no-session-data",
            "git_policy": "local-snapshots-must-not-be-committed",
        }
    )
    manifest.update(
        {
            "schema_version": str(manifest.get("schema_version") or "1.0"),
            "generated_at": utc_now(),
            "catalog_path": os.path.relpath(catalog_path, output_dir),
            "policy": policy,
            "statistics": {
                "total": len(sorted_items),
                "by_status": dict(sorted(counts.items())),
            },
            "items": sorted_items,
        }
    )
    atomic_write_text(
        output_dir / "manifest.json",
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
    )
    return manifest


def import_snapshots(
    *,
    input_path: Path,
    catalog_path: Path,
    output_dir: Path,
    max_item_bytes: int = DEFAULT_MAX_ITEM_BYTES,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
    max_input_bytes: int = DEFAULT_MAX_INPUT_BYTES,
    max_records: int = DEFAULT_MAX_RECORDS,
    max_asset_bytes: int = DEFAULT_MAX_ASSET_BYTES,
    max_asset_total_bytes: int = DEFAULT_MAX_ASSET_TOTAL_BYTES,
    max_assets_per_record: int = DEFAULT_MAX_ASSETS_PER_RECORD,
    max_assets_total: int = DEFAULT_MAX_ASSETS_TOTAL,
) -> dict[str, Any]:
    records = parse_records(
        input_path,
        max_input_bytes=max_input_bytes,
        max_records=max_records,
    )
    catalog = load_json(catalog_path)
    catalog_sources = catalog.get("sources")
    if not isinstance(catalog_sources, list):
        raise ImportValidationError("questions.json 缺少 sources 数组")
    validated = validate_records(
        records,
        catalog_sources,
        max_item_bytes=max_item_bytes,
        max_total_bytes=max_total_bytes,
        input_root=input_path.parent,
        max_asset_bytes=max_asset_bytes,
        max_asset_total_bytes=max_asset_total_bytes,
        max_assets_per_record=max_assets_per_record,
        max_assets_total=max_assets_total,
    )
    aliases = load_aliases(BANK_DIR, catalog_sources)
    existing_manifest, existing_items = load_existing_items(
        output_dir, catalog_sources, aliases
    )
    items_by_id = {item_identifier(item): item for item in existing_items}
    prepared: list[
        tuple[dict[str, Any], Path, str, list[tuple[Path, bytes]]]
    ] = []
    for record in validated:
        source_id = str(record["source_id"])
        prepared.append(
            build_imported_item(
                record,
                output_dir=output_dir,
                aliases=aliases.get(source_id, ()),
                existing_item=items_by_id.get(source_id),
            )
        )
    # 所有记录通过白名单、大小与路径校验后才开始写本地文件。
    resolved_output = output_dir.resolve()
    for item, target_path, document, asset_writes in prepared:
        if not target_path.resolve().is_relative_to(resolved_output):
            raise ImportValidationError("目标快照路径越界")
        for asset_path, _ in asset_writes:
            if not asset_path.resolve().is_relative_to(resolved_output):
                raise ImportValidationError("目标图片路径越界")
    for item, target_path, document, asset_writes in prepared:
        for asset_path, asset_content in asset_writes:
            atomic_write_bytes(asset_path, asset_content)
        atomic_write_text(target_path, document)
        items_by_id[str(item["source_id"])] = item
    return write_updated_manifest(
        output_dir,
        catalog_path=catalog_path,
        existing_manifest=existing_manifest,
        items=list(items_by_id.values()),
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "纯本地导入已授权浏览器导出的可见文本与图片；"
            "图片支持 base64 或导出目录内相对 file_path，"
            "不连接浏览器、不读取会话且不发起网络请求"
        )
    )
    parser.add_argument("--input", type=Path, required=True, help="JSON/NDJSON 导出文件")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--max-item-bytes", type=int, default=DEFAULT_MAX_ITEM_BYTES)
    parser.add_argument("--max-total-bytes", type=int, default=DEFAULT_MAX_TOTAL_BYTES)
    parser.add_argument("--max-input-bytes", type=int, default=DEFAULT_MAX_INPUT_BYTES)
    parser.add_argument("--max-records", type=int, default=DEFAULT_MAX_RECORDS)
    parser.add_argument("--max-asset-bytes", type=int, default=DEFAULT_MAX_ASSET_BYTES)
    parser.add_argument(
        "--max-asset-total-bytes",
        type=int,
        default=DEFAULT_MAX_ASSET_TOTAL_BYTES,
    )
    parser.add_argument(
        "--max-assets-per-record",
        type=int,
        default=DEFAULT_MAX_ASSETS_PER_RECORD,
    )
    parser.add_argument(
        "--max-assets-total", type=int, default=DEFAULT_MAX_ASSETS_TOTAL
    )
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    limits = {
        "max-item-bytes": args.max_item_bytes,
        "max-total-bytes": args.max_total_bytes,
        "max-input-bytes": args.max_input_bytes,
        "max-records": args.max_records,
        "max-asset-bytes": args.max_asset_bytes,
        "max-asset-total-bytes": args.max_asset_total_bytes,
        "max-assets-per-record": args.max_assets_per_record,
        "max-assets-total": args.max_assets_total,
    }
    invalid = [name for name, value in limits.items() if value <= 0]
    if invalid:
        raise SystemExit(f"限制参数必须大于 0：{', '.join(invalid)}")
    try:
        manifest = import_snapshots(
            input_path=args.input.resolve(),
            catalog_path=args.catalog.resolve(),
            output_dir=args.output.resolve(),
            max_item_bytes=args.max_item_bytes,
            max_total_bytes=args.max_total_bytes,
            max_input_bytes=args.max_input_bytes,
            max_records=args.max_records,
            max_asset_bytes=args.max_asset_bytes,
            max_asset_total_bytes=args.max_asset_total_bytes,
            max_assets_per_record=args.max_assets_per_record,
            max_assets_total=args.max_assets_total,
        )
    except (ImportValidationError, OSError, json.JSONDecodeError) as exc:
        print(f"导入失败：{exc}", file=sys.stderr)
        return 2
    imported = sum(
        item.get("capture_method") == "authenticated_browser_visible_text"
        for item in manifest["items"]
    )
    print(
        json.dumps(
            {
                "manifest": str((args.output / "manifest.json").resolve()),
                "authenticated_browser_snapshots": imported,
                "statistics": manifest["statistics"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(run())
