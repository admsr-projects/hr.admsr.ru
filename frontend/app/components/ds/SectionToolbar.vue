<template>
  <div
    class="overflow-hidden border-b border-default bg-default/75 backdrop-blur"
    :class="sticky ? 'sticky top-[var(--ui-header-height,4rem)] z-40' : undefined"
  >
    <div
      ref="scroller"
      class="ds-container flex h-12 items-center max-lg:overflow-x-auto max-lg:overflow-y-hidden max-lg:scrollbar-none"
      role="navigation"
      aria-label="Навигация по разделу"
    >
      <UNavigationMenu
        :items="items"
        highlight
        highlight-color="primary"
        variant="link"
        class="flex-none -mx-2.5 -mb-px lg:min-w-0 lg:flex-1"
        :ui="{ link: 'shrink-0 whitespace-nowrap', linkLabel: 'overflow-visible text-clip' }"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

withDefaults(defineProps<{
  items: NavigationMenuItem[]
  sticky?: boolean
}>(), {
  sticky: true,
})

// На узком экране полоса прокручивается — показываем активный пункт
const scroller = ref<HTMLElement | null>(null)

onMounted(() => {
  const active = scroller.value?.querySelector<HTMLElement>('[aria-current="page"]')
  if (!active || !scroller.value) return
  const box = scroller.value
  box.scrollLeft = active.offsetLeft - (box.clientWidth - active.clientWidth) / 2
})
</script>
