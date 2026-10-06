<template>
  <div>
    <div
      v-if="pending"
      class="flex flex-col gap-3 rounded-xl bg-elevated p-6"
      aria-busy="true"
      aria-label="Загрузка результатов конкурсов"
    >
      <USkeleton
        v-for="index in 3"
        :key="index"
        class="h-12 w-full"
      />
    </div>

    <DsEmptyState
      v-else-if="!results.length"
      icon="i-lucide-file-search"
      :title="emptyTitle"
      :description="emptyDescription"
    />

    <div
      v-else
      class="flex flex-col gap-4"
    >
      <DsTableSearch
        v-if="showControls"
        v-model="search"
        placeholder="Поиск по названию или победителю"
      />

      <div class="rounded-xl bg-elevated p-2 sm:p-4">
        <table class="block w-full text-left sm:table">
          <caption class="sr-only">
            Результаты завершённых конкурсов
          </caption>
          <thead class="max-sm:sr-only sm:table-header-group">
            <tr class="text-caption font-medium text-text-muted">
              <DsSortableTh
                label="Дата"
                class="w-36"
                :sort="ariaSort('date')"
                @sort="toggleSort('date')"
              />
              <DsSortableTh
                label="Конкурс"
                :sort="ariaSort('title')"
                @sort="toggleSort('title')"
              />
              <th
                scope="col"
                class="px-4 py-3 font-medium"
              >
                Победители
              </th>
              <th
                scope="col"
                class="px-4 py-3 font-medium"
              >
                Постановления
              </th>
            </tr>
          </thead>
          <tbody class="block sm:table-row-group">
            <tr
              v-for="entry in paginatedResults"
              :key="entry.id"
              class="block border-t border-default py-3 first:border-t-0 sm:table-row sm:py-0"
            >
              <td class="block px-4 py-1 text-caption text-text-muted sm:table-cell sm:w-36 sm:whitespace-nowrap sm:py-4 sm:align-top">
                <time
                  v-if="entry.completed_at"
                  :datetime="entry.completed_at"
                >
                  {{ formatDate(entry.completed_at) }}
                </time>
                <span v-else>—</span>
              </td>
              <td class="block px-4 py-1 sm:table-cell sm:max-w-md sm:py-4 sm:align-top">
                <p class="text-base font-semibold text-text-primary text-pretty">
                  {{ entry.title }}
                </p>
                <UBadge
                  v-if="showTypeBadge && entry.competitionTypeLabel"
                  :label="entry.competitionTypeLabel"
                  color="primary"
                  variant="soft"
                  class="mt-2"
                />
              </td>
              <td class="block px-4 py-1 sm:table-cell sm:py-4 sm:align-top">
                <ul
                  v-if="entry.winners?.length"
                  class="flex flex-col gap-2"
                >
                  <li
                    v-for="winner in entry.winners"
                    :key="winner.id"
                  >
                    <p class="text-caption font-medium text-text-primary">
                      {{ winner.full_name }}
                    </p>
                    <p
                      v-if="winner.position"
                      class="text-caption text-text-muted text-pretty"
                    >
                      {{ winner.position }}
                    </p>
                  </li>
                </ul>
                <span
                  v-else
                  class="text-caption text-text-muted"
                >
                  Будут опубликованы после подведения итогов
                </span>
              </td>
              <td class="block px-4 py-1 sm:table-cell sm:py-4 sm:align-top">
                <div class="flex flex-wrap gap-2 sm:flex-col sm:items-start">
                  <UButton
                    v-if="entry.decreeConductLink"
                    label="О проведении"
                    icon="i-lucide-download"
                    :to="entry.decreeConductLink"
                    target="_blank"
                    external
                    color="neutral"
                    variant="soft"
                    class="cursor-pointer"
                    :aria-label="`Постановление о проведении: ${entry.title}`"
                  />
                  <UButton
                    v-if="entry.decreeResultsLink"
                    label="О результатах"
                    icon="i-lucide-download"
                    :to="entry.decreeResultsLink"
                    target="_blank"
                    external
                    color="neutral"
                    variant="soft"
                    class="cursor-pointer"
                    :aria-label="`Постановление о результатах: ${entry.title}`"
                  />
                </div>
              </td>
            </tr>
            <tr v-if="!paginatedResults.length">
              <td
                colspan="4"
                class="block px-4 py-6 text-center text-base text-text-muted sm:table-cell"
              >
                Ничего не найдено
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <DsTableFooter
        v-if="showControls"
        v-model:page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        pagination-label="Страницы списка результатов конкурсов"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
export interface CompetitionWinnerItem {
  id: number
  full_name: string
  position?: string
  description?: string
  photo?: string | null
}

export interface CompetitionResultItem {
  id: number
  title: string
  competition_type?: 'vacancy' | 'reserve'
  competitionTypeLabel?: string
  decreeConductLink?: string | null
  decreeResultsLink?: string | null
  completed_at?: string | null
  winners?: CompetitionWinnerItem[]
}

const props = withDefaults(defineProps<{
  typeFilter?: 'vacancy' | 'reserve' | null
}>(), {
  typeFilter: null,
})

const config = useRuntimeConfig()

const showTypeBadge = computed(() => !props.typeFilter)

const emptyTitle = computed(() =>
  props.typeFilter === 'reserve'
    ? 'Результаты конкурсов на кадровый резерв не опубликованы'
    : 'Результаты не опубликованы',
)

const emptyDescription = computed(() =>
  props.typeFilter === 'reserve'
    ? 'Архив завершённых конкурсов на формирование кадрового резерва появится здесь после официального размещения постановлений.'
    : 'Информация о завершённых конкурсах появится здесь после официального размещения постановлений.',
)

const { data: resultsData, pending } = await useAsyncData(
  () => `competition-results-${props.typeFilter ?? 'all'}`,
  () => {
    const query = props.typeFilter ? { type: props.typeFilter } : undefined
    return $fetch<CompetitionResultItem[]>(
      `${config.public.apiBaseUrl}/api/competition-results/`,
      { query },
    )
  },
  { server: false, watch: [() => props.typeFilter] },
)

const results = computed(() => resultsData.value ?? [])

const {
  search,
  pageSize,
  currentPage,
  total,
  showControls,
  pageItems: paginatedResults,
  toggleSort,
  ariaSort,
} = useTableView(results, {
  sort: {
    date: entry => (entry.completed_at ? new Date(entry.completed_at).getTime() : null),
    title: entry => entry.title,
  },
  searchText: entry => [entry.title, ...(entry.winners ?? []).map(winner => winner.full_name)].join(' '),
})

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}
</script>
