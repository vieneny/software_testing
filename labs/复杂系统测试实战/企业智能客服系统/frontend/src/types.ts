export type TicketStatus =
  | 'NEW'
  | 'TRIAGED'
  | 'IN_PROGRESS'
  | 'WAITING_CUSTOMER'
  | 'RESOLVED'
  | 'CLOSED'
  | 'REOPENED'

export type TicketPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT'

export interface TicketSummary {
  id: string
  title: string
  category: string
  priority: TicketPriority
  status: TicketStatus
  assignedAgent?: string
  dueAt: string
  createdAt: string
  updatedAt: string
  version: number
}

export interface StatusHistory {
  fromStatus: TicketStatus
  toStatus: TicketStatus
  operatorName: string
  note?: string
  occurredAt: string
}

export interface TicketDetail extends TicketSummary {
  customerId: number
  customerName: string
  customerLevel: string
  conversationId?: number
  description: string
  statusHistory: StatusHistory[]
}

export interface Customer {
  id: number
  displayName: string
  email: string
  customerLevel: string
}

export interface TicketPage {
  content: TicketSummary[]
  totalElements: number
  totalPages: number
  number: number
  size: number
}

export interface CreateTicketPayload {
  customerId: number
  conversationId?: number
  title: string
  description: string
  category: string
  priority: TicketPriority
}

export type ConversationChannel = 'WEB' | 'APP' | 'EMAIL' | 'PHONE' | 'WECHAT'
export type ConversationState = 'OPEN' | 'WAITING_AGENT' | 'WAITING_CUSTOMER' | 'CLOSED'
export type MessageSenderType = 'CUSTOMER' | 'AGENT' | 'SYSTEM'
export type MessageVisibility = 'CUSTOMER' | 'INTERNAL'

export interface ConversationSummary {
  id: number
  customerId: number
  channel: ConversationChannel
  subject: string
  state: ConversationState
  startedAt: string
  lastMessageAt: string
  updatedAt: string
  version: number
}

export interface ConversationMessage {
  id: number
  sequence: number
  senderType: MessageSenderType
  visibility: MessageVisibility
  authorName: string
  content: string
  createdAt: string
}

export interface ConversationDetail extends ConversationSummary {
  customerName: string
  customerLevel: string
  createdAt: string
  messages: ConversationMessage[]
  linkedTicketIds: string[]
}

export interface ConversationPage {
  content: ConversationSummary[]
  totalElements: number
  totalPages: number
  number: number
  size: number
}

export interface CreateConversationPayload {
  customerId: number
  channel: ConversationChannel
  subject: string
  initialMessage: string
}

export interface SendConversationMessagePayload {
  expectedVersion: number
  senderType: Exclude<MessageSenderType, 'SYSTEM'>
  visibility: MessageVisibility
  authorName: string
  content: string
}

export interface TransitionConversationPayload {
  expectedVersion: number
  targetState: Extract<ConversationState, 'OPEN' | 'CLOSED'>
  operatorName: string
  note?: string
}

export interface AiSuggestion {
  summary: string
  suggestedReply: string
  suggestedCategory?: string
  suggestedPriority?: string
  confidence: number
  riskFlags: string[]
  knowledgeReferences: string[]
  suggestedActions: string[]
  mustVerify: string[]
  degraded: boolean
  degradationReason?: string
}
