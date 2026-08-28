<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import type { Mastery, ProgressRecord, Question } from '../types'
import SafeMarkdown from './SafeMarkdown.vue'
import SourceSnapshotViewer from './SourceSnapshotViewer.vue'

const props = defineProps<{
  question: Question
  progress: ProgressRecord
}>()

const emit = defineEmits<{
  update: [progress: ProgressRecord]
}>()

const revealed = ref(false)
const note = ref(props.progress.note)
const noteStatus = ref('')
const answerContent = ref<HTMLElement | null>(null)
const optimisticProgress = ref<ProgressRecord>({ ...props.progress })

watch(
  () => props.progress,
  (value) => {
    optimisticProgress.value = { ...value }
  },
)

watch(
  () => props.progress.note,
  (value) => {
    note.value = value
    noteStatus.value = ''
  },
)

function patch(changes: Partial<ProgressRecord>) {
  optimisticProgress.value = {
    ...optimisticProgress.value,
    questionId: props.question.id,
    ...changes,
  }
  emit('update', { ...optimisticProgress.value })
}

function setMastery(event: Event) {
  patch({ mastery: (event.target as HTMLSelectElement).value as Mastery })
}

function saveNote() {
  const normalizedNote = note.value.trim()
  note.value = normalizedNote
  patch({ note: normalizedNote })
  noteStatus.value = normalizedNote ? '笔记已保存' : '空笔记已清除'
}

async function toggleAnswer() {
  revealed.value = !revealed.value
  if (!revealed.value) return
  await nextTick()
  answerContent.value?.focus()
}

function originLabel(origin: string): string {
  const labels: Record<string, string> = {
    'xiaolincoding-reviewed': '小林 Coding 资料原创重构题',
    'supplemental-reviewed': '补充评审题',
    'curated-2026': '2026 公开资料增补题',
    'legacy-reviewed': '历史资料审核题',
  }
  return labels[origin] ?? origin
}
</script>

<template>
  <article class="question-card" :aria-labelledby="`question-${question.id}`">
    <header class="question-card__header">
      <div class="question-card__copy">
        <div class="eyebrow-row" aria-label="题目分类">
          <span class="chip chip--module">{{ question.moduleName }}</span>
          <span class="chip">{{ question.level }}</span>
          <span class="chip">{{ question.kind }}</span>
          <span v-if="question.origin" class="chip chip--ghost">
            {{ originLabel(question.origin) }}
          </span>
          <span v-for="role in question.roles" :key="role" class="chip chip--ghost">
            {{ role }}
          </span>
        </div>
        <h2 :id="`question-${question.id}`">{{ question.title }}</h2>
        <p v-if="question.focus" class="question-focus">
          <strong>面试官在看：</strong>{{ question.focus }}
        </p>
      </div>
      <div class="question-card__quick-actions">
        <button
          class="quick-action-button"
          type="button"
          :class="{ 'is-active': optimisticProgress.favorite }"
          :aria-pressed="optimisticProgress.favorite"
          :aria-label="optimisticProgress.favorite ? '取消收藏' : '收藏题目'"
          @click="patch({ favorite: !optimisticProgress.favorite })"
        >
          {{ optimisticProgress.favorite ? '已收藏' : '收藏' }}
        </button>
        <button
          class="quick-action-button quick-action-button--warning"
          type="button"
          :class="{ 'is-active': optimisticProgress.wrong }"
          :aria-pressed="optimisticProgress.wrong"
          :aria-label="optimisticProgress.wrong ? '移出错题本' : '加入错题本'"
          @click="patch({ wrong: !optimisticProgress.wrong })"
        >
          {{ optimisticProgress.wrong ? '移出错题' : '加入错题' }}
        </button>
      </div>
    </header>

    <div v-if="question.tags.length" class="tag-row" aria-label="知识标签">
      <span v-for="tag in question.tags" :key="tag" class="tag"># {{ tag }}</span>
    </div>

    <div v-if="question.scenario" class="scenario-box">
      <span class="scenario-box__label">模拟场景</span>
      <p>{{ question.scenario }}</p>
    </div>

    <div class="answer-gate">
      <div>
        <strong>先口述，再核对</strong>
        <p>建议先用 2–3 分钟说出结论、依据、落地步骤和风险，再展开参考内容。</p>
      </div>
      <button
        class="button button--primary"
        type="button"
        :aria-expanded="revealed"
        :aria-controls="`answer-${question.id}`"
        @click="toggleAnswer"
      >
        {{ revealed ? '收起参考内容' : '揭示参考答案' }}
      </button>
    </div>

    <div
      v-if="revealed"
      :id="`answer-${question.id}`"
      ref="answerContent"
      class="answer-stack"
      data-testid="answer-content"
      tabindex="-1"
    >
      <section v-if="question.answer" class="answer-panel answer-panel--primary">
        <h3>参考答案</h3>
        <SafeMarkdown :content="question.answer" />
      </section>
      <details
        v-if="question.explanation"
        class="answer-panel answer-panel--collapsible"
        open
      >
        <summary>原理与实践解释</summary>
        <SafeMarkdown :content="question.explanation" />
      </details>
      <details
        v-if="question.relatedQuestionIds.length"
        class="answer-panel answer-panel--collapsible"
        data-testid="deepening-rationale"
      >
        <summary>与核心题的深化关系</summary>
        <SafeMarkdown :content="question.deepeningRationale" />
        <p class="source-line">
          <strong>关联题目：</strong>{{ question.relatedQuestionIds.join('、') }}
        </p>
      </details>
      <details
        v-if="question.followups.length"
        class="answer-panel answer-panel--collapsible"
      >
        <summary>面试官可能追问（{{ question.followups.length }}）</summary>
        <ul class="clean-list">
          <li v-for="item in question.followups" :key="item">{{ item }}</li>
        </ul>
      </details>
      <details
        v-if="question.pitfalls.length"
        class="answer-panel answer-panel--collapsible answer-panel--caution"
      >
        <summary>常见误区（{{ question.pitfalls.length }}）</summary>
        <ul class="clean-list">
          <li v-for="item in question.pitfalls" :key="item">{{ item }}</li>
        </ul>
      </details>
      <details v-if="question.historicalReference" class="history-reference">
        <summary>查看历史资料关联</summary>
        <SafeMarkdown :content="question.historicalReference" />
      </details>
      <p v-if="question.sourceIds.length" class="source-line">
        <strong>来源索引：</strong>
        <template v-for="(sourceId, index) in question.sourceIds" :key="sourceId">
          <span v-if="index">、</span>
          <SourceSnapshotViewer
            :source-id="sourceId"
            :source-name="sourceId"
            compact
          />
        </template>
      </p>
    </div>

    <footer class="learning-panel">
      <label class="compact-field">
        <span>掌握度</span>
        <select :value="optimisticProgress.mastery" @change="setMastery">
          <option value="unseen">未学习</option>
          <option value="learning">学习中</option>
          <option value="mastered">已掌握</option>
        </select>
      </label>
      <label class="note-field">
        <span>我的笔记</span>
        <textarea
          v-model="note"
          rows="2"
          placeholder="写下自己的答题结构、薄弱点或待验证问题"
          @input="noteStatus = ''"
          @keydown.meta.enter.prevent="saveNote"
          @keydown.ctrl.enter.prevent="saveNote"
        />
        <small v-if="noteStatus" class="note-status" role="status" aria-live="polite">
          {{ noteStatus }}
        </small>
      </label>
      <button class="button button--secondary button--compact" type="button" @click="saveNote">
        保存笔记
      </button>
    </footer>
  </article>
</template>
