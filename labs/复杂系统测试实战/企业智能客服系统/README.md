# 企业智能客服系统

这是一套面向软件测试学习的完整业务骨架，不是只展示几个 CRUD 接口的玩具项目。它以企业客服常见的“客户咨询 → 建立会话 → 公开回复/内部备注 → 升级工单 → 分诊和分配 → 处理 → 解决/重开/关闭”为主链路，并把独立 Python AI 中间件作为可替换的辅助能力。

## 1. 能学到什么

- Java 21、Spring Boot 3.5.16、Spring MVC、JPA、Bean Validation 和统一异常处理。
- MySQL 数据持久化、Redis 扩展入口、H2 快速测试环境。
- Vue 3.5 + TypeScript + Vite 8 的后台工作台开发。
- 多租户数据边界、乐观锁、工单状态机、SLA 截止时间和坐席分配审计。
- 会话消息顺序、客户可见与内部备注隔离、会话状态机和写请求幂等。
- Java 调用 Python AI 服务、超时、断路器、请求追踪和明确降级。
- 接口测试、UI 自动化、性能测试、安全测试、AI 输出评测和故障演练。

## 2. 技术栈

| 层次 | 技术 | 学习用途 |
|---|---|---|
| 前端 | Vue 3.5.40、TypeScript 5.9、Vite 8.1、Nginx | 工单看板、表单、状态操作、AI 建议面板 |
| Java 后端 | Java 21、Spring Boot 3.5.16、JPA、Validation、Actuator | 核心业务、状态机、租户隔离、审计 |
| AI 中间件 | 相邻目录 `../人工智能中间件` 的 FastAPI 服务 | 统一模型调用、Mock、知识库检索和输出评测 |
| 数据 | MySQL 8.4、Redis 7.4；开发/测试默认 H2 | 持久化、缓存/限流扩展、隔离测试 |
| 稳定性 | Resilience4j、HTTP 超时、降级响应 | 验证 AI 非核心依赖故障时的韧性 |
| 交付 | Docker、Docker Compose、Nginx | 环境一致性和全链路练习 |

Vite 8 要求 Node.js 20.19+ 或 22.12+。后端必须使用 JDK 21；JDK 8/11 无法编译本项目。

## 3. 目录

```text
企业智能客服系统/
├── backend/                      # Spring Boot 后端与 JUnit 测试
├── frontend/                     # Vue 工单工作台
├── docker-compose.yml            # MySQL、Redis、AI、后端、前端
├── .env.example                  # 无敏感信息的本地变量模板
├── 系统架构.md
└── 功能与测试清单.md
```

## 4. 快速启动

### 4.1 一条命令启动全链路

确认相邻的 `../人工智能中间件` 已存在：

```bash
cp .env.example .env
docker compose up --build
```

打开：

- 前端工作台：`http://localhost:5173`
- Java 健康检查：`http://localhost:8080/api/health`
- Actuator：`http://localhost:8080/actuator/health`
- Swagger UI：`http://localhost:8080/swagger-ui.html`
- AI 中间件：`http://localhost:8091`

这里把 AI 的宿主机端口设为 `8091`，是为了能够与社区系统占用的后端端口
`8000` 同时运行；容器网络中的 Java 后端仍调用 `http://ai-middleware:8000`。
Java 后端的启动依赖中刻意没有 AI 和尚未接入业务的 Redis：即使 AI 启动失败，工单
主链路也必须启动，调用建议接口时再通过超时、断路器和降级响应处理故障。

清理容器但保留数据：`docker compose down`。连同本项目学习数据库一起清理：`docker compose down -v`。

### 4.2 不安装 MySQL，使用 H2 启动后端

```bash
cd backend
mvn spring-boot:run
```

默认使用内存 H2，并自动注入两个合成客户、两张合成工单和两篇公开学习知识。AI 服务不启动也不会影响工单创建和流转；请求 AI 建议时会得到 `degraded=true` 的人工处理提示。

### 4.3 本地启动前端

```bash
cd frontend
npm install
npm run dev
```

Vite 会把 `/api` 和 `/actuator` 代理到 `http://localhost:8080`。

## 5. 已实现接口

除健康检查外，业务接口统一位于 `/api/v1`，并默认使用请求头
`X-Tenant-Code: demo`。真实项目应由认证令牌解析租户，不能信任前端自由填写的租户头。

