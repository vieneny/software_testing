"""可预测、一次性的移动端故障注入。

真实设备故障往往具有偶发性，直接拿它们教学会让失败难以复现。本计划在指定的
WebDriver 操作命中时消费一条故障规则，既能稳定演示恢复策略，也能确保同一条
规则不会污染后续步骤。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from qa_learning.mobile.mock.移动端契约 import 定位器


class 故障类型(StrEnum):
    """覆盖移动端 UI 自动化最常见的四类基础故障。"""

    定位失败 = "locator_failure"
    操作超时 = "timeout"
    设备断连 = "device_disconnected"
    应用崩溃 = "app_crashed"


@dataclass(slots=True)
class 故障规则:
    """命中条件；定位器为空表示对该操作的任意元素生效。"""

    类型: 故障类型
    操作: str
    定位: 定位器 | None = None
    剩余次数: int = 1
    说明: str = ""


@dataclass(slots=True)
class 故障注入计划:
    """按添加顺序匹配故障，便于 Arrange 阶段明确声明失败点。"""

    规则: list[故障规则] = field(default_factory=list)

    def 添加(
        self,
        类型: 故障类型,
        *,
        操作: str,
        定位: 定位器 | None = None,
        次数: int = 1,
        说明: str = "",
    ) -> 故障注入计划:
        """添加规则并返回自身，支持链式构造测试场景。"""

        if 次数 < 1:
            raise ValueError("故障注入次数至少为 1")
        self.规则.append(故障规则(类型, 操作, 定位, 次数, 说明))
        return self

    def 消费(self, 操作: str, 定位: 定位器 | None = None) -> 故障规则 | None:
        """返回首条命中规则并扣减次数；没有命中时返回 ``None``。"""

        for 规则 in self.规则:
            if 规则.剩余次数 < 1 or 规则.操作 != 操作:
                continue
            if 规则.定位 is not None and 规则.定位 != 定位:
                continue
            规则.剩余次数 -= 1
            return 规则
        return None
