<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import type { CreateTicketPayload, Customer, TicketPriority } from '../types'

const props = defineProps<{
  customers: Customer[]
  saving: boolean
}>()

const emit = defineEmits<{
  submit: [payload: CreateTicketPayload]
  cancel: []
}>()

const form = reactive<CreateTicketPayload>({
  customerId: 0,
  title: '',
  description: '',
  category: 'ACCOUNT',
  priority: 'MEDIUM',
})
const validationError = ref('')
const remainingDescription = computed(() => 5000 - form.description.length)

watch(
  () => props.customers,
  (customers) => {
    if (!form.customerId && customers.length) {
      form.customerId = customers[0].id
    }
  },
  { immediate: true },
)

function submit() {
  validationError.value = ''
  const title = form.title.trim()
  const description = form.description.trim()
  if (!props.customers.some((customer) => customer.id === form.customerId)) {
    validationError.value = '请选择有效客户'
    return
  }
  if (!title) {
    validationError.value = '标题不能为空'
    return
  }
  if (!description) {
    validationError.value = '问题描述不能为空'
    return
  }
  if (props.saving) return
  emit('submit', { ...form, title, description })
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
      aria-labelledby="create-ticket-title"
      aria-describedby="create-ticket-privacy"
      @submit.prevent="submit"
    >
      <div class="panel-heading">
        <div>
          <p class="eyebrow">CREATE</p>
          <h2 id="create-ticket-title">创建工单</h2>
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
        标题
        <input
          v-model="form.title"
          maxlength="200"
          :disabled="saving"
          required
          autofocus
          placeholder="简要描述客户问题"
        />
      </label>

      <div class="form-grid">
        <label>
          分类
          <select v-model="form.category" :disabled="saving">
            <option value="ACCOUNT">账号</option>
            <option value="REFUND">退款</option>
            <option value="BILLING">账单</option>
            <option value="PRODUCT">产品</option>
            <option value="OTHER">其他</option>
          </select>
        </label>
        <label>
          优先级
          <select v-model="form.priority" :disabled="saving">
            <option v-for="priority in (['LOW', 'MEDIUM', 'HIGH', 'URGENT'] as TicketPriority[])" :key="priority">
              {{ priority }}
            </option>
          </select>
        </label>
      </div>

      <label>
        问题描述
        <textarea
          v-model="form.description"
          rows="5"
          maxlength="5000"
          :disabled="saving"
          required
          placeholder="描述现象、影响范围、复现条件和已尝试操作"
        />
        <small class="character-count">还可输入 {{ remainingDescription }} 字</small>
      </label>

      <p id="create-ticket-privacy" class="privacy-hint">
        提交后将进入工单队列，并保留创建时间、负责人和状态记录。
      </p>
      <p v-if="validationError" class="form-error" role="alert">{{ validationError }}</p>

      <div class="form-actions">
        <button class="secondary-button" type="button" :disabled="saving" @click="$emit('cancel')">
          取消
        </button>
        <button class="primary-button" type="submit" :disabled="saving || !customers.length">
          {{ saving ? '创建中…' : '创建工单' }}
        </button>
      </div>
    </form>
  </div>
</template>
