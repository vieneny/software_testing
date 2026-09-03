# 自动化测试综合练习工程

> 核对日期：2026-07-27
> 技术主线：Python 3.11+、pytest、Requests、Playwright、Appium 3

这个目录是一套可以真正运行的 API、Web、Android 和 iOS 自动化学习工程。
它的目标不是堆积脚本，而是让你练习一条完整链路：

```text
风险分析
  → 选择测试层
  → 配置环境
  → 准备合成数据
  → 执行测试
  → 保存失败证据
  → 清理状态
  → 分析与改进
```

## 1. 先看哪篇教程

- [接口自动化全流程](../../docs/09-自动化实战/01-接口自动化全流程.md)
- [Web 自动化全流程](../../docs/09-自动化实战/02-网页自动化全流程.md)
- [App 自动化项目快速学习（3 天项目主线）](../../docs/09-自动化实战/08-App自动化项目快速学习/README.md)
- [App 自动化 Mock 框架全流程](../../docs/09-自动化实战/07-移动端自动化模拟框架全流程.md)
- [Android 真机自动化全流程](../../docs/09-自动化实战/03-安卓真机自动化全流程.md)
- [iOS 自动化全流程](../../docs/09-自动化实战/04-苹果移动端自动化全流程.md)
- [框架设计与进阶项目](../../docs/09-自动化实战/05-框架设计与进阶项目.md)
- [故障排查](../../docs/09-自动化实战/06-故障排查.md)

第一次学习建议按 01 → 02 → 08 → 07 → 03 → 04 → 05 → 06 进行。第 08 篇先建立
App 自动化项目全局认识；第 07 篇不需要
Appium 或设备，是进入 Android/iOS 真机前的可运行训练桥梁。只准备面试或补某个
能力时，可以直接进入对应模块，但仍应先了解本页的运行开关。

## 2. 靶场分工

| 类型 | 本项目使用方式 | 适合做什么 | 不适合做什么 |
|---|---|---|---|
| 离线单元测试 | Fake Response、Schema、数据工厂 | 客户端、脱敏、错误信息、纯逻辑 | 证明真实系统可用 |
| 离线 App Mock | Fake Device/Driver、合成页面状态机 | 移动契约、业务流、故障、证据和清理 | 证明 ADB/WDA、真机 UI 或兼容性 |
| 本地 `demo-shop` | 自己启动的虚构 FastAPI 商店 | 稳定回归、API/UI 联调、性能入门 | 推断生产容量 |
| 本地 Mock | WireMock、Mockoon、Prism、httpbin 容器 | 异常注入、契约、状态机、超时 | 代替所有真实集成 |
| 公共 API | JSONPlaceholder、Restful Booker | HTTP 入门、模拟写入、低频真 CRUD | 压测、并发扫描、稳定 CI 门禁 |
| 公共 Web | TodoMVC、SauceDemo | 定位、等待、页面对象、业务流 | 高频定时任务、批量造数据 |
| 公开移动 App | ApiDemos、Sauce Labs My Demo App | 真机/模拟器 UI、手势、权限、跨端 | 上传来源不明的 APK/APP |
| 受限许可公开练习项目 | Practice Software Testing / Toolshop | API、Web、Android、iOS 联合项目 | 商业使用、公开托管、再分发或作为第三方服务 |

公共靶场由第三方维护，随时可能变慢、变化或下线。PR 主线应依赖离线测试和
自己控制的本地靶场；公共靶场只做人工显式开启、低频、串行的 smoke。

## 3. 从零安装

### 3.1 所有人都需要

先确认：

```bash
python3 --version
node --version
npm --version
```

进入本目录并创建隔离环境：

```bash
cd labs/automation-practice
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[all,dev]'
cp 环境变量示例.env .env
```

Windows PowerShell 激活命令为：

```powershell
.\.venv\Scripts\Activate.ps1
```

只学一条技术线时，可将 `all` 换成：

```bash
python -m pip install -e '.[api]'
python -m pip install -e '.[web]'
python -m pip install -e '.[mobile]'
```

只安装单项 extra 时，只运行对应的 `tests/api`、`tests/web` 或 `tests/mobile`；
直接收集整个 `tests` 目录需要 `all`，否则未安装技术线的模块可能无法导入。

只练 App Mock 时不需要安装 Appium，可使用基础依赖和开发检查：

```bash
python -m pip install -e '.[dev]'
pytest tests/unit/测试_离线移动端成功流程.py \
  tests/unit/测试_离线移动端故障与清理.py \
  tests/unit/测试_离线移动端运行装配.py -q
```

