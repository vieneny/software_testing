#!/usr/bin/env python3
"""对三个已启动服务执行只使用合成数据的全链路接口验收。"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Iterable
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4


class VerificationFailure(RuntimeError):
    """服务不可达、契约不一致或业务断言失败。"""


def request_json(
    method: str,
    url: str,
    *,
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    expected_statuses: Iterable[int] = (200,),
) -> tuple[int, dict[str, str], Any]:
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        **(headers or {}),
    }
    request = Request(url, data=body, headers=request_headers, method=method)

    try:
        with urlopen(request, timeout=30) as response:
            status = response.status
            response_headers = {
                key.lower(): value for key, value in response.headers.items()
            }
            raw_body = response.read()
    except HTTPError as error:
        status = error.code
        response_headers = {
            key.lower(): value for key, value in error.headers.items()
        }
        raw_body = error.read()
    except URLError as error:
        raise VerificationFailure(f"服务不可达：{url}；{error.reason}") from error

    try:
        response_body = json.loads(raw_body.decode("utf-8")) if raw_body else None
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise VerificationFailure(f"{url} 未返回合法 UTF-8 JSON") from error

    allowed = set(expected_statuses)
    if status not in allowed:
        safe_preview = json.dumps(response_body, ensure_ascii=False)[:500]
        raise VerificationFailure(
            f"{method} {url} 预期状态 {sorted(allowed)}，实际 {status}：{safe_preview}"
        )
    return status, response_headers, response_body


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationFailure(message)


def verify_community(base_url: str, run_id: str, *, verify_ai: bool) -> None:
    print("[社区] 健康检查")
    _, _, health = request_json("GET", f"{base_url}/api/v1/health")
    require(health["status"] == "ok", "社区健康检查状态不是 ok")

    question_key = f"e2e.question.{run_id}"
    question_payload = {
        "title": f"全链路合成问题 {run_id}",
        "content": "这是全链路接口验收生成的合成正文，只用于验证幂等、回答和状态机。",
        "author_name": "验收学习者",
        "tags": ["全链路", "合成数据"],
    }
    print("[社区] 创建问题并验证幂等重放")
    status, headers, question = request_json(
        "POST",
        f"{base_url}/api/v1/questions",
        payload=question_payload,
        headers={"Idempotency-Key": question_key},
        expected_statuses=(201,),
    )
    require(status == 201, "首次创建问题未返回 201")
    require(headers.get("idempotency-replayed") == "false", "首次创建被错误标记为重放")
    question_id = question["id"]

    replay_status, replay_headers, replay = request_json(
        "POST",
        f"{base_url}/api/v1/questions",
        payload=question_payload,
        headers={"Idempotency-Key": question_key},
        expected_statuses=(200,),
    )
    require(replay_status == 200, "问题幂等重放未返回 200")
    require(replay_headers.get("idempotency-replayed") == "true", "问题重放头缺失")
    require(replay["id"] == question_id, "问题幂等重放生成了不同资源")

    print("[社区] 回答、采纳、投票和问题关闭/重开")
    answer_payload = {
        "content": "先验证首次写入，再原样重放相同幂等键，最后检查数据库只存在一条回答。",
        "author_name": "验收回答者",
    }
    answer_key = f"e2e.answer.{run_id}"
    _, _, answer = request_json(
        "POST",
        f"{base_url}/api/v1/questions/{question_id}/answers",
        payload=answer_payload,
        headers={"Idempotency-Key": answer_key},
        expected_statuses=(201,),
    )
    answer_id = answer["id"]
    answer_replay_status, answer_replay_headers, answer_replay = request_json(
        "POST",
        f"{base_url}/api/v1/questions/{question_id}/answers",
        payload=answer_payload,
        headers={"Idempotency-Key": answer_key},
        expected_statuses=(200,),
    )
    require(answer_replay_status == 200, "回答幂等重放未返回 200")
    require(
        answer_replay_headers.get("idempotency-replayed") == "true",
        "回答重放头缺失",
    )
    require(answer_replay["id"] == answer_id, "回答幂等重放生成了不同资源")
    _, _, question_after_replay = request_json(
        "GET",
        f"{base_url}/api/v1/questions/{question_id}",
    )
    require(len(question_after_replay["answers"]) == 1, "回答幂等重放产生了重复数据")

    _, _, accepted = request_json(
        "PUT",
        f"{base_url}/api/v1/questions/{question_id}/answers/{answer_id}/acceptance",
        payload={"accepted": True},
    )
    require(
        any(item["id"] == answer_id and item["is_accepted"] for item in accepted["answers"]),
        "回答采纳状态未生效",
    )

    _, _, vote = request_json(
        "POST",
        f"{base_url}/api/v1/questions/{question_id}/votes",
        payload={"voter_key": f"e2e-voter-{run_id}", "value": 1},
    )
    require(vote["score"] == 1, "首次赞成票后的分数应为 1")

    _, _, closed = request_json(
        "PATCH",
        f"{base_url}/api/v1/questions/{question_id}/status",
        payload={"status": "closed"},
    )
    require(closed["status"] == "closed", "问题未进入 closed 状态")
    request_json(
        "POST",
        f"{base_url}/api/v1/questions/{question_id}/answers",
        payload={
            "content": "关闭后不应被写入的合成回答。",
            "author_name": "边界测试者",
        },
        headers={"Idempotency-Key": f"e2e.closed-answer.{run_id}"},
        expected_statuses=(409,),
    )
    _, _, reopened = request_json(
        "PATCH",
        f"{base_url}/api/v1/questions/{question_id}/status",
        payload={"status": "open"},
    )
    require(reopened["status"] == "open", "问题未重新进入 open 状态")

    if verify_ai:
        print("[社区] AI 摘要契约")
        _, _, summary = request_json(
            "POST",
            f"{base_url}/api/v1/questions/{question_id}/ai-summary",
            headers={"X-Request-ID": f"e2e.community.ai.{run_id}"},
        )
        require(summary["question_id"] == question_id, "AI 摘要关联了错误的问题")
        require(bool(summary["summary"].strip()), "AI 摘要为空")


def verify_customer_service(base_url: str, run_id: str, *, verify_ai: bool) -> None:
    tenant_headers = {"X-Tenant-Code": "demo"}
    print("[客服] 健康检查与客户数据")
    _, _, health = request_json("GET", f"{base_url}/api/health")
    require(health["status"] == "UP", "客服健康检查状态不是 UP")
    _, _, customers = request_json(
        "GET",
        f"{base_url}/api/v1/customers",
        headers=tenant_headers,
    )
    require(bool(customers), "客服系统没有可用于验收的合成客户")
    customer = customers[0]

    print("[客服] 创建会话并验证幂等重放")
    conversation_payload = {
        "customerId": customer["id"],
        "channel": "WEB",
        "subject": f"全链路合成会话 {run_id}",
        "initialMessage": "这是接口验收创建的合成客户消息，不对应任何真实客户。",
    }
    conversation_headers = {
        **tenant_headers,
        "Idempotency-Key": f"e2e.conversation.{run_id}",
    }
    _, _, conversation = request_json(
        "POST",
        f"{base_url}/api/v1/conversations",
        payload=conversation_payload,
        headers=conversation_headers,
        expected_statuses=(201,),
    )
    conversation_id = conversation["id"]
    _, _, replay = request_json(
        "POST",
        f"{base_url}/api/v1/conversations",
        payload=conversation_payload,
        headers=conversation_headers,
        expected_statuses=(201,),
    )
    require(replay["id"] == conversation_id, "会话幂等重放生成了不同资源")
    require(len(replay["messages"]) == 1, "会话幂等重放重复生成了首条消息")

    print("[客服] 内部备注不可见、公开回复可见")
    internal_payload = {
        "expectedVersion": replay["version"],
        "senderType": "AGENT",
        "visibility": "INTERNAL",
        "authorName": "验收坐席",
        "content": "仅坐席可见的合成内部备注。",
    }
    _, _, with_internal = request_json(
        "POST",
        f"{base_url}/api/v1/conversations/{conversation_id}/messages",
        payload=internal_payload,
        headers={
            **tenant_headers,
            "Idempotency-Key": f"e2e.internal-message.{run_id}",
        },
    )
    _, _, customer_view = request_json(
        "GET",
        f"{base_url}/api/v1/conversations/{conversation_id}",
        headers=tenant_headers,
    )
    require(
        all(message["visibility"] == "CUSTOMER" for message in customer_view["messages"]),
        "默认会话详情泄漏了内部备注",
    )

    public_payload = {
        "expectedVersion": with_internal["version"],
        "senderType": "AGENT",
        "visibility": "CUSTOMER",
        "authorName": "验收坐席",
        "content": "您好，这是合成场景中的公开回复，请核对演示账号状态。",
    }
    _, _, with_reply = request_json(
        "POST",
        f"{base_url}/api/v1/conversations/{conversation_id}/messages",
        payload=public_payload,
        headers={
            **tenant_headers,
            "Idempotency-Key": f"e2e.public-message.{run_id}",
        },
    )
    require(with_reply["state"] == "WAITING_CUSTOMER", "坐席公开回复后会话状态不正确")

    print("[客服] 会话升级工单并验证关联")
    ticket_payload = {
        "customerId": customer["id"],
        "conversationId": conversation_id,
        "title": f"全链路合成工单 {run_id}",
        "description": "由合成会话升级，用于验证工单、AI 建议和关联查询。",
        "category": "ACCOUNT",
        "priority": "HIGH",
    }
    _, _, ticket = request_json(
        "POST",
        f"{base_url}/api/v1/tickets",
        payload=ticket_payload,
        headers={
            **tenant_headers,
            "Idempotency-Key": f"e2e.ticket.{run_id}",
        },
        expected_statuses=(201,),
    )
    ticket_id = ticket["id"]
    _, _, linked = request_json(
        "GET",
        f"{base_url}/api/v1/conversations/{conversation_id}?includeInternal=true",
        headers=tenant_headers,
    )
    require(ticket_id in linked["linkedTicketIds"], "会话详情没有返回关联工单")

    if verify_ai:
        print("[客服] AI 回复建议契约")
        _, _, suggestion = request_json(
            "POST",
            f"{base_url}/api/v1/tickets/{ticket_id}/ai-suggestions",
            payload={"tone": "professional", "language": "zh-CN"},
            headers={
                **tenant_headers,
                "X-Request-ID": f"e2e.customer.ai.{run_id}",
            },
        )
        require(bool(suggestion["mustVerify"]), "AI 建议缺少人工核验项")
        require(
            suggestion["degraded"] is False,
            f"AI 建议发生降级：{suggestion.get('degradationReason')}",
        )

    print("[客服] 关闭会话")
    _, _, closed = request_json(
        "POST",
        f"{base_url}/api/v1/conversations/{conversation_id}/transitions",
        payload={
            "expectedVersion": linked["version"],
            "targetState": "CLOSED",
            "operatorName": "验收主管",
            "note": "全链路验收结束",
        },
        headers={
            **tenant_headers,
            "Idempotency-Key": f"e2e.close-conversation.{run_id}",
        },
    )
    require(closed["state"] == "CLOSED", "会话未进入 CLOSED 状态")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="使用纯合成数据验收社区、客服与 AI 中间件的核心纵向链路。"
    )
    parser.add_argument(
        "--community-url",
        default=os.getenv("COMMUNITY_BASE_URL", "http://127.0.0.1:8000"),
    )
    parser.add_argument(
        "--customer-service-url",
        default=os.getenv("CUSTOMER_SERVICE_BASE_URL", "http://127.0.0.1:8080"),
    )
    parser.add_argument(
        "--ai-url",
        default=os.getenv("AI_BASE_URL", "http://127.0.0.1:8090"),
    )
    parser.add_argument(
        "--skip-ai",
        action="store_true",
        help="只验证核心业务，不要求 AI 中间件已启动。",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_id = uuid4().hex[:12]
    try:
        if not args.skip_ai:
            print("[AI] 健康检查")
            _, _, health = request_json("GET", f"{args.ai_url.rstrip('/')}/health")
            require(health["status"] == "ok", "AI 中间件健康检查状态不是 ok")
        verify_community(
            args.community_url.rstrip("/"),
            run_id,
            verify_ai=not args.skip_ai,
        )
        verify_customer_service(
            args.customer_service_url.rstrip("/"),
            run_id,
            verify_ai=not args.skip_ai,
        )
    except (KeyError, TypeError, VerificationFailure) as error:
        print(f"\n验收失败：{error}", file=sys.stderr)
        return 1

    print(f"\n验收通过，合成运行标识：{run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
