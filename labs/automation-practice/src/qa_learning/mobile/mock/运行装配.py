"""把教学替身装配成一条可替换为真实 Appium 的运行链。

映射关系如下：

``设备提供器 → 驱动工厂 → Session → Screen/Task → Test → Evidence → Cleanup``

真实项目可分别将前两项替换成 adb/simctl 设备查询和 Appium DriverFactory；
Screen/Task、测试意图、证据与清理边界则可以保持。这里所有设备和应用都只是
显式合成数据，绝不扫描本机 USB 设备。
"""

from __future__ import annotations

from dataclasses import dataclass

from qa_learning.mobile.mock.假移动端驱动 import 假移动端驱动
from qa_learning.mobile.mock.公开演示应用 import (
    构建安卓公开演示应用,
    构建苹果公开演示应用,
)
from qa_learning.mobile.mock.故障注入 import 故障注入计划
from qa_learning.mobile.mock.移动端契约 import (
    安卓平台契约,
    定位器,
    苹果平台契约,
)


@dataclass(frozen=True, slots=True)
class 移动端运行契约:
    """一次运行的最小显式输入，对应 CI 参数和 Appium capabilities 来源。"""

    平台: str
    设备标识: str
    应用配置: str = "公开合成商城"

    def __post_init__(self) -> None:
        if self.平台 not in {"android", "ios"}:
            raise ValueError("平台只能是 android 或 ios")
        if self.应用配置 != "公开合成商城":
            raise ValueError("离线教学层只允许公开合成商城配置")
        if not self.设备标识.startswith("synthetic-"):
            raise ValueError("离线设备标识必须以 synthetic- 开头")


@dataclass(frozen=True, slots=True)
class 假设备:
    """由 Fake DeviceProvider 返回的确定性设备记录。"""

    平台: str
    设备标识: str
    状态: str = "online"


class 假设备提供器:
    """显式设备清单，不调用 adb、simctl，也不读取本地环境变量。"""

    def __init__(self) -> None:
        self._设备 = (
            假设备("android", "synthetic-android-01"),
            假设备("ios", "synthetic-ios-01"),
        )

    def 获取(self, 运行: 移动端运行契约) -> 假设备:
        for 设备 in self._设备:
            if 设备.平台 == 运行.平台 and 设备.设备标识 == 运行.设备标识:
                return 设备
        raise LookupError(f"找不到显式合成设备：{运行.设备标识}")


class 假驱动工厂:
    """根据统一运行契约创建 Android/iOS 离线 session。"""

    def __init__(self, 设备提供器: 假设备提供器 | None = None) -> None:
        self.设备提供器 = 设备提供器 or 假设备提供器()

    def 创建(
        self,
        运行: 移动端运行契约,
        *,
        故障计划: 故障注入计划 | None = None,
    ) -> 假移动端驱动:
        self.设备提供器.获取(运行)
        if 运行.平台 == "android":
            return 假移动端驱动(
                安卓平台契约(),
                构建安卓公开演示应用(),
                故障计划=故障计划,
            )
        return 假移动端驱动(
            苹果平台契约(),
            构建苹果公开演示应用(),
            故障计划=故障计划,
        )


class 演示商城定位仓库:
    """集中管理两端定位器，避免把定位细节散落到测试函数。"""

    _定位 = {
        "android": {
            "用户名": 定位器("id", "org.example.publicshop:id/username"),
            "密码": 定位器("id", "org.example.publicshop:id/password"),
            "登录": 定位器("accessibility id", "登录"),
            "商品": 定位器("accessibility id", "商品-学习背包"),
        },
        "ios": {
            "用户名": 定位器("accessibility id", "login.username"),
            "密码": 定位器("accessibility id", "login.password"),
            "登录": 定位器("-ios predicate string", "label == '登录'"),
            "商品": 定位器("accessibility id", "product.learning-backpack"),
        },
    }

    @classmethod
    def 获取(cls, 平台: str, 名称: str) -> 定位器:
        try:
            return cls._定位[平台][名称]
        except KeyError as exc:
            raise LookupError(f"没有定位器：平台={平台}，名称={名称}") from exc


class 应用管理器:
    """封装应用生命周期，不让业务测试直接散落 app id 和底层命令。"""

    def __init__(self, 驱动: 假移动端驱动) -> None:
        self.驱动 = 驱动

    def 重启并重置(self) -> None:
        """对应真实 Appium 的 terminate/activate，重置合成应用状态。"""

        应用标识 = self.驱动.平台.应用标识
        self.驱动.terminate_app(应用标识)
        self.驱动.activate_app(应用标识)


class 移动端动作:
    """稳定动作层：定位、点击、输入和平台手势只在此处组合。"""

    def __init__(self, 驱动: 假移动端驱动, 平台: str) -> None:
        self.驱动 = 驱动
        self.平台 = 平台

    def 输入(self, 定位: 定位器, 文本: str) -> None:
        元素 = self.驱动.find_element(*定位.转为元组())
        元素.clear()
        元素.send_keys(文本)

    def 点击(self, 定位: 定位器) -> None:
        self.驱动.find_element(*定位.转为元组()).click()

    def 向上滑动(self) -> None:
        脚本 = "mobile: swipeGesture" if self.平台 == "android" else "mobile: swipe"
        self.驱动.execute_script(脚本, {"direction": "up"})


class 系统处理器:
    """集中系统动作；真实实现可继续加入权限弹窗、键盘和系统提示。"""

    def __init__(self, 驱动: 假移动端驱动) -> None:
        self.驱动 = 驱动

    def 返回上一页(self) -> None:
        self.驱动.back()


class 演示商城任务:
    """业务级 Task Object：测试只描述意图，不直接拼装驱动命令。"""

    def __init__(self, 驱动: 假移动端驱动, 平台: str) -> None:
        self.驱动 = 驱动
        self.平台 = 平台
        self.动作 = 移动端动作(驱动, 平台)

    def 登录(self, 用户名: str, 密码: str) -> None:
        self.动作.输入(
            演示商城定位仓库.获取(self.平台, "用户名"),
            用户名,
        )
        self.动作.输入(
            演示商城定位仓库.获取(self.平台, "密码"),
            密码,
        )
        self.动作.点击(演示商城定位仓库.获取(self.平台, "登录"))

    def 打开学习背包(self) -> None:
        """统一业务动作，内部选择平台专属手势命令。"""

        self.动作.向上滑动()
        self.动作.点击(演示商城定位仓库.获取(self.平台, "商品"))
