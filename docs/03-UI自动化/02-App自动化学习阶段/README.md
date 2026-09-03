# App 自动化学习阶段：从项目逻辑到 Appium 真机

> 适用对象：会一点 Python 或手工测试，希望快速理解一个企业级 App 自动化项目如何从单条脚本演进为可维护工程的学习者。
>
> 配套工程：[`labs/app-automation-learning`](../../../labs/app-automation-learning/README.md)
>
> 内容核对日期：2026-09-03。Appium、平台 Driver 和公开练习 App 会持续变化，运行前以官方文档和 Release 为准。

本阶段将一套三天 Appium 课程中的完整项目重新组织成可执行学习路线。它不复制课堂工程，而是把环境、定位、业务流、Page Object、pytest、数据驱动、失败证据和 CI 串成一条主线，并由一套独立工程承载所有代码练习。

## 阶段导航

| 顺序 | 章节 | 学完后的可验证产物 |
|---:|---|---|
| 1 | [环境、ADB 与 Session](./01-环境ADB与Session.md) | 版本清单、目标设备清单、首个可释放 Session |
| 2 | [元素定位、等待与手势](./02-元素定位等待与手势.md) | Locator 清单、页面状态等待、有限滑动 |
| 3 | [项目结构与 Page Object](./03-项目结构与PageObject.md) | Driver、Base Screen、Screen、Flow、Test 分层图 |
| 4 | [业务流程与数据驱动](./04-业务流程与数据驱动.md) | 登录、搜索、购物车、订单的独立测试与关键旅程 |
| 5 | [Fixture、失败证据与报告](./05-Fixture失败证据与报告.md) | 首次失败证据包、可靠清理、Allure 报告 |
| 6 | [CI、真机矩阵与故障排查](./06-CI真机矩阵与故障排查.md) | 分层流水线、设备矩阵、逐层排障记录 |

完成后，你应当能够独立回答四个问题：

1. 一次 Appium 操作经过哪些组件，失败应从哪一层排查？
2. 登录、搜索、购物车和订单如何拆成 Screen、Flow、Fixture 与 Test？
3. 如何让用例不依赖固定等待、历史登录状态和执行顺序？
4. 如何用截图、Page Source、Appium 日志和受控设备日志说明失败原因？

## 1. 放在整个仓库中的位置

这是一条“快速建立全局认识”的路线，不替代详细专题：

```text
本模块：3 天快速学习项目逻辑
  ├─ 无设备：运行 App Mock，先学框架和失败恢复
  ├─ Android：连接 UiAutomator2，验证真实元素树与设备行为
  ├─ iOS：连接 XCUITest/WDA，验证 Simulator 或真机行为
  └─ 进阶：数据治理、证据、CI、跨端项目与故障排查
```

推荐使用方式：

- 第一次接触 App 自动化：完整按 Day 1 → Day 2 → Day 3 学习；
- 当前没有设备：先执行离线 App Mock，再读真机章节；
- 已经写过 Appium 脚本：重点检查第 6、8、10、11 节；
- 准备作品集：完成第 12 节交付物，不只展示通过截图。

## 2. 三天学习地图

| 阶段 | 核心问题 | 实践产物 | 验收重点 |
|---|---|---|---|
| Day 1：连通与操作 | Python 如何经过 Appium 控制指定设备和 App？ | 环境清单、首个 Session、定位实验、显式等待 | 能区分客户端、Server、Driver、ADB 与 App 状态 |
| Day 2：分层与业务 | 如何把单页面脚本改造成可维护项目？ | Base Screen、页面对象、fixture、数据集、登录与搜索流 | Test 只表达意图，页面细节不散落 |
| Day 3：闭环与工程化 | 如何完成购物车/订单并让失败可诊断？ | 业务 Flow、失败证据、报告、CI 分层与复盘 | 状态隔离、关键断言、证据和清理完整 |

每天都遵循同一循环：

```text
理解链路 → 跑通最小示例 → 主动制造失败 → 定位根因 → 重构 → 留下验收证据
```

不要第一天就复制一个完整框架。只有理解 Session、元素状态和页面切换后，分层才是在消除复杂度，而不是增加目录。

## 3. 开始前：选择练习路径

### 路径 A：无设备，先练项目逻辑