| 方法 | 路径 | 用途 |
|---|---|---|
| GET | `/api/health` | 轻量存活检查 |
| GET | `/actuator/health` | Spring 依赖健康检查 |
| GET | `/api/v1/customers` | 查询当前租户的合成客户 |
| GET | `/api/v1/conversations?state=OPEN&page=0&size=20` | 分页查询当前租户会话 |
| POST | `/api/v1/conversations` | 创建会话及首条客户消息，支持幂等键 |
| GET | `/api/v1/conversations/{conversationId}` | 会话详情；默认不返回内部备注 |
| POST | `/api/v1/conversations/{conversationId}/messages` | 客户消息、坐席公开回复或内部备注 |
| POST | `/api/v1/conversations/{conversationId}/transitions` | 关闭或重新打开会话 |
| GET | `/api/v1/tickets?status=NEW&page=0&size=20` | 分页查询工单 |
| POST | `/api/v1/tickets` | 创建工单并计算 SLA，可关联会话并支持幂等键 |
| GET | `/api/v1/tickets/{ticketId}` | 工单详情、版本和状态历史 |
| POST | `/api/v1/tickets/{ticketId}/transitions` | 按状态机和期望版本流转 |
| POST | `/api/v1/tickets/{ticketId}/assignments` | 按期望版本分配/转派坐席并留痕 |
| POST | `/api/v1/tickets/{ticketId}/ai-suggestions` | 调用 Python AI 中间件 |

所有 HTTP 响应都包含 `X-Request-ID`。客户端传入的值只有完全符合
`[A-Za-z0-9._:-]{1,128}` 才会被采用；缺失、超长或包含其他字符时由后端生成 UUID，
防止任意头值被原样回显。错误体中的 `request_id`、响应头以及发往 Python 的
`X-Request-ID` 使用同一个 canonical 值。

创建工单示例：

```json
{
  "customerId": 1,
  "title": "合成数据：无法查看模拟账单",
  "description": "用于接口测试的公开合成场景。",
  "category": "BILLING",
  "priority": "HIGH"
}
```

状态流转请求：

```json
{
  "expectedVersion": 0,
  "targetStatus": "TRIAGED",
  "operatorName": "学习坐席",
  "note": "已完成演示分诊"
}
```

坐席分配同样必须携带详情响应中的当前 `version`：

```json
{
  "expectedVersion": 1,
  "assignedAgent": "演示坐席甲",
  "operatorName": "学习管理员",
  "reason": "演示手动分配"
}
```

`expectedVersion` 缺失返回 400；与数据库当前版本不一致返回 HTTP 409 和
`CONCURRENT_MODIFICATION`。成功变更会在事务内显式 flush，响应中的 `version`
已经是递增后的新版本，客户端应保存新值用于下一次更新。
若工单已经分配给目标坐席，即使 `expectedVersion` 正确也会返回 409
`BUSINESS_RULE_VIOLATION`；重复请求不会新增分配审计，也不会改变工单版本。

### 5.1 会话、消息与内部备注

创建会话：

```json
{
  "customerId": 1,
  "channel": "WEB",
  "subject": "合成场景：演示账号无法登录",
  "initialMessage": "这是纯合成的客户消息。"
}
```

`channel` 支持 `WEB/APP/EMAIL/PHONE/WECHAT`。创建会话、发送消息、改变会话状态
以及创建工单都可以携带：

```http
Idempotency-Key: learning-conversation-001
```

合法键只能包含 `A-Z a-z 0-9 . _ : -`，长度 1～128。同一租户、同一操作中，同键
同内容会返回首次资源且不重复写入；同键不同内容返回
`409 IDEMPOTENCY_KEY_REUSED`。幂等记录与业务数据在同一事务提交。

发送坐席公开回复：

```json
{
  "expectedVersion": 1,
  "senderType": "AGENT",
  "visibility": "CUSTOMER",
  "authorName": "学习坐席",
  "content": "您好，请先核对合成演示账号状态。"
}
```

内部备注只需要把 `visibility` 改为 `INTERNAL`。默认详情
`GET /api/v1/conversations/{id}` 只返回 `CUSTOMER` 可见消息；只有显式传入
`includeInternal=true` 才返回内部备注。客户消息不能标记成内部备注，外部请求也不能
伪造 `SYSTEM` 消息。发送消息与关闭/重开会话的 `POST` 接口同样默认
`includeInternal=false`；坐席工作台需要查看内部备注时会显式传入 `true`。

消息写入和关闭/重开会话必须提交详情中的 `expectedVersion`。服务端在会话行上加锁，
再验证版本并分配单调递增的消息序号；过期版本返回
`409 CONCURRENT_MODIFICATION`。公开客户消息把状态变为 `WAITING_AGENT`，坐席公开
回复变为 `WAITING_CUSTOMER`，内部备注不改变业务状态。关闭会话会生成一条仅内部可见
的系统审计消息，关闭后必须先重新打开才能继续发送。

