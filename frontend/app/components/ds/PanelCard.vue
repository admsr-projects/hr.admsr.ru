<template>
  <section
    class="flex flex-col rounded-xl bg-elevated"
    :aria-labelledby="headingId"
  >
    <header class="flex items-center justify-between gap-3 px-6 py-4">
      <h2
        :id="headingId"
        class="flex items-center gap-1.5 text-lg font-medium text-text-primary"
      >
        {{ title }}
        <slot name="title-icon" />
      </h2>
      <slot name="action" />
    </header>
    <div class="flex-1 px-6 pb-6">
      <slot />
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  headingId?: string
}>()
</script>
