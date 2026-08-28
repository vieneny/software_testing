"""Safe read-only access to locally downloaded public-source snapshots."""

from __future__ import annotations

import hashlib
import json
import posixpath
import re
from pathlib import Path
from threading import RLock
from typing import Any, Iterable


MAX_SNAPSHOT_BYTES = 8 * 1024 * 1024
MAX_ASSET_BYTES = 8 * 1024 * 1024
ALLOWED_SUFFIXES = {".html", ".htm", ".md", ".markdown", ".txt"}
ALLOWED_ASSET_TYPES = {
    "image/avif": {".avif"},
    "image/gif": {".gif"},
    "image/jpeg": {".jpeg", ".jpg"},
    "image/png": {".png"},
    "image/webp": {".webp"},
}
SAFE_ASSET_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,159}$")
DEFAULT_COPYRIGHT_NOTICE = (
    "本地快照仅用于个人学习、题目核验与离线阅读；"
    "版权归原作者或原发布机构所有，请勿重新分发。"
)


class SourceSnapshotError(RuntimeError):
    """Base error raised by the local snapshot repository."""


class SourceSnapshotUnavailable(SourceSnapshotError):
    """Raised when a snapshot record exists but its content is unavailable."""

    def __init__(self, message: str, *, status: str = "unavailable") -> None:
        super().__init__(message)
        self.status = status


class SourceSnapshotIntegrityError(SourceSnapshotError):
    """Raised when a local snapshot fails validation."""


class SourceSnapshotAssetNotFound(SourceSnapshotError):
    """Raised when an asset is not registered for a snapshot."""


