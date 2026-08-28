<script setup lang="ts">
import { computed, onBeforeUnmount, reactive, ref } from 'vue'
import {
  createInterview,
  fetchInterview,
  fetchQuestions,
  finishInterviewSession,
  saveInterviewAnswer,
} from '../api'
import type {
  InterviewAnswer,
  InterviewRequest,
  InterviewSession,
  ProgressRecord,
  Question,
} from '../types'
import SafeMarkdown from './SafeMarkdown.vue'

const emit = defineEmits<{
  updateProgress: [progress: ProgressRecord]
}>()

type Stage = 'setup' | 'running' | 'report'

const stage = ref<Stage>('setup')
const setupError = ref('')
const fallbackMessage = ref('')
const answerError = ref('')
const creating = ref(false)
const revealing = ref(false)
const savingAnswer = ref(false)
const session = ref<InterviewSession | null>(null)
const currentIndex = ref(0)
const elapsedSeconds = ref(0)
const answers = ref<InterviewAnswer[]>([])
const request = reactive<InterviewRequest>({
  role: '测试开发工程师',
  difficulty: '综合',
  count: 10,
  seed: Math.floor(Date.now() / 1000) % 100000,
})
let timerId: number | undefined

const currentQuestion = computed(() => session.value?.questions[currentIndex.value])
const currentAnswer = computed(() => answers.value[currentIndex.value])
const completion = computed(() => {
  const total = session.value?.questions.length ?? 0
  return total ? Math.round(((currentIndex.value + 1) / total) * 100) : 0
})
const formattedTime = computed(() => {
  const minutes = Math.floor(elapsedSeconds.value / 60)
  const seconds = elapsedSeconds.value % 60
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
})
const averageScore = computed(() => {
  const scored = answers.value.filter((answer) => answer.score > 0)
  if (!scored.length) return 0
  return scored.reduce((sum, answer) => sum + answer.score, 0) / scored.length
})
const weakAnswers = computed(() =>
  answers.value
    .map((answer, index) => ({ answer, question: session.value?.questions[index] }))
    .filter((item) => item.answer.score > 0 && item.answer.score <= 2 && item.question),
)
const coveredModules = computed(() =>
  Array.from(new Set(session.value?.questions.map((question) => question.moduleName) ?? [])),
)

function seededShuffle(items: Question[], seed: number): Question[] {
  const shuffled = [...items]
  let state = seed || 1
  const random = () => {
    state = (state * 9301 + 49297) % 233280
    return state / 233280
  }
  for (let index = shuffled.length - 1; index > 0; index -= 1) {
    const swapIndex = Math.floor(random() * (index + 1))
    ;[shuffled[index], shuffled[swapIndex]] = [shuffled[swapIndex], shuffled[index]]
  }
  return shuffled
}

function primaryQuestionRole(targetRole: string): string {
  const roleMap: Record<string, string> = {
    软件测试工程师: '软件测试',
    自动化测试工程师: '自动化测试',
    测试开发工程师: '测试开发',
    'AI 测试工程师': 'AI测试',
    性能测试工程师: '性能测试',
  }
  return roleMap[targetRole] ?? ''
}

function beginTimer() {
  window.clearInterval(timerId)
  elapsedSeconds.value = 0
  timerId = window.setInterval(() => {
    elapsedSeconds.value += 1
  }, 1000)
}

async function localFallback(): Promise<Question[]> {
  const page = await fetchQuestions({
    query: '',
    module: '',
    level: request.difficulty === '综合' ? '' : request.difficulty,
    kind: '',
    origin: '',
    role: primaryQuestionRole(request.role),
    page: 1,
    pageSize: Math.min(100, Math.max(request.count * 4, 40)),
  })
  if (page.total < request.count) {
    throw new Error(
      `当前岗位与难度组合只有 ${page.total} 道题，少于请求的 ${request.count} 道；请降低题数或调整难度。`,
    )
  }
  return seededShuffle(page.items, request.seed).slice(0, request.count)
}

