# 软件测试学习与实践知识库

一套面向真实岗位能力、可持续更新、可在本地复现的软件测试学习教程。内容覆盖功能测试、接口测试、接口自动化、Web 与移动端 UI 自动化、性能测试、质量工程，以及生成式 AI / LLM / RAG / Agent 测试和 AI 提效；另设“测试转人工智能开发”模块，衔接 Java AI 应用与 Python Agent 开发。

> 当前路线核对日期：**2026-09-03**。

先看 [项目架构与内容治理](项目架构与内容治理.md)：它说明这套指南如何同时服务计算机专业小白、功能测试转自动化、测试开发拔高、AI 测试和测试转 AI 开发等学习者，以及如何通过公开市场、开源项目、可运行实验和版本核对建立可信度。

## 文件命名约定

仓库自有、可自定义的文件均使用中文名称，方便初学者见名知意。以下名称因代码托管
平台或工具链会自动识别而保留行业约定：`README.md`、`.gitignore`、
`pyproject.toml`、`pom.xml`、`package.json`、`Dockerfile`、`__init__.py` 和
`conftest.py`。Python/Java/TypeScript 源文件、包、类名和环境变量也遵守各语言的
行业规范；强行改成中文会破坏工具链、团队协作和真实岗位学习。面向学习者的教程、
架构说明和自有清单继续使用中文名称。

## 这套教程要解决什么

学习不是记住一堆工具名，而是完成一条可以展示和复现的质量闭环：

```text
理解需求 → 识别风险 → 设计测试 → 执行与取证 → 自动化回归
        → 性能与可靠性验证 → CI 质量门禁 → 线上观测 → 复盘改进
        → 对 AI 系统建立数据集、评测器、安全测试和持续评估
```

完成主线后，你应该能：

- 从需求和系统设计中提取风险，使用边界值、等价类、判定表、状态迁移、组合测试和探索式测试；
- 独立分析 HTTP API，验证鉴权、契约、幂等性、并发、错误处理和数据一致性；
- 用 Python、pytest 与 requests 组织可维护的接口自动化工程；
- 用 Playwright 完成稳定的 Web UI 关键路径测试，理解 Selenium 的适用场景；
- 用 Appium 设计 Android / iOS 的跨平台移动端自动化；
- 将业务目标转换为负载模型，用 k6、JMeter 或 Locust 找到性能风险，而不只是“压一个并发数”；
- 把测试接入 CI/CD，管理测试数据、环境、报告、失败分诊和质量门禁；
- 为 LLM、RAG 和 Agent 建立离线评测集、确定性检查、模型评分、人工复核、安全红队和线上持续评估；
- 安全地使用 AI 辅助需求分析、用例设计、脚本生成和失败归因，并对结果负责。
- 在完成普通后端能力后，使用 Spring AI 或 FastAPI/LangGraph 开发可评测、可观测、权限受控的 RAG 与 Agent 应用；
- 把测试能力转化为开发作品中的自动化测试、故障注入、AI 评测、安全门禁和可靠性证据。

## 主线技术选择

“主线”用于形成一套完整作品；“选修”用于适配不同团队，不要求全部学完。

| 领域 | 建议主线 | 选修 / 对照 | 学习结果 |
|---|---|---|---|
| 功能测试 | 风险驱动 + 探索式测试 + 系统化设计方法 | Pairwise、模型测试、可访问性 | 能解释为什么测、测什么、何时停止 |
| 接口探索 | HTTP、OpenAPI、Postman | curl、Bruno、GraphQL 客户端 | 能定位请求、协议、数据和服务端问题 |
| 接口自动化 | Python + pytest + requests + JSON Schema | Postman CLI、HTTPX、Newman（存量）、Schemathesis、Pact | 可维护、可并行、可进 CI 的测试工程 |
| Web UI | Playwright（Python） | Selenium | 聚焦用户关键旅程，减少脆弱等待与定位器 |
| 移动 UI | Appium 3 | 平台原生框架 | 掌握真机/模拟器、上下文、手势与稳定性治理 |
| 性能 | k6 + 指标/阈值/场景模型 | JMeter、Locust | 从容量问题出发设计并解释测试结果 |
| 质量工程 | Git + CI + Docker 基础 + 可观测性 | 契约测试、服务虚拟化、混沌工程 | 让反馈更快、失败可诊断、门禁可执行 |
| AI 测试 | 数据集 + 多层评测 + 安全测试 + 持续评估 | promptfoo、DeepEval、Ragas、Inspect AI、garak | 评测 LLM/RAG/Agent，而非凭聊天体验判断 |
| 复杂 Python 被测系统 | FastAPI + React + MySQL + Redis | 搜索、对象存储、消息队列 | 构建并测试社区问答系统的完整业务闭环 |
| 复杂 Java 被测系统 | Java 21 + Spring Boot + Vue + MySQL + Redis | RabbitMQ、Spring AI | 构建并测试多租户客服、工单与知识库 |
| AI 应用开发 | Python AI 中间件 + 版本化 HTTP 契约 | Spring AI、LangChain4j、Spring AI Alibaba | 让 Java/Python 业务安全调用可评测、可降级的 AI 能力 |
| Agent 开发 | Python + FastAPI + LangGraph + MCP | OpenAI Agents SDK、Google ADK、Microsoft Agent Framework | 能构建有状态、可恢复、有人审、权限受控的 Agent |

