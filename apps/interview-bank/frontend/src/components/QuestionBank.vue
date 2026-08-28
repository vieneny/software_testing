<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { fetchLegacyCoverage, fetchMeta, fetchQuestions } from '../api'
import type {
  LegacyCoverageSummary,
  Meta,
  ProgressRecord,
  Question,
  QuestionFilters,
} from '../types'
import QuestionCard from './QuestionCard.vue'

const props = defineProps<{
  progressRecords: Map<string, ProgressRecord>
}>()

const emit = defineEmits<{
  updateProgress: [progress: ProgressRecord]
}>()

const defaultMeta: Meta = {
  questionCount: 0,
  moduleCount: 0,
  modules: [],
  levels: ['入门', '进阶', '高级'],
  kinds: ['知识题', '场景题', '项目题', '行为题', '实操题'],
  origins: [
    'legacy-2025-reviewed',
    'reviewed-core',
    'curated-2026',
    'supplemental-reviewed',
    'xiaolincoding-reviewed',
  ],
  roles: [
    '软件测试',
    '功能测试',
    '接口测试',
    '自动化测试',
    '接口自动化',
    'Web自动化',
    '移动端测试',
    '移动端自动化',
    '性能测试',
    '稳定性测试',
    '测试开发',
    '质量工程',
    'AI测试',
    '大模型评测',
  ],
  lastUpdated: '',
}

const meta = ref<Meta>(defaultMeta)
const legacyCoverage = ref<LegacyCoverageSummary | null>(null)
const questions = ref<Question[]>([])
const total = ref(0)
const loading = ref(true)
const errorMessage = ref('')
const favoriteOnly = ref(false)
const wrongOnly = ref(false)
const filters = reactive<QuestionFilters>({
  query: '',
  module: '',
  level: '',
  kind: '',
  origin: '',
  role: '',
  page: 1,
  pageSize: 12,
})
let loadRequestId = 0
const progressOverrides = new Map<string, ProgressRecord>()

const displayedQuestions = computed(() => questions.value)

const pageCount = computed(() => Math.max(1, Math.ceil(total.value / filters.pageSize)))
const activeFilterCount = computed(
  () =>
    [
      filters.query,
      filters.module,
      filters.level,
      filters.kind,
      filters.origin,
      filters.role,
    ].filter(Boolean).length +
    Number(favoriteOnly.value) +
    Number(wrongOnly.value),
)

function originLabel(origin: string): string {
  const labels: Record<string, string> = {
    'legacy-2025-reviewed': '2025 第一版（已复核）',
    'reviewed-core': '核心模块评审题',
    'curated-2026': '2026 公开趋势重构题',
    'supplemental-reviewed': '补充评审题',
    'xiaolincoding-reviewed': '小林 Coding 资料原创重构题',
  }
  return labels[origin] ?? origin
}

function getProgress(questionId: string): ProgressRecord {
  return (
    progressOverrides.get(questionId) ??
    props.progressRecords.get(questionId) ?? {
      questionId,
      favorite: false,
      wrong: false,
      mastery: 'unseen',
      note: '',
    }
  )
}

function progressFilterQuestionIds(): string[] {
  const ids = new Set([
    ...props.progressRecords.keys(),
    ...progressOverrides.keys(),
  ])
  return Array.from(ids).filter((questionId) => {
    const progress = getProgress(questionId)
    if (favoriteOnly.value && !progress.favorite) return false
    if (wrongOnly.value && !progress.wrong) return false
    return true
  })
}

async function loadQuestions() {
  const requestId = ++loadRequestId
  const requestFilters: QuestionFilters = { ...filters }
  loading.value = true
  errorMessage.value = ''
  try {
    if (favoriteOnly.value || wrongOnly.value) {
      requestFilters.questionIds = progressFilterQuestionIds()
      if (!requestFilters.questionIds.length) {
        questions.value = []
        total.value = 0
        return
      }
    }
    const page = await fetchQuestions(requestFilters)
    if (requestId !== loadRequestId) return
    questions.value = page.items
    total.value = page.total
  } catch (error) {
    if (requestId !== loadRequestId) return
    questions.value = []
    total.value = 0
    errorMessage.value =
      error instanceof Error
        ? error.message
        : '题库加载失败，请确认 FastAPI 服务已启动并刷新页面。'
  } finally {
    if (requestId === loadRequestId) loading.value = false
  }
}

