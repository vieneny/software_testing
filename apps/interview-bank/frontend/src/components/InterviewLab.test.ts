import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'
import InterviewLab from './InterviewLab.vue'

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('InterviewLab', () => {
  it('提供岗位、难度、题数和随机种子的真实流程组卷入口', () => {
    const wrapper = mount(InterviewLab)

    expect(wrapper.text()).toContain('真实流程模拟面试')
    expect(wrapper.text()).toContain('目标岗位')
    expect(wrapper.text()).toContain('随机种子')
    expect(wrapper.findAll('select')).toHaveLength(2)
    expect(wrapper.get('input[type="number"]').attributes('min')).toBe('3')
    expect(wrapper.get('button[type="submit"]').text()).toContain('开始模拟面试')
    expect(wrapper.text()).toContain('生成一套可重复练习的面试题组')
    expect(wrapper.text()).not.toContain('真实任职经历')
  })

  it('作答区只提示答题结构，不重复项目级资料政策', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            id: 'session-1',
            role: '测试开发工程师',
            difficulty: '综合',
            seed: 1,
            questions: [
              {
                id: 'core-01-01',
                module_id: '01',
                module_name: '测试基础与质量思维',
                title: '如何说明测试结论？',
                answer: '说明结论、证据与残余风险。',
              },
            ],
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        ),
      ),
    )
    const wrapper = mount(InterviewLab)

    await wrapper.get('button[type="submit"]').trigger('submit')
    await flushPromises()

    expect(wrapper.get('textarea').attributes('placeholder')).toBe(
      '建议只记关键词：结论、步骤、证据指标、风险与复盘。',
    )
    wrapper.unmount()
  })
})
