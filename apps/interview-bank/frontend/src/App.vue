<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import InterviewLab from './components/InterviewLab.vue'
import QuestionBank from './components/QuestionBank.vue'
import SourcesView from './components/SourcesView.vue'
import { useProgress } from './progress'
import type { ProgressRecord } from './types'

type View = 'bank' | 'interview' | 'sources'

const activeView = ref<View>('bank')
const mobileMenuOpen = ref(false)
const progressStore = useProgress()
const { records, syncMessage, syncError } = progressStore

const progressSummary = computed(() => {
  const items = Array.from(records.value.values())
  return {
    mastered: items.filter((item) => item.mastery === 'mastered').length,
    wrong: items.filter((item) => item.wrong).length,
    favorite: items.filter((item) => item.favorite).length,
  }
})

function navigate(view: View) {
  activeView.value = view
  mobileMenuOpen.value = false
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function updateProgress(record: ProgressRecord) {
  void progressStore.update(record)
}

onMounted(() => void progressStore.load())
</script>

<template>
  <div class="app-shell">
    <header class="site-header">
      <a class="brand" href="#" aria-label="测试面试研习室首页" @click.prevent="navigate('bank')">
        <span class="brand__mark" aria-hidden="true">T</span>
        <span>
          <strong>测试面试研习室</strong>
          <small>INTERVIEW LAB</small>
        </span>
      </a>

      <button
        class="menu-button"
        type="button"
        :aria-expanded="mobileMenuOpen"
        aria-controls="main-navigation"
        @click="mobileMenuOpen = !mobileMenuOpen"
      >
        菜单
      </button>

      <nav
        id="main-navigation"
        class="main-navigation"
        :class="{ 'is-open': mobileMenuOpen }"
        aria-label="主要导航"
      >
        <button
          type="button"
          :class="{ 'is-active': activeView === 'bank' }"
          :aria-current="activeView === 'bank' ? 'page' : undefined"
          @click="navigate('bank')"
        >
          题库学习
        </button>
        <button
          type="button"
          :class="{ 'is-active': activeView === 'interview' }"
          :aria-current="activeView === 'interview' ? 'page' : undefined"
          @click="navigate('interview')"
        >
          模拟面试
        </button>
        <button
          type="button"
          :class="{ 'is-active': activeView === 'sources' }"
          :aria-current="activeView === 'sources' ? 'page' : undefined"
          @click="navigate('sources')"
        >
          资料来源
        </button>
      </nav>

      <div class="header-progress" aria-label="个人学习概览">
        <span>已掌握 <strong>{{ progressSummary.mastered }}</strong></span>
        <span>错题 <strong>{{ progressSummary.wrong }}</strong></span>
        <span>收藏 <strong>{{ progressSummary.favorite }}</strong></span>
      </div>
    </header>

    <div v-if="syncError" class="global-status global-status--warning" role="status">
      <span>{{ syncError }}</span>
      <button type="button" aria-label="关闭同步提示" @click="syncError = ''">关闭</button>
    </div>
    <div v-if="syncMessage" class="global-status" role="status">
      {{ syncMessage }}
    </div>

    <main id="main-content" class="main-content" tabindex="-1">
      <QuestionBank
        v-if="activeView === 'bank'"
        :progress-records="records"
        @update-progress="updateProgress"
      />
      <InterviewLab v-else-if="activeView === 'interview'" @update-progress="updateProgress" />
      <SourcesView v-else />
    </main>

    <footer class="site-footer">
      <div>
        <strong>测试面试研习室</strong>
        <p>覆盖题库学习、模拟面试、进度记录与来源核验。</p>
      </div>
      <button class="text-button" type="button" @click="navigate('sources')">查看资料来源</button>
    </footer>
  </div>
</template>
