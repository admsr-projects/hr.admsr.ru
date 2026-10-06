<template>
  <nav
    aria-label="Навигация киоска"
    class="fixed inset-x-0 bottom-0 z-40 flex items-center gap-3 bg-elevated px-4 py-3 sm:px-6"
    :style="{ height: 'var(--kiosk-nav-height)' }"
  >
    <UButton
      label="Назад"
      icon="i-lucide-arrow-left"
      color="neutral"
      variant="soft"
      class="flex-1 justify-center"
      :disabled="route.path === '/'"
      @click="goBack"
    />
    <UButton
      label="На главную"
      icon="i-lucide-house"
      color="primary"
      class="flex-1 justify-center"
      to="/"
    />
    <UButton
      label="Наверх"
      icon="i-lucide-arrow-up"
      color="neutral"
      variant="soft"
      class="flex-1 justify-center"
      @click="scrollToTop"
    />
  </nav>
</template>

<script setup lang="ts">
const route = useRoute()
const router = useRouter()

function goBack() {
  // Если истории нет (например, после сброса по бездействию), возвращаем на главную
  if (window.history.state?.back) router.back()
  else router.push('/')
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>