def _first_text(item: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _normalized_status(value: str, has_path: bool) -> str:
    normalized = value.strip().casefold()
    if normalized in {"available", "ready", "success", "ok", "downloaded", "captured"}:
        return "available"
    if normalized:
        # Keep crawler failure states (for example robots_denied, rate_limited
        # and access_limited) intact so the API and UI can explain why a
        # source is not available instead of collapsing every failure to
        # "missing".
        return normalized
    return "available" if has_path else "missing"


def _content_format(item: dict[str, Any], relative_path: str) -> str:
    declared = _first_text(item, "content_format", "format").casefold()
    aliases = {
        "md": "markdown",
        "markdown": "markdown",
        "html": "html",
        "htm": "html",
        "txt": "text",
        "text": "text",
        "plain": "text",
        "text/plain": "text",
        "text/html": "html",
        "text/markdown": "markdown",
    }
    if declared in aliases:
        return aliases[declared]
    suffix = Path(relative_path).suffix.casefold()
    if suffix in {".html", ".htm"}:
        return "html"
    if suffix in {".md", ".markdown"}:
        return "markdown"
    return "text"


def _optional_dimension(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        return None
    return value


class SourceSnapshotRepository:
    """Repository over ``source-snapshots/manifest.json``.

    Snapshot paths are always resolved relative to the manifest directory.
    The resolved target must remain under that directory, including after
    resolving symlinks.
    """

    def __init__(self, manifest_path: Path | None) -> None:
        self._lock = RLock()
        self.manifest_path = manifest_path.resolve() if manifest_path else None
        self.root = self.manifest_path.parent if self.manifest_path else None
        self._manifest_signature: tuple[int, int, int] | None | object = object()
        self.manifest_status = "not_configured" if manifest_path is None else "missing"
        self.manifest_error: str | None = None
        self.schema_version: str | None = None
        self.generated_at: str | None = None
        self.items: list[dict[str, Any]] = []
        self._by_key: dict[str, dict[str, Any]] = {}
        self._by_url: dict[str, dict[str, Any]] = {}
        if self.manifest_path is not None:
            self._load()

    def _current_signature(self) -> tuple[int, int, int] | None:
        if self.manifest_path is None:
            return None
        try:
            stat = self.manifest_path.stat()
        except FileNotFoundError:
            return None
        return (stat.st_mtime_ns, stat.st_size, stat.st_ino)

    def refresh_if_changed(self) -> None:
        """Reload an atomically replaced or modified manifest on demand."""

        if self.manifest_path is None:
            return
        signature = self._current_signature()
        with self._lock:
            if signature != self._manifest_signature:
                self._load()

    def _clear_loaded_data(self) -> None:
        self.manifest_error = None
        self.schema_version = None
        self.generated_at = None
        self.items = []
        self._by_key = {}
        self._by_url = {}

    def _load(self) -> None:
        assert self.manifest_path is not None
        with self._lock:
            signature = self._current_signature()
            self._clear_loaded_data()
            try:
                payload = json.loads(self.manifest_path.read_text(encoding="utf-8"))
                if not isinstance(payload, dict):
                    raise ValueError("manifest 顶层必须是对象")
                raw_items = (
                    payload.get("items")
                    or payload.get("snapshots")
                    or payload.get("sources")
                    or []
                )
                if not isinstance(raw_items, list):
                    raise ValueError("manifest 的 items/snapshots/sources 必须是数组")
                normalized = [
                    self._normalize_item(raw, index)
                    for index, raw in enumerate(raw_items, start=1)
                ]
                self._build_indexes(normalized)
            except FileNotFoundError:
                self.manifest_status = "missing"
            except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
                self.manifest_status = "invalid"
                self.manifest_error = str(exc)
            else:
                self.schema_version = (
                    str(payload.get("schema_version") or "") or None
                )
                self.generated_at = (
                    _first_text(payload, "generated_at", "captured_at") or None
                )
                self.items = normalized
                self.manifest_status = "ready"
            finally:
                # A concurrent atomic replacement gets a different signature
                # and is picked up on the next request.
                self._manifest_signature = signature

    def _normalize_item(self, raw: Any, index: int) -> dict[str, Any]:
        if not isinstance(raw, dict):
            raise ValueError(f"manifest items[{index}] 必须是对象")
        source_id = _first_text(raw, "source_id", "id", "document_id", "documentId")
        if not source_id:
            raise ValueError(f"manifest items[{index}] 缺少 source_id")
        if len(source_id) > 240 or any(char in source_id for char in "/\\\n\r\t"):
            raise ValueError(f"manifest items[{index}] 的 source_id 非法")

        relative_path = _first_text(raw, "local_path", "path", "file")
        aliases = _string_list(raw.get("aliases"))
        aliases.extend(
            value
            for value in (
                _first_text(raw, "document_id"),
                _first_text(raw, "documentId"),
            )
            if value and value != source_id
        )
        original_url = _first_text(
            raw, "original_url", "source_url", "canonical_url", "url"
        )
        status = _normalized_status(_first_text(raw, "status"), bool(relative_path))
        raw_assets = raw.get("assets") or []
        if not isinstance(raw_assets, list):
            raise ValueError(f"manifest items[{index}].assets 必须是数组")
        assets = [
            self._normalize_asset(asset, item_index=index, asset_index=asset_index)
            for asset_index, asset in enumerate(raw_assets, start=1)
        ]
        asset_ids = [asset["asset_id"].casefold() for asset in assets]
        if len(asset_ids) != len(set(asset_ids)):
            raise ValueError(f"manifest items[{index}].assets 含重复 asset_id")
        return {
            "source_id": source_id,
            "title": _first_text(raw, "title", "source_title") or source_id,
            "platform": _first_text(raw, "platform") or "公开来源",
            "original_url": original_url or None,
            "captured_at": _first_text(
                raw, "captured_at", "downloaded_at", "accessed_at"
            )
            or None,
            "status": status,
            "content_format": _content_format(raw, relative_path),
            "capture_method": _first_text(raw, "capture_method") or None,
            "content_hash": _first_text(raw, "content_hash", "sha256") or None,
            "local_path": relative_path or None,
            "char_count": raw.get("char_count"),
            "copyright_notice": _first_text(raw, "copyright_notice")
            or DEFAULT_COPYRIGHT_NOTICE,
            "aliases": list(dict.fromkeys(aliases)),
            "error": _first_text(raw, "error", "message") or None,
            "assets": assets,
            "_assets_by_id": {
                asset["asset_id"].casefold(): asset for asset in assets
            },
        }

    def _normalize_asset(
        self, raw: Any, *, item_index: int, asset_index: int
    ) -> dict[str, Any]:
        label = f"manifest items[{item_index}].assets[{asset_index}]"
        if not isinstance(raw, dict):
            raise ValueError(f"{label} 必须是对象")
        asset_id = _first_text(raw, "asset_id", "id")
        if not SAFE_ASSET_ID.fullmatch(asset_id):
            raise ValueError(f"{label} 的 asset_id 非法")
        content_type = _first_text(raw, "content_type", "mime_type").casefold()
        if ";" in content_type:
            content_type = content_type.split(";", 1)[0].strip()
        byte_count = raw.get("byte_count")
        if (
            isinstance(byte_count, bool)
            or not isinstance(byte_count, int)
            or byte_count < 0
        ):
            byte_count = None
        relative_path = _first_text(raw, "local_path", "path", "file")
        status = _normalized_status(
            _first_text(raw, "status"), bool(relative_path)
        )
        return {
            "asset_id": asset_id,
            "local_path": relative_path or None,
            "content_type": content_type or None,
            "content_hash": _first_text(raw, "content_hash", "sha256") or None,
            "byte_count": byte_count,
            "alt": _first_text(raw, "alt", "alt_text") or None,
            "caption": _first_text(raw, "caption", "title") or None,
            "width": _optional_dimension(raw.get("width")),
            "height": _optional_dimension(raw.get("height")),
            "original_url": _first_text(
                raw, "original_url", "source_url", "url"
            )
            or None,
            "status": status,
            "capture_method": _first_text(raw, "capture_method") or None,
            "error": _first_text(raw, "error", "message") or None,
        }

    def _build_indexes(self, items: Iterable[dict[str, Any]]) -> None:
        by_key: dict[str, dict[str, Any]] = {}
        by_url: dict[str, dict[str, Any]] = {}
        for item in items:
            for key in [item["source_id"], *item["aliases"]]:
                normalized = key.casefold()
                existing = by_key.get(normalized)
                if existing is not None and existing["source_id"] != item["source_id"]:
                    raise ValueError(f"manifest 别名重复：{key}")
                by_key[normalized] = item
            if item["original_url"]:
                normalized_url = item["original_url"].rstrip("/")
                existing = by_url.get(normalized_url)
                if existing is not None and existing["source_id"] != item["source_id"]:
                    raise ValueError(f"manifest 原始 URL 重复：{item['original_url']}")
                by_url[normalized_url] = item
        self._by_key = by_key
        self._by_url = by_url

    def summary(self) -> dict[str, Any]:
        self.refresh_if_changed()
        with self._lock:
            return {
                "status": self.manifest_status,
                "schema_version": self.schema_version,
                "generated_at": self.generated_at,
                "total": len(self.items),
                "available": sum(
                    item["status"] == "available" for item in self.items
                ),
                "unavailable": sum(
                    item["status"] != "available" for item in self.items
                ),
                "error": self.manifest_error,
            }

    def list_items(self) -> list[dict[str, Any]]:
        self.refresh_if_changed()
        with self._lock:
            return [self.metadata(item) for item in self.items]

    def find(
        self, source_id_or_alias: str, *, original_url: str | None = None
    ) -> dict[str, Any] | None:
        self.refresh_if_changed()
        with self._lock:
            item = self._by_key.get(source_id_or_alias.casefold())
            if item is not None:
                return item
            if original_url:
                return self._by_url.get(original_url.rstrip("/"))
            return None

    def metadata(self, item: dict[str, Any]) -> dict[str, Any]:
        return {
            key: item.get(key)
            for key in (
                "source_id",
                "title",
                "platform",
                "original_url",
                "captured_at",
                "status",
                "content_format",
                "capture_method",
                "content_hash",
                "local_path",
                "char_count",
                "copyright_notice",
                "aliases",
                "error",
                "assets",
            )
        }

    def find_asset(
        self, item: dict[str, Any], asset_id: str
    ) -> dict[str, Any] | None:
        return item.get("_assets_by_id", {}).get(asset_id.casefold())

    def read(self, item: dict[str, Any]) -> dict[str, Any]:
        status = item["status"]
        if status != "available":
            message = item.get("error") or f"本地来源快照状态为 {status}"
            raise SourceSnapshotUnavailable(message, status=status)

        relative_path = item.get("local_path")
        if not relative_path or self.root is None:
            raise SourceSnapshotUnavailable("本地来源快照未记录文件路径", status="missing")
        path_value = Path(relative_path)
        if path_value.is_absolute() or path_value.suffix.casefold() not in ALLOWED_SUFFIXES:
            raise SourceSnapshotIntegrityError("本地来源快照路径或文件类型不受支持")

        target = (self.root / path_value).resolve()
        try:
            target.relative_to(self.root)
        except ValueError as exc:
            raise SourceSnapshotIntegrityError("本地来源快照路径越出允许目录") from exc
        if not target.is_file():
            raise SourceSnapshotUnavailable("本地来源快照文件不存在", status="missing")

        size = target.stat().st_size
        if size > MAX_SNAPSHOT_BYTES:
            raise SourceSnapshotIntegrityError(
                f"本地来源快照超过 {MAX_SNAPSHOT_BYTES} 字节读取上限"
            )
        try:
            raw = target.read_bytes()
            content = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise SourceSnapshotIntegrityError(
                "本地来源快照必须是 UTF-8 文本"
            ) from exc
        digest = hashlib.sha256(raw).hexdigest()
        expected = (item.get("content_hash") or "").casefold()
        if expected.startswith("sha256:"):
            expected = expected.removeprefix("sha256:")
        if expected and expected != digest:
            raise SourceSnapshotIntegrityError("本地来源快照哈希校验失败")
        content = self._rewrite_registered_asset_references(content, item)

        return {
            **self.metadata(item),
            "status": "available",
            "content": content,
            "content_hash": f"sha256:{digest}",
            "char_count": len(content),
        }

    def _rewrite_registered_asset_references(
        self, content: str, item: dict[str, Any]
    ) -> str:
        """Bridge legacy local Markdown paths to the safe API asset scheme.

        Only an exact image destination calculated from a manifest-registered
        asset is rewritten. Ordinary links, unregistered paths and examples
        inside fenced code blocks are left untouched.
        """

        source_path = item.get("local_path")
        if not source_path:
            return content
        source_parent = posixpath.dirname(str(source_path)) or "."
        replacements: list[tuple[re.Pattern[str], str]] = []
        for asset in item.get("assets", []):
            if asset.get("status") != "available" or not asset.get("local_path"):
                continue
            relative_target = posixpath.relpath(
                str(asset["local_path"]), start=source_parent
            )
            pattern = re.compile(
                r"(!\[[^\]\r\n]*\]\(\s*)"
                + re.escape(relative_target)
                + r"(\s*\))"
            )
            replacements.append(
                (pattern, rf"\1snapshot-asset:{asset['asset_id']}\2")
            )
        if not replacements:
            return content

        rendered: list[str] = []
        fence_marker: str | None = None
        for line in content.splitlines(keepends=True):
            stripped = line.lstrip()
            if fence_marker is None and (
                stripped.startswith("```") or stripped.startswith("~~~")
            ):
                fence_marker = stripped[:3]
                rendered.append(line)
                continue
            if fence_marker is not None:
                rendered.append(line)
                if stripped.startswith(fence_marker):
                    fence_marker = None
                continue
            for pattern, replacement in replacements:
                line = pattern.sub(replacement, line)
            rendered.append(line)
        return "".join(rendered)

    def read_asset(
        self, item: dict[str, Any], asset_id: str
    ) -> tuple[bytes, dict[str, Any]]:
        asset = self.find_asset(item, asset_id)
        if asset is None:
            raise SourceSnapshotAssetNotFound("该来源未登记此本地图片")
        if asset.get("status") != "available":
            status = str(asset.get("status") or "unavailable")
            message = asset.get("error") or f"本地来源图片状态为 {status}"
            raise SourceSnapshotUnavailable(message, status=status)

        content_type = asset.get("content_type")
        allowed_suffixes = ALLOWED_ASSET_TYPES.get(content_type)
        if allowed_suffixes is None:
            raise SourceSnapshotIntegrityError("本地来源图片 MIME 类型不受支持")

        relative_path = asset.get("local_path")
        if not relative_path or self.root is None:
            raise SourceSnapshotIntegrityError("本地来源图片未记录文件路径")
        path_value = Path(relative_path)
        if path_value.is_absolute() or path_value.suffix.casefold() not in allowed_suffixes:
            raise SourceSnapshotIntegrityError(
                "本地来源图片路径后缀与 MIME 类型不匹配"
            )
        target = (self.root / path_value).resolve()
        try:
            target.relative_to(self.root)
        except ValueError as exc:
            raise SourceSnapshotIntegrityError(
                "本地来源图片路径越出允许目录"
            ) from exc
        if not target.is_file():
            raise SourceSnapshotUnavailable("本地来源图片文件不存在", status="missing")

        declared_size = asset.get("byte_count")
        if declared_size is None:
            raise SourceSnapshotIntegrityError("本地来源图片未记录 byte_count")
        if declared_size > MAX_ASSET_BYTES:
            raise SourceSnapshotIntegrityError(
                f"本地来源图片超过 {MAX_ASSET_BYTES} 字节读取上限"
            )
        actual_size = target.stat().st_size
        if actual_size > MAX_ASSET_BYTES:
            raise SourceSnapshotIntegrityError(
                f"本地来源图片超过 {MAX_ASSET_BYTES} 字节读取上限"
            )
        if actual_size != declared_size:
            raise SourceSnapshotIntegrityError("本地来源图片 byte_count 校验失败")

        raw = target.read_bytes()
        if len(raw) > MAX_ASSET_BYTES or len(raw) != declared_size:
            raise SourceSnapshotIntegrityError("本地来源图片大小校验失败")
        expected = (asset.get("content_hash") or "").casefold()
        if expected.startswith("sha256:"):
            expected = expected.removeprefix("sha256:")
        if not expected:
            raise SourceSnapshotIntegrityError("本地来源图片未记录 SHA-256")
        digest = hashlib.sha256(raw).hexdigest()
        if digest != expected:
            raise SourceSnapshotIntegrityError("本地来源图片哈希校验失败")
        return raw, {
            **asset,
            "content_hash": f"sha256:{digest}",
            "byte_count": len(raw),
        }
