<script setup lang="ts">
import { computed } from 'vue'
import type { AiSuggestion } from '../types'

const props = defineProps<{
  suggestion?: AiSuggestion
  loading: boolean
  disabled?: boolean
}>()

defineEmits<{
  generate: []
}>()

const confidencePercent = computed(() => {
  const confidence = props.suggestion?.confidence ?? 0
  if (!Number.isFinite(confidence)) return 0
  return Math.round(Math.min(1, Math.max(0, confidence)) * 100)
})
</script>

<template>
  <section class="ai-panel" :aria-busy="loading">
    <div class="ai-panel-heading">
      <div>
        <span class="ai-kicker">AI COPILOT</span>
        <h3>坐席建议</h3>
      </div>
      <button
        class="ai-button"
        type="button"
        :disabled="loading || disabled"
        @click="$emit('generate')"
      >
        {{ loading ? '分析中…' : '生成建议' }}
      </button>
    </div>

    <div v-if="loading && !suggestion" class="ai-placeholder" role="status">
      Python AI 中间件正在分析合成工单，请稍候…
    </div>
    <div v-else-if="!suggestion" class="ai-placeholder">
      调用独立 Python AI 中间件，结合工单与公开知识库生成回复草稿；默认使用离线 Mock。
    </div>

    <template v-else>
      <div v-if="suggestion.degraded" class="degraded-banner">
        <strong>已降级为人工处理提示</strong>
        <span>{{ suggestion.degradationReason || 'AI 服务未返回可用原因，请按人工流程处理' }}</span>
      </div>
      <div class="confidence-row">
        <span>置信度</span>
        <div class="confidence-track">
          <i :style="{ width: `${confidencePercent}%` }" />
        </div>
        <strong>{{ confidencePercent }}%</strong>
      </div>
      <div
        v-if="suggestion.suggestedCategory || suggestion.suggestedPriority"
        class="ai-meta-row"
      >
        <span v-if="suggestion.suggestedCategory">
          建议分类：{{ suggestion.suggestedCategory }}
        </span>
        <span v-if="suggestion.suggestedPriority">
          建议优先级：{{ suggestion.suggestedPriority }}
        </span>
      </div>
      <p class="ai-summary">{{ suggestion.summary }}</p>
      <div class="reply-draft">
        <span>建议回复</span>
        <p>{{ suggestion.suggestedReply }}</p>
      </div>
      <div v-if="suggestion.suggestedActions.length" class="ai-action-block">
        <span>建议动作</span>
        <ol>
          <li v-for="action in suggestion.suggestedActions" :key="action">{{ action }}</li>
        </ol>
      </div>
      <div v-if="suggestion.mustVerify.length" class="must-verify-block">
        <div>
          <strong>必须核验</strong>
          <span>发送或执行前由人工逐项确认</span>
        </div>
        <ul>
          <li v-for="item in suggestion.mustVerify" :key="item">{{ item }}</li>
        </ul>
      </div>
      <div v-if="suggestion.riskFlags.length" class="tag-row">
        <span v-for="flag in suggestion.riskFlags" :key="flag" class="risk-tag">{{ flag }}</span>
      </div>
      <div v-if="suggestion.knowledgeReferences.length" class="knowledge-references">
        <span>参考知识</span>
        <ul>
          <li v-for="reference in suggestion.knowledgeReferences" :key="reference">
            {{ reference }}
          </li>
        </ul>
      </div>
      <small>AI 输出必须经人工复核，不能自动发送给客户。</small>
    </template>
  </section>
</template>
