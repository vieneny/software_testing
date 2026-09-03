"""将截图、页面源码和驱动日志组成一次离线失败证据包。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from qa_learning.mobile.mock.假移动端驱动 import 假移动端驱动


@dataclass(frozen=True, slots=True)
class 假证据清单:
    """各证据路径与采集错误。

    断连或崩溃后，真实 Appium 也可能无法再取得截图和页面树，因此这两个字段
    允许为 ``None``；驱动日志与清单文件仍会落盘，保证原始故障有迹可循。
    """

    截图: Path | None
    页面源码: Path | None
    驱动日志: Path
    采集清单: Path
    采集错误: tuple[str, ...] = ()
    是否合成: bool = True


def 采集假证据(
    驱动: 假移动端驱动,
    目录: Path,
    *,
    前缀: str = "失败现场",
) -> 假证据清单:
    """采集当前现场，对应真实框架中 pytest hook 的失败附件步骤。

    生产框架通常在 ``pytest_runtest_makereport`` 中仅对失败用例调用类似逻辑，
    再把文件附加到 Allure/CI 报告。本函数不集成报告插件，保持离线、零依赖。
    """

    if not 前缀.strip() or "/" in 前缀 or "\\" in 前缀:
        raise ValueError("证据前缀必须是一个非空文件名，不能包含路径分隔符")
    根目录 = 目录.expanduser().resolve()
    根目录.mkdir(parents=True, exist_ok=True)
    截图路径 = 根目录 / f"{前缀}_合成截图.png"
    页面源码路径 = 根目录 / f"{前缀}_合成页面源码.xml"
    驱动日志 = 根目录 / f"{前缀}_合成驱动日志.json"
    清单路径 = 根目录 / f"{前缀}_证据清单.json"

    # 每个通道独立采集。真实框架也不应因截图失败而跳过日志，更不能让这里的
    # 二次异常覆盖测试最初抛出的设备断连或应用崩溃异常。
    错误: list[str] = []
    截图: Path | None = None
    页面源码: Path | None = None
    try:
        驱动.save_screenshot(str(截图路径))
        截图 = 截图路径.resolve()
    except Exception as exc:  # noqa: BLE001 - 证据收集器必须 best-effort
        错误.append(f"截图不可用：{type(exc).__name__}: {exc}")
    try:
        页面源码路径.write_text(驱动.page_source, encoding="utf-8")
        页面源码 = 页面源码路径.resolve()
    except Exception as exc:  # noqa: BLE001 - 证据收集器必须 best-effort
        错误.append(f"页面源码不可用：{type(exc).__name__}: {exc}")

    日志内容 = 驱动.get_log("driver")
    驱动日志.write_text(
        json.dumps(
            {
                "synthetic": True,
                "warning": "仅供离线框架教学，不代表真实设备测试结果",
                "collection_errors": 错误,
                "entries": 日志内容,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    清单路径.write_text(
        json.dumps(
            {
                "synthetic": True,
                "screenshot": str(截图) if 截图 else None,
                "page_source": str(页面源码) if 页面源码 else None,
                "driver_log": str(驱动日志.resolve()),
                "collection_errors": 错误,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return 假证据清单(
        截图,
        页面源码,
        驱动日志.resolve(),
        清单路径.resolve(),
        tuple(错误),
    )
