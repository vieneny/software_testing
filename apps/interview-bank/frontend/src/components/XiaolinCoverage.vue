<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { fetchXiaolinCoverage } from '../api'
import type { SourceCoverage } from '../types'
import SourceSnapshotViewer from './SourceSnapshotViewer.vue'

const coverage = ref<SourceCoverage | null>(null)
const selectedModule = ref('')
const loading = ref(true)
const errorMessage = ref('')

const modules = computed(() =>
  Array.from(
    new Set(
      (coverage.value?.documents ?? [])
        .map((document) => document.module)
        .filter(Boolean),
    ),
  ).sort((left, right) => left.localeCompare(right, 'zh-CN')),
)

const visibleDocuments = computed(() => {
  const documents = coverage.value?.documents ?? []
  return selectedModule.value
    ? documents.filter((document) => document.module === selectedModule.value)
    : documents
})

function coverageModeLabel(mode: string): string {
  const labels: Record<string, string> = {
    'direct-bank-reviewed': '直接题库 · 逐题盘点',
    'supporting-topic-mapping': '测开基础 · 主题映射',
    'navigation-reviewed': '学习导航 · 已核对',
  }
  return labels[mode] ?? mode
}

function formatNumber(value: number): string {
  return new Intl.NumberFormat('zh-CN').format(value)
}

async function loadCoverage() {
  loading.value = true
  errorMessage.value = ''
  try {
    coverage.value = await fetchXiaolinCoverage()
  } catch (error) {
    coverage.value = null
    errorMessage.value =
      error instanceof Error
        ? error.message
        : '小林 Coding 来源覆盖接口暂时不可用，请稍后重试。'
  } finally {
    loading.value = false
  }
}

onMounted(() => void loadCoverage())
</script>

<template>
  <section class="source-coverage card-surface" aria-labelledby="xiaolin-coverage-title">
    <div class="source-coverage__heading">
      <div class="section-heading">
        <span class="step-mark">扩展</span>
        <div>
          <p class="kicker">小林 Coding 测试与测开资料</p>
          <h2 id="xiaolin-coverage-title">直接题库逐题盘点，基础专题按能力映射</h2>
          <p>
            业务、Python 自动化、Java 自动化和性能题库用于发现问题；
            MySQL、Redis、网络、操作系统、Linux、Git、Docker 等作为测开基础。
            <strong>答案经过去重和原创重写，不复制“话术”。</strong>
          </p>
        </div>
      </div>
      <label v-if="coverage?.documents.length" class="source-coverage-module-filter">
        <span>按资料类型筛选</span>
        <select v-model="selectedModule">
          <option value="">全部资料（{{ coverage.documents.length }}）</option>
          <option v-for="module in modules" :key="module" :value="module">
            {{ module }}
          </option>
        </select>
      </label>
    </div>

    <div v-if="loading" class="source-coverage-loading" role="status">
      <span aria-hidden="true"></span>
      正在核对小林 Coding 来源覆盖…
    </div>

    <div v-else-if="errorMessage" class="notice notice--error" role="alert">
      <div>
        <strong>暂时无法读取小林 Coding 覆盖报告</strong>
        <p>{{ errorMessage }}</p>
      </div>
      <button class="button button--secondary" type="button" @click="loadCoverage">
        重新读取
      </button>
    </div>

    <template v-else-if="coverage?.documents.length">
      <div class="source-coverage-metrics" aria-label="小林 Coding 资料覆盖统计">
        <div>
          <strong>{{ coverage.documentCount }}</strong>
          <span>已盘点页面</span>
        </div>
        <div>
          <strong>{{ formatNumber(coverage.observedQuestionCount ?? 0) }}</strong>
          <span>当前可见题目标题</span>
        </div>
        <div>
          <strong>{{ coverage.questionReferenceCount }}</strong>
          <span>现行题映射关系</span>
        </div>
        <div :class="{ 'has-gap': coverage.unmappedDocuments > 0 }">
          <strong>{{ coverage.unmappedDocuments }}</strong>
          <span>未处置页面</span>
        </div>
      </div>

      <p
        v-if="
          coverage.declaredQuestionCount &&
          coverage.declaredQuestionCount !== coverage.observedQuestionCount
        "
        class="source-coverage-muted"
      >
        站内汇总页标注
        {{ formatNumber(coverage.declaredQuestionCount) }} 题，本次从当前页面标题实际识别
        {{ formatNumber(coverage.observedQuestionCount ?? 0) }} 题；差异单独保留，不用标称数量虚增覆盖。
      </p>

      <div v-if="visibleDocuments.length" class="source-coverage-document-list">
        <article
          v-for="document in visibleDocuments"
          :key="document.documentId"
          class="source-coverage-document"
        >
          <div class="source-coverage-document__main">
            <div class="eyebrow-row">
              <span class="chip chip--module">{{ document.module }}</span>
              <span class="chip">{{ coverageModeLabel(document.coverageMode) }}</span>
              <span class="chip chip--ghost">
                {{ formatNumber(document.sourceChars) }} 字符
              </span>
              <span
                v-if="document.observedQuestionCount"
                class="chip chip--ghost"
              >
                可见 {{ document.observedQuestionCount }} 题
              </span>
            </div>
            <h3>
              <SourceSnapshotViewer
                :source-id="document.snapshotId || document.documentId"
                :source-name="document.title"
                :original-url="document.url"
              >
                {{ document.title }}
              </SourceSnapshotViewer>
            </h3>
            <ul v-if="document.qualityNotes.length" class="source-coverage-quality-notes">
              <li v-for="note in document.qualityNotes" :key="note">{{ note }}</li>
            </ul>
          </div>
          <div class="source-coverage-document__mapping">
            <span>映射题目</span>
            <strong>{{ document.questionIds.length }}</strong>
            <details v-if="document.questionIds.length">
              <summary>查看题目 ID</summary>
              <p>{{ document.questionIds.join('、') }}</p>
            </details>
            <small v-else>等待处置</small>
          </div>
        </article>
      </div>
    </template>

    <div v-else class="empty-state empty-state--compact">
      <h3>覆盖报告暂时为空</h3>
      <p>接口已连接，但尚未生成小林 Coding 页面映射清单。</p>
    </div>
  </section>
</template>
