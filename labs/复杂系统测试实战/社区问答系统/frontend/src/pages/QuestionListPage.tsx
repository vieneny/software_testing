import { FormEvent, useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { ApiError, communityApi } from "../api/client";
import type { QuestionPage } from "../types";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("zh-CN", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export function QuestionListPage() {
  const [data, setData] = useState<QuestionPage | null>(null);
  const [keyword, setKeyword] = useState("");
  const [activeKeyword, setActiveKeyword] = useState("");
  const [activeTag, setActiveTag] = useState("");
  const [page, setPage] = useState(1);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setData(
        await communityApi.listQuestions({
          page,
          keyword: activeKeyword,
          tag: activeTag,
        }),
      );
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : "问题列表加载失败");
    } finally {
      setLoading(false);
    }
  }, [activeKeyword, activeTag, page]);

  useEffect(() => {
    void load();
  }, [load]);

  function search(event: FormEvent) {
    event.preventDefault();
    setPage(1);
    setActiveKeyword(keyword.trim());
  }

  return (
    <>
      <section className="hero">
        <div>
          <p className="eyebrow">完整问答流程 · 可验证测试实践</p>
          <h1>把每个疑问，变成可验证的知识</h1>
          <p>练习搜索、分页、发布、回答、投票和 AI 摘要的完整测试链路。</p>
        </div>
        <Link className="primary-button" to="/questions/new">
          发布一个问题
        </Link>
      </section>

      <section className="content-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">QUESTIONS</p>
            <h2>
              {activeKeyword
                ? `“${activeKeyword}”的搜索结果`
                : activeTag
                  ? `标签：${activeTag}`
                  : "最新问题"}
            </h2>
            {activeTag && (
              <button
                className="text-button clear-filter"
                type="button"
                onClick={() => {
                  setActiveTag("");
                  setPage(1);
                }}
              >
                清除标签筛选
              </button>
            )}
          </div>
          <form className="search" onSubmit={search}>
            <label className="sr-only" htmlFor="keyword">
              搜索问题
            </label>
            <input
              id="keyword"
              value={keyword}
              onChange={(event) => setKeyword(event.target.value)}
              placeholder="搜索标题或正文"
            />
            <button type="submit">搜索</button>
          </form>
        </div>

        {loading && <p className="notice">正在加载问题……</p>}
        {error && (
          <div className="error-panel" role="alert">
            <p>{error}</p>
            <button onClick={() => void load()}>重试</button>
          </div>
        )}
        {!loading && !error && data?.items.length === 0 && (
          <div className="empty-state">
            <h3>还没有匹配的问题</h3>
            <p>试试其他关键词，或创建第一条练习问题。</p>
          </div>
        )}
        <div className="question-list">
          {data?.items.map((question) => (
            <article className="question-row" key={question.id}>
              <div className="metrics" aria-label="问题统计">
                <span>
                  <strong>{question.score}</strong> 得票
                </span>
                <span>
                  <strong>{question.answer_count}</strong> 回答
                </span>
                <span>
                  <strong>{question.view_count}</strong> 浏览
                </span>
              </div>
              <div className="question-copy">
                <Link to={`/questions/${question.id}`}>
                  <h3>{question.title}</h3>
                </Link>
                <p>{question.excerpt}</p>
                <div className="meta-line">
                  <div className="tag-list">
                    {question.tags.map((tag) => (
                      <button
                        className="tag tag-button"
                        key={tag}
                        type="button"
                        aria-pressed={activeTag === tag}
                        onClick={() => {
                          setActiveTag(tag);
                          setPage(1);
                        }}
                      >
                        {tag}
                      </button>
                    ))}
                  </div>
                  <span>
                    {question.author_name} · {formatDate(question.created_at)}
                  </span>
                </div>
              </div>
            </article>
          ))}
        </div>

        {(data?.total_pages ?? 0) > 1 && (
          <div className="pagination">
            <button disabled={page <= 1} onClick={() => setPage((value) => value - 1)}>
              上一页
            </button>
            <span>
              第 {page} / {data?.total_pages} 页
            </span>
            <button
              disabled={page >= (data?.total_pages ?? 1)}
              onClick={() => setPage((value) => value + 1)}
            >
              下一页
            </button>
          </div>
        )}
      </section>
    </>
  );
}
