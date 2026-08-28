# 开源项目参考库

核对日期：**2026-07-27**。

这个目录不是 GitHub 收藏夹，而是本仓库的“公开工程样本库”。它把已经在教程中引用的项目和适合继续深入的高价值项目统一分类，并回答四个问题：

1. 项目里面有什么；
2. 可以拿它做什么；
3. 值得学习什么；
4. 在本仓库哪条路线、哪个阶段使用。

仓库原有的[精选开源项目学习地图](../开源项目学习地图.md)继续承担“少而精的主线推荐”；本目录承担“分类查阅、横向比较和进阶选修”。初学者不需要把这里的项目全部安装一遍。

## 目录

| 专题 | 主要内容 | 对应本仓库模块 |
|---|---|---|
| [测试基础与接口自动化](01-测试基础与接口自动化.md) | pytest、属性测试、API 客户端、契约、Mock、服务虚拟化和集成测试 | 功能测试、接口测试、接口自动化 |
| [网页与移动端自动化](02-网页与移动端自动化.md) | Playwright、Selenium、Appium、Android/iOS、可访问性和视觉回归 | Web、Android、iOS UI 自动化 |
| [性能可靠性与可观测性](03-性能可靠性与可观测性.md) | k6、JMeter、Locust、AI 推理压测、OpenTelemetry 和故障注入 | 性能测试、稳定性、质量工程 |
| [测试管理报告与持续集成](04-测试管理报告与持续集成.md) | Allure、ReportPortal、Kiwi TCMS、Jenkins、并行执行和安全门禁 | 测试开发、CI/CD、质量平台 |
| [公开练习应用与安全靶场](05-公开练习应用与安全靶场.md) | API、Web、Android、iOS、微服务和安全练习目标 | 全链路实战、作品集 |
| [人工智能测试与模型评测](06-人工智能测试与模型评测.md) | LLM/RAG 评测、模型 Benchmark、多模态、传统机器学习质量和数据质量 | AI 应用测试、模型评测 |
| [智能体测试安全与评测基准](07-智能体测试安全与评测基准.md) | 工具调用、终态、轨迹、Computer Use、红队和持续评估 | Agent 测试、AI 安全、评测平台 |
| [人工智能提效与测试智能体](08-人工智能提效与测试智能体.md) | AI UI 自动化、测试 Agent、代码助手、PR 审查和效果验证 | AI 提效、AI 原生测试 |
| [人工智能应用与智能体开发](09-人工智能应用与智能体开发.md) | Java/Python AI 应用、RAG、MCP、Agent、向量数据库和模型服务 | 测试转 AI 应用/Agent 开发 |
| [推荐学习组合与项目选型](10-推荐学习组合与项目选型.md) | 按人群的学习顺序、作品组合、选型评分和维护规则 | 学习路线、求职作品 |

## 标记说明

### 推荐级别

- **核心**：本仓库主线会真正运行，并形成作品证据；
- **按岗选修**：目标岗位或技术栈要求时选择，不与主线重复建设；
- **架构阅读**：重点学习设计、测试、CI 或评测思想，不要求完整部署；
- **迁移参考**：项目仍有历史价值，但已进入维护、迁移或被新项目替代，不作为新工程默认选择。

### 难度

- **L0**：计算机基础小白可在引导下使用；
- **L1**：会命令行、Git、HTTP 或一门编程语言；
- **L2**：能维护自动化工程，理解数据、环境和 CI；
- **L3**：需要性能、安全、分布式系统、机器学习或 Agent 基础；
- **L4**：需要复杂分布式环境、GPU、评测平台或较强的故障排查能力；
- **L5**：研究级或重资源基准，通常还需要虚拟机集群、专用数据集或严格的安全隔离。

### 开源状态

本目录优先收录许可证明确的开源项目。少量行业常用项目属于“源码可见、开放核心或混合许可”，会在对应项目的“定位”“许可提示”或紧邻说明中逐项标注，不能因为代码能在 GitHub 阅读就称为无限制开源。正式使用前必须重新检查当前：

- `LICENSE`、`NOTICE`、商标和第三方依赖；
- 是否存在 `ee/`、企业插件或附加条款；
- 是否允许修改、再分发、SaaS 和多租户托管；
- 模型权重、数据集和 Demo 素材是否有独立许可证。

## 最值得先学的项目

下面不是星标排名，而是按本仓库的完整能力链选择的第一批项目。

