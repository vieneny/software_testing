# 阶段 3：Web 与 App UI 自动化

目标：只把用户可见、跨层且高价值的旅程放入 UI 自动化，并建立稳定定位、状态等待、隔离、证据和失败分诊能力。

## 两条学习线

| 路线 | 主入口 | 配套工程 | 关键结果 |
|---|---|---|---|
| Web | [现代网页自动化](./01-现代网页自动化测试.md) → [Web 项目全流程](./04-Web自动化项目全流程.md) | [`automation-practice`](../../labs/automation-practice/README.md) | Playwright Page/Flow、Trace、跨浏览器 |
| App | [App 自动化学习阶段](./02-App自动化学习阶段/README.md) | [`app-automation-learning`](../../labs/app-automation-learning/README.md) | Appium 3、Screen/Flow、离线故障与真机 smoke |

[传统 Selenium](./03-传统网页自动化测试选修.md)用于维护存量项目，不与 Playwright 主线并行重复实现所有用例。

## 共同原则

- 测试表达用户行为，定位器留在 Page/Screen；
- 等待可观察状态，不使用固定睡眠同步页面；
- 每条测试拥有独立 Context、Session 或可靠状态重置；
- 保留少量关键 E2E，大量规则下沉 API/单元层；
- 失败证据必须能说明页面、操作、状态和时间；
- 公共网站和真实设备只在明确开关下运行。

## 完成证据

- [ ] Web 一条购买主路径和一条失败路径；
- [ ] App 一条登录到结算的合成业务流；
- [ ] Android 或 iOS 一个公开 Demo 真机/模拟器 smoke；
- [ ] 能主动制造定位、等待和状态污染失败；
- [ ] Web Trace 或 App screenshot + source + driver log；
- [ ] 能说明哪些场景不应放 UI 层。

完成后进入 [性能测试阶段](../04-性能测试/README.md)。
