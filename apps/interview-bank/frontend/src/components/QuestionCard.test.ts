import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import type { ProgressRecord, Question } from '../types'
import QuestionCard from './QuestionCard.vue'

const question: Question = {
  id: 'core-01-01',
  moduleId: '01',
  moduleName: '测试基础与质量思维',
  title: '测试能证明软件没有缺陷吗？',
  level: '入门',
  kind: '知识题',
  origin: 'reviewed-core',
  roles: ['软件测试'],
  tags: ['风险'],
  focus: '风险意识',
  answer: '不能。测试是在明确范围内提供质量与风险证据。',
  explanation: '有限输入无法穷举全部状态。',
  followups: ['如何提高测试信心？'],
  pitfalls: ['把用例全通过等同于没有风险。'],
  scenario: '',
  sourceIds: ['istqb'],
  relatedQuestionIds: [],
  deepeningRationale: '',
  historicalReference: '',
  updatedAt: '2026-07-29',
}

const progress: ProgressRecord = {
  questionId: question.id,
  favorite: false,
  wrong: false,
  mastery: 'unseen',
  note: '',
}

describe('QuestionCard', () => {
  it('默认隐藏答案，点击后安全展示结构化参考并建立可访问关系', async () => {
    const wrapper = mount(QuestionCard, { props: { question, progress } })

    expect(wrapper.find('[data-testid="answer-content"]').exists()).toBe(false)
    const revealButton = wrapper.get('button[aria-expanded="false"]')
    expect(revealButton.attributes('aria-controls')).toBe(`answer-${question.id}`)
    await revealButton.trigger('click')

    expect(wrapper.find('[data-testid="answer-content"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('测试是在明确范围内提供质量与风险证据')
    expect(wrapper.find('a[href]').exists()).toBe(false)
    expect(wrapper.get('details[open] summary').text()).toBe('原理与实践解释')
    expect(wrapper.get('button[aria-haspopup="dialog"]').text()).toContain('istqb')
  })

  it('把答案中的表格、列表和代码渲染为可读结构，不产生外部链接', async () => {
    const wrapper = mount(QuestionCard, {
      props: {
        question: {
          ...question,
          answer:
            '| 步骤 | 证据 |\n| --- | --- |\n| 定位 | `trace_id` |\n\n- 先缩小范围\n- 再验证假设\n\n[资料](https://evil.example)',
        },
        progress,
      },
    })

    await wrapper.get('button[aria-expanded="false"]').trigger('click')
    expect(wrapper.get('.answer-markdown table').text()).toContain('定位')
    expect(wrapper.get('.answer-markdown code').text()).toBe('trace_id')
    expect(wrapper.findAll('.answer-markdown li')).toHaveLength(2)
    expect(wrapper.find('a[href]').exists()).toBe(false)
  })

  it('收藏和笔记更新通过事件交给进度层保存', async () => {
    const wrapper = mount(QuestionCard, { props: { question, progress } })
    expect(wrapper.get('textarea').attributes('placeholder')).toBe(
      '写下自己的答题结构、薄弱点或待验证问题',
    )

    await wrapper.get('button[aria-label="收藏题目"]').trigger('click')
    expect(wrapper.emitted('update')?.[0][0]).toMatchObject({ favorite: true })

    await wrapper.get('textarea').setValue('先说结论，再说明残余风险。')
    await wrapper.get('button.button--compact').trigger('click')
    expect(wrapper.emitted('update')?.[1][0]).toMatchObject({
      note: '先说结论，再说明残余风险。',
    })
    expect(wrapper.get('[role="status"]').text()).toBe('笔记已保存')
  })

  it('连续修改多个学习状态时基于最新的乐观状态合并', async () => {
    const wrapper = mount(QuestionCard, { props: { question, progress } })

    await wrapper.get('button[aria-label="收藏题目"]').trigger('click')
    await wrapper.get('button[aria-label="加入错题本"]').trigger('click')

    expect(wrapper.emitted('update')?.[1][0]).toMatchObject({
      favorite: true,
      wrong: true,
    })
  })

  it('显示专项深化题与核心题的可审计关系', async () => {
    const wrapper = mount(QuestionCard, {
      props: {
        question: {
          ...question,
          relatedQuestionIds: ['core-05-14'],
          deepeningRationale: '在通用断言分层基础上深化 Java 与 REST Assured 落地。',
        },
        progress,
      },
    })

    await wrapper.get('button[aria-expanded="false"]').trigger('click')
    expect(
      wrapper.get('[data-testid="deepening-rationale"]').attributes('open'),
    ).toBeUndefined()
    await wrapper.get('[data-testid="deepening-rationale"] summary').trigger('click')
    expect(wrapper.get('[data-testid="deepening-rationale"]').text()).toContain(
      'core-05-14',
    )
  })
})
