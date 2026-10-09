<template>
  <div class="flex flex-col gap-0.5">
    <dt class="text-xs font-medium text-text-muted">
      {{ label }}
    </dt>
    <dd class="text-sm text-text-primary text-pretty">
      <slot />
      <span
        v-if="refText"
        class="text-text-muted"
      > ({{ refText }})</span>
    </dd>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  /** Пункт акта, из которого взято значение */
  refText?: string | null
}>()
</script>
