<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { fetchLegacyCoverage, fetchSources } from '../api'
import type { LegacyCoverageSummary, Source } from '../types'
import SourceSnapshotViewer from './SourceSnapshotViewer.vue'
import XiaolinCoverage from './XiaolinCoverage.vue'

const staticSources: Source[] = [
  {
    id: 'istqb',
    snapshotId: 'istqb',
    name: 'ISTQB 测试知识体系',
    url: 'https://www.istqb.org/certifications/certified-tester-foundation-level',
    kind: '国际知识体系',
    accessedAt: '',
    summary: '用于校验测试基础、测试设计与质量活动的概念边界。',
  },
  {
    id: 'owasp-wstg',
    snapshotId: 'owasp-wstg',
    name: 'OWASP Web Security Testing Guide',
    url: 'https://owasp.org/www-project-web-security-testing-guide/',
    kind: '官方开源指南',
    accessedAt: '',
    summary: '用于 Web 与接口安全测试的检查维度和实践方法。',
  },
  {
    id: 'playwright',
    snapshotId: 'playwright',
    name: 'Playwright 官方文档',
    url: 'https://playwright.dev/docs/intro',
    kind: '官方工具文档',
    accessedAt: '',
    summary: '用于 UI 自动化定位、等待、隔离和工程化实践。',
  },
  {
    id: 'appium',
    snapshotId: 'appium',
    name: 'Appium 官方文档',
    url: 'https://appium.io/docs/en/latest/',
    kind: '官方工具文档',
    accessedAt: '',
    summary: '用于 Android 与 iOS 移动端自动化的跨平台实践。',
  },
  {
    id: 'nist-ai-rmf',
    snapshotId: 'nist-ai-rmf',
    name: 'NIST AI Risk Management Framework',
    url: 'https://www.nist.gov/itl/ai-risk-management-framework',
    kind: 'AI 风险框架',
    accessedAt: '',
    summary: '用于 AI 系统可信、安全、可解释与治理测试的风险框架。',
  },
]

const sources = ref<Source[]>([])
const legacyCoverage = ref<LegacyCoverageSummary | null>(null)
const loading = ref(true)
const warning = ref('')

onMounted(async () => {
  const [sourcesResult, coverageResult] = await Promise.allSettled([
    fetchSources(),
    fetchLegacyCoverage(),
  ])
  if (sourcesResult.status === 'fulfilled') {
    const remote = sourcesResult.value
    sources.value = remote.length ? remote : staticSources
  } else {
    sources.value = staticSources
    const error = sourcesResult.reason
    warning.value =
      error instanceof Error
        ? `${error.message} 当前展示内置的权威来源清单。`
        : '来源接口暂不可用，当前展示内置清单。'
  }
  if (coverageResult.status === 'fulfilled') {
    legacyCoverage.value = coverageResult.value
  }
  loading.value = false
})
</script>

<template>
  <section aria-labelledby="source-title">
    <div class="page-heading">
      <div>
        <p class="kicker">标准校验 · 来源追溯 · 覆盖审计</p>
        <h1 id="source-title">资料来源与覆盖情况</h1>
        <p>查看题目使用的标准、官方工具文档、本地来源快照与个人整理最新版覆盖情况。</p>
      </div>
    </div>

    <section v-if="legacyCoverage" class="legacy-audit card-surface" aria-labelledby="legacy-title">
      <div class="legacy-audit__copy">
        <p class="kicker">个人整理最新版覆盖审计</p>
        <h2 id="legacy-title">{{ legacyCoverage.mappedToAnswer }} / {{ legacyCoverage.total }} 道已关联详细答案</h2>
        <p>
          待人工复核 {{ legacyCoverage.unmapped }} 道。
          只有强语义匹配的题意进入搜索索引，低置信候选不计覆盖。
        </p>
      </div>
      <div class="legacy-audit__rate" aria-label="个人整理最新版覆盖率">
        <strong>{{ Math.round(legacyCoverage.coverageRate * 100) }}%</strong>
        <span>覆盖率</span>
      </div>
    </section>

    <XiaolinCoverage />

    <section class="method-card card-surface" aria-labelledby="method-title">
      <div class="section-heading">
        <span class="step-mark">方法</span>
        <div>
          <h2 id="method-title">一道题如何进入题库</h2>
          <p>从能力主题到可练习题目，完整保留事实核验和来源索引过程。</p>
        </div>
      </div>
      <ol class="method-flow">
        <li><span>1</span><strong>提炼主题</strong><p>从招聘要求与社区面经识别高频能力。</p></li>
        <li><span>2</span><strong>校验事实</strong><p>使用标准、官方文档和开源项目确认技术口径。</p></li>
        <li><span>3</span><strong>组织题目</strong><p>整理问题、练习场景、结构化答案和追问。</p></li>
        <li><span>4</span><strong>关联来源</strong><p>记录来源索引、访问日期和适用模块。</p></li>
      </ol>
    </section>

    <section class="source-section" aria-labelledby="source-list-title">
      <div class="section-heading">
        <span class="step-mark">索引</span>
        <div>
          <h2 id="source-list-title">参考来源</h2>
          <p>优先阅读仓库内的来源快照；社区资料用于观察样本趋势，标准和官方文档用于核验技术事实。</p>
        </div>
      </div>
      <div v-if="warning" class="notice notice--warning" role="status">
        <div>
          <strong>来源服务暂不可用</strong>
          <p>{{ warning }}</p>
        </div>
      </div>
      <p v-if="loading">正在加载来源索引…</p>
      <div v-else class="source-list">
        <article v-for="source in sources" :key="source.id" class="source-item">
          <div>
            <span class="chip">{{ source.kind }}</span>
            <h3>
              <SourceSnapshotViewer
                :source-id="source.snapshotId || source.id"
                :source-name="source.name"
                :original-url="source.url"
              />
            </h3>
            <p>{{ source.summary }}</p>
          </div>
          <span v-if="source.accessedAt" class="source-date">访问：{{ source.accessedAt }}</span>
        </article>
      </div>
    </section>
  </section>
</template>
