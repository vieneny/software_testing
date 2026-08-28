# 社区问答系统：FastAPI + React 全链路测试实战

这是一个面向软件测试学习的“类似知乎/技术论坛”复杂业务骨架。它不是只有几个演示接口的玩具：首期已贯通问题、回答、搜索分页、投票、写请求幂等、问题关闭/开放、回答采纳、统一异常、数据库迁移和 AI 摘要，后续可以沿着认证、内容治理、消息通知、搜索、缓存和可观测性继续扩展。

## 1. 当前可以实际操作什么

已实现的最小闭环：

- 浏览、关键词搜索和分页查询问题；
- 发布带标签的问题，查看问题详情；
- 发布回答，关闭问题后禁止新回答，重新开放后恢复；
- 采纳、切换和取消采纳回答，同一问题最多一个回答被采纳；
- 发布问题和回答支持 `Idempotency-Key`，安全重试不会生成重复数据；
- 对问题赞成、反对、修改投票，相同投票幂等冲突；
- 调用统一 Python AI 中间件生成摘要和风险提示；
- React 页面覆盖问题列表、发布、详情、回答、投票、AI 摘要；
- SQLite 零依赖练习模式与 MySQL 容器生产近似模式；
- Alembic 首版迁移、统一错误响应、Request ID、OpenAPI；
- 后端 pytest 接口测试和可继续扩展的测试清单。

当前版本没有伪装成“全部完成”。认证、关注、收藏、审核、通知等内容在[功能与测试清单](功能与测试清单.md)中明确标为后续迭代，可以直接作为学习需求和测试任务。

## 2. 技术栈

| 层次 | 技术 | 学习价值 |
|---|---|---|
| 前端 | React 19、TypeScript、Vite、React Router | SPA 路由、表单、状态、错误处理、API 联调 |
| 接口 | Python 3.12、FastAPI、Pydantic Settings | REST 契约、数据校验、依赖注入、OpenAPI |
| 领域与持久化 | SQLAlchemy 2、Alembic | 分层设计、关系模型、事务、迁移 |
| 数据 | MySQL 8.4、SQLite | 正式环境与轻量自动化测试双模式，正文使用 LONGTEXT/TEXT |
| 缓存基础设施 | Redis 7.4 | 为热点问题、限流、会话和异步任务预留 |
| AI | 统一 Python AI 中间件、HTTPX | 模型隔离、超时、上游异常、AI 质量测试 |
| 运行 | Docker Compose、Nginx | 多服务编排、反向代理、健康检查 |

Redis 已进入运行架构，首期业务尚未读写 Redis。这是刻意保留的第二阶段任务：可以分别实现列表缓存、浏览量延迟聚合和限流，再设计缓存一致性测试。
因此后端当前不会把 Redis 设为启动硬依赖；接入缓存后再定义连接失败时的降级或
失败策略，并为两种策略补测试。

后端镜像通过提交的 `uv.lock` 和 `uv sync --frozen` 固定依赖解析，前端镜像通过
`package-lock.json` 和 `npm ci` 固定依赖解析；两个构建上下文都排除本地环境、
缓存、测试报告和练习数据库。

## 3. 目录结构

```text
社区问答系统/
├── backend/
│   ├── app/
│   │   ├── interfaces/api/          # 路由、请求/响应模型、依赖装配
│   │   ├── application/             # 问答用例与 AI 端口
│   │   ├── domain/questions/        # 实体、规则、仓储抽象
│   │   ├── infrastructure/          # SQLAlchemy 仓储、AI HTTP 客户端
│   │   └── core/                    # 配置、统一错误模型
│   ├── migrations/                  # Alembic 迁移
│   └── tests/                       # pytest 接口测试
├── frontend/
│   └── src/
│       ├── api/                     # 类型化 API 客户端
│       └── pages/                   # 列表、发布、详情页面
├── docker-compose.yml
├── 架构设计.md
└── 功能与测试清单.md
```

## 4. 最快启动：SQLite 本地模式

要求：Python 3.12、[uv](https://docs.astral.sh/uv/)、Node.js `20.19+` 或
`22.12+`（本项目按 Node.js 22 验证，满足 Vite 8 的运行要求）。

启动后端：

```bash
cd backend
cp .env.example .env
uv sync --dev
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

另开终端启动前端：

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

入口：

- 前端：<http://localhost:5173>
- OpenAPI：<http://localhost:8000/docs>
- 健康检查：<http://localhost:8000/api/v1/health>

健康检查只返回 `ai_configured` 布尔状态，不返回 AI 服务地址，避免暴露容器名、
端口等内部拓扑。

## 5. Docker Compose：MySQL + Redis 模式

```bash
cp .env.example .env
docker compose up --build
```

访问 <http://localhost:3000>。MySQL 对宿主机暴露 `3307`，Redis 暴露 `6380`，避免和常见本地端口冲突。

同时启动相邻目录的统一 AI 中间件：

```bash
docker compose --profile ai up --build
```

如果 AI 中间件独立运行，只要修改后端的 `AI_BASE_URL` 和 `AI_SUMMARY_PATH`。不启动 AI 中间件时，社区核心功能仍可运行，只有 AI 摘要接口会返回结构化的 `502 upstream_service_error`。

停止容器：

```bash
docker compose down
```

清除本项目练习数据库（会删除容器卷中的练习数据）：

```bash
docker compose down -v
```

执行最后一个命令前应确认数据确实只是可丢弃的合成数据。

## 6. API 快速练习

创建问题：

```bash
curl -X POST http://localhost:8000/api/v1/questions \
  -H 'Content-Type: application/json' \
  -H 'X-Request-ID: learning-request-001' \
  -H 'Idempotency-Key: question-create-learning-001' \
  -d '{
    "title": "如何验证重复提交不会产生两条订单？",
    "content": "这是一个完全合成的幂等接口测试练习场景。",
    "author_name": "学习者001",
    "tags": ["api", "幂等性"]
  }'
