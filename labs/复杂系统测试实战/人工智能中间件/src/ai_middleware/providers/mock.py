"""完全离线、无随机数的 Provider，适合学习、契约测试和 CI。"""

from __future__ import annotations

import re
from collections import Counter

from ai_middleware.models import (
    Citation,
    ContentAnalysisRequest,
    ContentAnalysisResult,
    KnowledgeAnswerRequest,
    KnowledgeAnswerResult,
    ModerationRequest,
    ModerationResult,
    ReplySuggestionRequest,
    ReplySuggestionResult,
    TicketClassificationRequest,
    TicketClassificationResult,
)
from ai_middleware.providers.base import AIProvider

_MODERATION_RULES: dict[str, tuple[str, ...]] = {
    "violence": ("炸弹", "杀死", "袭击", "bomb"),
    "abuse": ("蠢货", "废物", "idiot"),
    "privacy": ("身份证", "银行卡", "api_key", "password"),
    "prompt_injection": ("忽略之前", "system prompt", "越狱"),
}

_TAG_RULES: dict[str, tuple[str, ...]] = {
    "接口测试": ("接口", "api", "http"),
    "用户界面测试": ("ui", "页面", "安卓", "ios", "web"),
    "性能测试": ("性能", "并发", "吞吐", "响应时间"),
    "人工智能测试": ("ai", "模型", "大语言模型", "agent", "智能体"),
    "安全测试": ("安全", "漏洞", "注入", "越权"),
    "登录": ("登录", "验证码", "密码"),
    "支付退款": ("支付", "退款", "账单", "发票"),
}

_CATEGORY_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("security", ("泄露", "越权", "盗号", "攻击", "漏洞", "安全")),
    ("billing", ("退款", "扣款", "支付", "账单", "发票")),
    ("account", ("登录", "密码", "验证码", "账号")),
    ("technical", ("崩溃", "报错", "异常", "超时", "打不开", "卡死")),
    ("product", ("建议", "希望增加", "新功能", "需求")),
)


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _contains(text: str, terms: tuple[str, ...]) -> list[str]:
    lowered = text.lower()
    return [term for term in terms if term.lower() in lowered]


def _truncate(text: str, limit: int) -> tuple[str, bool]:
    if len(text) <= limit:
        return text, False
    if limit <= 1:
        return "…", True
    return text[: limit - 1].rstrip() + "…", True


def _tokens(text: str) -> set[str]:
    lowered = text.lower()
    ascii_tokens = set(re.findall(r"[a-z0-9_]{2,}", lowered))
    chinese_runs = re.findall(r"[\u4e00-\u9fff]+", lowered)
    chinese_tokens: set[str] = set()
    for run in chinese_runs:
        chinese_tokens.update(run[index : index + 2] for index in range(len(run) - 1))
        if len(run) == 1:
            chinese_tokens.add(run)
    return ascii_tokens | chinese_tokens


