import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fetchLegacyCoverage, fetchSources } from '../api'
import SourcesView from './SourcesView.vue'

vi.mock('../api', () => ({
  fetchSources: vi.fn(),
  fetchLegacyCoverage: vi.fn(),
  fetchSourceSnapshot: vi.fn(),
}))

const fetchSourcesMock = vi.mocked(fetchSources)
const fetchLegacyCoverageMock = vi.mocked(fetchLegacyCoverage)

beforeEach(() => {
  fetchSourcesMock.mockReset()
  fetchLegacyCoverageMock.mockReset()
})

describe('SourcesView', () => {
  it('参考来源只打开站内快照，不输出外站链接', async () => {
    fetchSourcesMock.mockResolvedValue([
      {
        id: 'owasp-wstg',
        snapshotId: 'owasp-wstg',
        name: 'OWASP Web Security Testing Guide',
        url: 'https://owasp.org/www-project-web-security-testing-guide/',
        kind: '官方开源指南',
        accessedAt: '2026-07-29',
        summary: '用于安全测试事实核验。',
      },
    ])
    fetchLegacyCoverageMock.mockResolvedValue({
      total: 10,
      mappedToAnswer: 10,
      unmapped: 0,
      isolatedAnswers: 0,
      coverageRate: 1,
      purpose: '历史资料审计',
      answerHandling: '仅保留泛化后的题意。',
    })

    const wrapper = mount(SourcesView, {
      global: {
        stubs: {
          XiaolinCoverage: true,
        },
      },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('资料来源与覆盖情况')
    expect(wrapper.text()).toContain('标准校验 · 来源追溯 · 覆盖审计')
    expect(wrapper.text()).toContain('OWASP Web Security Testing Guide')
    expect(wrapper.text()).toContain('优先阅读仓库内的来源快照')
    expect(wrapper.find('a[href]').exists()).toBe(false)
    expect(wrapper.get('button[aria-haspopup="dialog"]').text()).toContain(
      'OWASP Web Security Testing Guide',
    )
  })
})
