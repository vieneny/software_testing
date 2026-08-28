<script setup lang="ts">
import { computed } from 'vue'
import { renderAnswerMarkdown } from '../sourceMarkdown'

const props = defineProps<{
  content: string
}>()

const renderedContent = computed(() => renderAnswerMarkdown(props.content))
</script>

<template>
  <!-- 唯一受控 HTML 出口：禁用原始 HTML/链接/图片，再经 DOMPurify 白名单净化。 -->
  <div class="answer-markdown" v-html="renderedContent"></div>
</template>
