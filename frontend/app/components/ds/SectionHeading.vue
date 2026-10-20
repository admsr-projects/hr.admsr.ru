<template>
  <header
    class="relative mb-4 pb-2.5 after:absolute after:bottom-0 after:left-0 after:h-[3px] after:w-8 after:rounded-full after:bg-[#50C891]"
    :class="align === 'center' ? 'text-center mx-auto max-w-2xl after:left-1/2 after:-translate-x-1/2' : undefined"
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
        <!-- Описание раздела — круглая кнопка «i» с тёмной подсказкой по наведению и фокусу -->
        <span
          v-if="description"
          class="group relative inline-flex"
        >
          <button
            type="button"
            class="inline-grid size-7 cursor-help place-items-center rounded-full text-text-muted transition-colors duration-200 hover:bg-elevated hover:text-text-primary motion-reduce:transition-none"
            :aria-label="`Описание раздела «${title}»`"
            :aria-describedby="tooltipId"
          >
            <UIcon
              name="i-lucide-info"
              class="size-4"
              aria-hidden="true"
            />
          </button>
          <span
            :id="tooltipId"
            role="tooltip"
            class="pointer-events-none absolute left-0 top-[calc(100%+0.375rem)] z-20 hidden w-max max-w-[min(20rem,80vw)] rounded-lg bg-text-primary px-3 py-2 text-caption font-normal text-(--ui-bg) shadow-lg group-focus-within:block group-hover:block"
          >
            {{ description }}
          </span>
        </span>
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
const tooltipId = useId()

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