创建工单时可增加 `"conversationId": 1`。服务端会验证会话和客户属于当前租户且
互相匹配；会话详情的 `linkedTicketIds` 会返回关联的公开工单编号。

统一错误体示例：

```json
{
  "timestamp": "2026-07-27T12:00:00Z",
  "status": 409,
  "code": "CONCURRENT_MODIFICATION",
  "message": "工单已被其他坐席更新，请刷新后重试",
  "request_id": "7c9bf681-b473-47a6-8c5f-7cc6baf69a56",
  "fieldErrors": {}
}
```

## 6. 工单状态机

```text
NEW ──> TRIAGED ──> IN_PROGRESS ──> RESOLVED ──> CLOSED
 │          │              │             │
 └──────────┘              └─> WAITING_CUSTOMER
                         REOPENED <───────┘（从 RESOLVED 重开）
```

实际允许关系以 `TicketService.ALLOWED_TRANSITIONS` 为准。未解决工单不能直接关闭；
非法跳转返回 HTTP 409 和错误码 `BUSINESS_RULE_VIOLATION`。版本过期返回
`CONCURRENT_MODIFICATION`，适合做模型测试、状态迁移测试和真实的并发覆盖测试。

## 7. Java 与 Python AI 的完整契约

默认调用：

```text
POST ${AI_BASE_URL}${AI_SUGGESTION_PATH}
默认路径：/api/v1/customer-service/suggest
Content-Type: application/json
X-Request-ID: 透传上游值；上游未提供时由 Java 生成 UUID
连接超时：2s；读取超时：20s（均可通过环境变量覆盖）
```

一次客服建议会依次执行分类、回复、摘要、内容安全和知识检索等最多 5 个操作。按每个
操作 1.5 秒、最多 2 次尝试估算，极端串行预算约为 `5 × 1.5s × 2 = 15s`；
默认 `AI_READ_TIMEOUT=20s` 为 HTTP、序列化和调度留出余量。学习者仍可通过
`AI_CONNECT_TIMEOUT`、`AI_READ_TIMEOUT` 环境变量覆盖，进行超时和故障注入练习。

请求体：

```json
{
  "tenant_code": "demo",
  "ticket_id": "TK-DEMO00001",
  "title": "多次输入正确演示密码仍无法登录",
  "description": "这是纯合成学习数据。",
  "category": "ACCOUNT",
  "priority": "HIGH",
  "customer_level": "VIP",
  "tone": "professional",
  "language": "zh-CN",
  "knowledge_context": [
    {
      "title": "账号登录故障排查",
      "category": "ACCOUNT",
      "content": "先核对账号状态，再建议重置演示密码。"
    }
  ]
}
```

正常响应：

```json
{
  "summary": "用户遇到登录问题",
  "suggested_reply": "您好，请先尝试重置演示密码。",
  "suggested_category": "ACCOUNT",
  "suggested_priority": "HIGH",
  "confidence": 0.87,
  "risk_flags": [],
  "knowledge_references": ["账号登录故障排查"],
  "suggested_actions": ["核对账号状态", "检查认证服务状态"],
  "must_verify": ["不得索取真实密码或验证码", "人工确认事实后再发送"],
  "degraded": false,
  "degradation_reason": null,
  "api_version": "v1",
  "request_id": "customer-service-demo-001",
  "model": "mock/deterministic-rules@2026.07"
}
```

Java 响应 DTO 会忽略未来新增的元数据字段，避免中间件做向后兼容扩展时破坏调用方，
但不会盲目信任 2xx。消费者会校验非空摘要和建议回复、分类枚举
`ACCOUNT/BILLING/TECHNICAL/SECURITY/PRODUCT/OTHER`、优先级枚举、置信度
`0..1`，以及全部结构化列表：

- `risk_flags`、`knowledge_references`、`suggested_actions`、`must_verify` 都必须存在。
- 每个列表最多 20 项；每一项必须非空。动作和核验项单项最多 500 字符。
- `must_verify` 至少包含一项，确保任何 AI 建议都有明确的人工确认门槛。

关联元数据同样属于必需契约：

- `api_version` 必须严格等于 `v1`。
- `request_id` 必须符合 `[A-Za-z0-9._:-]{1,128}`，并与 Java 本次出站的 canonical
  `X-Request-ID` 完全一致。
