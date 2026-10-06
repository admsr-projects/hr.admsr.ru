<template>
  <header
    class="mb-4"
    :class="align === 'center' ? 'text-center mx-auto max-w-2xl' : undefined"
  >
    <div
      class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between sm:gap-4"
      :class="align === 'center' && 'sm:flex-col sm:items-center'"
    >
      <div
        class="flex items-center gap-1.5"
        :class="align === 'center' ? 'justify-center' : ''"
      >
        <h2
          :id="headingId"
          class="text-xl font-bold text-text-primary text-balance scroll-mt-28"
        >
          {{ title }}
        </h2>
        <!-- Описание раздела — в подсказке по кнопке «i», чтобы не загромождать страницу -->
        <UPopover
          v-if="description"
          :content="{ side: 'bottom', align: 'start' }"
        >
          <UButton
            icon="i-lucide-info"
            color="neutral"
            variant="ghost"
            size="sm"
            class="cursor-pointer text-text-muted"
            :aria-label="`Описание раздела «${title}»`"
          />
          <template #content>
            <p class="max-w-xs p-4 text-sm leading-5 text-text-muted text-pretty">
              {{ description }}
            </p>
          </template>
        </UPopover>
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
