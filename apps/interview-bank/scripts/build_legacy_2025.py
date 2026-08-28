#!/usr/bin/env python3
"""Build reviewed questions from the repository's first 2025 interview bank.

The original GitHub files are useful provenance but contain draft prose that is
not suitable for republication. This builder reads the sanitized historical
copies already tracked in the repository, reuses reviewed current answers when
the intent is clear, and otherwise writes a safe interview framework. It never
depends on the ignored local raw download.
"""

from __future__ import annotations

import argparse
import difflib
import html
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Optional


REPO_ROOT = Path(__file__).resolve().parents[3]
BANK_ROOT = REPO_ROOT / "apps" / "interview-bank"
DATA_DIR = BANK_ROOT / "data"
HISTORY_DIR = REPO_ROOT / "docs" / "08-求职备考" / "04-面试题库" / "历史资料"
OUTLINE_PATH = HISTORY_DIR / "大纲面试题-优化修订稿-2525年10月24日.md"
HTML_PATH = HISTORY_DIR / "面试题答案-粗稿-1.0版.html"
OUTPUT_PATH = DATA_DIR / "legacy-2025-reviewed.json"
COMMIT_SHA = "d0a8cfde75fe43c3abd7919e91c72bb7f3c15823"
UPDATED_AT = "2026-08-28"

SECTION_MODULE = {
    "测试理论": "01",
    "测试思维 & 场景": "10",
    "测试思维与场景": "10",
    "项目相关": "10",
    "测试用例设计": "02",
    "测试管理": "08",
    "抓包与网络协议": "04",
    "职业规划": "10",
}
MODULE_NAMES = {
    "01": "测试基础与质量思维",
    "02": "功能测试与用例设计",
    "03": "计算机基础、命令行、数据库与版本控制",
    "04": "网络、接口与数据库测试",
    "05": "编程语言与接口自动化测试框架",
    "06": "Web、Android 与 iOS 界面自动化",
    "07": "性能测试与稳定性",
    "08": "持续集成、质量工程与测试开发",
    "09": "AI、RAG、Agent 与大模型系统测试",
    "10": "场景题、项目题与行为面试",
}
MODULE_ROLES = {
    "01": ["功能测试", "软件测试", "测试开发"],
    "02": ["功能测试", "软件测试"],
    "04": ["接口测试", "自动化测试", "测试开发"],
    "08": ["测试开发", "质量工程", "测试负责人"],
    "10": ["软件测试", "自动化测试", "测试开发"],
}
SECTION_IDS = {
    "theory": "测试理论",
    "thinking": "测试思维与场景",
    "project": "项目相关",
    "cases": "测试用例设计",
    "management": "测试管理",
    "network": "抓包与网络协议",
    "career": "职业规划",
}
FORBIDDEN = (
    "\u5ea6\u5c0f\u6ee1",
    "\u751f\u4ea7\u73af\u5883\u8131\u654f\u6570\u636e",
    "\u771f\u5b9e\u516c\u53f8\u9879\u76ee",
    "\u4e2a\u4eba\u7ecf\u9a8c\uff1a",
)
PRIVATE_CONTACT_PATTERNS = (
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    re.compile(r"\bQQ\s*[:：]?\s*\d{6,12}\b", re.IGNORECASE),
)


@dataclass
class OutlineItem:
    index: int
    section: str
    question: str


@dataclass
class HtmlAnswer:
    section: str
    question: str
    answer: str
    sensitive: bool


