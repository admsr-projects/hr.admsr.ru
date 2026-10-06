<template>
  <div class="flex flex-col gap-3">
    <p
      id="education-lattice-caption"
      class="text-caption font-medium text-text-primary"
    >
      Все позиции обзора — нажмите ромб, чтобы открыть
    </p>

    <svg
      :viewBox="`0 0 ${width} ${height}`"
      class="h-auto w-full max-w-md"
      role="group"
      aria-labelledby="education-lattice-caption"
    >
      <g
        v-for="cell in cells"
        :key="cell.id"
        class="group cursor-pointer outline-none transition-opacity duration-200 motion-reduce:transition-none"
        :class="edu.filteredIds.value.has(cell.id) ? undefined : 'opacity-30'"
        role="button"
        tabindex="0"
        :aria-label="`Позиция ${cell.id}: ${cell.title}`"
        @click="edu.openPosition(cell.id)"
        @keydown.enter.prevent="edu.openPosition(cell.id)"
        @keydown.space.prevent="edu.openPosition(cell.id)"
      >
        <title>№ {{ cell.id }}. {{ cell.title }}</title>
        <polygon
          :points="diamond(cell.x, cell.y, OUTER)"
          class="fill-[var(--ui-bg)] stroke-transparent transition-colors duration-150 group-hover:fill-[var(--ui-bg-accented)] group-focus-visible:stroke-[var(--ui-primary)] motion-reduce:transition-none"
          stroke-width="3"
        />
        <polygon
          :points="diamond(cell.x, cell.y, INNER)"
          fill="none"
          stroke-width="3"
          :class="cell.stroke"
        />
        <text
          :x="cell.x"
          :y="cell.y + 4.5"
          text-anchor="middle"
          font-size="13"
          font-weight="700"
          class="pointer-events-none fill-current text-text-primary"
        >{{ cell.id }}</text>
      </g>
    </svg>

    <ul
      class="flex flex-wrap gap-x-4 gap-y-1 text-overline text-text-muted"
      aria-label="Категории"
    >
      <li
        v-for="category in edu.categories.value"
        :key="category.id"
        class="flex items-center gap-1.5"
      >
        <span
          class="size-2 shrink-0 rotate-45"
          :class="categoryColor(category.color).dot"
          aria-hidden="true"
        />
        {{ category.short_name }}
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { categoryColor } from '~/utils/education'

const edu = useEducationReview()

// Решётка из ромбов: ряды по 5 и 4 ромба со сдвигом, как в обзоре
const R = 30
const OUTER = R * 0.9
const INNER = OUTER * 0.7

function diamond(cx: number, cy: number, size: number) {
  return `${cx},${cy - size} ${cx + size},${cy} ${cx},${cy + size} ${cx - size},${cy}`
}

const cells = computed(() => {
  const result: Array<{ id: number, title: string, x: number, y: number, stroke: string }> = []
  let index = 0
  for (let row = 0; index < edu.positions.value.length; row++) {
    const inRow = row % 2 ? 4 : 5
    for (let column = 0; column < inRow && index < edu.positions.value.length; column++) {
      const position = edu.positions.value[index++]!
      result.push({
        id: position.id,
        title: position.title,
        x: (row % 2 ? 2 * R : R) + column * 2 * R,
        y: R + row * R,
        stroke: categoryColor(edu.categoryById.value.get(position.category)?.color ?? '').stroke,
      })
    }
  }
  return result
})

const width = 10 * R
const height = computed(() => (Math.max(...cells.value.map(cell => cell.y), R) + R))
</script>
