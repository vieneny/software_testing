"""可运行的离线 Appium WebDriver 教学替身。

方法名尽量贴近 Appium Python Client，让 Page Object 的思维能够迁移：

* ``find_element``：平台校验后在当前页面查找元素；
* ``click/clear/send_keys``：由假元素代理到驱动并记录日志；
* ``execute_script``：解释 Android/iOS 各自的 ``mobile:`` 滑动命令；
* ``page_source/save_screenshot/get_log``：输出明确标记为 synthetic 的假证据；
* ``quit``：无论会话是否崩溃，都执行注册的清理回调。

它不是 Appium 协议模拟器，也不应拿来证明真实应用兼容性。其目的只是让学习者
在没有 SDK、Appium Server 和设备时练习测试框架的控制流与故障恢复。
"""

from __future__ import annotations

import base64
import copy
from collections.abc import Callable
from contextlib import ExitStack
from dataclasses import dataclass
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any

from qa_learning.mobile.mock.故障注入 import 故障注入计划, 故障类型
from qa_learning.mobile.mock.移动端契约 import (
    会话不可用错误,
    会话状态,
    元素定义,
    元素未找到错误,
    公开演示应用,
    定位器,
    平台契约,
    应用崩溃错误,
    操作超时错误,
    设备断连错误,
)

# 一个有效的 1×1 PNG。真实截图必须由设备渲染；这里写固定像素并在日志、文件名
# 和证据清单中声明 synthetic，避免它被误当成真实测试结果。
_合成PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk/x8AAusB9Wl2nC8AAAAASUVORK5CYII="
)


@dataclass(frozen=True, slots=True)
class 假日志:
    """结构与远端驱动日志相似，但内容完全由本进程生成。"""

    时间: str
    级别: str
    事件: str
    消息: str

    def 转为字典(self) -> dict[str, str | bool]:
        return {
            "timestamp": self.时间,
            "level": self.级别,
            "event": self.事件,
            "message": self.消息,
            "synthetic": True,
        }


class 假移动端元素:
    """绑定到当前会话的元素句柄，对应 Appium ``WebElement``。"""

    def __init__(self, 驱动: 假移动端驱动, 定义: 元素定义) -> None:
        self._驱动 = 驱动
        self._定义 = 定义

    @property
    def text(self) -> str:
        """输入框优先返回当前输入值，普通元素返回静态可见文本。"""

        return self._定义.输入值 if self._定义.可输入 else self._定义.文本

    def is_displayed(self) -> bool:
        return self._驱动._元素当前可见(self._定义)

    def is_enabled(self) -> bool:
        return self._定义.可用

    def click(self) -> None:
        self._驱动._点击(self._定义)

    def clear(self) -> None:
        self._驱动._清空(self._定义)

    def send_keys(self, value: str) -> None:
        self._驱动._输入(self._定义, value)