## 按阶段学习

完整目录、项目映射和统一完成方式见 [学习阶段总览](docs/README.md)。不要从工具名或临时课程目录随机跳读。

| 阶段 | 学习入口 | 对应实践 |
|---:|---|---|
| 0 | [环境与测试基础](docs/00-学习指南/README.md) | 本机环境自检与 Git 练习 |
| 1 | [功能测试](docs/01-功能测试/README.md) | [`demo-shop`](labs/demo-shop/README.md) 风险、模型、用例与总结 |
| 2 | [接口测试与自动化](docs/02-接口测试/README.md) | `demo-shop` + [`automation-practice`](labs/automation-practice/README.md) |
| 3 | [Web 与 App UI 自动化](docs/03-UI自动化/README.md) | Playwright 工程 + [`app-automation-learning`](labs/app-automation-learning/README.md) |
| 4 | [性能测试](docs/04-性能测试/README.md) | 负载模型、阈值、监控证据和结论 |
| 5 | [质量工程](docs/05-质量工程/README.md) | CI、数据环境、可观测性与失败分诊 |
| 6 | [AI 测试](docs/06-AI测试/README.md) | 评测集、评分器、安全用例与持续回归 |
| 7 | [综合实战](docs/07-综合实战/README.md) | [复杂系统测试实战](labs/复杂系统测试实战/README.md) |
| 8 | [求职备考](docs/08-求职备考/README.md) | [单文件离线题库](apps/interview-bank/README.md)与模拟复盘 |
| 9 | [测试转 AI 开发](docs/10-测试转人工智能开发/README.md) | Java AI 应用或 Python Agent 项目 |

接口、Web、App 和框架教程已经分别归入对应学习阶段，不再维护平行的“自动化实战”目录。后续加入课程或项目时，先映射能力，再将知识、代码、练习和验收合并到现有阶段。

## 推荐学习节奏

按每周 8～10 小时设计，完整主线约 20 周；有经验可按验收项跳级。

| 阶段 | 周数 | 主题 | 必须交付 |
|---|---:|---|---|
| A | 1～2 | 环境、Git、Linux、网络、SQL、Python 基础 | 环境自检记录与 20 个基础练习 |
| B | 3～5 | 功能测试与测试设计 | 一份风险清单、测试模型、探索式测试记录 |
| C | 6～8 | HTTP、API 探索与接口用例 | 一套含鉴权/异常/幂等/并发的 API 用例 |
| D | 9～11 | pytest 接口自动化 | 可在 CI 运行的接口测试项目和报告 |
| E | 12～14 | Playwright + Appium | Web 关键旅程与至少一个移动端公开 Demo 真正运行 |
| F | 15～16 | 性能测试 | 负载模型、脚本、指标、瓶颈证据与结论 |
| G | 17～18 | CI/CD、数据、环境、可观测性 | 分层流水线与失败分诊手册 |
| H | 19～20 | AI 测试与综合项目 | 评测集、评分规则、安全用例和项目复盘 |

每一阶段都按同一个循环学习：

1. 用自己的话解释概念和适用边界；
2. 在 `demo-shop` 或公开练习服务上运行最小示例；
3. 主动制造一个失败并保留诊断证据；
4. 把重复步骤自动化；
5. 写出结论、限制和下一步，而不只贴截图；
6. 按阶段验收清单自评，未通过就补实验。

## 快速开始综合实验

```bash
cd labs/demo-shop
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
uvicorn app.商城服务:app --host 127.0.0.1 --port 8000
```

另开一个终端：

```bash
cd labs/demo-shop
source .venv/bin/activate
pytest tests/api tests/ai -q
```

UI 和性能实验需要额外依赖，具体命令见 [实验说明](labs/demo-shop/README.md)。示例只监听本机回环地址，数据全部在内存中，重启服务即可重置。

## 内容维护规则

- 普通测试岗位每季度、AI 测试与 Agent/评测岗位每月检查一次 BOSS 公开样本；工具状态、官方链接和学习路线至少每季度复核；
- 工具热度不是唯一标准，优先选择可迁移的原理与能形成闭环的主线；
- 新工具先放入选修，完成真实实验和对比后再决定是否进入主线；
- 引用数据必须标明来源与核对日期；无法获得可靠统计时，只写“样本观察”，不伪造百分比；
- 所有教程以可运行实验和明确验收项结束；
- 不直接推送未经复核的 AI 生成内容。

欢迎通过 Issue 提出勘误或学习需求。
