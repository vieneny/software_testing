#!/usr/bin/env python3
"""将题库中的公开来源保存为仅供本机学习的安全文本快照。

设计边界：

* 只读取 ``questions.json`` 已登记的 http/https 公共 URL；
* 不发送 Cookie、Authorization，不读取浏览器会话，也不处理登录或验证码；
* 每次请求前校验公网地址，并在跨域重定向后重新校验 robots.txt；
* 尊重 robots.txt、超时、按主机限速、有限重试与响应大小限制；
* HTML 仅转换为无脚本、无外链的 Markdown 文本，不保存原始页面；
* 完整快照是本地运行数据，必须被 Git 忽略。
"""

from __future__ import annotations

import argparse
import hashlib
import html
import ipaddress
import json
import os
import re
import socket
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from email.message import Message
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import (
    HTTPRedirectHandler,
    ProxyHandler,
    Request,
    build_opener,
)
from urllib.robotparser import RobotFileParser


SCRIPT_DIR = Path(__file__).resolve().parent
BANK_DIR = SCRIPT_DIR.parent
DEFAULT_CATALOG = BANK_DIR / "data" / "questions.json"
DEFAULT_OUTPUT = BANK_DIR / "data" / "source-snapshots"
DEFAULT_USER_AGENT = (
    "SoftwareTestingStudySnapshot/1.0 "
    "(public learning archive; +https://gitee.com/a251376784/software_testing)"
)
ROBOT_USER_AGENT = "SoftwareTestingStudySnapshot"
SUPPORTED_TEXT_TYPES = {
    "application/json",
    "application/ld+json",
    "application/xhtml+xml",
    "application/xml",
    "text/html",
    "text/markdown",
    "text/plain",
    "text/xml",
}
SUPPORTED_IMAGE_TYPES = {
    "image/gif": ".gif",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
TRANSIENT_STATUS = {408, 425, 429, 500, 502, 503, 504}
REDIRECT_STATUS = {301, 302, 303, 307, 308}
RETRY_ON_NEXT_RUN_STATUS = {
    "dns_error",
    "network_error",
    "not_requested",
    "pending",
    "processing_error",
    "robots_unavailable",
}
SAFE_SOURCE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,159}$")
SPACE_RE = re.compile(r"[ \t\f\v]+")
BLANK_LINES_RE = re.compile(r"\n{3,}")
LIMITED_PAGE_RE = re.compile(
    r"(请先登录|登录后查看|人机验证|安全验证|(?:完成|输入).{0,8}验证码|"
    r"captcha|verify you are human|"
    r"attention required|just a moment|access denied)",
    re.IGNORECASE,
)


class SnapshotError(RuntimeError):
    """可映射为清单状态的抓取错误。"""

    def __init__(self, status: str, message: str, *, http_status: int | None = None):
        super().__init__(message)
        self.status = status
        self.http_status = http_status


class NoRedirectHandler(HTTPRedirectHandler):
    """禁止 urllib 自动跟随重定向，确保每个目标都重新做安全与 robots 校验。"""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


@dataclass(frozen=True)
class FetchResponse:
    url: str
    status: int
    headers: Mapping[str, str]
    body: bytes


@dataclass(frozen=True)
class RobotsPolicy:
    allowed: bool
    status: str
    delay_seconds: float
    detail: str | None = None


@dataclass(frozen=True)
class RobotsRules:
    parser: RobotFileParser | None
    default_allowed: bool
    status: str
    delay_seconds: float
    detail: str | None = None


@dataclass(frozen=True)
class ImageCandidate:
    marker: str
    original_url: str
    alt_text: str


VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}
ARTICLE_CLASS_NAMES = (
    "theme-default-content",
    "vp-doc",
    "theme-reco-content",
    "markdown-body",
    "article-content",
    "post-content",
    "entry-content",
    "doc-content",
    "main-content",
)
CHROME_TOKEN_RE = re.compile(
    r"(?:^|[\s_-])(?:"
    r"ad|ads|advert|advertisement|banner|breadcrumb|comments?|contributors?|"
    r"edit-link|footer|header|last-updated|navbar|navigation|page-edit|page-nav|"
    r"pagination|sidebar|social-share|sponsor|table-of-contents|toc"
    r")(?:$|[\s_-])",
    re.IGNORECASE,
)


def selector_matches(
    tag: str,
    attrs: list[tuple[str, str | None]],
    selector_kind: str,
    selector_value: str,
) -> bool:
    attr_map = {key.lower(): str(value or "") for key, value in attrs}
    if selector_kind == "tag":
        return tag == selector_value
    if selector_kind == "class":
        return selector_value in attr_map.get("class", "").split()
    if selector_kind == "id":
        return attr_map.get("id") == selector_value
    if selector_kind == "role":
        return attr_map.get("role", "").lower() == selector_value
    return False


class HTMLContainerExtractor(HTMLParser):
    """提取匹配容器的内部 HTML；用于先选正文、再做 Markdown 转换。"""

    def __init__(self, selector_kind: str, selector_value: str) -> None:
        super().__init__(convert_charrefs=False)
        self.selector_kind = selector_kind
        self.selector_value = selector_value
        self.depth = 0
        self.parts: list[str] = []
        self.fragments: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        tag = tag.lower()
        if self.depth:
            self.parts.append(self.get_starttag_text() or f"<{tag}>")
            if tag not in VOID_TAGS:
                self.depth += 1
            return
        if selector_matches(
            tag, attrs, self.selector_kind, self.selector_value
        ):
            self.depth = 1
            self.parts = []

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        if self.depth:
            self.parts.append(self.get_starttag_text() or f"<{tag}/>")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if not self.depth or tag in VOID_TAGS:
            return
        if self.depth > 1:
            self.parts.append(f"</{tag}>")
        self.depth -= 1
        if self.depth == 0:
            self.fragments.append("".join(self.parts))
            self.parts = []

    def handle_data(self, data: str) -> None:
        if self.depth:
            self.parts.append(html.escape(data, quote=False))

    def handle_entityref(self, name: str) -> None:
        if self.depth:
            self.parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if self.depth:
            self.parts.append(f"&#{name};")

    def close(self) -> None:
        super().close()
        if self.depth and self.parts:
            self.fragments.append("".join(self.parts))
            self.parts = []
            self.depth = 0


class DocumentTitleExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_title = False
        self.parts: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        if tag.lower() == "title":
            self.in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.parts.append(data)

    @property
    def title(self) -> str:
        return clean_heading_text("".join(self.parts))


class HostRateLimiter:
    """按主机串行限速；测试可注入单调时钟与 sleep。"""

    def __init__(
        self,
        *,
        monotonic: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._monotonic = monotonic
        self._sleep = sleep
        self._last_request: dict[str, float] = {}

    def wait(self, host: str, delay_seconds: float) -> None:
        now = self._monotonic()
        previous = self._last_request.get(host)
        if previous is not None:
            remaining = delay_seconds - (now - previous)
            if remaining > 0:
                self._sleep(remaining)
                now = self._monotonic()
        self._last_request[host] = now


class MarkdownExtractor(HTMLParser):
    """把常见正文结构转换为无脚本、无外链的 Markdown 文本。"""

    SKIP_TAGS = {
        "aside",
        "button",
        "footer",
        "header",
        "nav",
        "script",
        "style",
        "noscript",
        "svg",
        "canvas",
        "iframe",
        "object",
        "embed",
        "form",
        "template",
    }
    BLOCK_TAGS = {
        "article",
        "aside",
        "blockquote",
        "dd",
        "div",
        "dl",
        "dt",
        "figcaption",
        "figure",
        "footer",
        "header",
        "main",
        "nav",
        "p",
        "section",
        "table",
        "tbody",
        "td",
        "tfoot",
        "th",
        "thead",
        "tr",
        "ul",
        "ol",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.title_parts: list[str] = []
        self.skip_stack: list[str] = []
        self.in_title = False
        self.in_pre = False
        self.in_code = False
        self.list_depth = 0
        self.image_candidates: list[ImageCandidate] = []
        self.picture_sources: list[list[str]] = []
        self.heading_level: int | None = None
        self.heading_parts: list[str] = []

    def _append(self, value: str) -> None:
        if value:
            self.parts.append(value)

    def _newline(self, count: int = 1) -> None:
        self._append("\n" * count)

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        tag = tag.lower()
        if self.skip_stack:
            if tag not in VOID_TAGS:
                self.skip_stack.append(tag)
            return
        attr_map = {key.lower(): value for key, value in attrs}
        chrome_identity = " ".join(
            str(attr_map.get(key) or "") for key in ("class", "id")
        ).lower()
        role = str(attr_map.get("role") or "").lower()
        style = str(attr_map.get("style") or "").replace(" ", "").lower()
        if (
            tag in self.SKIP_TAGS
            or "hidden" in attr_map
            or str(attr_map.get("aria-hidden") or "").lower() == "true"
            or role in {"banner", "complementary", "contentinfo", "navigation"}
            or CHROME_TOKEN_RE.search(chrome_identity)
            or "display:none" in style
            or "visibility:hidden" in style
        ):
            if tag not in VOID_TAGS:
                self.skip_stack.append(tag)
            return
        if tag == "title":
            self.in_title = True
        elif tag in {f"h{level}" for level in range(1, 7)}:
            self._newline(2)
            self.heading_level = int(tag[1])
            self.heading_parts = []
        elif self.heading_level is not None:
            return
        elif tag == "br":
            self._newline()
        elif tag == "li":
            self._newline()
            self._append("  " * max(0, self.list_depth - 1) + "- ")
        elif tag in {"ul", "ol"}:
            self.list_depth += 1
            self._newline()
        elif tag == "pre":
            self.in_pre = True
            self._newline(2)
            self._append("```\n")
        elif tag == "code" and not self.in_pre:
            self.in_code = True
            self._append("`")
        elif tag == "blockquote":
            self._newline(2)
            self._append("> ")
        elif tag == "picture":
            self.picture_sources.append([])
        elif tag == "source" and self.picture_sources:
            source_url = srcset_url(attr_map.get("srcset") or attr_map.get("src"))
            if source_url:
                self.picture_sources[-1].append(source_url)
        elif tag == "img":
            alt = attr_map.get("alt")
            image_url = (
                self.picture_sources[-1][-1]
                if self.picture_sources and self.picture_sources[-1]
                else srcset_url(
                    attr_map.get("srcset")
                    or attr_map.get("src")
                    or attr_map.get("data-src")
                )
            )
            safe_alt = SPACE_RE.sub(" ", str(alt or "图片")).strip()[:500] or "图片"
            if image_url:
                marker = f"@@LOCAL_ASSET_{len(self.image_candidates) + 1:04d}@@"
                self.image_candidates.append(
                    ImageCandidate(marker, image_url, safe_alt)
                )
                self._append(marker)
            else:
                self._append(f"[图片：{safe_alt}]")
        elif tag in self.BLOCK_TAGS:
            self._newline(2 if tag in {"article", "main", "section"} else 1)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self.skip_stack:
            if tag in self.skip_stack:
                reverse_index = self.skip_stack[::-1].index(tag)
                del self.skip_stack[len(self.skip_stack) - reverse_index - 1 :]
            return
        if tag == "title":
            self.in_title = False
        elif (
            self.heading_level is not None
            and tag == f"h{self.heading_level}"
        ):
            heading = clean_heading_text("".join(self.heading_parts))
            if heading:
                self._append("#" * self.heading_level + " " + heading)
            self.heading_level = None
            self.heading_parts = []
            self._newline()
        elif tag in {"ul", "ol"}:
            self.list_depth = max(0, self.list_depth - 1)
            self._newline()
        elif tag == "pre":
            self.in_pre = False
            self._append("\n```\n")
        elif tag == "code" and not self.in_pre and self.in_code:
            self.in_code = False
            self._append("`")
        elif tag == "picture":
            if self.picture_sources:
                self.picture_sources.pop()
        elif tag in self.BLOCK_TAGS or tag.startswith("h"):
            self._newline(2 if tag in {"article", "main", "section"} else 1)

    def handle_data(self, data: str) -> None:
        if self.skip_stack:
            return
        if self.in_title:
            self.title_parts.append(data)
        if self.heading_level is not None:
            normalized_heading = SPACE_RE.sub(
                " ", data.replace("\r", " ").replace("\n", " ")
            )
            if normalized_heading.strip():
                self.heading_parts.append(normalized_heading)
            return
        if self.in_pre:
            self._append(data.replace("\r\n", "\n").replace("\r", "\n"))
            return
        normalized = SPACE_RE.sub(" ", data.replace("\r", " ").replace("\n", " "))
        if normalized.strip():
            self._append(normalized)

    @property
    def title(self) -> str:
        return clean_heading_text("".join(self.title_parts))

    def markdown(self) -> str:
        raw = html.unescape("".join(self.parts))
        lines: list[str] = []
        in_fence = False
        for line in raw.replace("\r\n", "\n").replace("\r", "\n").splitlines():
            if line.strip().startswith("```"):
                in_fence = not in_fence
                lines.append(line.strip())
            elif in_fence:
                lines.append(line.rstrip())
            else:
                normalized = SPACE_RE.sub(" ", line).strip()
                heading = re.match(r"^(#{1,6})\s*(.*)$", normalized)
                if heading:
                    heading_text = clean_heading_text(heading.group(2))
                    normalized = (
                        f"{heading.group(1)} {heading_text}"
                        if heading_text
                        else ""
                    )
                lines.append(normalized)
        return BLANK_LINES_RE.sub("\n\n", "\n".join(lines)).strip()


def clean_heading_text(value: str) -> str:
    text = html.unescape(value).replace("\u200b", "").replace("\ufeff", "")
    text = SPACE_RE.sub(" ", text.replace("\r", " ").replace("\n", " ")).strip()
    return re.sub(r"^(?:#{1,6}\s*)+", "", text).strip()


def markdown_visible_score(content: str) -> int:
    without_markers = re.sub(r"@@LOCAL_ASSET_\d+@@", "", content)
    without_syntax = re.sub(r"[#>*_`\-\[\]()|]", "", without_markers)
    return len(re.sub(r"\s+", "", without_syntax))


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def srcset_url(value: str | None) -> str:
    """选择 srcset 中最后一个候选（通常为最高密度），不解析或下载 data URL。"""

    if not value:
        return ""
    candidates = [part.strip().split()[0] for part in value.split(",") if part.strip()]
    return candidates[-1] if candidates else ""


def markdown_alt(value: str) -> str:
    return value.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")


def normalize_url(url: str) -> str:
    parsed = urlsplit(url.strip())
    scheme = parsed.scheme.lower()
    host = (parsed.hostname or "").lower().rstrip(".")
    if not scheme or not host:
        return url
    port = parsed.port
    default_port = (scheme == "http" and port == 80) or (
        scheme == "https" and port == 443
    )
    authority = host if port is None or default_port else f"{host}:{port}"
    path = parsed.path or "/"
    if path != "/":
        path = path.rstrip("/")
    return urlunsplit((scheme, authority, path, parsed.query, ""))


def redirect_key(url: str) -> str:
    """重定向去重保留尾斜杠，避免把合法的 /path -> /path/ 误判为循环。"""

    parsed = urlsplit(url.strip())
    return urlunsplit(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path or "/",
            parsed.query,
            "",
        )
    )


def validate_public_url(
    url: str,
    *,
    resolver: Callable[..., list[tuple[Any, ...]]] = socket.getaddrinfo,
) -> None:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        raise SnapshotError("blocked_url", "只允许 http/https URL")
    if not parsed.hostname or parsed.username or parsed.password:
        raise SnapshotError("blocked_url", "URL 主机无效或包含用户凭据")
    host = parsed.hostname.rstrip(".").lower()
    if host == "localhost" or host.endswith(".localhost") or host.endswith(".local"):
        raise SnapshotError("blocked_url", "拒绝访问本机或局域网主机")
    try:
        literal = ipaddress.ip_address(host)
        addresses = [literal]
    except ValueError:
        try:
            resolved = resolver(host, parsed.port or 443, type=socket.SOCK_STREAM)
        except OSError as exc:
            raise SnapshotError("dns_error", f"DNS 解析失败：{exc}") from exc
        addresses = []
        for entry in resolved:
            try:
                addresses.append(ipaddress.ip_address(entry[4][0]))
            except (IndexError, ValueError):
                continue
        if not addresses:
            raise SnapshotError("dns_error", "DNS 未返回可验证地址")
    for address in addresses:
        if (
            address.is_private
            or address.is_loopback
            or address.is_link_local
            or address.is_multicast
            or address.is_reserved
            or address.is_unspecified
        ):
            raise SnapshotError("blocked_url", f"拒绝访问非公网地址：{address}")


def parse_content_type(headers: Mapping[str, str]) -> tuple[str, str]:
    raw = headers.get("Content-Type") or headers.get("content-type") or ""
    if not raw.strip():
        return "", "utf-8"
    message = Message()
    message["content-type"] = raw
    media_type = message.get_content_type().lower()
    charset = message.get_content_charset() or "utf-8"
    return media_type, charset


def decode_body(body: bytes, charset: str) -> str:
    candidates = [charset, "utf-8", "gb18030"]
    for candidate in candidates:
        try:
            return body.decode(candidate)
        except (LookupError, UnicodeDecodeError):
            continue
    return body.decode("utf-8", errors="replace")


def convert_to_markdown(
    body: bytes,
    content_type: str,
    charset: str,
    fallback_title: str,
) -> tuple[str, str]:
    text = decode_body(body, charset).replace("\x00", "")
    if content_type in {"text/html", "application/xhtml+xml"}:
        title, content, candidates = convert_html_with_images(text, fallback_title)
        for candidate in candidates:
            content = content.replace(
                candidate.marker, f"[图片：{candidate.alt_text}]"
            )
    elif content_type in {"application/json", "application/ld+json"}:
        try:
            rendered = json.dumps(json.loads(text), ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            rendered = text
        content = f"```json\n{rendered.strip()}\n```"
        title = fallback_title
    elif content_type in {"application/xml", "text/xml"}:
        parser = MarkdownExtractor()
        parser.feed(text)
        parser.close()
        content = parser.markdown()
        title = parser.title or fallback_title
    else:
        content = BLANK_LINES_RE.sub(
            "\n\n", text.replace("\r\n", "\n").replace("\r", "\n")
        ).strip()
        title = fallback_title
    if not content:
        raise SnapshotError("empty_content", "页面没有可离线阅读的文本内容")
    return title.strip() or fallback_title, content


def convert_html_with_images(
    text: str, fallback_title: str
) -> tuple[str, str, list[ImageCandidate]]:
    title_parser = DocumentTitleExtractor()
    title_parser.feed(text)
    title_parser.close()
    extracted_title = title_parser.title or clean_heading_text(fallback_title)
    selectors: list[tuple[str, str, int]] = [
        *(("class", class_name, 1) for class_name in ARTICLE_CLASS_NAMES),
        ("tag", "article", 40),
        ("tag", "main", 40),
        ("role", "main", 40),
        ("id", "main", 40),
        ("id", "content", 40),
        ("tag", "body", 1),
    ]
    for selector_kind, selector_value, minimum_score in selectors:
        container = HTMLContainerExtractor(selector_kind, selector_value)
        container.feed(text)
        container.close()
        best: tuple[int, str, list[ImageCandidate]] | None = None
        for fragment in container.fragments:
            parser = MarkdownExtractor()
            parser.feed(fragment)
            parser.close()
            content = parser.markdown()
            score = markdown_visible_score(content)
            if content and (best is None or score > best[0]):
                best = (score, content, parser.image_candidates)
        if best is not None and best[0] >= minimum_score:
            return extracted_title or fallback_title, best[1], best[2]
    parser = MarkdownExtractor()
    parser.feed(text)
    parser.close()
    content = parser.markdown()
    if not content:
        raise SnapshotError("empty_content", "页面没有可离线阅读的文本内容")
    return (
        extracted_title or parser.title or fallback_title,
        content,
        parser.image_candidates,
    )


def copyright_notice(original_url: str) -> str:
    return (
        "版权归原作者及原网站所有。本地快照仅供个人学习、检索和事实核验，"
        "不代表获得转载或再分发授权；引用时请保留原始来源。"
        f"原始来源：{original_url}"
    )


def safe_file_name(source_id: str) -> str:
    if SAFE_SOURCE_ID.fullmatch(source_id):
        return f"{source_id}.md"
    digest = hashlib.sha256(source_id.encode("utf-8")).hexdigest()[:20]
    return f"source-{digest}.md"


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def atomic_write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def image_signature_matches(content: bytes, mime_type: str) -> bool:
    if mime_type == "image/png":
        return content.startswith(b"\x89PNG\r\n\x1a\n")
    if mime_type == "image/jpeg":
        return content.startswith(b"\xff\xd8\xff")
    if mime_type == "image/gif":
        return content.startswith((b"GIF87a", b"GIF89a"))
    if mime_type == "image/webp":
        return (
            len(content) >= 12
            and content.startswith(b"RIFF")
            and content[8:12] == b"WEBP"
        )
    return False


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        payload = json.load(stream)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} 顶层必须是对象")
    return payload


def load_aliases(bank_dir: Path, sources: Iterable[Mapping[str, Any]]) -> dict[str, list[str]]:
    """按规范化 URL 把 coverage document_id 映射到真实 source_id。"""

    ids_by_url: dict[str, str] = {}
    for source in sources:
        if source.get("url"):
            ids_by_url[normalize_url(str(source["url"]))] = str(source["id"])
    aliases: dict[str, set[str]] = {source_id: set() for source_id in ids_by_url.values()}
    for coverage_path in sorted((bank_dir / "data").glob("*-coverage.json")):
        try:
            payload = load_json(coverage_path)
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        for document in payload.get("documents") or []:
            if not isinstance(document, dict) or not document.get("url"):
                continue
            source_id = ids_by_url.get(normalize_url(str(document["url"])))
            document_id = str(document.get("document_id") or "").strip()
            if source_id and document_id and document_id != source_id:
                aliases.setdefault(source_id, set()).add(document_id)
    return {
        source_id: sorted(source_aliases)
        for source_id, source_aliases in aliases.items()
        if source_aliases
    }


class SourceSnapshotCrawler:
    def __init__(
        self,
        *,
        output_dir: Path,
        timeout_seconds: float = 15.0,
        delay_seconds: float = 1.0,
        retries: int = 2,
        max_bytes: int = 5_000_000,
        max_assets_per_source: int = 20,
        max_asset_bytes: int = 5_000_000,
        max_asset_total_bytes: int = 20_000_000,
        max_redirects: int = 5,
        user_agent: str = DEFAULT_USER_AGENT,
        resolver: Callable[..., list[tuple[Any, ...]]] = socket.getaddrinfo,
        sleep: Callable[[float], None] = time.sleep,
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        self.output_dir = output_dir
        self.timeout_seconds = timeout_seconds
        self.delay_seconds = delay_seconds
        self.retries = retries
        self.max_bytes = max_bytes
        self.max_assets_per_source = max_assets_per_source
        self.max_asset_bytes = max_asset_bytes
        self.max_asset_total_bytes = max_asset_total_bytes
        self.max_redirects = max_redirects
        self.user_agent = user_agent
        self.resolver = resolver
        self.sleep = sleep
        self.rate_limiter = HostRateLimiter(monotonic=monotonic, sleep=sleep)
        self.robots_cache: dict[str, RobotsRules] = {}
        # 显式禁用环境代理，避免个人学习任务意外使用公司内网代理。
        self.opener = build_opener(ProxyHandler({}), NoRedirectHandler())

    def _request_once(self, url: str, *, max_bytes: int) -> FetchResponse:
        request = Request(
            url,
            method="GET",
            headers={
                "Accept": (
                    "text/html,application/xhtml+xml,application/json,"
                    "text/plain,text/markdown,application/xml;q=0.9,*/*;q=0.1"
                ),
                "Accept-Encoding": "identity",
                "User-Agent": self.user_agent,
            },
        )
        try:
            response = self.opener.open(request, timeout=self.timeout_seconds)
        except HTTPError as exc:
            body = exc.read(min(max_bytes + 1, 64_000))
            return FetchResponse(
                url=exc.geturl(),
                status=exc.code,
                headers=dict(exc.headers.items()) if exc.headers else {},
                body=body,
            )
        with response:
            headers = dict(response.headers.items())
            declared_size = headers.get("Content-Length") or headers.get(
                "content-length"
            )
            if declared_size:
                try:
                    if int(declared_size) > max_bytes:
                        raise SnapshotError(
                            "too_large",
                            f"响应声明大小 {declared_size} 字节，超过上限 {max_bytes}",
                        )
                except ValueError:
                    pass
            body = response.read(max_bytes + 1)
            if len(body) > max_bytes:
                raise SnapshotError(
                    "too_large", f"响应超过 {max_bytes} 字节大小限制"
                )
            return FetchResponse(
                url=response.geturl(),
                status=response.status,
                headers=headers,
                body=body,
            )

    def _request_with_retry(
        self, url: str, *, max_bytes: int, delay_seconds: float | None = None
    ) -> FetchResponse:
        last_error: BaseException | None = None
        host = (urlsplit(url).hostname or "").lower()
        request_delay = (
            self.delay_seconds if delay_seconds is None else delay_seconds
        )
        for attempt in range(self.retries + 1):
            self.rate_limiter.wait(host, request_delay)
            try:
                response = self._request_once(url, max_bytes=max_bytes)
            except SnapshotError:
                raise
            except (TimeoutError, URLError, OSError) as exc:
                last_error = exc
                if attempt >= self.retries:
                    break
                self.sleep(min(2**attempt, 4))
                continue
            if response.status not in TRANSIENT_STATUS or attempt >= self.retries:
                return response
            retry_after = response.headers.get("Retry-After") or response.headers.get(
                "retry-after"
            )
            try:
                wait_seconds = min(float(retry_after or 0), 30.0)
            except ValueError:
                wait_seconds = 0
            self.sleep(max(wait_seconds, min(2**attempt, 4)))
        raise SnapshotError("network_error", f"请求失败：{last_error}")

    def _robots_origin(self, url: str) -> tuple[str, str]:
        parsed = urlsplit(url)
        port = parsed.port
        default_port = (parsed.scheme == "http" and port == 80) or (
            parsed.scheme == "https" and port == 443
        )
        authority = parsed.hostname or ""
        if port is not None and not default_port:
            authority = f"{authority}:{port}"
        origin = f"{parsed.scheme}://{authority}"
        return origin, f"{origin}/robots.txt"

    def _fetch_robots_response(self, robots_url: str) -> FetchResponse:
        current_url = robots_url
        visited: set[str] = set()
        for _ in range(self.max_redirects + 1):
            current_key = redirect_key(current_url)
            if current_key in visited:
                raise SnapshotError("robots_unavailable", "robots.txt 重定向循环")
            visited.add(current_key)
            validate_public_url(current_url, resolver=self.resolver)
            response = self._request_with_retry(current_url, max_bytes=512_000)
            if response.status not in REDIRECT_STATUS:
                return response
            location = response.headers.get("Location") or response.headers.get(
                "location"
            )
            if not location:
                raise SnapshotError(
                    "robots_unavailable", "robots.txt 重定向缺少 Location"
                )
            current_url = urljoin(current_url, location)
        raise SnapshotError("robots_unavailable", "robots.txt 重定向次数超过限制")

    def _load_robots(self, url: str) -> RobotsPolicy:
        origin, robots_url = self._robots_origin(url)
        rules = self.robots_cache.get(origin)
        if rules is None:
            try:
                response = self._fetch_robots_response(robots_url)
            except SnapshotError as exc:
                rules = RobotsRules(
                    parser=None,
                    default_allowed=False,
                    status="robots_unavailable",
                    delay_seconds=self.delay_seconds,
                    detail=str(exc),
                )
            else:
                if response.status in {404, 410}:
                    rules = RobotsRules(
                        parser=None,
                        default_allowed=True,
                        status="robots_not_found",
                        delay_seconds=self.delay_seconds,
                    )
                elif response.status in {401, 403}:
                    rules = RobotsRules(
                        parser=None,
                        default_allowed=False,
                        status="robots_denied",
                        delay_seconds=self.delay_seconds,
                        detail=f"robots.txt 返回 HTTP {response.status}",
                    )
                elif response.status >= 500:
                    rules = RobotsRules(
                        parser=None,
                        default_allowed=False,
                        status="robots_unavailable",
                        delay_seconds=self.delay_seconds,
                        detail=f"robots.txt 返回 HTTP {response.status}",
                    )
                elif 300 <= response.status < 400:
                    rules = RobotsRules(
                        parser=None,
                        default_allowed=False,
                        status="robots_unavailable",
                        delay_seconds=self.delay_seconds,
                        detail=f"robots.txt 返回未处理的 HTTP {response.status}",
                    )
                elif response.status != 200:
                    rules = RobotsRules(
                        parser=None,
                        default_allowed=True,
                        status="robots_not_found",
                        delay_seconds=self.delay_seconds,
                        detail=f"robots.txt 返回 HTTP {response.status}",
                    )
                else:
                    robot_parser = RobotFileParser()
                    robot_parser.set_url(robots_url)
                    robot_parser.parse(
                        decode_body(response.body, "utf-8").splitlines()
                    )
                    crawl_delay = robot_parser.crawl_delay(ROBOT_USER_AGENT)
                    if crawl_delay is None:
                        crawl_delay = robot_parser.crawl_delay("*")
                    rules = RobotsRules(
                        parser=robot_parser,
                        default_allowed=True,
                        status="robots_allowed",
                        delay_seconds=max(
                            self.delay_seconds,
                            float(crawl_delay or self.delay_seconds),
                        ),
                    )
            self.robots_cache[origin] = rules
        allowed = (
            rules.parser.can_fetch(ROBOT_USER_AGENT, url)
            if rules.parser is not None
            else rules.default_allowed
        )
        return RobotsPolicy(
            allowed=allowed,
            status=(
                rules.status
                if allowed or rules.status != "robots_allowed"
                else "robots_denied"
            ),
            delay_seconds=rules.delay_seconds,
            detail=rules.detail,
        )

    def fetch(
        self, url: str, *, max_bytes: int | None = None
    ) -> tuple[FetchResponse, RobotsPolicy]:
        current_url = url
        visited: set[str] = set()
        for _ in range(self.max_redirects + 1):
            current_key = redirect_key(current_url)
            if current_key in visited:
                raise SnapshotError("redirect_error", "检测到重定向循环")
            visited.add(current_key)
            validate_public_url(current_url, resolver=self.resolver)
            policy = self._load_robots(current_url)
            if not policy.allowed:
                raise SnapshotError(policy.status, policy.detail or "robots.txt 禁止抓取")
            response = self._request_with_retry(
                current_url,
                max_bytes=self.max_bytes if max_bytes is None else max_bytes,
                delay_seconds=policy.delay_seconds,
            )
            if response.status in REDIRECT_STATUS:
                location = response.headers.get("Location") or response.headers.get(
                    "location"
                )
                if not location:
                    raise SnapshotError("redirect_error", "重定向缺少 Location")
                current_url = urljoin(current_url, location)
                continue
            return response, policy
        raise SnapshotError("redirect_error", "重定向次数超过限制")

    def download_assets(
        self,
        *,
        source_id: str,
        page_url: str,
        candidates: list[ImageCandidate],
        content: str,
    ) -> tuple[str, list[dict[str, Any]]]:
        assets: list[dict[str, Any]] = []
        by_url: dict[str, dict[str, Any]] = {}
        total_bytes = 0
        unique_count = 0
        for candidate in candidates:
            resolved_url = urljoin(page_url, candidate.original_url)
            normalized_url = redirect_key(resolved_url)
            existing = by_url.get(normalized_url)
            if existing is not None:
                replacement = (
                    f"![{markdown_alt(candidate.alt_text)}]"
                    f"(snapshot-asset:{existing['asset_id']})"
                    if existing.get("status") == "downloaded"
                    else f"[图片未缓存：{candidate.alt_text}]"
                )
                content = content.replace(candidate.marker, replacement)
                continue
            unique_count += 1
            asset_id = (
                "asset-"
                + hashlib.sha256(normalized_url.encode("utf-8")).hexdigest()[:16]
            )
            base: dict[str, Any] = {
                "asset_id": asset_id,
                "original_url": resolved_url,
                "final_url": None,
                "local_path": None,
                "mime_type": None,
                "status": "pending",
                "content_hash": None,
                "byte_count": 0,
                "alt_text": candidate.alt_text,
                "capture_method": "public_crawler",
                "license": None,
                "copyright_notice": copyright_notice(resolved_url),
                "error": None,
            }
            if unique_count > self.max_assets_per_source:
                base.update(
                    {
                        "status": "asset_count_limit",
                        "error": (
                            f"单来源图片数量超过上限 {self.max_assets_per_source}"
                        ),
                    }
                )
            else:
                remaining = self.max_asset_total_bytes - total_bytes
                if remaining <= 0:
                    base.update(
                        {
                            "status": "asset_total_size_limit",
                            "error": (
                                "单来源图片累计大小超过上限 "
                                f"{self.max_asset_total_bytes}"
                            ),
                        }
                    )
                else:
                    try:
                        response, _ = self.fetch(
                            resolved_url,
                            max_bytes=min(self.max_asset_bytes, remaining),
                        )
                        if response.status in {401, 403}:
                            raise SnapshotError(
                                "access_denied",
                                f"图片返回 HTTP {response.status}",
                                http_status=response.status,
                            )
                        if response.status < 200 or response.status >= 300:
                            raise SnapshotError(
                                "http_error",
                                f"图片返回 HTTP {response.status}",
                                http_status=response.status,
                            )
                        mime_type, _ = parse_content_type(response.headers)
                        base["mime_type"] = mime_type or None
                        if mime_type == "image/svg+xml":
                            raise SnapshotError(
                                "unsafe_svg",
                                "SVG 可能包含脚本或外部引用，当前安全策略拒绝保存",
                            )
                        extension = SUPPORTED_IMAGE_TYPES.get(mime_type)
                        if extension is None:
                            raise SnapshotError(
                                "unsupported_image_type",
                                f"不支持图片类型：{mime_type or 'missing Content-Type'}",
                            )
                        if not image_signature_matches(response.body, mime_type):
                            raise SnapshotError(
                                "invalid_image_signature",
                                "图片内容与 Content-Type 文件签名不一致",
                            )
                        local_path = (
                            Path("assets")
                            / safe_file_name(source_id).removesuffix(".md")
                            / f"{asset_id}{extension}"
                        )
                        target_path = self.output_dir / local_path
                        if not target_path.resolve().is_relative_to(
                            self.output_dir.resolve()
                        ):
                            raise SnapshotError(
                                "blocked_path", "本地图片目标路径越界"
                            )
                        atomic_write_bytes(target_path, response.body)
                        digest = hashlib.sha256(response.body).hexdigest()
                        total_bytes += len(response.body)
                        base.update(
                            {
                                "final_url": response.url,
                                "local_path": local_path.as_posix(),
                                "status": "downloaded",
                                "content_hash": f"sha256:{digest}",
                                "byte_count": len(response.body),
                                "error": None,
                            }
                        )
                    except SnapshotError as exc:
                        base["status"] = exc.status
                        base["error"] = str(exc)
                    except Exception as exc:
                        base["status"] = "processing_error"
                        base["error"] = f"{type(exc).__name__}: {exc}"
            assets.append(base)
            by_url[normalized_url] = base
            replacement = (
                f"![{markdown_alt(candidate.alt_text)}](snapshot-asset:{asset_id})"
                if base.get("status") == "downloaded"
                else f"[图片未缓存：{candidate.alt_text}]"
            )
            content = content.replace(candidate.marker, replacement)
        return content, assets

    def snapshot_item(
        self,
        source: Mapping[str, Any],
        *,
        aliases: Iterable[str] = (),
    ) -> dict[str, Any]:
        source_id = str(source.get("id") or "").strip()
        title = str(source.get("title") or source_id).strip()
        original_url = source.get("url")
        base: dict[str, Any] = {
            "source_id": source_id,
            "aliases": sorted(set(aliases)),
            "title": title,
            "platform": str(source.get("platform") or "").strip(),
            "original_url": original_url,
            "final_url": None,
            "local_path": None,
            "content_type": None,
            "content_format": None,
            "capture_method": None,
            "captured_at": None,
            "accessed_at": source.get("accessed_at"),
            "status": "no_url" if not original_url else "pending",
            "http_status": None,
            "content_hash": None,
            "char_count": 0,
            "byte_count": 0,
            "assets": [],
            "license": None,
            "copyright_notice": (
                copyright_notice(str(original_url)) if original_url else None
            ),
            "error": None,
        }
        if not original_url:
            base["error"] = "本地资料没有公开 URL，不执行网络抓取"
            return base
        try:
            response, policy = self.fetch(str(original_url))
            base["http_status"] = response.status
            base["final_url"] = response.url
            if response.status in {401, 403}:
                raise SnapshotError(
                    "access_denied",
                    f"页面返回 HTTP {response.status}；不尝试登录或绕过访问控制",
                    http_status=response.status,
                )
            if response.status == 429:
                raise SnapshotError(
                    "rate_limited",
                    "页面返回 HTTP 429；已停止，不规避站点限流",
                    http_status=response.status,
                )
            if response.status < 200 or response.status >= 300:
                raise SnapshotError(
                    "http_error",
                    f"页面返回 HTTP {response.status}",
                    http_status=response.status,
                )
            content_type, charset = parse_content_type(response.headers)
            base["content_type"] = content_type
            if content_type not in SUPPORTED_TEXT_TYPES:
                raise SnapshotError(
                    "unsupported_content_type",
                    f"不保存 {content_type}；当前仅落地文本、HTML、JSON 和 XML",
                )
            image_candidates: list[ImageCandidate] = []
            if content_type in {"text/html", "application/xhtml+xml"}:
                extracted_title, content, image_candidates = convert_html_with_images(
                    decode_body(response.body, charset).replace("\x00", ""), title
                )
            else:
                extracted_title, content = convert_to_markdown(
                    response.body, content_type, charset, title
                )
            if len(content) < 500 and LIMITED_PAGE_RE.search(content):
                raise SnapshotError(
                    "access_limited",
                    "页面要求登录、人机验证或显示访问限制；不尝试绕过",
                )
            content, assets = self.download_assets(
                source_id=source_id,
                page_url=response.url,
                candidates=image_candidates,
                content=content,
            )
            notice = copyright_notice(str(original_url))
            captured_at = utc_now()
            document = (
                f"# {extracted_title}\n\n"
                f"> {notice}\n\n"
                f"> 快照时间：{captured_at}；robots 状态：{policy.status}。\n\n"
                f"{content.rstrip()}\n"
            )
            encoded = document.encode("utf-8")
            content_hash = hashlib.sha256(encoded).hexdigest()
            local_path = Path("content") / safe_file_name(source_id)
            atomic_write_text(self.output_dir / local_path, document)
            base.update(
                {
                    "title": extracted_title,
                    "local_path": local_path.as_posix(),
                    "content_format": "markdown",
                    "capture_method": "public_crawler",
                    "captured_at": captured_at,
                    "status": "downloaded",
                    "content_hash": f"sha256:{content_hash}",
                    "char_count": len(document),
                    "byte_count": len(encoded),
                    "assets": assets,
                    "error": None,
                }
            )
        except SnapshotError as exc:
            base["status"] = exc.status
            base["http_status"] = exc.http_status or base["http_status"]
            base["error"] = str(exc)
        except Exception as exc:
            # 单个第三方页面即使包含畸形 HTML，也不能中断其余来源的落地。
            base["status"] = "processing_error"
            base["error"] = f"{type(exc).__name__}: {exc}"
        return base


def should_reuse(item: Mapping[str, Any], output_dir: Path) -> bool:
    local_path = item.get("local_path")
    status = str(item.get("status") or "")
    if status == "downloaded":
        return isinstance(local_path, str) and (output_dir / local_path).is_file()
    return bool(status) and status not in RETRY_ON_NEXT_RUN_STATUS


def empty_item(
    source: Mapping[str, Any], aliases: Iterable[str], status: str = "not_requested"
) -> dict[str, Any]:
    original_url = source.get("url")
    return {
        "source_id": source.get("id"),
        "aliases": sorted(set(aliases)),
        "title": source.get("title"),
        "platform": source.get("platform"),
        "original_url": original_url,
        "final_url": None,
        "local_path": None,
        "content_type": None,
        "content_format": None,
        "capture_method": None,
        "captured_at": None,
        "accessed_at": source.get("accessed_at"),
        "status": "no_url" if not original_url else status,
        "http_status": None,
        "content_hash": None,
        "char_count": 0,
        "byte_count": 0,
        "assets": [],
        "license": None,
        "copyright_notice": (
            copyright_notice(str(original_url)) if original_url else None
        ),
        "error": (
            "本地资料没有公开 URL，不执行网络抓取" if not original_url else None
        ),
    }


def write_manifest(
    output_dir: Path,
    *,
    catalog_path: Path,
    items: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    sorted_items = sorted(items, key=lambda item: str(item.get("source_id") or ""))
    counts: dict[str, int] = {}
    for item in sorted_items:
        status = str(item.get("status") or "unknown")
        counts[status] = counts.get(status, 0) + 1
    payload = {
        "schema_version": "1.0",
        "generated_at": utc_now(),
        "catalog_path": os.path.relpath(catalog_path, output_dir),
        "policy": {
            "scope": "public-http-https-only",
            "authentication": "never-used",
            "robots_txt": "required",
            "content_storage": "sanitized-markdown-only",
            "git_policy": "local-snapshots-must-not-be-committed",
        },
        "statistics": {
            "total": len(sorted_items),
            "by_status": dict(sorted(counts.items())),
        },
        "items": sorted_items,
    }
    atomic_write_text(
        output_dir / "manifest.json",
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    )
    return payload


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="把 questions.json 中的公开来源保存为本地安全 Markdown 快照"
    )
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--source-id",
        action="append",
        default=[],
        help="仅抓指定 source_id，可重复；未指定时抓全部公开 URL",
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="最多处理多少条待抓来源，便于分批执行"
    )
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--max-bytes", type=int, default=5_000_000)
    parser.add_argument("--max-assets-per-source", type=int, default=20)
    parser.add_argument("--max-asset-bytes", type=int, default=5_000_000)
    parser.add_argument("--max-asset-total-bytes", type=int, default=20_000_000)
    parser.add_argument("--refresh", action="store_true", help="重新抓取已有成功快照")
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if (
        args.timeout <= 0
        or args.delay < 0
        or args.retries < 0
        or args.max_bytes <= 0
        or args.max_assets_per_source <= 0
        or args.max_asset_bytes <= 0
        or args.max_asset_total_bytes <= 0
    ):
        raise SystemExit(
            "timeout、页面/图片大小和图片数量限制必须大于 0，"
            "delay/retries 不能小于 0"
        )
    catalog_path = args.catalog.resolve()
    output_dir = args.output.resolve()
    catalog = load_json(catalog_path)
    sources = catalog.get("sources")
    if not isinstance(sources, list):
        raise SystemExit(f"{catalog_path} 缺少 sources 数组")
    source_ids = [str(source.get("id") or "") for source in sources]
    if len(source_ids) != len(set(source_ids)) or any(not item for item in source_ids):
        raise SystemExit("sources 中存在空 ID 或重复 ID")
    requested = set(args.source_id)
    unknown = requested - set(source_ids)
    if unknown:
        raise SystemExit(f"未知 source_id：{', '.join(sorted(unknown))}")
    aliases = load_aliases(BANK_DIR, sources)
    existing_path = output_dir / "manifest.json"
    existing_items: dict[str, dict[str, Any]] = {}
    if existing_path.is_file():
        try:
            existing = load_json(existing_path)
            existing_items = {
                str(item.get("source_id")): item
                for item in existing.get("items") or []
                if isinstance(item, dict) and item.get("source_id")
            }
        except (OSError, ValueError, json.JSONDecodeError):
            existing_items = {}
    crawler = SourceSnapshotCrawler(
        output_dir=output_dir,
        timeout_seconds=args.timeout,
        delay_seconds=args.delay,
        retries=args.retries,
        max_bytes=args.max_bytes,
        max_assets_per_source=args.max_assets_per_source,
        max_asset_bytes=args.max_asset_bytes,
        max_asset_total_bytes=args.max_asset_total_bytes,
    )
    items: dict[str, dict[str, Any]] = {}
    selected = [
        source
        for source in sources
        if not requested or str(source.get("id")) in requested
    ]
    if args.limit is not None:
        selected = selected[: max(0, args.limit)]
    selected_ids = {str(source.get("id")) for source in selected}
    for source in sources:
        source_id = str(source["id"])
        previous = existing_items.get(source_id)
        items[source_id] = previous or empty_item(
            source, aliases.get(source_id, ())
        )
    write_manifest(output_dir, catalog_path=catalog_path, items=items.values())
    for source in sources:
        source_id = str(source["id"])
        if source_id not in selected_ids:
            continue
        previous = existing_items.get(source_id)
        if previous and not args.refresh and should_reuse(previous, output_dir):
            reused = dict(previous)
            reused["aliases"] = aliases.get(source_id, [])
            items[source_id] = reused
        else:
            print(f"[fetch] {source_id}: {source.get('url') or 'no public URL'}")
            items[source_id] = crawler.snapshot_item(
                source, aliases=aliases.get(source_id, ())
            )
            write_manifest(
                output_dir, catalog_path=catalog_path, items=items.values()
            )
            print(f"[{items[source_id]['status']}] {source_id}")
    manifest = write_manifest(
        output_dir, catalog_path=catalog_path, items=items.values()
    )
    print(
        json.dumps(
            manifest["statistics"], ensure_ascii=False, separators=(",", ":")
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(run())
