# demo-shop 综合测试实验

`demo-shop` 是从零编写的虚构商店，使用内存数据运行，重启服务会清空订单。

## 你会练到什么

- 从业务规则设计功能和接口用例；
- 用 requests + pytest 验证状态码、响应结构、错误语义、幂等性和数据一致性；
- 用 Playwright 覆盖 Web 用户关键旅程；
- 用 k6 / Locust 建立最小性能基线；
- 用版本化 JSONL 数据集和确定性评分器搭建 AI 评测的第一道门禁；
- 在 CI 中分层运行并保存可诊断结果。

## 系统规则

本实验只有三类能力：

| 接口 | 规则 | 主要风险 |
|---|---|---|
| `GET /api/products` | 可按关键词过滤，`limit` 为 1～100 | 边界、编码、空结果、契约 |
| `GET /api/products/{id}` | 不存在返回 404 | ID 类型、错误语义 |
| `POST /api/orders` | 1～20 个条目；每种数量 1～10；不可超过库存 | 校验、金额、库存、幂等、并发 |
| `GET /api/orders/{id}` | 读取本进程创建的订单 | 状态、数据一致性、隔离 |

创建订单必须携带长度 8～128 的 `Idempotency-Key`：

- 同一个键、同一个请求体重复提交，返回同一个订单；
- 同一个键、不同请求体重复提交，返回 409；
- 缺少键或格式不合法，返回 422。

这是教学实现，不是生产参考架构。它没有持久化、事务、真实库存扣减、鉴权、分布式锁或多实例一致性；这些限制正是后续设计风险与扩展实验的入口。

## 1. 启动服务

要求 Python 3.11 或更高版本：

```bash
cd labs/demo-shop
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[test]'
uvicorn app.商城服务:app --host 127.0.0.1 --port 8000
```

浏览器打开 `http://127.0.0.1:8000`。OpenAPI 交互文档位于 `http://127.0.0.1:8000/docs`。

只监听 `127.0.0.1`，不要在不理解网络和安全风险时把教学服务暴露到公网。

健康检查：

```bash
curl -i http://127.0.0.1:8000/health
```

预期为 200，JSON 主体是 `{"status":"ok"}`。

## 2. 手工探索接口

查询商品：

```bash
curl -sS 'http://127.0.0.1:8000/api/products?keyword=马克杯&limit=5'
```

创建订单：

```bash
curl -i -X POST 'http://127.0.0.1:8000/api/orders' \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: learning-demo-0001' \
  -d '{"items":[{"product_id":1,"quantity":2}]}'
```

立即用完全相同的命令再发一次，观察订单 ID 是否相同。然后修改数量但保留幂等键，观察 409。这比只验证一次 201 更接近真实风险。

## 3. 运行接口与 AI 基线测试

保持服务运行，在另一个终端进入同一目录并激活虚拟环境：

```bash
pytest tests/api tests/ai -q
```

使用其他端口时：

```bash
DEMO_BASE_URL=http://127.0.0.1:9000 pytest tests/api -q
```

只运行确定性 AI 评测，不需要模型密钥或网络：

```bash
python tests/ai/人工智能回答评测器.py
```

尝试删除某条 `candidate_output` 的必需词，确认脚本返回非零退出码。这个实验说明：评测门禁必须能主动失败，才能证明它真的在保护质量。

## 4. 运行 Web UI 测试

```bash
python -m pip install -e '.[test,ui]'
python -m playwright install chromium
pytest tests/ui -q
```

诊断失败可开启 trace：

```bash
pytest tests/ui --tracing=retain-on-failure --screenshot=only-on-failure
```

重点观察：测试使用 role 和可访问名称定位，而不是依赖容易变化的 CSS 层级；等待依赖可见状态和断言，而不是固定休眠。

## 5. 运行性能 smoke

### k6

先按 [k6 官方安装说明](https://grafana.com/docs/k6/latest/set-up/install-k6/) 安装 k6，再运行：

```bash
k6 run tests/performance/轻量性能冒烟脚本.js
```

调整小规模负载：

```bash
VUS=5 DURATION=30s k6 run tests/performance/轻量性能冒烟脚本.js
```

脚本里的 300 ms 只是本地教学阈值，不是通用行业标准。真实项目必须从用户体验目标、服务 SLO、环境能力与业务量推导阈值。

### Locust

```bash
python -m pip install -e '.[performance]'
locust -f tests/performance/用户负载模型.py --host http://127.0.0.1:8000
```

访问终端提示的 Locust 页面，从极低负载开始。不要把开发电脑上的结果描述成生产容量。

## 建议实验顺序

### 实验 A：建立测试模型

1. 从本页规则提取对象、属性、约束、状态和依赖；
2. 为 `quantity` 和 `limit` 设计等价类与边界；
3. 为幂等键设计状态表；
4. 为下单列出影响 × 可能性的风险排序；
5. 标记哪些风险适合 API、UI、性能或代码级测试。

完成标准：别人能从模型理解你的取舍，而不是只看到用例列表。

### 实验 B：增强 API 自动化

- 为关键词空白、Unicode、未知商品、多条商品和金额计算增加用例；
- 把重复请求封装成业务客户端；
- 引入测试数据工厂，保持随机值可复现；
- 从 `/openapi.json` 读取契约并增加兼容性检查；
- 让 smoke 集合在 30 秒内完成。

完成标准：测试可乱序、重复运行三次，失败信息能直接指向违反的规则。

### 实验 C：发现并说明设计缺陷

研究以下问题，但不要先急着改应用：

- 两个不同幂等键同时下单会不会突破库存？
- 应用多实例部署后，内存幂等记录是否有效？
- 重复请求应返回 200 还是 201？契约如何约定？
- 商品名称直接插入 HTML 是否有安全风险？
- 服务重启后查询旧订单会发生什么？

先写可观察的失败或风险证据，再提出方案。测试的价值是支持决策，不是为了让所有用例变绿。

### 实验 D：建立 AI 评测集

1. 将 `人工智能评测数据集.jsonl` 扩展到 30 条合成样本；
2. 按事实性、规则遵循、拒答、安全和计算分类；
3. 为每条样本写清期望行为，不强求唯一文案；
4. 增加大小写、同义表达和 Unicode 处理，观察关键词评分的局限；
5. 设计人工评分量表，并抽样比较人与自动评分的一致性；
6. 只有在数据安全和成本可控时，再接入模型评分器。

完成标准：报告分项指标、失败样本和限制，不用单一总分掩盖安全失败。

## 清理

在服务终端按 `Ctrl+C` 停止。订单只在内存中，进程退出后自动清空。虚拟环境和本地报告已由仓库 `.gitignore` 排除。

提交前仍需运行：

```bash
git status --short
git diff --check
```

确认没有 `.env`、Token、浏览器登录状态、HAR、日志、截图或其他本机工作资料进入变更列表。
