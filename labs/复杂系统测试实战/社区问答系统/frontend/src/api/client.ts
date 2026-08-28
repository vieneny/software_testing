import type {
  AISummary,
  ApiErrorBody,
  Answer,
  QuestionDetail,
  QuestionInput,
  QuestionPage,
} from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly code: string,
    public readonly requestId?: string,
  ) {
    super(message);
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as ApiErrorBody;
    throw new ApiError(
      body.error?.message ?? `请求失败（HTTP ${response.status}）`,
      response.status,
      body.error?.code ?? "unknown_error",
      body.error?.request_id ?? body.error?.trace_id,
    );
  }
  return (await response.json()) as T;
}

export const communityApi = {
  listQuestions(
    params: { page?: number; keyword?: string; tag?: string } = {},
    signal?: AbortSignal,
  ) {
    const query = new URLSearchParams({
      page: String(params.page ?? 1),
      page_size: "10",
    });
    if (params.keyword) query.set("keyword", params.keyword);
    if (params.tag) query.set("tag", params.tag);
    return request<QuestionPage>(`/questions?${query}`, { signal });
  },

  getQuestion(id: string) {
    return request<QuestionDetail>(`/questions/${encodeURIComponent(id)}`);
  },

  createQuestion(input: QuestionInput, idempotencyKey: string) {
    return request<QuestionDetail>("/questions", {
      method: "POST",
      headers: { "Idempotency-Key": idempotencyKey },
      body: JSON.stringify(input),
    });
  },

  createAnswer(
    questionId: string,
    input: { content: string; author_name: string },
    idempotencyKey: string,
  ) {
    return request<Answer>(
      `/questions/${encodeURIComponent(questionId)}/answers`,
      {
        method: "POST",
        headers: { "Idempotency-Key": idempotencyKey },
        body: JSON.stringify(input),
      },
    );
  },

  vote(questionId: string, value: 1 | -1, voterKey: string) {
    return request<{ question_id: string; score: number }>(
      `/questions/${encodeURIComponent(questionId)}/votes`,
      {
        method: "POST",
        body: JSON.stringify({ voter_key: voterKey, value }),
      },
    );
  },

  updateStatus(questionId: string, status: "open" | "closed") {
    return request<QuestionDetail>(
      `/questions/${encodeURIComponent(questionId)}/status`,
      {
        method: "PATCH",
        body: JSON.stringify({ status }),
      },
    );
  },

  setAnswerAcceptance(questionId: string, answerId: string, accepted: boolean) {
    return request<QuestionDetail>(
      `/questions/${encodeURIComponent(questionId)}/answers/${encodeURIComponent(answerId)}/acceptance`,
      {
        method: "PUT",
        body: JSON.stringify({ accepted }),
      },
    );
  },

  summarize(questionId: string) {
    return request<AISummary>(
      `/questions/${encodeURIComponent(questionId)}/ai-summary`,
      {
        method: "POST",
      },
    );
  },
};