def clean_text(value: str) -> str:
    value = html.unescape(value).replace("\xa0", " ")
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in value.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def safe_question(value: str) -> str:
    replacements = {
        "你们原来项目": "你选择的公开或虚构练习项目",
        "你们xx项目": "该公开或虚构练习项目",
        "上一家公司": "过往经历（仅按本人真实情况）",
        "公司的产品": "虚构产品",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return clean_text(value)


def has_forbidden(value: str) -> bool:
    return any(term in value for term in FORBIDDEN) or any(
        pattern.search(value) for pattern in PRIVATE_CONTACT_PATTERNS
    )


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).lower()
    value = re.sub(r"^2025\s*初版\s*\d+\s*[|｜]", "", value)
    value = re.sub(r"^\s*(?:q)?\d+[.、:：]?\s*", "", value)
    for old, new in {
        "bug": "缺陷",
        "app": "移动端",
        "web": "网页",
        "怎么": "如何",
        "怎样": "如何",
        "哪些": "什么",
        "测试点": "测试",
        "测试要点": "测试",
        "是什么": "",
        "你会": "",
    }.items():
        value = value.replace(old, new)
    return re.sub(r"[\W_]+", "", value, flags=re.UNICODE)


def similarity(left: str, right: str) -> float:
    a, b = normalize(left), normalize(right)
    if not a or not b:
        return 0.0
    score = difflib.SequenceMatcher(None, a, b).ratio()
    if a in b or b in a:
        score = max(score, min(len(a), len(b)) / max(len(a), len(b)) + 0.18)
    return min(score, 1.0)


def parse_outline() -> list[OutlineItem]:
    section = ""
    items: list[OutlineItem] = []
    for line in OUTLINE_PATH.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"^#{2,3}\s+(?:\d+[.、]?\s*)?(.+?)\s*$", line)
        if heading:
            candidate = clean_text(heading.group(1))
            section = "" if candidate == "功能测试" else candidate
            continue
        match = re.match(r"^\s*(\d+)\.\s+(.+?)\s*$", line)
        if match and section in SECTION_MODULE:
            items.append(
                OutlineItem(
                    index=len(items) + 1,
                    section=section,
                    question=safe_question(match.group(2)),
                )
            )
    return items


class AnswerParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.section = ""
        self.depth = 0
        self.collecting: Optional[str] = None
        self.collect_depth = -1
        self.buffer: list[str] = []
        self.question = ""
        self.items: list[HtmlAnswer] = []

    @staticmethod
    def attrs(values: list[tuple[str, Optional[str]]]) -> dict[str, str]:
        return {key: value or "" for key, value in values}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        if tag == "div":
            self.depth += 1
            values = self.attrs(attrs)
            classes = set(values.get("class", "").split())
            if "section" in classes:
                self.section = SECTION_IDS.get(values.get("id", ""), "")
            if "question" in classes:
                self.collecting, self.collect_depth, self.buffer = "question", self.depth, []
            elif "answer" in classes:
                self.collecting, self.collect_depth, self.buffer = "answer", self.depth, []
        elif self.collecting == "answer" and tag in {"p", "li", "br", "tr", "h3", "h4"}:
            self.buffer.append("\n")

    def handle_data(self, data: str) -> None:
        if self.collecting:
            self.buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != "div":
            return
        if self.collecting and self.depth == self.collect_depth:
            value = clean_text("".join(self.buffer))
            if self.collecting == "question":
                self.question = safe_question(re.sub(r"^\s*\d+[.、]\s*", "", value))
            elif self.question:
                sensitive = self.section in {"项目相关", "职业规划"} or has_forbidden(value)
                self.items.append(HtmlAnswer(self.section, self.question, value, sensitive))
                self.question = ""
            self.collecting, self.collect_depth, self.buffer = None, -1, []
        self.depth -= 1


def parse_html_answers() -> list[HtmlAnswer]:
    parser = AnswerParser()
    parser.feed(HTML_PATH.read_text(encoding="utf-8"))
    parser.close()
    return parser.items


def current_questions() -> list[dict[str, Any]]:
    payload = json.loads((DATA_DIR / "questions.json").read_text(encoding="utf-8"))
    return [
        item
        for item in payload.get("questions", [])
        if item.get("origin") != "legacy-2025-reviewed"
    ]


def best_match(question: str, candidates: list[dict[str, Any]]) -> tuple[float, dict[str, Any]]:
    return max(
        ((similarity(question, str(item.get("title", ""))), item) for item in candidates),
        key=lambda pair: pair[0],
    )


