<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref } from 'vue'
import { fetchSourceSnapshot } from '../api'
import { renderSourceMarkdown } from '../sourceMarkdown'
import type { SourceSnapshot } from '../types'

const props = withDefaults(
  defineProps<{
    sourceId: string
    sourceName?: string
    originalUrl?: string
    compact?: boolean
  }>(),
  {
    sourceName: '',
    originalUrl: '',
    compact: false,
  },
)

const open = ref(false)
const loading = ref(false)
const errorMessage = ref('')
const snapshot = ref<SourceSnapshot | null>(null)
const copyStatus = ref('')
const closeButton = ref<HTMLButtonElement | null>(null)
const dialog = ref<HTMLElement | null>(null)
let trigger: HTMLButtonElement | null = null
let previousBodyOverflow = ''
let snapshotRequestId = 0

function formatNumber(value: number): string {
  return new Intl.NumberFormat('zh-CN').format(value)
}

function formatCapturedAt(value: string): string {
  if (!value) return '未记录'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('zh-CN', {
    dateStyle: 'medium',
    timeStyle: 'medium',
  }).format(date)
}

function resolvedOriginalUrl(): string {
  return snapshot.value?.originalUrl || props.originalUrl
}

const renderedContent = computed(() => {
  if (!snapshot.value?.content) return ''
  return renderSourceMarkdown(
    snapshot.value.content,
    snapshot.value.sourceId || props.sourceId,
    snapshot.value.assets,
    snapshot.value.title,
  )
})

async function loadSnapshot() {
  const requestId = ++snapshotRequestId
  loading.value = true
  errorMessage.value = ''
  copyStatus.value = ''
  snapshot.value = null
  try {
    const loadedSnapshot = await fetchSourceSnapshot(props.sourceId)
    if (requestId !== snapshotRequestId) return
    snapshot.value = loadedSnapshot
    if (!snapshot.value.content.trim()) {
      errorMessage.value = '本地快照存在，但正文为空。请重新运行来源下载与校验流程。'
    }
  } catch (error) {
    if (requestId !== snapshotRequestId) return
    snapshot.value = null
    errorMessage.value =
      error instanceof Error
        ? error.message
        : '暂时无法读取本地来源快照。'
  } finally {
    if (requestId === snapshotRequestId) loading.value = false
  }
}

async function showSnapshot(event: MouseEvent) {
  trigger = event.currentTarget as HTMLButtonElement
  open.value = true
  previousBodyOverflow = document.body.style.overflow
  document.body.style.overflow = 'hidden'
  document.addEventListener('keydown', onKeydown)
  await nextTick()
  closeButton.value?.focus()
  await loadSnapshot()
}

function closeSnapshot() {
  if (!open.value) return
  snapshotRequestId += 1
  loading.value = false
  open.value = false
  document.body.style.overflow = previousBodyOverflow
  document.removeEventListener('keydown', onKeydown)
  void nextTick(() => trigger?.focus())
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    closeSnapshot()
    return
  }
  if (event.key !== 'Tab' || !dialog.value) return

  const focusable = Array.from(
    dialog.value.querySelectorAll<HTMLElement>(
      'button:not([disabled]), summary, input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
    ),
  )
  if (!focusable.length) return
  const first = focusable[0]
  const last = focusable[focusable.length - 1]
  if (event.shiftKey && (document.activeElement === first || !dialog.value.contains(document.activeElement))) {
    event.preventDefault()
    last.focus()
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault()
    first.focus()
  }
}

async function copyOriginalUrl() {
  const url = resolvedOriginalUrl()
  if (!url) return
  try {
    if (!navigator.clipboard?.writeText) {
      copyStatus.value = '当前浏览器不支持自动复制，请手动选择网址文本。'
      return
    }
    await navigator.clipboard.writeText(url)
    copyStatus.value = '原始网址已复制。'
  } catch {
    copyStatus.value = '复制失败，请手动选择网址文本。'
  }
}

function handleAssetError(event: Event) {
  const image = event.target
  if (!(image instanceof HTMLImageElement)) return
  const placeholder = document.createElement('span')
  placeholder.className = 'source-markdown-asset-placeholder'
  placeholder.setAttribute('role', 'img')
  const alt = image.alt.trim() || '未命名图片'
  placeholder.setAttribute('aria-label', `本地图片加载失败：${alt}`)
  placeholder.textContent = `图片加载失败：${alt}`
  image.replaceWith(placeholder)
}

