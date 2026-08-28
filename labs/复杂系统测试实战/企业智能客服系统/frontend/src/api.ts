import type {
  AiSuggestion,
  ConversationDetail,
  ConversationPage,
  ConversationState,
  CreateConversationPayload,
  CreateTicketPayload,
  Customer,
  SendConversationMessagePayload,
  TicketDetail,
  TicketPage,
  TicketStatus,
  TransitionConversationPayload,
} from './types'

const API_V1 = '/api/v1'
const IDEMPOTENCY_KEY_PATTERN = /^[A-Za-z0-9._:-]{1,128}$/

declare const idempotencyKeyBrand: unique symbol
export type IdempotencyKey = string & { readonly [idempotencyKeyBrand]: true }

export function createIdempotencyKey(scope: string): IdempotencyKey {
  const safeScope = scope.replace(/[^A-Za-z0-9._:-]/g, '-').slice(0, 40) || 'operation'
  const uniquePart = defaultRequestId().replace(/[^A-Za-z0-9._:-]/g, '-')
  const key = `web.${safeScope}:${uniquePart}`.slice(0, 128)
  if (!IDEMPOTENCY_KEY_PATTERN.test(key)) {
    throw new Error('无法生成合法的 Idempotency-Key')
  }
  return key as IdempotencyKey
}

interface ApiErrorBody {
  code?: unknown
  message?: unknown
  request_id?: unknown
  fieldErrors?: unknown
}

interface ApiClientOptions {
  baseUrl?: string
  tenantCode?: string
  timeoutMs?: number
  fetchImpl?: typeof fetch
  requestIdFactory?: () => string
}

export class ApiError extends Error {
  readonly status: number
  readonly code?: string
  readonly requestId?: string

  constructor(
    message: string,
    options: { status: number; code?: string; requestId?: string },
  ) {
    super(message)
    this.name = 'ApiError'
    this.status = options.status
    this.code = options.code
    this.requestId = options.requestId
  }
}

function stringValue(value: unknown): string | undefined {
  return typeof value === 'string' && value.trim() ? value.trim() : undefined
}

function fieldMessages(value: unknown): string[] {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return []
  return Object.entries(value)
    .map(([field, message]) => {
      const readable = stringValue(message)
      return readable ? `${field}：${readable}` : undefined
    })
    .filter((item): item is string => Boolean(item))
}