async function startInterview() {
  creating.value = true
  setupError.value = ''
  fallbackMessage.value = ''
  let nextSession: InterviewSession | null = null

  try {
    nextSession = await createInterview({ ...request })
    if (!nextSession.questions.length) throw new Error('服务端没有返回可用题目。')
  } catch (error) {
    try {
      const questions = await localFallback()
      if (!questions.length) throw new Error('当前题库没有可用于组卷的题目。')
      nextSession = {
        id: `local-${Date.now()}`,
        questions,
        role: request.role,
        difficulty: request.difficulty,
        seed: request.seed,
      }
      const reason = error instanceof Error ? error.message : '服务端组卷失败'
      fallbackMessage.value = `${reason} 已使用当前题库按相同种子在浏览器内组卷。`
    } catch (fallbackError) {
      setupError.value =
        fallbackError instanceof Error
          ? fallbackError.message
          : '无法创建模拟面试，请检查 FastAPI 服务和题库数据。'
    }
  }

  if (nextSession) {
    session.value = nextSession
    currentIndex.value = 0
    answers.value = nextSession.questions.map((question) => ({
      questionId: question.id,
      answer: '',
      score: 0,
      revealed: false,
    }))
    stage.value = 'running'
    beginTimer()
  }
  creating.value = false
}

async function revealAnswer() {
  if (!currentAnswer.value || !session.value) return
  answerError.value = ''
  if (session.value.id.startsWith('local-')) {
    currentAnswer.value.revealed = true
    return
  }
  revealing.value = true
  try {
    const revealed = await fetchInterview(session.value.id, true)
    const byId = new Map(revealed.questions.map((question) => [question.id, question]))
    session.value.questions = session.value.questions.map(
      (question) => byId.get(question.id) ?? question,
    )
    currentAnswer.value.revealed = true
  } catch (error) {
    answerError.value =
      error instanceof Error ? error.message : '参考答案读取失败，请稍后重试。'
  } finally {
    revealing.value = false
  }
}

async function rate(score: number) {
  const answer = currentAnswer.value
  const question = currentQuestion.value
  if (!answer || !question || !session.value) return
  answer.score = score
  answerError.value = ''
  emit('updateProgress', {
    questionId: question.id,
    favorite: false,
    wrong: score <= 2,
    mastery: score >= 4 ? 'mastered' : 'learning',
    note: answer.answer.trim(),
    selfScore: score,
  })
  if (!session.value.id.startsWith('local-')) {
    savingAnswer.value = true
    try {
      await saveInterviewAnswer(
        session.value.id,
        question.id,
        answer.answer.trim(),
        score,
      )
    } catch (error) {
      answerError.value =
        error instanceof Error
          ? `${error.message} 自评已保存在学习进度中，可继续作答。`
          : '会话答案同步失败，自评已保存在学习进度中。'
    } finally {
      savingAnswer.value = false
    }
  }
}

