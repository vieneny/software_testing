<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import type {
  ConversationChannel,
  CreateConversationPayload,
  Customer,
} from '../types'

const props = defineProps<{
  customers: Customer[]
  saving: boolean
}>()

const emit = defineEmits<{
  submit: [payload: CreateConversationPayload]
  cancel: []
}>()

const form = reactive<CreateConversationPayload>({
  customerId: 0,
  channel: 'WEB',
  subject: '',
  initialMessage: '',
})
const validationError = ref('')

watch(
  () => props.customers,
  (customers) => {
    if (!form.customerId && customers.length) form.customerId = customers[0].id
  },
  { immediate: true },
)

function submit() {
  validationError.value = ''
  const subject = form.subject.trim()
  const initialMessage = form.initialMessage.trim()
  if (!props.customers.some((customer) => customer.id === form.customerId)) {
    validationError.value = '请选择有效客户'
    return
  }
  if (!subject) {
    validationError.value = '会话主题不能为空'
    return
  }
  if (!initialMessage) {
    validationError.value = '首条客户消息不能为空'
    return
  }
  if (props.saving) return
  emit('submit', { ...form, subject, initialMessage })
}
</script>

<template>
  <div
    class="modal-backdrop"
    role="presentation"
    @click.self="$emit('cancel')"
    @keydown.esc.prevent="$emit('cancel')"
  >
    <form
      class="modal-card"
      role="dialog"
      aria-modal="true"
      aria-labelledby="create-conversation-title"
      @submit.prevent="submit"
    >
      <div class="panel-heading">
        <div>
          <p class="eyebrow">CREATE CONVERSATION</p>
          <h2 id="create-conversation-title">创建客户会话</h2>
        </div>
        <button
          class="icon-button"
          type="button"
          aria-label="关闭"
          :disabled="saving"
          @click="$emit('cancel')"
        >
          ×
        </button>
      </div>

      <label>
        客户
        <select v-model.number="form.customerId" :disabled="saving || !customers.length" required>
          <option v-if="!customers.length" :value="0">暂无可用客户</option>
          <option v-for="customer in customers" :key="customer.id" :value="customer.id">
            {{ customer.displayName }} · {{ customer.customerLevel }}
          </option>
        </select>
      </label>

      <label>
        渠道
        <select v-model="form.channel" :disabled="saving">
          <option
            v-for="channel in (['WEB', 'APP', 'EMAIL', 'PHONE', 'WECHAT'] as ConversationChannel[])"
            :key="channel"
          >
            {{ channel }}
          </option>
        </select>
      </label>

      <label>
        会话主题
        <input
          v-model="form.subject"
          maxlength="200"
          :disabled="saving"
          required
          autofocus
          placeholder="例如：公开演示账号无法登录"
        />
      </label>

      <label>
        首条客户消息
        <textarea
          v-model="form.initialMessage"
          rows="5"
          maxlength="5000"
          :disabled="saving"
          required
          placeholder="描述客户诉求、问题现象和期望结果"
        />
      </label>

      <p class="privacy-hint">
        首条消息将作为客户可见消息保存，创建后可继续补充回复或内部备注。
      </p>
      <p v-if="validationError" class="form-error" role="alert">{{ validationError }}</p>

      <div class="form-actions">
        <button class="secondary-button" type="button" :disabled="saving" @click="$emit('cancel')">
          取消
        </button>
        <button class="primary-button" type="submit" :disabled="saving || !customers.length">
          {{ saving ? '创建中…' : '创建会话' }}
        </button>
      </div>
    </form>
  </div>
</template>
