import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { fetchSourceSnapshot } from '../api'
import SourceSnapshotViewer from './SourceSnapshotViewer.vue'

vi.mock('../api', () => ({
  fetchSourceSnapshot: vi.fn(),
}))

const fetchSnapshotMock = vi.mocked(fetchSourceSnapshot)

afterEach(() => {
  fetchSnapshotMock.mockReset()
  vi.unstubAllGlobals()
  document.body.style.overflow = ''
})

describe('SourceSnapshotViewer', () => {
  it('在站内对话框读取本地正文，原始网址仅作为可复制文本', async () => {
    fetchSnapshotMock.mockResolvedValue({
      sourceId: 'xiaolincoding-network',
      title: '网络面试题本地快照',
      kind: '公开资料快照',
      originalUrl: 'https://xiaolincoding.com/network/',
      capturedAt: '2026-07-29T09:30:00+08:00',
      contentFormat: 'markdown',
      content: '# TCP\n\n正文来自仓库本地快照。',
      contentHash: 'sha256:abc123',
      localPath: 'data/source-snapshots/xiaolincoding-network.md',
      charCount: 22,
      copyrightNotice: '仅用于个人学习与事实核验。',
      assets: [],
    })
    const writeText = vi.fn().mockResolvedValue(undefined)
    vi.stubGlobal('navigator', { clipboard: { writeText } })

    const wrapper = mount(SourceSnapshotViewer, {
      props: {
        sourceId: 'xiaolincoding-network',
        sourceName: '网络面试题',
        originalUrl: 'https://xiaolincoding.com/network/',
      },
      global: {
        stubs: { Teleport: true },
      },
    })

    await wrapper.get('button[aria-haspopup="dialog"]').trigger('click')
    await flushPromises()

    expect(fetchSnapshotMock).toHaveBeenCalledWith('xiaolincoding-network')
    expect(wrapper.get('[role="dialog"]').text()).toContain('正文来自仓库本地快照')
    expect(wrapper.get('[data-testid="source-snapshot-markdown"] h1').text()).toBe(
      'TCP',
    )
    expect(wrapper.findAll('.source-snapshot-meta dd')[1].text()).not.toContain(
      'T09:30:00',
    )
    expect(wrapper.get('[data-testid="source-original-url"]').text()).toBe(
      'https://xiaolincoding.com/network/',
    )
    expect(wrapper.find('a[href]').exists()).toBe(false)

    await wrapper.get('.source-snapshot-url button').trigger('click')
    await flushPromises()
    expect(writeText).toHaveBeenCalledWith('https://xiaolincoding.com/network/')
    expect(wrapper.text()).toContain('原始网址已复制')
  })

  it('快照缺失时明确报错并允许重试，不回退为外站链接', async () => {
    fetchSnapshotMock.mockRejectedValue(new Error('该来源尚未下载到本地'))
    const wrapper = mount(SourceSnapshotViewer, {
      props: {
        sourceId: 'missing-source',
        sourceName: '待下载来源',
        originalUrl: 'https://example.com/reference',
      },
      global: {
        stubs: { Teleport: true },
      },
    })

    await wrapper.get('button[aria-haspopup="dialog"]').trigger('click')
    await flushPromises()

    expect(wrapper.get('[role="alert"]').text()).toContain('该来源尚未下载到本地')
    expect(wrapper.get('[role="alert"] button').text()).toBe('重新读取')
    expect(wrapper.find('a[href]').exists()).toBe(false)
  })

  it('本地图片加载失败后显示可读占位和说明文字', async () => {
    fetchSnapshotMock.mockResolvedValue({
      sourceId: 'local-image-source',
      title: '含图快照',
      kind: '公开资料快照',
      originalUrl: '',
      capturedAt: '2026-07-29T09:30:00+08:00',
      contentFormat: 'markdown',
      content: '![流程图](snapshot-asset:flow-chart)',
      contentHash: 'sha256:content',
      localPath: 'data/source-snapshots/content/local-image-source.md',
      charCount: 42,
      copyrightNotice: '仅用于个人学习。',
      assets: [
        {
          assetId: 'flow-chart',
          mediaType: 'image/png',
          alt: '接口自动化执行流程',
          caption: '图 1：从用例到报告',
          byteCount: 2048,
          contentHash: 'sha256:image',
        },
      ],
    })
    const wrapper = mount(SourceSnapshotViewer, {
      props: {
        sourceId: 'local-image-source',
        sourceName: '含图快照',
      },
      attachTo: document.body,
      global: {
        stubs: { Teleport: true },
      },
    })

    await wrapper.get('button[aria-haspopup="dialog"]').trigger('click')
    await flushPromises()

    const image = wrapper.get('.source-markdown-figure img')
    expect(wrapper.get('.source-markdown-image').attributes('open')).toBeUndefined()
    expect(wrapper.get('.source-markdown-image summary').text()).toBe(
      '查看图片：图 1：从用例到报告',
    )
    const summary = wrapper.get<HTMLElement>('.source-markdown-image summary')
    summary.element.focus()
    document.dispatchEvent(
      new KeyboardEvent('keydown', { key: 'Tab', bubbles: true }),
    )
    expect(document.activeElement).toBe(
      wrapper.get('button[aria-label="关闭来源快照"]').element,
    )
    expect(image.attributes('src')).toBe(
      '/api/v1/sources/local-image-source/assets/flow-chart',
    )
    expect(wrapper.get('figcaption').text()).toBe('图 1：从用例到报告')

    await image.trigger('error')
    expect(wrapper.find('.source-markdown-figure img').exists()).toBe(false)
    expect(wrapper.get('.source-markdown-asset-placeholder').text()).toContain(
      '图片加载失败：接口自动化执行流程',
    )
    wrapper.unmount()
  })

  it('关闭重开时忽略上一轮迟到的快照响应', async () => {
    let resolveFirst!: (value: Awaited<ReturnType<typeof fetchSourceSnapshot>>) => void
    const firstRequest = new Promise<Awaited<ReturnType<typeof fetchSourceSnapshot>>>(
      (resolve) => {
        resolveFirst = resolve
      },
    )
    fetchSnapshotMock
      .mockReturnValueOnce(firstRequest)
      .mockResolvedValueOnce({
        sourceId: 'race-source',
        title: '第二次读取的新快照',
        kind: '公开资料快照',
        originalUrl: '',
        capturedAt: '2026-07-29T10:00:00+08:00',
        contentFormat: 'markdown',
        content: '第二次读取正文。',
        contentHash: 'sha256:new',
        localPath: '',
        charCount: 8,
        copyrightNotice: '仅用于个人学习。',
        assets: [],
      })
    const wrapper = mount(SourceSnapshotViewer, {
      props: { sourceId: 'race-source' },
      global: { stubs: { Teleport: true } },
    })

    await wrapper.get('button[aria-haspopup="dialog"]').trigger('click')
    await wrapper.get('button[aria-label="关闭来源快照"]').trigger('click')
    await wrapper.get('button[aria-haspopup="dialog"]').trigger('click')
    await flushPromises()
    expect(wrapper.get('[role="dialog"]').text()).toContain('第二次读取的新快照')

    resolveFirst({
      sourceId: 'race-source',
      title: '第一次读取的旧快照',
      kind: '公开资料快照',
      originalUrl: '',
      capturedAt: '2026-07-29T09:00:00+08:00',
      contentFormat: 'markdown',
      content: '迟到的旧正文。',
      contentHash: 'sha256:old',
      localPath: '',
      charCount: 7,
      copyrightNotice: '仅用于个人学习。',
      assets: [],
    })
    await flushPromises()
    expect(wrapper.get('[role="dialog"]').text()).toContain('第二次读取的新快照')
    expect(wrapper.get('[role="dialog"]').text()).not.toContain('第一次读取的旧快照')
  })
})
