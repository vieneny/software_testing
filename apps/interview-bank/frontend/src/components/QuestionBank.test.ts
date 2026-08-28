import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import {
  fetchLegacyCoverage,
  fetchMeta,
  fetchQuestions,
} from '../api'
import type { ProgressRecord, Question, QuestionFilters } from '../types'
import QuestionBank from './QuestionBank.vue'

vi.mock('../api', () => ({
  fetchLegacyCoverage: vi.fn(),
  fetchMeta: vi.fn(),
  fetchQuestions: vi.fn(),
}))

const fetchQuestionsMock = vi.mocked(fetchQuestions)

function makeQuestion(index: number): Question {
  return {
    id: `question-${index}`,
    moduleId: '01',
    moduleName: '测试基础与质量思维',
    title: `第 ${index} 题`,
    level: '入门',
    kind: '知识题',
    origin: 'reviewed-core',
    roles: ['软件测试'],
    tags: ['质量'],
    focus: '回答边界',
    answer: '参考答案需要说明结论、依据、执行步骤和残余风险。',
    explanation: '解释答案为什么成立，以及结论在哪些边界内有效。',
    followups: ['如何取证？'],
    pitfalls: ['不要编造数据。'],
    scenario: '',
    sourceIds: [],
    relatedQuestionIds: [],
    deepeningRationale: '',
    historicalReference: '',
    updatedAt: '2026-07-29',
  }
}

beforeEach(() => {
  vi.stubGlobal('scrollTo', vi.fn())
  vi.mocked(fetchMeta).mockResolvedValue({
    questionCount: 101,
    moduleCount: 1,
    modules: [{ id: '01', name: '测试基础与质量思维', count: 101 }],
    levels: ['入门'],
    kinds: ['知识题'],
    origins: ['reviewed-core'],
    roles: ['软件测试'],
    lastUpdated: '2026-07-29',
  })
  vi.mocked(fetchLegacyCoverage).mockRejectedValue(new Error('本测试不加载历史覆盖'))
  fetchQuestionsMock.mockImplementation(async (filters: QuestionFilters) => {
    const matchingIndexes = filters.questionIds?.length
      ? filters.questionIds
          .map((questionId) => Number(questionId.replace('question-', '')))
          .sort((left, right) => left - right)
      : Array.from({ length: 101 }, (_, index) => index + 1)
    const pageSize = filters.pageSize
    const page = filters.page
    const start = (page - 1) * pageSize
    const end = Math.min(page * pageSize, matchingIndexes.length)
    return {
      items: matchingIndexes.slice(start, end).map(makeQuestion),
      total: matchingIndexes.length,
      page,
      pageSize,
    }
  })
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('QuestionBank', () => {
  it('首屏聚焦筛选、作答和复盘功能', async () => {
    const wrapper = mount(QuestionBank, { props: { progressRecords: new Map() } })
    await flushPromises()

    expect(wrapper.text()).toContain(
      '按模块、岗位能力和难度筛选题目，先口述，再对照答案、解释和追问完成复盘。',
    )
    expect(wrapper.text()).not.toContain('公司名称或内部材料')
  })

  it('收藏筛选会读取全部服务端分页，而不是只筛当前页', async () => {
    const favoriteProgress: ProgressRecord = {
      questionId: 'question-101',
      favorite: true,
      wrong: false,
      mastery: 'learning',
      note: '',
    }
    const wrapper = mount(QuestionBank, {
      props: {
        progressRecords: new Map([[favoriteProgress.questionId, favoriteProgress]]),
      },
    })
    await flushPromises()

    expect(wrapper.text()).not.toContain('第 101 题')
    await wrapper.findAll('button.toggle-button')[0].trigger('click')
    await flushPromises()

    expect(fetchQuestionsMock).toHaveBeenCalledWith(
      expect.objectContaining({ questionIds: ['question-101'] }),
    )
    expect(wrapper.text()).toContain('第 101 题')
    expect(wrapper.text()).toContain('共找到 1 道')

    await wrapper.get('button[aria-label="取消收藏"]').trigger('click')
    expect(wrapper.text()).toContain('没有符合条件的题目')
    expect(wrapper.emitted('updateProgress')?.[0][0]).toMatchObject({
      questionId: 'question-101',
      favorite: false,
    })
  })

  it('取消跨页收藏后补齐当前页，并在尾页清空时回退页码', async () => {
    const progressRecords = new Map<string, ProgressRecord>(
      Array.from({ length: 13 }, (_, index) => {
        const questionId = `question-${index + 1}`
        return [
          questionId,
          {
            questionId,
            favorite: true,
            wrong: false,
            mastery: 'learning',
            note: '',
          },
        ]
      }),
    )
    const wrapper = mount(QuestionBank, { props: { progressRecords } })
    await flushPromises()
    await wrapper.findAll('button.toggle-button')[0].trigger('click')
    await flushPromises()

    expect(wrapper.findAll('.question-card')).toHaveLength(12)
    expect(wrapper.text()).not.toContain('第 13 题')
    await wrapper.findAll('button[aria-label="取消收藏"]')[0].trigger('click')
    await flushPromises()
    expect(wrapper.findAll('.question-card')).toHaveLength(12)
    expect(wrapper.text()).toContain('第 13 题')

    wrapper.unmount()

    const tailWrapper = mount(QuestionBank, { props: { progressRecords } })
    await flushPromises()
    await tailWrapper.findAll('button.toggle-button')[0].trigger('click')
    await flushPromises()
    await tailWrapper
      .findAll('.pagination button')
      .find((button) => button.text() === '下一页')!
      .trigger('click')
    await flushPromises()
    expect(tailWrapper.text()).toContain('第 13 题')

    await tailWrapper.get('button[aria-label="取消收藏"]').trigger('click')
    await flushPromises()
    expect(tailWrapper.text()).toContain('第 1 题')
    expect(tailWrapper.text()).toContain('共找到 12 道')
    expect(tailWrapper.find('.pagination').exists()).toBe(false)
  })
})