- `model` 必须是非空、无控制字符且不超过 200 字符的模型标识。

`{}`、缺字段、错误版本、下游返回其他关联 ID、未知枚举、越界置信度或非法列表都会
被丢弃并转换为确定性降级结果。

连接超时、读取超时、5xx、空响应、契约非法或断路器打开时，接口仍返回 HTTP 200，
但包含：

```json
{
  "confidence": 0,
  "riskFlags": ["AI_UNAVAILABLE"],
  "suggestedActions": ["转交人工坐席核实工单事实、客户诉求和下一步处理方式"],
  "mustVerify": ["人工确认客户身份、问题事实和回复内容后再发送"],
  "degraded": true,
  "degradationReason": "AI_MIDDLEWARE_UNAVAILABLE:ResourceAccessException"
}
```

契约非法时错误类别类似
`AI_RESPONSE_CONTRACT_INVALID:CATEGORY_INVALID`、
`AI_RESPONSE_CONTRACT_INVALID:API_VERSION_UNSUPPORTED` 或
`AI_RESPONSE_CONTRACT_INVALID:REQUEST_ID_MISMATCH`；Python 主动报告降级时统一为
`AI_MIDDLEWARE_REPORTED_DEGRADED`。`degradationReason` 只返回稳定错误类别，
不回显异常消息、响应正文、服务 URL、实际版本、实际关联 ID、模型值或调用栈，避免
把内网地址和上游响应片段暴露给前端。降级只表示“没有可靠 AI 建议”，不得被当成
业务成功建议；工单创建、分配和状态流转完全不依赖 AI。

API 会把 `suggestedActions` 和 `mustVerify` 返回给工作台，分别展示为“建议动作”和
醒目的“必须核验”。首版 `ai_suggestion_records` 只保存建议回复、置信度、是否降级和
稳定降级原因等核心审计字段；动作与核验列表暂不做历史持久化，后续应以版本化 JSON
或子表保存，不能误认为页面上的临时结果已经进入审计库。

## 8. 自动化验证

后端：

```bash
cd backend
mvn test
```

测试覆盖健康接口、`/api/v1` 合成客户、会话创建/消息/可见性/状态/幂等/多租户、
会话升级工单、工单创建/详情/状态流转、非法流转、
`expectedVersion` 必填、旧版本拒绝、flush 后版本递增；MockWebServer 覆盖 AI 路径、
`{}` 与逐字段非法契约、合法 `TECHNICAL/SECURITY` 分类，以及 canonical
`X-Request-ID` 从响应头贯穿到 Python 请求并由响应原样关联；同时覆盖缺失元数据、
错误 API 版本、错误下游关联 ID、动作/核验列表缺失、超量、空项与超长项。

前端：

```bash
cd frontend
npm install
npm run typecheck
npm run test
npm run build
```

建议继续加入 Playwright：创建会话、内部备注隔离、会话升级工单、筛选、分配坐席、
合法/非法状态流转、AI 正常和 AI 降级等主链路。

## 9. 参考开源项目

本骨架仅参考公开项目的架构思想，代码为本学习项目重新实现：

- [Spring Petclinic](https://github.com/spring-projects/spring-petclinic)：Spring Boot 分层、测试和可运行样例。
- [Chatwoot](https://github.com/chatwoot/chatwoot)：全渠道客服、会话和坐席工作台领域设计。
- [Zammad](https://github.com/zammad/zammad)：工单、组织、权限和通知模型。
- [Rasa](https://github.com/RasaHQ/rasa)：对话式 AI 与业务动作分离。
- [Resilience4j](https://github.com/resilience4j/resilience4j)：超时、断路和弹性设计。

注意各项目许可证不同；学习架构不等于可以直接复制代码或商用。

## 10. 当前边界与持续完善

当前版本优先建立可测试的主干，以下能力应在后续迭代加入：

1. Spring Security、OIDC、RBAC、坐席技能组和租户由令牌解析。
2. Flyway 版本化迁移，生产环境将 `ddl-auto` 改为 `validate`。
3. Redis 缓存、幂等键、分布式限流和会话在线状态。
4. WebSocket 实时消息、邮件/短信等异步通知、事务 Outbox。
5. 知识库向量检索、引用可追溯、提示词版本与 AI 评测数据集。
6. OpenTelemetry、Prometheus、Grafana、结构化日志和统一 Trace ID。
7. Playwright、REST Assured、Pact、k6、OWASP ZAP 和故障注入实战。

这些限制被显式保留为学习路线，不应在未完成安全和数据治理前把本项目直接用于真实生产。
