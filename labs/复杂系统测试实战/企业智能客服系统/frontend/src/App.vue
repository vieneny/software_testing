<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import {
  ApiError,
  api,
  createIdempotencyKey,
  type IdempotencyKey,
} from './api'
import CreateTicketForm from './components/CreateTicketForm.vue'
import TicketBoard from './components/TicketBoard.vue'
import TicketDetailPanel from './components/TicketDetailPanel.vue'
import ConversationBoard from './components/会话列表.vue'
import ConversationDetailPanel from './components/会话详情面板.vue'
import CreateConversationForm from './components/创建会话表单.vue'
import type {
  AiSuggestion,
  ConversationDetail,
  ConversationState,
  ConversationSummary,
  CreateConversationPayload,
  CreateTicketPayload,
  Customer,
  SendConversationMessagePayload,
  TicketDetail,
  TicketPriority,
  TicketStatus,
  TicketSummary,
  TransitionConversationPayload,
} from './types'

type WorkspaceModule = 'tickets' | 'conversations'

interface PendingOperation {
  fingerprint: string
  key: IdempotencyKey
}

interface LinkedTicketDraft {
  title: string
  description: string
  category: string
  priority: TicketPriority
}

const activeModule = ref<WorkspaceModule>('tickets')
const tickets = ref<TicketSummary[]>([])
const customers = ref<Customer[]>([])
const selected = ref<TicketDetail>()
const suggestion = ref<AiSuggestion>()
const conversations = ref<ConversationSummary[]>([])
const selectedConversation = ref<ConversationDetail>()
const includeInternal = ref(false)
const conversationMessageSuccessToken = ref(0)
const linkedTicketSuccessToken = ref(0)
const statusFilter = ref<TicketStatus | ''>('')
const conversationStateFilter = ref<ConversationState | ''>('')
const ticketsLoading = ref(false)
const customersLoading = ref(false)
const detailLoading = ref(false)
const conversationsLoading = ref(false)
const conversationDetailLoading = ref(false)
const busy = ref(false)
const aiLoading = ref(false)
const createOpen = ref(false)
const conversationCreateOpen = ref(false)
const error = ref('')
const notice = ref('')

let ticketsController: AbortController | undefined
let detailController: AbortController | undefined
let conversationsController: AbortController | undefined
let conversationDetailController: AbortController | undefined
let detailSequence = 0
let conversationDetailSequence = 0
let ticketCreateAttempt: PendingOperation | undefined
let conversationCreateAttempt: PendingOperation | undefined
let conversationMessageAttempt: PendingOperation | undefined
let conversationTransitionAttempt: PendingOperation | undefined
let linkedTicketAttempt: PendingOperation | undefined

const activeCount = computed(
  () => tickets.value.filter((ticket) => !['RESOLVED', 'CLOSED'].includes(ticket.status)).length,
)
const urgentCount = computed(
  () => tickets.value.filter((ticket) => ticket.priority === 'URGENT').length,
)
const waitingCount = computed(
  () => tickets.value.filter((ticket) => ticket.status === 'WAITING_CUSTOMER').length,
)
const openConversationCount = computed(
  () => conversations.value.filter((conversation) => conversation.state !== 'CLOSED').length,
)
const waitingAgentCount = computed(
  () => conversations.value.filter((conversation) => conversation.state === 'WAITING_AGENT').length,
)
const waitingCustomerConversationCount = computed(
  () =>
    conversations.value.filter((conversation) => conversation.state === 'WAITING_CUSTOMER').length,
)

function isAbortError(reason: unknown): boolean {
  return reason instanceof DOMException && reason.name === 'AbortError'
}

function showError(reason: unknown, fallback = '操作失败，请稍后重试') {
  if (isAbortError(reason)) return
  error.value = reason instanceof Error && reason.message ? reason.message : fallback
  notice.value = ''
}

function showNotice(message: string) {
  notice.value = message
  error.value = ''
}

function operationKey(
  current: PendingOperation | undefined,
  scope: string,
  payload: unknown,
): PendingOperation {
  const fingerprint = JSON.stringify(payload)
  return current?.fingerprint === fingerprint
    ? current
    : { fingerprint, key: createIdempotencyKey(scope) }
}

function customerSafeConversation(detail: ConversationDetail): ConversationDetail {
  if (includeInternal.value) return detail
  return {
    ...detail,
    messages: detail.messages.filter((message) => message.visibility === 'CUSTOMER'),
  }
}