### 3.2 Web 额外安装

```bash
python -m playwright install chromium
```

需要跨浏览器练习时再安装：

```bash
python -m playwright install firefox webkit
```

### 3.3 Android / iOS 额外安装

按 [Appium 官方安装文档](https://appium.io/docs/en/latest/quickstart/install/)
安装 Appium，然后只安装当前需要的驱动：

```bash
npm install -g appium
appium driver install uiautomator2
```

macOS 上学习 iOS 时还需要完整 Xcode，并安装 XCUITest 驱动：

```bash
appium driver install xcuitest
```

检查环境：

```bash
bash scripts/检查自动化测试环境.sh
appium driver doctor uiautomator2
appium driver doctor xcuitest
```

最后一条仅在 macOS + Xcode 的 iOS 学习环境执行。某个工具没有安装时，
`检查自动化测试环境.sh` 会指出停在哪一步；逐项修复，不要同时改很多配置。

## 4. 先理解默认安全门

直接执行：

```bash
pytest -q
```

会运行确定性的离线单元/Mock 测试，但不会自动访问公共 API、公共 Web 或控制
手机/模拟器：

| 范围 | 必须显式添加 | 默认行为 |
|---|---|---|
| 公共 API | `--run-public-api` | 带 `external` 的 API 用例跳过 |
| 公共 Web | `--run-public-web` | Web 用例在启动浏览器前跳过 |
| 真实 Android / iOS | `--run-mobile` | `device` 用例跳过，不创建 Appium Session |
| Android/iOS Mock | 无需开关 | 默认本地运行，只创建 `synthetic-*` 合成设备 |
| 本地 Demo Shop 联调 | 设置 `DEMO_SHOP_URL` 并先启动服务 | 未设置时跳过 |

这些开关是防误操作边界，不要写进 `pyproject.toml` 的默认参数，也不要为了让
CI“全绿”删除 guard fixture。

### 三条显式执行命令

确认目标、网络与数据范围后，三条主线命令是：

```bash
pytest tests/api -q --run-public-api
pytest tests/web -q --run-public-web
pytest tests/mobile -q --run-mobile
```

在运行真机前，先执行完全离线的 App 框架练习：

```bash
pytest tests/unit/测试_离线移动端成功流程.py \
  tests/unit/测试_离线移动端故障与清理.py \
  tests/unit/测试_离线移动端运行装配.py -q
```

它们不是要求一次全部执行。每次只运行你已经准备好的技术线：

- 公共 API 命令只做低频功能调用，不并行、不压测；
- 公共 Web 命令会真正打开第三方站点；
- 移动命令会控制 `.env` 中明确指定的设备或模拟器；
- Android 真机存在多个设备时必须设置 `MOBILE_UDID`，不能“随便选一个”；
- iOS 只能在满足 Xcode、模拟器/测试设备和 WDA 条件的 macOS 上运行。

## 5. 目录树

```text
labs/automation-practice/
├── README.md
├── 环境变量示例.env
├── pyproject.toml
├── scripts/
│   ├── 检查自动化测试环境.sh
│   └── 下载公开演示应用.sh
├── src/qa_learning/
│   ├── 运行配置.py
│   ├── api/
│   │   ├── 接口客户端.py
│   │   ├── 响应数据契约.py
│   │   ├── 公开占位文章接口.py
│   │   ├── 公开预订服务接口.py
│   │   └── 本地演示商城接口.py
│   ├── web/
│   │   ├── 浏览器练习目标.py
│   │   ├── pages/
│   │   └── flows/
│   └── mobile/
│       ├── 移动端驱动工厂.py
│       ├── mock/
│       │   ├── 移动端契约.py
│       │   ├── 假移动端驱动.py
│       │   ├── 运行装配.py
│       │   ├── 故障注入.py
│       │   ├── 证据采集.py
│       │   └── 公开演示应用.py
│       └── screens/
└── tests/
    ├── conftest.py
    ├── api/
    ├── web/
    ├── mobile/
    └── unit/                         # 默认运行的离线 App Mock/Contract 测试
```

移动端文件会根据 Android/iOS 教程持续增加；以实际仓库为准。分层原则是：

- `运行配置.py` 只负责环境差异；
- Client / Driver 负责协议与会话；
- API Service、Page、Screen 负责可复用业务行为；
- Flow 负责跨页面、跨端业务编排；
- Test 保留测试意图和关键业务断言；
- Fixture 负责创建、隔离、证据和清理。

## 6. 运行本地 Demo Shop

本地虚构商店位于相邻目录 [`labs/demo-shop`](../demo-shop/README.md)。先在终端 A：

```bash
cd labs/demo-shop
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test,ui]'
uvicorn app.商城服务:app --host 127.0.0.1 --port 8000
```

终端 B 回到本目录：

```bash
cd labs/automation-practice
source .venv/bin/activate
DEMO_SHOP_URL=http://127.0.0.1:8000 pytest tests/api/测试_本地演示商城接口.py -q
```

服务只监听 `127.0.0.1`。订单存在内存中，重启即清空，适合反复练习：

- 商品查询和 Unicode；
- 金额计算；
- 库存边界；
- 幂等键；
- 同键同请求与同键不同请求；
- API 准备数据、Web 验证结果；
- 本地低负载性能 smoke。

不要把本机实验结果称为线上容量，也不要把服务开放到公网。

## 7. 无设备先跑 App Mock

离线框架使用从零生成的公开合成商城，覆盖 Android/UiAutomator2 与
iOS/XCUITest 两套平台契约。它不会导入 Appium、扫描 adb/simctl、访问网络或
控制任何设备：

```bash
pytest tests/unit/测试_离线移动端成功流程.py \
  tests/unit/测试_离线移动端故障与清理.py \
  tests/unit/测试_离线移动端运行装配.py -q
```

建议按这个顺序阅读并单步调试：

```text
移动端契约.py
  → 公开演示应用.py
  → 假移动端驱动.py
  → 运行装配.py
  → 故障注入.py
  → 证据采集.py
  → tests/unit/测试_离线移动端*.py
```

成功流会让同一个“登录 → 滑动 → 打开学习商品”任务分别运行在 Android 和 iOS
契约上；失败流可稳定注入定位失败、操作超时、设备断连和 App 崩溃，并验证证据
优先于清理、`quit()` 幂等、每个 Session 状态隔离。完整讲解见
[App 自动化 Mock 框架全流程](../../docs/09-自动化实战/07-移动端自动化模拟框架全流程.md)。

Mock 只证明框架控制流和业务编排，不证明安装包、真实元素树、手势、权限、
ADB/WDA、签名、系统版本兼容性或性能。真机连接后必须继续完成下面两节 smoke。

## 8. 配置自己的 Android 真机

手机打开开发者选项与 USB 调试，连接后先确认：

```bash
adb devices -l
```

状态必须是 `device`，不是 `unauthorized` 或 `offline`。复制模板：

```bash
cp 环境变量示例.env .env
```

只在本机 `.env` 中填写公开练习 App：

```dotenv
MOBILE_PLATFORM=android
MOBILE_APP_PROFILE=api_demos
MOBILE_DEVICE_NAME=Android
MOBILE_UDID=这里填写adb显示的设备序列号
MOBILE_APP=/绝对路径/ApiDemos-debug-v6.0.14.apk
```

下载脚本只从教程已核对的公开 Release 获取资产，并对可核验资产检查 SHA-256：

```bash
bash scripts/下载公开演示应用.sh mobile-apps
```

下载后仍应人工核对来源、文件名与哈希。APK、`.app`、zip 和真机日志都不应提交。

启动服务后再运行：

```bash
appium
pytest tests/mobile -q -m android --run-mobile
```

首次先跑一条 smoke，确认目标 UDID、包名和 Activity，再扩大范围。

## 9. 配置 iOS 模拟器

iOS 自动化必须在 macOS 上完成。先确认：

```bash
xcodebuild -version
xcrun simctl list devices available
appium driver doctor xcuitest
```

将官方 Simulator 包放到本机忽略目录，在 `.env` 中使用绝对路径。当前 Driver
Factory 接受官方 `.zip`，无需为了运行测试把二进制展开进仓库：

```dotenv
MOBILE_PLATFORM=ios
MOBILE_APP_PROFILE=my_demo_app
MOBILE_UDID=这里填写simctl显示的Simulator UDID
IOS_DEVICE_NAME=iPhone 17 Pro
MOBILE_APP=/绝对路径/SauceLabs-Demo-App-2.2.2-Simulator.zip
IOS_BUNDLE_ID=com.saucelabs.mydemo.app.ios
```

实际模拟器名称以 `simctl` 输出为准，不要机械照抄示例。启动 Appium 后：

```bash
pytest tests/mobile -q -m ios --run-mobile
```

真机 iOS 还涉及开发者证书、Provisioning Profile、设备信任与 WebDriverAgent
签名，不建议在第一阶段跳过模拟器直接开始。

## 10. Toolshop 跨端 Capstone

[Practice Software Testing / Toolshop](https://github.com/testsmith-io/practice-software-testing)
提供 Web、REST API、Swagger、Android 和 iOS Simulator 练习资产，同一版本的
多端共享业务环境，适合毕业项目。

推荐旅程：

```text
API 创建或查询合成测试数据
  → Web 登录、搜索、加入购物车
  → Android 验证商品与购物车
  → iOS 验证同类关键路径
  → API 查询最终状态
  → 汇总跨端差异与失败证据
```

公共实例只跑少量串行 smoke；完整回归应使用自己控制的本地部署。官方仓库许可
限制未经授权的重新分发、公开托管和商业使用，因此本仓库只链接官方来源：

- 不提交上游源码副本；
- 不提交 APK、iOS zip 或解压后的 `.app`；
- 不把本地部署公开暴露给第三方；
- 使用前重新阅读仓库当前 License 和 README。

Capstone 不要求同一条测试跨四端串成一个脆弱巨型脚本。更合理的交付是：

1. 一份风险与范围说明；
2. API、Web、Android、iOS 各自独立的关键测试；
3. 少量证明数据一致性的跨端旅程；
4. 可重复的数据准备和清理；
5. 一套失败证据与缺陷报告；
6. 公共 smoke 与本地回归的执行边界。

## 11. 失败证据

失败不是只有红色堆栈。至少保留：

| 技术线 | 推荐证据 |
|---|---|
| API | 方法、脱敏 URL、状态码、关联 ID、脱敏 JSON、Schema 路径 |
| Web | Playwright Trace、失败截图、必要时视频、Console/Network |
| Android | Appium 服务日志、截图、Page Source、受控 `adb logcat` |
| iOS | Appium/WDA 日志、截图、Page Source、Simulator/Xcode 诊断 |

Web 示例：

```bash
pytest tests/web \
  --run-public-web \
  --tracing retain-on-failure \
  --screenshot only-on-failure \
  --output test-results
```

查看 Trace：

```bash
python -m playwright show-trace test-results/<case>/trace.zip
```

证据文件只能包含公开 Demo 和合成数据。提交前检查：

```bash
git status --short
git diff --check
```

## 12. 阶段验收

### 环境验收

- [ ] Python 虚拟环境可重建，没有依赖全局包“碰巧可用”；
- [ ] `pytest -q` 不访问公网、不启动浏览器、不控制设备；
- [ ] 三个显式开关都能说明其风险；
- [ ] `.env`、应用安装包、报告和设备日志未进入 Git；
- [ ] 所有数据均为公开演示数据或明显虚构的数据。

### API 验收

- [ ] Client 每次请求都有显式超时；
- [ ] 日志隐藏 Token、Cookie、密码和 Secret；
- [ ] 能解释 JSONPlaceholder 模拟写入与 Restful Booker 真 CRUD；
- [ ] CRUD 即使中途失败也会尝试清理；
- [ ] 公共 API 不并行、不压测、不作为 PR 硬门禁。

### Web 验收

- [ ] Locator 表达用户语义，不依赖脆弱 `nth()`；
- [ ] 使用条件等待和 Web-first 断言，没有碰运气的固定睡眠；
- [ ] Page、Flow 和 Test 职责清楚；
- [ ] 每条测试使用隔离 Context；
- [ ] 失败可通过 Trace 和截图独立分析。

### 移动验收

- [ ] 不接设备也能跑完 Android/iOS Mock 成功流与四类故障流；
- [ ] 能说清 Mock 只验证框架，不等于真机验证；
- [ ] 能明确说出当前控制的是哪台设备/模拟器；
- [ ] Android 使用稳定 resource-id/accessibility id，并理解 UiSelector 的边界；
- [ ] iOS 能解释 XCUITest、WDA、Bundle ID 和签名关系；
- [ ] 测试清理应用状态，不依赖上一条用例；
- [ ] Appium 失败有截图、Page Source 和服务端日志。

### 工程验收

- [ ] Offline、Local、Public、Mobile 四类任务分开；
- [ ] PR 只依赖确定性、本地可控检查；
- [ ] 公共环境失败能区分网络、环境变化与产品断言；
- [ ] 没有用盲目重试隐藏竞态或真实缺陷；
- [ ] Toolshop 项目包含范围、风险、代码、证据、报告和复盘。

出现问题时，不要先加重试或固定等待，按
[故障排查手册](../../docs/09-自动化实战/06-故障排查.md)从环境、连接、会话、
定位、状态和断言逐层定位。
