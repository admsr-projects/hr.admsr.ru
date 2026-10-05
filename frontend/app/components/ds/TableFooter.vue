<template>
  <div
    v-if="visible"
    class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
  >
    <div class="flex items-center gap-2 text-caption text-text-muted">
      <span :id="labelId">Показывать по</span>
      <USelect
        v-model="pageSize"
        :items="sizeItems"
        :aria-labelledby="labelId"
        class="w-20"
      />
    </div>

    <UPagination
      v-if="total > pageSize"
      v-model:page="page"
      :aria-label="paginationLabel"
      :total="total"
      :items-per-page="pageSize"
      color="neutral"
      variant="subtle"
      :ui="{ first: 'hidden', last: 'hidden' }"
    />
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  /** Строк после поиска. */
  total: number
  /** Строк до поиска: если их не больше минимального размера страницы, футер не нужен. */
  totalAll: number
  paginationLabel: string
}>()

const page = defineModel<number>('page', { required: true })
const pageSize = defineModel<number>('pageSize', { required: true })

const labelId = useId()
const sizeItems = TABLE_PAGE_SIZES.map(size => ({ label: String(size), value: size }))
const visible = computed(() => props.totalAll > TABLE_PAGE_SIZES[0])
</script>
