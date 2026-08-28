import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fetchProgress, saveProgress } from './api'
import { useProgress } from './progress'
import type { ProgressRecord } from './types'

vi.mock('./api', () => ({
  fetchProgress: vi.fn(),
  saveProgress: vi.fn(),
}))

const fetchProgressMock = vi.mocked(fetchProgress)
const saveProgressMock = vi.mocked(saveProgress)

function record(changes: Partial<ProgressRecord> = {}): ProgressRecord {
  return {
    questionId: 'core-01-01',
    favorite: false,
    wrong: false,
    mastery: 'unseen',
    note: '',
    ...changes,
  }
}

function deferred<T>() {
  let resolve!: (value: T) => void
  let reject!: (error: unknown) => void
  const promise = new Promise<T>((resolvePromise, rejectPromise) => {
    resolve = resolvePromise
    reject = rejectPromise
  })
  return { promise, resolve, reject }
}

beforeEach(() => {
  localStorage.clear()
  fetchProgressMock.mockReset()
  saveProgressMock.mockReset()
})

describe('useProgress', () => {
  it('同一题并发保存乱序返回时保留最新修改', async () => {
    const first = deferred<ProgressRecord>()
    const second = deferred<ProgressRecord>()
    saveProgressMock
      .mockReturnValueOnce(first.promise)
      .mockReturnValueOnce(second.promise)
    const store = useProgress()

    const firstUpdate = store.update(record({ favorite: true }))
    const secondUpdate = store.update(record({ favorite: true, wrong: true }))

    second.resolve(record({ favorite: true, wrong: true }))
    await secondUpdate
    first.resolve(record({ favorite: true, wrong: false }))
    await firstUpdate

    expect(store.records.value.get('core-01-01')).toMatchObject({
      favorite: true,
      wrong: true,
    })
  })

  it('初始化加载迟到时不会覆盖加载期间发生的本地修改', async () => {
    const loading = deferred<ProgressRecord[]>()
    fetchProgressMock.mockReturnValueOnce(loading.promise)
    saveProgressMock.mockResolvedValue(record({ favorite: true }))
    const store = useProgress()

    const loadPromise = store.load()
    await Promise.resolve()
    await store.update(record({ favorite: true }))
    loading.resolve([record({ favorite: false })])
    await loadPromise

    expect(store.records.value.get('core-01-01')?.favorite).toBe(true)
  })
})
