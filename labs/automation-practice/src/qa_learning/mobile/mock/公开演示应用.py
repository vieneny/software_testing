"""Android/iOS 共用业务、平台定位不同的纯合成商城。

这里没有从公司应用、内网接口或真实用户复制任何字段。两个构造函数刻意保持
页面业务一致，只改变定位器，以便学习者练习“业务断言复用、平台页面对象分层”。
"""

from __future__ import annotations

from qa_learning.mobile.mock.移动端契约 import (
    元素定义,
    公开演示应用,
    定位器,
    页面定义,
)


def _构建应用(定位: dict[str, 定位器]) -> 公开演示应用:
    return 公开演示应用(
        应用名="公开合成演示商城",
        起始页面="登录",
        页面={
            "登录": 页面定义(
                "登录",
                [
                    元素定义(定位["用户名"], 文本="用户名", 可输入=True),
                    元素定义(定位["密码"], 文本="密码", 可输入=True),
                    元素定义(定位["登录按钮"], 文本="登录", 点击后页面="商品列表"),
                ],
            ),
            "商品列表": 页面定义(
                "商品列表",
                [
                    元素定义(定位["标题"], 文本="公开演示商品"),
                    元素定义(
                        定位["背包商品"],
                        文本="学习背包",
                        点击后页面="商品详情",
                        需要滑动次数=1,
                    ),
                ],
            ),
            "商品详情": 页面定义(
                "商品详情",
                [
                    元素定义(定位["详情标题"], 文本="学习背包"),
                    元素定义(定位["价格"], 文本="¥99.00"),
                ],
            ),
        },
    )


def 构建安卓公开演示应用() -> 公开演示应用:
    """返回使用 Android resource-id/accessibility id 的页面模型。"""

    return _构建应用(
        {
            "用户名": 定位器("id", "org.example.publicshop:id/username"),
            "密码": 定位器("id", "org.example.publicshop:id/password"),
            "登录按钮": 定位器("accessibility id", "登录"),
            "标题": 定位器("id", "org.example.publicshop:id/catalog_title"),
            "背包商品": 定位器("accessibility id", "商品-学习背包"),
            "详情标题": 定位器("id", "org.example.publicshop:id/detail_title"),
            "价格": 定位器("id", "org.example.publicshop:id/price"),
        }
    )


def 构建苹果公开演示应用() -> 公开演示应用:
    """返回使用 iOS accessibility id/predicate 的页面模型。"""

    return _构建应用(
        {
            "用户名": 定位器("accessibility id", "login.username"),
            "密码": 定位器("accessibility id", "login.password"),
            "登录按钮": 定位器("-ios predicate string", "label == '登录'"),
            "标题": 定位器("accessibility id", "catalog.title"),
            "背包商品": 定位器("accessibility id", "product.learning-backpack"),
            "详情标题": 定位器("accessibility id", "detail.title"),
            "价格": 定位器("accessibility id", "detail.price"),
        }
    )
