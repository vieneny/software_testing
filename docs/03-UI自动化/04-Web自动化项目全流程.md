# Web 自动化全流程：从公开靶场到可维护框架

> 技术主线：Python + pytest + Playwright  
> 公开资料核对日期：2026-07-27  
> 代码位置：`labs/automation-practice`  
本章不是把几段浏览器脚本拼在一起，而是完成一次接近真实工作的
Web 自动化项目：

1. 选择合法、适合学习的公开测试靶场。
2. 从手工探索和 Codegen 草稿开始设计测试。
3. 使用可靠定位、自动等待和 Web-first 断言。
4. 将重复行为重构为 Page Object 和跨页面 Flow。
5. 隔离浏览器状态，控制测试数据和清理动作。
6. 保留失败 Trace、截图与视频，能够独立定位失败。
7. 将本地回归和第三方公开站点测试分开运行。
8. 把代码接入 CI，但不滥用公共服务。

WebKit 或移动视口只能用于 Web 兼容性与响应式页面练习，不等于在真实
iPhone 上测试 Safari，也不等于原生 iOS App 自动化。原生 Android/iOS
App 应使用 Appium 对应的 UiAutomator2/XCUITest 驱动。

## 1. 公开靶场不是“你控制的 Mock”

公开练习站点是第三方维护的演示应用。它们适合学习，但存在：

- 页面或测试数据随时更新。
- 服务临时下线、变慢或返回 `429`、`5xx`。
- 多位学习者共享账号或数据库。
- 广告、分析服务和网络策略带来额外噪声。
- 没有为你的 CI 提供可用性承诺。

因此，可靠学习项目应采用三层靶场：

| 层级 | 目标 | 用途 | 运行策略 |
|---|---|---|---|
| 本地稳定主线 | 仓库内 `demo-shop` | PR 全量回归、接口与 UI 联调 | 每次提交 |
| 本地开源靶场 | The Internet、ParaBank Docker | 浏览器专题、UI/API 全链路 | 本地或受控 CI |
| 第三方公开靶场 | TodoMVC、SauceDemo 等 | 对照练习、低频冒烟 | 默认关闭、人工显式开启 |

不要因为站点写着“供测试练习”就对它运行压力测试、安全扫描、爬虫、
高并发或无限重试。

## 2. 靶场调研与选型

### 2.1 对比表

