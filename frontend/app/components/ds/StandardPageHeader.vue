<template>
  <div class="flex flex-col gap-4">
    <header class="flex flex-col gap-4 border-b border-default pb-4">
      <p
        v-if="overline"
        class="-mb-2 text-caption font-semibold text-primary"
      >
        {{ overline }}
      </p>
      <h1 class="text-h1 text-text-primary text-balance">
        {{ title }}
      </h1>
      <p
        v-if="description"
        class="whitespace-pre-line text-base text-text-muted text-pretty"
      >
        {{ description }}
      </p>
    </header>
    <div
      v-if="$slots.actions"
      class="flex flex-wrap gap-3"
    >
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  /** Надзаголовок над названием страницы (основным цветом) */
  overline?: string
  description?: string
}>()
</script>
