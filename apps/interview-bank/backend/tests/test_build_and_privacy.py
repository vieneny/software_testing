from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
BANK_DIR = BACKEND_DIR.parent
REPO_ROOT = BANK_DIR.parents[1]
DATA_DIR = BANK_DIR / "data"


def load(name: str) -> dict:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def test_generated_bank_counts_and_required_answer_fields() -> None:
    payload = load("questions.json")
    questions = payload["questions"]
    assert len(questions) == 310
    assert payload["statistics"]["reviewed_core_questions"] == 172
    assert payload["statistics"]["curated_questions"] == 138
    assert payload["statistics"]["by_origin"] == {
        "curated-2026": 24,
        "reviewed-core": 172,
        "xiaolincoding-reviewed": 62,
        "supplemental-reviewed": 52,
    }
    assert len({question["id"] for question in questions}) == len(questions)
    assert {question["module_id"] for question in questions} == {
        f"{index:02d}" for index in range(1, 11)
    }
    for question in questions:
        assert question["title"]
        assert question["focus"]
        assert question["answer"]
        assert question["explanation"]
        assert question["level"] in {"入门", "进阶", "高级"}
        assert question["kind"] in {"知识题", "场景题", "项目题", "行为题", "实操题"}
        if question["kind"] in {"场景题", "项目题", "行为题", "实操题"}:
            assert question.get("scenario")


