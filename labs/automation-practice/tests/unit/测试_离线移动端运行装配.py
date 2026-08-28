"""验证 DeviceProvider 到 Task Object 的完整装配链。"""

from __future__ import annotations

import pytest

from qa_learning.mobile.mock import (
    假驱动工厂,
    应用管理器,
    演示商城任务,
    移动端运行契约,
    系统处理器,
)

pytestmark = [pytest.mark.mobile, pytest.mark.mock, pytest.mark.contract]


@pytest.mark.parametrize(
    ("平台", "设备标识"),
    [
        ("android", "synthetic-android-01"),
        ("ios", "synthetic-ios-01"),
    ],
)
def test_统一运行契约可驱动两端相同业务任务(平台, 设备标识) -> None:
    运行 = 移动端运行契约(平台, 设备标识)

    with 假驱动工厂().创建(运行) as 驱动:
        任务 = 演示商城任务(驱动, 平台)
        任务.登录("public_learner", "synthetic_password")
        任务.打开学习背包()

        assert 驱动.当前页面 == "商品详情"
        assert 驱动.capabilities["synthetic"] is True

        系统处理器(驱动).返回上一页()
        assert 驱动.当前页面 == "商品列表"

        应用管理器(驱动).重启并重置()
        assert 驱动.当前页面 == "登录"


def test_运行契约拒绝看似真实的设备标识() -> None:
    with pytest.raises(ValueError, match="synthetic-"):
        移动端运行契约("android", "real-device-serial")
