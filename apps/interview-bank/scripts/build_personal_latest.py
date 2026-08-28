#!/usr/bin/env python3
"""Validate and normalize the personal latest reviewed interview bank."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
BANK_ROOT = REPO_ROOT / "apps" / "interview-bank"
DATA_PATH = BANK_ROOT / "data" / "personal-latest-reviewed.json"
OUTLINE_PATH = (
    REPO_ROOT
    / "docs"
    / "08-求职备考"
    / "04-面试题库"
    / "历史资料"
    / "个人整理最新版题库.md"
)
COMMIT_SHA = "d0a8cfde75fe43c3abd7919e91c72bb7f3c15823"
UPDATED_AT = "2026-08-28"
QUESTION_COUNT = 160
REQUIRED_TEXT_FIELDS = ("answer_strategy", "answer", "explanation")
REQUIRED_LIST_FIELDS = ("followups", "pitfalls")


def compact_length(value: str) -> int:
    return len(re.sub(r"\s+", "", value))


def safe_question(value: str) -> str:
    replacements = {
        "你们原来项目": "你选择的公开或虚构练习项目",
        "你们xx项目": "该公开或虚构练习项目",
        "上一家公司": "过往经历（仅按本人真实情况）",
        "公司的产品": "虚构产品",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value.strip()


def parse_outline() -> list[tuple[str, str]]:
    section = ""
    questions: list[tuple[str, str]] = []
    for line in OUTLINE_PATH.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"^#{2,3}\s+(.+?)\s*$", line)
        if heading:
            candidate = heading.group(1).strip()
            section = "" if candidate == "功能测试" else candidate
            continue
        match = re.match(r"^\s*\d+\.\s+(.+?)\s*$", line)
        if match and section:
            questions.append((section, safe_question(match.group(1))))
    if len(questions) != QUESTION_COUNT:
        raise ValueError(
            f"个人整理最新版大纲预期 {QUESTION_COUNT} 题，实际 {len(questions)} 题"
        )
    return questions


def title_question(title: str) -> str:
    return re.sub(
        r"^个人整理最新版\s*\d{3}\s*[|｜]\s*",
        "",
        title,
    ).strip()


def normalize_question(
    raw: dict[str, Any], index: int, section: str, outline_question: str
) -> dict[str, Any]:
    expected_id = f"legacy-2025-{index:03d}"
    if raw.get("id") != expected_id:
        raise ValueError(f"第 {index} 题 ID 应为 {expected_id}，实际为 {raw.get('id')}")
    if title_question(str(raw.get("title") or "")) != outline_question:
        raise ValueError(
            f"{expected_id} 与大纲题意不一致：{raw.get('title')} / {outline_question}"
        )
    for field in REQUIRED_TEXT_FIELDS:
        if not str(raw.get(field) or "").strip():
            raise ValueError(f"{expected_id} 缺少 {field}")
    for field in REQUIRED_LIST_FIELDS:
        value = raw.get(field)
        if not isinstance(value, list) or not any(str(item).strip() for item in value):
            raise ValueError(f"{expected_id} 缺少 {field}")
    if compact_length(str(raw["answer"])) < 120:
        raise ValueError(f"{expected_id} 的 answer 少于 120 个非空白字符")
    if compact_length(str(raw["answer_strategy"])) < 120:
        raise ValueError(f"{expected_id} 的 answer_strategy 少于 120 个非空白字符")

    item = dict(raw)
    item["origin"] = "personal-latest-reviewed"
    item["title"] = f"个人整理最新版 {index:03d}｜{outline_question}"
    item["tags"] = [section.replace(" & ", "与"), "个人整理最新版", "面试题整理"]
    if "主题线索" in str(item["explanation"]):
        item["explanation"] = (
            "本答案已经补入适用边界、执行步骤和验证证据。面试回答需要把概念转成"
            "可执行过程，并区分需求事实、个人真实经历与练习场景；无法核验的数据和"
            "成果不能写进答案。"
        )
    item["pitfalls"] = [
        (
            "只背概念条目，不说明适用边界、执行证据和风险。"
            if "条目" in str(value) and "适用边界" in str(value)
            else str(value)
        )
        for value in item["pitfalls"]
    ]
    item["source_ids"] = ["personal-latest-reviewed"]
    item["updated_at"] = UPDATED_AT
    return item


def build_payload() -> dict[str, Any]:
    source = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    raw_questions = source.get("questions")
    if not isinstance(raw_questions, list) or len(raw_questions) != QUESTION_COUNT:
        raise ValueError(
            f"已审校答案预期 {QUESTION_COUNT} 题，实际 "
            f"{len(raw_questions) if isinstance(raw_questions, list) else '无效'} 题"
        )
    outline = parse_outline()
    questions = [
        normalize_question(raw, index, *outline[index - 1])
        for index, raw in enumerate(raw_questions, start=1)
    ]
    return {
        "schema_version": "1.0",
        "updated_at": UPDATED_AT,
        "collection": {
            "id": "personal-latest-reviewed",
            "title": "个人整理最新版软件测试面试题（含详细答案与答题思路）",
            "source_commit": COMMIT_SHA,
            "question_count": QUESTION_COUNT,
            "answer_policy": "个人整理最新版中的已审校内容是唯一答案源。",
        },
        "sources": [
            {
                "id": "personal-latest-reviewed",
                "title": "个人整理最新版题库",
                "url": None,
                "platform": "本地整理",
                "accessed_at": UPDATED_AT,
                "note": "题目、详细答案与答题思路均来自当前已审校版本。",
            }
        ],
        "questions": questions,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if DATA_PATH.read_text(encoding="utf-8") != rendered:
            print(f"{DATA_PATH} 不是最新生成结果", file=sys.stderr)
            return 1
        print(f"个人整理最新版校验通过：{QUESTION_COUNT} 题")
        return 0
    DATA_PATH.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"个人整理最新版整理完成：{QUESTION_COUNT} 题")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
