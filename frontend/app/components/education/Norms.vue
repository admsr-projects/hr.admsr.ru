<template>
  <DsEmptyState
    v-if="!groups.length"
    icon="i-lucide-scale"
    title="Нормы не найдены"
    description="Под выбранные условия не подходит ни одна позиция. Сбросьте фильтры, чтобы увидеть все нормы."
  >
    <template #action>
      <UButton
        color="neutral"
        variant="soft"
        @click="edu.resetFilters()"
      >
        Сбросить фильтры
      </UButton>
    </template>
  </DsEmptyState>

  <div
    v-else
    class="flex flex-col gap-4"
  >
    <div
      class="flex flex-wrap items-center gap-2"
      role="group"
      aria-label="Сортировка"
    >
      <UButton
        v-for="option in sortOptions"
        :key="option.value"
        :color="sort === option.value ? 'primary' : 'neutral'"
        variant="soft"
        :aria-pressed="sort === option.value"
        @click="sort = option.value"
      >
        {{ option.label }}
      </UButton>
    </div>

    <section
      v-for="group in groups"
      :key="group.abbr"
      class="rounded-xl bg-elevated"
      :aria-label="group.abbr"
    >
      <header class="flex flex-wrap items-start justify-between gap-3 px-6 py-4">
        <div class="flex min-w-0 flex-1 flex-col gap-1">
          <h3 class="text-h3 text-text-primary">
            {{ group.abbr }}
          </h3>
          <p class="text-caption text-text-muted">
            {{ group.fullName }}
          </p>
          <UAlert
            v-if="group.changedNote"
            color="warning"
            variant="soft"
            title="Норма изменена"
            :description="group.changedNote"
            class="mt-2"
          />
        </div>
        <p class="shrink-0 text-caption text-text-muted">
          <span class="text-h2 text-text-primary">{{ group.positions }}</span>
          поз.
        </p>
      </header>

      <ul class="flex flex-col gap-1 px-3 pb-3">
        <li
          v-for="row in group.rows"
          :key="row.tag"
          class="grid grid-cols-1 items-center gap-2 rounded-lg px-3 py-2 sm:grid-cols-[minmax(10rem,14rem)_1fr_auto] sm:gap-4"
        >
          <button
            type="button"
            class="text-left text-caption font-semibold transition-colors duration-150 hover:text-primary motion-reduce:transition-none"
            :class="edu.filters.norm === row.tag ? 'text-primary' : 'text-text-primary'"
            :aria-pressed="edu.filters.norm === row.tag"
            title="Отфильтровать по норме"
            @click="edu.toggleNorm(row.tag)"
          >
            {{ row.tag }}
          </button>
          <div class="flex flex-wrap gap-1.5">
            <EducationNumberChip
              v-for="id in row.ids"
              :id="id"
              :key="id"
            />
          </div>
          <span class="flex items-center justify-end gap-2 text-caption font-semibold text-text-primary">
            <span
              class="block h-1.5 rounded-full bg-primary"
              :style="{ width: `${(row.ids.length / group.max) * 3.5}rem` }"
              aria-hidden="true"
            />
            {{ row.ids.length }}
          </span>
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup lang="ts">
const edu = useEducationReview()

type Sort = 'freq' | 'act'
const sort = ref<Sort>('freq')
const sortOptions: Array<{ value: Sort, label: string }> = [
  { value: 'freq', label: 'По частоте' },
  { value: 'act', label: 'По акту' },
]

const groups = computed(() => {
  // норма → позиции, затем нормы группируем по нормативному акту
  const byTag = new Map<string, { act: string, ids: number[] }>()
  for (const position of edu.filtered.value) {
    for (const norm of position.legal_basis) {
      const entry = byTag.get(norm.tag) ?? { act: norm.act, ids: [] }
      entry.ids.push(position.id)
      byTag.set(norm.tag, entry)
    }
  }

  const byAct = new Map<string, Array<{ tag: string, ids: number[] }>>()
  for (const [tag, { act, ids }] of byTag) {
    byAct.set(act, [...(byAct.get(act) ?? []), { tag, ids }])
  }

  const max = Math.max(1, ...[...byTag.values()].map(entry => entry.ids.length))
  const result = [...byAct].map(([abbr, rows]) => {
    const act = edu.actByAbbr.value.get(abbr)
    return {
      abbr,
      fullName: act?.full_name ?? '',
      changedNote: act?.changed_note ?? '',
      rows: rows.sort((a, b) => b.ids.length - a.ids.length || a.tag.localeCompare(b.tag, 'ru', { numeric: true })),
      positions: new Set(rows.flatMap(row => row.ids)).size,
      max,
    }
  })

  return result.sort((a, b) =>
    sort.value === 'freq'
      ? b.positions - a.positions || a.abbr.localeCompare(b.abbr, 'ru')
      : a.abbr.localeCompare(b.abbr, 'ru'),
  )
})
</script>
