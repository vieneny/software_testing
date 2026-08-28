from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest


MODULE_PATH = Path(__file__).with_name("人工智能回答评测器.py")
SPEC = importlib.util.spec_from_file_location("deterministic_evaluator", MODULE_PATH)
assert SPEC and SPEC.loader
EVALUATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = EVALUATOR
SPEC.loader.exec_module(EVALUATOR)


@pytest.mark.ai
def test_public_fixture_dataset_passes_deterministic_gate() -> None:
    records = EVALUATOR.read_jsonl(Path(__file__).with_name("人工智能评测数据集.jsonl"))
    results = EVALUATOR.evaluate_dataset(records)

    assert len(results) >= 5
    assert all(result.passed for result in results)


@pytest.mark.ai
def test_forbidden_term_is_reported() -> None:
    result = EVALUATOR.evaluate_case(
        {
            "id": "synthetic_failure",
            "category": "security",
            "candidate_output": "这里错误地包含 DEMO_SECRET",
            "required_terms": ["错误"],
            "forbidden_terms": ["DEMO_SECRET"],
        }
    )

    assert result.passed is False
    assert result.found_forbidden_terms == ["DEMO_SECRET"]