进入 `labs/app-automation-learning`，安装基础与开发依赖：

```powershell
cd labs\app-automation-learning
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e '.[all]'
pytest tests\unit -q
```

这条路径能验证项目结构、业务编排、故障注入、证据顺序和清理，但不能证明 ADB、真实 UI、安装包或设备兼容性。

### 路径 B：Android 真机或模拟器

使用官方公开练习 App，按 [环境、ADB 与 Session](./01-环境ADB与Session.md)准备环境。最少检查：

```powershell
node --version
appium --version
appium driver list --installed
appium driver doctor uiautomator2
adb version
adb devices -l
python --version
```

`adb devices -l` 中目标必须是 `device`。出现多个设备时显式填写 `MOBILE_UDID`，不要让脚本猜测目标。

### 路径 C：iOS Simulator 或真机

iOS 自动化需要 macOS、Xcode、XCUITest Driver 和 WDA。先读 [CI、真机矩阵与故障排查](./06-CI真机矩阵与故障排查.md)中的 iOS 边界，不要在 Windows 上尝试绕过平台限制。

## 4. Day 1：先理解控制链路

Appium 不是 Python 直接操作手机。Android 的一次点击通常经过：

```text
pytest / Appium Python Client
       ↓ W3C WebDriver 请求
Appium 3 Server
       ↓ 根据 automationName 路由
UiAutomator2 Driver
       ↓ ADB + 设备端 instrumentation
Android 设备
       ↓
公开练习 App（AUT）
```

据此判断常见失败：

| 现象 | 优先检查 |
|---|---|
| Python 无法导入 `appium` | 虚拟环境与客户端依赖 |
| 找不到 `automationName` 对应驱动 | Appium Driver 是否安装、版本是否兼容 |
| `unauthorized` / `offline` | USB 调试授权、数据线、ADB Server |
| Session 建立失败 | App 路径、UDID、包名/Activity、W3C capabilities |
| Session 成功但元素找不到 | 页面状态、弹窗、Context、定位器和等待条件 |

### 4.1 ADB 只掌握够用的命令

```powershell
adb devices -l
adb -s <UDID> shell pm list packages -3
adb -s <UDID> shell dumpsys window | findstr mCurrentFocus
adb -s <UDID> shell am force-stop <PACKAGE>
adb -s <UDID> shell am start -W <PACKAGE>/<ACTIVITY>
adb -s <UDID> install -r <APK绝对路径>
adb -s <UDID> pull <设备文件> <本地目录>
```

始终带 `-s <UDID>` 可以让命令和自动化配置指向同一台设备。`logcat` 输出量很大，排障时限定时间、进程或标签，并只保存在本地运行产物目录。

### 4.2 建立第一个安全 Session

本仓库的实现位于 `labs/app-automation-learning/src/qa_learning/mobile/移动端驱动工厂.py`。它要求绝对 App 路径和明确 UDID，并只接受仓库支持的公开练习 Profile。

核心形式如下：

```python
from appium import webdriver
from appium.options.android import UiAutomator2Options

options = UiAutomator2Options().load_capabilities(
    {
        "platformName": "Android",
        "appium:automationName": "UiAutomator2",
        "appium:udid": "emulator-5554",
        "appium:app": r"C:\mobile-apps\ApiDemos-debug.apk",
        "appium:noReset": False,
    }
)

driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
try:
    # 在这里执行最小 smoke
    pass
finally:
    driver.quit()
```

关键点：

- Appium 3 默认服务基路径是 `/`，不要机械复制旧教程的 `/wd/hub`；
- 扩展能力使用 `appium:` 前缀，Python Options 会负责规范化；
- 初学阶段使用 `noReset=False`，让用例不依赖历史登录状态；
- `quit()` 必须位于 fixture teardown 或 `finally` 中；
- Server 只监听本机，不开启不需要的宽松安全能力。

### 4.3 用 Inspector 建立定位认知

Appium Inspector 用于查看当前页面元素树、属性和定位结果。先确认 Inspector 的 Session 配置与测试代码一致，再按以下顺序选择定位器：

1. Accessibility ID：语义清晰，通常最稳定；
2. Android `resource-id`；
3. Android UIAutomator / iOS Predicate 或 Class Chain；
4. 短且有明确语义的 XPath；
5. 坐标只作为画布等无元素树场景的最后方案。

