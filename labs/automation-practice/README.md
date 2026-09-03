# API 与 Web 自动化练习工程

这个工程只负责接口和网页自动化。移动端内容已经迁入独立的 [App 自动化学习工程](../app-automation-learning/README.md)，避免一个项目同时承担三套环境和依赖。

对应学习阶段：

- [接口测试阶段](../../docs/02-接口测试/README.md)
- [UI 自动化阶段](../../docs/03-UI自动化/README.md)
- [自动化框架与质量工程](../../docs/05-质量工程/README.md)

## 1. 安装

```powershell
cd labs\automation-practice
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e '.[all,dev]'
Copy-Item 环境变量示例.env .env
python -m playwright install chromium
```

## 2. 默认执行边界

直接运行：

```powershell
pytest -q
```

不会访问公共 API，也不会打开公共网站。访问第三方练习目标必须显式开启：

```powershell
pytest tests\api -q --run-public-api
pytest tests\web -q --run-public-web
```

本地 Demo Shop 接口联调需要先启动相邻的 `labs/demo-shop`，再设置：

```powershell
$env:DEMO_SHOP_URL='http://127.0.0.1:8000'
pytest tests\api\测试_本地演示商城接口.py -q
```

## 3. 目录职责

```text
labs/automation-practice/
├── pyproject.toml
├── 环境变量示例.env
├── src/qa_learning/
│   ├── 运行配置.py
│   ├── api/                 # Client、Schema 与服务对象
│   └── web/
│       ├── pages/           # 页面定位与行为
│       └── flows/           # 跨页面业务编排
└── tests/
    ├── api/
    └── web/
```

分层规则：

- 配置只描述环境差异；
- Client/Page 封装协议或页面能力；
- Flow 编排业务步骤；
- Test 保留场景和关键断言；
- Fixture 管理隔离、证据和清理。

## 4. 阶段验收

- [ ] 接口 Client 有显式超时和分层断言；
- [ ] CRUD 或本地订单场景能可靠清理；
- [ ] Web 使用语义 Locator 和 Web-first 断言；
- [ ] 每条浏览器测试使用隔离 Context；
- [ ] 公共环境只做低频 smoke，不作为 PR 强门禁；
- [ ] 失败能区分代码、网络、测试数据和目标变化；
- [ ] `ruff check src tests` 与默认离线测试通过。
