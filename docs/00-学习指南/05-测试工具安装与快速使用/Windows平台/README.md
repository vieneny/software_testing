# Windows 测试工具安装与快速使用

> 核对日期：**2026-07-27**。主线面向 Windows 11 x64。Windows 10、Windows ARM64 或受企业策略管理的电脑，必须逐项核对官方支持矩阵。

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

## Windows 版本和架构

在“设置 → 系统 → 系统信息”确认：

- Windows 版本和 OS 内部版本；
- 系统类型是 x64 还是 ARM64；
- 可用内存和磁盘；
- 是否有管理员权限；
- BIOS/UEFI 是否启用虚拟化。

也可在 PowerShell 执行：

```powershell
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsBuildNumber, OsArchitecture
$env:PROCESSOR_ARCHITECTURE
systeminfo.exe
```

2026 年的几个重要变化：

- 新版 MySQL Community Server 官方支持矩阵只列 Windows 11 x86_64，不应假设 Windows 10/ARM64 受支持；
- Anaconda 已停止为 Windows 10 发布新的仓库包；
- Android Studio 的 Windows ARM CPU 版本目前不在官方支持范围；
- Docker Desktop 的 Windows ARM 版本仍可能处于不同支持阶段；
- Playwright 的当前 Python 版本要求 Windows 11 或受支持的 Windows Server。

如果电脑是 Windows 10，不要靠“安装器能打开”判断兼容。可选择升级 Windows、使用官方支持的旧版本并固定依赖，或在另一台受支持环境学习。

## 推荐安装清单

| 优先级 | 工具 | 结论 |
|---|---|---|
| 必装 | Git、Python 3.12、PyCharm 或 VS Code、Apifox | 接口与 Web 自动化起步 |
| Web 自动化 | Playwright；Selenium 作为对照 | 不手工维护浏览器驱动 |
| 服务环境 | Docker Desktop、MySQL 8.4 LTS、DBeaver/Workbench 二选一 | 需要数据库和复杂系统时安装 |
| Android | Node.js LTS、JDK 21、Android Studio、ADB、Appium 3、Inspector | 有真机或模拟器时安装 |
| 性能 | k6 或 JMeter | 只压本机/授权环境 |
| 抓包 | Reqable / Fiddler Everywhere / Charles 三选一 | 不同时启用多个系统代理 |
| 报告 | Allure 3 | 有展示和历史分析需要时再装 |
| 按需 | Miniconda、Postman、Wireshark、Mockoon | 根据课程或团队栈选择 |

## 推荐目录

教程默认在当前用户目录下创建工作区，所有电脑都有这一位置：

```text
%USERPROFILE%\
├─ workspace\          # 学习项目
├─ tools\              # 免安装工具、JMeter 等
├─ test-data\          # 仅公开/合成数据
└─ test-output\        # 临时报告、日志、抓包
```

PowerShell 中用 `Join-Path $HOME "workspace"` 生成实际路径。若电脑有专用数据盘，
可自行改到 `D:\workspace`，但不要直接复制一个本机不存在的盘符。

路径中出现中文并不一定错误，但旧 Java、Android、构建和脚本工具对空格、非 ASCII 字符和超长路径的兼容性不一致。教程建议先使用短路径，掌握后再验证边界。

## 完成标准

完成全部必装项后运行[Windows 环境自检脚本](Windows环境自检.ps1)，再按[环境验收与故障排查](07-环境验收与故障排查.md)完成手工验收。
