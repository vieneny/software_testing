export interface Answer {
  id: string;
  question_id: string;
  content: string;
  author_name: string;
  score: number;
  is_accepted: boolean;
  created_at: string;
}

export interface QuestionSummary {
  id: string;
  title: string;
  excerpt: string;
  author_name: string;
  tags: string[];
  status: string;
  score: number;
  view_count: number;
  answer_count: number;
  created_at: string;
  updated_at: string;
}

export interface QuestionDetail extends Omit<QuestionSummary, "excerpt" | "answer_count"> {
  content: string;
  answers: Answer[];
}

export interface QuestionPage {
  items: QuestionSummary[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface QuestionInput {
  title: string;
  content: string;
  author_name: string;
  tags: string[];
}

export interface AISummary {
  question_id: string;
  summary: string;
  risk_hints: string[];
  model: string;
}

export interface ApiErrorBody {
  error?: {
    code?: string;
    message?: string;
    request_id?: string;
    trace_id?: string;
  };
}
