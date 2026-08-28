import type {
  InterviewRequest,
  InterviewSession,
  LegacyCoverageSummary,
  Meta,
  ProgressRecord,
  Question,
  QuestionFilters,
  QuestionPage,
  Source,
  SourceSnapshot,
  SourceCoverage,
} from './types'

const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? '/api/v1').replace(/\/$/, '')
const QUALITY_API_BASE = API_BASE.endsWith('/v1') ? API_BASE.slice(0, -3) : API_BASE

export class ApiError extends Error {
  status: number

  constructor(message: string, status = 0) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

function asString(value: unknown, fallback = ''): string {
  if (value === null || value === undefined) return fallback
  if (typeof value === 'string') return value
  if (Array.isArray(value)) return value.map((item) => asString(item)).filter(Boolean).join('\n')
  return String(value)
}

function asStringList(value: unknown): string[] {
  if (Array.isArray(value)) {
    return value.map((item) => asString(item).trim()).filter(Boolean)
  }
  const text = asString(value).trim()
  if (!text) return []
  return text
    .split(/\n|；|(?<!\d);/)
    .map((item) => item.replace(/^[-*•\d.)、\s]+/, '').trim())
    .filter(Boolean)
}

function recordOf(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? (value as Record<string, unknown>) : {}
}

function asApiErrorMessage(body: unknown): string {
  const item = recordOf(body)
  const detail = item.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((entry) => {
        if (typeof entry === 'string') return entry
        const detailItem = recordOf(entry)
        return asString(detailItem.message ?? detailItem.msg ?? detailItem.code)
      })
      .filter(Boolean)
      .join('；')
  }
  const detailItem = recordOf(detail)
  const message = asString(detailItem.message ?? detailItem.msg)
  const code = asString(detailItem.code)
  if (message && code) return `${message}（${code}）`
  if (message || code) return message || code
  return asString(item.message)
}

function asScenario(value: unknown): string {
  if (typeof value === 'string') return value
  const item = recordOf(value)
  const parts = [
    item.background ? `背景：${asString(item.background)}` : '',
    item.data ? `已知数据：${asString(item.data)}` : '',
    item.task ? `任务：${asString(item.task)}` : '',
    item.prompt ? `题目：${asString(item.prompt)}` : '',
  ].filter(Boolean)
  return parts.join('\n')
}

export function normalizeQuestion(raw: unknown): Question {
  const item = recordOf(raw)
  return {
    id: asString(item.id ?? item.question_id ?? item.slug),
    moduleId: asString(item.module_id ?? item.moduleId ?? item.module),
    moduleName: asString(item.module_name ?? item.moduleName ?? item.category ?? item.module, '未分类'),
    title: asString(item.title ?? item.question ?? item.name, '未命名题目'),
    level: asString(item.level ?? item.difficulty, '基础'),
    kind: asString(item.kind ?? item.type ?? item.question_type, '知识题'),
    origin: asString(item.origin ?? item.source_origin, '课程整理'),
    roles: asStringList(item.roles ?? item.role),
    tags: asStringList(item.tags),
    focus: asString(item.focus ?? item.key_points ?? item.interview_focus),
    answer: asString(item.answer ?? item.reference_answer),
    explanation: asString(item.explanation ?? item.principle ?? item.practice),
    followups: asStringList(item.followups ?? item.follow_up ?? item.common_followups),
    pitfalls: asStringList(item.pitfalls ?? item.mistakes ?? item.common_mistakes),
    scenario: asScenario(item.scenario ?? item.mock_scenario),
    sourceIds: asStringList(item.source_ids ?? item.sourceIds ?? item.sources),
    relatedQuestionIds: asStringList(
      item.related_question_ids ?? item.relatedQuestionIds,
    ),
    deepeningRationale: asString(
      item.deepening_rationale ?? item.deepeningRationale,
    ),
    historicalReference: asString(
      item.historical_reference ??
        item.historicalReference ??
        item.historical_references,
    ),
    updatedAt: asString(item.updated_at ?? item.updatedAt),
  }
}

function normalizeProgress(raw: unknown): ProgressRecord {
  const item = recordOf(raw)
  const status = asString(item.mastery ?? item.status, 'not_started')
  return {
    questionId: asString(item.question_id ?? item.questionId ?? item.id),
    favorite: Boolean(item.favorite ?? item.starred),
    wrong: Boolean(item.wrong ?? item.needs_review) || status === 'review',
    mastery:
      status === 'mastered' ? 'mastered' : status === 'learning' || status === 'review' ? 'learning' : 'unseen',
    note: asString(item.note ?? item.notes),
    selfScore: Number(item.self_score ?? item.selfScore ?? item.score) || undefined,
    updatedAt: asString(item.updated_at ?? item.updatedAt),
  }
}