def generic_answer(question: str, section: str) -> str:
    if section == "测试思维 & 场景":
        return (
            f"回答“{question}”时，先澄清对象、用户、入口、约束和成功标准，再建立测试模型。"
            "功能维度覆盖主流程、分支、状态迁移、权限和撤销；数据维度覆盖有效、无效、边界、空值、重复与并发；"
            "异常维度覆盖弱网、超时、重试、依赖失败、进程中断和恢复。随后补充兼容性、易用性、可访问性、性能、安全与隐私。"
            "执行时使用合成账号和可重置数据，为每个关键动作记录请求、响应、状态变化和用户可见结果。"
            "最后按影响与发生概率排序，先跑高风险主链路，再扩展组合，并明确没有需求依据时需要向产品或开发确认的假设。"
        )
    if section == "项目相关":
        return (
            "这类题只回答本人确实做过的内容；练习时可以明确使用公开的 Demo Shop 合成项目。"
            f"围绕“{question}”，先用一句话说明系统目标、用户和负责边界，再按需求分析、风险建模、测试设计、执行取证、缺陷协作和发布复盘展开。"
            "示例可以描述订单、库存和支付替身之间的状态一致性：准备可重置数据，覆盖重复提交、超时、回调乱序和库存竞争，"
            "通过接口响应、数据库状态和审计事件交叉证明结果。结尾说明发现的问题、采取的行动、可核验产物和仍未覆盖的风险。"
            "不要借用他人的公司、团队规模、线上指标或项目成果；具体数字必须来自自己能解释和出示证据的实践。"
        )
    if section == "职业规划":
        return (
            f"回答“{question}”应基于本人真实情况，不背诵虚构履历。可以采用“当前事实—选择原因—行动证据—下一步”结构："
            "先给出与岗位直接相关的经历或学习现状，再说明为什么形成这一选择，接着列出已经完成且可展示的课程、代码、测试报告或复盘，"
            "最后给出六到十二个月可验证的目标。对薪资、入职时间、加班和离职原因等问题，保持简洁、专业并说明边界；"
            "不评价前雇主，不提供无关隐私，也不把模板内容说成亲身经历。"
        )
    if section == "测试管理":
        return (
            f"针对“{question}”，先明确目标、范围、质量标准和决策人，再把工作拆为风险、人员、环境、数据、进度和交付物。"
            "用风险清单决定优先级，用需求到用例到缺陷的追踪关系说明覆盖，用准入/准出标准管理节奏；每天关注阻塞、缺陷趋势和剩余高风险项。"
            "发生冲突时回到需求、复现证据和用户影响，由对应负责人作业务决策并留下记录。复盘时比较计划与实际、逃逸原因和自动化收益，"
            "形成负责人、截止时间和验证方式明确的改进项，而不是只汇报用例数量或通过率。"
        )
    return (
        f"回答“{question}”时，先给出定义和适用边界，再说明工作步骤、输入输出与验证证据。"
        "实践中把需求拆成正常、边界、异常、权限、并发和恢复场景，使用合成数据执行，并通过界面、接口、数据库或日志中的可核验结果交叉确认。"
        "如果规则存在版本差异，应说明依据的规范或工具版本；如果信息不足，应列出假设和待确认项。"
        "结尾补充常见失败模式、自动化适用范围和残余风险，避免只列概念、把工具操作当成测试结论，或承诺无法证明的绝对覆盖。"
    )


def enrich_answer(answer: str, question: str, section: str) -> str:
    answer = clean_text(answer)
    if has_forbidden(answer) or section in {"项目相关", "职业规划"}:
        return generic_answer(question, section)
    supplement = (
        "面试表达时还应说明适用边界、准备的数据、执行步骤和判断证据；遇到场景信息不足，先提出澄清问题。"
        "所有示例使用公开或从零构造的合成项目，不把模板包装成个人经历。"
    )
    if len(re.sub(r"\s+", "", answer)) < 120:
        answer = f"{answer}\n\n{supplement}\n\n{generic_answer(question, section)}"
    else:
        answer = f"{answer}\n\n{supplement}"
    return answer


