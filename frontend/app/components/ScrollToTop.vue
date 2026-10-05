<template>
  <Transition
    enter-active-class="transition duration-200"
    leave-active-class="transition duration-200"
    enter-from-class="translate-y-2 opacity-0"
    leave-to-class="translate-y-2 opacity-0"
  >
    <UButton
      v-if="visible"
      label="Наверх"
      icon="i-lucide-arrow-up"
      color="primary"
      size="lg"
      class="fixed bottom-6 right-6 z-40 cursor-pointer rounded-full shadow-md"
      aria-label="Наверх"
      @click="scrollToTop"
    />
  </Transition>
</template>

<script setup lang="ts">
/** Показываем кнопку, когда страницу прокрутили больше чем на ~1,5 экрана */
const visible = ref(false)

function update() {
  visible.value = window.scrollY > window.innerHeight * 1.5
}

function scrollToTop() {
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' })
}

onMounted(() => {
  update()
  window.addEventListener('scroll', update, { passive: true })
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', update)
})
</script>
