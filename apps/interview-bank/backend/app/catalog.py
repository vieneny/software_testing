"""Read-only repository over generated interview-bank JSON artifacts."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


class CatalogError(RuntimeError):
    """Raised when generated data is missing or malformed."""


def _read_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CatalogError(f"缺少生成数据：{path}") from exc
    except json.JSONDecodeError as exc:
        raise CatalogError(f"生成数据不是有效 JSON：{path}") from exc
    if not isinstance(payload, dict):
        raise CatalogError(f"生成数据顶层必须是对象：{path}")
    return payload


def _is_ordered_subsequence(needle: str, haystack: str) -> bool:
    """Allow short Chinese searches such as “音频上传” to span title wording.

    Exact substring matching remains the primary rule.  The ordered fallback is
    intentionally limited to short CJK queries so long prose does not produce
    surprising fuzzy matches.
    """
    compact_needle = "".join(needle.split())
    if not (2 <= len(compact_needle) <= 12):
        return False
    if not all("\u4e00" <= char <= "\u9fff" for char in compact_needle):
        return False
    iterator = iter(haystack)
    return all(any(char == candidate for candidate in iterator) for char in compact_needle)


class CatalogRepository:
    def __init__(self, catalog_path: Path, legacy_coverage_path: Path) -> None:
        self.catalog_path = catalog_path
        self.legacy_coverage_path = legacy_coverage_path
        self.payload = _read_object(catalog_path)
        self.coverage_payload = _read_object(legacy_coverage_path)
        self.questions: list[dict[str, Any]] = list(self.payload.get("questions") or [])
        self.by_id = {question["id"]: question for question in self.questions}
        if len(self.by_id) != len(self.questions):
            raise CatalogError("questions.json 含重复 id")
        self.coverage: list[dict[str, Any]] = list(
            self.coverage_payload.get("items") or []
        )
        self.source_items: list[dict[str, Any]] = list(
            self.payload.get("sources") or []
        )
        self.sources_by_id = {
            source["id"]: source
            for source in self.source_items
            if isinstance(source, dict) and isinstance(source.get("id"), str)
        }
        self.aliases_by_question: dict[str, list[str]] = {}
        for item in self.coverage:
            for question_id in item.get("mapped_question_ids") or []:
                self.aliases_by_question.setdefault(question_id, []).append(
                    item.get("question_intent") or ""
                )

    def get_question(self, question_id: str) -> dict[str, Any] | None:
        return self.by_id.get(question_id)

    def get_source(self, source_id: str) -> dict[str, Any] | None:
        return self.sources_by_id.get(source_id)

    def filter_questions(
        self,
        *,
        q: str | None = None,
        module_id: str | None = None,
        level: str | None = None,
        kind: str | None = None,
        origin: str | None = None,
        role: str | None = None,
        tag: str | None = None,
        question_ids: set[str] | None = None,
    ) -> list[dict[str, Any]]:
        needle = (q or "").strip().casefold()
        results: list[dict[str, Any]] = []
        for question in self.questions:
            if question_ids is not None and question["id"] not in question_ids:
                continue
            if module_id and question["module_id"] != module_id:
                continue
            if level and question["level"] != level:
                continue
            if kind and question["kind"] != kind:
                continue
            if origin and question["origin"] != origin:
                continue
            if role and role not in question.get("roles", []):
                continue
            if tag and tag not in question.get("tags", []):
                continue
            if needle:
                searchable = " ".join(
                    [
                        question.get("title", ""),
                        question.get("focus", ""),
                        question.get("answer", ""),
                        question.get("explanation", ""),
                        " ".join(question.get("followups", [])),
                        " ".join(question.get("pitfalls", [])),
                        str(question.get("scenario", "")),
                        " ".join(question.get("tags", [])),
                        " ".join(self.aliases_by_question.get(question["id"], [])),
                    ]
                ).casefold()
                if needle not in searchable and not _is_ordered_subsequence(
                    needle, searchable
                ):
                    continue
            results.append(question)
        return results

    def filter_coverage(
        self,
        *,
        source_id: str | None = None,
        mapping_status: str | None = None,
        q: str | None = None,
    ) -> list[dict[str, Any]]:
        needle = (q or "").strip().casefold()
        return [
            item
            for item in self.coverage
            if (not source_id or item["source_id"] == source_id)
            and (not mapping_status or item["mapping_status"] == mapping_status)
            and (not needle or needle in item["question_intent"].casefold())
        ]

    def meta(self) -> dict[str, Any]:
        return {
            "schema_version": self.payload.get("schema_version"),
            "generated_at": self.payload.get("generated_at"),
            "curated_updated_at": self.payload.get("curated_updated_at"),
            "statistics": self.payload.get("statistics", {}),
            "facets": {
                "levels": dict(Counter(item["level"] for item in self.questions)),
                "kinds": dict(Counter(item["kind"] for item in self.questions)),
                "origins": dict(Counter(item["origin"] for item in self.questions)),
                "roles": dict(
                    Counter(
                        role
                        for item in self.questions
                        for role in item.get("roles", [])
                    ).most_common()
                ),
                "tags": dict(
                    Counter(
                        tag
                        for item in self.questions
                        for tag in item.get("tags", [])
                    ).most_common()
                ),
            },
        }

    def modules(self) -> list[dict[str, Any]]:
        counts = Counter(question["module_id"] for question in self.questions)
        return [
            {**module, "question_count": counts[module["id"]]}
            for module in self.payload.get("modules", [])
        ]

    def sources(self) -> list[dict[str, Any]]:
        return list(self.source_items)


def compact_question(question: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in question.items()
        if key not in {"answer", "explanation", "followups", "pitfalls"}
    }
