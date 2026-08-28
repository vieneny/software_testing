import { FormEvent, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ApiError, communityApi } from "../api/client";
import type { AISummary, QuestionDetail } from "../types";

export function QuestionDetailPage() {
  const { questionId = "" } = useParams();
  const [question, setQuestion] = useState<QuestionDetail | null>(null);
  const [answer, setAnswer] = useState("");
  const [authorName, setAuthorName] = useState("学习者002");
  const [summary, setSummary] = useState<AISummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [busyAction, setBusyAction] = useState("");
  const [error, setError] = useState("");
  const answerIdempotency = useRef<{ fingerprint: string; key: string } | null>(null);
  const voterKey = useMemo(
    () => localStorage.getItem("synthetic-voter") ?? "synthetic-browser-user",
    [],
  );

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setQuestion(await communityApi.getQuestion(questionId));
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : "问题加载失败");
    } finally {
      setLoading(false);
    }
  }, [questionId]);

  useEffect(() => {
    void load();
  }, [load]);

  async function submitAnswer(event: FormEvent) {
    event.preventDefault();
    const input = {
      content: answer.trim(),
      author_name: authorName.trim(),
    };
    const fingerprint = JSON.stringify(input);
    if (answerIdempotency.current?.fingerprint !== fingerprint) {
      answerIdempotency.current = {
        fingerprint,
        key: crypto.randomUUID(),
      };
    }
    setBusyAction("answer");
    setError("");
    try {
      const saved = await communityApi.createAnswer(
        questionId,
        input,
        answerIdempotency.current.key,
      );
      setQuestion((current) =>
        current
          ? {
              ...current,
              answers: current.answers.some((item) => item.id === saved.id)
                ? current.answers
                : [...current.answers, saved],
            }
          : current,
      );
      setAnswer("");
      answerIdempotency.current = null;
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : "回答发布失败");
    } finally {
      setBusyAction("");
    }
  }

  async function vote(value: 1 | -1) {
    setBusyAction("vote");
    setError("");
    try {
      const result = await communityApi.vote(questionId, value, voterKey);
      setQuestion((current) => (current ? { ...current, score: result.score } : current));
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : "投票失败");
    } finally {
      setBusyAction("");
    }
  }

  async function summarize() {
    setBusyAction("ai");
    setError("");
    try {
      setSummary(await communityApi.summarize(questionId));
    } catch (reason) {
      setError(
        reason instanceof ApiError
          ? `${reason.message}。请确认 AI 中间件已启动。`
          : "AI 摘要生成失败",
      );
    } finally {
      setBusyAction("");
    }
  }

  async function updateStatus(status: "open" | "closed") {
    setBusyAction("status");
    setError("");
    try {
      setQuestion(await communityApi.updateStatus(questionId, status));
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : "问题状态更新失败");
    } finally {
      setBusyAction("");
    }
  }

  async function setAcceptance(answerId: string, accepted: boolean) {
    setBusyAction(`accept-${answerId}`);
    setError("");
    try {
      setQuestion(
        await communityApi.setAnswerAcceptance(questionId, answerId, accepted),
      );
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : "回答采纳状态更新失败");
    } finally {
      setBusyAction("");
    }
  }

  if (loading) return <p className="notice">正在加载问题详情……</p>;
  if (!question) {
    return (
      <section className="empty-state">
        <h1>{error || "问题不存在"}</h1>
        <Link className="primary-button" to="/">
          返回问题列表
        </Link>
      </section>
    );
  }

  return (
    <div className="detail-layout">
      <article className="content-card question-detail">
        <div className="detail-title">
          <div>
            <div className="tag-list">
              {question.tags.map((tag) => (
                <span className="tag" key={tag}>
                  {tag}
                </span>
              ))}
            </div>
            <h1>{question.title}</h1>
            <p className="muted">
              {question.author_name} · 浏览 {question.view_count} · 状态{" "}
              <span className={`status status-${question.status}`}>
                {question.status === "open" ? "开放回答" : "已关闭"}
              </span>
            </p>
            <button
              className="text-button status-action"
              disabled={Boolean(busyAction)}
              onClick={() =>
                void updateStatus(question.status === "open" ? "closed" : "open")
              }
            >
              {question.status === "open" ? "关闭问题" : "重新开放"}
            </button>
          </div>
          <div className="vote-box">
            <button
              aria-label="赞成"
              disabled={Boolean(busyAction)}
              onClick={() => void vote(1)}
            >
              ▲
            </button>
            <strong>{question.score}</strong>
            <button
              aria-label="反对"
              disabled={Boolean(busyAction)}
              onClick={() => void vote(-1)}
            >
              ▼
            </button>
          </div>
        </div>
        <div className="body-copy">{question.content}</div>
        {error && <div className="error-panel">{error}</div>}

        <div className="ai-panel">
          <div>
            <p className="eyebrow">AI ASSISTANT</p>
            <h2>问题摘要与风险提示</h2>
            <p>调用本地统一 AI 中间件，生成问题摘要与后续排查建议。</p>
          </div>
          <button disabled={Boolean(busyAction)} onClick={() => void summarize()}>
            {busyAction === "ai" ? "生成中……" : "生成 AI 摘要"}
          </button>
          {summary && (
            <div className="ai-result">
              <p>{summary.summary}</p>
              {summary.risk_hints.length > 0 && (
                <ul>
                  {summary.risk_hints.map((hint) => (
                    <li key={hint}>{hint}</li>
                  ))}
                </ul>
              )}
              <small>模型：{summary.model}</small>
            </div>
          )}
        </div>
      </article>

      <section className="content-card answers">
        <h2>{question.answers.length} 个回答</h2>
        {question.answers.length === 0 && <p className="muted">暂无回答，来贡献第一条吧。</p>}
        {question.answers.map((item) => (
          <article className={item.is_accepted ? "answer accepted-answer" : "answer"} key={item.id}>
            {item.is_accepted && <p className="accepted-label">✓ 已采纳回答</p>}
            <div className="body-copy">{item.content}</div>
            <div className="answer-meta">
              <p className="muted">由 {item.author_name} 回答</p>
              <button
                className="text-button"
                disabled={Boolean(busyAction)}
                onClick={() => void setAcceptance(item.id, !item.is_accepted)}
              >
                {item.is_accepted ? "取消采纳" : "采纳此回答"}
              </button>
            </div>
          </article>
        ))}
        {question.status === "open" ? (
          <form className="stacked-form answer-form" onSubmit={submitAnswer}>
            <h3>撰写回答</h3>
            <label>
              回答内容
              <textarea
                required
                minLength={5}
                maxLength={20000}
                rows={6}
                value={answer}
                onChange={(event) => setAnswer(event.target.value)}
                placeholder="提供可复现、可验证的公开学习方案……"
              />
              <small>{answer.length}/20000</small>
            </label>
            <label>
              合成昵称
              <input
                required
                minLength={2}
                maxLength={50}
                value={authorName}
                onChange={(event) => setAuthorName(event.target.value)}
              />
            </label>
            <button
              className="primary-button"
              disabled={Boolean(busyAction)}
              type="submit"
            >
              {busyAction === "answer" ? "提交中……" : "提交回答"}
            </button>
          </form>
        ) : (
          <div className="closed-notice">该问题已关闭。重新开放后才能提交新回答。</div>
        )}
      </section>
    </div>
  );
}
