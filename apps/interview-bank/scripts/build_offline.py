#!/usr/bin/env python3
"""Package the generated question bank as a serverless single-file HTML app."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
BANK_ROOT = REPO_ROOT / "apps" / "interview-bank"
DATA_PATH = BANK_ROOT / "data" / "questions.json"
OUTPUT_PATH = BANK_ROOT / "offline" / "软件测试离线题库.html"

ORIGIN_LABELS = {
    "legacy-2025-reviewed": "2025 第一版",
    "reviewed-core": "后续整理：核心模块",
    "curated-2026": "后续整理：2026 公开趋势",
    "supplemental-reviewed": "后续整理：补充评审",
    "xiaolincoding-reviewed": "后续整理：公开资料重构",
}


def compact_payload() -> dict:
    payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    questions = payload.get("questions", [])
    groups = []
    for origin, label in ORIGIN_LABELS.items():
        groups.append(
            {
                "id": origin,
                "label": label,
                "count": sum(item.get("origin") == origin for item in questions),
            }
        )
    return {
        "generatedAt": payload.get("generated_at"),
        "questionCount": len(questions),
        "modules": payload.get("modules", []),
        "groups": groups,
        "questions": questions,
    }


def render(payload: dict) -> str:
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    data = data.replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <title>软件测试离线题库</title>
  <style>
    :root {{ color-scheme: light; font-family: "Microsoft YaHei", "PingFang SC", sans-serif; background: #f4f6f5; color: #17201c; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; min-width: 320px; }}
    button, input, select {{ font: inherit; letter-spacing: 0; }}
    button, select, input {{ min-height: 40px; border: 1px solid #bcc7c1; background: #fff; color: #17201c; }}
    button {{ cursor: pointer; padding: 0 14px; }}
    button:disabled {{ cursor: not-allowed; opacity: .45; }}
    button:focus-visible, input:focus-visible, select:focus-visible, summary:focus-visible {{ outline: 3px solid #ffbf47; outline-offset: 2px; }}
    header {{ background: #173f35; color: #fff; border-bottom: 4px solid #ffbf47; }}
    .header-inner {{ max-width: 1440px; margin: 0 auto; padding: 24px clamp(16px, 4vw, 48px); display: flex; align-items: end; justify-content: space-between; gap: 24px; }}
    h1 {{ margin: 0 0 6px; font-size: clamp(24px, 3vw, 34px); letter-spacing: 0; }}
    .subtitle {{ margin: 0; color: #d8e6df; line-height: 1.6; }}
    .total {{ flex: 0 0 auto; font-size: 14px; color: #173f35; background: #ffbf47; padding: 8px 12px; font-weight: 700; }}
    main {{ max-width: 1440px; margin: 0 auto; padding: 24px clamp(16px, 4vw, 48px) 56px; }}
    .controls {{ display: grid; grid-template-columns: minmax(260px, 2fr) repeat(2, minmax(180px, 1fr)); gap: 12px; margin-bottom: 18px; }}
    .field {{ display: grid; gap: 6px; font-size: 13px; font-weight: 700; }}
    input, select {{ width: 100%; padding: 0 12px; border-radius: 4px; }}
    .layout {{ display: grid; grid-template-columns: minmax(210px, 260px) minmax(0, 1fr); gap: 24px; align-items: start; }}
    aside {{ border-top: 3px solid #173f35; background: #fff; padding: 16px; position: sticky; top: 12px; }}
    aside h2 {{ font-size: 16px; margin: 0 0 12px; }}
    .source-list {{ display: grid; gap: 8px; }}
    .source-button {{ display: flex; justify-content: space-between; align-items: center; width: 100%; text-align: left; background: #fff; border-radius: 4px; }}
    .source-button.active {{ color: #fff; background: #173f35; border-color: #173f35; }}
    .source-count {{ font-variant-numeric: tabular-nums; }}
    .result-head {{ min-height: 44px; display: flex; justify-content: space-between; align-items: center; gap: 16px; border-bottom: 1px solid #cbd4cf; margin-bottom: 12px; }}
    .result-head p {{ margin: 0; }}
    .clear {{ border: 0; background: transparent; color: #9c2f22; min-height: 36px; }}
    .question-list {{ display: grid; gap: 12px; }}
    details {{ background: #fff; border: 1px solid #cbd4cf; border-radius: 6px; overflow: hidden; }}
    details[open] {{ border-color: #688176; }}
    summary {{ cursor: pointer; list-style: none; padding: 18px; }}
    summary::-webkit-details-marker {{ display: none; }}
    .meta {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }}
    .chip {{ font-size: 12px; color: #405149; background: #eef2f0; padding: 3px 7px; border-radius: 3px; }}
    .question-title {{ display: block; font-size: 17px; line-height: 1.55; font-weight: 700; }}
    .focus {{ display: block; color: #53635b; line-height: 1.6; margin-top: 6px; }}
    .answer {{ border-top: 1px solid #d8dfdb; padding: 18px; }}
    .answer h3 {{ font-size: 14px; margin: 18px 0 7px; color: #173f35; }}
    .answer h3:first-child {{ margin-top: 0; }}
    .prose {{ margin: 0; white-space: pre-wrap; line-height: 1.75; overflow-wrap: anywhere; }}
    .list {{ margin: 0; padding-left: 20px; line-height: 1.7; }}
    .bookmark {{ margin-top: 16px; border-radius: 4px; }}
    .bookmark.active {{ background: #ffbf47; border-color: #c78b00; }}
    .empty {{ background: #fff; border-left: 4px solid #9c2f22; padding: 24px; }}
    .pager {{ display: flex; justify-content: center; align-items: center; gap: 12px; margin-top: 20px; }}
    .pager button {{ border-radius: 4px; }}
    .footer-note {{ color: #5b6a63; text-align: center; margin: 28px 0 0; font-size: 13px; }}
    @media (max-width: 820px) {{
      .header-inner {{ align-items: start; flex-direction: column; }}
      .controls {{ grid-template-columns: 1fr; }}
      .layout {{ grid-template-columns: 1fr; }}
      aside {{ position: static; }}
      .source-list {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .source-button {{ min-height: 54px; padding: 8px; gap: 6px; }}
    }}
    @media (max-width: 480px) {{ .source-list {{ grid-template-columns: 1fr; }} .result-head {{ align-items: start; flex-direction: column; padding-bottom: 10px; }} }}
  </style>
</head>
<body>
  <header>
    <div class="header-inner">
      <div><h1>软件测试离线题库</h1><p class="subtitle">无需启动服务，按来源、模块和关键词复习完整答案。</p></div>
      <div class="total" id="total"></div>
    </div>
  </header>
  <main>
    <section class="controls" aria-label="题库筛选">
      <label class="field"><span>搜索题目、答案或标签</span><input id="query" type="search" placeholder="例如：回归测试、弱网、SQL"></label>
      <label class="field"><span>模块</span><select id="module"><option value="">全部模块</option></select></label>
      <label class="field"><span>学习状态</span><select id="bookmark"><option value="">全部题目</option><option value="saved">只看已收藏</option></select></label>
    </section>
    <div class="layout">
      <aside><h2>来源分组</h2><div class="source-list" id="sources"></div></aside>
      <section aria-live="polite">
        <div class="result-head"><p id="result"></p><button class="clear" id="clear" type="button">清空筛选</button></div>
        <div class="question-list" id="questions"></div>
        <nav class="pager" aria-label="分页"><button id="prev" type="button">上一页</button><span id="page"></span><button id="next" type="button">下一页</button></nav>
      </section>
    </div>
    <p class="footer-note">学习记录仅保存在当前浏览器。题目示例使用公开或合成场景，不代表个人真实经历。</p>
  </main>
  <script id="bank-data" type="application/json">{data}</script>
  <script>
    (() => {{
      const bank = JSON.parse(document.getElementById('bank-data').textContent);
      const labels = Object.fromEntries(bank.groups.map(group => [group.id, group.label]));
      const state = {{ query: '', module: '', origin: '', bookmark: '', page: 1, pageSize: 16 }};
      let savedValues = [];
      try {{ savedValues = JSON.parse(localStorage.getItem('software-testing-offline-saved') || '[]'); }} catch {{ savedValues = []; }}
      const saved = new Set(Array.isArray(savedValues) ? savedValues : []);
      const byId = id => document.getElementById(id);
      const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[char]));
      const match = question => {{
        if (state.origin && question.origin !== state.origin) return false;
        if (state.module && question.module_id !== state.module) return false;
        if (state.bookmark === 'saved' && !saved.has(question.id)) return false;
        const query = state.query.trim().toLowerCase();
        if (!query) return true;
        return [question.title, question.answer, question.explanation, ...(question.tags || [])].join(' ').toLowerCase().includes(query);
      }};
      const sourceButtons = () => {{
        const groups = [{{id:'',label:'全部来源',count:bank.questionCount}}, ...bank.groups];
        byId('sources').innerHTML = groups.map(group => `<button type="button" class="source-button ${{state.origin === group.id ? 'active' : ''}}" data-origin="${{escape(group.id)}}"><span>${{escape(group.label)}}</span><span class="source-count">${{group.count}}</span></button>`).join('');
        byId('sources').querySelectorAll('button').forEach(button => button.addEventListener('click', () => {{ state.origin = button.dataset.origin; state.page = 1; render(); }}));
      }};
      const questionHtml = question => {{
        const followups = (question.followups || []).map(item => `<li>${{escape(item)}}</li>`).join('');
        const pitfalls = (question.pitfalls || []).map(item => `<li>${{escape(item)}}</li>`).join('');
        return `<details><summary><span class="meta"><span class="chip">${{escape(labels[question.origin] || question.origin)}}</span><span class="chip">${{escape(question.module_name)}}</span><span class="chip">${{escape(question.level)}}</span><span class="chip">${{escape(question.kind)}}</span></span><span class="question-title">${{escape(question.title)}}</span><span class="focus">面试官在看：${{escape(question.focus)}}</span></summary><div class="answer"><h3>参考答案</h3><p class="prose">${{escape(question.answer)}}</p><h3>原理与实践解释</h3><p class="prose">${{escape(question.explanation)}}</p>${{followups ? `<h3>常见追问</h3><ul class="list">${{followups}}</ul>` : ''}}${{pitfalls ? `<h3>常见误区</h3><ul class="list">${{pitfalls}}</ul>` : ''}}<button type="button" class="bookmark ${{saved.has(question.id) ? 'active' : ''}}" data-id="${{escape(question.id)}}">${{saved.has(question.id) ? '取消收藏' : '收藏题目'}}</button></div></details>`;
      }};
      const render = () => {{
        sourceButtons();
        const filtered = bank.questions.filter(match);
        const pages = Math.max(1, Math.ceil(filtered.length / state.pageSize));
        state.page = Math.min(state.page, pages);
        const items = filtered.slice((state.page - 1) * state.pageSize, state.page * state.pageSize);
        byId('result').innerHTML = `找到 <strong>${{filtered.length}}</strong> 道题，当前显示 ${{items.length}} 道`;
        byId('questions').innerHTML = items.length ? items.map(questionHtml).join('') : '<div class="empty">没有符合当前条件的题目。</div>';
        byId('page').textContent = `第 ${{state.page}} / ${{pages}} 页`;
        byId('prev').disabled = state.page <= 1;
        byId('next').disabled = state.page >= pages;
        byId('questions').querySelectorAll('.bookmark').forEach(button => button.addEventListener('click', () => {{
          saved.has(button.dataset.id) ? saved.delete(button.dataset.id) : saved.add(button.dataset.id);
          try {{ localStorage.setItem('software-testing-offline-saved', JSON.stringify([...saved])); }} catch {{ /* 文件模式可能禁用持久化，筛选和阅读仍可使用。 */ }}
          render();
        }}));
      }};
      byId('total').textContent = `${{bank.questionCount}} 道完整题目`;
      bank.modules.forEach(module => byId('module').insertAdjacentHTML('beforeend', `<option value="${{escape(module.id)}}">${{escape(module.name)}}</option>`));
      byId('query').addEventListener('input', event => {{ state.query = event.target.value; state.page = 1; render(); }});
      byId('module').addEventListener('change', event => {{ state.module = event.target.value; state.page = 1; render(); }});
      byId('bookmark').addEventListener('change', event => {{ state.bookmark = event.target.value; state.page = 1; render(); }});
      byId('prev').addEventListener('click', () => {{ state.page -= 1; render(); scrollTo({{top: 0, behavior: 'smooth'}}); }});
      byId('next').addEventListener('click', () => {{ state.page += 1; render(); scrollTo({{top: 0, behavior: 'smooth'}}); }});
      byId('clear').addEventListener('click', () => {{ Object.assign(state, {{query:'',module:'',origin:'',bookmark:'',page:1}}); byId('query').value=''; byId('module').value=''; byId('bookmark').value=''; render(); }});
      render();
    }})();
  </script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = compact_payload()
    expected = render(payload)
    if args.check:
        if not OUTPUT_PATH.exists() or OUTPUT_PATH.read_text(encoding="utf-8") != expected:
            print(f"离线题库已过期：{OUTPUT_PATH.relative_to(REPO_ROOT)}", file=sys.stderr)
            return 1
    else:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(expected, encoding="utf-8")
    print(f"离线题库完成：{payload['questionCount']} 题，{len(payload['groups'])} 个来源分组")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
