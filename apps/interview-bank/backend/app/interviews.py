"""Mock interview templates and deterministic question selection."""

from __future__ import annotations

import random
from typing import Any


INTERVIEW_TEMPLATES: list[dict[str, Any]] = [
    {
        "id": "quick",
        "name": "20 分钟快速热身",
        "description": "基础、接口、自动化与场景各抽一部分，适合每日口述。",
        "default_count": 6,
        "minutes": 20,
        "module_ids": ["01", "02", "04", "05", "06", "10"],
    },
    {
        "id": "standard",
        "name": "45 分钟标准技术面",
        "description": "覆盖基础、功能、网络接口、自动化、性能、工程化、AI 与场景。",
        "default_count": 10,
        "minutes": 45,
        "module_ids": ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10"],
    },
    {
        "id": "full",
        "name": "90 分钟全流程模拟",
        "description": "技术基础、项目深挖、场景分析、AI 测试和行为题的完整组合。",
        "default_count": 16,
        "minutes": 90,
        "module_ids": ["10", "01", "02", "03", "04", "05", "06", "07", "08", "09"],
    },
    {
        "id": "automation",
        "name": "自动化测试专项",
        "description": "接口自动化、Web/移动端 UI 自动化及 CI 质量工程。",
        "default_count": 10,
        "minutes": 50,
        "module_ids": ["04", "05", "06", "08", "10"],
    },
    {
        "id": "ai-testing",
        "name": "AI 测试与测试开发专项",
        "description": "LLM、RAG、Agent、评测平台与 AI 提效场景。",
        "default_count": 10,
        "minutes": 55,
        "module_ids": ["09", "05", "07", "08", "10"],
    },
]

TARGET_ROLE_GROUPS: dict[str, list[str]] = {
    "软件测试工程师": ["软件测试", "功能测试", "接口测试", "移动端测试", "安全测试"],
    "自动化测试工程师": ["自动化测试", "接口自动化", "Web自动化", "移动端自动化"],
    "测试开发工程师": ["测试开发", "质量工程"],
    "AI 测试工程师": ["AI测试", "大模型评测", "数据评测"],
    "性能测试工程师": ["性能测试", "稳定性测试", "SRE"],
}


def template_by_id(template_id: str) -> dict[str, Any] | None:
    return next(
        (template for template in INTERVIEW_TEMPLATES if template["id"] == template_id),
        None,
    )


def select_questions(
    questions: list[dict[str, Any]],
    *,
    module_ids: list[str],
    count: int,
    level: str | None,
    seed: int,
    role_names: list[str] | None = None,
) -> list[str]:
    rng = random.Random(seed)
    accepted_roles = set(role_names or [])
    buckets: dict[str, list[dict[str, Any]]] = {}
    for module_id in module_ids:
        bucket = [
            question
            for question in questions
            if question["module_id"] == module_id
            and (not level or question["level"] == level)
            and (
                not accepted_roles
                or accepted_roles.intersection(question.get("roles", []))
            )
        ]
        rng.shuffle(bucket)
        buckets[module_id] = bucket

    selected: list[dict[str, Any]] = []
    # Round-robin prevents a random pool from losing entire interview dimensions.
    while len(selected) < count:
        added = False
        for module_id in module_ids:
            if buckets[module_id] and len(selected) < count:
                selected.append(buckets[module_id].pop())
                added = True
        if not added:
            break
    return [question["id"] for question in selected]
