# AI 应用开发全栈学习

这是一块独立、连续的课程学习区。课程笔记按源目录原样保留在 [`260108Java智能体同步班`](260108Java智能体同步班/) 下，不拆分到 Java、接口、微服务或其他阶段，便于按课程顺序离线学习和复盘。

在线查看： [GitHub 课程目录](https://github.com/vieneny/software_testing/tree/master/docs/09-AI%E5%BA%94%E7%94%A8%E5%BC%80%E5%8F%91%E5%85%A8%E6%A0%88%E5%AD%A6%E4%B9%A0/260108Java%E6%99%BA%E8%83%BD%E4%BD%93%E5%90%8C%E6%AD%A5%E7%8F%AD) · [Gitee 课程目录](https://gitee.com/a251376784/software_testing/tree/master/docs/09-AI%E5%BA%94%E7%94%A8%E5%BC%80%E5%8F%91%E5%85%A8%E6%A0%88%E5%AD%A6%E4%B9%A0/260108Java%E6%99%BA%E8%83%BD%E4%BD%93%E5%90%8C%E6%AD%A5%E7%8F%AD)

## 学习目标

完成前三个课程模块后，能够：

- 使用 Java 完成面向对象、集合、异常、IO、多线程和常用 API 编程；
- 使用 MySQL、JDBC、连接池和事务完成持久化开发；
- 使用 Maven、Spring、Spring Boot、MyBatis、Vue 基础构建单体 Web 应用；
- 理解 Linux、Git、Docker、Redis、Nginx、RabbitMQ 和 Spring Cloud 在应用交付中的位置；
- 以尚品甄选为案例，串起商品、购物车、订单、支付、鉴权、缓存和消息等业务链路；
- 为后续 Spring AI、RAG、Tool Calling、Agent 和 AI 测试学习建立可运行的后端基础。

## 课程结构

| 顺序 | 源课程模块 | 主要内容 | 建议产出 |
|---:|---|---|---|
| 1 | `01-尚硅谷Java智能体技术之Java&AI基础` | JavaSE、面向对象、Maven/JUnit、异常、IO、多线程、集合、MySQL、JDBC、反射 | Java 基础练习、SQL 查询、JDBC 小程序 |
| 2 | `02-尚硅谷Java智能体技术之JavaWEB和单体架构` | Maven、Spring MVC、Spring/MyBatis/Spring Boot、Vue3、Linux、Redis、Git、Docker、Spring Cloud、Nginx、RabbitMQ | 单体 Web 服务、接口文档、容器化运行记录 |
| 3 | `03-尚硅谷Java智能体技术之尚品甄选项目` | 项目搭建、商品详情、购物车、订单、支付、环境准备 | 一份业务链路图、接口测试清单和项目复盘 |

> 源目录前三个模块没有 `day02` 的尚品甄选资料，本仓库不自行补造编号。后续课程模块可继续按相同方式追加到 `260108Java智能体同步班/`，保持原始相对路径。

## 推荐学习顺序

```text
Java 基础与面向对象
  -> 数据库与 JDBC
  -> Maven / Spring / Spring Boot / MyBatis
  -> Vue 与 HTTP 接口
  -> Linux / Git / Docker / Redis / 消息队列
  -> 尚品甄选业务链路
  -> Spring AI / RAG / Agent 实战
```

每节笔记建议完成以下闭环：

1. 先通读标题和示例，写出自己的三到五条要点；
2. 在本地新建最小练习，至少修改一次示例代码；
3. 主动制造一个可解释的失败，例如参数校验失败、事务回滚或缓存未命中；
4. 记录运行命令、现象、定位依据和修复结果；
5. 用阶段产出验收，而不是只以“看完笔记”为完成标准。

## 离线阅读与资料边界

- `260108Java智能体同步班/` 中 98 篇 Markdown 笔记可直接在本地编辑器或 Git 平台阅读，不需要启动服务、数据库或前端项目。
- 源笔记引用了大量课堂配图。本次只导入 Markdown 正文，不批量复制课程图片、视频、压缩包、安装包、IDE 配置或数据库备份；本地图片标记已转换为文字占位，代码、概念和步骤可完整离线阅读。
- 课程原始资料仍保留在本机源目录，仓库只维护可审阅、可离线阅读的笔记版本。

## 与其他阶段的关系

本模块是独立的“开发基础与项目课程”主线：

- 与 `docs/01` 至 `docs/07` 的测试学习并列，不把课程章节拆成测试阶段；
- 学习过程中需要测试时，引用已有测试阶段的方法和工具，但课程笔记仍集中在本目录；
- 完成这里的 Java/Web 基础后，再进入 [`测试转人工智能开发`](../10-测试转人工智能开发/README.md)，学习 Spring AI、RAG、Agent、评测、安全和部署；
- 面试题只在 `docs/08-求职备考` 和离线题库中维护，不依赖服务启动。

## 课程资料索引

按源目录进入对应模块：

- [完整课程大纲](课程大纲.md)
- [01 Java 与 AI 基础](260108Java智能体同步班/01-尚硅谷Java智能体技术之Java&AI基础/)
- [02 JavaWEB 和单体架构](260108Java智能体同步班/02-尚硅谷Java智能体技术之JavaWEB和单体架构/)
- [03 尚品甄选项目](260108Java智能体同步班/03-尚硅谷Java智能体技术之尚品甄选项目/)
- [完整笔记清单](课程笔记索引.md)
