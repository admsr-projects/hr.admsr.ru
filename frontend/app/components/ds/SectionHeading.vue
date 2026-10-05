<template>
  <header
    class="mb-4"
    :class="align === 'center' ? 'text-center mx-auto max-w-2xl' : undefined"
  >
    <div
      class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between sm:gap-4"
      :class="align === 'center' && 'sm:flex-col sm:items-center'"
    >
      <div :class="align === 'center' ? 'text-center' : ''">
        <h2
          :id="headingId"
          class="text-xl font-bold text-text-primary text-balance scroll-mt-28"
        >
          {{ title }}
        </h2>
        <p
          v-if="description"
          class="text-sm text-text-muted mt-1 text-pretty"
        >
          {{ description }}
        </p>
      </div>
      <div
        v-if="$slots.action"
        class="shrink-0"
      >
        <slot name="action" />
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  title: string
  description?: string
  /** @deprecated Не отображается */
  overline?: string
  headingId?: string
  align?: 'left' | 'center'
}>(), {
  description: undefined,
  overline: undefined,
  headingId: undefined,
  align: 'left',
})
</script>
