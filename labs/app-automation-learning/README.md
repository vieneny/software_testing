# App 自动化学习工程

这是 [App 自动化学习阶段](../../docs/03-UI自动化/02-App自动化学习阶段/README.md) 的唯一配套工程。它把课程中的登录、搜索、购物车、订单、Page Object、pytest fixture、数据驱动、证据和 CI 组织成两条明确的执行通道。

| 通道 | 默认运行 | 用途 | 能证明什么 |
|---|---|---|---|
| 离线项目逻辑 | 是 | 合成商城、平台契约、Flow、故障、证据、清理 | 代码结构和业务编排可重复 |
| Appium 真机 smoke | 否，需 `--run-mobile` | ApiDemos / My Demo App / UIKitCatalog | 真实 Session、元素树和设备交互 |

## 1. 从零运行

```powershell
cd labs\app-automation-learning
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e '.[all]'
pytest -q
```

默认命令不会创建 Appium Session。建议按顺序阅读：

```text
mobile/course_project.py
  → tests/unit/test_course_purchase_flow.py
  → mobile/mock/移动端契约.py
  → mobile/mock/假移动端驱动.py
  → mobile/mock/运行装配.py
  → tests/unit/测试_离线移动端*.py
```

## 2. 课程业务流

`course_project.py` 将完整流程拆成五个可观察状态：

```text
STARTED → AUTHENTICATED → SEARCHED → CART_READY → ORDERED
```

对应测试覆盖：

- 正常登录、搜索、加购和结算；
- 登录失败后不继续搜索；
- 搜索无结果；
- 数量下界和库存上界；
- 同一幂等键不重复创建订单；
- 不允许绕过页面状态直接结算。

真实项目中，`SyntheticCommerceApp` 的方法由 Screen/Flow 通过 Appium 实现；测试的业务断言和状态约束不应消失。

## 3. 运行 Appium smoke

安装移动端依赖并复制配置：

```powershell
python -m pip install -e '.[all]'
Copy-Item .env.example .env
```

在 `.env` 填写明确的 App 路径和设备 UDID，然后检查：

```powershell
appium --version
appium driver list --installed
adb devices -l
```

启动 Appium 后，只运行已准备的平台：

```powershell
pytest tests\mobile -q -m android --run-mobile
pytest tests\mobile -q -m ios --run-mobile
```

iOS 命令只在 macOS、Xcode、Simulator/WDA 已配置时执行。没有 `--run-mobile` 时，所有 `device` 测试会在导入 Appium 和创建 Session 前跳过。

## 4. 工程结构

```text
labs/app-automation-learning/
├── .env.example
├── pyproject.toml
├── scripts/下载公开演示应用.sh
├── src/qa_learning/
│   ├── 运行配置.py
│   └── mobile/
│       ├── course_project.py
│       ├── 移动端驱动工厂.py
│       ├── screens/
│       └── mock/
└── tests/
    ├── conftest.py
    ├── unit/
    └── mobile/
```

学习阶段的每一章都指向这里的具体文件和测试。不要另外复制一份课堂工程；后续增加新的 App 项目时，先提取可迁移能力，再扩展本工程的 Profile、Screen、Flow 和验收用例。
