# 社区问答系统后端

这是根目录教程的后端子项目。完整启动、接口和测试说明请阅读上一级 `README.md`。

本地开发：

```bash
uv sync --dev
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
uv run pytest
```

默认使用 SQLite；容器环境通过 `DATABASE_URL` 使用 MySQL。

当前写接口练习契约：

- 发布问题和回答可以携带 `Idempotency-Key`，原请求重试不会重复写入；
- `PATCH /api/v1/questions/{id}/status` 关闭或重新开放问题；
- `PUT /api/v1/questions/{id}/answers/{answer_id}/acceptance` 采纳或取消采纳回答；
- 所有示例只能使用公开或合成数据。
