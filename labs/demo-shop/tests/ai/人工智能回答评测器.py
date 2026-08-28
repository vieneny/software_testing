"""A deterministic baseline evaluator for synthetic LLM output fixtures.

This script does not call a model or external service. It teaches dataset
versioning, explicit criteria, per-case diagnostics and CI thresholds before
learners introduce probabilistic graders.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_DATASET = Path(__file__).with_name("人工智能评测数据集.jsonl")


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    category: str
    passed: bool
    score: float
    missing_terms: list[str]
    found_forbidden_terms: list[str]


def read_jsonl(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    with path.open(encoding="utf-8") as dataset_file:
        for line_number, raw_line in enumerate(dataset_file, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid JSON on line {line_number}: {error}") from error
            records.append(record)
    if not records:
        raise ValueError("dataset is empty")
    return records


def evaluate_case(record: dict[str, object]) -> CaseResult:
    case_id = str(record["id"])
    category = str(record["category"])
    output = str(record["candidate_output"]).casefold()
    required_terms = [str(term) for term in record.get("required_terms", [])]
    forbidden_terms = [str(term) for term in record.get("forbidden_terms", [])]

    missing_terms = [term for term in required_terms if term.casefold() not in output]
    found_forbidden_terms = [
        term for term in forbidden_terms if term.casefold() in output
    ]
    total_checks = len(required_terms) + len(forbidden_terms)
    passed_checks = total_checks - len(missing_terms) - len(found_forbidden_terms)
    score = passed_checks / total_checks if total_checks else 0.0

    return CaseResult(
        case_id=case_id,
        category=category,
        passed=score == 1.0 and total_checks > 0,
        score=round(score, 4),
        missing_terms=missing_terms,
        found_forbidden_terms=found_forbidden_terms,
    )


def evaluate_dataset(records: Iterable[dict[str, object]]) -> list[CaseResult]:
    return [evaluate_case(record) for record in records]


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate synthetic response fixtures")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument(
        "--pass-rate", type=float, default=1.0, help="Required case pass rate, 0..1"
    )
    args = parser.parse_args()
    if not 0 <= args.pass_rate <= 1:
        parser.error("--pass-rate must be between 0 and 1")

    results = evaluate_dataset(read_jsonl(args.dataset))
    passed_count = sum(result.passed for result in results)
    pass_rate = passed_count / len(results)
    summary = {
        "dataset": str(args.dataset),
        "case_count": len(results),
        "passed_count": passed_count,
        "pass_rate": round(pass_rate, 4),
        "required_pass_rate": args.pass_rate,
        "results": [asdict(result) for result in results],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if pass_rate >= args.pass_rate else 1


if __name__ == "__main__":
    raise SystemExit(main())
