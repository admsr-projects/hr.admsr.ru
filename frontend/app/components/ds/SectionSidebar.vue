<template>
  <nav
    :aria-label="title"
    class="rounded-md bg-elevated p-3"
  >
    <p class="px-2.5 py-1.5 text-sm font-semibold text-text-primary">
      {{ title }}
    </p>
    <DsSectionSidebarList :items="items" />
  </nav>
</template>

<script setup lang="ts">
import type { SidebarItem } from '~/data/standard-pages'

defineProps<{
  title: string
  items: SidebarItem[]
}>()
</script>