function nextQuestion() {
  if (!session.value) return
  if (currentIndex.value >= session.value.questions.length - 1) {
    void finishInterview('completed')
    return
  }
  currentIndex.value += 1
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function finishInterview(status: 'completed' | 'abandoned' = 'completed') {
  window.clearInterval(timerId)
  if (session.value && !session.value.id.startsWith('local-')) {
    try {
      await finishInterviewSession(session.value.id, status)
    } catch (error) {
      fallbackMessage.value =
        error instanceof Error ? `${error.message} 本地复盘报告仍可查看。` : '会话结束状态同步失败。'
    }
  }
  stage.value = 'report'
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function resetInterview() {
  window.clearInterval(timerId)
  stage.value = 'setup'
  session.value = null
  answers.value = []
  currentIndex.value = 0
  elapsedSeconds.value = 0
  fallbackMessage.value = ''
}

onBeforeUnmount(() => window.clearInterval(timerId))
</script>

<template>
  <section aria-labelledby="interview-title">
    <div class="page-heading">
      <div>
        <p class="kicker">限时作答 · 结构复盘</p>
        <h1 id="interview-title">真实流程模拟面试</h1>
        <p>随机种子让同一套题可以复盘重做。先完整口述，再看答案；评分衡量表达质量，不只看关键词数量。</p>
      </div>
      <div class="interview-principle">
        <span>建议结构</span>
        <strong>结论 → 方法 → 证据 → 风险</strong>
      </div>
    </div>

    <div v-if="stage === 'setup'" class="setup-grid">
      <form class="interview-setup card-surface" @submit.prevent="startInterview">
        <div class="section-heading">
          <span class="step-mark">01</span>
          <div>
            <h2>生成一场面试</h2>
            <p>选择目标岗位、难度和题量，生成一套可重复练习的面试题组。</p>
          </div>
        </div>
        <div class="setup-fields">
          <label>
            <span>目标岗位</span>
            <select v-model="request.role">
              <option>软件测试工程师</option>
              <option>自动化测试工程师</option>
              <option>测试开发工程师</option>
              <option>AI 测试工程师</option>
              <option>性能测试工程师</option>
            </select>
          </label>
          <label>
            <span>难度</span>
            <select v-model="request.difficulty">
              <option>入门</option>
              <option>进阶</option>
              <option>高级</option>
              <option>综合</option>
            </select>
          </label>
          <label>
            <span>题目数量</span>
            <input v-model.number="request.count" type="number" min="3" max="30" />
          </label>
          <label>
            <span>随机种子</span>
            <input v-model.number="request.seed" type="number" min="1" />
            <small>记录这个数字，就能重现同一套题。</small>
          </label>
        </div>
        <div v-if="setupError" class="notice notice--error" role="alert">
          <div>
            <strong>组卷失败</strong>
            <p>{{ setupError }}</p>
          </div>
        </div>
        <button class="button button--primary button--large" type="submit" :disabled="creating">
          {{ creating ? '正在组卷…' : '开始模拟面试' }}
        </button>
      </form>

      <aside class="process-card card-surface" aria-labelledby="process-title">
        <p class="kicker">完整面试节奏</p>
        <h2 id="process-title">不是背答案，是训练沟通</h2>
        <ol class="process-list">
          <li><span>1</span><div><strong>读题澄清</strong><p>先确认范围、用户与约束。</p></div></li>
          <li><span>2</span><div><strong>限时口述</strong><p>基础题约 2 分钟，场景题约 5 分钟。</p></div></li>
          <li><span>3</span><div><strong>揭示答案</strong><p>对照方法、证据和遗漏风险。</p></div></li>
          <li><span>4</span><div><strong>诚实自评</strong><p>1–5 分并自动沉淀错题。</p></div></li>
          <li><span>5</span><div><strong>面后复盘</strong><p>只补最薄弱的 1–2 个知识链。</p></div></li>
        </ol>
      </aside>
    </div>

    <template v-else-if="stage === 'running' && session && currentQuestion && currentAnswer">
      <div v-if="fallbackMessage" class="notice notice--warning" role="status">
        <div>
          <strong>当前为本地组卷</strong>
          <p>{{ fallbackMessage }}</p>
        </div>
      </div>

      <div class="interview-status" aria-label="面试进度">
        <div>
          <span>进度</span>
          <strong>{{ currentIndex + 1 }} / {{ session.questions.length }}</strong>
        </div>
        <div class="status-progress" aria-hidden="true">
          <span :style="{ width: `${completion}%` }"></span>
        </div>
        <div>
          <span>计时</span>
          <strong class="timer">{{ formattedTime }}</strong>
        </div>
        <button
          class="text-button text-button--danger"
          type="button"
          @click="finishInterview('abandoned')"
        >
          提前结束
        </button>
      </div>

      <article class="interview-question card-surface" :aria-labelledby="`mock-${currentQuestion.id}`">
        <div class="eyebrow-row">
          <span class="chip chip--module">{{ currentQuestion.moduleName }}</span>
          <span class="chip">{{ currentQuestion.level }}</span>
          <span class="chip">{{ currentQuestion.kind }}</span>
        </div>
        <h2 :id="`mock-${currentQuestion.id}`">{{ currentQuestion.title }}</h2>
        <p v-if="currentQuestion.scenario" class="scenario-prompt">{{ currentQuestion.scenario }}</p>
        <div v-if="currentQuestion.focus" class="interviewer-note">
          <strong>面试官提示</strong>
          <p>{{ currentQuestion.focus }}</p>
        </div>

        <label class="spoken-answer">
          <span>记录你的口述提纲</span>
          <textarea
            v-model="currentAnswer.answer"
            rows="8"
            placeholder="建议只记关键词：结论、步骤、证据指标、风险与复盘。"
          />
        </label>

        <div v-if="!currentAnswer.revealed" class="reveal-panel">
          <p>口述完成后再揭示答案，训练效果更接近真实面试。</p>
          <button
            class="button button--primary"
            type="button"
            :disabled="revealing"
            @click="revealAnswer"
          >
            {{ revealing ? '正在读取参考…' : '我答完了，查看参考' }}
          </button>
        </div>

        <div v-if="answerError" class="notice notice--warning" role="status">
          <div>
            <strong>会话同步提示</strong>
            <p>{{ answerError }}</p>
          </div>
        </div>

        <div v-if="currentAnswer.revealed" class="mock-reference" data-testid="mock-reference">
          <section>
            <h3>参考答案</h3>
            <SafeMarkdown
              :content="currentQuestion.answer || '本题暂无参考答案，请标记后补充。'"
            />
          </section>
          <details v-if="currentQuestion.explanation" open>
            <summary>解释与落地</summary>
            <SafeMarkdown :content="currentQuestion.explanation" />
          </details>
          <details v-if="currentQuestion.followups.length">
            <summary>继续追问（{{ currentQuestion.followups.length }}）</summary>
            <ul class="clean-list">
              <li v-for="item in currentQuestion.followups" :key="item">{{ item }}</li>
            </ul>
          </details>

          <div class="rating-panel">
            <div>
              <strong>这次回答几分？</strong>
              <p>1 分几乎不会；3 分结构基本完整；5 分能给出可信证据并处理追问。</p>
            </div>
            <div class="score-buttons" role="group" aria-label="为当前回答评分">
              <button
                v-for="score in 5"
                :key="score"
                class="score-button"
                :class="{ 'is-active': currentAnswer.score === score }"
                type="button"
                :aria-pressed="currentAnswer.score === score"
                :disabled="savingAnswer"
                @click="rate(score)"
              >
                {{ score }}
              </button>
            </div>
          </div>
        </div>

        <footer class="mock-actions">
          <span v-if="currentAnswer.revealed && !currentAnswer.score">评分后会自动加入学习进度</span>
          <span v-else-if="currentAnswer.score">已评分 {{ currentAnswer.score }} / 5</span>
          <button
            class="button button--primary"
            type="button"
            :disabled="!currentAnswer.revealed || !currentAnswer.score"
            @click="nextQuestion"
          >
            {{ currentIndex === session.questions.length - 1 ? '完成并看报告' : '下一题' }}
          </button>
        </footer>
      </article>
    </template>

    <div v-else-if="stage === 'report' && session" class="report-stack">
      <section class="report-hero">
        <p class="kicker">面试复盘报告</p>
        <h2>{{ averageScore >= 4 ? '表达已成体系，继续打磨证据。' : averageScore >= 3 ? '基础不错，重点补齐薄弱链路。' : '先别追求题量，优先练稳答题结构。' }}</h2>
        <div class="report-metrics">
          <div><strong>{{ averageScore.toFixed(1) }}</strong><span>平均分 / 5</span></div>
          <div><strong>{{ formattedTime }}</strong><span>总用时</span></div>
          <div><strong>{{ answers.filter((item) => item.score > 0).length }}</strong><span>已完成题</span></div>
          <div><strong>{{ weakAnswers.length }}</strong><span>需重点复盘</span></div>
        </div>
      </section>

      <div class="report-grid">
        <section class="card-surface">
          <h3>模块覆盖</h3>
          <div class="tag-row">
            <span v-for="module in coveredModules" :key="module" class="tag">{{ module }}</span>
          </div>
          <p class="report-advice">
            下一轮建议只选一个薄弱模块，使用同一随机种子重做，比较回答是否从“术语罗列”进步到“方法与证据闭环”。
          </p>
        </section>
        <section class="card-surface">
          <h3>优先复盘清单</h3>
          <ol v-if="weakAnswers.length" class="review-list">
            <li v-for="item in weakAnswers" :key="item.answer.questionId">
              <span>{{ item.answer.score }} 分</span>
              <strong>{{ item.question?.title }}</strong>
            </li>
          </ol>
          <p v-else>没有 1–2 分题目。可以继续检查 3 分题是否缺少量化证据或风险边界。</p>
        </section>
      </div>

      <button class="button button--primary button--large" type="button" @click="resetInterview">
        再进行一场
      </button>
    </div>
  </section>
</template>
