# 个人整理最新版题库资料

本目录保留个人整理最新版的 160 道软件测试面试题大纲：

- [个人整理最新版题库.md](./个人整理最新版题库.md)：按主题分组的完整题目清单。

每道题均已补充独立答题思路、详细答案、原理解释、追问和常见误区，并进入单文件离线题库。机器可读的评审数据位于：

```text
apps/interview-bank/data/personal-latest-reviewed.json
```

## 覆盖校验

构建器会解析大纲中的 160 个编号项，并逐题核对当前详解题。每条记录都有稳定 ID、原文件定位、题意、当前详解题 ID、匹配状态和复核标记。机器可读结果位于：

```text
apps/interview-bank/data/legacy-coverage.json
```

当前 160 道题已全部通过强语义匹配并关联详细答案。大纲只用于覆盖校验，`personal-latest-reviewed.json` 是答案与答题思路的唯一来源。

## 维护方式

1. 修改题目或答案时先更新 `personal-latest-reviewed.json`；
2. 大纲题意发生变化时同步更新 `个人整理最新版题库.md`；
3. 运行 `python apps/interview-bank/scripts/build_personal_latest.py --check` 校验 160 道题的字段、长度和对应关系；
4. 运行 `python apps/interview-bank/scripts/build_bank.py --check` 校验统一题库与覆盖结果。
