import DOMPurify from 'dompurify'
import type { Config } from 'dompurify'
import MarkdownIt from 'markdown-it'
import type { SourceSnapshotAsset } from './types'

interface SourceMarkdownEnvironment {
  sourceId: string
  assets: Map<string, SourceSnapshotAsset>
}

const SAFE_IMAGE_MEDIA_TYPES = new Set([
  'image/avif',
  'image/gif',
  'image/jpeg',
  'image/png',
  'image/webp',
])

const markdown = new MarkdownIt({
  html: false,
  linkify: false,
  typographer: false,
})

// Destinations are never emitted. Accepting them here lets the custom rules
// turn even javascript:/data: image syntax into an explicit blocked placeholder.
markdown.validateLink = () => true
markdown.renderer.rules.link_open = () =>
  '<span class="source-markdown-link" title="外部链接已禁用">'
markdown.renderer.rules.link_close = () => '</span>'

function assetUrl(sourceId: string, assetId: string): string {
  return `/api/v1/sources/${encodeURIComponent(sourceId)}/assets/${encodeURIComponent(assetId)}`
}

function imagePlaceholder(alt: string, reason: string): string {
  const safeAlt = markdown.utils.escapeHtml(alt.trim() || '未命名图片')
  const safeReason = markdown.utils.escapeHtml(reason)
  return `<span class="source-markdown-asset-placeholder" role="img" aria-label="${safeReason}：${safeAlt}">图片未显示：${safeAlt}（${safeReason}）</span>`
}

markdown.renderer.rules.image = (tokens, index, _options, environment) => {
  const token = tokens[index]
  const source = token.attrGet('src') ?? ''
  const alt = token.content || token.attrGet('alt') || ''
  if (!source.startsWith('snapshot-asset:')) {
    return imagePlaceholder(alt, '仅允许仓库本地资产')
  }

  const assetId = source.slice('snapshot-asset:'.length)
  const env = environment as SourceMarkdownEnvironment
  const asset = env.assets.get(assetId)
  if (!asset || !SAFE_IMAGE_MEDIA_TYPES.has(asset.mediaType)) {
    return imagePlaceholder(alt, '资产未登记或格式不受支持')
  }

  const resolvedAlt = asset.alt || alt || asset.caption || '本地快照图片'
  const caption = asset.caption || resolvedAlt
  const safeAlt = markdown.utils.escapeHtml(resolvedAlt)
  const safeCaption = markdown.utils.escapeHtml(caption)
  const safeUrl = markdown.utils.escapeHtml(assetUrl(env.sourceId, asset.assetId))
  return [
    '<details class="source-markdown-image">',
    `<summary>查看图片：${safeCaption}</summary>`,
    '<figure class="source-markdown-figure">',
    `<img src="${safeUrl}" alt="${safeAlt}" loading="lazy" decoding="async">`,
    `<figcaption>${safeCaption}</figcaption>`,
    '</figure>',
    '</details>',
  ].join('')
}

const PURIFY_CONFIG: Config = {
  ALLOWED_TAGS: [
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'p',
    'br',
    'hr',
    'strong',
    'em',
    'del',
    'blockquote',
    'ul',
    'ol',
    'li',
    'pre',
    'code',
    'table',
    'thead',
    'tbody',
    'tr',
    'th',
    'td',
    'span',
    'details',
    'summary',
    'figure',
    'figcaption',
    'img',
  ],
  ALLOWED_ATTR: [
    'class',
    'src',
    'alt',
    'title',
    'loading',
    'decoding',
    'role',
    'aria-label',
  ],
  ALLOW_DATA_ATTR: false,
}

function replaceWithRejectedImage(
  image: HTMLImageElement,
  reason: string,
): void {
  const placeholder = document.createElement('span')
  placeholder.className = 'source-markdown-asset-placeholder'
  placeholder.setAttribute('role', 'img')
  const alt = image.alt.trim() || '未命名图片'
  placeholder.setAttribute('aria-label', `${reason}：${alt}`)
  placeholder.textContent = `图片未显示：${alt}（${reason}）`
  image.replaceWith(placeholder)
}

export function renderSourceMarkdown(
  content: string,
  sourceId: string,
  assets: SourceSnapshotAsset[],
  documentTitle = '',
): string {
  const assetMap = new Map(
    assets.map((asset) => [asset.assetId, asset] as const),
  )
  const rendered = markdown.render(content, {
    sourceId,
    assets: assetMap,
  } satisfies SourceMarkdownEnvironment)
  const sanitized = String(DOMPurify.sanitize(rendered, PURIFY_CONFIG))

  // Renderer rules are the first boundary; this DOM pass is defense in depth.
  const template = document.createElement('template')
  template.innerHTML = sanitized
  template.content.querySelectorAll('a').forEach((link) => {
    link.replaceWith(document.createTextNode(link.textContent ?? ''))
  })
  const allowedUrls = new Set(
    assets
      .filter((asset) => SAFE_IMAGE_MEDIA_TYPES.has(asset.mediaType))
      .map((asset) => assetUrl(sourceId, asset.assetId)),
  )
  template.content.querySelectorAll('img').forEach((image) => {
    const src = image.getAttribute('src') ?? ''
    if (!allowedUrls.has(src)) {
      replaceWithRejectedImage(image, '图片地址未通过本地资产校验')
    }
  })
  const firstElement = template.content.firstElementChild
  const normalizeTitle = (value: string) =>
    value.trim().replace(/\s+/g, ' ')
  const normalizedDocumentTitle = normalizeTitle(documentTitle)
  if (
    firstElement?.tagName === 'H1' &&
    normalizedDocumentTitle !== '' &&
    normalizeTitle(firstElement.textContent ?? '') ===
      normalizedDocumentTitle
  ) {
    firstElement.remove()
  }
  return template.innerHTML
}

/**
 * Render authored question-bank prose with the same strict boundary as source
 * snapshots. Links cannot be clicked, raw HTML is escaped and images have no
 * registered manifest, so they become an explicit blocked placeholder.
 */
export function renderAnswerMarkdown(content: string): string {
  return renderSourceMarkdown(content, 'question-answer', [])
}
