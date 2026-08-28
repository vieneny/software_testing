<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { AiSuggestion, TicketDetail, TicketStatus } from '../types'
import AiSuggestionPanel from './AiSuggestionPanel.vue'

const props = defineProps<{
  ticket?: TicketDetail
  loading: boolean
  busy: boolean
  aiLoading: boolean
  suggestion?: AiSuggestion
}>()

defineEmits<{
  transition: [status: TicketStatus]
  assign: [agent: string]
  suggest: []
}>()

const agent = ref('')
const normalizedAgent = computed(() => agent.value.trim())
const canAssign = computed(
  () =>
    Boolean(normalizedAgent.value) &&
    normalizedAgent.value.length <= 100 &&
    normalizedAgent.value !== (props.ticket?.assignedAgent ?? ''),
)

watch(
  () => props.ticket?.assignedAgent,
  (value) => {
    agent.value = value ?? ''
  },
  { immediate: true },
)

const statusLabels: Record<TicketStatus, string> = {
  NEW: '新建',
  TRIAGED: '已分诊',
  IN_PROGRESS: '处理中',
  WAITING_CUSTOMER: '等待客户',
  RESOLVED: '已解决',
  CLOSED: '已关闭',
  REOPENED: '已重开',
}

const transitions: Record<TicketStatus, TicketStatus[]> = {
  NEW: ['TRIAGED', 'IN_PROGRESS'],
  TRIAGED: ['IN_PROGRESS', 'WAITING_CUSTOMER'],
  IN_PROGRESS: ['WAITING_CUSTOMER', 'RESOLVED'],
  WAITING_CUSTOMER: ['IN_PROGRESS', 'RESOLVED'],
  RESOLVED: ['CLOSED', 'REOPENED'],
  REOPENED: ['IN_PROGRESS', 'RESOLVED'],
  CLOSED: [],
}

function formatDate(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '时间未知'
  return new Intl.DateTimeFormat('zh-CN', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}
</script>

<template>
  <section class="detail-panel panel">
    <div v-if="loading" class="empty-state detail-empty" role="status">
      <span class="loading-spinner" aria-hidden="true" />
      <strong>正在加载工单详情</strong>
    </div>
    <div v-else-if="!ticket" class="empty-state detail-empty">
      <span class="empty-symbol">↗</span>
      <strong>选择一张工单</strong>
      <p>查看客户信息、状态历史，并练习坐席操作与 AI 建议评测。</p>
    </div>

    <template v-else>
      <div class="detail-header">
        <div>
          <div class="detail-id-row">
            <span>{{ ticket.id }}</span>
            <span class="status-pill" :data-status="ticket.status">{{ statusLabels[ticket.status] }}</span>
          </div>
          <h2>{{ ticket.title }}</h2>
        </div>
        <span class="priority-large" :data-priority="ticket.priority">{{ ticket.priority }}</span>
      </div>

      <div class="customer-strip">
        <div class="avatar">{{ ticket.customerName.slice(0, 1) }}</div>
        <div>
          <strong>{{ ticket.customerName }}</strong>
          <span>{{ ticket.customerLevel }} 客户 · {{ ticket.category }}</span>
        </div>
        <time>截止 {{ formatDate(ticket.dueAt) }}</time>
      </div>

      <div class="description-block">
        <span>问题描述</span>
        <p>{{ ticket.description }}</p>
      </div>

      <div class="action-grid">
        <div>
          <span class="action-label">状态流转</span>
          <div class="button-row">
            <button
              v-for="status in transitions[ticket.status]"
              :key="status"
              class="secondary-button compact"
              type="button"
              :disabled="busy"
              @click="$emit('transition', status)"
            >
              {{ statusLabels[status] }}
            </button>
            <span v-if="!transitions[ticket.status].length" class="muted">已是终态</span>
          </div>
        </div>
        <div>
          <label for="agent">坐席分配</label>
          <div class="inline-form">
            <input
              id="agent"
              v-model="agent"
              maxlength="100"
              :disabled="busy"
              aria-describedby="agent-hint"
              placeholder="坐席名称"
              @keyup.enter="canAssign && $emit('assign', normalizedAgent)"
            />
            <button
              class="secondary-button compact"
              type="button"
              :disabled="busy || !canAssign"
              @click="$emit('assign', normalizedAgent)"
            >
              分配
            </button>
          </div>
          <small id="agent-hint" class="field-hint">
            {{ normalizedAgent === ticket.assignedAgent ? '当前已分配给该坐席' : '最多 100 字' }}
          </small>
        </div>
      </div>

      <AiSuggestionPanel
        :suggestion="suggestion"
        :loading="aiLoading"
        :disabled="busy"
        @generate="$emit('suggest')"
      />

      <section class="timeline">
        <div class="section-title">
          <span>流转记录</span>
          <small>{{ ticket.statusHistory.length }} 次变更</small>
        </div>
        <div v-if="!ticket.statusHistory.length" class="muted">暂无状态变更</div>
        <div
          v-for="(item, index) in ticket.statusHistory"
          :key="`${item.occurredAt}-${index}`"
          class="timeline-item"
        >
          <i />
          <div>
            <strong>{{ statusLabels[item.fromStatus] }} → {{ statusLabels[item.toStatus] }}</strong>
            <span>{{ item.operatorName }} · {{ formatDate(item.occurredAt) }}</span>
            <p v-if="item.note">{{ item.note }}</p>
          </div>
        </div>
      </section>
    </template>
  </section>
</template>
