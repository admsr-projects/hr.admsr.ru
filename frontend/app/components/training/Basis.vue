<template>
  <p
    v-if="text"
    class="flex items-start gap-1.5 text-overline text-text-muted"
  >
    <UIcon
      name="i-lucide-file-text"
      class="mt-px size-4 shrink-0"
      aria-hidden="true"
    />
    <span>{{ text }}</span>
  </p>
</template>

<script setup lang="ts">
/** Пункт акта, на который опирается утверждение */
defineProps<{
  text?: string
}>()
</script>