```

分页与搜索：

```bash
curl 'http://localhost:8000/api/v1/questions?page=1&page_size=10&keyword=幂等'
```

将响应中的问题 ID 替换到下面。问题和回答创建接口首次成功返回 `201`；
以同一幂等键和同一规范化内容重试返回同一个资源、状态码 `200`，同时响应头
`Idempotency-Replayed: true`。同一幂等键若改了内容会返回
`409 idempotency_key_reused`：

```bash
curl -X POST http://localhost:8000/api/v1/questions/问题ID/answers \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: answer-create-learning-001' \
  -d '{"content":"连续提交三次，并验证响应和数据库唯一约束。","author_name":"学习者002"}'

curl -X POST http://localhost:8000/api/v1/questions/问题ID/votes \
  -H 'Content-Type: application/json' \
  -d '{"voter_key":"synthetic-user-001","value":1}'
```

关闭问题、重新开放和采纳回答：

```bash
curl -X PATCH http://localhost:8000/api/v1/questions/问题ID/status \
  -H 'Content-Type: application/json' \
  -d '{"status":"closed"}'

curl -X PATCH http://localhost:8000/api/v1/questions/问题ID/status \
  -H 'Content-Type: application/json' \
  -d '{"status":"open"}'

curl -X PUT http://localhost:8000/api/v1/questions/问题ID/answers/回答ID/acceptance \
  -H 'Content-Type: application/json' \
  -d '{"accepted":true}'
