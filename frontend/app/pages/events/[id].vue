<template>
  <div class="ds-inner">
    <DsBreadcrumbs :items="breadcrumbs" />

    <div class="ds-container pb-12 lg:pb-16">
      <article
        class="mx-auto flex max-w-3xl flex-col gap-6"
        :aria-busy="pending"
      >
        <template v-if="pending">
          <USkeleton class="h-6 w-40" />
          <USkeleton class="h-10 w-full" />
          <USkeleton class="h-10 w-3/4" />
          <USkeleton class="h-24 w-full rounded-xl" />
          <USkeleton class="h-5 w-full" />
          <USkeleton class="h-5 w-11/12" />
        </template>

        <template v-else-if="event">
          <div class="flex flex-wrap items-center gap-2">
            <UBadge
              :label="event.eventTypeLabel"
              color="primary"
              variant="soft"
            />
            <UBadge
              v-if="past"
              label="Завершено"
              icon="i-lucide-check"
              color="neutral"
              variant="soft"
              class="bg-elevated"
            />
            <UBadge
              v-else
              label="Предстоит"
              icon="i-lucide-clock"
              color="success"
              variant="soft"
            />
          </div>

          <h1 class="text-h1 text-text-primary text-balance">
            {{ event.title }}
          </h1>

          <dl class="grid grid-cols-1 gap-4 rounded-xl bg-elevated p-6 sm:grid-cols-2">
            <div class="flex items-start gap-3">
              <span
                class="flex size-10 shrink-0 items-center justify-center rounded-full bg-default text-primary"
                aria-hidden="true"
              >
                <UIcon
                  name="i-lucide-calendar"
                  class="size-5"
                />
              </span>
              <div class="min-w-0">
                <dt class="text-caption text-text-muted">
                  Дата и время
                </dt>
                <dd class="text-base font-semibold text-text-primary">
                  <time :datetime="event.event_date">{{ formatDateTime(event.event_date) }}</time>
                </dd>
              </div>
            </div>

            <div
              v-if="event.location"
              class="flex items-start gap-3"
            >
              <span
                class="flex size-10 shrink-0 items-center justify-center rounded-full bg-default text-primary"
                aria-hidden="true"
              >
                <UIcon
                  name="i-lucide-map-pin"
                  class="size-5"
                />
              </span>
              <div class="min-w-0">
                <dt class="text-caption text-text-muted">
                  Место проведения
                </dt>
                <dd class="text-base font-semibold text-text-primary text-pretty">
                  {{ event.location }}
                </dd>
              </div>
            </div>
          </dl>

          <DsMarkdown
            v-if="event.description?.trim()"
            :source="event.description"
          />

          <DsEmptyState
            v-else
            icon="i-lucide-file-text"
            title="Описание готовится"
            description="Подробности о мероприятии появятся позже."
          />

          <div>
            <UButton
              label="К расписанию"
              icon="i-lucide-arrow-left"
              to="/profdev"
              color="neutral"
              variant="soft"
              class="cursor-pointer"
            />
          </div>
        </template>

        <DsEmptyState
          v-else
          icon="i-lucide-search-x"
          title="Мероприятие не найдено"
          description="Оно снято с публикации или адрес указан неверно."
        >
          <template #action>
            <UButton
              label="К расписанию"
              to="/profdev"
              color="neutral"
              variant="soft"
              class="cursor-pointer"
            />
          </template>
        </DsEmptyState>
      </article>

      <section
        v-if="!pending && event && related.length"
        aria-labelledby="events-related"
        class="mx-auto mt-12 max-w-3xl"
      >
        <h2
          id="events-related"
          class="mb-4 text-h2 text-text-primary"
        >
          Другие мероприятия
        </h2>

        <ul class="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <li
            v-for="item in related"
            :key="item.id"
          >
            <NuxtLink
              :to="`/events/${item.id}`"
              class="flex h-full flex-col gap-2 rounded-xl bg-elevated p-6 transition-colors duration-200 hover:bg-accented motion-reduce:transition-none"
            >
              <time
                :datetime="item.event_date"
                class="text-caption text-text-muted"
              >
                {{ formatDateTime(item.event_date) }}
              </time>
              <span class="text-base font-semibold text-text-primary text-pretty">
                {{ item.title }}
              </span>
            </NuxtLink>
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TrainingEvent } from '~/components/TrainingEventsList.vue'

const config = useRuntimeConfig()
const route = useRoute()

const eventId = computed(() => String(route.params.id ?? ''))

const { data: event, pending } = await useAsyncData(
  () => `training-event-${eventId.value}`,
  () => $fetch<TrainingEvent>(`${config.public.apiBaseUrl}/api/training-events/${eventId.value}/`)
    .catch(() => null),
  { server: false },
)

const { data: list } = await useAsyncData(
  'training-events',
  () => $fetch<TrainingEvent[]>(`${config.public.apiBaseUrl}/api/training-events/`),
  { server: false },
)

useHead(() => ({
  title: event.value?.title ?? 'Мероприятие',
}))

const past = computed(() => (event.value ? new Date(event.value.event_date) < new Date() : false))

// Ближайшие предстоящие мероприятия, кроме текущего
const related = computed(() =>
  (list.value ?? [])
    .filter(item => String(item.id) !== eventId.value && new Date(item.event_date) >= new Date())
    .sort((a, b) => new Date(a.event_date).getTime() - new Date(b.event_date).getTime())
    .slice(0, 3),
)

const breadcrumbs = computed(() => [
  { label: 'Главная', to: '/', icon: 'i-lucide-home' },
  { label: 'Профессиональное развитие', to: '/profdev' },
  { label: event.value?.title ?? 'Мероприятие' },
])

function formatDateTime(value: string) {
  return new Date(value).toLocaleString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>
