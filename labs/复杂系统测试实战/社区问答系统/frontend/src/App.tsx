import { Link, NavLink, Route, Routes } from "react-router-dom";

import { CreateQuestionPage } from "./pages/CreateQuestionPage";
import { QuestionDetailPage } from "./pages/QuestionDetailPage";
import { QuestionListPage } from "./pages/QuestionListPage";

export default function App() {
  return (
    <div className="app-shell">
      <header className="topbar">
        <Link to="/" className="brand">
          <span className="brand-mark">Q</span>
          <span>测试学习社区</span>
        </Link>
        <nav aria-label="主导航">
          <NavLink to="/" end>
            发现问题
          </NavLink>
          <NavLink to="/questions/new">发布问题</NavLink>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<QuestionListPage />} />
          <Route path="/questions/new" element={<CreateQuestionPage />} />
          <Route path="/questions/:questionId" element={<QuestionDetailPage />} />
          <Route
            path="*"
            element={
              <section className="empty-state">
                <h1>页面不存在</h1>
                <Link className="primary-button" to="/">
                  返回首页
                </Link>
              </section>
            }
          />
        </Routes>
      </main>
      <footer>问题检索 · 内容发布 · 回答投票 · AI 辅助整理</footer>
    </div>
  );
}
