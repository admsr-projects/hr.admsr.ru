<template>
  <DsEmptyState
    v-if="!edu.filtered.value.length"
    icon="i-lucide-calendar-x"
    title="Нет позиций для хронологии"
    description="Под выбранные условия не подходит ни одна позиция. Сбросьте фильтры, чтобы увидеть всю хронологию."
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
      v-if="columns.length"
      class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3"
      role="list"
      aria-label="Хронология по годам"
    >
      <section
        v-for="column in columns"
        :key="column.year"
        class="flex min-w-0 flex-col gap-3 rounded-xl bg-elevated p-4"
        role="listitem"
      >
        <h3 class="flex items-baseline justify-between gap-2 text-text-primary">
          <span class="text-h2">{{ column.year }}</span>
          <span class="text-caption font-normal text-text-muted">{{ column.items.length }} поз.</span>
        </h3>
        <EducationTimelineItem
          v-for="position in column.items"
          :key="position.id"
          :position="position"
        />
      </section>
    </div>

    <section
      v-if="undated.length"
      class="flex flex-col gap-3 rounded-xl bg-elevated p-4"
    >
      <h3 class="flex items-baseline gap-2 text-text-primary">
        <span class="text-h3">Без дат в фабуле</span>
        <span class="text-caption font-normal text-text-muted">{{ undated.length }} поз.</span>
      </h3>
      <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <EducationTimelineItem
          v-for="position in undated"
          :key="position.id"
          :position="position"
        />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const edu = useEducationReview()

const columns = computed(() => {
  const years = [...new Set(edu.filtered.value.filter(p => p.year).map(p => p.year as number))].sort()
  return years.map(year => ({ year, items: edu.filtered.value.filter(p => p.year === year) }))
})

const undated = computed(() => edu.filtered.value.filter(p => !p.year))
</script>