async function loadMeta() {
  const [metaResult, coverageResult] = await Promise.allSettled([
    fetchMeta(),
    fetchLegacyCoverage(),
  ])
  meta.value = metaResult.status === 'fulfilled' ? metaResult.value : defaultMeta
  legacyCoverage.value =
    coverageResult.status === 'fulfilled' ? coverageResult.value : null
}

function applyFilters() {
  filters.page = 1
  void loadQuestions()
}

function resetFilters() {
  Object.assign(filters, {
    query: '',
    module: '',
    level: '',
    kind: '',
    origin: '',
    role: '',
    page: 1,
    pageSize: 12,
  })
  favoriteOnly.value = false
  wrongOnly.value = false
  void loadQuestions()
}

function changePage(page: number) {
  filters.page = Math.min(Math.max(page, 1), pageCount.value)
  void loadQuestions()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function toggleProgressFilter(kind: 'favorite' | 'wrong') {
  if (kind === 'favorite') favoriteOnly.value = !favoriteOnly.value
  if (kind === 'wrong') wrongOnly.value = !wrongOnly.value
  filters.page = 1
  void loadQuestions()
}

async function handleProgressUpdate(progress: ProgressRecord) {
  progressOverrides.set(progress.questionId, progress)
  emit('updateProgress', progress)
  const noLongerMatches =
    (favoriteOnly.value && !progress.favorite) ||
    (wrongOnly.value && !progress.wrong)
  if (!noLongerMatches) return
  questions.value = questions.value.filter(
    (question) => question.id !== progress.questionId,
  )
  total.value = Math.max(0, total.value - 1)
  const remainingPageCount = Math.max(
    1,
    Math.ceil(total.value / filters.pageSize),
  )
  if (filters.page > remainingPageCount) filters.page = remainingPageCount
  await nextTick()
  void loadQuestions()
}

watch(
  () => filters.pageSize,
  () => {
    filters.page = 1
    void loadQuestions()
  },
)

onMounted(() => {
  void Promise.all([loadMeta(), loadQuestions()])
})
</script>

<template>
  <section aria-labelledby="bank-title">
    <div class="page-heading">
      <div>
        <p class="kicker">按模块学习 · 用证据回答</p>
        <h1 id="bank-title">面试题库</h1>
        <p>
          按模块、岗位能力和难度筛选题目，先口述，再对照答案、解释和追问完成复盘。
        </p>
      </div>
      <div class="stat-strip" aria-label="题库概览">
        <div>
          <strong>{{ meta.questionCount || total }}</strong>
          <span>道题目</span>
        </div>
        <div>
          <strong>{{ meta.moduleCount || meta.modules.length }}</strong>
          <span>个模块</span>
        </div>
        <div>
          <strong>{{ progressRecords.size }}</strong>
          <span>条学习记录</span>
        </div>
      </div>
    </div>

    <div v-if="legacyCoverage" class="history-banner" aria-label="历史资料迁移情况">
      <div>
        <span class="history-banner__mark">迁移</span>
        <p>
          <strong>历史资料已逐题解析，匹配结论从严计算</strong>
          {{ legacyCoverage.mappedToAnswer }} / {{ legacyCoverage.total }} 条题目意图通过强语义匹配，
          {{ legacyCoverage.unmapped }} 条保留候选并等待人工复核；{{ legacyCoverage.isolatedAnswers }} 条旧答案未纳入现行题库。
        </p>
      </div>
      <span>只有强语义匹配的历史题关键词会进入现行题搜索</span>
    </div>

    <form class="filter-panel" role="search" @submit.prevent="applyFilters">
      <label class="search-field">
        <span>搜索题目、答案或标签</span>
        <div class="search-field__control">
          <input
            v-model="filters.query"
            type="search"
            placeholder="例如：Playwright、慢 SQL、RAG 评测"
          />
        </div>
      </label>
      <label>
        <span>模块</span>
        <select v-model="filters.module">
          <option value="">全部模块</option>
          <option v-for="module in meta.modules" :key="module.id" :value="module.id">
            {{ module.name }}{{ module.count ? `（${module.count}）` : '' }}
          </option>
        </select>
      </label>
      <label>
        <span>岗位能力</span>
        <select v-model="filters.role">
          <option value="">全部岗位能力</option>
          <option v-for="role in meta.roles" :key="role" :value="role">{{ role }}</option>
        </select>
      </label>
      <label>
        <span>难度</span>
        <select v-model="filters.level">
          <option value="">全部难度</option>
          <option v-for="level in meta.levels" :key="level" :value="level">{{ level }}</option>
        </select>
      </label>
      <label>
        <span>题型</span>
        <select v-model="filters.kind">
          <option value="">全部题型</option>
          <option v-for="kind in meta.kinds" :key="kind" :value="kind">{{ kind }}</option>
        </select>
      </label>
      <label>
        <span>来源</span>
        <select v-model="filters.origin">
          <option value="">全部来源</option>
          <option v-for="origin in meta.origins" :key="origin" :value="origin">
            {{ originLabel(origin) }}
          </option>
        </select>
      </label>
      <div class="filter-panel__actions">
        <button class="button button--primary" type="submit">应用筛选</button>
        <button v-if="activeFilterCount" class="text-button" type="button" @click="resetFilters">
          清空 {{ activeFilterCount }} 项条件
        </button>
      </div>
    </form>

    <div class="bank-toolbar">
      <p aria-live="polite">
        <template v-if="loading">正在整理题目…</template>
        <template v-else>共找到 <strong>{{ total }}</strong> 道，当前显示 {{ displayedQuestions.length }} 道</template>
      </p>
      <div class="toolbar-group">
        <button
          class="toggle-button"
          :class="{ 'is-active': favoriteOnly }"
          type="button"
          :aria-pressed="favoriteOnly"
          @click="toggleProgressFilter('favorite')"
        >
          只看收藏
        </button>
        <button
          class="toggle-button"
          :class="{ 'is-active': wrongOnly }"
          type="button"
          :aria-pressed="wrongOnly"
          @click="toggleProgressFilter('wrong')"
        >
          只看错题
        </button>
        <label class="inline-select">
          <span class="sr-only">每页题数</span>
          <select v-model.number="filters.pageSize">
            <option :value="8">每页 8 题</option>
            <option :value="12">每页 12 题</option>
            <option :value="20">每页 20 题</option>
          </select>
        </label>
      </div>
    </div>

    <div v-if="errorMessage" class="notice notice--error" role="alert">
      <div>
        <strong>暂时无法读取题库</strong>
        <p>{{ errorMessage }}</p>
      </div>
      <button class="button button--secondary" type="button" @click="loadQuestions">重新连接</button>
    </div>

    <div v-else-if="loading" class="skeleton-list" aria-hidden="true">
      <div v-for="index in 3" :key="index" class="skeleton-card"></div>
    </div>

    <div v-else-if="displayedQuestions.length" class="question-list">
      <QuestionCard
        v-for="question in displayedQuestions"
        :key="question.id"
        :question="question"
        :progress="getProgress(question.id)"
        @update="handleProgressUpdate"
      />
    </div>

    <div v-else class="empty-state">
      <h2>没有符合条件的题目</h2>
      <p>试试减少筛选条件，或清空“只看收藏 / 错题”。</p>
      <button class="button button--secondary" type="button" @click="resetFilters">重置筛选</button>
    </div>

    <nav v-if="!loading && !errorMessage && pageCount > 1" class="pagination" aria-label="题库分页">
      <button
        class="button button--secondary button--compact"
        type="button"
        :disabled="filters.page <= 1"
        @click="changePage(filters.page - 1)"
      >
        上一页
      </button>
      <span>第 {{ filters.page }} / {{ pageCount }} 页</span>
      <button
        class="button button--secondary button--compact"
        type="button"
        :disabled="filters.page >= pageCount"
        @click="changePage(filters.page + 1)"
      >
        下一页
      </button>
    </nav>
  </section>
</template>