def infer_kind(section: str, title: str) -> str:
    if section == "职业规划":
        return "行为题"
    if section == "项目相关":
        return "项目题"
    if section == "测试思维 & 场景" or any(word in title for word in ("如何测试", "测试思路", "排查")):
        return "场景题"
    return "知识题"


def answer_strategy(question: str, section: str, kind: str) -> str:
    """Build a reusable speaking plan that stays distinct from the model answer."""
    if kind == "项目题":
        return (
            f"回答“{question}”时，先界定这是不是本人真实经历；若只是练习，明确说明使用公开或虚构项目。"
            "按 STAR 展开：用两三句话交代系统目标、用户和约束，只陈述自己负责的范围；再说明面对的质量风险与任务目标；"
            "随后按需求澄清、测试设计、数据准备、执行取证、缺陷协作和回归发布描述行动；最后用可核验的报告、缺陷、代码或复盘说明结果。"
            "表达时区分团队成果与个人贡献，具体数字必须能解释口径和来源，并在结尾补充没有覆盖的风险及下一步改进。"
        )
    if kind == "行为题" or section == "职业规划":
        return (
            f"回答“{question}”时采用“事实—原因—证据—下一步”结构。先直接给出与问题有关的真实现状或选择，"
            "再解释形成该选择的原因，避免评价他人或前雇主；随后列出自己确实完成且可展示的学习记录、代码、测试报告或复盘作为证据；"
            "最后说明下一阶段的具体目标、时间范围和衡量方式。涉及薪资、离职、加班或个人安排时只提供岗位决策所需信息，"
            "保持专业边界，不背模板、不虚构履历，也不把练习项目包装成商业经历。"
        )
    if kind == "场景题":
        return (
            f"回答“{question}”时先澄清测试对象、目标用户、入口、成功标准、依赖和限制条件，避免立即罗列测试点。"
            "接着建立测试模型，从功能流程、状态迁移、数据边界、权限、并发、异常恢复、兼容性、性能、安全和可用性中选择相关维度；"
            "按用户影响、发生概率和可发现性排序，先覆盖高风险主链路，再扩展组合。说明数据与环境准备、执行顺序以及界面、接口、数据库、日志或指标证据，"
            "最后总结已覆盖范围、残余风险和需要继续确认的问题。"
        )
    return (
        f"回答“{question}”时先用一两句话给出准确的定义或结论，并说明适用条件，避免只背关键词。"
        "然后按“组成或机制—执行步骤—验证证据”展开：解释关键概念之间的关系，给出能在合成环境复现的操作或测试方法，"
        "再说明应观察的界面、请求响应、数据库状态、日志、指标或报告。若结论受协议、工具版本、数据规模或并发条件影响，要明确这些边界；"
        "最后补充一个常见误区和一个可继续追问的实践点，使回答同时包含原理、落地与风险。"
    )


