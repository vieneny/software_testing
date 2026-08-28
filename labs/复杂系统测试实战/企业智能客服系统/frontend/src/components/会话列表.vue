<script setup lang="ts">
import type { ConversationState, ConversationSummary } from '../types'

defineProps<{
  conversations: ConversationSummary[]
  selectedId?: number
  loading: boolean
}>()

defineEmits<{
  select: [conversationId: number]
}>()

const stateLabels: Record<ConversationState, string> = {
  OPEN: '已打开',
  WAITING_AGENT: '等待坐席',
  WAITING_CUSTOMER: '等待客户',
  CLOSED: '已关闭',
}

function formatTime(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '时间未知'
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}
</script>

<template>
  <section class="ticket-board panel">
    <div class="panel-heading">
      <div>
        <p class="eyebrow">CONVERSATIONS</p>
        <h2>客户会话</h2>
      </div>
      <span class="count-chip">{{ conversations.length }} 条</span>
    </div>

    <div v-if="loading" class="empty-state" role="status">正在加载会话…</div>
    <div v-else-if="!conversations.length" class="empty-state">
      当前筛选下没有会话
    </div>
    <div v-else class="ticket-list">
      <button
        v-for="conversation in conversations"
        :key="conversation.id"
        class="ticket-card conversation-card"
        :class="{ active: conversation.id === selectedId }"
        type="button"
        :aria-current="conversation.id === selectedId ? 'true' : undefined"
        :aria-label="`会话 ${conversation.id}，${conversation.subject}，${stateLabels[conversation.state]}`"
        @click="$emit('select', conversation.id)"
      >
        <div class="ticket-card-top">
          <span class="ticket-id">CONV-{{ conversation.id }}</span>
          <span class="status-pill" :data-status="conversation.state">
            {{ stateLabels[conversation.state] }}
          </span>
        </div>
        <strong>{{ conversation.subject }}</strong>
        <div class="ticket-meta">
          <span>{{ conversation.channel }}</span>
          <span>·</span>
          <span>客户 #{{ conversation.customerId }}</span>
        </div>
        <div class="ticket-card-bottom">
          <span>版本 {{ conversation.version }}</span>
          <time>{{ formatTime(conversation.lastMessageAt) }}</time>
        </div>
      </button>
    </div>
  </section>
</template>