```

取消采纳传 `{"accepted":false}`；采纳另一个回答会在同一事务中取消原采纳。
当前没有身份系统，因此这些管理操作只适合本地合成数据练习，不能直接部署到公网。

### 6.1 写请求幂等的学习契约

- 键只能使用 `A-Z a-z 0-9 . _ : -`，长度为 8～128；
- 前端会为当前表单内容生成 UUID；网络失败后原样重试会复用该键；
- 后端对去空格、标签小写去重后的业务内容计算 SHA-256 指纹；
- 唯一约束是 `scope + idempotency_key`，问题发布和每个问题下的回答互不串线；
- 幂等记录和业务数据在同一数据库事务提交；唯一约束负责兜住并发竞争；
- 生产化时还应增加幂等记录 TTL/归档、容量告警和并发压测。

投票会在 MySQL 事务中先锁定问题行，再读取用户已有投票并更新聚合分数。这能避免
不同用户并发投票时丢失 `score` 增量，也能让同一用户并发首投在锁后读到已有记录。
SQLite 不提供等价的行锁语义，因此并发投票验收必须使用 Compose MySQL 或
Testcontainers MySQL；SQLite 只用于快速功能回归。

## 7. AI 中间件契约

社区服务只依赖一个 HTTP 端口，不直接绑定任何模型厂商：

```http
POST /api/v1/forum/summarize
Content-Type: application/json
```

请求：

```json
{
  "title": "如何测试幂等接口？",
  "content": "完全合成的问题正文",
  "answers": ["完全合成的回答一"]
}
```

响应：

```json
{
  "api_version": "v1",
  "request_id": "learning-request-001",
  "summary": "该问题关注重复请求下的数据唯一性。",
  "risk_hints": ["并发竞争", "重复消费", "事务回滚"],
  "model": "mock-community-model"
}
```

该边界便于测试超时、错误码、畸形响应、提示词注入、敏感数据拦截、结果稳定性和模型切换。AI 中间件可以先使用确定性 Mock，之后再接真实模型。

消费者契约不会把任意 2xx 当成功：顶层必须是 JSON 对象，`api_version` 必须
严格等于 `v1`，响应 `request_id` 必须与本次实际发送的 canonical ID 完全相同；
`summary` 和 `model` 必须是非空字符串，分别不超过 10,000 和 200 字符；
`risk_hints` 必须是字符串列表，最多 20 项，每项非空且不超过 500 字符。缺字段、
数组顶层、关联 ID 不匹配、数字冒充字符串、超长内容或混合类型列表都会转换成
安全的 `502 upstream_service_error`，响应不会回显上游原始内容。

论坛允许保存的正文可能大于 AI 中间件单次契约。发送前客户端会创建一个确定性的
“AI 副本”：

- 标题最多 300 个 Unicode 字符；
- 正文最多 10,000 个 Unicode 字符；
- 最多取前 100 条回答，每条最多 5,000 个字符；
- 标题、正文、回答合计不超过 20,000 个字符；
- 优先保留标题、正文开头和按时间排序的较早回答。

**截断只发生在发给 AI 的临时副本中，不会修改数据库里的原帖或回答。** Python
和中间件均按 Unicode 码点计数，而不是按 UTF-8 字节数计数。MySQL 中的问题和回答
正文使用 `LONGTEXT`，SQLite 练习模式仍使用 `TEXT`，因此合法的 20,000 字符
Unicode 正文不会撞上 MySQL `TEXT` 的字节上限。

## 8. 请求关联 ID

入口优先接受 `X-Request-ID`，兼容旧的 `X-Trace-ID`。合法值只能包含
`A-Z a-z 0-9 . _ : -` 且最长 128 字符；非法或缺失时生成 UUID，避免回显不可信
请求头。所有成功和受控错误响应都会同时返回：

```http
X-Request-ID: learning-request-001
X-Trace-ID: learning-request-001
```

错误体同时提供规范字段 `request_id` 和兼容字段 `trace_id`。社区后端把同一个
已校验 ID 传给 AI 中间件，便于跨服务排查。AI 摘要失败只影响这个独立端点，
不影响发布问题、回答、投票、搜索和详情。

论坛等待 AI 中间件的默认超时是 **25 秒**。预算推导为：最多 3 块内容 × 每块
分析/审核 2 类操作 × 每次最多 2 次尝试 × 单次 1.5 秒，最坏计算时间约 18 秒；
再预留约 7 秒给容器调度、网络、连接、JSON 序列化和事件循环抖动。原来的 10 秒
会在中间件仍按合法重试预算工作时提前断开。可在本地 `.env` 或 Compose 中通过
`AI_TIMEOUT_SECONDS` 覆盖，允许范围为大于 0 且不超过 120 秒，例如：

```dotenv
AI_TIMEOUT_SECONDS=35
```

增加超时只能容纳已知合法预算，不能代替性能告警、并发限制或异步任务设计。

所有 API 时间字段使用带时区的 ISO 8601 UTC，例如 `2026-07-27T08:00:00Z`
或 `2026-07-27T08:00:00+00:00`。SQLite/MySQL 驱动若返回 naive `datetime`，
响应映射会按项目的“数据库统一存 UTC”约定补上 UTC；已经带时区的值会转换为 UTC，
避免同一接口有时带时区、有时不带。

## 9. 运行测试

后端测试：

```bash
cd backend
uv sync --dev
uv run pytest
uv run pytest --cov=app --cov-report=term-missing
uv run ruff check .
```

前端类型与构建检查：

```bash
cd frontend
npm install
npm run typecheck
npm run build
```

测试目前覆盖健康检查、创建/列表/详情、关键词与标签组合、分页边界、标签归一化、
问题与回答幂等重试/冲突、关闭与重新开放、回答采纳切换、投票与改票、AI 严格契约、
OpenAPI、404/409/422/502 和关联 ID。完整进阶任务见
[功能与测试清单](功能与测试清单.md)。

## 10. 开源项目参考方式

本项目借鉴公开项目的产品形态和架构思想，不复制其业务数据：

| 项目 | 可学习内容 | 在本项目中的参考点 |
|---|---|---|
| [FastAPI Full Stack Template](https://github.com/fastapi/full-stack-fastapi-template) | FastAPI、前后端、数据库、容器、测试组合 | 配置隔离、容器化和全栈工程意识 |
| [Answer](https://github.com/apache/answer) | 问答、标签、投票、权限、插件 | 社区领域与后续能力清单 |
| [Forem](https://github.com/forem/forem) | 大型社区治理、内容与运营 | 审核、通知、标签和可观测性方向 |
| [Discourse](https://github.com/discourse/discourse) | 成熟论坛、信任等级、治理 | 反滥用、权限、复杂状态测试 |
| [FastAPI](https://github.com/fastapi/fastapi) | 类型化 API 与 OpenAPI | 接口层实现 |
| [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) | ORM、事务和关系模型 | 持久化与仓储实现 |

参考开源项目时先看许可证、架构和测试策略，再用自己的合成数据重新实现；不要把未知来源代码或真实数据直接拷入仓库。

## 11. 推荐学习顺序

1. 先跑 pytest 和 OpenAPI，理解每个已有接口。
2. 用 React 页面完成功能探索，记录等价类和边界值。
3. 阅读幂等、状态和采纳测试，再补并发重试与故障注入用例。
4. 使用 Playwright 实现“发布问题 → 回答 → 采纳 → 关闭 → 重新开放”的 UI 流程。
5. 使用 k6/Locust 压测问题列表，建立 P95 和错误率目标。
6. 启动 Mock AI 中间件，完成契约、故障与输出质量测试。
7. 从功能清单选择一个第二阶段需求，走完需求分析、开发、测试和复盘。

更完整的边界和依赖关系见[架构设计](架构设计.md)。
