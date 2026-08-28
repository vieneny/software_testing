import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fetchXiaolinCoverage } from '../api'
import XiaolinCoverage from './XiaolinCoverage.vue'

vi.mock('../api', () => ({
  fetchXiaolinCoverage: vi.fn(),
  fetchSourceSnapshot: vi.fn(),
}))

const fetchCoverageMock = vi.mocked(fetchXiaolinCoverage)

beforeEach(() => {
  fetchCoverageMock.mockReset()
})

describe('XiaolinCoverage', () => {
  it('展示实际题量差异、原创声明并支持资料类型筛选', async () => {
    fetchCoverageMock.mockResolvedValue({
      documentCount: 21,
      mappedDocumentCount: 21,
      questionReferenceCount: 184,
      unmappedDocuments: 0,
      declaredQuestionCount: 1143,
      observedQuestionCount: 1111,
      documents: [
        {
          documentId: 'business',
          snapshotId: 'xiaolincoding-business-testing',
          title: '业务测试面试题',
          module: '直接题库 · 业务测试',
          url: 'https://xiaolincoding.com/interview/business_testing.html',
          sourceChars: 36544,
          coverageMode: 'direct-bank-reviewed',
          declaredQuestionCount: 154,
          observedQuestionCount: 148,
          questionIds: ['xiaolin-business-session-based-exploration'],
          qualityNotes: ['固定阈值已经移除'],
        },
        {
          documentId: 'jvm',
          snapshotId: 'xiaolincoding-jvm',
          title: 'Java 虚拟机面试题',
          module: '测开基础 · Java 与 JVM',
          url: 'https://xiaolincoding.com/interview/jvm.html',
          sourceChars: 26022,
          coverageMode: 'supporting-topic-mapping',
          declaredQuestionCount: 40,
          observedQuestionCount: 37,
          questionIds: ['xiaolin-automation-jvm-gc-evidence'],
          qualityNotes: ['按当前 JDK 版本核对'],
        },
      ],
    })

    const wrapper = mount(XiaolinCoverage)
    await flushPromises()

    expect(wrapper.text()).toContain('答案经过去重和原创重写')
    expect(wrapper.text()).toContain('1,143')
    expect(wrapper.text()).toContain('1,111')
    expect(wrapper.text()).toContain('业务测试面试题')
    expect(wrapper.find('a[href]').exists()).toBe(false)
    expect(wrapper.find('button[aria-haspopup="dialog"]').exists()).toBe(true)

    await wrapper.get('select').setValue('测开基础 · Java 与 JVM')
    expect(wrapper.text()).toContain('Java 虚拟机面试题')
    expect(wrapper.text()).not.toContain('业务测试面试题')
  })

  it('接口失败时展示可重试错误', async () => {
    fetchCoverageMock.mockRejectedValue(new Error('来源覆盖接口暂不可用'))

    const wrapper = mount(XiaolinCoverage)
    await flushPromises()

    expect(wrapper.get('[role="alert"]').text()).toContain(
      '来源覆盖接口暂不可用',
    )
    expect(wrapper.get('[role="alert"] button').text()).toBe('重新读取')
  })
})