def build_payload() -> dict[str, Any]:
    outline = parse_outline()
    html_answers = parse_html_answers()
    current = current_questions()
    questions: list[dict[str, Any]] = []

    for item in outline:
        module_id = SECTION_MODULE[item.section]
        module_candidates = [q for q in current if q.get("module_id") == module_id]
        current_score, current_match = best_match(item.question, module_candidates)
        html_candidates = [a for a in html_answers if a.section.replace("与", " & ") == item.section]
        if not html_candidates:
            html_candidates = [a for a in html_answers if SECTION_MODULE.get(a.section) == module_id]
        html_score, html_match = max(
            ((similarity(item.question, a.question), a) for a in html_candidates),
            key=lambda pair: pair[0],
        )

        if current_score >= 0.58:
            answer = str(current_match["answer"])
            explanation = str(current_match["explanation"])
            followups = list(current_match.get("followups") or [])
            pitfalls = list(current_match.get("pitfalls") or [])
            focus = str(current_match.get("focus") or "定义、步骤、证据与边界")
        elif html_score >= 0.52 and not html_match.sensitive:
            answer = html_match.answer
            explanation = (
                "旧版答案只作为主题线索，本条已经补入边界、证据和风险表达。面试回答需要把概念转成可执行步骤，"
                "并区分需求事实、个人真实经历与为了练习构造的场景；无法核验的数据和成果不能写进答案。"
            )
            followups = ["追问：如何把答案落到一个可复现的合成练习中？"]
            pitfalls = ["只背旧版条目，不说明适用边界、执行证据和风险。"]
            focus = f"{item.section}中的核心概念、执行步骤、证据和边界"
        else:
            answer = generic_answer(item.question, item.section)
            explanation = (
                "该题适合用结构化框架回答：先澄清条件，再建立测试模型，最后用证据和风险收尾。"
                "场景题没有唯一固定清单，维度必须随对象、状态、依赖和用户影响调整；行为与项目题则必须坚持真实性。"
            )
            followups = ["追问：哪些信息不明确时必须先向面试官澄清？"]
            pitfalls = ["机械罗列测试点，忽略优先级、判断依据和可验证证据。"]
            focus = f"{item.section}的结构化回答、风险优先级与证据意识"

        answer = enrich_answer(answer, item.question, item.section)
        kind = infer_kind(item.section, item.question)
        question: dict[str, Any] = {
            "id": f"legacy-2025-{item.index:03d}",
            "module_id": module_id,
            "origin": "legacy-2025-reviewed",
            "position": 20_000 + item.index,
            "title": f"2025 优化修订版 {item.index:03d}｜{item.question}",
            "level": "进阶" if kind in {"场景题", "项目题"} else "入门",
            "kind": kind,
            "roles": MODULE_ROLES[module_id],
            "tags": [item.section, "2025 优化修订版", "历史题整理"],
            "focus": clean_text(focus),
            "answer_strategy": answer_strategy(item.question, item.section, kind),
            "answer": clean_text(answer),
            "explanation": clean_text(explanation),
            "followups": followups or ["追问：如何用证据证明结论？"],
            "pitfalls": pitfalls or ["只给结论，不说明条件、步骤和证据。"],
            "source_ids": ["github-first-commit-2025"],
            "updated_at": UPDATED_AT,
        }
        if kind in {"场景题", "项目题", "行为题"}:
            question["scenario"] = {
                "type": "合成面试练习",
                "background": "使用公开的 Demo Shop 或从零构造的虚构系统，不引用任何公司内部资料。",
                "task": item.question,
                "synthetic": True,
            }
        reviewed = json.dumps(question, ensure_ascii=False)
        if has_forbidden(reviewed):
            raise ValueError(f"{question['id']} 含禁止发布内容")
        questions.append(question)

    if len(questions) != 160:
        raise ValueError(f"2025 优化修订版预期 160 题，实际生成 {len(questions)} 题")
    return {
        "schema_version": "1.0",
        "updated_at": UPDATED_AT,
        "collection": {
            "id": "github-first-edition-2025",
            "title": "2025 优化修订版软件测试面试题（已净化并补全答案与答题思路）",
            "source_commit": COMMIT_SHA,
            "question_count": len(questions),
            "answer_policy": "旧答案只作线索；发布内容使用现行评审答案或安全回答框架，项目与行为题不复用他人经历。",
        },
        "sources": [
            {
                "id": "github-first-commit-2025",
                "title": "software_testing 的 2025 优化修订版历史题库",
                "url": f"https://github.com/vieneny/software_testing/commit/{COMMIT_SHA}",
                "platform": "GitHub 公开历史提交",
                "accessed_at": UPDATED_AT,
                "note": "用于题目来源追溯；仓库仅收录净化后的题意和重新评审答案，不复制旧版个人信息或项目陈述。",
            }
        ],
        "questions": questions,
    }


def render(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    expected = render(payload)
    if args.check:
        if not OUTPUT_PATH.exists() or OUTPUT_PATH.read_text(encoding="utf-8") != expected:
            print(f"生成文件已过期：{OUTPUT_PATH.relative_to(REPO_ROOT)}", file=sys.stderr)
            return 1
    else:
        OUTPUT_PATH.write_text(expected, encoding="utf-8")
    print(f"2025 优化修订版整理完成：{len(payload['questions'])} 题")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
