"""移动端 Fake Driver 的平台和数据契约。

真实 Appium 会把客户端能力（capabilities）发送给服务端，由 UiAutomator2 或
XCUITest 驱动解释定位器和手势。离线替身没有服务端，因此在本文件中显式定义
双方都必须遵守的契约。这样测试失败时，学习者能区分“定位器不受平台支持”和
“业务页面中没有该元素”。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol


class 会话状态(StrEnum):
    """模拟 Appium session 和被测应用的关键生命周期状态。"""

    活跃 = "active"
    应用已终止 = "app_terminated"
    设备已断连 = "device_disconnected"
    应用已崩溃 = "app_crashed"
    已退出 = "quit"


class 移动端替身错误(RuntimeError):
    """所有离线移动端错误的公共父类，便于测试按层捕获异常。"""


class 会话不可用错误(移动端替身错误):
    """会话已退出、应用未运行或设备不可用时抛出。"""


class 元素未找到错误(移动端替身错误):
    """对应 Selenium/Appium 的 ``NoSuchElementException``。"""


class 操作超时错误(移动端替身错误):
    """对应显式等待最终抛出的 ``TimeoutException``，但不会真的等待。"""


class 设备断连错误(移动端替身错误):
    """模拟 USB、网络或模拟器连接中断。"""


class 应用崩溃错误(移动端替身错误):
    """模拟被测应用在命令执行期间退出。"""


@dataclass(frozen=True, slots=True)
class 定位器:
    """一个与 ``driver.find_element(by, value)`` 等价的定位器。"""

    方式: str
    值: str

    def __post_init__(self) -> None:
        if not self.方式.strip() or not self.值.strip():
            raise ValueError("定位方式和定位值都不能为空")

    def 转为元组(self) -> tuple[str, str]:
        """返回 Selenium Page Object 常用的二元组形式。"""

        return self.方式, self.值


class 平台契约(Protocol):
    """Android 与 iOS 契约都必须提供的最小接口。"""

    平台名: str
    自动化引擎: str
    应用标识: str

    def 校验定位器(self, 定位: 定位器) -> None:
        """拒绝当前平台无法解释的定位策略。"""

    def 校验滑动命令(self, 脚本名: str) -> None:
        """校验 ``execute_script`` 使用的平台专属移动命令。"""


@dataclass(frozen=True, slots=True)
class 安卓平台契约:
    """模拟 UiAutomator2 的一小组稳定、常用能力。"""

    应用标识: str = "org.example.publicshop"
    平台名: str = "Android"
    自动化引擎: str = "UiAutomator2"
    支持的定位方式: frozenset[str] = field(
        default_factory=lambda: frozenset(
            {"id", "accessibility id", "class name", "xpath", "-android uiautomator"}
        )
    )

    def 校验定位器(self, 定位: 定位器) -> None:
        if 定位.方式.lower() not in self.支持的定位方式:
            raise ValueError(f"Android/UiAutomator2 不支持定位方式：{定位.方式}")

    def 校验滑动命令(self, 脚本名: str) -> None:
        if 脚本名 != "mobile: swipeGesture":
            raise ValueError("Android 教学替身只接受 mobile: swipeGesture")


@dataclass(frozen=True, slots=True)
class 苹果平台契约:
    """模拟 XCUITest 的一小组稳定、常用能力。"""

    应用标识: str = "org.example.publicshop.ios"
    平台名: str = "iOS"
    自动化引擎: str = "XCUITest"
    支持的定位方式: frozenset[str] = field(
        default_factory=lambda: frozenset(
            {
                "id",
                "accessibility id",
                "class name",
                "xpath",
                "-ios predicate string",
                "-ios class chain",
            }
        )
    )

    def 校验定位器(self, 定位: 定位器) -> None:
        if 定位.方式.lower() not in self.支持的定位方式:
            raise ValueError(f"iOS/XCUITest 不支持定位方式：{定位.方式}")

    def 校验滑动命令(self, 脚本名: str) -> None:
        if 脚本名 != "mobile: swipe":
            raise ValueError("iOS 教学替身只接受 mobile: swipe")


@dataclass(slots=True)
class 元素定义:
    """页面模型中的一个合成元素。

    ``点击后页面`` 相当于演示应用真实点击后的导航结果；``需要滑动次数`` 用来
    教学“元素存在于页面模型，但尚未进入可见区域”这一常见场景。
    """

    定位: 定位器
    文本: str = ""
    可见: bool = True
    可用: bool = True
    可输入: bool = False
    输入值: str = ""
    点击后页面: str | None = None
    需要滑动次数: int = 0


@dataclass(slots=True)
class 页面定义:
    """一个可序列化为简化 XML page source 的合成页面。"""

    名称: str
    元素: list[元素定义]


@dataclass(slots=True)
class 公开演示应用:
    """完全合成、无任何企业数据的最小移动应用状态机。"""

    应用名: str
    起始页面: str
    页面: dict[str, 页面定义]
    当前页面: str = ""
    页面历史: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.起始页面 not in self.页面:
            raise ValueError(f"起始页面不存在：{self.起始页面}")
        self.重置()

    def 重置(self) -> None:
        self.当前页面 = self.起始页面
        self.页面历史.clear()
        for 页面 in self.页面.values():
            for 元素 in 页面.元素:
                元素.输入值 = ""

    def 跳转(self, 页面名称: str) -> None:
        if 页面名称 not in self.页面:
            raise ValueError(f"目标页面不存在：{页面名称}")
        self.页面历史.append(self.当前页面)
        self.当前页面 = 页面名称

    def 返回(self) -> None:
        if self.页面历史:
            self.当前页面 = self.页面历史.pop()
