import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import ConversationDetailPanel from './会话详情面板.vue'
import type { ConversationDetail } from '../types'

const conversation: ConversationDetail = {
  id: 42,
  customerId: 7,
  customerName: '合成客户',
  customerLevel: 'NORMAL',
  channel: 'WEB',
  subject: '公开合成登录咨询',
  state: 'WAITING_AGENT',
  startedAt: '2026-07-28T00:00:00Z',
  lastMessageAt: '2026-07-28T00:02:00Z',
  createdAt: '2026-07-28T00:00:00Z',
  updatedAt: '2026-07-28T00:02:00Z',
  version: 3,
  linkedTicketIds: [],
  messages: [
    {
      id: 1,
      sequence: 1,
      senderType: 'CUSTOMER',
      visibility: 'CUSTOMER',
      authorName: '合成客户',
      content: '客户可见的合成咨询。',
      createdAt: '2026-07-28T00:00:00Z',
    },
    {
      id: 2,
      sequence: 2,
      senderType: 'AGENT',
      visibility: 'INTERNAL',
      authorName: '学习坐席',
      content: '绝不能出现在默认客户视图的内部备注。',
      createdAt: '2026-07-28T00:01:00Z',
    },
  ],
}

describe('会话详情面板', () => {
  it('默认客户视图对内部备注做第二层过滤', () => {
    const wrapper = mount(ConversationDetailPanel, {
      props: {
        conversation,
        loading: false,
        busy: false,
        includeInternal: false,
      },
    })

    expect(wrapper.text()).toContain('客户可见的合成咨询')
    expect(wrapper.text()).not.toContain('绝不能出现在默认客户视图的内部备注')
    expect(wrapper.text()).toContain('内部备注和系统内部状态记录不会显示')
  })

  it('坐席视图展示内部备注并按契约提交公开回复', async () => {
    const wrapper = mount(ConversationDetailPanel, {
      props: {
        conversation,
        loading: false,
        busy: false,
        includeInternal: true,
      },
    })

    expect(wrapper.text()).toContain('绝不能出现在默认客户视图的内部备注')
    await wrapper.find('.conversation-compose textarea').setValue('  合成公开回复。  ')
    await wrapper.find('.conversation-compose .primary-button').trigger('click')

    expect(wrapper.emitted('sendMessage')?.[0]).toEqual([
      'reply',
      '学习坐席',
      '合成公开回复。',
    ])
  })

  it('关闭动作携带目标状态与备注', async () => {
    const wrapper = mount(ConversationDetailPanel, {
      props: {
        conversation,
        loading: false,
        busy: false,
        includeInternal: false,
      },
    })

    await wrapper.find('.conversation-actions input').setValue('合成场景处理完成')
    await wrapper.find('.conversation-actions .secondary-button').trigger('click')

    expect(wrapper.emitted('transition')?.[0]).toEqual([
      'CLOSED',
      '合成场景处理完成',
    ])
  })

  it('并发刷新保留未发送正文，只有明确成功信号才清空', async () => {
    const wrapper = mount(ConversationDetailPanel, {
      props: {
        conversation,
        loading: false,
        busy: false,
        includeInternal: true,
        messageSuccessToken: 0,
      },
    })
    const textarea = wrapper.find<HTMLTextAreaElement>('.conversation-compose textarea')
    await textarea.setValue('等待重试的合成回复')
    await wrapper.setProps({
      conversation: { ...conversation, version: conversation.version + 1 },
    })
    expect(textarea.element.value).toBe('等待重试的合成回复')

    await wrapper.setProps({ messageSuccessToken: 1 })
    expect(textarea.element.value).toBe('')
  })

  it('关联工单成功信号会关闭创建表单', async () => {
    const wrapper = mount(ConversationDetailPanel, {
      props: {
        conversation,
        loading: false,
        busy: false,
        includeInternal: false,
        ticketSuccessToken: 0,
      },
    })
    await wrapper.find('.conversation-actions .secondary-button.compact').trigger('click')
    expect(wrapper.find('.linked-ticket-form').exists()).toBe(true)

    await wrapper.setProps({ ticketSuccessToken: 1 })
    expect(wrapper.find('.linked-ticket-form').exists()).toBe(false)
  })
})