当 `resource-id` 重复时，不要直接换成长 XPath。先结合可访问名称、父子关系、页面区域或唯一业务状态缩小范围，并和开发讨论增加稳定测试标识。

## 5. Day 1：等待的是状态，不是时间

固定 `sleep(5)` 既可能浪费时间，也可能仍然不够。页面对象应等待可观察条件：

```python
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

def wait_clickable(driver, locator, timeout=15):
    return WebDriverWait(driver, timeout).until(
        ec.element_to_be_clickable(locator)
    )
```

根据操作选择条件：

| 操作 | 合适条件 |
|---|---|
| 读取文本 | `visibility_of_element_located` |
| 点击按钮 | `element_to_be_clickable` |
| 等待加载结束 | `invisibility_of_element_located` |
| Toast | `presence_of_element_located`，并使用较短轮询间隔 |
| 页面跳转 | 目标页面唯一标识出现，或旧标识消失 |
| Hybrid 切换 | 目标 `WEBVIEW` Context 出现在 `driver.contexts` |

广告、更新提醒和权限弹窗属于状态分支。将“如果出现则按预期处理”封装为小方法；不要用捕获所有异常后继续执行来掩盖真正的定位失败。

## 6. Day 2：从脚本升级为项目

推荐目录与仓库现有工程一致：

```text
mobile automation
├── configuration/          # 环境变量解析、Profile 和前置校验
├── drivers/                # Android/iOS Session 创建
├── screens/                # 定位器、页面状态和原子交互
├── flows/                  # 登录、搜索、购物车、订单等业务编排
├── data/                   # 合成测试数据与 schema
├── evidence/               # 失败证据采集与脱敏
├── tests/
│   ├── unit/               # 无设备的契约和 Flow 测试
│   └── mobile/             # 显式开启的真机 smoke
└── conftest.py             # Session、状态准备、证据和清理
```

各层职责要保持单向：

| 层 | 应该做 | 不应该做 |
|---|---|---|
| Driver Factory | 校验配置并创建一个 Session | 猜设备、顺便执行业务步骤 |
| Base Screen | 等待、点击、输入、有限滑动、截图 | 放所有页面定位器和完整业务 |
| Screen/Page | 保存本页面定位器和可复用行为 | 写测试数据、启动 Driver |
| Flow | 串联多个页面形成业务任务 | 吞掉异常、替 Test 决定所有断言 |
| Test | 表达场景、关键断言与预期 | 散落 XPath、固定等待和环境细节 |
| Fixture | 准备独立状态、失败取证、清理 Session | 依赖上一条用例留下的状态 |

一个“小而全”的 `BasePage` 很容易继续膨胀。只有多个 Screen 真正共享的协议级操作才放入 Base；“加入购物车”“提交订单”是业务行为，应留在 Screen/Flow。

## 7. Day 2：把四条业务流拆开

课程中的“进入首页 → 登录 → 搜索 → 加入购物车 → 下单”适合作为学习地图，但不适合只写成一条巨型 E2E。

### 登录

覆盖：成功、账号格式错误、密码错误、空值、重复登录和会话失效。成功断言应使用用户状态或首页标识，不只判断按钮被点击。

### 搜索

覆盖：精确词、模糊词、无结果、特殊字符、清空与重复搜索。断言结果与搜索词或业务规则相关，不只判断列表非空。

### 购物车

覆盖：首次加入、重复加入、数量边界、库存变化和返回页面后的状态。断言商品、数量、金额和页面角标中的关键一致性。

### 订单

覆盖：结算页展示、地址/配送前置条件、金额汇总、提交失败和重复点击。学习环境应停在不会产生真实交易的受控步骤，或使用本地/公开演示系统。

合理的测试组合是：

```text
登录独立测试 ─┐
搜索独立测试 ─┼─ 快速定位页面能力和规则问题
购物车独立测试┤
订单独立测试 ─┘

登录 → 搜索 → 加购 → 结算：只保留少量关键旅程 smoke
```

## 8. Day 2：Fixture 与数据驱动

Fixture 负责资源生命周期，而不是共享隐含状态：

