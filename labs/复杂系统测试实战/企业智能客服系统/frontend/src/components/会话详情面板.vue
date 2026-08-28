<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import type {
  ConversationDetail,
  ConversationState,
  TicketPriority,
} from '../types'

interface LinkedTicketDraft {
  title: string
  description: string
  category: string
  priority: TicketPriority
}

const props = withDefaults(
  defineProps<{
    conversation?: ConversationDetail
    loading: boolean
    busy: boolean
    includeInternal: boolean
    messageSuccessToken?: number
    ticketSuccessToken?: number
  }>(),
  {
    messageSuccessToken: 0,
    ticketSuccessToken: 0,
  },
)

const emit = defineEmits<{
  toggleInternal: [includeInternal: boolean]
  sendMessage: [kind: 'reply' | 'note', authorName: string, content: string]
  transition: [targetState: Extract<ConversationState, 'OPEN' | 'CLOSED'>, note: string]
  createTicket: [draft: LinkedTicketDraft]
}>()

const messageKind = ref<'reply' | 'note'>('reply')
const authorName = ref('学习坐席')
const messageContent = ref('')
const transitionNote = ref('')
const formError = ref('')
const ticketOpen = ref(false)
const ticketDraft = reactive<LinkedTicketDraft>({
  title: '',
  description: '',
  category: 'OTHER',
  priority: 'MEDIUM',
})

const stateLabels: Record<ConversationState, string> = {
  OPEN: '已打开',
  WAITING_AGENT: '等待坐席',
  WAITING_CUSTOMER: '等待客户',
  CLOSED: '已关闭',
}

const visibleMessages = computed(() => {
  const messages = props.conversation?.messages ?? []
  return props.includeInternal
    ? messages
    : messages.filter((message) => message.visibility === 'CUSTOMER')
})

watch(
  () => props.conversation?.id,
  () => {
    messageKind.value = 'reply'
    messageContent.value = ''
    transitionNote.value = ''
    formError.value = ''
    ticketOpen.value = false
    ticketDraft.title = props.conversation?.subject ?? ''
    ticketDraft.description = props.conversation
      ? `由会话 #${props.conversation.id} 升级创建，请结合客户可见消息继续排查。`
      : ''
  },
  { immediate: true },
)

watch(
  () => props.includeInternal,
  (enabled) => {
    if (!enabled && messageKind.value === 'note') messageKind.value = 'reply'
  },
)

watch(
  () => props.messageSuccessToken,
  () => {
    messageContent.value = ''
  },
)

watch(
  () => props.ticketSuccessToken,
  () => {
    ticketOpen.value = false
  },
)