async function requestUrl<T>(url: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(url, {
      ...init,
      headers: {
        'Content-Type': 'application/json',
        ...(init?.headers ?? {}),
      },
    })
  } catch {
    throw new ApiError('无法连接题库服务，请确认 FastAPI 已启动。')
  }

  if (!response.ok) {
    let detail = ''
    try {
      const body = await response.json()
      detail = asApiErrorMessage(body)
    } catch {
      detail = ''
    }
    throw new ApiError(detail || `服务请求失败（HTTP ${response.status}）`, response.status)
  }
  if (response.status === 204) return undefined as T
  return (await response.json()) as T
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  return requestUrl<T>(`${API_BASE}${path}`, init)
}

export function buildQuestionQuery(filters: QuestionFilters): string {
  const params = new URLSearchParams()
  if (filters.query.trim()) params.set('q', filters.query.trim())
  if (filters.module) params.set('module_id', filters.module)
  if (filters.level) params.set('level', filters.level)
  if (filters.kind) params.set('kind', filters.kind)
  if (filters.origin) params.set('origin', filters.origin)
  if (filters.role) params.set('role', filters.role)
  filters.questionIds?.forEach((questionId) =>
    params.append('question_id', questionId),
  )
  params.set('page', String(filters.page))
  params.set('page_size', String(filters.pageSize))
  return params.toString()
}

export async function fetchMeta(): Promise<Meta> {
  const [rawMeta, rawModuleResponse] = await Promise.all([
    request<unknown>('/meta'),
    request<unknown>('/modules'),
  ])
  const raw = recordOf(rawMeta)
  const moduleResponse = recordOf(rawModuleResponse)
  const rawModules = Array.isArray(moduleResponse.items)
    ? moduleResponse.items
    : Array.isArray(raw.modules)
      ? raw.modules
      : []
  const statistics = recordOf(raw.statistics)
  const facets = recordOf(raw.facets)
  const facetLevels = recordOf(facets.levels)
  const facetKinds = recordOf(facets.kinds)
  const facetOrigins = recordOf(facets.origins)
  const facetRoles = recordOf(facets.roles)
  return {
    questionCount:
      Number(raw.question_count ?? raw.questionCount ?? raw.total_questions ?? statistics.total_questions) ||
      0,
    moduleCount: Number(raw.module_count ?? raw.moduleCount) || rawModules.length,
    modules: rawModules.map((module) => {
      const item = recordOf(module)
      return {
        id: asString(item.id ?? item.module_id ?? item.name),
        name: asString(item.name ?? item.module_name ?? item.id),
        count: Number(item.count ?? item.question_count) || 0,
      }
    }),
    levels: asStringList(raw.levels ?? raw.difficulties ?? Object.keys(facetLevels)),
    kinds: asStringList(raw.kinds ?? raw.types ?? Object.keys(facetKinds)),
    origins: asStringList(raw.origins ?? Object.keys(facetOrigins)),
    roles: asStringList(raw.roles ?? Object.keys(facetRoles)),
    lastUpdated: asString(raw.last_updated ?? raw.updated_at ?? raw.lastUpdated ?? raw.curated_updated_at),
  }
}

export async function fetchQuestions(filters: QuestionFilters): Promise<QuestionPage> {
  const query = buildQuestionQuery(filters)
  const raw = await request<unknown>(`/questions?${query}&include_answer=true`)
  const body = recordOf(raw)
  const rawItems = Array.isArray(raw) ? raw : Array.isArray(body.items) ? body.items : []
  return {
    items: rawItems.map(normalizeQuestion),
    total: Number(body.total ?? body.count) || rawItems.length,
    page: Number(body.page) || filters.page,
    pageSize: Number(body.page_size ?? body.pageSize) || filters.pageSize,
  }
}

export async function fetchQuestion(id: string): Promise<Question> {
  return normalizeQuestion(await request<unknown>(`/questions/${encodeURIComponent(id)}`))
}

export async function fetchSources(): Promise<Source[]> {
  const raw = await request<unknown>('/sources')
  const body = recordOf(raw)
  const items = Array.isArray(raw) ? raw : Array.isArray(body.items) ? body.items : []
  return items.map((source) => {
    const item = recordOf(source)
    return {
      id: asString(item.id),
      snapshotId: asString(item.snapshot_id ?? item.snapshotId ?? item.id),
      name: asString(item.name ?? item.title),
      url: asString(item.url),
      kind: asString(item.kind ?? item.type ?? item.platform, '公开资料'),
      accessedAt: asString(item.accessed_at ?? item.accessedAt),
      summary: asString(item.summary ?? item.description ?? item.usage),
    }
  })
}

