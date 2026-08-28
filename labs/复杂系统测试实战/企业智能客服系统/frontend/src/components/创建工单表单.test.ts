import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { describe, expect, it } from 'vitest'
import CreateTicketForm from './CreateTicketForm.vue'

const customers = [
  {
    id: 7,
    displayName: '合成客户',
    email: 'synthetic@example.test',
    customerLevel: 'NORMAL',
  },
]

describe('创建工单表单', () => {
  it('阻止纯空白输入并在提交时统一去除首尾空格', async () => {
    const wrapper = mount(CreateTicketForm, {
      props: { customers, saving: false },
    })
    await nextTick()

    await wrapper.find('input[placeholder="简要描述客户问题"]').setValue('   ')
    await wrapper.find('textarea').setValue('合成问题描述')
    await wrapper.find('form').trigger('submit')

    expect(wrapper.text()).toContain('标题不能为空')
    expect(wrapper.emitted('submit')).toBeUndefined()

    await wrapper.find('input[placeholder="简要描述客户问题"]').setValue('  合成登录问题  ')
    await wrapper.find('textarea').setValue('  仅用于公开学习的合成描述。  ')
    await wrapper.find('form').trigger('submit')

    expect(wrapper.emitted('submit')).toHaveLength(1)
    expect(wrapper.emitted('submit')?.[0]?.[0]).toMatchObject({
      customerId: 7,
      title: '合成登录问题',
      description: '仅用于公开学习的合成描述。',
      category: 'ACCOUNT',
      priority: 'MEDIUM',
    })
  })

  it('没有客户时给出明确空状态并禁止提交', async () => {
    const wrapper = mount(CreateTicketForm, {
      props: { customers: [], saving: false },
    })

    expect(wrapper.text()).toContain('暂无可用客户')
    expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeDefined()
  })
})
