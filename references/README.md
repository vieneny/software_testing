# 公开资料索引

本页只收录公开来源，核对日期为 **2026-07-27**。优先级依次为：标准/论文、官方文档、官方 GitHub 仓库、可信行业报告、公开职位样本。链接不等于复制许可；编写教程时应独立表达并核对各项目许可证。

工具版本、产品状态和职位页面都会变化。引用前先检查页面更新时间；发现失效链接时用同一组织的当前官方页面替换，并更新核对日期。

## 分类开源项目参考库

完整的分类项目卡、学习价值、适用场景、难度、迁移状态和作品组合见[开源项目参考库](开源项目参考库/README.md)。本页继续保存标准、论文、官方文档、报告和招聘样本；[精选开源项目学习地图](开源项目学习地图.md)负责少而精的主线，[分类参考库](开源项目参考库/README.md)用于横向比较、进阶选修和项目选型。

## 测试基础与安全

- [ISTQB CTFL 4.0.1 syllabus（PDF）](https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf)：测试活动、风险、设计技术与协作的工具无关框架；
- [OWASP Web Security Testing Guide](https://github.com/OWASP/wstg)：Web 安全测试指南及开源仓库；
- [OWASP API Security Top 10 2023](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)：接口权限、资源、业务流和配置风险；
- [OpenAPI Specification](https://spec.openapis.org/oas/) 与 [GitHub 仓库](https://github.com/OAI/OpenAPI-Specification)：机器可读 API 契约；
- [JSON Schema](https://json-schema.org/learn/getting-started-step-by-step)：JSON 结构验证基础。

## Python 与接口自动化

- [pytest 文档](https://docs.pytest.org/en/stable/) / [pytest GitHub](https://github.com/pytest-dev/pytest)；
- [Requests 文档](https://requests.readthedocs.io/en/stable/) / [Requests GitHub](https://github.com/psf/requests)；
- [HTTPX 文档](https://www.python-httpx.org/)：异步、HTTP/2、ASGI/WSGI 场景的选修；
- [Postman 测试脚本](https://learning.postman.com/docs/tests-and-scripts/write-scripts/test-scripts/)；
- [Postman CLI](https://learning.postman.com/docs/tests-and-scripts/postman-cli-guides/overview/)；
- [从 Newman 迁移到 Postman CLI](https://learning.postman.com/docs/reference/newman-cli/migrate-to-postman-cli/)：解释 Postman v12 / Collection v3 的 2026 取舍；
- [Newman GitHub](https://github.com/postmanlabs/newman)：Collection v2.1 存量项目兼容选修；
- [Schemathesis 文档](https://schemathesis.readthedocs.io/en/stable/)：从 OpenAPI 生成属性测试；
- [WireMock 文档](https://wiremock.org/docs/)：独立 HTTP 服务虚拟化；
- [Pact 工作原理](https://docs.pact.io/getting_started/how_pact_works)：消费者驱动契约测试。

## Web 与移动端 UI 自动化

- [Playwright Python](https://playwright.dev/python/docs/intro) / [playwright-python GitHub](https://github.com/microsoft/playwright-python)；
- [Playwright 定位器](https://playwright.dev/python/docs/locators)、[自动等待](https://playwright.dev/python/docs/actionability)、[Trace Viewer](https://playwright.dev/python/docs/trace-viewer)；
- [Selenium WebDriver](https://www.selenium.dev/documentation/webdriver/) / [Selenium GitHub](https://github.com/SeleniumHQ/selenium)；
- [Appium 文档](https://appium.io/docs/en/latest/) / [Appium GitHub](https://github.com/appium/appium)；
- [Appium UiAutomator2 Driver](https://github.com/appium/appium-uiautomator2-driver)；
- [Appium Android ApiDemos](https://github.com/appium/android-apidemos)：公开 Android 练习应用。
- [Appium XCUITest Driver](https://github.com/appium/appium-xcuitest-driver)；
- [Appium UIKitCatalog](https://github.com/appium/ios-uicatalog)：公开 iOS Simulator 练习应用；
- [Sauce Labs My Demo App Android](https://github.com/saucelabs/my-demo-app-android) /
  [iOS](https://github.com/saucelabs/my-demo-app-ios)：移动电商业务练习；仓库未声明许可证，只按官方条款使用 Release 做个人学习，不复制或再分发；
- [Playwright TodoMVC](https://demo.playwright.dev/todomvc/) 与
  [SauceDemo](https://www.saucedemo.com/)：公开 Web UI 练习；
- [Practice Software Testing / Toolshop](https://github.com/testsmith-io/practice-software-testing)：
  API、Web、Android、iOS 共用业务环境的跨端综合练习项目；当前为受限许可而非开源，禁止商业使用、公开托管、再分发和第三方服务。

## 性能与可观测性

- [Grafana k6 文档](https://grafana.com/docs/k6/latest/) / [k6 GitHub](https://github.com/grafana/k6)；
- [k6 scenarios](https://grafana.com/docs/k6/latest/using-k6/scenarios/) / [thresholds](https://grafana.com/docs/k6/latest/using-k6/thresholds/)；
- [Apache JMeter 用户手册](https://jmeter.apache.org/usermanual/) / [JMeter GitHub](https://github.com/apache/jmeter)；
- [Locust 文档](https://docs.locust.io/en/stable/) / [Locust GitHub](https://github.com/locustio/locust)；
- [OpenTelemetry 文档](https://opentelemetry.io/docs/)：跨 traces、metrics、logs 的可观测性基础；
- [Grafana QuickPizza](https://github.com/grafana/quickpizza)：Grafana 官方组织中的公开 Web/API/k6 练习项目。

## AI 系统质量、评测与安全

- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) / [GenAI Profile 600-1](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence)；
- [ISO/IEC 25059:2023](https://www.iso.org/standard/80655.html)：已发布的 AI 系统质量模型；
- [OWASP LLM Applications Top 10 2025](https://genai.owasp.org/llm-top-10/)；
- [OWASP Agentic Applications Top 10 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)；
- [OWASP GenAI Red Teaming Guide](https://genai.owasp.org/resource/genai-red-teaming-guide/)；
- [MITRE ATLAS](https://atlas.mitre.org/)：AI 系统对抗战术与技术知识库；
- [OpenAI Evaluation Best Practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)：确定性检查、模型评分与人工校准的当前官方方法；
- [OpenAI Evals 平台弃用公告](https://developers.openai.com/api/docs/deprecations#2026-06-03-evals-platform)：2026-10-31 只读、2026-11-30 关闭；
- [OpenAI 官方迁移到 Promptfoo 示例](https://developers.openai.com/cookbook/examples/evaluation/moving-from-openai-evals-to-promptfoo)；
- [Promptfoo GitHub](https://github.com/promptfoo/promptfoo)：跨 provider 评测与红队主线；截至核对日，新环境直接采用 Node.js 24 LTS；
- [DeepEval GitHub](https://github.com/confident-ai/deepeval)：Python / pytest 风格评测选修；
- [Ragas GitHub](https://github.com/vibrantlabsai/ragas) / [指标文档](https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/) / [RAGAS 论文](https://aclanthology.org/2024.eacl-demo.16/)；
- [Inspect AI](https://inspect.aisi.org.uk/)：英国 AI Security Institute 的评测框架；
- [NVIDIA garak](https://github.com/NVIDIA/garak)：LLM 漏洞扫描与红队入口；
- [Arize Phoenix](https://arize.com/docs/phoenix)：开源 tracing、数据集和评测；
- [LangSmith Evaluation Concepts](https://docs.langchain.com/langsmith/evaluation-concepts)：离线与在线评测概念；
- [MT-Bench / LLM-as-a-Judge](https://papers.neurips.cc/paper_files/paper/2023/hash/91f18a1287b398d378ef22505bf41832-Abstract-Datasets_and_Benchmarks.html)：模型裁判及偏差研究；
- [τ-bench](https://arxiv.org/abs/2406.12045) / [τ³-bench（仓库名仍为 tau2-bench）](https://github.com/sierra-research/tau2-bench)：面向工具、环境状态和多轮交互的 Agent 评测；
- [OpenTelemetry GenAI semantic conventions](https://github.com/open-telemetry/semantic-conventions-genai)：仍快速演进，落地时需固定 schema 版本。

## AI 应用与 Agent 开发

- [Spring AI](https://github.com/spring-projects/spring-ai) / [官方示例](https://github.com/spring-projects/spring-ai-examples)：Java AI 应用主线，学习时按官方版本矩阵锁定 Spring Boot 与 BOM；
- [LangChain4j](https://github.com/langchain4j/langchain4j) / [官方示例](https://github.com/langchain4j/langchain4j-examples)：Java 对照路线；
- [Spring AI Alibaba](https://github.com/alibaba/spring-ai-alibaba)：Java Agent/Graph 与国内模型生态选修；
- [LangGraph](https://github.com/langchain-ai/langgraph)：Python 有状态 Agent 工作流；
- [MCP 规范](https://github.com/modelcontextprotocol/modelcontextprotocol)、[Java SDK](https://github.com/modelcontextprotocol/java-sdk) 与 [Python SDK](https://github.com/modelcontextprotocol/python-sdk)；
- [FastAPI](https://github.com/fastapi/fastapi)：Python Agent 后端基础；
- [pgvector](https://github.com/pgvector/pgvector) 与 [Qdrant](https://github.com/qdrant/qdrant)：向量检索主线与进阶对照；
- [Dify](https://github.com/langgenius/dify) 与 [RAGFlow](https://github.com/infiniflow/ragflow)：用于理解 AI 产品与 RAG 架构，使用前核对许可证和资源要求。

两门公开课程的逐项核对、主线/备选/延后项目矩阵、岗位样本和 24 周转岗路线见[测试转人工智能开发模块](../docs/10-测试转人工智能开发/README.md)。课程宣传不作为市场或薪资事实。

## CI/CD 与供应链

- [GitHub Actions：构建和测试 Python](https://docs.github.com/en/actions/tutorials/build-and-test-code/python)；
- [GitHub Actions 安全使用](https://docs.github.com/en/actions/reference/security/secure-use)；
- [Playwright CI](https://playwright.dev/docs/ci)；
- [Allure Report 文档](https://allurereport.org/docs/)：报告与历史趋势的选修方案；
- [Testcontainers 指南](https://testcontainers.com/guides/)：用临时真实依赖做集成测试。

## 市场趋势与公开样本

课程选型不是只按 GitHub star 或单一招聘页面决定。当前中国招聘底座、BOSS 关键词矩阵、26 个 AI 测试去重样本和更新规则见[软件测试与人工智能测试招聘需求调研](../docs/00-学习指南/04-软件测试与人工智能测试招聘需求调研.md)；证据分级和技术选型见[市场需求与技术选型](../docs/00-学习指南/02-市场需求与技术选型.md)。

BOSS 当前公开入口包括：

- [软件测试](https://www.zhipin.com/zhaopin/efc8bd81e959348b0nB429W4EQ~~/)；
- [测试开发](https://www.zhipin.com/zhaopin/5bdec7fdb047c30f1HJ82dS1EA~~/)；
- [性能测试](https://www.zhipin.com/zhaopin/b4750d7f070dd0850XVz3tq4/)；
- [人工智能测试](https://www.zhipin.com/zhaopin/11d8c819f3aba1511nJ429S5Fw~~/)；
- [AI 测试开发](https://www.zhipin.com/zhaopin/2216979552c39d641HR42tS8/)；
- [多模态评测](https://www.zhipin.com/zhaopin/16603fbec8b6c1a61nN42NS5Eg~~/)；
- [AI 应用开发](https://www.zhipin.com/zhaopin/4ad7cfcdefcf1f150nB509y9Fw~~/)；
- [Java AI 应用开发](https://www.zhipin.com/zhaopin/5ac152f5a48008d51n1_39S5/)。

这些页面会下线、换序或个性化，只用于带日期的定性快照。用于交叉验证的公开报告包括：

- [State of Testing 2026](https://www.practitest.com/state-of-testing)；
- [World Quality Report 2025–26](https://www.capgemini.com/in-en/mf_form/revamp-world-quality-report-2025-2026/)；
- [DORA 2025](https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report)；
- [Software Quality Pulse Report](https://www.testrail.com/first-edition-software-quality-pulse-report/)；
- [CNCF Annual Cloud Native Survey](https://www.cncf.io/announcements/2026/01/20/kubernetes-established-as-the-de-facto-operating-system-for-ai-as-production-use-hits-82-in-2025-cncf-annual-cloud-native-survey/)；
- [GitHub Octoverse 2025](https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/)。

调查常有自愿样本、厂商受众和地区偏差；职位页面也会下线。仓库只把它们作为课程取舍证据之一，不从样本推导未经平台完整数据支持的全市场比例、薪资中位数或职位总量。

## 公开练习目标的授权边界

- 优先在本地运行自己创建的 `demo-shop`；
- 可在本地部署 [OWASP Juice Shop](https://github.com/juice-shop/juice-shop) 学习安全测试，但必须遵循项目说明；
- 不对公共演示站、第三方 API、招聘网站或开源项目的在线实例做自动化扫描、性能测试或红队；
- 任何安全或性能测试都先确认资产所有权、书面授权、范围、窗口与停止条件。