class MockProvider(AIProvider):
    name = "mock"
    model = "deterministic-rules"
    version = "2026.07"

    @property
    def ready(self) -> bool:
        return True

    async def moderate(self, request: ModerationRequest) -> ModerationResult:
        matched_by_category = {
            category: _contains(request.text, terms)
            for category, terms in _MODERATION_RULES.items()
        }
        matched_by_category = {
            category: terms for category, terms in matched_by_category.items() if terms
        }
        categories = sorted(matched_by_category)
        matched_terms = sorted(
            {term for terms in matched_by_category.values() for term in terms}
        )

        weights = {
            "violence": 0.9,
            "privacy": 0.65,
            "prompt_injection": 0.6,
            "abuse": 0.45,
        }
        score = max((weights[category] for category in categories), default=0.0)
        decision = "block" if score >= 0.75 else "review" if score >= 0.35 else "allow"
        reason = (
            "离线规则未发现风险关键词"
            if not categories
            else f"离线规则命中：{', '.join(categories)}；需结合上下文人工复核"
        )
        return ModerationResult(
            allowed=decision == "allow",
            decision=decision,
            risk_score=score,
            categories=categories,
            matched_terms=matched_terms,
            reason=reason,
        )

    async def analyze_content(
        self, request: ContentAnalysisRequest
    ) -> ContentAnalysisResult:
        text = _normalise(request.text)
        sentence_parts = [
            item.strip()
            for item in re.split(r"(?<=[。！？.!?])\s*", text)
            if item.strip()
        ]
        candidate = " ".join(sentence_parts[:3]) if sentence_parts else text
        summary, truncated = _truncate(candidate, request.max_summary_chars)

        tags = [
            tag for tag, terms in _TAG_RULES.items() if _contains(text, terms)
        ][: request.max_tags]
        if not tags:
            words = re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", text.lower())
            counts = Counter(words)
            tags = [
                word
                for word, _ in sorted(
                    counts.items(), key=lambda item: (-item[1], item[0])
                )[: request.max_tags]
            ]
        if not tags:
            tags = ["通用内容"]

        return ContentAnalysisResult(
            summary=summary,
            tags=tags,
            source_chars=len(text),
            truncated=truncated,
        )

    async def classify_ticket(
        self, request: TicketClassificationRequest
    ) -> TicketClassificationResult:
        text = f"{request.subject} {request.content}".lower()
        category = "other"
        matched: list[str] = []
        for candidate, terms in _CATEGORY_RULES:
            found = _contains(text, terms)
            if found:
                category = candidate
                matched = found
                break

        if category == "security" or _contains(text, ("全站", "大面积", "数据丢失")):
            priority = "P0"
        elif _contains(text, ("紧急", "无法使用", "重复扣款", "生产故障")):
            priority = "P1"
        elif category == "product":
            priority = "P3"
        else:
            priority = "P2"

        confidence = 0.9 if len(matched) >= 2 else 0.75 if matched else 0.4
        reasons = (
            [f"命中离线分类词：{', '.join(matched)}"]
            if matched
            else ["未命中专用规则，归入人工分诊队列"]
        )
        reasons.append(f"优先级规则输出 {priority}，生产环境必须由人工确认")
        return TicketClassificationResult(
            category=category,
            priority=priority,
            confidence=confidence,
            reasons=reasons,
        )

    async def answer_knowledge(
        self, request: KnowledgeAnswerRequest
    ) -> KnowledgeAnswerResult:
        question_tokens = _tokens(request.question)
        ranked: list[tuple[float, str, str, str]] = []
        for document in request.documents:
            document_tokens = _tokens(f"{document.title} {document.content}")
            common = question_tokens & document_tokens
            score = len(common) / max(len(question_tokens), 1)
            ranked.append((score, document.source_id, document.title, document.content))

        score, source_id, title, content = max(
            ranked, key=lambda item: (item[0], item[1])
        )
        if score <= 0:
            return KnowledgeAnswerResult(
                answer="现有资料中没有找到足够依据，请补充知识文档或转人工处理。",
                grounded=False,
                confidence=0.0,
                citations=[],
                must_verify=["不得依据本回答臆测政策、价格或账户状态"],
            )

        excerpt, _ = _truncate(_normalise(content), 300)
        return KnowledgeAnswerResult(
            answer=f"依据《{title}》：{excerpt}",
            grounded=True,
            confidence=min(0.95, round(0.45 + score, 2)),
            citations=[Citation(source_id=source_id, title=title)],
            must_verify=["发送给客户前核对原文版本和适用范围"],
        )

    async def suggest_reply(
        self, request: ReplySuggestionRequest
    ) -> ReplySuggestionResult:
        category_labels = {
            "account": "账号问题",
            "billing": "支付或账单问题",
            "technical": "技术问题",
            "security": "安全问题",
            "product": "产品建议",
            "other": "咨询",
        }
        opening = {
            "professional": "您好，我们已记录您的反馈。",
            "empathetic": "您好，很抱歉给您带来不便，我们已记录您的反馈。",
            "concise": "您好，您的反馈已记录。",
        }[request.tone]
        suggestion = (
            f"{opening} 当前初步识别为{category_labels[request.category]}，"
            f"优先级建议为 {request.priority}。为避免误判，请提供可公开的复现步骤、"
            "发生时间和客户端版本；请勿发送密码、验证码或完整证件号码。"
        )
        actions = {
            "account": ["核对账号标识与登录时间", "检查认证服务状态"],
            "billing": ["核对脱敏订单号", "检查支付回调与账务状态"],
            "technical": ["收集客户端版本和复现步骤", "检查对应时间段服务指标"],
            "security": ["立即转安全值班人员", "冻结敏感操作并保全审计证据"],
            "product": ["记录使用场景和预期收益", "转交产品评审"],
            "other": ["补充问题上下文", "人工选择正确队列"],
        }[request.category]
        return ReplySuggestionResult(
            suggestion=suggestion,
            suggested_actions=actions,
            must_verify=[
                "不得承诺退款、赔偿、修复时间或最终结论",
                "核对客户身份、工单上下文和公司正式政策",
            ],
            requires_human_review=True,
        )