onBeforeUnmount(() => {
  document.removeEventListener('keydown', onKeydown)
  if (open.value) document.body.style.overflow = previousBodyOverflow
})
</script>

<template>
  <button
    class="source-snapshot-trigger"
    :class="{ 'source-snapshot-trigger--compact': compact }"
    type="button"
    aria-haspopup="dialog"
    @click="showSnapshot"
  >
    <slot>{{ sourceName || sourceId }}</slot>
  </button>

  <Teleport to="body">
    <div
      v-if="open"
      class="source-snapshot-backdrop"
      data-testid="source-snapshot-backdrop"
      @click.self="closeSnapshot"
    >
      <section
        ref="dialog"
        class="source-snapshot-dialog"
        :class="{ 'source-snapshot-dialog--reader': snapshot?.content }"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="`source-snapshot-title-${sourceId}`"
        :aria-describedby="`source-snapshot-description-${sourceId}`"
      >
        <header class="source-snapshot-dialog__header">
          <div>
            <p class="kicker">仓库本地资料</p>
            <h2 :id="`source-snapshot-title-${sourceId}`">
              {{ snapshot?.title || sourceName || sourceId }}
            </h2>
            <p :id="`source-snapshot-description-${sourceId}`">
              正文从本地快照读取，本窗口不会跳转到来源网站。
            </p>
          </div>
          <button
            ref="closeButton"
            class="button button--secondary button--compact"
            type="button"
            aria-label="关闭来源快照"
            @click="closeSnapshot"
          >
            关闭
          </button>
        </header>

        <div v-if="loading" class="source-snapshot-state" role="status">
          正在读取本地快照…
        </div>

        <div
          v-else-if="errorMessage"
          class="notice notice--error source-snapshot-state"
          role="alert"
        >
          <div>
            <strong>本地快照暂不可读</strong>
            <p>{{ errorMessage }}</p>
          </div>
          <button class="button button--secondary" type="button" @click="loadSnapshot">
            重新读取
          </button>
        </div>

        <dl v-if="snapshot" class="source-snapshot-meta">
          <div>
            <dt>资料类型</dt>
            <dd>{{ snapshot.kind }}</dd>
          </div>
          <div>
            <dt>抓取时间</dt>
            <dd>{{ formatCapturedAt(snapshot.capturedAt) }}</dd>
          </div>
          <div>
            <dt>正文字符</dt>
            <dd>{{ formatNumber(snapshot.charCount) }}</dd>
          </div>
          <div>
            <dt>内容校验</dt>
            <dd class="source-snapshot-hash">
              {{ snapshot.contentHash || '未记录' }}
            </dd>
          </div>
        </dl>

        <div v-if="resolvedOriginalUrl()" class="source-snapshot-url">
          <div>
            <strong>原始网址（仅供追溯，不会自动打开）</strong>
            <code data-testid="source-original-url">{{ resolvedOriginalUrl() }}</code>
          </div>
          <button
            class="button button--secondary button--compact"
            type="button"
            @click="copyOriginalUrl"
          >
            复制网址
          </button>
        </div>
        <p v-if="copyStatus" class="source-snapshot-copy-status" role="status">
          {{ copyStatus }}
        </p>

        <div v-if="snapshot?.content" class="source-snapshot-content">
          <div class="source-snapshot-content__heading">
            <strong>本地快照正文</strong>
            <span v-if="snapshot.localPath">本地文件：{{ snapshot.localPath }}</span>
          </div>
          <!-- 唯一受控 HTML 出口：markdown-it 禁用 HTML/链接后，再经 DOMPurify 白名单净化。 -->
          <article
            class="source-snapshot-markdown"
            data-testid="source-snapshot-markdown"
            @error.capture="handleAssetError"
            v-html="renderedContent"
          ></article>
        </div>

        <p v-if="snapshot" class="source-snapshot-notice">
          {{ snapshot.copyrightNotice }}
        </p>
      </section>
    </div>
  </Teleport>
</template>
