# 第三章：项目结构与 Page Object

本章解决课程工程最容易出现的问题：Base 类过大、fixture 串联业务、Page 吞掉断言、测试依赖执行顺序。

## 1. 目标结构

```text
配置 → Driver Factory → Base Screen → Screen → Flow → Test
                                      ↘ Evidence
Fixture ───────── 生命周期、状态准备、证据和清理 ───────┘
```

| 组件 | 输入 | 输出 | 不负责 |
|---|---|---|---|
| 配置 | 环境变量 | 已解析 Settings | 控制设备 |
| Driver Factory | Settings | WebDriver Session | 登录和搜索 |
| Base Screen | Driver + Locator | 原子交互 | 完整业务 |
| Screen | 页面状态 | 页面能力 | 创建 Session |
| Flow | 多个 Screen | 业务结果 | 隐藏关键断言 |
| Test | 场景与预期 | 质量结论 | XPath 和端口 |
| Fixture | 资源范围 | 可用上下文 | 让用例共享脏状态 |

## 2. Base Screen 的边界

只放多页面共享的协议级能力：

- `wait_visible`、`wait_clickable`、`wait_until_gone`；
- `tap`、`type_text`、`text`；
- 有界滚动；
- 写入调用方指定目录的截图。

“提交订单”“选择配送地址”“关闭某活动弹窗”属于页面或业务能力。

## 3. Screen Object

Screen 同时封装定位器、页面加载标识和页面内行为：

```python
class SearchScreen(BaseScreen):
    INPUT = (AppiumBy.ACCESSIBILITY_ID, "search-input")
    RESULT = (AppiumBy.ACCESSIBILITY_ID, "search-result")

    def search(self, keyword: str) -> str:
        self.type_text(self.INPUT, keyword)
        return self.text(self.RESULT)
```

测试只看到 `search("毛巾")`，但仍对返回结果进行业务断言。

## 4. Flow 的使用条件

跨三个以上页面或会被多条用例复用时再建立 Flow。例如 `PurchaseFlow`：登录、搜索、加购、结算。登录错误、搜索空结果、数量边界仍应有独立测试，不能全部依赖一条 E2E。

配套代码 `mobile/course_project.py` 使用 `CommerceScreenGateway` 协议，让同一业务编排既能使用合成 Adapter，也能逐步替换为真实 Screen。

## 5. 依赖方向

```text
Test → Flow → Screen → Base/Driver
              ↓
           Locator
```

下层不能导入 Test；Base 不能知道登录页面；配置不能导入 WebDriver。出现循环导入通常说明职责混在了一起。

## 6. 本章练习

- [ ] 从单文件脚本画出实际依赖图；
- [ ] 把定位器移入 Screen；
- [ ] 把登录到结算的编排移入 Flow；
- [ ] 保留 Test 中的金额、商品和结果断言；
- [ ] 单独运行任一测试，不依赖文件顺序；
- [ ] 说明每个目录为什么存在，不能只复述名称。
