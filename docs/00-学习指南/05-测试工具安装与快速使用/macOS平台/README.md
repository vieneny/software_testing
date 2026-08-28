# macOS 测试工具安装与快速使用

> 核对日期：**2026-07-27**。完整新工具链优先面向 Apple Silicon。Intel Mac 的 Anaconda、Android Studio、Xcode 和最新 iOS 支持正在明显收缩，必须逐项固定兼容版本。

## 学习顺序

1. [安装前准备与包管理](01-安装前准备与包管理.md)
2. [编程语言与开发工具](02-编程语言与开发工具.md)
3. [数据库与容器工具](03-数据库与容器工具.md)
4. [接口测试与网络抓包](04-接口测试与网络抓包.md)
5. [网页与移动端自动化](05-网页与移动端自动化.md)
6. [性能测试与测试报告](06-性能测试与测试报告.md)
7. [环境验收与故障排查](07-环境验收与故障排查.md)

快速查阅：

- [跨平台工具选择与安装顺序](../跨平台速查/01-工具选择与安装顺序.md)
- [跨平台验证命令](../跨平台速查/02-常用验证命令.md)
- [代理证书与数据安全](../跨平台速查/03-代理证书与数据安全.md)
- [升级、卸载与版本冲突](../跨平台速查/04-升级卸载与版本冲突.md)

## 先确认芯片和系统

```bash
sw_vers
uname -m
arch
sysctl -n machdep.cpu.brand_string 2>/dev/null || true
```

常见结果：

- `arm64`：Apple Silicon 原生终端；
- `x86_64` + Intel CPU：Intel Mac；
- Apple Silicon 机器出现 `x86_64`：当前终端可能通过 Rosetta 运行。

新环境应让 Homebrew、Python、Node、JDK、MySQL 和 Android 模拟器尽量使用同一原生架构。不要在无意识状态下混合：

```text
/opt/homebrew       Apple Silicon Homebrew
/usr/local          Intel Homebrew 或部分 PKG 工具
arm64 包            Apple Silicon 原生
x86_64 包           Intel / Rosetta
```

## 2026 年平台边界

- Homebrew 当前受支持环境从 macOS Sonoma 14 起；
- 当前 PyCharm 版本可能要求 macOS 15 或更新；
- 当前 Playwright Python 版本要求 macOS 14 或更新；
- Android Studio 仍可在部分 Intel Mac 运行，但官方正在逐步退出 Intel 支持；
- Miniconda 已停止发布新的 macOS Intel `osx-64` 包；
- 当前 Xcode App Store 构建可能要求 Apple Silicon 和更高 macOS；
- iOS 自动化必须使用完整 Xcode；Command Line Tools 不够；
- Intel Mac 只能安装与其 macOS 兼容的旧 Xcode，不能保证测试最新 iOS。

如果系统不满足当前官方要求，选择“升级系统/设备”或“固定受支持旧工具链”，不要强行关闭签名、隔离和 Gatekeeper。

## 推荐安装清单

| 优先级 | 工具 | 结论 |
|---|---|---|
| 必装 | Xcode Command Line Tools、Homebrew、Git、Python 3.12、IDE、Apifox | 接口与 Web 自动化基础 |
| Web 自动化 | Playwright；Selenium/Safari 作为对照 | Playwright 浏览器与版本绑定 |
| 服务环境 | Docker Desktop、MySQL 8.4 LTS、DBeaver/Workbench 二选一 | 按芯片下载 |
| Android | Node.js LTS、JDK 21、Android Studio、ADB、Appium 3 | AVD 镜像选 arm64-v8a/x86_64 |
| iOS | 完整 Xcode、Simulator、Appium 3、XCUITest、Inspector | 先模拟器，后真机签名 |
| 性能 | k6 或 JMeter | 只压本机/授权环境 |
| 抓包 | Reqable / Fiddler Everywhere / Charles 三选一 | 不同时启用多个系统代理 |
| 报告 | Allure 3 | 项目本地安装优先 |
| 按需 | Miniconda、Postman、Wireshark、Mockoon、VS Code | 根据课程选择 |

## 完成标准

运行[macOS 环境自检脚本](macOS环境自检.sh)，再按[环境验收与故障排查](07-环境验收与故障排查.md)完成手工验收。自检不会安装或删除软件。
