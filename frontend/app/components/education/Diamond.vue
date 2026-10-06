<template>
  <svg
    viewBox="0 0 40 40"
    class="shrink-0"
    :class="size"
    aria-hidden="true"
  >
    <polygon
      points="20,2 38,20 20,38 2,20"
      class="transition-colors duration-150 motion-reduce:transition-none"
      :class="[onDefault ? 'fill-[var(--ui-bg-elevated)]' : 'fill-[var(--ui-bg)]', hoverClass]"
    />
    <polygon
      points="20,9 31,20 20,31 9,20"
      fill="none"
      stroke-width="2.5"
      :class="categoryColor(color).stroke"
    />
    <text
      x="20"
      y="24.5"
      text-anchor="middle"
      font-size="12"
      font-weight="700"
      class="fill-current text-text-primary"
    >{{ id }}</text>
  </svg>
</template>

<script setup lang="ts">
import { categoryColor } from '~/utils/education'

withDefaults(defineProps<{
  id: number
  /** Ключ цвета категории (indigo, teal…) */
  color: string
  /** Размер: классы Tailwind */
  size?: string
  /** Ромб лежит на фоне bg-default (иначе на bg-elevated) */
  onDefault?: boolean
  /** Класс заливки при наведении на родителя с классом group */
  hoverClass?: string
}>(), {
  size: 'size-10',
  onDefault: false,
  hoverClass: undefined,
})
</script>
