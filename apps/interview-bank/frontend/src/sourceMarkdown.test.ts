import { describe, expect, it } from 'vitest'
import { renderAnswerMarkdown, renderSourceMarkdown } from './sourceMarkdown'
import type { SourceSnapshotAsset } from './types'

const assets: SourceSnapshotAsset[] = [
  {
    assetId: 'flow-chart',
    mediaType: 'image/png',
    alt: '接口调用流程图',
    caption: '图 1：本地接口调用流程',
    byteCount: 2048,
    contentHash: 'sha256:image123',
  },
  {
    assetId: 'unsafe-svg',
    mediaType: 'image/svg+xml',
    alt: 'SVG 图片',
    caption: '不受支持的格式',
    byteCount: 1024,
    contentHash: 'sha256:svg123',
  },
]

function renderInHost(markdown: string): HTMLElement {
  const host = document.createElement('div')
  host.innerHTML = renderSourceMarkdown(markdown, 'source/测试', assets)
  return host
}

describe('renderSourceMarkdown', () => {
  it('正确展示标题、列表、引用、表格、代码块和行内代码', () => {
    const host = renderInHost(`
# 性能排查

- 先观察
- 再验证

> 结论必须有证据。

| 指标 | 含义 |
| --- | --- |
| P95 | 尾延迟 |

使用 \`jcmd\` 采样：

\`\`\`bash
jcmd 1234 VM.native_memory summary
\`\`\`
`)

    expect(host.querySelector('h1')?.textContent).toBe('性能排查')
    expect(host.querySelectorAll('li')).toHaveLength(2)
    expect(host.querySelector('blockquote')?.textContent).toContain('证据')
    expect(host.querySelector('table')?.textContent).toContain('尾延迟')
    expect(host.querySelector('p code')?.textContent).toBe('jcmd')
    expect(host.querySelector('pre code')?.textContent).toContain(
      'VM.native_memory',
    )
  })

  it('仅移除与文档标题相同的首个 H1，其他 H1 保持不变', () => {
    const duplicate = document.createElement('div')
    duplicate.innerHTML = renderSourceMarkdown(
      '#  网络   面试题  \n\n正文',
      'network',
      [],
      '网络 面试题',
    )
    expect(duplicate.querySelector('h1')).toBeNull()
    expect(duplicate.textContent).toContain('正文')

    const different = document.createElement('div')
    different.innerHTML = renderSourceMarkdown(
      '# TCP 专题\n\n正文',
      'network',
      [],
      '网络面试题',
    )
    expect(different.querySelector('h1')?.textContent).toBe('TCP 专题')

    const notFirst = document.createElement('div')
    notFirst.innerHTML = renderSourceMarkdown(
      '前言\n\n# 网络面试题',
      'network',
      [],
      '网络面试题',
    )
    expect(notFirst.querySelector('h1')?.textContent).toBe('网络面试题')
  })

  it('禁用原始 HTML 和所有可点击链接，并清除 XSS 载荷', () => {
    const host = renderInHost(`
<script>window.pwned = true</script>
<img src=x onerror="window.pwned=true">
[外部资料](https://evil.example/phish)
<https://evil.example/auto>
`)

    expect(host.querySelector('script')).toBeNull()
    expect(host.querySelector('[onerror]')).toBeNull()
    expect(host.querySelector('a')).toBeNull()
    expect(host.innerHTML).not.toContain('href=')
    expect(host.innerHTML).not.toContain('src="x"')
    expect(host.textContent).toContain('外部资料')
  })

  it('只把 manifest 中安全类型的 snapshot-asset 渲染为本地懒加载图片', () => {
    const host = renderInHost(`
![流程](snapshot-asset:flow-chart)
![未登记](snapshot-asset:not-found)
![SVG](snapshot-asset:unsafe-svg)
![远程](https://evil.example/a.png)
![数据](data:image/png;base64,AAAA)
![脚本](javascript:alert(1))
`)

    const images = host.querySelectorAll('img')
    expect(images).toHaveLength(1)
    const imageDisclosure = host.querySelector('details.source-markdown-image')
    expect(imageDisclosure).not.toBeNull()
    expect(imageDisclosure?.hasAttribute('open')).toBe(false)
    expect(imageDisclosure?.querySelector('summary')?.textContent).toBe(
      '查看图片：图 1：本地接口调用流程',
    )
    expect(images[0].getAttribute('src')).toBe(
      '/api/v1/sources/source%2F%E6%B5%8B%E8%AF%95/assets/flow-chart',
    )
    expect(images[0].getAttribute('loading')).toBe('lazy')
    expect(images[0].getAttribute('decoding')).toBe('async')
    expect(images[0].getAttribute('alt')).toBe('接口调用流程图')
    expect(host.querySelector('figcaption')?.textContent).toBe(
      '图 1：本地接口调用流程',
    )

    const placeholders = host.querySelectorAll(
      '.source-markdown-asset-placeholder',
    )
    expect(placeholders).toHaveLength(5)
    expect(host.innerHTML).not.toContain('evil.example')
    expect(host.innerHTML).not.toContain('data:image')
    expect(host.innerHTML).not.toContain('javascript:')
  })

  it('安全渲染题库答案中的表格与代码，同时禁用 HTML、链接和图片', () => {
    const host = document.createElement('div')
    host.innerHTML = renderAnswerMarkdown(`
| 阶段 | 证据 |
| --- | --- |
| 执行 | \`trace_id\` |

[外部链接](https://evil.example)
![远程图片](https://evil.example/a.png)
<img src=x onerror="window.pwned=true">
`)

    expect(host.querySelector('table')?.textContent).toContain('trace_id')
    expect(host.querySelector('code')?.textContent).toBe('trace_id')
    expect(host.querySelector('a')).toBeNull()
    expect(host.querySelector('img')).toBeNull()
    expect(host.querySelector('[onerror]')).toBeNull()
    expect(host.textContent).toContain('外部链接')
    expect(host.textContent).toContain('图片未显示：远程图片')
  })
})