| 项目 | 为什么值得先学 | 最小学习结果 |
|---|---|---|
| [pytest](https://github.com/pytest-dev/pytest) | Python 自动化主线和大量 AI 评测工具的工程基础 | fixture、参数化、marker、hook、失败诊断和 JUnit 报告 |
| [Requests](https://github.com/psf/requests) | 最清晰的同步 HTTP 客户端学习入口 | 可复用 API Client、超时、认证、异常和日志脱敏 |
| [Schemathesis](https://github.com/schemathesis/schemathesis) | 把 OpenAPI 契约转换成生成式 API 测试 | 发现边界问题、缩小失败样本、保存回归案例 |
| [WireMock](https://github.com/wiremock/wiremock) | 学习服务虚拟化、失败注入和第三方依赖隔离 | 模拟延迟、429、500、坏 JSON、断流和有状态场景 |
| [Pact](https://github.com/pact-foundation) | 学习消费者驱动契约和跨团队接口演进 | 消费者契约、Provider 验证和版本兼容策略 |
| [Testcontainers](https://github.com/testcontainers) | 用临时真实依赖替代脆弱的共享测试环境 | 自动启动数据库/队列、隔离数据并可靠清理 |
| [Playwright](https://github.com/microsoft/playwright) | 现代 Web 自动化、等待、隔离和失败取证能力完整 | 关键旅程、Trace、网络控制和 CI 并行 |
| [Appium](https://github.com/appium/appium) | Android 与 iOS 跨平台移动自动化主线 | 真机/模拟器、Driver、手势、权限、WebView 和证据 |
| [k6](https://github.com/grafana/k6) | 代码化性能场景、阈值和 CI 门禁清晰 | 负载模型、p95、错误率、容量结论和退出码 |
| [OpenTelemetry](https://github.com/open-telemetry) | 把测试请求与服务端 trace、metric、log 连接起来 | 端到端定位慢请求、错误依赖和 Agent 工具调用 |
| [Allure 3](https://github.com/allure-framework/allure3) | 学习结果模型、附件、分类和可读报告 | 将 pytest/Playwright/Appium 证据组织成可复核报告 |
| [Practice Software Testing](https://github.com/testsmith-io/practice-software-testing) | **受限许可公开练习项目，不属于开源软件**；API、Web、Android、iOS 共用业务数据 | 在其许可范围内完成跨端 Capstone；不得商业使用、公开托管、再分发或作为第三方服务 |
| [OWASP Juice Shop](https://github.com/juice-shop/juice-shop) | 安全测试与业务功能结合的成熟本地靶场 | 威胁模型、漏洞验证、修复回归和授权边界 |
| [Promptfoo](https://github.com/promptfoo/promptfoo) | LLM 应用评测、跨模型比较、CI 与红队的低门槛主线 | 版本化评测集、断言、切片、安全门禁和基线比较 |
| [DeepEval](https://github.com/confident-ai/deepeval) | Python/pytest 思维容易迁移到 LLM、RAG 与 Agent | 自定义指标、对话评测、工具调用评测和回归阈值 |
| [Ragas](https://github.com/vibrantlabsai/ragas) | RAG 数据生成、检索与生成质量评测的代表项目 | Recall、上下文质量、忠实度和人工校准 |
| [Inspect AI](https://github.com/UKGovernmentBEIS/inspect_ai) | 任务、solver、scorer、sandbox 的高阶评测框架 | 可复现任务、受控执行、多次运行和安全评测 |
| [garak](https://github.com/NVIDIA/garak) | 生成式 AI 漏洞扫描和插件化红队入口 | 在本地靶场运行有限 probe、人工复核并做修复回归 |
| [τ³-bench](https://github.com/sierra-research/tau2-bench) | 以工具、环境终态、多轮和多次运行评测 Agent | 状态可重置的 Mock 环境、轨迹与任务成功率 |
| [Phoenix](https://github.com/Arize-ai/phoenix) | AI Trace、数据集、实验和评测平台样本；**Elastic License 2.0，源码可见但非 OSI 开源** | 定位错误检索、错误工具调用、延迟和成本问题 |
| [Spring AI](https://github.com/spring-projects/spring-ai) | Java AI 应用、RAG、工具调用和 MCP 主线 | 有测试、评测、观测和异常治理的 Java AI 服务 |
| [LangGraph](https://github.com/langchain-ai/langgraph) | 有状态、可恢复、有人审的 Agent 工作流主线 | 状态图、checkpoint、预算、工具边界和失败恢复 |
| [MCP 规范与 SDK](https://github.com/modelcontextprotocol) | 当前 Agent 工具互操作的重要开放协议生态 | 只读工具、Schema、超时、授权和契约测试 |

## 正确使用方式

对每个真正要学习的项目执行同一套流程：

1. 确认官方仓库、维护状态、稳定版本和许可证；
2. 只克隆到独立个人学习目录，记录 tag 或 commit；
3. 按官方最小示例运行一次；
4. 找到项目自己的一个测试，解释 setup、action、oracle、cleanup；
5. 主动制造一个失败，保存日志、trace 或报告；
6. 将一个概念迁移到本仓库的虚构 `demo-shop` 或本地 Mock；
7. 写出取舍、限制和可复现命令，而不是复制原项目大段源码。

## 数据、授权和安全边界

- 只使用公开项目、公开文档和自己生成的合成数据；
- 公共 Demo 只做低频功能验证；自动化回归优先本地部署；
- 性能、安全、红队和故障注入只能针对自己拥有或书面授权的实例；
- 发现开源项目安全问题时遵守其 `SECURITY.md`，不公开利用细节。