```python
import pytest

@pytest.fixture
def mobile_driver(settings, request):
    driver = create_mobile_driver(settings)
    try:
        yield driver
    finally:
        report = getattr(request.node, "rep_call", None)
        if report and report.failed:
            collect_first_failure_evidence(driver, request.node.nodeid)
        driver.quit()
```

实际项目可通过 pytest hook 保存执行阶段结果。关键顺序是：保留第一次失败 → 尽力采集证据 → 尽力清理；证据或清理失败不能覆盖原始异常。

数据驱动不要依赖 JSON 字典字段顺序转换元组。显式读取命名字段：

```python
import json
from pathlib import Path

def load_login_cases(path: Path) -> list[dict[str, str]]:
    cases = json.loads(path.read_text(encoding="utf-8"))
    required = {"case_id", "username", "password", "expected"}
    for case in cases:
        missing = required - case.keys()
        if missing:
            raise ValueError(f"{case.get('case_id', '<unknown>')} missing {sorted(missing)}")
    return cases
```

测试数据使用明显虚构值，并让 `case_id` 进入报告。密码、Token、设备 UDID 和本机 App 路径由本地环境变量提供，不写进 JSON、源码或 CI 日志。

## 9. Day 3：让滑动和页面状态可控

固定像素坐标只适合临时调试。仓库的 `移动端基础页面.py` 使用窗口比例和平台原生命令，并限制最大滑动次数：

```python
for attempt in range(max_swipes + 1):
    try:
        return self.wait_visible(locator, timeout=1.5)
    except TimeoutException:
        if attempt == max_swipes:
            break
        self._swipe(direction)
raise TimeoutException("target was not visible within the swipe budget")
```

这个设计同时解决三个问题：不同分辨率、无限滑动和失败信息不清楚。更进一步，应让每个 Screen 定义自己的“已加载”标识：

```text
进入页面 → 等待唯一标识 → 处理允许出现的分支 → 执行业务动作 → 等待结果状态
```

## 10. Day 3：失败证据不是只有截图

最小证据包建议包含：

| 证据 | 回答的问题 |
|---|---|
| 测试名、步骤、时间与版本 | 在什么上下文失败？ |
| 屏幕截图 | 用户当时看到什么？ |
| Page Source | 自动化当时能看到哪些节点和属性？ |
| Appium Server 日志 | 请求、Driver 与 Session 如何响应？ |
| 受控 `adb logcat` / WDA 日志 | App 或平台是否崩溃、拒绝或超时？ |
| 配置摘要 | 使用哪个平台、Profile 和非敏感版本？ |

证据采集原则：

1. 优先保留第一次失败，后续异常作为附加信息；
2. 每次运行使用独立目录，避免并发覆盖；
3. 日志隐藏凭据、Cookie、Token 和输入内容；
4. 截图与 Page Source 在保存或分享前检查页面内容；
5. 证据目录属于运行产物，不进入 Git。

Allure 用于组织步骤、附件、环境与历史趋势，但报告“生成成功”不等于断言正确。先让测试语义和证据可靠，再接报告工具。

## 11. Day 3：CI 分层

移动 UI 比单元/API 测试更慢且环境更复杂，不应让所有任务使用同一频率：

| 层级 | 建议触发 | 内容 |
|---|---|---|
| PR | 每次提交 | 静态检查、单元测试、离线 App Mock、配置校验 |
| 主分支 | 合并后 | 本地受控模拟器关键 smoke |
| 夜间 | 定时 | 更多系统版本、权限、异常和业务回归 |
| 发布前 | 人工确认 | 关键真机矩阵、升级/安装、弱网与高风险旅程 |

Jenkins、GitHub Actions 或其他平台只是调度器。真正需要版本化的是执行命令、依赖、设备选择、超时、产物目录和退出码。公共第三方环境不作为 PR 的强制门禁。

## 12. 与旧式课堂写法的差异

