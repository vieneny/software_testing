from __future__ import annotations

import importlib.util
from pathlib import Path


BANK_DIR = Path(__file__).resolve().parents[2]
SCRIPT_PATH = BANK_DIR / "scripts" / "audit_question_quality.py"
SPEC = importlib.util.spec_from_file_location("audit_question_quality", SCRIPT_PATH)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def valid_question() -> dict:
    return {
        "id": "quality-gate-example",
        "module_id": "02",
        "module_name": "功能测试与用例设计",
        "title": "如何测试一个合成审批流程？",
        "level": "进阶",
        "kind": "场景题",
        "roles": ["软件测试"],
        "tags": ["状态机"],
        "focus": "状态、权限、并发与审计证据",
        "scenario": {
            "background": "从零构造的审批系统",
            "task": "验证合法和非法状态迁移",
            "synthetic": True,
        },
        "answer": "先建立状态、事件、角色和守卫条件矩阵，再覆盖合法迁移、非法迁移、并发冲突与重复请求。接口、数据库和审计记录要围绕同一业务标识交叉核对；失败时保留业务码、版本号和脱敏日志。对每条迁移记录前置状态、触发事件、预期状态和副作用，并用版本号制造竞争。最后写明未测范围、环境限制和残余风险，由有权限的人决定是否接受。",
        "explanation": "状态机测试把零散按钮转换为可审计模型。状态覆盖只能说明每个状态出现过，迁移覆盖才能检查边是否正确；权限、幂等和审计属于跨迁移不变量，需要在并发与重试下单独验证。",
        "followups": ["如何验证两个操作同时发生？"],
        "pitfalls": ["只测正常按钮路径。"],
        "origin": "curated-2026",
        "source_ids": ["official-source"],
        "deepening_rationale": "",
        "historical_references": [],
        "updated_at": "2026-07-29",
    }


def test_privacy_and_image_checks_cover_every_displayed_prose_field() -> None:
    question = valid_question()
    checks, _ = AUDIT.validate_question(question, {"official-source"})
    assert all(checks.values())

    question["scenario"]["background"] = "真实公司项目"
    checks, _ = AUDIT.validate_question(question, {"official-source"})
    assert checks["no_forbidden_company_content"] is False

    question = valid_question()
    question["deepening_rationale"] = "![内部图](https://example.invalid/a.png)"
    checks, _ = AUDIT.validate_question(question, {"official-source"})
    assert checks["no_markdown_images"] is False

    question = valid_question()
    question["historical_references"] = ["生产环境脱敏数据"]
    checks, _ = AUDIT.validate_question(question, {"official-source"})
    assert checks["no_forbidden_company_content"] is False


def test_updated_at_must_be_a_real_calendar_date() -> None:
    question = valid_question()
    question["updated_at"] = "2026-99-99"
    checks, _ = AUDIT.validate_question(question, {"official-source"})
    assert checks["updated_at_valid"] is False