export async function fetchSourceSnapshot(id: string): Promise<SourceSnapshot> {
  const raw = recordOf(
    await request<unknown>(
      `/sources/${encodeURIComponent(id)}/snapshot`,
    ),
  )
  const item = recordOf(raw.snapshot ?? raw)
  const content = asString(
    item.content ?? item.text ?? item.body ?? item.markdown,
  )
  const format = asString(
    item.content_format ?? item.contentFormat ?? item.format,
    'text',
  ).toLowerCase()
  const assets = Array.isArray(item.assets) ? item.assets : []
  return {
    sourceId: asString(
      item.source_id ?? item.sourceId ?? item.id,
      id,
    ),
    title: asString(item.title ?? item.name, id),
    kind: asString(
      item.kind ?? item.type ?? item.platform,
      '公开资料本地快照',
    ),
    originalUrl: asString(
      item.original_url ?? item.originalUrl ?? item.url,
    ),
    capturedAt: asString(
      item.captured_at ??
        item.capturedAt ??
        item.downloaded_at ??
        item.accessed_at,
    ),
    contentFormat:
      format === 'markdown' || format === 'html' ? format : 'text',
    content,
    contentHash: asString(
      item.content_hash ?? item.contentHash ?? item.sha256,
    ),
    localPath: asString(
      item.local_path ?? item.localPath ?? item.storage_path,
    ),
    charCount:
      Number(item.char_count ?? item.charCount ?? item.content_length) ||
      content.length,
    copyrightNotice: asString(
      item.copyright_notice ??
        item.copyrightNotice ??
        item.usage_notice,
      '本地快照仅用于个人学习、事实核验与来源追溯，请遵守原站许可及著作权要求。',
    ),
    assets: assets
      .map((asset) => {
        const assetItem = recordOf(asset)
        return {
          assetId: asString(
            assetItem.asset_id ?? assetItem.assetId ?? assetItem.id,
          ),
          mediaType: asString(
            assetItem.media_type ??
              assetItem.mediaType ??
              assetItem.content_type,
          ).toLowerCase(),
          alt: asString(
            assetItem.alt ?? assetItem.alt_text ?? assetItem.description,
          ),
          caption: asString(
            assetItem.caption ?? assetItem.title ?? assetItem.description,
          ),
          byteCount:
            Number(assetItem.byte_count ?? assetItem.byteCount) || 0,
          contentHash: asString(
            assetItem.content_hash ??
              assetItem.contentHash ??
              assetItem.sha256,
          ),
        }
      })
      .filter((asset) => asset.assetId),
  }
}

export async function fetchLegacyCoverage(): Promise<LegacyCoverageSummary> {
  const raw = recordOf(await request<unknown>('/legacy-coverage?page=1&page_size=5'))
  const statistics = recordOf(raw.statistics)
  const policy = recordOf(raw.policy)
  const total = Number(statistics.total) || 0
  const mappedToAnswer =
    Number(statistics.mapped_to_answer ?? statistics.mappedToAnswer) || 0
  return {
    total,
    mappedToAnswer,
    unmapped: Number(statistics.unmapped) || 0,
    isolatedAnswers:
      Number(statistics.isolated_answers ?? statistics.isolatedAnswers) || 0,
    coverageRate:
      Number(statistics.coverage_rate ?? statistics.coverageRate) ||
      (total ? mappedToAnswer / total : 0),
    purpose: asString(policy.purpose),
    answerHandling: asString(policy.answer_handling ?? policy.answerHandling),
  }
}

async function fetchSourceCoverage(path: string): Promise<SourceCoverage> {
  const raw = recordOf(
    await requestUrl<unknown>(`${QUALITY_API_BASE}/quality/${path}`),
  )
  const documents = Array.isArray(raw.documents) ? raw.documents : []
  const rawUnmappedDocuments =
    raw.unmapped_documents ?? raw.unmappedDocuments
  return {
    documentCount: Number(raw.document_count ?? raw.documentCount) || documents.length,
    mappedDocumentCount:
      Number(raw.mapped_document_count ?? raw.mappedDocumentCount) || 0,
    questionReferenceCount:
      Number(raw.question_reference_count ?? raw.questionReferenceCount) || 0,
    unmappedDocuments:
      Array.isArray(rawUnmappedDocuments)
        ? rawUnmappedDocuments.length
        : Number(rawUnmappedDocuments) || 0,
    declaredQuestionCount:
      Number(raw.declared_question_count ?? raw.declaredQuestionCount) || 0,
    observedQuestionCount:
      Number(raw.observed_question_count ?? raw.observedQuestionCount) || 0,
    documents: documents.map((document) => {
      const item = recordOf(document)
      return {
        documentId: asString(item.document_id ?? item.documentId ?? item.id),
        snapshotId: asString(
          item.snapshot_id ??
            item.snapshotId ??
            item.document_id ??
            item.documentId ??
            item.id,
        ),
        title: asString(item.title, '未命名来源文档'),
        module: asString(item.module, '未分类'),
        url: asString(item.url),
        sourceChars: Number(item.source_chars ?? item.sourceChars) || 0,
        coverageMode: asString(
          item.coverage_mode ?? item.coverageMode,
          '主题映射',
        ),
        questionIds: asStringList(item.question_ids ?? item.questionIds),
        qualityNotes: asStringList(item.quality_notes ?? item.qualityNotes),
        declaredQuestionCount:
          Number(
            item.declared_question_count ?? item.declaredQuestionCount,
          ) || 0,
        observedQuestionCount:
          Number(
            item.observed_question_count ?? item.observedQuestionCount,
          ) || 0,
      }
    }),
  }
}

