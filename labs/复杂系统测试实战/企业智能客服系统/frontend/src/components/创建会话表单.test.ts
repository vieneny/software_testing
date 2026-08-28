import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { describe, expect, it } from 'vitest'
import CreateConversationForm from './创建会话表单.vue'

describe('创建会话表单', () => {
  it('校验并规范化客户会话输入', async () => {
    const wrapper = mount(CreateConversationForm, {
      props: {
        saving: false,
        customers: [
          {
            id: 7,
            displayName: '合成客户',
            email: 'synthetic@example.test',
            customerLevel: 'NORMAL',
          },
        ],
      },
    })
    await nextTick()

    await wrapper.find('input').setValue('  合成登录咨询  ')
    await wrapper.find('textarea').setValue('  这是公开合成的首条客户消息。  ')
    await wrapper.find('form').trigger('submit')

    expect(wrapper.emitted('submit')?.[0]?.[0]).toEqual({
      customerId: 7,
      channel: 'WEB',
      subject: '合成登录咨询',
      initialMessage: '这是公开合成的首条客户消息。',
    })
  })
})
