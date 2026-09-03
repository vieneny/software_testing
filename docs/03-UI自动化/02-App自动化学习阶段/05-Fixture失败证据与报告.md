# 第五章：Fixture、失败证据与报告

本章关注测试是否能独立运行、失败后是否可诊断、清理失败是否会掩盖根因。

## 1. Fixture 生命周期

```text
校验配置
  → 准备数据
  → 创建 Session
  → yield 给测试
  → 记录第一次失败
  → 采集可用证据
  → 清理业务状态
  → quit Session
```

Session 通常使用 function scope。设备资源昂贵时可以复用设备，但不能复用不可控的 App 状态；每条测试仍需回到已知起点。

## 2. 第一失败原则

原始断言或驱动异常是主错误。截图、Page Source、日志、清理任一步再次失败时，记录为附加诊断，不覆盖主错误。

配套 Mock 能稳定注入：

- 元素不存在；
- 操作超时；
- 设备断连；
- App 崩溃。

对应测试位于 `tests/unit/测试_离线移动端故障与清理.py`。

## 3. 最小证据包

| 文件 | 最少内容 |
|---|---|
| `run.json` | case ID、阶段、时间、平台和版本 |
| `screenshot.png` | 失败时可见页面 |
| `page-source.xml` | 当时元素树 |
| `appium.log` | Session 与命令链 |
| `device.log` | 限定范围的 logcat/WDA 诊断 |
| `failure.txt` | 原始异常、步骤和关键上下文 |

目录使用 `run-id/case-id/`，并发时不会覆盖。正常通过只保留关键里程碑；失败优先采集最小必要证据。

## 4. 日志设计

日志应包含页面、动作、稳定定位名称、耗时、结果和关联 ID；不要把所有输入值、完整 capabilities 或请求头直接打印出来。

错误信息示例：

```text
CheckoutScreen.wait_loaded failed after 15s
expected: accessibility id=checkout-summary
observed: currentActivity=.CartActivity, overlay=network-error
```

它比“元素定位失败”更能指导下一步。

## 5. Allure 的位置

Allure 用于汇总步骤、附件、环境与趋势，不负责修复测试设计。接入前先确认：

- 失败退出码正确；
- 测试名和 case ID 可追踪；
- 关键断言可见；
- 证据目录不会互相覆盖；
- 报告生成失败不会改变用例事实。

## 6. 本章练习

- [ ] 分别注入四类离线故障；
- [ ] 检查 `quit()` 幂等；
- [ ] 故意让截图失败，确认主异常未变化；
- [ ] 为一个失败写出“现象、证据、判断、下一步”；
- [ ] 清理后重新运行同一用例，结果一致。
