import { afterEach, describe, expect, it, vi } from 'vitest'
import {
  buildQuestionQuery,
  createInterview,
  fetchQuestions,
  fetchSourceSnapshot,
  fetchXiaolinCoverage,
  normalizeQuestion,
  saveProgress,
} from './api'

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('题库 API 参数与规范化', () => {
  it('使用后端真实字段生成筛选参数', () => {
    const query = new URLSearchParams(
      buildQuestionQuery({
        query: ' RAG 评测 ',
        module: '09',
        level: '高级',
        kind: '场景题',
        origin: 'curated-2026',
        role: '性能测试',
        questionIds: ['core-09-01', 'core-09-02'],
        page: 2,
        pageSize: 12,
      }),
    )

    expect(query.get('q')).toBe('RAG 评测')
    expect(query.get('module_id')).toBe('09')
    expect(query.get('level')).toBe('高级')
    expect(query.get('kind')).toBe('场景题')
    expect(query.get('origin')).toBe('curated-2026')
    expect(query.get('role')).toBe('性能测试')
    expect(query.getAll('question_id')).toEqual(['core-09-01', 'core-09-02'])
    expect(query.get('page')).toBe('2')
    expect(query.has('module')).toBe(false)
  })

  it('把结构化合成场景转成可读文本而不是对象字符串', () => {
    const question = normalizeQuestion({
      id: 'ai-1',
      title: '如何定位 RAG 错答？',
      scenario: {
        background: '合成知识库给出错误答案。',
        data: '已保存召回文档与分数。',
        task: '设计最小定位实验。',
        synthetic: true,
      },
    })

    expect(question.scenario).toContain('背景：合成知识库给出错误答案。')
    expect(question.scenario).toContain('任务：设计最小定位实验。')
    expect(question.scenario).not.toContain('[object Object]')
  })

  it('列表请求显式获取答案，但界面仍由用户手动揭示', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          items: [{ id: 'core-1', title: '测试目的', answer: '提供风险信息' }],
          total: 1,
          page: 1,
          page_size: 12,
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      ),
    )
    vi.stubGlobal('fetch', fetchMock)

    const result = await fetchQuestions({
      query: '',
      module: '',
      level: '',
      kind: '',
      origin: '',
      role: '',
      page: 1,
      pageSize: 12,
    })

    expect(String(fetchMock.mock.calls[0][0])).toContain('include_answer=true')
    expect(result.items[0].answer).toBe('提供风险信息')
  })

  it('读取并规范化仓库内的来源快照，不请求原始网站', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          source_id: 'xiaolin/network',
          title: '网络面试题本地快照',
          platform: '小林 Coding',
          original_url: 'https://xiaolincoding.com/network/',
          captured_at: '2026-07-29T09:30:00+08:00',
          content_format: 'markdown',
          content: '# TCP\\n\\n这是保存在仓库中的正文。',
          content_hash: 'sha256:abc123',
          local_path: 'data/source-snapshots/xiaolin-network.md',
          char_count: 24,
          copyright_notice: '仅用于个人学习与事实核验。',
          assets: [
            {
              asset_id: 'tcp-flow',
              content_type: 'image/png',
              alt_text: 'TCP 状态迁移图',
              caption: '图 1：TCP 状态迁移',
              byte_count: 2048,
              sha256: 'sha256:image123',
              url: 'https://untrusted.example/image.png',
            },
          ],
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      ),
    )
    vi.stubGlobal('fetch', fetchMock)

    const result = await fetchSourceSnapshot('xiaolin/network')

    expect(String(fetchMock.mock.calls[0][0])).toBe(
      '/api/v1/sources/xiaolin%2Fnetwork/snapshot',
    )
    expect(result).toMatchObject({
      sourceId: 'xiaolin/network',
      kind: '小林 Coding',
      contentFormat: 'markdown',
      originalUrl: 'https://xiaolincoding.com/network/',
      localPath: 'data/source-snapshots/xiaolin-network.md',
      contentHash: 'sha256:abc123',
    })
    expect(result.content).toContain('保存在仓库中的正文')
    expect(result.assets).toEqual([
      {
        assetId: 'tcp-flow',
        mediaType: 'image/png',
        alt: 'TCP 状态迁移图',
        caption: '图 1：TCP 状态迁移',
        byteCount: 2048,
        contentHash: 'sha256:image123',
      },
    ])
  })

  it('把 FastAPI 结构化快照错误转成站内可读提示', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          detail: {
            code: 'robots_denied',
            message: '来源站点 robots.txt 不允许自动抓取',
          },
        }),
        { status: 403, headers: { 'Content-Type': 'application/json' } },
      ),
    )
    vi.stubGlobal('fetch', fetchMock)

    const error = await fetchSourceSnapshot('blocked-source').catch(
      (reason: unknown) => reason,
    )
    expect(error).toMatchObject({
      message: '来源站点 robots.txt 不允许自动抓取（robots_denied）',
      status: 403,
    })
    expect((error as Error).message).not.toContain('[object Object]')
  })

  it.each([
    {
      status: 404,
      code: 'snapshot_not_found',
      message: '该来源尚未生成本地快照',
    },
    {
      status: 409,
      code: 'snapshot_unavailable',
      message: '该来源快照当前不可用',
    },
  ])(
    '保留 FastAPI $status 快照状态和结构化原因',
    async ({ status, code, message }) => {
      vi.stubGlobal(
        'fetch',
        vi.fn().mockResolvedValue(
          new Response(
            JSON.stringify({
              detail: { status, code, message },
            }),
            {
              status,
              headers: { 'Content-Type': 'application/json' },
            },
          ),
        ),
      )

      const error = await fetchSourceSnapshot('source-state').catch(
        (reason: unknown) => reason,
      )
      expect(error).toMatchObject({
        message: `${message}（${code}）`,
        status,
      })
    },
  )

  it('按学习者和题目保存后端支持的进度字段', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          learner_id: 'local-learner',
          question_id: 'core-1',
          status: 'review',
          favorite: true,
          note: '补充边界',
          score: 2,
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      ),
    )
    vi.stubGlobal('fetch', fetchMock)

    const saved = await saveProgress('local-learner', {
      questionId: 'core-1',
      favorite: true,
      wrong: true,
      mastery: 'learning',
      note: '补充边界',
      selfScore: 2,
    })

    expect(String(fetchMock.mock.calls[0][0])).toContain(
      '/progress/local-learner/core-1',
    )
    const init = fetchMock.mock.calls[0][1] as RequestInit
    expect(JSON.parse(String(init.body))).toEqual({
      favorite: true,
      status: 'review',
      note: '补充边界',
      score: 2,
    })
    expect(saved.wrong).toBe(true)
  })

  it('模拟面试把目标岗位传给后端做角色题目过滤', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          id: 'session-performance',
          role: '性能测试工程师',
          seed: 29,
          questions: [],
        }),
        { status: 201, headers: { 'Content-Type': 'application/json' } },
      ),
    )
    vi.stubGlobal('fetch', fetchMock)

    await createInterview({
      role: '性能测试工程师',
      difficulty: '综合',
      count: 8,
      seed: 29,
    })

    const init = fetchMock.mock.calls[0][1] as RequestInit
    expect(JSON.parse(String(init.body))).toMatchObject({
      role: '性能测试工程师',
      template_id: 'standard',
      count: 8,
      seed: 29,
    })
  })

  it('读取小林 Coding 覆盖时保留标称题量与实际题量', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          document_count: 21,
          mapped_document_count: 21,
          question_reference_count: 184,
          declared_question_count: 1143,
          observed_question_count: 1111,
          unmapped_documents: [],
          documents: [
            {
              document_id: 'xiaolincoding-performance-testing',
              title: '性能测试面试题',
              module: '直接题库 · 性能测试',
              url: 'https://xiaolincoding.com/interview/performance_testing.html',
              source_chars: 25298,
              coverage_mode: 'direct-bank-reviewed',
              declared_question_count: 105,
              observed_question_count: 100,
              question_ids: ['xiaolin-performance-jmeter-distributed-validity'],
              quality_notes: ['固定阈值已经改成基于证据的判断。'],
            },
          ],
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      ),
    )
    vi.stubGlobal('fetch', fetchMock)

    const result = await fetchXiaolinCoverage()

    expect(String(fetchMock.mock.calls[0][0])).toBe(
      '/api/quality/xiaolincoding-coverage',
    )
    expect(result.documentCount).toBe(21)
    expect(result.declaredQuestionCount).toBe(1143)
    expect(result.observedQuestionCount).toBe(1111)
    expect(result.documents[0]).toMatchObject({
      documentId: 'xiaolincoding-performance-testing',
      snapshotId: 'xiaolincoding-performance-testing',
      declaredQuestionCount: 105,
      observedQuestionCount: 100,
    })
  })
})