function formatDate(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '时间未知'
  return new Intl.DateTimeFormat('zh-CN', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}

function submitMessage() {
  formError.value = ''
  const author = authorName.value.trim()
  const content = messageContent.value.trim()
  if (!author) {
    formError.value = '坐席名称不能为空'
    return
  }
  if (!content) {
    formError.value = messageKind.value === 'note' ? '内部备注不能为空' : '回复内容不能为空'
    return
  }
  if (!props.conversation || props.busy) return
  emit('sendMessage', messageKind.value, author, content)
}

function submitTicket() {
  formError.value = ''
  const title = ticketDraft.title.trim()
  const description = ticketDraft.description.trim()
  if (!title || !description) {
    formError.value = '关联工单的标题和描述不能为空'
    return
  }
  if (!props.conversation || props.busy) return
  emit('createTicket', { ...ticketDraft, title, description })
}
</script>

<template>
  <section class="detail-panel panel conversation-detail">
    <div v-if="loading" class="empty-state detail-empty" role="status">
      <span class="loading-spinner" aria-hidden="true" />
      <strong>正在加载会话详情</strong>
    </div>
    <div v-else-if="!conversation" class="empty-state detail-empty">
      <span class="empty-symbol">↗</span>
      <strong>选择一条客户会话</strong>
      <p>练习客户可见回复、内部备注、并发版本、幂等重试与会话升级工单。</p>
    </div>

    <template v-else>
      <div class="detail-header">
        <div>
          <div class="detail-id-row">
            <span>CONV-{{ conversation.id }}</span>
            <span class="status-pill" :data-status="conversation.state">
              {{ stateLabels[conversation.state] }}
            </span>
          </div>
          <h2>{{ conversation.subject }}</h2>
        </div>
        <span class="priority-large">{{ conversation.channel }}</span>
      </div>

      <div class="customer-strip">
        <div class="avatar">{{ conversation.customerName.slice(0, 1) }}</div>
        <div>
          <strong>{{ conversation.customerName }}</strong>
          <span>{{ conversation.customerLevel }} 客户 · 版本 {{ conversation.version }}</span>
        </div>
        <time>最近消息 {{ formatDate(conversation.lastMessageAt) }}</time>
      </div>

      <div class="conversation-toolbar">
        <div>
          <strong>消息时间线</strong>
          <span>{{ visibleMessages.length }} 条当前可见消息</span>
        </div>
        <label class="internal-toggle">
          <input
            type="checkbox"
            :checked="includeInternal"
            :disabled="busy"
            @change="$emit('toggleInternal', ($event.target as HTMLInputElement).checked)"
          />
          坐席视图（包含内部备注）
        </label>
      </div>
      <p v-if="!includeInternal" class="customer-view-hint">
        当前为默认客户视图：内部备注和系统内部状态记录不会显示。
      </p>

      <div class="message-timeline">
        <article
          v-for="message in visibleMessages"
          :key="message.id"
          class="message-bubble"
          :class="{
            internal: message.visibility === 'INTERNAL',
            customer: message.senderType === 'CUSTOMER',
          }"
        >
          <div>
            <strong>{{ message.authorName }}</strong>
            <span>{{ message.senderType }}</span>
            <span v-if="message.visibility === 'INTERNAL'" class="risk-tag">内部备注</span>
            <time>{{ formatDate(message.createdAt) }}</time>
          </div>
          <p>{{ message.content }}</p>
        </article>
        <div v-if="!visibleMessages.length" class="empty-state">当前视图暂无消息</div>
      </div>

      <section class="conversation-compose">
        <div class="compose-tabs">
          <button
            class="secondary-button compact"
            :class="{ active: messageKind === 'reply' }"
            type="button"
            :disabled="busy || conversation.state === 'CLOSED'"
            @click="messageKind = 'reply'"
          >
            客户可见回复
          </button>
          <button
            v-if="includeInternal"
            class="secondary-button compact"
            :class="{ active: messageKind === 'note' }"
            type="button"
            :disabled="busy || conversation.state === 'CLOSED'"
            @click="messageKind = 'note'"
          >
            内部备注
          </button>
        </div>
        <label>
          坐席名称
          <input v-model="authorName" maxlength="100" :disabled="busy" />
        </label>
        <label>
          {{ messageKind === 'note' ? '内部备注内容' : '回复客户的内容' }}
          <textarea
            v-model="messageContent"
            rows="3"
            maxlength="5000"
            :disabled="busy || conversation.state === 'CLOSED'"
            :placeholder="
              messageKind === 'note'
                ? '仅坐席视图可见，可记录排查证据和下一步'
                : '客户可见，发送前请人工核对'
            "
          />
        </label>
        <div class="form-actions compact-actions">
          <span v-if="conversation.state === 'CLOSED'" class="muted">
            已关闭会话需先重新打开
          </span>
          <button
            class="primary-button"
            type="button"
            :disabled="busy || conversation.state === 'CLOSED'"
            @click="submitMessage"
          >
            {{ busy ? '提交中…' : messageKind === 'note' ? '添加内部备注' : '发送公开回复' }}
          </button>
        </div>
      </section>

      <section class="conversation-actions">
        <div>
          <label>
            状态备注（可选）
            <input
              v-model="transitionNote"
              maxlength="500"
              :disabled="busy"
              placeholder="记录本次状态变更原因（可选）"
            />
          </label>
          <button
            class="secondary-button"
            type="button"
            :disabled="busy"
            @click="
              $emit(
                'transition',
                conversation.state === 'CLOSED' ? 'OPEN' : 'CLOSED',
                transitionNote.trim(),
              )
            "
          >
            {{ conversation.state === 'CLOSED' ? '重新打开会话' : '关闭会话' }}
          </button>
        </div>
        <div>
          <strong>关联工单</strong>
          <div v-if="conversation.linkedTicketIds.length" class="linked-ticket-list">
            <span v-for="ticketId in conversation.linkedTicketIds" :key="ticketId">
              {{ ticketId }}
            </span>
          </div>
          <span v-else class="muted">尚未升级为工单</span>
          <button
            class="secondary-button compact"
            type="button"
            :disabled="busy"
            @click="ticketOpen = !ticketOpen"
          >
            {{ ticketOpen ? '收起工单表单' : '从会话创建工单' }}
          </button>
        </div>
      </section>

      <form v-if="ticketOpen" class="linked-ticket-form" @submit.prevent="submitTicket">
        <h3>创建关联工单</h3>
        <label>
          标题
          <input v-model="ticketDraft.title" maxlength="200" :disabled="busy" required />
        </label>
        <label>
          描述
          <textarea
            v-model="ticketDraft.description"
            rows="3"
            maxlength="5000"
            :disabled="busy"
            required
          />
        </label>
        <div class="form-grid">
          <label>
            分类
            <select v-model="ticketDraft.category" :disabled="busy">
              <option value="ACCOUNT">账号</option>
              <option value="BILLING">账单</option>
              <option value="PRODUCT">产品</option>
              <option value="OTHER">其他</option>
            </select>
          </label>
          <label>
            优先级
            <select v-model="ticketDraft.priority" :disabled="busy">
              <option
                v-for="priority in (['LOW', 'MEDIUM', 'HIGH', 'URGENT'] as TicketPriority[])"
                :key="priority"
              >
                {{ priority }}
              </option>
            </select>
          </label>
        </div>
        <div class="form-actions">
          <button class="primary-button" type="submit" :disabled="busy">
            {{ busy ? '创建中…' : '确认创建关联工单' }}
          </button>
        </div>
      </form>

      <p v-if="formError" class="form-error" role="alert">{{ formError }}</p>
    </template>
  </section>
</template>
