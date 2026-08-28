<script setup lang="ts">
import type { TicketSummary } from '../types'

defineProps<{
  tickets: TicketSummary[]
  selectedId?: string
  loading: boolean
}>()

defineEmits<{
  select: [ticketId: string]
}>()

const statusLabels: Record<string, string> = {
  NEW: '新建',
  TRIAGED: '已分诊',
  IN_PROGRESS: '处理中',
  WAITING_CUSTOMER: '待客户',
  RESOLVED: '已解决',
  CLOSED: '已关闭',
  REOPENED: '已重开',
}

const priorityLabels: Record<string, string> = {
  LOW: '低',
  MEDIUM: '中',
  HIGH: '高',
  URGENT: '紧急',
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
        <p class="eyebrow">QUEUE</p>
        <h2>工单队列</h2>
      </div>
      <span class="count-chip">{{ tickets.length }} 条</span>
    </div>

    <div v-if="loading" class="empty-state" role="status">正在加载工单…</div>
    <div v-else-if="!tickets.length" class="empty-state">当前筛选下没有工单</div>
    <div v-else class="ticket-list">
      <button
        v-for="ticket in tickets"
        :key="ticket.id"
        class="ticket-card"
        :class="{ active: ticket.id === selectedId }"
        type="button"
        :aria-current="ticket.id === selectedId ? 'true' : undefined"
        :aria-label="`${ticket.id}，${ticket.title}，${statusLabels[ticket.status]}`"
        @click="$emit('select', ticket.id)"
      >
        <div class="ticket-card-top">
          <span class="ticket-id">{{ ticket.id }}</span>
          <span class="priority" :data-priority="ticket.priority">
            {{ priorityLabels[ticket.priority] }}
          </span>
        </div>
        <strong>{{ ticket.title }}</strong>
        <div class="ticket-meta">
          <span class="status-dot" :data-status="ticket.status" />
          <span>{{ statusLabels[ticket.status] }}</span>
          <span>·</span>
          <span>{{ ticket.category }}</span>
        </div>
        <div class="ticket-card-bottom">
          <span>{{ ticket.assignedAgent || '待分配' }}</span>
          <time>{{ formatTime(ticket.updatedAt) }}</time>
        </div>
      </button>
    </div>
  </section>
</template>