class 假移动端驱动:
    """不联网、不接设备，但保持真实 Appium 流程边界的驱动。

    构造函数相当于 ``webdriver.Remote(...)`` 成功创建 session；上下文管理器的
    退出相当于 fixture teardown 调用 ``driver.quit()``。建议教学代码始终使用
    ``with`` 或 pytest yield fixture，保证断言失败时也能走清理流程。
    """

    def __init__(
        self,
        平台: 平台契约,
        应用: 公开演示应用,
        *,
        故障计划: 故障注入计划 | None = None,
    ) -> None:
        self.平台 = 平台
        # 每个 session 都深拷贝应用，避免并行用例共享输入值、导航历史等状态。
        self.应用 = copy.deepcopy(应用)
        self.故障计划 = 故障计划 or 故障注入计划()
        self.状态 = 会话状态.活跃
        self.capabilities: dict[str, Any] = {
            "platformName": 平台.平台名,
            "appium:automationName": 平台.自动化引擎,
            "appium:app": "synthetic://public-demo-app",
            "appium:appId": 平台.应用标识,
            "synthetic": True,
        }
        self._滑动次数: dict[str, int] = {}
        self._日志: list[假日志] = []
        self._清理栈 = ExitStack()
        self._记录("INFO", "SESSION_STARTED", f"{平台.平台名} 离线会话已创建")

    def __enter__(self) -> 假移动端驱动:
        return self

    def __exit__(self, _类型: object, _值: object, _追踪: object) -> None:
        self.quit()

    @property
    def 当前页面(self) -> str:
        return self.应用.当前页面

    def 添加清理(
        self,
        回调: Callable[..., Any],
        /,
        *参数: Any,
        **关键字参数: Any,
    ) -> None:
        """注册 LIFO 清理回调，对应 fixture finalizer/``ExitStack.callback``。"""

        self._清理栈.callback(回调, *参数, **关键字参数)

    def find_element(self, by: str, value: str) -> 假移动端元素:
        """在当前页面找一个元素；没有轮询，也不会真实等待。"""

        定位 = 定位器(by, value)
        self._检查可操作()
        self.平台.校验定位器(定位)
        self._应用故障("find_element", 定位)
        for 定义 in self._当前页面定义().元素:
            if 定义.定位 == 定位 and self._元素当前可见(定义):
                self._记录("INFO", "ELEMENT_FOUND", f"{定位.方式}={定位.值}")
                return 假移动端元素(self, 定义)
        self._记录("WARN", "ELEMENT_NOT_FOUND", f"{定位.方式}={定位.值}")
        raise 元素未找到错误(f"当前页面“{self.当前页面}”找不到元素：{定位}")

    def swipe(self, direction: str = "up") -> None:
        """执行一次有界的合成滑动，使延迟展示元素变为可见。"""

        self._检查可操作()
        self._应用故障("swipe")
        if direction not in {"up", "down", "left", "right"}:
            raise ValueError(f"不支持的滑动方向：{direction}")
        self._滑动次数[self.当前页面] = self._滑动次数.get(self.当前页面, 0) + 1
        self._记录("INFO", "SWIPE", f"方向={direction}，页面={self.当前页面}")

    def execute_script(self, script: str, arguments: dict[str, Any]) -> None:
        """解释真实 Page Object 常用的 ``mobile: swipe*`` 命令。"""

        self.平台.校验滑动命令(script)
        direction = str(arguments.get("direction", "up"))
        self.swipe(direction)

    def back(self) -> None:
        """模拟系统返回键或导航返回；根页面执行时保持不变。"""

        self._检查可操作()
        self._应用故障("back")
        原页面 = self.当前页面
        self.应用.返回()
        self._记录("INFO", "BACK", f"{原页面} -> {self.当前页面}")

    def terminate_app(self, app_id: str) -> bool:
        """终止合成应用但保留 session，对应 Appium ``terminate_app``。"""

        self._检查应用标识(app_id)
        if self.状态 is 会话状态.已退出:
            raise 会话不可用错误("会话已退出，不能终止应用")
        self.状态 = 会话状态.应用已终止
        self._记录("INFO", "APP_TERMINATED", app_id)
        return True

    def activate_app(self, app_id: str) -> None:
        """重新激活应用并回到起始页面，对应 Appium ``activate_app``。"""

        self._检查应用标识(app_id)
        if self.状态 in {会话状态.设备已断连, 会话状态.已退出}:
            raise 会话不可用错误(f"当前状态不能激活应用：{self.状态.value}")
        self.应用.重置()
        self._滑动次数.clear()
        self.状态 = 会话状态.活跃
        self._记录("INFO", "APP_ACTIVATED", app_id)

    @property
    def page_source(self) -> str:
        """返回当前可见树的合成 XML，对应 Appium page source。"""

        self._检查可操作()
        节点: list[str] = []
        for 元素 in self._当前页面定义().元素:
            if not self._元素当前可见(元素):
                continue
            text = 元素.输入值 if 元素.可输入 else 元素.文本
            节点.append(
                "  <element"
                f' by="{escape(元素.定位.方式)}"'
                f' value="{escape(元素.定位.值)}"'
                f' text="{escape(text)}"'
                f' enabled="{str(元素.可用).lower()}" />'
            )
        内容 = "\n".join(节点)
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<synthetic-page platform="{escape(self.平台.平台名)}" '
            f'name="{escape(self.当前页面)}">\n{内容}\n</synthetic-page>'
        )

    def save_screenshot(self, filename: str) -> bool:
        """写入固定 1×1 PNG；只验证证据流程，不验证任何视觉结果。"""

        self._检查可操作()
        self._应用故障("save_screenshot")
        路径 = Path(filename).expanduser().resolve()
        路径.parent.mkdir(parents=True, exist_ok=True)
        路径.write_bytes(_合成PNG)
        self._记录("INFO", "SYNTHETIC_SCREENSHOT", str(路径))
        return True

    def get_log(self, log_type: str) -> list[dict[str, str | bool]]:
        """读取驱动日志快照；当前仅支持教学用 ``driver`` 类型。"""

        if log_type != "driver":
            raise ValueError("离线教学替身仅支持 driver 日志")
        return [日志.转为字典() for 日志 in self._日志]

    def quit(self) -> None:
        """幂等退出并始终执行清理栈，包括崩溃、断连后的场景。"""

        if self.状态 is 会话状态.已退出:
            return
        self._记录("INFO", "SESSION_QUITTING", f"原状态={self.状态.value}")
        try:
            self._清理栈.close()
        finally:
            self.状态 = 会话状态.已退出
            self._记录("INFO", "SESSION_QUIT", "离线会话已退出")

    def _当前页面定义(self):
        return self.应用.页面[self.当前页面]

    def _元素当前可见(self, 元素: 元素定义) -> bool:
        已滑动 = self._滑动次数.get(self.当前页面, 0)
        return 元素.可见 and 已滑动 >= 元素.需要滑动次数

    def _点击(self, 元素: 元素定义) -> None:
        self._检查可操作()
        self._应用故障("click", 元素.定位)
        if not self._元素当前可见(元素) or not 元素.可用:
            raise 元素未找到错误(f"元素不可点击：{元素.定位}")
        self._记录("INFO", "CLICK", f"{元素.定位.方式}={元素.定位.值}")
        if 元素.点击后页面:
            原页面 = self.当前页面
            self.应用.跳转(元素.点击后页面)
            self._记录("INFO", "NAVIGATION", f"{原页面} -> {self.当前页面}")

    def _清空(self, 元素: 元素定义) -> None:
        self._检查可操作()
        self._应用故障("clear", 元素.定位)
        if not 元素.可输入:
            raise ValueError(f"元素不是输入框：{元素.定位}")
        元素.输入值 = ""
        self._记录("INFO", "CLEAR", f"{元素.定位.方式}={元素.定位.值}")

    def _输入(self, 元素: 元素定义, value: str) -> None:
        self._检查可操作()
        self._应用故障("send_keys", 元素.定位)
        if not 元素.可输入:
            raise ValueError(f"元素不是输入框：{元素.定位}")
        元素.输入值 += value
        # 日志只保留字符数，不记录密码或其他输入内容，演示测试证据最小化原则。
        self._记录("INFO", "SEND_KEYS", f"{元素.定位.值} 输入 {len(value)} 个字符")

    def _检查应用标识(self, app_id: str) -> None:
        if app_id != self.平台.应用标识:
            raise ValueError(f"应用标识不匹配：{app_id}")

    def _检查可操作(self) -> None:
        异常映射 = {
            会话状态.应用已终止: 会话不可用错误("应用已终止，请先 activate_app"),
            会话状态.设备已断连: 设备断连错误("设备已断连"),
            会话状态.应用已崩溃: 应用崩溃错误("应用已崩溃"),
            会话状态.已退出: 会话不可用错误("会话已退出"),
        }
        if self.状态 in 异常映射:
            raise 异常映射[self.状态]

    def _应用故障(self, 操作: str, 定位: 定位器 | None = None) -> None:
        规则 = self.故障计划.消费(操作, 定位)
        if 规则 is None:
            return
        说明 = 规则.说明 or f"在 {操作} 注入 {规则.类型.value}"
        self._记录("ERROR", "FAULT_INJECTED", 说明)
        if 规则.类型 is 故障类型.定位失败:
            raise 元素未找到错误(说明)
        if 规则.类型 is 故障类型.操作超时:
            raise 操作超时错误(说明)
        if 规则.类型 is 故障类型.设备断连:
            self.状态 = 会话状态.设备已断连
            raise 设备断连错误(说明)
        self.状态 = 会话状态.应用已崩溃
        raise 应用崩溃错误(说明)

    def _记录(self, 级别: str, 事件: str, 消息: str) -> None:
        self._日志.append(
            假日志(
                datetime.now(UTC).isoformat(timespec="milliseconds"),
                级别,
                事件,
                消息,
            )
        )