async function loadCustomers(clearError = true) {
  customersLoading.value = true
  if (clearError) error.value = ''
  try {
    customers.value = await api.customers()
  } catch (reason) {
    showError(reason, '客户列表加载失败')
  } finally {
    customersLoading.value = false
  }
}

async function loadTickets(selectFirst = false, clearError = true) {
  ticketsController?.abort()
  const controller = new AbortController()
  ticketsController = controller
  ticketsLoading.value = true
  if (clearError) error.value = ''
  try {
    const page = await api.listTickets(statusFilter.value || undefined, controller.signal)
    tickets.value = page.content
    if (selected.value && !tickets.value.some((ticket) => ticket.id === selected.value?.id)) {
      selected.value = undefined
      suggestion.value = undefined
    }
    if (selectFirst && !selected.value && tickets.value.length) {
      await selectTicket(tickets.value[0].id)
    }
    return true
  } catch (reason) {
    showError(reason, '工单队列加载失败')
    return false
  } finally {
    if (ticketsController === controller) {
      ticketsLoading.value = false
      ticketsController = undefined
    }
  }
}

async function selectTicket(ticketId: string) {
  detailController?.abort()
  const controller = new AbortController()
  detailController = controller
  const sequence = ++detailSequence
  detailLoading.value = true
  error.value = ''
  try {
    const detail = await api.ticketDetail(ticketId, controller.signal)
    if (sequence === detailSequence) {
      selected.value = detail
      suggestion.value = undefined
    }
  } catch (reason) {
    showError(reason, '工单详情加载失败')
  } finally {
    if (sequence === detailSequence) {
      detailLoading.value = false
      detailController = undefined
    }
  }
}

async function loadConversations(selectFirst = false, clearError = true) {
  conversationsController?.abort()
  const controller = new AbortController()
  conversationsController = controller
  conversationsLoading.value = true
  if (clearError) error.value = ''
  try {
    const page = await api.listConversations(
      conversationStateFilter.value || undefined,
      controller.signal,
    )
    conversations.value = page.content
    if (
      selectedConversation.value &&
      !conversations.value.some(
        (conversation) => conversation.id === selectedConversation.value?.id,
      )
    ) {
      selectedConversation.value = undefined
      includeInternal.value = false
    }
    if (selectFirst && !selectedConversation.value && conversations.value.length) {
      await selectConversation(conversations.value[0].id)
    }
    return true
  } catch (reason) {
    showError(reason, '会话列表加载失败')
    return false
  } finally {
    if (conversationsController === controller) {
      conversationsLoading.value = false
      conversationsController = undefined
    }
  }
}

async function loadConversationDetail(conversationId: number, showInternal: boolean) {
  conversationDetailController?.abort()
  const controller = new AbortController()
  conversationDetailController = controller
  const sequence = ++conversationDetailSequence
  conversationDetailLoading.value = true
  error.value = ''
  try {
    const detail = await api.conversationDetail(
      conversationId,
      showInternal,
      controller.signal,
    )
    if (sequence === conversationDetailSequence) {
      selectedConversation.value = customerSafeConversation(detail)
    }
    return true
  } catch (reason) {
    showError(reason, '会话详情加载失败')
    return false
  } finally {
    if (sequence === conversationDetailSequence) {
      conversationDetailLoading.value = false
      conversationDetailController = undefined
    }
  }
}

async function selectConversation(conversationId: number) {
  includeInternal.value = false
  await loadConversationDetail(conversationId, false)
}

async function toggleInternalMessages(enabled: boolean) {
  if (!selectedConversation.value) return
  includeInternal.value = enabled
  await loadConversationDetail(selectedConversation.value.id, enabled)
}

async function initialize() {
  notice.value = ''
  await Promise.all([
    loadCustomers(false),
    loadTickets(true, false),
    loadConversations(false, false),
  ])
}

async function createTicket(payload: CreateTicketPayload) {
  if (busy.value) return
  ticketCreateAttempt = operationKey(ticketCreateAttempt, 'ticket-create', payload)
  busy.value = true
  error.value = ''
  try {
    const created = await api.createTicket(payload, ticketCreateAttempt.key)
    ticketCreateAttempt = undefined
    selected.value = created
    suggestion.value = undefined
    createOpen.value = false
    const refreshed = await loadTickets(false, false)
    if (refreshed) showNotice(`工单 ${created.id} 创建成功`)
    else notice.value = `工单 ${created.id} 已创建，但队列刷新失败`
  } catch (reason) {
    showError(reason, '工单创建失败')
  } finally {
    busy.value = false
  }
}

