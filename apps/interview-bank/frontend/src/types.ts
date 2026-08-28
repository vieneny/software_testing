export type Mastery = 'unseen' | 'learning' | 'mastered'

export interface Question {
  id: string
  moduleId: string
  moduleName: string
  title: string
  level: string
  kind: string
  origin: string
  roles: string[]
  tags: string[]
  focus: string
  answerStrategy: string
  answer: string
  explanation: string
  followups: string[]
  pitfalls: string[]
  scenario: string
  sourceIds: string[]
  relatedQuestionIds: string[]
  deepeningRationale: string
  historicalReference: string
  updatedAt: string
}

export interface QuestionFilters {
  query: string
  module: string
  level: string
  kind: string
  origin: string
  role: string
  questionIds?: string[]
  page: number
  pageSize: number
}

export interface QuestionPage {
  items: Question[]
  total: number
  page: number
  pageSize: number
}

export interface ModuleOption {
  id: string
  name: string
  count: number
}

export interface Meta {
  questionCount: number
  moduleCount: number
  modules: ModuleOption[]
  levels: string[]
  kinds: string[]
  origins: string[]
  roles: string[]
  lastUpdated: string
}

export interface ProgressRecord {
  questionId: string
  favorite: boolean
  wrong: boolean
  mastery: Mastery
  note: string
  selfScore?: number
  updatedAt?: string
}

export interface Source {
  id: string
  snapshotId: string
  name: string
  url: string
  kind: string
  accessedAt: string
  summary: string
}

export interface SourceSnapshot {
  sourceId: string
  title: string
  kind: string
  originalUrl: string
  capturedAt: string
  contentFormat: 'markdown' | 'text' | 'html'
  content: string
  contentHash: string
  localPath: string
  charCount: number
  copyrightNotice: string
  assets: SourceSnapshotAsset[]
}

export interface SourceSnapshotAsset {
  assetId: string
  mediaType: string
  alt: string
  caption: string
  byteCount: number
  contentHash: string
}

export interface LegacyCoverageSummary {
  total: number
  mappedToAnswer: number
  unmapped: number
  isolatedAnswers: number
  coverageRate: number
  purpose: string
  answerHandling: string
}

export interface SourceCoverageDocument {
  documentId: string
  snapshotId: string
  title: string
  module: string
  url: string
  sourceChars: number
  coverageMode: string
  questionIds: string[]
  qualityNotes: string[]
  declaredQuestionCount?: number
  observedQuestionCount?: number
}

export interface SourceCoverage {
  documentCount: number
  mappedDocumentCount: number
  questionReferenceCount: number
  unmappedDocuments: number
  declaredQuestionCount?: number
  observedQuestionCount?: number
  documents: SourceCoverageDocument[]
}

export interface InterviewRequest {
  role: string
  difficulty: string
  count: number
  seed: number
}

export interface InterviewSession {
  id: string
  questions: Question[]
  role: string
  difficulty: string
  seed: number
}

export interface InterviewAnswer {
  questionId: string
  answer: string
  score: number
  revealed: boolean
}
