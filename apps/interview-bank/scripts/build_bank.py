#!/usr/bin/env python3
"""Build the interview question bank from reviewed Markdown and curated data."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import html
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[3]
BANK_ROOT = REPO_ROOT / "apps" / "interview-bank"
DATA_DIR = BANK_ROOT / "data"
DOCS_DIR = REPO_ROOT / "docs" / "08-求职备考" / "04-面试题库"
HISTORY_DIR = DOCS_DIR / "历史资料"

MODULE_FILES: Sequence[Tuple[str, str, str]] = (
    ("01", "测试基础与质量思维", "01-测试基础与质量思维.md"),
    ("02", "功能测试与用例设计", "02-功能测试与用例设计.md"),
    ("03", "计算机基础、命令行、数据库与版本控制", "03-计算机基础与命令行数据库版本控制.md"),
    ("04", "网络、接口与数据库测试", "04-网络接口与数据库测试.md"),
    ("05", "编程语言与接口自动化测试框架", "05-编程语言与接口自动化测试框架.md"),
    ("06", "Web、Android 与 iOS 界面自动化", "06-网页与移动端界面自动化.md"),
    ("07", "性能测试与稳定性", "07-性能测试与稳定性.md"),
    ("08", "持续集成、质量工程与测试开发", "08-持续集成持续交付质量工程与测试开发.md"),
    ("09", "AI、RAG、Agent 与大模型系统测试", "09-人工智能测试与大模型系统测试.md"),
    ("10", "场景题、项目题与行为面试", "10-场景题项目题与行为面试.md"),
)

HISTORY_FILES: Sequence[Tuple[str, str]] = (
    ("personal-latest-outline", "个人整理最新版题库.md"),
)

CURATED_FILES: Sequence[str] = (
    "personal-latest-reviewed.json",
    "curated-2026.json",
    "supplemental-backend-questions.json",
    "supplemental-ui-performance-questions.json",
    "supplemental-interview-questions.json",
    "supplemental-sources.json",
    "xiaolincoding-business-questions.json",
    "xiaolincoding-automation-questions.json",
    "xiaolincoding-performance-questions.json",
    "xiaolincoding-sources.json",
)

QUESTION_HEADING = re.compile(r"^##\s+(?:Q)?(\d+)[.：:]\s*(.+?)\s*$", re.MULTILINE)
FIELD_HEADING = re.compile(r"^\*\*(岗位考点|参考答案|原理或实践解释|原理与实践解释|常见追问或误区|常见追问与误区)\*\*\s*$")
MODULE_APPENDIX_HEADING = re.compile(r"^##\s+\S")
OUTLINE_ITEM = re.compile(r"^\s*(\d+)\.\s+(.+?)\s*$")

# These strings must never enter the generated public bank or coverage artifact.
# They represent claims that must not enter the generated public bank.
FORBIDDEN_PUBLIC_PATTERNS: Sequence[re.Pattern[str]] = (
    re.compile(r"\u5ea6\u5c0f\u6ee1"),
    re.compile(r"\u751f\u4ea7\u73af\u5883\u8131\u654f\u6570\u636e"),
    re.compile(r"\u771f\u5b9e\u516c\u53f8\u9879\u76ee"),
    re.compile(r"\u4e2a\u4eba\u7ecf\u9a8c\uff1a"),
)

PERSONAL_OR_PROJECT_TERMS = (
    "上一家公司",
    "你们项目",
    "最近负责的项目",
    "团队规模",
    "项目组",
    "活跃用户",
    "版本号",
    "离职原因",
    "期望薪资",
    "入职周期",
    "个人负责",
    "从事3年",
    "从事 3 年",
)

SECTION_MODULE_HINTS: Dict[str, str] = {
    "测试理论": "01",
    "测试思维 & 场景": "10",
    "测试思维与场景": "10",
    "项目相关": "10",
    "测试用例设计": "02",
    "测试管理": "08",
    "抓包与网络协议": "04",
    "职业规划": "10",
}

MODULE_ROLES: Dict[str, List[str]] = {
    "01": ["功能测试", "软件测试", "测试开发"],
    "02": ["功能测试", "软件测试"],
    "03": ["自动化测试", "测试开发"],
    "04": ["接口测试", "自动化测试", "测试开发"],
    "05": ["接口自动化", "测试开发"],
    "06": ["Web自动化", "移动端自动化", "测试开发"],
    "07": ["性能测试", "稳定性测试", "测试开发"],
    "08": ["测试开发", "质量工程", "测试负责人"],
    "09": ["AI测试", "大模型评测", "测试开发"],
    "10": ["软件测试", "自动化测试", "测试开发"],
}

MODULE_PRACTICE_SCENARIOS: Dict[str, Dict[str, str]] = {
    "01": {
        "background": "Demo Shop 正在做版本发布评审，已经形成需求范围、缺陷清单和测试执行记录。",
        "data": "提供版本范围、风险清单、测试结果、残余缺陷和准出时间点。",
    },
    "02": {
        "background": "Demo Shop 包含搜索、上传、下单、库存和权限等常见业务能力。",
        "data": "提供可重置的用户、订单、边界值和异常状态，用于完成用例设计。",
    },
    "03": {
        "background": "练习环境包含 Linux 日志、PostgreSQL 示例库和 Git 演示仓库。",
        "data": "提供应用日志、表数据、提交历史和可重复执行的故障样本。",
    },
    "04": {
        "background": "订单 API 提供 OpenAPI 契约、测试数据库和可控制的异步消息。",
        "data": "提供测试 Token、订单、分页数据和故障注入结果，用于建立接口证据链。",
    },
    "05": {
        "background": "Python 接口自动化练习工程使用 pytest、HTTP 客户端和可替换的 Mock 服务。",
        "data": "提供环境配置、认证占位值、可重复测试数据和标准化失败证据。",
    },
    "06": {
        "background": "Web 演示站与 Android/iOS Mock 应用提供稳定的自动化练习页面。",
        "data": "提供测试账号、隔离浏览器上下文、可重置设备状态和定位属性。",
    },
    "07": {
        "background": "容量实验服务提供可控负载、监控指标和故障开关。",
        "data": "提供目标业务比例、到达率、延迟、错误率、资源曲线和恢复时间。",
    },
    "08": {
        "background": "CI 练习仓库包含流水线、容器化依赖、契约测试和可观测性样例。",
        "data": "提供提交记录、构建制品、测试结果、失败日志和门禁配置。",
    },
    "09": {
        "background": "RAG 智能助手包含离线评测集、检索 Trace、工具沙箱和安全策略。",
        "data": "提供版本化提示词、知识文档、人工标注、攻击样本和完整调用轨迹。",
    },
}

ALLOWED_ROLES = {
    "AI测试",
    "SRE",
    "Web自动化",
    "功能测试",
    "后端测试",
    "大模型评测",
    "安全测试",
    "性能测试",
    "接口测试",
    "接口自动化",
    "数据评测",
    "测试开发",
    "测试负责人",
    "移动端测试",
    "移动端自动化",
    "稳定性测试",
    "自动化测试",
    "质量工程",
    "软件测试",
}

XIAOLINCODING_QUESTION_FIELDS = {
    "id",
    "module_id",
    "origin",
    "title",
    "level",
    "kind",
    "roles",
    "tags",
    "focus",
    "scenario",
    "answer",
    "explanation",
    "followups",
    "pitfalls",
    "related_question_ids",
    "deepening_rationale",
    "source_ids",
    "updated_at",
}

TAG_KEYWORDS: Sequence[Tuple[str, str]] = (
    ("pytest", "pytest"),
    ("playwright", "Playwright"),
    ("selenium", "Selenium"),
    ("appium", "Appium"),
    ("http", "HTTP"),
    ("接口", "接口测试"),
    ("数据库", "数据库"),
    ("sql", "SQL"),
    ("性能", "性能测试"),
    ("稳定性", "稳定性"),
    ("rag", "RAG"),
    ("agent", "Agent"),
    ("llm", "LLM"),
    ("大模型", "大模型"),
    ("ai", "AI测试"),
    ("安全", "安全测试"),
    ("兼容", "兼容性"),
    ("持续集成", "CI/CD"),
    ("ci", "CI/CD"),
    ("git", "Git"),
    ("docker", "Docker"),
)


@dataclass
class LegacyItem:
    source_id: str
    source_file: str
    source_type: str
    index: int
    section: str
    question: str
    answer_has_sensitive_claim: bool = False


def clean_text(value: str) -> str:
    """Normalize prose while preserving indentation inside fenced code blocks."""
    value = html.unescape(value).replace("\xa0", " ")
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    result: List[str] = []
    blank = False
    in_fence = False
    for raw_line in value.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("```"):
            result.append(stripped)
            in_fence = not in_fence
            blank = False
            continue
        if in_fence:
            result.append(raw_line.rstrip())
            blank = False
            continue
        line = re.sub(r"[ \t]+", " ", raw_line).strip()
        if line:
            result.append(line)
            blank = False
        elif result and not blank:
            result.append("")
            blank = True
    return "\n".join(result).strip()


def normalize_title(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).lower()
    value = re.sub(
        r"^个人整理最新版\s*\d+\s*[|｜]",
        "",
        value,
    )
    value = re.sub(r"^\s*(?:q)?\d+[.、:：]?\s*", "", value)
    replacements = {
        "bug": "缺陷",
        "app": "移动端",
        "web": "网页",
        "测试点": "测试",
        "测试要点": "测试",
        "怎么": "如何",
        "怎样": "如何",
        "哪些": "什么",
        "是什么": "",
        "你会": "",
        "请": "",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return re.sub(r"[\W_]+", "", value, flags=re.UNICODE)


def safe_question_text(value: str) -> str:
    """Sanitize a legacy question title without carrying personal assertions."""
    value = re.sub(
        r"\u5ea6\u5c0f\u6ee1(?:\u91d1\u878d)?\u9879\u76ee",
        "公开虚构练习项目",
        value,
    )
    value = value.replace("你们原来项目", "你选择的公开或虚构练习项目")
    value = value.replace("你们xx项目", "该公开或虚构练习项目")
    value = value.replace("上一家公司", "过往经历（仅按本人真实情况）")
    value = value.replace("公司的产品", "虚构产品")
    return clean_text(value)


def has_forbidden_public_text(value: str) -> bool:
    return any(pattern.search(value) for pattern in FORBIDDEN_PUBLIC_PATTERNS)


def validate_public_text(value: str, context: str) -> None:
    for pattern in FORBIDDEN_PUBLIC_PATTERNS:
        match = pattern.search(value)
        if match:
            raise ValueError(f"{context} 含禁止进入个人题库的内容：{match.group(0)}")


def split_markdown_fields(body: str) -> Dict[str, str]:
    fields: Dict[str, List[str]] = {}
    current: Optional[str] = None
    for line in body.splitlines():
        # The last question in each module is followed by maintenance notes,
        # checklists and public references. They belong to the module, not to
        # that question's pitfalls.
        if MODULE_APPENDIX_HEADING.match(line.strip()):
            break
        match = FIELD_HEADING.match(line.strip())
        if match:
            current = match.group(1)
            fields[current] = []
            continue
        if current is not None:
            fields[current].append(line)
    return {name: clean_text("\n".join(lines)) for name, lines in fields.items()}


def parse_followups(value: str) -> Tuple[List[str], List[str]]:
    followups: List[str] = []
    pitfalls: List[str] = []
    for raw_line in value.splitlines():
        line = re.sub(r"^[-*]\s*", "", raw_line).strip()
        if not line:
            continue
        if line.startswith("追问"):
            followups.append(line)
        elif line.startswith("误区"):
            pitfalls.append(line)
        else:
            pitfalls.append(line)
    return followups, pitfalls


def infer_level(module_id: str, position: int, title: str) -> str:
    advanced = ("架构", "一致性", "并发", "隔离", "安全", "评测平台", "容量", "故障", "红队")
    if module_id in {"07", "08", "09"} and (position >= 8 or any(term in title for term in advanced)):
        return "高级"
    if position <= 5 and module_id in {"01", "02", "03", "04", "05", "06"}:
        return "入门"
    return "进阶"


def infer_kind(module_id: str, title: str) -> str:
    if module_id == "10":
        if any(term in title for term in ("自我介绍", "为什么选择", "失败", "面试官")):
            return "行为题"
        if any(term in title for term in ("项目", "负责模块", "印象深刻")):
            return "项目题"
        return "场景题"
    if any(term in title.lower() for term in ("如何设计", "怎么测试", "怎样测试", "如何测试", "如何排查", "如何使用")):
        return "实操题"
    return "知识题"


def infer_tags(module_name: str, title: str, body: str) -> List[str]:
    text = f"{module_name} {title} {body}".lower()
    tags: List[str] = [module_name.split("、")[0]]
    for keyword, tag in TAG_KEYWORDS:
        if keyword in text and tag not in tags:
            tags.append(tag)
    return tags[:8]


def parse_module_questions(
    module_id: str, module_name: str, file_name: str
) -> List[Dict[str, Any]]:
    path = DOCS_DIR / file_name
    text = path.read_text(encoding="utf-8")
    matches = list(QUESTION_HEADING.finditer(text))
    questions: List[Dict[str, Any]] = []
    for ordinal, match in enumerate(matches, start=1):
        end = matches[ordinal].start() if ordinal < len(matches) else len(text)
        title = clean_text(match.group(2))
        fields = split_markdown_fields(text[match.end() : end])
        required = ("岗位考点", "参考答案")
        missing = [field for field in required if not fields.get(field)]
        explanation = fields.get("原理或实践解释") or fields.get("原理与实践解释")
        followup_text = fields.get("常见追问或误区") or fields.get("常见追问与误区")
        if not explanation:
            missing.append("原理或实践解释")
        if not followup_text:
            missing.append("常见追问或误区")
        if missing:
            raise ValueError(f"{file_name} / {title} 缺少字段：{', '.join(missing)}")
        followups, pitfalls = parse_followups(followup_text or "")
        question_id = f"core-{module_id}-{int(match.group(1)):02d}"
        answer = fields["参考答案"]
        focus = fields["岗位考点"]
        combined = "\n".join((focus, answer, explanation or "", followup_text or ""))
        validate_public_text(combined, f"{file_name} / {title}")
        item: Dict[str, Any] = {
            "id": question_id,
            "module_id": module_id,
            "module_name": module_name,
            "position": ordinal,
            "title": title,
            "level": infer_level(module_id, ordinal, title),
            "kind": infer_kind(module_id, title),
            "roles": MODULE_ROLES[module_id],
            "tags": infer_tags(module_name, title, combined),
            "focus": focus,
            "answer_strategy": focus,
            "answer": answer,
            "explanation": explanation,
            "followups": followups,
            "pitfalls": pitfalls,
            "origin": "reviewed-core",
            "source_ids": ["local-reviewed-bank"],
            "source_locations": [
                {
                    "path": path.relative_to(REPO_ROOT).as_posix(),
                    "heading": match.group(0).strip(),
                }
            ],
            "historical_references": [],
        }
        if module_id == "10":
            item["scenario"] = {
                "type": item["kind"],
                "prompt": title,
            }
        elif item["kind"] == "实操题":
            practice = MODULE_PRACTICE_SCENARIOS[module_id]
            item["scenario"] = {
                "type": "合成实操题",
                "background": practice["background"],
                "data": practice["data"],
                "task": title,
                "synthetic": True,
            }
        questions.append(item)
    return questions


def parse_outline(source_id: str, file_name: str) -> List[LegacyItem]:
    path = HISTORY_DIR / file_name
    section = "未分类"
    items: List[LegacyItem] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"^#{2,3}\s+(?:\d+[.、]?\s*)?(.+?)\s*$", line)
        if heading:
            candidate = clean_text(heading.group(1))
            section = "未分类" if candidate == "功能测试" else candidate
            continue
        match = OUTLINE_ITEM.match(line)
        if not match or section == "未分类":
            continue
        question = safe_question_text(match.group(2))
        items.append(
            LegacyItem(
                source_id=source_id,
                source_file=file_name,
                source_type="markdown-outline",
                index=len(items) + 1,
                section=section,
                question=question,
                answer_has_sensitive_claim=False,
            )
        )
    return items


def parse_legacy_items() -> List[LegacyItem]:
    all_items: List[LegacyItem] = []
    for source_id, file_name in HISTORY_FILES:
        all_items.extend(parse_outline(source_id, file_name))
    return all_items


def title_similarity(left: str, right: str) -> float:
    a = normalize_title(left)
    b = normalize_title(right)
    if not a or not b:
        return 0.0
    ratio = difflib.SequenceMatcher(None, a, b).ratio()
    if a in b or b in a:
        ratio = max(ratio, min(len(a), len(b)) / max(len(a), len(b)) + 0.18)
    return min(ratio, 1.0)


def map_legacy_items(
    items: Sequence[LegacyItem], questions: Sequence[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], Dict[str, List[str]]]:
    coverage: List[Dict[str, Any]] = []
    references: Dict[str, List[str]] = {question["id"]: [] for question in questions}
    for item in items:
        hinted_module = SECTION_MODULE_HINTS.get(item.section)
        candidates = [
            question
            for question in questions
            if not hinted_module or question["module_id"] == hinted_module
        ]
        if not candidates:
            candidates = list(questions)
        scored = sorted(
            (
                (title_similarity(item.question, question["title"]), question)
                for question in candidates
            ),
            key=lambda pair: pair[0],
            reverse=True,
        )
        best_score, best = scored[0]
        # Only a sufficiently similar intent is treated as a semantic mapping.
        # Lower-scoring results retain a review candidate for traceability, but
        # must not inflate coverage or pollute full-text aliases.
        if best_score >= 0.51:
            mapping_status = "strong-semantic-match"
            mapped_ids = [best["id"]]
            canonical_question_id: Optional[str] = best["id"]
            references[best["id"]].append(
                f"{item.source_id}-{item.index:03d}"
            )
        else:
            mapping_status = "candidate-assignment-review-required"
            mapped_ids = []
            canonical_question_id = None
        coverage_id = f"{item.source_id}-{item.index:03d}"
        answer_policy = "reviewed-answer-in-personal-latest-bank"
        record = {
            "id": coverage_id,
            "source_id": item.source_id,
            "source_file": item.source_file,
            "source_type": item.source_type,
            "source_index": item.index,
            "section": item.section,
            "question_intent": item.question,
            "mapping_status": mapping_status,
            "mapped_question_ids": mapped_ids,
            "canonical_question_id": canonical_question_id,
            "canonical_question_title": best["title"]
            if canonical_question_id
            else None,
            "canonical_module_id": best["module_id"]
            if canonical_question_id
            else None,
            "canonical_module_name": best["module_name"]
            if canonical_question_id
            else None,
            "review_candidate_question_id": best["id"],
            "review_candidate_question_title": best["title"],
            "review_candidate_module_id": best["module_id"],
            "review_candidate_module_name": best["module_name"],
            "best_match_score": round(best_score, 4),
            "review_recommended": mapping_status != "strong-semantic-match",
            "answer_policy": answer_policy,
            "privacy_note": "题目大纲只用于覆盖校验；答案使用个人整理最新版中的评审内容。",
        }
        validate_public_text(json.dumps(record, ensure_ascii=False), coverage_id)
        coverage.append(record)
    return coverage, references


def load_curated() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], str]:
    questions: List[Dict[str, Any]] = []
    sources: List[Dict[str, Any]] = []
    updated_dates: List[str] = []
    for file_name in CURATED_FILES:
        path = DATA_DIR / file_name
        if not path.exists() or not path.read_text(encoding="utf-8").strip():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            file_questions = payload
            file_sources: List[Dict[str, Any]] = []
            updated_at = ""
        elif isinstance(payload, dict):
            file_questions = payload.get("questions") or []
            file_sources = payload.get("sources") or []
            updated_at = str(payload.get("updated_at") or "")
        else:
            raise ValueError(f"{file_name} 顶层必须是对象或题目数组")
        if not isinstance(file_questions, list) or not isinstance(file_sources, list):
            raise ValueError(f"{file_name} 的 questions 和 sources 必须是数组")
        if file_name.startswith("xiaolincoding-") and file_name.endswith("-questions.json"):
            for question in file_questions:
                if isinstance(question, dict):
                    unknown_fields = set(question) - XIAOLINCODING_QUESTION_FIELDS
                    if unknown_fields:
                        raise ValueError(
                            f"{file_name} 的 {question.get('id') or '未命名题目'} "
                            f"含未声明字段：{sorted(unknown_fields)}"
                        )
                    scenario = question.get("scenario")
                    if scenario is not None and (
                        not isinstance(scenario, dict)
                        or scenario.get("synthetic") is not True
                    ):
                        raise ValueError(
                            f"{file_name} 的 {question.get('id') or '未命名题目'} "
                            "场景必须显式标记 synthetic=true"
                        )
                    question.setdefault("origin", "xiaolincoding-reviewed")
        questions.extend(file_questions)
        sources.extend(file_sources)
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", updated_at):
            updated_dates.append(updated_at)
    return questions, sources, max(updated_dates, default="")


def listify(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [clean_text(str(item)) for item in value if clean_text(str(item))]
    return [clean_text(str(value))]


def normalize_curated_question(
    raw: Dict[str, Any],
    index: int,
    module_names: Dict[str, str],
    generated_at: str,
) -> Dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError(f"curated questions[{index}] 必须是对象")
    module_id = str(raw.get("module_id") or "").zfill(2)
    title = clean_text(str(raw.get("title") or ""))
    if module_id not in module_names or not title:
        raise ValueError(f"curated questions[{index}] 缺少有效 module_id/title")
    digest = hashlib.sha1(f"{module_id}:{title}".encode("utf-8")).hexdigest()[:10]
    question_id = clean_text(str(raw.get("id") or f"curated-{module_id}-{digest}"))
    focus_value = raw.get("focus") or ""
    focus = "\n".join(listify(focus_value))
    answer_strategy = clean_text(str(raw.get("answer_strategy") or focus))
    answer = clean_text(str(raw.get("answer") or ""))
    explanation = clean_text(str(raw.get("explanation") or ""))
    if not focus or not answer or not explanation:
        raise ValueError(f"{question_id} 必须包含 focus、answer、explanation")
    followups = listify(raw.get("followups"))
    pitfalls = listify(raw.get("pitfalls"))
    source_ids = listify(raw.get("source_ids"))
    if not source_ids:
        raise ValueError(f"{question_id} 必须至少关联一个来源")
    has_related_ids = "related_question_ids" in raw
    has_deepening_rationale = "deepening_rationale" in raw
    if has_related_ids != has_deepening_rationale:
        raise ValueError(
            f"{question_id} 的 related_question_ids 与 deepening_rationale "
            "必须同时出现"
        )
    related_question_ids: List[str] = []
    deepening_rationale = ""
    if has_related_ids:
        raw_related_ids = raw["related_question_ids"]
        if not isinstance(raw_related_ids, list):
            raise ValueError(f"{question_id} 的 related_question_ids 必须是数组")
        related_question_ids = [
            clean_text(str(item))
            for item in raw_related_ids
            if isinstance(item, str) and clean_text(item)
        ]
        if (
            not 1 <= len(related_question_ids) <= 5
            or len(related_question_ids) != len(raw_related_ids)
            or len(set(related_question_ids)) != len(related_question_ids)
        ):
            raise ValueError(
                f"{question_id} 的 related_question_ids 必须包含 1–5 个唯一非空 ID"
            )
        deepening_rationale = clean_text(str(raw["deepening_rationale"]))
        if not 20 <= len(deepening_rationale) <= 300:
            raise ValueError(
                f"{question_id} 的 deepening_rationale 必须为 20–300 字"
            )
    combined = json.dumps(raw, ensure_ascii=False)
    validate_public_text(combined, question_id)
    level = str(raw.get("level") or "进阶")
    kind = str(raw.get("kind") or infer_kind(module_id, title))
    if level not in {"入门", "进阶", "高级"}:
        raise ValueError(f"{question_id} 的 level 无效：{level}")
    allowed_kinds = {"知识题", "场景题", "项目题", "行为题", "实操题"}
    if kind not in allowed_kinds:
        raise ValueError(f"{question_id} 的 kind 无效：{kind}")
    origin = clean_text(str(raw.get("origin") or "curated-2026"))
    if origin not in {
        "personal-latest-reviewed",
        "curated-2026",
        "supplemental-reviewed",
        "xiaolincoding-reviewed",
    }:
        raise ValueError(f"{question_id} 的 origin 无效：{origin}")
    roles = listify(raw.get("roles")) or MODULE_ROLES[module_id]
    unknown_roles = sorted(set(roles) - ALLOWED_ROLES)
    if unknown_roles:
        raise ValueError(f"{question_id} 含无效岗位角色：{unknown_roles}")
    item: Dict[str, Any] = {
        "id": question_id,
        "module_id": module_id,
        "module_name": clean_text(str(raw.get("module_name") or module_names[module_id])),
        "position": int(raw.get("position") or 10_000 + index),
        "title": title,
        "level": level,
        "kind": kind,
        "roles": roles,
        "tags": listify(raw.get("tags")) or infer_tags(module_names[module_id], title, combined),
        "focus": focus,
        "answer_strategy": answer_strategy,
        "answer": answer,
        "explanation": explanation,
        "followups": followups,
        "pitfalls": pitfalls,
        "origin": origin,
        "source_ids": source_ids,
        "source_locations": [],
        "historical_references": [],
        "updated_at": clean_text(str(raw.get("updated_at") or generated_at)),
    }
    if raw.get("scenario"):
        scenario = dict(raw["scenario"])
        scenario.pop("data_policy", None)
        item["scenario"] = scenario
    elif kind in {"场景题", "项目题", "行为题"}:
        item["scenario"] = {
            "type": kind,
            "prompt": title,
        }
    if related_question_ids:
        item["related_question_ids"] = related_question_ids
        item["deepening_rationale"] = deepening_rationale
    return item


def normalize_sources(
    curated_sources: Sequence[Dict[str, Any]], generated_at: str
) -> List[Dict[str, Any]]:
    sources: List[Dict[str, Any]] = [
        {
            "id": "local-reviewed-bank",
            "title": "本仓库已评审的十模块面试题库",
            "platform": "本地文档",
            "url": None,
            "accessed_at": generated_at,
            "usage": "正式题目与详细答案的统一合并落点。",
        },
        {
            "id": "personal-latest-outline",
            "title": "个人整理最新版题目大纲",
            "platform": "本地文档",
            "url": None,
            "accessed_at": generated_at,
            "usage": "用于逐题覆盖校验；详细答案使用个人整理最新版评审数据。",
        },
    ]
    seen = {source["id"] for source in sources}
    for index, raw in enumerate(curated_sources, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"curated sources[{index}] 必须是对象")
        source_id = clean_text(str(raw.get("id") or ""))
        if not source_id or source_id in seen:
            if source_id in seen:
                continue
            raise ValueError(f"curated sources[{index}] 缺少 id")
        source = {
            "id": source_id,
            "title": clean_text(str(raw.get("title") or source_id)),
            "platform": clean_text(str(raw.get("platform") or "公开来源")),
            "url": clean_text(str(raw.get("url") or "")) or None,
            "accessed_at": clean_text(str(raw.get("accessed_at") or generated_at)),
            "usage": clean_text(
                str(raw.get("note") or raw.get("usage") or "仅提炼岗位能力主题，不复制原文。")
            ),
        }
        validate_public_text(json.dumps(source, ensure_ascii=False), source_id)
        sources.append(source)
        seen.add(source_id)
    return sources


def ensure_source_references(
    questions: Sequence[Dict[str, Any]], sources: List[Dict[str, Any]], generated_at: str
) -> None:
    known = {source["id"] for source in sources}
    missing = sorted(
        {
            source_id
            for question in questions
            for source_id in question.get("source_ids", [])
            if source_id not in known
        }
    )
    if missing:
        raise ValueError(f"题目引用了未定义来源：{missing}")
    xiaolin_without_verification = sorted(
        question["id"]
        for question in questions
        if question.get("origin") == "xiaolincoding-reviewed"
        and not any(
            not source_id.startswith("xiaolincoding-")
            for source_id in question.get("source_ids", [])
        )
    )
    if xiaolin_without_verification:
        raise ValueError(
            "小林 Coding 新增题必须至少关联一个独立核验来源："
            f"{xiaolin_without_verification}"
        )


def build_payload(generated_at: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    modules = [
        {"id": module_id, "name": name, "source_file": file_name}
        for module_id, name, file_name in MODULE_FILES
    ]
    core_questions: List[Dict[str, Any]] = []
    for module_id, module_name, file_name in MODULE_FILES:
        core_questions.extend(parse_module_questions(module_id, module_name, file_name))
    if len(core_questions) != 172:
        raise ValueError(f"正式十模块预期 172 题，实际解析 {len(core_questions)} 题")

    curated_raw, curated_sources, curated_updated_at = load_curated()
    module_names = {module["id"]: module["name"] for module in modules}
    curated_questions = [
        normalize_curated_question(raw, index, module_names, generated_at)
        for index, raw in enumerate(curated_raw, start=1)
    ]

    ids: set[str] = set()
    normalized_titles: Dict[str, str] = {}
    questions: List[Dict[str, Any]] = []
    for question in [*core_questions, *curated_questions]:
        if question["id"] in ids:
            raise ValueError(f"重复题目 id：{question['id']}")
        normalized = normalize_title(question["title"])
        if question["origin"] != "reviewed-core" and normalized in normalized_titles:
            raise ValueError(
                f"curated 题目与已有题目标题重复：{question['title']} / {normalized_titles[normalized]}"
            )
        ids.add(question["id"])
        normalized_titles[normalized] = question["id"]
        questions.append(question)

    legacy_items = parse_legacy_items()
    coverage, references = map_legacy_items(legacy_items, questions)
    for question in questions:
        question["historical_references"] = references[question["id"]]
        question["updated_at"] = clean_text(str(question.get("updated_at") or generated_at))

    for question in questions:
        related_question_ids = question.get("related_question_ids", [])
        if question["id"] in related_question_ids:
            raise ValueError(f"{question['id']} 不能关联自身")
        missing_related_ids = sorted(set(related_question_ids) - ids)
        if missing_related_ids:
            raise ValueError(
                f"{question['id']} 关联了不存在的题目：{missing_related_ids}"
            )

    questions.sort(key=lambda item: (item["module_id"], item["position"], item["id"]))
    sources = normalize_sources(curated_sources, generated_at)
    ensure_source_references(questions, sources, generated_at)

    by_module = {
        module["id"]: sum(1 for question in questions if question["module_id"] == module["id"])
        for module in modules
    }
    by_origin = {
        origin: sum(1 for question in questions if question["origin"] == origin)
        for origin in sorted({question["origin"] for question in questions})
    }
    mapped_count = sum(bool(item["mapped_question_ids"]) for item in coverage)
    review_required_count = len(coverage) - mapped_count
    isolated_count = 0
    payload = {
        "schema_version": "1.0",
        "generated_at": generated_at,
        "curated_updated_at": curated_updated_at or None,
        "statistics": {
            "total_questions": len(questions),
            "reviewed_core_questions": len(core_questions),
            "curated_questions": len(curated_questions),
            "legacy_items": len(coverage),
            "legacy_strong_semantic_matches": mapped_count,
            "legacy_review_required": review_required_count,
            "legacy_verified_coverage_rate": round(mapped_count / len(coverage), 4)
            if coverage
            else 1.0,
            "legacy_isolated_answers": isolated_count,
            "by_module": by_module,
            "by_origin": by_origin,
        },
        "modules": modules,
        "sources": sources,
        "questions": questions,
    }
    coverage_payload = {
        "schema_version": "1.0",
        "generated_at": generated_at,
        "policy": {
            "purpose": "证明个人整理最新版大纲中的每道题均已解析并映射到已审校题库。",
            "answer_handling": "个人整理最新版评审数据是详细答案与答题思路的唯一来源。",
        },
        "statistics": {
            "total": len(coverage),
            "by_source": {
                source_id: sum(item["source_id"] == source_id for item in coverage)
                for source_id, _ in HISTORY_FILES
            },
            "strong_semantic_matches": sum(
                item["mapping_status"] == "strong-semantic-match"
                for item in coverage
            ),
            "candidate_assignments_review_required": sum(
                item["mapping_status"] == "candidate-assignment-review-required"
                for item in coverage
            ),
            "mapped_to_answer": mapped_count,
            "unmapped": review_required_count,
            "coverage_rate": round(mapped_count / len(coverage), 4)
            if coverage
            else 1.0,
            "isolated_answers": isolated_count,
        },
        "items": coverage,
    }
    validate_public_text(json.dumps(payload, ensure_ascii=False), "questions.json")
    validate_public_text(
        json.dumps(coverage_payload, ensure_ascii=False), "legacy-coverage.json"
    )
    return payload, coverage_payload


def render_json(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def default_generated_at() -> str:
    """Use the curated snapshot date so builds stay reproducible across machines."""
    path = DATA_DIR / "curated-2026.json"
    if path.exists():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            payload = {}
        if isinstance(payload, dict):
            updated_at = str(payload.get("updated_at") or "")
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", updated_at):
                return updated_at
    return date.today().isoformat()


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="构建软件测试面试题库数据")
    parser.add_argument(
        "--generated-at",
        default=default_generated_at(),
        help="构建日期，默认使用 curated-2026.json 的快照日期，格式 YYYY-MM-DD",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="只校验已生成文件是否与源文件一致，不写文件",
    )
    args = parser.parse_args(argv)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.generated_at):
        parser.error("--generated-at 必须是 YYYY-MM-DD")

    payload, coverage = build_payload(args.generated_at)
    outputs = {
        DATA_DIR / "questions.json": render_json(payload),
        DATA_DIR / "legacy-coverage.json": render_json(coverage),
    }
    if args.check:
        stale = [
            str(path.relative_to(REPO_ROOT))
            for path, expected in outputs.items()
            if not path.exists() or path.read_text(encoding="utf-8") != expected
        ]
        if stale:
            print("以下生成文件已过期：", *stale, sep="\n- ", file=sys.stderr)
            return 1
    else:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        for path, content in outputs.items():
            path.write_text(content, encoding="utf-8")
    stats = payload["statistics"]
    print(
        "构建完成："
        f"正式题 {stats['reviewed_core_questions']}，"
        f"最新增补 {stats['curated_questions']}，"
        f"历史逐项覆盖 {stats['legacy_items']}。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
