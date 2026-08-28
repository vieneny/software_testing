# 测试工具安装与快速使用知识库

> 官方资料核对日期：**2026-07-27**。

这套知识库解决三个常见问题：

1. 新电脑应该先装什么，哪些工具其实互为替代；
2. Windows 与 macOS 的安装、环境变量和权限差异；
3. 安装成功后怎样做一个最小实验，而不是只看到桌面图标就结束。

## 先选择你的平台

- [Windows 平台完整教程](Windows平台/README.md)
- [macOS 平台完整教程](macOS平台/README.md)
- [跨平台工具选择与安装顺序](跨平台速查/01-工具选择与安装顺序.md)
- [跨平台常用验证命令](跨平台速查/02-常用验证命令.md)
- [代理证书、抓包与数据安全](跨平台速查/03-代理证书与数据安全.md)
- [升级、卸载与版本冲突处理](跨平台速查/04-升级卸载与版本冲突.md)

## 内容分类

| 分类 | 主要工具 | 你会完成什么 |
|---|---|---|
| 安装前准备 | PowerShell、WinGet、Terminal、Homebrew、Git | 确认系统/芯片，建立可信下载和版本记录习惯 |
| 编程环境 | Python、venv、Conda、PyCharm、Node.js、npm、JDK、VS Code | 建立 Python、JavaScript、Java 三条自动化运行链 |
| 数据与服务 | MySQL、MySQL Workbench、DBeaver、Docker Desktop、Redis（容器） | 建库、查询、连接、重置公开练习数据 |
| 接口与抓包 | Apifox、Postman、Reqable、Fiddler、Charles、Wireshark、Mockoon | 发请求、加断言、做 Mock、分析 HTTP/HTTPS 和基础网络问题 |
| Web 自动化 | Playwright、Selenium、Chrome、Edge、Safari | 运行首个浏览器脚本并理解驱动管理 |
| 移动自动化 | Android Studio、SDK、ADB、Appium 3、UiAutomator2、XCUITest、Appium Inspector | 连接模拟器或真机，完成环境诊断和首个会话 |
| 性能与报告 | JMeter、k6、Allure Report | 运行低负载练习、设置阈值、生成可阅读报告 |

## 版本策略

安装软件时会遇到两种“正确版本”：

- **官方当前版本**：适合新建独立实验，但可能刚发布，第三方插件尚未完全兼容；
- **项目推荐基线**：以本仓库示例能稳定运行、仍在安全支持期内为准。

本仓库当前建议：

| 运行时 / 工具 | 推荐基线 | 原因 |
|---|---|---|
| Python | 3.12 | 生态兼容性好；不要修改系统自带 Python |
| Node.js | 24 LTS | Appium 3 与现代前端工具可用；存量项目按锁文件降级 |
| Java | Temurin JDK 21 LTS | 适配本仓库 Spring Boot、JMeter 和常见测试工具 |
| MySQL | 8.4 LTS | 与大量企业项目和本仓库练习兼容；新 LTS 先做兼容验证 |
| Appium | 3.x | 新项目主线；Appium 2 仅用于存量兼容 |
| Allure | 3.x | 新项目主线；Allure 2 仍可用于已有流水线 |

版本号会持续变化。执行安装前先打开文中官方链接，核对：

1. 操作系统最低版本；
2. Intel / AMD、Windows ARM64、Mac Intel、Apple Silicon 架构；
3. LTS、Stable、Current、Preview 或 Canary 渠道；
4. 项目自身的 `pyproject.toml`、`package.json`、`pom.xml`、锁文件和 CI 镜像版本。

## 不要一次全部安装

面向初学者的推荐顺序：

1. Git、终端、编辑器；
2. Python 3.12 + `venv`，或 Miniconda 二选一作为当前项目环境；
3. Apifox；
4. Playwright；
5. Docker Desktop + MySQL；
6. Android Studio + ADB + Appium 3；
7. JDK + JMeter 或 k6；
8. 抓包工具按场景选一个；
9. 需要漂亮报告时再装 Allure。

同类工具不需要全装：

- PyCharm 与 VS Code 都能写 Python，先选一个；
- MySQL Workbench 与 DBeaver 都能管理 MySQL，先选一个；
- Apifox 与 Postman 都能做接口探索，国内学习主线可先用 Apifox；
- Reqable、Fiddler Everywhere、Charles 都能做 HTTP(S) 抓包，先选一个；
- Selenium 与 Playwright 都能做 Web 自动化，主线先学 Playwright；
- JMeter 与 k6 都能做性能测试，先根据团队技术栈选一个。

## 每个工具的统一验收标准

不能以“安装程序执行完了”为验收。每个工具至少完成：

```text
官方来源可追溯
→ 命令或关于页面能显示版本
→ 最小公开实验成功
→ 主动制造一个失败并能定位
→ 知道配置、缓存和日志在哪里
→ 知道怎样升级、卸载和清理证书
```

建议把结果记录成：

```markdown
- 系统与芯片：
- 工具、版本与下载来源：
- 安装方式：
- 验证命令与结果：
- 最小实验：
- 主动制造的失败：
- 解决方法：
- 配置 / 缓存位置：
- 下一次复核日期：
```

## 安全红线

- 只测试本机靶场、公开专用测试站点或你明确拥有授权的系统；
- 不对公共演示站执行并发压测；
- 不把公司的接口文档、域名、请求、HAR、SAZ、会话、Cookie、Token、证书或数据库连接同步到个人 SaaS 账号；
- HTTPS 解密证书只装到个人测试设备和专用测试用户，练习后移除；
- 不关闭证书校验作为长期解决方案；
- 不把 `.env`、数据库备份、抓包文件、测试报告和设备日志提交到 Git。

详细操作见[代理证书、抓包与数据安全](跨平台速查/03-代理证书与数据安全.md)。

## 官方资料入口

本知识库的安装事实优先来自各项目官方文档。重要入口包括：

- [Python](https://www.python.org/downloads/)
- [PyCharm](https://www.jetbrains.com/help/pycharm/installation-guide.html)
- [Node.js](https://nodejs.org/en/download)
- [Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/main)
- [MySQL](https://dev.mysql.com/downloads/mysql/)
- [Apifox](https://docs.apifox.com/download)
- [Reqable](https://reqable.com/en-US/download/)
- [Fiddler](https://www.telerik.com/fiddler)
- [Charles](https://www.charlesproxy.com/documentation/)
- [Android Studio](https://developer.android.com/studio/install)
- [Appium](https://appium.io/docs/en/latest/quickstart/)
- [Playwright Python](https://playwright.dev/python/docs/intro)
- [Selenium](https://www.selenium.dev/documentation/)
- [JMeter](https://jmeter.apache.org/usermanual/get-started.html)
- [k6](https://grafana.com/docs/k6/latest/set-up/install-k6/)
- [Allure Report](https://allurereport.org/docs/)

文中出现的第三方包管理器只是便捷安装渠道。涉及证书、驱动、内核扩展或公司设备策略时，以操作系统、工具厂商和组织安全策略为准。