async function refreshAfterConcurrentChange(ticketId: string, reason: unknown) {
  if (reason instanceof ApiError && reason.code === 'CONCURRENT_MODIFICATION') {
    await Promise.all([loadTickets(false, false), selectTicket(ticketId)])
  }
}

async function transition(status: TicketStatus) {
  if (!selected.value || busy.value) return
  const currentTicket = selected.value
  busy.value = true
  error.value = ''
  try {
    selected.value = await api.transitionTicket(
      currentTicket.id,
      status,
      currentTicket.version,
    )
    suggestion.value = undefined
    const refreshed = await loadTickets(false, false)
    if (refreshed) showNotice(`工单已流转为 ${status}`)
    else notice.value = `工单已流转为 ${status}，但队列刷新失败`
  } catch (reason) {
    showError(reason, '状态流转失败')
    await refreshAfterConcurrentChange(currentTicket.id, reason)
  } finally {
    busy.value = false
  }
}

async function assign(agent: string) {
  if (!selected.value || busy.value) return
  const currentTicket = selected.value
  busy.value = true
  error.value = ''
  try {
    selected.value = await api.assignTicket(
      currentTicket.id,
      agent,
      currentTicket.version,
    )
    const refreshed = await loadTickets(false, false)
    if (refreshed) showNotice(`工单已分配给 ${agent}`)
    else notice.value = `工单已分配给 ${agent}，但队列刷新失败`
  } catch (reason) {
    showError(reason, '坐席分配失败')
    await refreshAfterConcurrentChange(currentTicket.id, reason)
  } finally {
    busy.value = false
  }
}

async function generateSuggestion() {
  if (!selected.value || aiLoading.value) return
  const ticketId = selected.value.id
  aiLoading.value = true
  error.value = ''
  try {
    const generated = await api.aiSuggestion(ticketId)
    if (selected.value?.id === ticketId) suggestion.value = generated
  } catch (reason) {
    showError(reason, 'AI 建议生成失败')
  } finally {
    aiLoading.value = false
  }
}

async function createConversation(payload: CreateConversationPayload) {
  if (busy.value) return
  conversationCreateAttempt = operationKey(
    conversationCreateAttempt,
    'conversation-create',
    payload,
  )
  busy.value = true
  error.value = ''
  try {
    const created = await api.createConversation(payload, conversationCreateAttempt.key)
    conversationCreateAttempt = undefined
    selectedConversation.value = customerSafeConversation(created)
    conversationCreateOpen.value = false
    await loadConversations(false, false)
    showNotice(`会话 CONV-${created.id} 创建成功`)
  } catch (reason) {
    showError(reason, '会话创建失败')
  } finally {
    busy.value = false
  }
}

async function refreshConversationAfterConflict(conversationId: number, reason: unknown) {
  if (reason instanceof ApiError && reason.code === 'CONCURRENT_MODIFICATION') {
    const detail = await api.conversationDetail(conversationId, includeInternal.value)
    selectedConversation.value = customerSafeConversation(detail)
    await loadConversations(false, false)
  }
}

async function sendConversationMessage(
  kind: 'reply' | 'note',
  authorName: string,
  content: string,
) {
  if (!selectedConversation.value || busy.value) return
  const current = selectedConversation.value
  const payload: SendConversationMessagePayload = {
    expectedVersion: current.version,
    senderType: 'AGENT',
    visibility: kind === 'note' ? 'INTERNAL' : 'CUSTOMER',
    authorName,
    content,
  }
  conversationMessageAttempt = operationKey(
    conversationMessageAttempt,
    `conversation-${kind}`,
    { conversationId: current.id, kind, authorName, content },
  )
  busy.value = true
  error.value = ''
  try {
    const updated = await api.sendConversationMessage(
      current.id,
      payload,
      conversationMessageAttempt.key,
      includeInternal.value,
    )
    conversationMessageAttempt = undefined
    selectedConversation.value = customerSafeConversation(updated)
    conversationMessageSuccessToken.value += 1
    await loadConversations(false, false)
    showNotice(kind === 'note' ? '内部备注已保存' : '客户可见回复已保存')
  } catch (reason) {
    showError(reason, kind === 'note' ? '内部备注保存失败' : '公开回复发送失败')
    await refreshConversationAfterConflict(current.id, reason)
  } finally {
    busy.value = false
  }
}