| 靶场 | 是否明确用于测试 | 适合场景 | 状态模型与风险 | 本项目定位 |
|---|---|---|---|---|
| [Playwright TodoMVC](https://demo.playwright.dev/todomvc/) | 是；Playwright 官方 Codegen、Fixture 和 Trace 文档使用 | CRUD、编辑、过滤、键盘、localStorage、Context 隔离 | 数据位于浏览器 localStorage，无共享业务数据库；公开服务仍可能中断 | 初学主线 |
| [SauceDemo](https://www.saucedemo.com/) | 是；Sauce Labs 官方教程和文档使用 | 固定用户、商品排序、购物车、表单校验、完整结算 | 公共固定账号；购物车主要跟随浏览器会话；未提供公开 SLA | 业务流程主线 |
| [The Internet](https://the-internet.herokuapp.com/) | 是；开源仓库明确表示用于自动化验收测试 | 动态加载、弹窗、窗口、frame、上传下载、Shadow DOM、状态码 | 多数场景无持久数据；部分内容故意随机或延迟；可本地部署 | 浏览器专题 |
| [Automation Exercise](https://automationexercise.com/) | 是；提供 26 个 UI 和 14 个 API 练习 | 注册、商品、购物车、结算、上传、发票、UI/API 混合 | 注册账号写入共享数据库；必须唯一数据、串行执行和删除账号 | 进阶低频 E2E |
| [Practice Test Automation](https://practicetestautomation.com/practice/) | 是；页面直接给出练习目标 | 正反登录、Selenium 异常、动态表格 | 固定演示数据，状态基本局部；页面内容可能更新 | Selenium/等待专题 |
| [ParaBank](https://parabank.parasoft.com/parabank/index.htm) | 是；Parasoft 官方开源 Web/API Demo | 银行注册、开户、转账、账单、REST/SOAP | 公共数据库共享，管理页能初始化或清空数据库 | 仅本地完整回归 |

### 2.2 为什么代码主线选择两个站点

本章提供两套可以直接运行的练习：

- TodoMVC：功能少、状态隔离好，适合观察测试代码本身。
- SauceDemo：包含登录、列表、购物车和结算，适合练习企业常见分层。

The Internet、Automation Exercise、Practice Test Automation 和 ParaBank
作为后续 24 项任务的专题靶场。先把一套小框架写对，再扩充场景；不要一开始
复制几十个没有断言的脚本。

## 3. 项目结构

```text
labs/automation-practice/
├── pyproject.toml
├── src/qa_learning/web/
│   ├── 浏览器练习目标.py
│   ├── pages/
│   │   ├── 待办事项页面.py
│   │   └── 演示商城页面.py
│   └── flows/
│       └── 演示商城结账流程.py
└── tests/
    ├── conftest.py
    └── web/
        ├── conftest.py
        ├── 测试_公开待办事项网站.py
        └── 测试_公开演示商城网站.py
```

对应源码：

- [TodoMVC Page Object](../../labs/automation-practice/src/qa_learning/web/pages/待办事项页面.py)
- [SauceDemo Pages](../../labs/automation-practice/src/qa_learning/web/pages/演示商城页面.py)
- [SauceDemo Checkout Flow](../../labs/automation-practice/src/qa_learning/web/flows/演示商城结账流程.py)
- [TodoMVC 递进测试](../../labs/automation-practice/tests/web/测试_公开待办事项网站.py)
- [SauceDemo 业务测试](../../labs/automation-practice/tests/web/测试_公开演示商城网站.py)

分层职责：

| 层 | 职责 | 不应做什么 |
|---|---|---|
| Target/Config | URL、公开演示账号、环境变量覆盖 | 不保存私人或公司账号 |
| Page | 页面元素和单页用户行为 | 不建立万能 `click(selector)` |
| Flow | 跨页面业务编排 | 不隐藏所有断言和错误 |
| Test | 数据、测试意图和业务结果 | 不复制大段页面操作 |
| Fixture | 浏览器、状态隔离、开关和清理 | 不让测试产生顺序依赖 |

## 4. 环境准备与第一次运行

进入实验目录并创建独立环境：

```bash
cd labs/automation-practice
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[web]'
python -m playwright install chromium
```

先执行默认命令：

```bash
pytest tests/web -q
```

所有用例都带有 `external` 标记，默认结果应是跳过。这样：

- 安装依赖不会自动访问第三方站点。
- 普通 `pytest` 和 PR CI 不会给公开站点制造流量。
- 断网时仍可执行本地接口、AI 和单元测试。

明确同意访问公开练习站点后再运行：

```bash
pytest tests/web -q --run-public-web
```

只运行一个靶场：

```bash
pytest tests/web/测试_公开待办事项网站.py -q --run-public-web
pytest tests/web/测试_公开演示商城网站.py -q --run-public-web
```

只运行一个用例并显示浏览器：

```bash
pytest tests/web/测试_公开待办事项网站.py \
  -k crud \
  --run-public-web \
  --headed \
  -s
```

`--run-public-web` 是有意设置的安全阀，不要将它写进 pytest 默认参数。

### 4.1 URL 覆盖

如需把相同用例指向自己部署的站点：

```bash
export TODO_MVC_URL='http://127.0.0.1:3000/'
export SAUCE_DEMO_URL='http://127.0.0.1:3001/'
```

目标配置集中在 `浏览器练习目标.py`。不要为了切换环境修改测试代码。

## 5. 从 Codegen 录制到可维护测试

### 5.1 录制草稿

```bash
python -m playwright codegen \
  https://demo.playwright.dev/todomvc/
```

手工完成“新增任务—勾选—过滤”后，Codegen 会生成一段线性脚本。它的价值是：

- 快速发现可访问角色、名称和 test ID。
- 验证交互路径能否被浏览器执行。
- 作为 Page Object 的输入材料。

它不是最终交付物。录制器不知道：

- 哪些步骤属于业务前置条件。
- 哪个断言最能证明需求成立。
- 哪些页面行为会在其他测试复用。
- 哪些数据需要清理。
- 哪些公网操作不应进入 CI。

### 5.2 第一次重构：补充业务断言

录制结果可能只有：

```python
page.get_by_placeholder("What needs to be done?").fill("学习 Playwright")
page.get_by_placeholder("What needs to be done?").press("Enter")
```

至少补上用户可观察结果：

```python
expect(page.get_by_test_id("todo-title")).to_have_text(
    ["学习 Playwright"]
)
```

### 5.3 第二次重构：抽取行为

```python
class TodoMVCPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.new_todo = page.get_by_placeholder(
            "What needs to be done?"
        )
        self.titles = page.get_by_test_id("todo-title")

    def add(self, text: str) -> None:
        self.new_todo.fill(text)
        self.new_todo.press("Enter")
```

测试变为：

```python
todos.add("学习 Playwright")
expect(todos.titles).to_have_text(["学习 Playwright"])
```

Page Object 封装的是“新增任务”，不是 `fill(selector, value)`。后者只是把
Playwright 再包装一层，会损失类型提示、自动等待和故障信息。

### 5.4 第三次重构：跨页面 Flow

SauceDemo 完整结算需要：

1. 登录。
2. 选择商品。
3. 打开购物车。
4. 进入结算。
5. 填写虚拟收货人。
6. 核对金额。
7. 完成订单。

每个页面对象只理解自己的页面，`SauceCheckoutFlow` 负责业务编排。测试仍在
关键节点断言商品小计和最终成功信息，没有把整个过程藏进一个不可检查的
`do_everything()`。

## 6. 定位策略

按以下顺序思考，而不是盲目使用 XPath：

1. `get_by_role()`：按钮、链接、标题、表格等用户可感知语义。
2. `get_by_label()`：表单控件和有可访问名称的按钮。
3. `get_by_placeholder()`：适合少量稳定输入框。
4. `get_by_text()`：适合用户必须看到的稳定文案。
5. `get_by_test_id()`：团队明确维护的测试契约。
6. 稳定属性 CSS：公开靶场已有 `data-test`，但不是默认 `data-testid`。
7. XPath：只有表达表格关系或遗留 DOM 关系时才考虑。

SauceDemo 使用：

```python
page.locator("[data-test='username']")
```

原因是目标站点使用 `data-test` 而非 Playwright 默认的 `data-testid`。
不要为了使用 `get_by_test_id()` 擅自假设属性名。

### 6.1 避免模糊匹配

商品卡应先缩小到目标卡片，再点击卡片内部的按钮：

```python
name = page.locator("[data-test='inventory-item-name']").filter(
    has_text=re.compile(r"^Sauce Labs Backpack$")
)
item = items.filter(has=name)
item.get_by_role("button", name="Add to cart").click()
```

这比：

```python
page.locator("button").nth(2).click()
```

更能表达用户意图，也不依赖商品排列位置。

### 6.2 什么时候需要 test ID

以下情况可与开发约定 test ID：

- 文案会根据语言变化。
- 相同角色和名称确实出现多次。
- 元素没有自然可访问语义。
- 该元素是回归测试长期依赖的交互契约。

test ID 不能替代可访问性。一个没有 label 的输入框不应只因为有 test ID
就被视为设计正确。

## 7. 等待：条件驱动，不是时间驱动

禁止为了“等页面大概加载完”而写固定 3 秒延时。这种“碰运气”等待会让
测试既慢又不稳定，而且无法证明业务状态真的就绪。

Playwright Locator 在点击、填写等操作前会等待元素可交互，`expect` 会在超时
范围内自动重试：

```python
expect(inventory.container).to_be_visible()
expect(page).to_have_url(re.compile(r"/inventory\.html$"))
expect(cart_badge).to_have_text("2")
```

等待原则：

- 等待业务条件，不等待固定秒数。
- 页面跳转后同时验证 URL 和关键页面元素。
- 网络请求是业务证据时，使用 `expect_response`。
- 下载、新窗口、弹窗等先注册事件等待，再触发动作。
- 只有测试真实时间行为时才使用定时等待，并解释原因。

### 7.1 不要滥用 `networkidle`

含分析脚本、广告或长连接的页面可能永远达不到你期待的“网络空闲”。
结算页真正需要的条件是“商品摘要可见、金额已显示”，应直接等待这些条件。
本项目导航只等待 `domcontentloaded`，随后由 Page Object 等待目标页的关键
交互元素；这样不会把无关图片或第三方资源当成业务就绪条件。

### 7.2 不要用重试掩盖竞态

重试可以用于收集偶发环境问题，但不能替代：

- 正确 Locator。
- 明确状态初始化。
- 唯一测试数据。
- 条件等待。
- 可诊断的失败证据。

## 8. TodoMVC 递进实战

现有测试覆盖：

1. 新增、编辑、删除完整 CRUD。
2. 空字符串和纯空格边界。
3. Active、Completed、All 过滤和剩余计数。
4. 全部完成及清除完成项。
5. 刷新保持 localStorage，但新 BrowserContext 不共享状态。

### 8.1 Page Object 的关键点

`TodoMVCPage.item(title)` 使用标题缩小到唯一任务项。随后完成、编辑、删除都从
该任务项内部继续查找控件，避免全局 `nth()`。

`filter_by()` 对允许值做白名单检查：

```python
if name not in {"All", "Active", "Completed"}:
    raise ValueError(...)
```

Page Object 越早对无效调用报错，定位测试代码错误越容易。

### 8.2 验证 localStorage 与测试隔离

同一 Context 中刷新：

```python
first_todos.add("只属于第一个浏览器上下文")
first_page.reload()
expect(first_todos.titles).to_have_text(
    ["只属于第一个浏览器上下文"]
)
```

另开 Context：

```python
second_context = browser.new_context()
second_page = second_context.new_page()
second_todos = TodoMVCPage(second_page)
second_todos.open()
expect(second_todos.items).to_have_count(0)
```

这两个断言不矛盾：

- 刷新用于验证产品的持久化能力。
- 新 Context 用于验证测试之间没有污染。

## 9. SauceDemo 业务框架

### 9.1 页面拆分

| 类 | 行为 |
|---|---|
| `SauceLoginPage` | 打开站点、填写账号、登录、暴露错误区域 |
| `SauceInventoryPage` | 等待商品页、排序、加入购物车、读取价格 |
| `SauceCartPage` | 验证购物车、进入结算 |
| `SauceCheckoutPage` | 填写用户、查看摘要、完成订单、确认成功 |
| `SauceCheckoutFlow` | 组合登录、选品、购物车和结算 |

### 9.2 公开账号

SauceDemo 页面和 Sauce Labs 官方文档公开：

```text
standard_user
locked_out_user
secret_sauce
```

这些是靶场公开演示账号，不是秘密。框架允许通过环境变量覆盖，避免把“配置
只能写死在代码中”养成习惯。任何真实项目账号都必须从受控 Secret 获取。

### 9.3 负向登录

锁定用户测试验证：

- 错误信息包含 locked out。
- 页面没有进入 inventory。

只断言“错误元素存在”不够，因为错误原因可能完全不同。

### 9.4 排序

页面对象读取所有可见价格并转换为 `float`：

```python
prices = [
    float(text.replace("$", ""))
    for text in price_locators.all_text_contents()
]
```

测试分别选择 `lohi` 与 `hilo`，再与 Python 排序结果比较。这样验证的是排序
规则，而不是只检查下拉框显示了某个值。

### 9.5 完整结算

代表性用例选择 Backpack 与 Bike Light：

```python
flow.purchase(
    ["Sauce Labs Backpack", "Sauce Labs Bike Light"],
    CheckoutCustomer(
        first_name="Learning",
        last_name="Tester",
        postal_code="000000",
    ),
)
```

这些姓名和邮编是明显的虚构数据。不要填写真实姓名、公司地址、手机号或支付
信息。

进入摘要后验证：

- 两件目标商品均出现在购物车。
- Item total 为 `$39.98`。
- Tax 和 Total 已显示。
- 完成后出现 `Thank you for your order!`。

金额是公开 Demo 当前固定商品数据。如果站点更改价格，失败应先被归类为：

1. 目标站点数据变更。
2. 业务预期需要更新。
3. 页面定位失效。
4. 网络或 WAF 故障。

不要看到公开站失败就立即增加重试。

## 10. 状态隔离与测试数据

### 10.1 每条测试使用新 Context

pytest-playwright 的 `page` fixture 默认基于隔离的 BrowserContext。不要把一个
全局 page 在所有测试中复用。

每条测试必须能够：

- 单独运行。
- 任意顺序运行。
- 失败后不影响下一条。
- 在不同浏览器上得到同类结果。

### 10.2 不依赖上一条测试

错误设计：

```text
test_01_register_user
test_02_login_registered_user
test_03_checkout
test_04_delete_user
```

第二条依赖第一条，第三条依赖第二条；只要中间失败，后续全部失去意义。

正确设计：

- 单个 E2E 用例在 fixture 中创建自己的用户。
- `yield` 后执行删除清理。
- 即使 UI 断言失败，也通过 `finally` 或 fixture teardown 尝试清理。
- 写入公开站点的测试默认关闭、串行执行。

### 10.3 唯一且虚构的数据

Automation Exercise 等允许注册的靶场应生成：

```text
learning-<uuid>@example.com
Learning Tester
Example Street
000000
```

`example.com` 是文档示例域名，不应换成个人邮箱或公司域名。不要把随机生成的
数据伪装成真实身份。

## 11. 失败证据与调试

### 11.1 保留失败 Trace 和截图

```bash
pytest tests/web \
  --run-public-web \
  --tracing retain-on-failure \
  --screenshot only-on-failure \
  --output test-results
```

查看 Trace：

```bash
python -m playwright show-trace \
  test-results/<测试目录>/trace.zip
```

Trace 可帮助检查：

- 每一步实际使用的 Locator。
- 点击前后的 DOM 快照。
- URL、控制台和网络请求。
- 元素为什么不可操作。

### 11.2 Inspector

```bash
PWDEBUG=1 pytest \
  tests/web/测试_公开演示商城网站.py \
  -k checkout \
  --run-public-web \
  -s
```

在 Inspector 中逐步执行并使用 Pick Locator。调试完成后仍应保留清晰的源码，
不能要求后续维护者必须打开 Inspector 才知道测试在做什么。

### 11.3 失败分类

| 现象 | 优先检查 |
|---|---|
| DNS、连接超时、`502/503` | 第三方环境是否可用 |
| `403/429` | WAF、访问频率和公共站点政策 |
| Locator 找不到 | 页面结构、文案、frame、可访问名称 |
| 点击超时 | 遮挡、禁用、动画、目标选错 |
| 断言金额变化 | 公共测试数据是否更新 |
| 单独通过、批量失败 | 状态污染、共享账号、顺序依赖 |
| CI 失败、本地通过 | 浏览器版本、时区、字体、视口和网络 |

公开站环境错误与产品断言错误应在报告中区分，但不能把所有失败自动 `skip`，
否则真实的测试代码回归也会被隐藏。

## 12. 多浏览器与移动视口

先让 Chromium 主线稳定，再执行：

```bash
python -m playwright install firefox webkit
pytest tests/web/测试_公开待办事项网站.py \
  --run-public-web \
  --browser chromium \
  --browser firefox \
  --browser webkit
```

公共站点完整结算不需要在 CI 中每天重复三个浏览器。更合理的分配：

- 本地受控应用：完整跨浏览器回归。
- TodoMVC：少量跨浏览器基础交互。
- SauceDemo：Chromium 关键流程；需要时人工跨浏览器检查。
- 原生 App：进入 Appium 专项，不用桌面 WebKit 冒充真实 iOS。

## 13. CI 设计

### 13.1 PR 阶段

PR 默认只运行本地受控测试：

```bash
pytest -m "not external"
```

公开站点用例不会因为普通 `pytest` 被执行。

### 13.2 人工触发公开 smoke

建议单独建立 `workflow_dispatch` 工作流：

```yaml
name: public-web-smoke

on:
  workflow_dispatch:

jobs:
  smoke:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - run: python -m pip install -e 'labs/automation-practice[web]'
      - run: python -m playwright install --with-deps chromium
      - run: >
          pytest labs/automation-practice/tests/web
          -q
          --run-public-web
          --browser chromium
          --tracing retain-on-failure
          --screenshot only-on-failure
```

不要给此任务添加：

- pytest-xdist 并行访问第三方站点。
- 无限重试。
- 每几分钟一次的定时计划。
- 创建大量账号的循环。
- 性能或安全扫描。

### 13.3 失败产物

上传 Trace 或截图前要确认其中只有公开 Demo 和虚构数据。真实系统的 Trace
可能包含 token、Cookie、请求体、用户信息和内部 URL，不能上传到公开仓库或
公共 CI Artifact。

## 14. 公共站点安全阀

本项目的公网测试满足：

- 统一使用 `@pytest.mark.external`。
- 默认缺少 `--run-public-web` 时跳过。
- 不在 import 或收集阶段访问网络。
- 不使用并发。
- 不执行性能、压力或安全测试。
- 不访问 ParaBank 公共 Admin 的 Initialize/Clean。
- 不创建真实身份或真实支付数据。
- 不将公共站点可用性视为仓库 PR 的质量门禁。

Grafana k6 官方也明确要求不要对不属于自己的服务器做负载测试。性能章节的
脚本只能指向本地 `demo-shop`、本地 Docker 或取得明确授权的环境。

## 15. Selenium 兼容学习线

市场岗位仍会要求 Selenium，因此可保留一组小型兼容练习：

1. Practice Test Automation 正反登录。
2. The Internet Dynamic Loading 显式等待。
3. iframe 和多窗口。
4. JavaScript Alert。
5. 上传和下载。
6. 动态表格和 XPath 关系定位。

不要把 Playwright 全套用例机械复制到 Selenium，也不要创建一个同时包装
Playwright Page 与 Selenium WebDriver 的统一驱动。两者等待、Locator 和
浏览器生命周期模型不同；强行统一只会制造“最小公分母”框架。

Selenium 线应：

- 使用 Selenium Manager 管理常见驱动。
- 使用显式条件等待。
- 不混合隐式等待和大量固定睡眠。
- 复用业务场景说明及虚拟测试数据，不复用驱动封装。

## 16. 二十四项递进任务

### L1：Playwright 基础

1. 用 Codegen 录制 TodoMVC 新增任务，再重构为语义化 Locator。
2. 实现新增、编辑、删除，断言每一步用户可见结果。
3. 参数化空字符串、纯空格、中文、Emoji 和超长文本。
4. 验证 Active、Completed、All 过滤和剩余计数。
5. 验证刷新后 localStorage 持久化及新 Context 隔离。
6. 在 Chromium、Firefox、WebKit 和一个移动视口执行核心用例。

### L2：电商业务

7. 参数化 SauceDemo 正常、错误密码和锁定用户登录。
8. 验证明确错误原因和登录失败后的 URL。
9. 验证商品名称和价格的正序、倒序。
10. 添加和移除多件商品，验证购物车角标。
11. 参数化结算页三个必填字段的错误提示。
12. 完成登录、选品、购物车、结算、成功页全流程。
13. 将重复行为重构为 Page、Component 和 Checkout Flow。

### L3：浏览器专项

14. 在 The Internet 用 Dynamic Loading/Controls 练习条件等待。
15. 处理 alert、confirm、prompt 和 Basic Auth。
16. 处理 iframe、嵌套 frame、新窗口、新标签页及 Shadow DOM。
17. 实现文件上传、下载事件捕获、文件名及内容校验。
18. 校验动态表格、失效图片、HTTP 状态码与重定向。

### L4：UI/API 与本地全链路

19. 为 Practice Test Login 编写三组数据驱动测试。
20. 先复现 NoSuchElement、不可交互、Stale、Timeout，再正确修复。
21. 验证动态表格组合过滤、数字排序、空结果和 Reset。
22. 对比 Automation Exercise 商品 API 与 UI 搜索结果。
23. API 创建唯一虚构用户，UI 下单并下载发票，API 删除用户；串行执行。
24. 本地 Docker 启动 ParaBank，UI 注册/开户/转账/支付，再用 REST API
    验证余额和交易。

## 17. 阶段验收

### 基础验收

- [ ] 默认 `pytest tests/web` 不访问公网，测试被安全跳过。
- [ ] `--run-public-web` 后 TodoMVC 和 SauceDemo 可以执行。
- [ ] 没有用于碰运气的固定等待。
- [ ] 核心 Locator 使用角色、名称、明确 test ID 或稳定 `data-test`。
- [ ] 每条测试能够独立运行。

### 框架验收

- [ ] Page、Flow、Test 职责清楚。
- [ ] 没有万能 `BasePage.click(selector)`。
- [ ] 环境 URL 可通过变量覆盖。
- [ ] 失败能生成 Trace 和截图。
- [ ] 公共站点失败能区分环境、定位、数据和业务原因。

### 作品集验收

- [ ] README 解释为什么选择这些靶场。
- [ ] 能展示一次 Codegen 草稿到 Page Object 的重构过程。
- [ ] 能解释 BrowserContext 隔离和 storage state 的区别。
- [ ] 能说明为什么 PR 不默认访问公共站点。
- [ ] 能现场调试一条失败测试并阅读 Trace。
- [ ] 所有账号、姓名、地址和订单数据都是公开演示或虚构数据。

## 18. 官方与项目来源

以下链接均在 2026-07-27 核对：

### Playwright

- [Playwright Python 安装与 pytest 插件](https://playwright.dev/python/docs/intro)
- [Playwright Python Codegen](https://playwright.dev/python/docs/codegen)
- [Playwright Locator](https://playwright.dev/python/docs/locators)
- [Playwright 自动等待](https://playwright.dev/python/docs/actionability)
- [Playwright 测试隔离](https://playwright.dev/python/docs/browser-contexts)
- [Playwright Trace Viewer](https://playwright.dev/python/docs/trace-viewer)
- [Playwright TodoMVC](https://demo.playwright.dev/todomvc/)

### 练习靶场

- [Sauce Labs 自动化教程](https://saucelabs.com/resources/blog/test-automation-tutorial)
- [Sauce Labs Playwright/Selenium Grid 文档](https://docs.saucelabs.com/web-apps/automated-testing/playwright/selenium-grid/)
- [The Internet 开源仓库](https://github.com/saucelabs/the-internet)
- [Automation Exercise UI 用例](https://automationexercise.com/test_cases)
- [Automation Exercise API 列表](https://automationexercise.com/api_list)
- [Practice Test Automation 登录](https://practicetestautomation.com/practice-test-login/)
- [Practice Test Automation 异常](https://practicetestautomation.com/practice-test-exceptions/)
- [Practice Test Automation 动态表格](https://practicetestautomation.com/practice-test-table/)
- [ParaBank 开源仓库](https://github.com/parasoft/parabank)
- [ParaBank Docker 镜像](https://hub.docker.com/r/parasoft/parabank)
- [ParaBank REST API](https://parabank.parasoft.com/parabank/api-docs/index.html)

### 公共环境边界

- [Grafana k6：不要负载测试不属于自己的服务器](https://grafana.com/docs/k6/latest/testing-guides/load-testing-websites/)

公开站点与工具会持续变化。每季度检查链接、页面行为和官方文档；如果一个
公开站点不再稳定，优先切换为本地开源部署，而不是堆叠等待和重试。