def test_xiaolincoding_raw_questions_follow_the_reviewed_contract() -> None:
    allowed_fields = {
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
    allowed_roles = {
        "Web自动化",
        "功能测试",
        "安全测试",
        "性能测试",
        "接口测试",
        "接口自动化",
        "测试开发",
        "移动端测试",
        "移动端自动化",
        "自动化测试",
        "质量工程",
        "软件测试",
    }
    files = (
        "xiaolincoding-business-questions.json",
        "xiaolincoding-automation-questions.json",
        "xiaolincoding-performance-questions.json",
    )
    for file_name in files:
        for question in load(file_name)["questions"]:
            assert set(question) <= allowed_fields
            assert question["roles"]
            assert set(question["roles"]) <= allowed_roles
            assert question["source_ids"]
            scenario = question.get("scenario")
            if scenario is not None:
                assert isinstance(scenario, dict)
                assert scenario.get("synthetic") is True


def test_semantic_deepening_links_are_explicit_and_valid() -> None:
    raw_questions = {
        question["id"]: question
        for question in load("xiaolincoding-automation-questions.json")["questions"]
    }
    generated_questions = {
        question["id"]: question
        for question in load("questions.json")["questions"]
    }
    expected = {
        "xiaolin-automation-restassured-assertion-depth": ["core-05-14"],
        "xiaolin-automation-java-api-module-architecture": ["core-05-12"],
        "xiaolin-automation-retry-governance-java": ["core-05-16"],
    }
    for question_id, related_ids in expected.items():
        raw = raw_questions[question_id]
        generated = generated_questions[question_id]
        assert raw["related_question_ids"] == related_ids
        assert generated["related_question_ids"] == related_ids
        assert generated["deepening_rationale"] == raw["deepening_rationale"]
        assert 20 <= len(generated["deepening_rationale"]) <= 300
        assert len(set(related_ids)) == len(related_ids)
        assert question_id not in related_ids
        assert set(related_ids) <= generated_questions.keys()


def test_generated_answers_preserve_fenced_code_indentation() -> None:
    questions = {
        question["id"]: question
        for question in load("questions.json")["questions"]
    }
    answer = questions["xiaolin-automation-restassured-spec-filter"]["answer"]
    assert "\n    URI baseUri, String token, Filter sanitizedEvidenceFilter)" in answer
    assert "\n      .setBaseUri(baseUri.toString())" in answer


def test_module_appendices_do_not_leak_into_the_last_core_question() -> None:
    questions = load("questions.json")["questions"]
    core_questions = [
        question for question in questions if question["origin"] == "reviewed-core"
    ]
    for question in core_questions:
        reviewed_text = "\n".join(
            [
                question["answer"],
                question["explanation"],
                *question["followups"],
                *question["pitfalls"],
            ]
        )
        assert "\n## " not in reviewed_text
        assert "## 公开参考" not in reviewed_text
        assert "## 版本敏感点" not in reviewed_text


def test_every_legacy_item_has_a_traceable_disposition() -> None:
    coverage = load("legacy-coverage.json")
    assert coverage["statistics"]["total"] == 495
    assert coverage["statistics"]["by_source"] == {
        "outline-draft": 175,
        "outline-revision": 160,
        "answer-draft": 160,
    }
    assert len(coverage["items"]) == 495
    assert len({item["id"] for item in coverage["items"]}) == 495
    assert coverage["statistics"]["strong_semantic_matches"] == 40
    assert coverage["statistics"]["candidate_assignments_review_required"] == 455
    assert coverage["statistics"]["mapped_to_answer"] == 40
    assert coverage["statistics"]["unmapped"] == 455
    assert coverage["statistics"]["coverage_rate"] == 0.0808
    for item in coverage["items"]:
        assert item["question_intent"]
        assert item["mapping_status"] in {
            "strong-semantic-match",
            "candidate-assignment-review-required",
        }
        if item["mapping_status"] == "strong-semantic-match":
            assert len(item["mapped_question_ids"]) == 1
            assert item["canonical_question_id"] == item["mapped_question_ids"][0]
            assert item["canonical_question_title"]
            assert item["canonical_module_id"] in {
                f"{index:02d}" for index in range(1, 11)
            }
            assert item["review_recommended"] is False
        else:
            assert item["mapped_question_ids"] == []
            assert item["canonical_question_id"] is None
            assert item["canonical_question_title"] is None
            assert item["canonical_module_id"] is None
            assert item["review_candidate_question_id"]
            assert item["review_candidate_module_id"] in {
                f"{index:02d}" for index in range(1, 11)
            }
            assert item["review_recommended"] is True
        assert item["answer_policy"] in {
            "legacy-answer-isolated-personal-or-project-claim",
            "legacy-answer-not-published-use-reviewed-answer",
        }
        assert "answer" not in item

    expected_modules = {
        "测试理论": "01",
        "测试思维 & 场景": "10",
        "测试思维与场景": "10",
        "项目相关": "10",
        "测试用例设计": "02",
        "测试管理": "08",
        "抓包与网络协议": "04",
        "职业规划": "10",
    }
    for item in coverage["items"]:
        if item["section"] in expected_modules:
            effective_module_id = (
                item["canonical_module_id"]
                or item["review_candidate_module_id"]
            )
            assert effective_module_id == expected_modules[item["section"]]


def test_generated_public_artifacts_contain_no_quarantined_text() -> None:
    artifact_names = [
        "questions.json",
        "legacy-coverage.json",
        "supplemental-backend-questions.json",
        "supplemental-ui-performance-questions.json",
        "supplemental-interview-questions.json",
        "supplemental-sources.json",
        "xiaolincoding-business-questions.json",
        "xiaolincoding-automation-questions.json",
        "xiaolincoding-performance-questions.json",
        "xiaolincoding-sources.json",
        "xiaolincoding-coverage.json",
    ]
    combined = "\n".join(
        (DATA_DIR / name).read_text(encoding="utf-8")
        for name in artifact_names
        if (DATA_DIR / name).exists()
    )
    forbidden = (
        "\u5ea6\u5c0f\u6ee1",
        "\u751f\u4ea7\u73af\u5883\u8131\u654f\u6570\u636e",
        "\u771f\u5b9e\u516c\u53f8\u9879\u76ee",
        "\u4e2a\u4eba\u7ecf\u9a8c\uff1a",
    )
    assert not [term for term in forbidden if term in combined]
    assert "legacy-answer-isolated-personal-or-project-claim" in combined


def test_curated_sources_are_traceable() -> None:
    payload = load("questions.json")
    sources = {source["id"]: source for source in payload["sources"]}
    assert len(sources) == 100
    used = {
        source_id
        for question in payload["questions"]
        for source_id in question["source_ids"]
    }
    assert used <= sources.keys()
    xiaolin_questions = [
        question
        for question in payload["questions"]
        if question["origin"] == "xiaolincoding-reviewed"
    ]
    assert all(
        any(not source_id.startswith("xiaolincoding-") for source_id in question["source_ids"])
        for question in xiaolin_questions
    )
    public = [source for source in sources.values() if source["url"]]
    assert len(public) == 98
    assert all(source["url"].startswith("https://") for source in public)
    assert all(source["accessed_at"] for source in public)


def test_build_outputs_are_current() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(BANK_DIR / "scripts" / "build_bank.py"),
            "--generated-at",
            "2026-07-29",
            "--check",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