export async function fetchXiaolinCoverage(): Promise<SourceCoverage> {
  return fetchSourceCoverage('xiaolincoding-coverage')
}

export async function fetchProgress(learnerId: string): Promise<ProgressRecord[]> {
  const raw = await request<unknown>(`/progress/${encodeURIComponent(learnerId)}`)
  const body = recordOf(raw)
  const items = Array.isArray(raw) ? raw : Array.isArray(body.items) ? body.items : []
  return items.map(normalizeProgress).filter((item) => item.questionId)
}

export async function saveProgress(
  learnerId: string,
  progress: ProgressRecord,
): Promise<ProgressRecord> {
  const body = {
    favorite: progress.favorite,
    status: progress.wrong
      ? 'review'
      : progress.mastery === 'unseen'
        ? 'not_started'
        : progress.mastery,
    note: progress.note,
    score: progress.selfScore,
  }
  const raw = await request<unknown>(
    `/progress/${encodeURIComponent(learnerId)}/${encodeURIComponent(progress.questionId)}`,
    {
      method: 'PUT',
      body: JSON.stringify(body),
    },
  )
  return normalizeProgress(raw)
}

export async function createInterview(payload: InterviewRequest): Promise<InterviewSession> {
  const templateId = payload.role.includes('AI')
    ? 'ai-testing'
    : payload.role.includes('自动化')
      ? 'automation'
      : payload.count >= 15
        ? 'full'
        : 'standard'
  const requestBody = {
    learner_id: 'local-learner',
    template_id: templateId,
    role: payload.role,
    count: payload.count,
    level: payload.difficulty === '综合' ? null : payload.difficulty,
    seed: payload.seed,
  }
  const raw = recordOf(
    await request<unknown>('/interviews', {
      method: 'POST',
      body: JSON.stringify(requestBody),
    }),
  )
  const items = Array.isArray(raw.questions) ? raw.questions : Array.isArray(raw.items) ? raw.items : []
  return {
    id: asString(raw.id ?? raw.session_id, `local-${Date.now()}`),
    questions: items.map(normalizeQuestion),
    role: asString(raw.role, payload.role),
    difficulty: asString(raw.difficulty, payload.difficulty),
    seed: Number(raw.seed) || payload.seed,
  }
}

export async function fetchInterview(
  sessionId: string,
  revealAnswers = false,
): Promise<InterviewSession> {
  const raw = recordOf(
    await request<unknown>(
      `/interviews/${encodeURIComponent(sessionId)}?reveal_answers=${String(revealAnswers)}`,
    ),
  )
  const items = Array.isArray(raw.questions) ? raw.questions : []
  return {
    id: asString(raw.id ?? raw.session_id, sessionId),
    questions: items.map(normalizeQuestion),
    role: asString(raw.role ?? raw.template_id),
    difficulty: asString(raw.difficulty ?? raw.level),
    seed: Number(raw.seed) || 0,
  }
}

export async function saveInterviewAnswer(
  sessionId: string,
  questionId: string,
  answer: string,
  selfScore: number,
): Promise<void> {
  await request<unknown>(
    `/interviews/${encodeURIComponent(sessionId)}/answers/${encodeURIComponent(questionId)}`,
    {
      method: 'PUT',
      body: JSON.stringify({
        answer,
        self_score: selfScore,
        notes: '浏览器端模拟面试自评',
      }),
    },
  )
}

export async function finishInterviewSession(
  sessionId: string,
  status: 'completed' | 'abandoned',
): Promise<void> {
  await request<unknown>(`/interviews/${encodeURIComponent(sessionId)}/status`, {
    method: 'PUT',
    body: JSON.stringify({ status }),
  })
}
