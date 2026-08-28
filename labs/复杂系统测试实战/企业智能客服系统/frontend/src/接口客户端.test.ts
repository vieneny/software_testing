import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, createApi, createIdempotencyKey } from './api'

describe('客服 Java API 客户端', () => {
  afterEach(() => {
    vi.useRealTimers()
  })

  it('按 Java 契约发送租户、请求 ID 和筛选参数', async () => {
    const fetchImpl = vi.fn(
      async (_input: RequestInfo | URL, _init?: RequestInit) =>
        new Response(
          JSON.stringify({
            content: [],
            totalElements: 0,
            totalPages: 0,
            number: 0,
            size: 50,
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        ),
    )
    const client = createApi({
      baseUrl: 'http://127.0.0.1:8080/',
      tenantCode: 'demo',
      fetchImpl,
      requestIdFactory: () => 'web-contract-001',
    })

    await client.listTickets('IN_PROGRESS')

    expect(fetchImpl).toHaveBeenCalledOnce()
    const [url, init] = fetchImpl.mock.calls[0]
    expect(url).toBe(
      'http://127.0.0.1:8080/api/v1/tickets?size=50&status=IN_PROGRESS',
    )
    const headers = new Headers(init?.headers)
    expect(headers.get('X-Tenant-Code')).toBe('demo')
    expect(headers.get('X-Request-ID')).toBe('web-contract-001')
    expect(headers.get('Content-Type')).toBeNull()
  })

  it('显示 Java 字段错误和可追踪请求 ID', async () => {
    const fetchImpl = vi.fn(async () =>
      new Response(
        JSON.stringify({
          code: 'VALIDATION_FAILED',
          message: '请求参数校验失败',
          request_id: 'java-error-001',
          fieldErrors: { title: '不能为空' },
        }),
        {
          status: 400,
          headers: {
            'Content-Type': 'application/json',
            'X-Request-ID': 'java-error-001',
          },
        },
      ),
    )
    const client = createApi({ fetchImpl })

    const error = await client.customers().catch((reason: unknown) => reason)

    expect(error).toBeInstanceOf(ApiError)
    expect(error).toMatchObject({
      status: 400,
      code: 'VALIDATION_FAILED',
      requestId: 'java-error-001',
    })
    expect((error as Error).message).toContain('title：不能为空')
    expect((error as Error).message).toContain('请求 ID：java-error-001')
  })

  it('拒绝成功状态下的非 JSON 或空响应', async () => {
    const malformed = createApi({
      fetchImpl: vi.fn(async () => new Response('<html>bad gateway</html>')),
    })
    const empty = createApi({
      fetchImpl: vi.fn(async () => new Response(null, { status: 200 })),
    })

    await expect(malformed.customers()).rejects.toThrow('无法解析')
    await expect(empty.customers()).rejects.toThrow('空响应')
  })

  it('在超时后主动取消请求并返回可读错误', async () => {
    vi.useFakeTimers()
    const fetchImpl = vi.fn(
      async (_url: RequestInfo | URL, init?: RequestInit): Promise<Response> =>
        new Promise((_, reject) => {
          init?.signal?.addEventListener('abort', () => {
            reject(new DOMException('aborted', 'AbortError'))
          })
        }),
    )
    const client = createApi({ fetchImpl, timeoutMs: 100 })
    const assertion = expect(client.customers()).rejects.toThrow('请求超过 100 毫秒')

    await vi.advanceTimersByTimeAsync(101)
    await assertion
  })

  it('编码路径参数并发送与 Java DTO 一致的状态流转字段', async () => {
    const fetchImpl = vi.fn(
      async (_input: RequestInfo | URL, _init?: RequestInit) =>
        new Response(JSON.stringify({ id: 'ignored-by-this-contract-test' }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }),
    )
    const client = createApi({ fetchImpl })

    await client.transitionTicket('SYNTHETIC/001', 'IN_PROGRESS', 3)

    const [url, init] = fetchImpl.mock.calls[0]
    expect(url).toBe('/api/v1/tickets/SYNTHETIC%2F001/transitions')
    expect(JSON.parse(String(init?.body))).toEqual({
      expectedVersion: 3,
      targetStatus: 'IN_PROGRESS',
      operatorName: '学习坐席',
      note: '由演示工作台执行状态流转',
    })
  })

  it('会话详情默认显式使用客户视图，不请求内部备注', async () => {
    const fetchImpl = vi.fn(
      async (_input: RequestInfo | URL, _init?: RequestInit) =>
        new Response(JSON.stringify({ messages: [] }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }),
    )
    const client = createApi({ fetchImpl })

    await client.conversationDetail(42)

    expect(fetchImpl.mock.calls[0][0]).toBe(
      '/api/v1/conversations/42?includeInternal=false',
    )
  })

  it('为会话消息发送合法幂等键和 expectedVersion', async () => {
    const fetchImpl = vi.fn(
      async (_input: RequestInfo | URL, _init?: RequestInit) =>
        new Response(JSON.stringify({ id: 42, messages: [] }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }),
    )
    const client = createApi({ fetchImpl })
    const key = createIdempotencyKey('conversation-message')

    await client.sendConversationMessage(
      42,
      {
        expectedVersion: 7,
        senderType: 'AGENT',
        visibility: 'INTERNAL',
        authorName: '学习坐席',
        content: '完全合成的内部备注。',
      },
      key,
      true,
    )

    expect(key).toMatch(/^[A-Za-z0-9._:-]{1,128}$/)
    const [url, init] = fetchImpl.mock.calls[0]
    expect(url).toBe('/api/v1/conversations/42/messages?includeInternal=true')
    expect(new Headers(init?.headers).get('Idempotency-Key')).toBe(key)
    expect(JSON.parse(String(init?.body))).toEqual({
      expectedVersion: 7,
      senderType: 'AGENT',
      visibility: 'INTERNAL',
      authorName: '学习坐席',
      content: '完全合成的内部备注。',
    })
  })

  it('关闭会话时同时发送幂等键与当前版本', async () => {
    const fetchImpl = vi.fn(
      async (_input: RequestInfo | URL, _init?: RequestInit) =>
        new Response(JSON.stringify({ id: 42, messages: [] }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }),
    )
    const client = createApi({ fetchImpl })
    const key = createIdempotencyKey('conversation-transition')

    await client.transitionConversation(
      42,
      {
        expectedVersion: 8,
        targetState: 'CLOSED',
        operatorName: '学习坐席',
        note: '公开合成场景完成',
      },
      key,
      true,
    )

    const [url, init] = fetchImpl.mock.calls[0]
    expect(url).toBe('/api/v1/conversations/42/transitions?includeInternal=true')
    expect(new Headers(init?.headers).get('Idempotency-Key')).toBe(key)
    expect(JSON.parse(String(init?.body))).toMatchObject({
      expectedVersion: 8,
      targetState: 'CLOSED',
    })
  })

  it('从会话创建工单时保留 conversationId 和幂等键', async () => {
    const fetchImpl = vi.fn(
      async (_input: RequestInfo | URL, _init?: RequestInit) =>
        new Response(JSON.stringify({ id: 'TICKET-SYNTHETIC-001' }), {
          status: 201,
          headers: { 'Content-Type': 'application/json' },
        }),
    )
    const client = createApi({ fetchImpl })
    const key = createIdempotencyKey('ticket-from-conversation')

    await client.createTicket(
      {
        customerId: 7,
        conversationId: 42,
        title: '合成会话升级工单',
        description: '仅用于公开学习。',
        category: 'ACCOUNT',
        priority: 'HIGH',
      },
      key,
    )

    const [url, init] = fetchImpl.mock.calls[0]
    expect(url).toBe('/api/v1/tickets')
    expect(new Headers(init?.headers).get('Idempotency-Key')).toBe(key)
    expect(JSON.parse(String(init?.body))).toMatchObject({
      customerId: 7,
      conversationId: 42,
      priority: 'HIGH',
    })
  })
})
