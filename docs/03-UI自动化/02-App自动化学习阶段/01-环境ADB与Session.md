# 第一章：环境、ADB 与 Appium Session

本章目标不是把工具全部装上，而是证明 Python 能通过 Appium 3 和指定平台 Driver 控制一台明确的练习设备，并且无论测试成功或失败都能释放 Session。

## 1. 先建立组件边界

```text
pytest 用例
  → Appium Python Client
  → Appium 3 Server
  → UiAutomator2 / XCUITest Driver
  → ADB / WDA
  → Android / iOS
  → 被测 App
```

每层都要能独立检查。客户端导入失败与设备离线不是同一问题，不能靠反复重装 Appium 一起解决。

## 2. Android 环境验收

```powershell
python --version
node --version
npm --version
appium --version
appium driver list --installed
appium driver doctor uiautomator2
adb version
adb devices -l
```

期望：Appium 为 3.x；UiAutomator2 已安装；唯一目标设备状态为 `device`。`unauthorized` 要在已解锁设备上确认调试授权，`offline` 先检查数据线、USB 模式和 ADB Server。

常用命令都显式指定设备：

```powershell
adb -s <UDID> shell getprop ro.build.version.release
adb -s <UDID> shell pm list packages -3
adb -s <UDID> shell dumpsys window | findstr mCurrentFocus
adb -s <UDID> shell am force-stop <PACKAGE>
adb -s <UDID> shell am start -W <PACKAGE>/<ACTIVITY>
```

## 3. iOS 环境验收

iOS 只能在 macOS 上完成：

```bash
xcodebuild -version
xcrun simctl list devices available
appium driver list --installed
appium driver doctor xcuitest
```

Simulator 先验证无签名主链路；真机再处理 Developer Mode、Team、Provisioning Profile、Bundle ID 和 WDA。macOS、Xcode、iOS Runtime、设备版本与 XCUITest Driver 必须按当前兼容表组合。

## 4. 配置项目

```powershell
cd labs\app-automation-learning
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e '.[all]'
Copy-Item .env.example .env
```

填写 `MOBILE_PLATFORM`、`MOBILE_APP_PROFILE`、`MOBILE_UDID` 和绝对 `MOBILE_APP` 路径。配置解析位于 `src/qa_learning/运行配置.py`，Session 校验位于 `mobile/移动端驱动工厂.py`。

## 5. Session 生命周期

一个可靠 fixture 至少负责：

1. 在连接设备前校验配置；
2. 每条用例创建明确 Session；
3. 失败时先采集可用证据；
4. teardown 中调用 `quit()`；
5. 清理异常不覆盖原始失败。

不要默认 `noReset=True` 共享历史登录态。需要已登录前置时，使用 API、固定合成账号或显式 UI 步骤准备，并让测试说明该状态从哪里来。

## 6. 本章练习

- [ ] 保存 Server、Driver、Python Client、OS 与设备版本；
- [ ] 用明确 UDID 建立 Session；
- [ ] 主动写错 App 路径，确认在连接前失败；
- [ ] 主动让断言失败，确认 Session 仍退出；
- [ ] 记录一次从客户端到设备的分层排障过程。