| 常见入门写法 | 本模块采用的做法 | 原因 |
|---|---|---|
| Appium 1 的 `/wd/hub` 与旧 capabilities | Appium 3 + W3C Options | 避免协议和示例过时 |
| 固定模拟器名称、系统版本和包名 | 环境变量 + Profile + 启动前校验 | 防止控制错误目标 |
| 默认 `noReset=True` 复用登录状态 | 默认隔离状态，必要时显式准备 | 避免顺序依赖和污染 |
| `sleep()` 等页面 | 等待可见、可点击、消失或业务标识 | 更快且失败原因清楚 |
| 长 XPath 或固定坐标 | 可访问标识/resource-id/平台定位，坐标兜底 | 降低布局变化带来的脆弱性 |
| 一个 fixture 先登录再给后续用例复用 | 每条测试拥有明确前置和清理 | 支持独立、重跑和并行 |
| JSON 依赖 `dict.values()` 顺序 | 按字段名校验和读取 | 数据变化时尽早失败 |
| 每次成功都截图 | 关键里程碑 + 首次失败证据 | 降低噪声和内容暴露风险 |
| 一条脚本贯穿全部业务 | 独立能力测试 + 少量关键 E2E | 更容易定位和维护 |
| 只看 Allure 是否绿色 | 断言、证据、隔离和清理共同验收 | 报告不能替代测试可信度 |

## 13. 三天实践任务

### Day 1 交付

- [ ] 画出 Appium Client → Server → Driver → 设备 → App 链路；
- [ ] 保存版本清单并通过 Driver Doctor；
- [ ] 使用明确 UDID 建立和释放一个 Session；
- [ ] 用 Inspector 比较 Accessibility ID、resource-id 和 XPath；
- [ ] 主动定位一个不存在的元素，读懂超时信息；
- [ ] 将一个固定等待改为页面状态等待。

### Day 2 交付

- [ ] 创建 Driver Factory、Base Screen、两个 Screen 和一个 Flow；
- [ ] 登录成功与失败数据均使用合成值；
- [ ] 登录和搜索可以分别运行，不依赖用例顺序；
- [ ] Fixture 即使断言失败也会执行 `quit()`；
- [ ] JSON 数据缺字段时在创建 Session 前失败；
- [ ] Test 中没有散落的长 XPath、端口和 App 路径。

### Day 3 交付

- [ ] 购物车和订单各有独立断言；
- [ ] 只保留一条关键“登录 → 搜索 → 加购 → 结算”旅程；
- [ ] 滑动有方向、范围和最大次数；
- [ ] 主动制造一次定位失败，得到完整最小证据包；
- [ ] 验证失败证据采集失败时原始异常仍被保留；
- [ ] PR 与真机任务分层，不默认控制本地设备；
- [ ] 写一页复盘：覆盖了什么、没证明什么、下一步是什么。

## 14. 推荐阅读与代码入口

按学习顺序继续：

1. [项目结构与 Page Object](./03-项目结构与PageObject.md)：把单文件脚本拆成可维护工程；
2. [业务流程与数据驱动](./04-业务流程与数据驱动.md)：完成登录、搜索、购物车和订单；
3. [Fixture、失败证据与报告](./05-Fixture失败证据与报告.md)：建立生命周期和证据链；
4. [CI、真机矩阵与故障排查](./06-CI真机矩阵与故障排查.md)：扩展 Android、iOS 与流水线；
5. [自动化框架设计与进阶项目](../../05-质量工程/03-自动化框架设计与进阶项目.md)：理解跨技术线的工程治理。

重点代码：

- `labs/app-automation-learning/src/qa_learning/mobile/course_project.py`
- `labs/app-automation-learning/src/qa_learning/mobile/移动端驱动工厂.py`
- `labs/app-automation-learning/src/qa_learning/mobile/screens/移动端基础页面.py`
- `labs/app-automation-learning/src/qa_learning/mobile/mock/`
- `labs/app-automation-learning/tests/unit/`
- `labs/app-automation-learning/tests/mobile/`

## 15. 官方资料

- [Appium 官方文档](https://appium.io/docs/en/latest/)
- [Appium 安装与 Quickstart](https://appium.io/docs/en/latest/quickstart/)
- [Appium Inspector](https://appium.github.io/appium-inspector/latest/)
- [UiAutomator2 Driver](https://github.com/appium/appium-uiautomator2-driver)
- [Appium Python Client](https://github.com/appium/python-client)
- [Android Debug Bridge](https://developer.android.com/tools/adb)
- [Android ApiDemos](https://github.com/appium/android-apidemos)

完成本模块不等于“已经掌握所有 App 自动化”。真正的完成标准是：在明确目标设备和公开练习对象上，任何一条用例都能独立运行、主动失败、留下足以定位问题的证据，并可靠恢复环境。
