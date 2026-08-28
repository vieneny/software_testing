#!/usr/bin/env python3
"""Run deterministic, per-question quality gates for the generated interview bank."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any


BANK_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BANK = BANK_ROOT / "data" / "questions.json"
DEFAULT_REPORT = BANK_ROOT / "data" / "题库逐题质量审计.json"
REVIEW_FIELDS = (
    "title",
    "focus",
    "answer_strategy",
    "scenario",
    "answer",
    "explanation",
    "followups",
    "pitfalls",
    "deepening_rationale",
    "historical_reference",
    "historical_references",
)
MARKDOWN_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]+\)")
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\([^)]+\)")
DATE_VALUE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FORBIDDEN_PUBLIC_TEXT = (
    "\u5ea6\u5c0f\u6ee1",
    "生产环境脱敏数据",
    "真实公司项目",
    "个人经验：",
)
ABSOLUTE_LANGUAGE = (
    "绝对没有缺陷",
    "一定不会",
    "永远不会",
    "完全保证",
    "百分之百保证",
)


def normalized_length(value: str) -> int:
    return len(re.sub(r"\s+", "", value))


def display_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def valid_iso_date(value: Any) -> bool:
    text = str(value)
    if not DATE_VALUE.fullmatch(text):
        return False
    try:
        date.fromisoformat(text)
    except ValueError:
        return False
    return True


def stable_hash(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def validate_question(
    question: dict[str, Any],
    known_source_ids: set[str],
) -> tuple[dict[str, bool], list[str]]:
    all_reviewed_text = "\n".join(
        display_text(question.get(field, ""))
        for field in (
            "title",
            "focus",
            "answer_strategy",
            "scenario",
            "answer",
            "explanation",
            "followups",
            "pitfalls",
            "deepening_rationale",
            "historical_reference",
            "historical_references",
        )
    )
    source_ids = question.get("source_ids", [])
    answer = str(question.get("answer", "")).strip()
    answer_strategy = str(question.get("answer_strategy", "")).strip()
    explanation = str(question.get("explanation", "")).strip()
    checks = {
        "required_fields_complete": all(
            question.get(field) not in (None, "", [])
            for field in (
                "id",
                "module_id",
                "module_name",
                "title",
                "level",
                "kind",
                "roles",
                "tags",
                "focus",
                "answer_strategy",
                "answer",
                "explanation",
                "followups",
                "pitfalls",
                "origin",
                "source_ids",
                "updated_at",
            )
        ),
        "answer_has_working_depth": normalized_length(answer) >= 120,
        "answer_strategy_present": bool(answer_strategy),
        "reviewed_2025_strategy_has_working_depth": (
            question.get("origin") != "legacy-2025-reviewed"
            or normalized_length(answer_strategy) >= 120
        ),
        "explanation_has_reasoning_depth": normalized_length(explanation) >= 60,
        "answer_and_explanation_are_distinct": answer != explanation,
        "followups_and_pitfalls_present": bool(question.get("followups"))
        and bool(question.get("pitfalls")),
        "practice_scenario_present": (
            question.get("kind")
            not in {"实操题", "场景题", "项目题", "行为题"}
            or bool(question.get("scenario"))
        ),
        "code_fences_balanced": answer.count("```") % 2 == 0
        and explanation.count("```") % 2 == 0,
        "no_markdown_images": MARKDOWN_IMAGE.search(all_reviewed_text) is None,
        "no_forbidden_company_content": not any(
            value in all_reviewed_text for value in FORBIDDEN_PUBLIC_TEXT
        ),
        "sources_resolve": bool(source_ids)
        and all(source_id in known_source_ids for source_id in source_ids),
        "updated_at_valid": valid_iso_date(question.get("updated_at", "")),
    }
    warnings: list[str] = []
    if MARKDOWN_LINK.search(all_reviewed_text):
        warnings.append("正文含 Markdown 链接；前端会将其降级为不可点击文本")
    matched_absolutes = sorted(
        phrase for phrase in ABSOLUTE_LANGUAGE if phrase in all_reviewed_text
    )
    if matched_absolutes:
        warnings.append(
            f"发现绝对化措辞，需结合上下文人工确认：{'、'.join(matched_absolutes)}"
        )
    return checks, warnings


def build_report(bank_path: Path) -> tuple[dict[str, Any], list[str]]:
    payload = json.loads(bank_path.read_text(encoding="utf-8"))
    questions = payload.get("questions", [])
    sources = payload.get("sources", [])
    if not isinstance(questions, list) or not isinstance(sources, list):
        raise ValueError("questions.json 缺少 questions 或 sources 数组")

    source_ids = {
        str(source["id"])
        for source in sources
        if isinstance(source, dict) and source.get("id")
    }
    seen_ids: set[str] = set()
    duplicate_ids: set[str] = set()
    module_totals: Counter[str] = Counter()
    module_passed: Counter[str] = Counter()
    origin_totals: Counter[str] = Counter()
    failed_items: list[str] = []
    warning_items: list[str] = []
    entries: list[dict[str, Any]] = []
    titles_by_module: dict[str, set[str]] = defaultdict(set)

    for question in questions:
        question_id = str(question.get("id", ""))
        module_id = str(question.get("module_id", ""))
        origin = str(question.get("origin", ""))
        if question_id in seen_ids:
            duplicate_ids.add(question_id)
        seen_ids.add(question_id)

        normalized_title = re.sub(r"\s+", "", str(question.get("title", ""))).lower()
        title_unique = normalized_title not in titles_by_module[module_id]
        titles_by_module[module_id].add(normalized_title)

        checks, warnings = validate_question(question, source_ids)
        checks["title_unique_within_module"] = title_unique
        status = "passed" if all(checks.values()) else "failed"
        module_totals[module_id] += 1
        origin_totals[origin] += 1
        if status == "passed":
            module_passed[module_id] += 1
        else:
            failed_checks = [name for name, passed in checks.items() if not passed]
            failed_items.append(f"{question_id}: {', '.join(failed_checks)}")
        if warnings:
            warning_items.append(f"{question_id}: {'；'.join(warnings)}")

        reviewed_payload = {
            field: question.get(field)
            for field in REVIEW_FIELDS
        }
        entries.append(
            {
                "id": question_id,
                "module_id": module_id,
                "origin": origin,
                "title": question.get("title", ""),
                "content_hash": stable_hash(reviewed_payload),
                "answer_chars": normalized_length(str(question.get("answer", ""))),
                "answer_strategy_chars": normalized_length(
                    str(question.get("answer_strategy", ""))
                ),
                "explanation_chars": normalized_length(
                    str(question.get("explanation", ""))
                ),
                "automated_checks": checks,
                "warnings": warnings,
                "status": status,
            }
        )

    max_updated_at = max(
        (str(question.get("updated_at", "")) for question in questions),
        default="",
    )
    report = {
        "schema_version": "1.0",
        "audited_at": max_updated_at,
        "bank_content_hash": stable_hash(questions),
        "scope": "逐题检查生成题库的结构完整性、答案深度、解析深度、来源可追溯性、图片策略与代码围栏。",
        "accuracy_boundary": "自动化门禁不能替代技术事实的人工审校；人工审校方法与变更摘要见面试题库质量审校说明。",
        "thresholds": {
            "answer_non_whitespace_characters_min": 120,
            "reviewed_2025_answer_strategy_non_whitespace_characters_min": 120,
            "explanation_non_whitespace_characters_min": 60,
        },
        "summary": {
            "question_count": len(questions),
            "passed": len(questions) - len(failed_items),
            "failed": len(failed_items),
            "warnings": len(warning_items),
            "duplicate_ids": sorted(duplicate_ids),
            "module_count": len(module_totals),
        },
        "modules": [
            {
                "module_id": module_id,
                "total": module_totals[module_id],
                "passed": module_passed[module_id],
                "failed": module_totals[module_id] - module_passed[module_id],
            }
            for module_id in sorted(module_totals)
        ],
        "origins": [
            {"origin": origin, "total": origin_totals[origin]}
            for origin in sorted(origin_totals)
        ],
        "questions": entries,
    }
    problems = [
        *(f"重复题目 ID：{item}" for item in sorted(duplicate_ids)),
        *failed_items,
    ]
    return report, problems


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bank", type=Path, default=DEFAULT_BANK)
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--write-report", type=Path, nargs="?", const=DEFAULT_REPORT)
    output.add_argument("--check-report", type=Path, nargs="?", const=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report, problems = build_report(args.bank)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"题库质量审计无法运行：{error}", file=sys.stderr)
        return 2

    if args.write_report:
        args.write_report.parent.mkdir(parents=True, exist_ok=True)
        args.write_report.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"已写入逐题质量报告：{args.write_report}")
    elif args.check_report:
        try:
            expected = json.loads(args.check_report.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            print(f"逐题质量报告不可读：{error}", file=sys.stderr)
            return 2
        if expected != report:
            print(
                "逐题质量报告与当前题库不一致；请重新运行 "
                "audit_question_quality.py --write-report。",
                file=sys.stderr,
            )
            return 1

    summary = report["summary"]
    print(
        "题库逐题质量门禁："
        f"{summary['passed']}/{summary['question_count']} 通过，"
        f"{summary['failed']} 失败，{summary['warnings']} 条人工复核提示。"
    )
    if problems:
        print("\n".join(f"- {problem}" for problem in problems), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
