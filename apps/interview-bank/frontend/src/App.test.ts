import { mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from './App.vue'

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('App', () => {
  it('初始空同步状态不会误显示为告警', () => {
    vi.stubGlobal('fetch', vi.fn(() => new Promise(() => undefined)))
    const wrapper = mount(App)

    expect(wrapper.find('.global-status').exists()).toBe(false)
    expect(wrapper.text()).toContain('测试面试研习室')
    expect(wrapper.text()).toContain('资料来源')
    expect(wrapper.text()).toContain('覆盖题库学习、模拟面试、进度记录与来源核验')
  })
})
