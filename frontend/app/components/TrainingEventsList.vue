<template>
  <div>
    <div
      v-if="pending"
      class="flex flex-col gap-3 rounded-xl bg-elevated p-6"
      aria-busy="true"
      aria-label="Загрузка расписания"
    >
      <USkeleton
        v-for="index in 3"
        :key="index"
        class="h-12 w-full"
      />
    </div>

    <DsEmptyState
      v-else-if="!events.length"
      icon="i-lucide-calendar-x"
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
        placeholder="Поиск по названию, описанию или месту"
      />

      <div class="rounded-xl bg-elevated p-2 sm:p-4">
        <table class="block w-full text-left sm:table">
          <caption class="sr-only">
            Расписание мероприятий
          </caption>
          <thead class="max-sm:sr-only sm:table-header-group">
            <tr class="text-caption font-medium text-text-muted">
              <DsSortableTh
                label="Дата и время"
                class="w-52"
                :sort="ariaSort('date')"
                @sort="toggleSort('date')"
              />
              <DsSortableTh
                label="Статус"
                class="w-36"
                :sort="ariaSort('status')"
                @sort="toggleSort('status')"
              />
              <DsSortableTh
                label="Мероприятие"
                :sort="ariaSort('title')"
                @sort="toggleSort('title')"
              />
              <th
                scope="col"
                class="w-56 px-4 py-3 font-medium"
              >
                Место
              </th>
            </tr>
          </thead>
          <tbody class="block sm:table-row-group">
            <tr
              v-for="event in pageItems"
              :key="event.id"
              class="block border-t border-default py-3 first:border-t-0 sm:table-row sm:py-0"
            >
              <td class="block px-4 py-1 sm:table-cell sm:w-52 sm:py-4 sm:align-top">
                <time
                  :datetime="event.event_date"
                  class="block text-caption"
                  :class="isPast(event.event_date) ? 'text-text-muted' : 'font-medium text-text-primary'"
                >
                  {{ formatDateTime(event.event_date) }}
                </time>
              </td>
              <td class="block px-4 py-1 sm:table-cell sm:w-36 sm:py-4 sm:align-top">
                <UBadge
                  v-if="isPast(event.event_date)"
                  label="Завершено"
                  icon="i-lucide-check"
                  color="neutral"
                  variant="soft"
                  class="bg-default"
                />
                <UBadge
                  v-else
                  label="Предстоит"
                  icon="i-lucide-clock"
                  color="success"
                  variant="soft"
                />
              </td>
              <td class="block px-4 py-1 sm:table-cell sm:py-4 sm:align-top">
                <UBadge
                  v-if="showTypeBadge"
                  :label="event.eventTypeLabel"
                  color="primary"
                  variant="soft"
                  class="mb-2"
                />
                <NuxtLink
                  :to="`/events/${event.id}`"
                  class="block text-base font-semibold text-pretty transition-colors duration-200 hover:text-primary motion-reduce:transition-none"
                  :class="isPast(event.event_date) ? 'text-text-muted' : 'text-text-primary'"
                >
                  {{ event.title }}
                </NuxtLink>
                <p
                  v-if="event.description"
                  class="mt-1 line-clamp-2 text-caption text-text-muted text-pretty"
                >
                  {{ markdownToPlain(event.description) }}
                </p>
                <NuxtLink
                  :to="`/events/${event.id}`"
                  class="mt-2 inline-flex items-center gap-1 text-caption font-medium text-primary underline-offset-2 hover:underline"
                  :aria-label="`Подробнее: ${event.title}`"
                >
                  Подробнее
                  <UIcon
                    name="i-lucide-arrow-right"
                    class="size-4"
                    aria-hidden="true"
                  />
                </NuxtLink>
              </td>
              <td class="block px-4 py-1 text-caption text-text-muted sm:table-cell sm:w-56 sm:py-4 sm:align-top">
                <span
                  v-if="event.location"
                  class="flex items-start gap-2"
                >
                  <UIcon
                    name="i-lucide-map-pin"
                    class="mt-0.5 size-4 shrink-0 text-primary"
                    aria-hidden="true"
                  />
                  <span class="text-pretty">{{ event.location }}</span>
                </span>
              </td>
            </tr>
            <tr v-if="!pageItems.length">
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
        pagination-label="Страницы списка мероприятий"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
export interface TrainingEvent {
  id: number
  title: string
  event_type: string
  eventTypeLabel: string
  description?: string
  event_date: string
  location?: string
}

const props = withDefaults(defineProps<{
  events: TrainingEvent[]
  pending?: boolean
  showTypeBadge?: boolean
  emptyTitle?: string
  emptyDescription?: string
}>(), {
  pending: false,
  showTypeBadge: true,
  emptyTitle: 'Мероприятия пока не запланированы',
  emptyDescription: 'Загляните позже — расписание обновляется по мере появления новых программ.',
})

function isPast(dateStr: string) {
  return new Date(dateStr) < new Date()
}

// По умолчанию сначала ближайшие предстоящие, затем прошедшие от новых к старым
const orderedEvents = computed(() => {
  const time = (event: TrainingEvent) => new Date(event.event_date).getTime()
  const upcoming = props.events.filter(event => !isPast(event.event_date)).sort((a, b) => time(a) - time(b))
  const past = props.events.filter(event => isPast(event.event_date)).sort((a, b) => time(b) - time(a))
  return [...upcoming, ...past]
})

const { search, pageSize, currentPage, total, showControls, pageItems, toggleSort, ariaSort } = useTableView(orderedEvents, {
  sort: {
    date: event => new Date(event.event_date).getTime(),
    status: event => (isPast(event.event_date) ? 1 : 0),
    title: event => event.title,
  },
  searchText: event => [event.title, event.description, event.location].filter(Boolean).join(' '),
})

function formatDateTime(dateStr: string) {
  return new Date(dateStr).toLocaleString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>
