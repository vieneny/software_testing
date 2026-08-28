import { FormEvent, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { ApiError, communityApi } from "../api/client";

export function CreateQuestionPage() {
  const navigate = useNavigate();
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [authorName, setAuthorName] = useState("学习者001");
  const [tags, setTags] = useState("fastapi,测试");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const idempotency = useRef<{ fingerprint: string; key: string } | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    const normalizedTags = Array.from(
      new Set(
        tags
          .split(",")
          .map((item) => item.trim().toLowerCase())
          .filter(Boolean),
      ),
    );
    if (normalizedTags.length > 5) {
      setError("标签最多 5 个，请删除多余标签后再发布。");
      return;
    }
    if (normalizedTags.some((item) => item.length > 30)) {
      setError("每个标签最多 30 个字符。");
      return;
    }
    const input = {
      title: title.trim(),
      content: content.trim(),
      author_name: authorName.trim(),
      tags: normalizedTags,
    };
    const fingerprint = JSON.stringify(input);
    if (idempotency.current?.fingerprint !== fingerprint) {
      idempotency.current = {
        fingerprint,
        key: crypto.randomUUID(),
      };
    }

    setSubmitting(true);
    try {
      const question = await communityApi.createQuestion(input, idempotency.current.key);
      navigate(`/questions/${question.id}`);
    } catch (reason) {
      setError(
        reason instanceof ApiError
          ? `${reason.message}${reason.requestId ? `（请求编号：${reason.requestId}）` : ""}`
          : "发布失败，请稍后重试",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="form-card narrow">
      <div className="section-heading">
        <div>
          <p className="eyebrow">CREATE</p>
          <h1>发布问题</h1>
          <p>清晰描述问题现象、复现条件、期望结果和已经尝试的方法。</p>
        </div>
      </div>
      {error && <div className="error-panel">{error}</div>}
      <form className="stacked-form" onSubmit={submit}>
        <label>
          标题
          <input
            required
            minLength={5}
            maxLength={200}
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="例如：如何验证订单接口的幂等性？"
          />
          <small>{title.length}/200</small>
        </label>
        <label>
          详细描述
          <textarea
            required
            minLength={10}
            maxLength={20000}
            rows={10}
            value={content}
            onChange={(event) => setContent(event.target.value)}
            placeholder="说明场景、已尝试的方法、预期结果和实际结果……"
          />
        </label>
        <div className="two-columns">
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
          <label>
            标签（逗号分隔，最多 5 个）
            <input
              value={tags}
              onChange={(event) => setTags(event.target.value)}
              placeholder="例如：fastapi,接口测试"
            />
          </label>
        </div>
        <div className="form-actions">
          <Link className="text-button" to="/">
            取消
          </Link>
          <button className="primary-button" disabled={submitting} type="submit">
            {submitting ? "发布中……" : "确认发布"}
          </button>
        </div>
      </form>
    </section>
  );
}
