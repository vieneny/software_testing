import { ref } from 'vue'
import { fetchProgress, saveProgress } from './api'
import type { ProgressRecord } from './types'

const PROGRESS_KEY = 'interview-bank-progress-v1'

function createLearnerId(): string {
  return 'local-learner'
}

function readLocalProgress(): ProgressRecord[] {
  try {
    const parsed = JSON.parse(localStorage.getItem(PROGRESS_KEY) ?? '[]')
    return Array.isArray(parsed) ? (parsed as ProgressRecord[]) : []
  } catch {
    return []
  }
}

export function useProgress() {
  const learnerId = createLearnerId()
  const records = ref(new Map<string, ProgressRecord>())
  const syncMessage = ref('')
  const syncError = ref('')
  const editVersions = new Map<string, number>()
  let syncOperation = 0
  let syncMessageTimer: number | undefined

  function apply(items: ProgressRecord[]) {
    records.value = new Map(items.map((item) => [item.questionId, item]))
  }

  function writeLocal() {
    localStorage.setItem(PROGRESS_KEY, JSON.stringify(Array.from(records.value.values())))
  }

  async function load() {
    const operation = ++syncOperation
    const local = readLocalProgress()
    apply(local)
    const versionsAtStart = new Map(editVersions)
    try {
      const remote = await fetchProgress(learnerId)
      const merged = new Map(records.value)
      remote.forEach((item) => {
        const startedVersion = versionsAtStart.get(item.questionId) ?? 0
        const currentVersion = editVersions.get(item.questionId) ?? 0
        if (startedVersion === currentVersion) {
          merged.set(item.questionId, item)
        }
      })
      records.value = merged
      writeLocal()
      if (operation === syncOperation) syncError.value = ''
    } catch (error) {
      if (operation !== syncOperation) return
      syncError.value =
        error instanceof Error
          ? `${error.message} 学习进度仍可保存在本机。`
          : '进度同步失败。'
    }
  }

  function get(questionId: string): ProgressRecord {
    return (
      records.value.get(questionId) ?? {
        questionId,
        favorite: false,
        wrong: false,
        mastery: 'unseen',
        note: '',
      }
    )
  }

  async function update(next: ProgressRecord) {
    const revision = (editVersions.get(next.questionId) ?? 0) + 1
    editVersions.set(next.questionId, revision)
    const operation = ++syncOperation
    if (syncMessageTimer !== undefined) {
      window.clearTimeout(syncMessageTimer)
      syncMessageTimer = undefined
    }
    records.value = new Map(records.value).set(next.questionId, {
      ...next,
      updatedAt: new Date().toISOString(),
    })
    writeLocal()
    syncMessage.value = '已保存在本机，正在同步…'
    syncError.value = ''
    try {
      const remote = await saveProgress(learnerId, next)
      if (editVersions.get(next.questionId) !== revision) return
      records.value = new Map(records.value).set(next.questionId, { ...next, ...remote })
      writeLocal()
      if (operation === syncOperation) {
        syncMessage.value = '学习进度已同步'
        syncMessageTimer = window.setTimeout(() => {
          if (operation === syncOperation) syncMessage.value = ''
          syncMessageTimer = undefined
        }, 1800)
      }
    } catch (error) {
      if (
        editVersions.get(next.questionId) !== revision ||
        operation !== syncOperation
      ) {
        return
      }
      syncMessage.value = ''
      syncError.value =
        error instanceof Error ? `${error.message} 本次修改已保存在本机。` : '同步失败，本次修改已保存在本机。'
    }
  }

  return { records, syncMessage, syncError, load, get, update }
}