function defaultRequestId(): string {
  if (globalThis.crypto?.randomUUID) return globalThis.crypto.randomUUID()
  return `web-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function normalizeBaseUrl(value: string): string {
  return value.trim().replace(/\/+$/, '')
}

function idempotencyHeaders(key: IdempotencyKey): HeadersInit {
  if (!IDEMPOTENCY_KEY_PATTERN.test(key)) {
    throw new Error('Idempotency-Key 格式不符合 Java 接口契约')
  }
  return { 'Idempotency-Key': key }
}

export function createApi(options: ApiClientOptions = {}) {
  const baseUrl = normalizeBaseUrl(options.baseUrl ?? import.meta.env.VITE_API_BASE_URL ?? '')
  const tenantCode = (options.tenantCode ?? import.meta.env.VITE_TENANT_CODE ?? 'demo').trim()
  const timeoutMs = options.timeoutMs ?? 15_000
  const fetchImpl = options.fetchImpl ?? globalThis.fetch
  const requestIdFactory = options.requestIdFactory ?? defaultRequestId

  if (!fetchImpl) throw new Error('当前运行环境不支持 Fetch API')
  if (!tenantCode) throw new Error('VITE_TENANT_CODE 不能为空')
  if (!Number.isFinite(timeoutMs) || timeoutMs < 100 || timeoutMs > 60_000) {
    throw new Error('前端请求超时必须在 100 到 60000 毫秒之间')
  }

  async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
    const controller = new AbortController()
    let timedOut = false
    const timeout = globalThis.setTimeout(() => {
      timedOut = true
      controller.abort()
    }, timeoutMs)
    const upstreamSignal = init.signal
    const abortFromUpstream = () => controller.abort(upstreamSignal?.reason)
    upstreamSignal?.addEventListener('abort', abortFromUpstream, { once: true })
    if (upstreamSignal?.aborted) abortFromUpstream()

    const headers = new Headers(init.headers)
    headers.set('Accept', 'application/json')
    headers.set('X-Tenant-Code', tenantCode)
    headers.set('X-Request-ID', requestIdFactory())
    if (init.body !== undefined) headers.set('Content-Type', 'application/json')

    try {
      const response = await fetchImpl(`${baseUrl}${path}`, {
        ...init,
        headers,
        signal: controller.signal,
      })
      const text = await response.text()
      let body: unknown
      if (text) {
        try {
          body = JSON.parse(text)
        } catch {
          throw new ApiError(
            response.ok ? '服务返回了无法解析的数据' : `请求失败（${response.status}）`,
            {
              status: response.status,
              requestId: response.headers.get('X-Request-ID') ?? undefined,
            },
          )
        }
      }

      if (!response.ok) {
        const error =
          body && typeof body === 'object' && !Array.isArray(body)
            ? (body as ApiErrorBody)
            : {}
        const requestId =
          stringValue(error.request_id) ??
          response.headers.get('X-Request-ID') ??
          undefined
        const details = fieldMessages(error.fieldErrors)
        throw new ApiError(
          [
            stringValue(error.message) ?? `请求失败（${response.status}）`,
            ...details,
            requestId ? `请求 ID：${requestId}` : undefined,
          ]
            .filter(Boolean)
            .join('；'),
          {
            status: response.status,
            code: stringValue(error.code),
            requestId,
          },
        )
      }
      if (body === undefined) {
        throw new ApiError('服务返回了空响应', {
          status: response.status,
          requestId: response.headers.get('X-Request-ID') ?? undefined,
        })
      }
      return body as T
    } catch (reason) {
      if (timedOut) {
        throw new ApiError(`请求超过 ${timeoutMs} 毫秒，请稍后重试`, {
          status: 0,
        })
      }
      throw reason
    } finally {
      globalThis.clearTimeout(timeout)
      upstreamSignal?.removeEventListener('abort', abortFromUpstream)
    }
  }

  return {
    listTickets(status?: TicketStatus, signal?: AbortSignal): Promise<TicketPage> {
      const query = new URLSearchParams({ size: '50' })
      if (status) query.set('status', status)
      return request(`${API_V1}/tickets?${query}`, { signal })
    },

    ticketDetail(ticketId: string, signal?: AbortSignal): Promise<TicketDetail> {
      return request(`${API_V1}/tickets/${encodeURIComponent(ticketId)}`, { signal })
    },

    customers(signal?: AbortSignal): Promise<Customer[]> {
      return request(`${API_V1}/customers`, { signal })
    },

    createTicket(
      payload: CreateTicketPayload,
      idempotencyKey: IdempotencyKey,
    ): Promise<TicketDetail> {
      return request(`${API_V1}/tickets`, {
        method: 'POST',
        headers: idempotencyHeaders(idempotencyKey),
        body: JSON.stringify(payload),
      })
    },

    transitionTicket(
      ticketId: string,
      targetStatus: TicketStatus,
      expectedVersion: number,
    ): Promise<TicketDetail> {
      return request(`${API_V1}/tickets/${encodeURIComponent(ticketId)}/transitions`, {
        method: 'POST',
        body: JSON.stringify({
          expectedVersion,
          targetStatus,
          operatorName: '学习坐席',
          note: '由演示工作台执行状态流转',
        }),
      })
    },

    assignTicket(
      ticketId: string,
      assignedAgent: string,
      expectedVersion: number,
    ): Promise<TicketDetail> {
      return request(`${API_V1}/tickets/${encodeURIComponent(ticketId)}/assignments`, {
        method: 'POST',
        body: JSON.stringify({
          expectedVersion,
          assignedAgent,
          operatorName: '学习管理员',
          reason: '演示手动分配',
        }),
      })
    },

    aiSuggestion(ticketId: string): Promise<AiSuggestion> {
      return request(`${API_V1}/tickets/${encodeURIComponent(ticketId)}/ai-suggestions`, {
        method: 'POST',
        body: JSON.stringify({ tone: 'professional', language: 'zh-CN' }),
      })
    },

    listConversations(
      state?: ConversationState,
      signal?: AbortSignal,
    ): Promise<ConversationPage> {
      const query = new URLSearchParams({ size: '50' })
      if (state) query.set('state', state)
      return request(`${API_V1}/conversations?${query}`, { signal })
    },

    conversationDetail(
      conversationId: number,
      includeInternal = false,
      signal?: AbortSignal,
    ): Promise<ConversationDetail> {
      const query = new URLSearchParams({
        includeInternal: String(includeInternal),
      })
      return request(
        `${API_V1}/conversations/${encodeURIComponent(conversationId)}?${query}`,
        { signal },
      )
    },

    createConversation(
      payload: CreateConversationPayload,
      idempotencyKey: IdempotencyKey,
    ): Promise<ConversationDetail> {
      return request(`${API_V1}/conversations`, {
        method: 'POST',
        headers: idempotencyHeaders(idempotencyKey),
        body: JSON.stringify(payload),
      })
    },

    sendConversationMessage(
      conversationId: number,
      payload: SendConversationMessagePayload,
      idempotencyKey: IdempotencyKey,
      includeInternal = false,
    ): Promise<ConversationDetail> {
      const query = new URLSearchParams({
        includeInternal: String(includeInternal),
      })
      return request(
        `${API_V1}/conversations/${encodeURIComponent(conversationId)}/messages?${query}`,
        {
          method: 'POST',
          headers: idempotencyHeaders(idempotencyKey),
          body: JSON.stringify(payload),
        },
      )
    },

    transitionConversation(
      conversationId: number,
      payload: TransitionConversationPayload,
      idempotencyKey: IdempotencyKey,
      includeInternal = false,
    ): Promise<ConversationDetail> {
      const query = new URLSearchParams({
        includeInternal: String(includeInternal),
      })
      return request(
        `${API_V1}/conversations/${encodeURIComponent(conversationId)}/transitions?${query}`,
        {
          method: 'POST',
          headers: idempotencyHeaders(idempotencyKey),
          body: JSON.stringify(payload),
        },
      )
    },
  }
}

export const api = createApi()
