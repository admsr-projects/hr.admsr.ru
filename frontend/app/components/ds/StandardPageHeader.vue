<template>
  <div class="flex flex-col gap-4">
    <header class="flex flex-col gap-4 border-b border-default pb-4">
      <h1 class="text-3xl sm:text-4xl font-bold text-text-primary text-balance">
        {{ title }}
      </h1>
      <p
        v-if="description"
        class="text-base text-text-muted text-pretty"
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
  description?: string
}>()
</script>
