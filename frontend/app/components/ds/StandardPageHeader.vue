<template>
  <header class="ds-cover relative overflow-hidden rounded-xl p-6 text-white sm:p-8">
    <div
      class="relative z-10 grid grid-cols-1 gap-6"
      :class="$slots.aside ? 'lg:grid-cols-[minmax(0,1fr)_18rem] lg:items-end lg:gap-8' : undefined"
    >
      <div class="flex flex-col gap-4">
        <p
          v-if="overline"
          class="text-overline font-semibold uppercase tracking-[0.14em] text-white/80"
        >
          {{ overline }}
        </p>
        <h1 class="text-h1 text-balance">
          {{ title }}
        </h1>
        <p
          v-if="description"
          class="max-w-2xl whitespace-pre-line text-body text-pretty text-white/90"
        >
          {{ description }}
        </p>
        <div
          v-if="$slots.actions"
          class="flex flex-wrap gap-3 pt-2"
        >
          <slot name="actions" />
        </div>
      </div>

      <div
        v-if="$slots.aside"
        class="rounded-lg bg-[#1b1a40]/50 p-4 backdrop-blur-sm"
      >
        <slot name="aside" />
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  /** Надзаголовок капсом над названием страницы */
  overline?: string
  description?: string
}>()
</script>

<style scoped>
/* Обложка страницы: фирменный градиент 135° (индиго → бирюза → мята), в тёмной теме начинается с графита */
.ds-cover {
  background: linear-gradient(135deg, #2c238b 0%, #347d88 58%, #50c891 100%);
}

:global(.dark) .ds-cover {
  background: linear-gradient(135deg, #1b1a40 0%, #2c238b 38%, #347d88 78%, #50c891 100%);
}

/* Ромбовидный паттерн, затухает от правого верхнего угла к центру */
.ds-cover::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: min(45%, 28rem);
  height: 100%;
  pointer-events: none;
  opacity: 0.32;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40' viewBox='0 0 40 40'%3E%3Cpath d='M20 4 36 20 20 36 4 20Z' fill='none' stroke='%23FFFFFF' stroke-width='1.5'/%3E%3Cpath d='M20 13 27 20 20 27 13 20Z' fill='%23FFFFFF' fill-opacity='.35'/%3E%3C/svg%3E");
  background-size: 2.5rem 2.5rem;
  -webkit-mask-image: linear-gradient(225deg, #000 0%, rgb(0 0 0 / 45%) 45%, transparent 80%);
  mask-image: linear-gradient(225deg, #000 0%, rgb(0 0 0 / 45%) 45%, transparent 80%);
}
</style>
