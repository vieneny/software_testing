"""成功场景：同一业务流程在 Android 和 iOS 契约下运行。"""

from __future__ import annotations

import json

import pytest

from qa_learning.mobile.mock import (
    会话状态,
    假移动端驱动,
    元素未找到错误,
    安卓平台契约,
    构建安卓公开演示应用,
    构建苹果公开演示应用,
    苹果平台契约,
    采集假证据,
)

pytestmark = [pytest.mark.mobile, pytest.mark.mock, pytest.mark.contract]


@pytest.mark.parametrize(
    ("平台", "应用", "用户名定位", "密码定位", "登录定位", "滑动脚本", "商品定位"),
    [
        (
            安卓平台契约(),
            构建安卓公开演示应用(),
            ("id", "org.example.publicshop:id/username"),
            ("id", "org.example.publicshop:id/password"),
            ("accessibility id", "登录"),
            "mobile: swipeGesture",
            ("accessibility id", "商品-学习背包"),
        ),
        (
            苹果平台契约(),
            构建苹果公开演示应用(),
            ("accessibility id", "login.username"),
            ("accessibility id", "login.password"),
            ("-ios predicate string", "label == '登录'"),
            "mobile: swipe",
            ("accessibility id", "product.learning-backpack"),
        ),
    ],
)
def test_登录滑动查看商品并采集合成证据(
    tmp_path,
    平台,
    应用,
    用户名定位,
    密码定位,
    登录定位,
    滑动脚本,
    商品定位,
) -> None:
    清理顺序: list[str] = []

    with 假移动端驱动(平台, 应用) as 驱动:
        驱动.添加清理(清理顺序.append, "先注册后执行")
        驱动.添加清理(清理顺序.append, "后注册先执行")

        用户名 = 驱动.find_element(*用户名定位)
        用户名.clear()
        用户名.send_keys("public_learner")
        assert 用户名.text == "public_learner"

        密码 = 驱动.find_element(*密码定位)
        密码.send_keys("synthetic_password")
        驱动.find_element(*登录定位).click()
        assert 驱动.当前页面 == "商品列表"

        # 商品被建模为首屏外元素，先查找失败，滑动后才可见。
        with pytest.raises(元素未找到错误):
            驱动.find_element(*商品定位)
        驱动.execute_script(滑动脚本, {"direction": "up"})
        驱动.find_element(*商品定位).click()
        assert 驱动.当前页面 == "商品详情"
        assert "synthetic-page" in 驱动.page_source
        assert "¥99.00" in 驱动.page_source

        清单 = 采集假证据(驱动, tmp_path, 前缀=f"{平台.平台名}成功流程")
        assert 清单.是否合成 is True
        assert 清单.截图 is not None
        assert 清单.页面源码 is not None
        assert 清单.截图.read_bytes().startswith(b"\x89PNG")
        assert "<synthetic-page" in 清单.页面源码.read_text(encoding="utf-8")
        assert 清单.采集清单.exists()
        assert 清单.采集错误 == ()
        日志 = json.loads(清单.驱动日志.read_text(encoding="utf-8"))
        assert 日志["synthetic"] is True
        assert any(条目["event"] == "NAVIGATION" for 条目 in 日志["entries"])

    assert 驱动.状态 is 会话状态.已退出
    assert 清理顺序 == ["后注册先执行", "先注册后执行"]


def test_应用终止与重新激活会重置页面状态() -> None:
    平台 = 安卓平台契约()
    驱动 = 假移动端驱动(平台, 构建安卓公开演示应用())
    驱动.find_element("accessibility id", "登录").click()
    assert 驱动.当前页面 == "商品列表"

    assert 驱动.terminate_app(平台.应用标识) is True
    assert 驱动.状态 is 会话状态.应用已终止
    驱动.activate_app(平台.应用标识)

    assert 驱动.状态 is 会话状态.活跃
    assert 驱动.当前页面 == "登录"
    驱动.quit()
    驱动.quit()  # quit 必须幂等，方便多个 teardown 层安全调用。