async function transitionConversation(
  targetState: Extract<ConversationState, 'OPEN' | 'CLOSED'>,
  note: string,
) {
  if (!selectedConversation.value || busy.value) return
  const current = selectedConversation.value
  const payload: TransitionConversationPayload = {
    expectedVersion: current.version,
    targetState,
    operatorName: '学习坐席',
    ...(note ? { note } : {}),
  }
  conversationTransitionAttempt = operationKey(
    conversationTransitionAttempt,
    'conversation-transition',
    { conversationId: current.id, targetState, note },
  )
  busy.value = true
  error.value = ''
  try {
    const updated = await api.transitionConversation(
      current.id,
      payload,
      conversationTransitionAttempt.key,
      includeInternal.value,
    )
    conversationTransitionAttempt = undefined
    selectedConversation.value = customerSafeConversation(updated)
    await loadConversations(false, false)
    showNotice(targetState === 'CLOSED' ? '会话已关闭' : '会话已重新打开')
  } catch (reason) {
    showError(reason, targetState === 'CLOSED' ? '会话关闭失败' : '会话重开失败')
    await refreshConversationAfterConflict(current.id, reason)
  } finally {
    busy.value = false
  }
}

async function createLinkedTicket(draft: LinkedTicketDraft) {
  if (!selectedConversation.value || busy.value) return
  const conversation = selectedConversation.value
  const payload: CreateTicketPayload = {
    customerId: conversation.customerId,
    conversationId: conversation.id,
    ...draft,
  }
  linkedTicketAttempt = operationKey(linkedTicketAttempt, 'ticket-from-conversation', payload)
  busy.value = true
  error.value = ''
  try {
    const created = await api.createTicket(payload, linkedTicketAttempt.key)
    linkedTicketAttempt = undefined
    const refreshedConversation = await api.conversationDetail(
      conversation.id,
      includeInternal.value,
    )
    selectedConversation.value = customerSafeConversation(refreshedConversation)
    selected.value = created
    linkedTicketSuccessToken.value += 1
    await Promise.all([loadTickets(false, false), loadConversations(false, false)])
    showNotice(`关联工单 ${created.id} 创建成功`)
  } catch (reason) {
    showError(reason, '关联工单创建失败')
  } finally {
    busy.value = false
  }
}

function openPrimaryCreate() {
  if (!customers.value.length) {
    error.value = customersLoading.value ? '客户列表仍在加载，请稍候' : '没有可用客户，请先重新加载'
    return
  }
  if (activeModule.value === 'tickets') createOpen.value = true
  else conversationCreateOpen.value = true
}

function switchModule(module: WorkspaceModule) {
  activeModule.value = module
  error.value = ''
  notice.value = ''
  if (module === 'conversations' && !conversations.value.length) {
    void loadConversations(true)
  }
}

onMounted(initialize)
onBeforeUnmount(() => {
  ticketsController?.abort()
  detailController?.abort()
  conversationsController?.abort()
  conversationDetailController?.abort()
})
</script>

