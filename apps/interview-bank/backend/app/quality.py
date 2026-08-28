"""Read-only validation and reporting for reviewed source coverage."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SourceCoverageError(RuntimeError):
    """Raised when a generated source coverage snapshot is invalid."""


class SourceCoverageRepository:
    def __init__(
        self,
        coverage_path: Path | None,
        valid_question_ids: set[str],
        *,
        source_label: str,
        missing_filename: str,
    ) -> None:
        self.coverage_path = coverage_path
        self.valid_question_ids = valid_question_ids
        self.source_label = source_label
        self.missing_filename = missing_filename
        self.payload = self._load()
        self.response = self._build_response()

    def _empty_payload(self) -> dict[str, Any]:
        return {
            "source_title": None,
            "source_url": None,
            "accessed_at": None,
            "summary": f"{self.source_label}覆盖快照尚未生成。",
            "documents": [],
        }

    def _load(self) -> dict[str, Any]:
        if self.coverage_path is None or not self.coverage_path.exists():
            return self._empty_payload()
        try:
            raw = json.loads(self.coverage_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise SourceCoverageError(
                f"{self.source_label}覆盖文件不是有效 JSON"
            ) from exc
        except OSError as exc:
            raise SourceCoverageError(
                f"无法读取{self.source_label}覆盖文件"
            ) from exc
        if not isinstance(raw, dict):
            raise SourceCoverageError(
                f"{self.source_label}覆盖文件顶层必须是对象"
            )
        documents = raw.get("documents")
        if not isinstance(documents, list):
            raise SourceCoverageError(
                f"{self.source_label}覆盖文件的 documents 必须是数组"
            )

        normalized_documents: list[dict[str, Any]] = []
        seen_urls: set[str] = set()
        seen_ids: set[str] = set()
        for index, document in enumerate(documents, start=1):
            if not isinstance(document, dict):
                raise SourceCoverageError(f"documents[{index}] 必须是对象")
            normalized = self._normalize_document(document, index)
            document_url = normalized["url"]
            document_id = normalized["document_id"]
            if document_url in seen_urls:
                raise SourceCoverageError(f"文档 URL 重复：{document_url}")
            if document_id in seen_ids:
                raise SourceCoverageError(f"document_id 重复：{document_id}")
            seen_urls.add(document_url)
            seen_ids.add(document_id)
            unknown = sorted(
                set(normalized["question_ids"]) - self.valid_question_ids
            )
            if unknown:
                raise SourceCoverageError(
                    f"文档 {document_id} 引用了不存在的题目 ID：{', '.join(unknown)}"
                )
            normalized_documents.append(normalized)

        return {
            "source_title": self._optional_string(raw.get("source_title")),
            "source_url": self._optional_string(raw.get("source_url")),
            "accessed_at": self._optional_string(raw.get("accessed_at")),
            "summary": self._optional_string(raw.get("summary")),
            "documents": normalized_documents,
        }

    @staticmethod
    def _required_string(document: dict[str, Any], field: str, index: int) -> str:
        value = document.get(field)
        if not isinstance(value, str) or not value.strip():
            raise SourceCoverageError(
                f"documents[{index}].{field} 必须是非空字符串"
            )
        return value.strip()

    @staticmethod
    def _optional_string(value: Any) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise SourceCoverageError("来源元数据字段必须是字符串或 null")
        return value.strip() or None

    @staticmethod
    def _optional_nonnegative_int(
        document: dict[str, Any], field: str, index: int
    ) -> int | None:
        value = document.get(field)
        if value is None:
            return None
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise SourceCoverageError(
                f"documents[{index}].{field} 必须是非负整数或 null"
            )
        return value

    def _normalize_document(
        self, document: dict[str, Any], index: int
    ) -> dict[str, Any]:
        question_ids = document.get("question_ids")
        if not isinstance(question_ids, list) or any(
            not isinstance(question_id, str) or not question_id.strip()
            for question_id in question_ids
        ):
            raise SourceCoverageError(
                f"documents[{index}].question_ids 必须是字符串数组"
            )
        normalized_ids = [question_id.strip() for question_id in question_ids]
        if len(normalized_ids) != len(set(normalized_ids)):
            raise SourceCoverageError(
                f"documents[{index}].question_ids 不能包含重复项"
            )
        source_chars = document.get("source_chars")
        if not isinstance(source_chars, int) or isinstance(source_chars, bool) or source_chars < 0:
            raise SourceCoverageError(
                f"documents[{index}].source_chars 必须是非负整数"
            )
        quality_notes = document.get("quality_notes")
        if not isinstance(quality_notes, (str, list)):
            raise SourceCoverageError(
                f"documents[{index}].quality_notes 必须是字符串或数组"
            )
        if isinstance(quality_notes, list) and any(
            not isinstance(note, str) for note in quality_notes
        ):
            raise SourceCoverageError(
                f"documents[{index}].quality_notes 数组只能包含字符串"
            )
        return {
            "document_id": self._required_string(document, "document_id", index),
            "title": self._required_string(document, "title", index),
            "module": self._required_string(document, "module", index),
            "url": self._required_string(document, "url", index),
            "source_chars": source_chars,
            "coverage_mode": self._required_string(
                document, "coverage_mode", index
            ),
            "question_ids": normalized_ids,
            "quality_notes": quality_notes,
            "declared_question_count": self._optional_nonnegative_int(
                document, "declared_question_count", index
            ),
            "observed_question_count": self._optional_nonnegative_int(
                document, "observed_question_count", index
            ),
        }

    def _build_response(self) -> dict[str, Any]:
        documents = self.payload["documents"]
        unmapped = [
            {
                "document_id": document["document_id"],
                "title": document["title"],
                "module": document["module"],
                "url": document["url"],
            }
            for document in documents
            if not document["question_ids"]
        ]
        available = self.coverage_path is not None and self.coverage_path.exists()
        return {
            "status": "ready" if available else "not_available",
            "message": (
                f"{self.source_label}覆盖快照已加载并通过引用校验。"
                if available
                else f"尚未生成 {self.missing_filename}；当前返回空覆盖状态。"
            ),
            "source_title": self.payload["source_title"],
            "source_url": self.payload["source_url"],
            "accessed_at": self.payload["accessed_at"],
            "summary": self.payload["summary"],
            "document_count": len(documents),
            "mapped_document_count": len(documents) - len(unmapped),
            "question_reference_count": sum(
                len(document["question_ids"]) for document in documents
            ),
            "declared_question_count": sum(
                document["declared_question_count"] or 0
                for document in documents
            ),
            "observed_question_count": sum(
                document["observed_question_count"] or 0
                for document in documents
            ),
            "unmapped_documents": unmapped,
            "documents": documents,
        }

    def report(self) -> dict[str, Any]:
        return self.response
