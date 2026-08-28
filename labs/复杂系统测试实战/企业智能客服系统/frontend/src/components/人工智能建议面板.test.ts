import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import AiSuggestionPanel from './AiSuggestionPanel.vue'

describe('AI 坐席建议面板', () => {
  it('限制异常置信度并完整展示 Java 返回的辅助字段', () => {
    const wrapper = mount(AiSuggestionPanel, {
      props: {
        loading: false,
        suggestion: {
          summary: '合成摘要',
          suggestedReply: '合成回复草稿',
          suggestedCategory: 'ACCOUNT',
          suggestedPriority: 'HIGH',
          confidence: 1.4,
          riskFlags: ['HUMAN_REVIEW_REQUIRED'],
          knowledgeReferences: ['公开演示登录说明'],
          suggestedActions: ['检查合成认证服务'],
          mustVerify: ['人工核对身份'],
          degraded: false,
        },
      },
    })

    expect(wrapper.text()).toContain('100%')
    expect(wrapper.find('.confidence-track i').attributes('style')).toContain('width: 100%')
    expect(wrapper.text()).toContain('建议分类：ACCOUNT')
    expect(wrapper.text()).toContain('建议优先级：HIGH')
    expect(wrapper.text()).toContain('公开演示登录说明')
    expect(wrapper.text()).toContain('人工核对身份')
  })

  it('加载时阻止重复生成', () => {
    const wrapper = mount(AiSuggestionPanel, {
      props: { loading: true },
    })

    expect(wrapper.find('.ai-button').attributes('disabled')).toBeDefined()
    expect(wrapper.text()).toContain('正在分析')
  })
})
