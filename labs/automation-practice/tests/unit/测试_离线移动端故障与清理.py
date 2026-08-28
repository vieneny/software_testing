"""失败场景：验证异常类型、状态迁移、一次性规则和最终清理。"""

from __future__ import annotations

import json

import pytest

from qa_learning.mobile.mock import (
    会话状态,
    假移动端驱动,
    元素未找到错误,
    安卓平台契约,
    定位器,
    应用崩溃错误,
    操作超时错误,
    故障注入计划,
    故障类型,
    构建安卓公开演示应用,
    设备断连错误,
    采集假证据,
)

pytestmark = [pytest.mark.mobile, pytest.mark.mock, pytest.mark.contract]

用户名 = 定位器("id", "org.example.publicshop:id/username")


@pytest.mark.parametrize(
    ("故障", "异常"),
    [
        (故障类型.定位失败, 元素未找到错误),
        (故障类型.操作超时, 操作超时错误),
    ],
)
def test_定位失败和超时会留首次失败证据且不会污染重试(
    tmp_path,
    故障,
    异常,
) -> None:
    计划 = 故障注入计划().添加(
        故障,
        操作="find_element",
        定位=用户名,
        说明="合成的首次查找失败",
    )
    驱动 = 假移动端驱动(
        安卓平台契约(),
        构建安卓公开演示应用(),
        故障计划=计划,
    )

    with pytest.raises(异常, match="首次查找失败"):
        驱动.find_element(*用户名.转为元组())

    首次失败证据 = 采集假证据(驱动, tmp_path, 前缀=故障.value)
    首次失败日志 = json.loads(首次失败证据.驱动日志.read_text(encoding="utf-8"))
    assert any(条目["event"] == "FAULT_INJECTED" for 条目 in 首次失败日志["entries"])

    # 同一规则已消费，第二次查找成功；可据此练习有上限且有条件的重试。
    assert 驱动.find_element(*用户名.转为元组()).is_displayed()
    assert 驱动.状态 is 会话状态.活跃
    驱动.quit()


def test_设备断连改变会话状态且仍会留日志证据并执行清理(tmp_path) -> None:
    计划 = 故障注入计划().添加(
        故障类型.设备断连,
        操作="swipe",
        说明="合成 USB 连接中断",
    )
    已清理: list[str] = []
    驱动 = 假移动端驱动(
        安卓平台契约(),
        构建安卓公开演示应用(),
        故障计划=计划,
    )
    驱动.添加清理(已清理.append, "释放测试账号")

    with pytest.raises(设备断连错误, match="USB"):
        驱动.swipe("up")
    assert 驱动.状态 is 会话状态.设备已断连

    证据 = 采集假证据(驱动, tmp_path, 前缀="设备断连")
    assert 证据.截图 is None
    assert 证据.页面源码 is None
    assert len(证据.采集错误) == 2
    日志 = json.loads(证据.驱动日志.read_text(encoding="utf-8"))
    assert any(条目["event"] == "FAULT_INJECTED" for 条目 in 日志["entries"])
    assert 证据.采集清单.exists()

    驱动.quit()
    assert 已清理 == ["释放测试账号"]
    assert 驱动.状态 is 会话状态.已退出


def test_点击时应用崩溃且退出动作保持可用() -> None:
    登录 = 定位器("accessibility id", "登录")
    计划 = 故障注入计划().添加(
        故障类型.应用崩溃,
        操作="click",
        定位=登录,
        说明="合成应用进程退出",
    )
    驱动 = 假移动端驱动(
        安卓平台契约(),
        构建安卓公开演示应用(),
        故障计划=计划,
    )
    登录按钮 = 驱动.find_element(*登录.转为元组())

    with pytest.raises(应用崩溃错误, match="进程退出"):
        登录按钮.click()
    assert 驱动.状态 is 会话状态.应用已崩溃

    驱动.quit()
    assert 驱动.状态 is 会话状态.已退出