<template>
  <main>
    <header class="app-header">
      <div class="brand">
        <div class="brand-mark">智</div>
        <div>
          <strong>智服台</strong>
          <span>SMART SERVICE LAB</span>
        </div>
      </div>
      <div class="header-actions">
        <span class="environment"><i /> 学习环境 · demo</span>
        <button
          class="primary-button"
          type="button"
          :disabled="customersLoading"
          @click="openPrimaryCreate"
        >
          {{ activeModule === 'tickets' ? '＋ 新建工单' : '＋ 新建会话' }}
        </button>
      </div>
    </header>

    <nav class="module-tabs" aria-label="工作台模块">
      <button
        type="button"
        :class="{ active: activeModule === 'tickets' }"
        @click="switchModule('tickets')"
      >
        工单工作台
      </button>
      <button
        type="button"
        :class="{ active: activeModule === 'conversations' }"
        @click="switchModule('conversations')"
      >
        客户会话
      </button>
    </nav>

    <section class="workspace-heading">
      <div v-if="activeModule === 'tickets'">
        <p class="eyebrow">CUSTOMER OPERATIONS</p>
        <h1>客服工单工作台</h1>
        <p>练习工单流转、分配、并发版本、关联会话与 AI 辅助建议。</p>
      </div>
      <div v-else>
        <p class="eyebrow">OMNICHANNEL SERVICE</p>
        <h1>客户会话工作台</h1>
        <p>练习公开回复、内部备注、关闭重开、幂等重试以及从会话升级工单。</p>
      </div>

      <label v-if="activeModule === 'tickets'" class="filter-control">
        队列筛选
        <select
          v-model="statusFilter"
          :disabled="ticketsLoading"
          aria-label="按工单状态筛选"
          @change="loadTickets(false)"
        >
          <option value="">全部状态</option>
          <option value="NEW">新建</option>
          <option value="TRIAGED">已分诊</option>
          <option value="IN_PROGRESS">处理中</option>
          <option value="WAITING_CUSTOMER">等待客户</option>
          <option value="RESOLVED">已解决</option>
          <option value="CLOSED">已关闭</option>
          <option value="REOPENED">已重开</option>
        </select>
      </label>
      <label v-else class="filter-control">
        会话筛选
        <select
          v-model="conversationStateFilter"
          :disabled="conversationsLoading"
          aria-label="按会话状态筛选"
          @change="loadConversations(false)"
        >
          <option value="">全部状态</option>
          <option value="OPEN">已打开</option>
          <option value="WAITING_AGENT">等待坐席</option>
          <option value="WAITING_CUSTOMER">等待客户</option>
          <option value="CLOSED">已关闭</option>
        </select>
      </label>
    </section>

    <section v-if="activeModule === 'tickets'" class="metrics" aria-label="工单指标">
      <article><span>当前队列</span><strong>{{ tickets.length }}</strong><small>当前筛选结果</small></article>
      <article><span>活跃工单</span><strong>{{ activeCount }}</strong><small>仍需坐席处理</small></article>
      <article><span>紧急事项</span><strong>{{ urgentCount }}</strong><small>优先级为 URGENT</small></article>
      <article><span>等待客户</span><strong>{{ waitingCount }}</strong><small>需要客户补充信息</small></article>
    </section>
    <section v-else class="metrics" aria-label="会话指标">
      <article><span>当前会话</span><strong>{{ conversations.length }}</strong><small>当前筛选结果</small></article>
      <article><span>未关闭</span><strong>{{ openConversationCount }}</strong><small>仍在服务流程中</small></article>
      <article><span>等待坐席</span><strong>{{ waitingAgentCount }}</strong><small>优先响应客户</small></article>
      <article><span>等待客户</span><strong>{{ waitingCustomerConversationCount }}</strong><small>已发送公开回复</small></article>
    </section>

    <div v-if="error" class="error-banner" role="alert">
      <span>{{ error }}</span>
      <div>
        <button type="button" @click="initialize">重新加载</button>
        <button type="button" aria-label="关闭错误提示" @click="error = ''">关闭</button>
      </div>
    </div>
    <div v-if="notice" class="success-banner" role="status">
      <span>{{ notice }}</span>
      <button type="button" aria-label="关闭成功提示" @click="notice = ''">关闭</button>
    </div>

    <section v-if="activeModule === 'tickets'" class="workspace-grid">
      <TicketBoard
        :tickets="tickets"
        :selected-id="selected?.id"
        :loading="ticketsLoading"
        @select="selectTicket"
      />
      <TicketDetailPanel
        :ticket="selected"
        :loading="detailLoading"
        :busy="busy"
        :ai-loading="aiLoading"
        :suggestion="suggestion"
        @transition="transition"
        @assign="assign"
        @suggest="generateSuggestion"
      />
    </section>
    <section v-else class="workspace-grid">
      <ConversationBoard
        :conversations="conversations"
        :selected-id="selectedConversation?.id"
        :loading="conversationsLoading"
        @select="selectConversation"
      />
      <ConversationDetailPanel
        :conversation="selectedConversation"
        :loading="conversationDetailLoading"
        :busy="busy"
        :include-internal="includeInternal"
        :message-success-token="conversationMessageSuccessToken"
        :ticket-success-token="linkedTicketSuccessToken"
        @toggle-internal="toggleInternalMessages"
        @send-message="sendConversationMessage"
        @transition="transitionConversation"
        @create-ticket="createLinkedTicket"
      />
    </section>

    <CreateTicketForm
      v-if="createOpen"
      :customers="customers"
      :saving="busy"
      @submit="createTicket"
      @cancel="createOpen = false"
    />
    <CreateConversationForm
      v-if="conversationCreateOpen"
      :customers="customers"
      :saving="busy"
      @submit="createConversation"
      @cancel="conversationCreateOpen = false"
    />
  </main>
</template>
