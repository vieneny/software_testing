# 软件测试离线面试题库

这是仓库唯一的面试题浏览方式。无需安装依赖或启动服务，直接打开：

```text
apps/interview-bank/offline/软件测试离线题库.html
```

题库包含 470 道详解题：

| 来源 | 数量 |
|---|---:|
| 个人整理最新版 | 160 |
| 10 个核心专题 | 172 |
| 2026 公开趋势重构 | 24 |
| 补充评审 | 52 |
| 公开测试资料重构 | 62 |

离线页面支持关键词、模块、来源、收藏和每页 `8/16/32/64` 条。收藏与每页条数保存在当前浏览器。

## 1. 目录结构

```text
apps/interview-bank/
├── README.md
├── pyproject.toml
├── data/
│   ├── questions.json
│   ├── personal-latest-reviewed.json
│   └── 其他来源与审计数据
├── offline/
│   └── 软件测试离线题库.html
├── scripts/
│   ├── build_personal_latest.py
│   ├── build_bank.py
│   ├── audit_question_quality.py
│   └── build_offline.py
└── tests/
```

`docs/08-求职备考/04-面试题库/` 保存便于版本评审的 Markdown 专题；`data/questions.json` 是统一生成结果；离线 HTML 将统一数据打包进单文件。

## 2. 普通学习者

1. 双击离线 HTML；
2. 按目标岗位选择模块；
3. 先脱稿回答，再展开答题思路与详解；
4. 收藏不会的题；
5. 回到对应学习阶段完成实验；
6. 再次限时回答并记录追问。

不需要运行 `uvicorn`、`npm`、数据库或开发服务器。

## 3. 维护者重新生成

从仓库根目录依次执行：

```powershell
python apps\interview-bank\scripts\build_personal_latest.py --check
python apps\interview-bank\scripts\build_bank.py --check
python apps\interview-bank\scripts\audit_question_quality.py
python apps\interview-bank\scripts\build_offline.py --check
python -m pytest apps\interview-bank\tests -q
```

修改真源后，去掉相应 `--check` 生成新结果，再重复完整检查：

```powershell
python apps\interview-bank\scripts\build_personal_latest.py
python apps\interview-bank\scripts\build_bank.py
python apps\interview-bank\scripts\audit_question_quality.py --write-report
python apps\interview-bank\scripts\build_offline.py
```

生成顺序不能颠倒：个人题库校验 → 聚合 470 题 → 逐题质量审计 → 单文件离线页面。

## 4. 内容边界

- 题目 Markdown 和评审 JSON 是内容真源；
- `questions.json`、审计报告和离线 HTML 是生成产物；
- 不直接编辑生成后的 HTML 修题；
- 新题先映射学习阶段，再决定是否进入题库；
- 整理学习项目不会自动修改面试题或答案；
- 每次内容变化都必须重新生成并比较题数、ID 和数据哈希。

## 5. 完成检查

- [ ] `questions.json` 恰好 470 道且 ID 唯一；
- [ ] 个人整理最新版 160 道全部有答题思路和详细答案；
- [ ] 每道题的模块、难度、类型、来源和日期有效；
- [ ] 场景/项目/行为/实操题具有可回答的场景；
- [ ] 离线 HTML 内嵌 470 道题并可直接打开；
- [ ] 搜索、来源、模块、收藏和分页无需服务；
- [ ] 所有生成器 `--check` 和离线测试通过。
