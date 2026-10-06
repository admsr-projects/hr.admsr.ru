<template>
  <div>
    <div
      v-if="pending"
      class="space-y-4"
      aria-busy="true"
      aria-label="Загрузка конкурсов"
    >
      <DsSkeletonCard
        v-for="index in 2"
        :key="index"
      />
    </div>

    <DsEmptyState
      v-else-if="!competitions.length"
      icon="i-lucide-calendar-off"
      title="В настоящее время конкурсы не проводятся"
      description="Информация о новых конкурсах на замещение должностей и формирование кадрового резерва будет опубликована в этом разделе."
    >
      <template #action>
        <div class="flex flex-wrap justify-center gap-3">
          <UButton
            label="Вакансии"
            to="/vacancies"
            color="primary"
            variant="soft"
            trailing-icon="i-lucide-arrow-right"
            class="cursor-pointer"
          />
          <UButton
            label="Кадровый резерв"
            to="/staffreserve"
            color="neutral"
            variant="soft"
            trailing-icon="i-lucide-arrow-right"
            class="cursor-pointer transition-colors duration-200"
          />
        </div>
      </template>
    </DsEmptyState>

    <ul
      v-else
      class="flex flex-col gap-4"
    >
      <li
        v-for="item in competitions"
        :key="item.id"
      >
        <article
          class="flex min-w-0 flex-col gap-4 rounded-xl bg-elevated p-6"
          :aria-labelledby="`competition-${item.id}-title`"
        >
          <div class="flex flex-wrap items-start justify-between gap-3">
            <h3
              :id="`competition-${item.id}-title`"
              class="min-w-0 flex-1 text-h3 text-text-primary text-balance"
            >
              {{ item.title }}
            </h3>
            <UBadge
              color="primary"
              variant="soft"
              class="shrink-0"
            >
              {{ item.competitionTypeLabel }}
            </UBadge>
          </div>

          <ul
            v-if="item.date_start || item.date_end || item.contact_phones"
            class="flex flex-col gap-2 text-caption text-text-muted sm:flex-row sm:flex-wrap sm:gap-x-6"
          >
            <li
              v-if="item.date_start || item.date_end"
              class="flex items-center gap-2"
            >
              <UIcon
                name="i-lucide-calendar"
                class="size-4 shrink-0 text-primary"
                aria-hidden="true"
              />
              <span>Приём документов:</span>
              <time
                class="font-medium text-text-primary"
                :datetime="item.date_start || item.date_end || undefined"
              >
                {{ formatDateRange(item.date_start, item.date_end) }}
              </time>
            </li>
            <li
              v-if="item.contact_phones"
              class="flex items-start gap-2"
            >
              <UIcon
                name="i-lucide-phone"
                class="mt-0.5 size-4 shrink-0 text-primary"
                aria-hidden="true"
              />
              <span class="whitespace-pre-line text-text-primary">{{ item.contact_phones }}</span>
            </li>
          </ul>

          <UAccordion
            v-if="detailItems(item).length"
            type="multiple"
            :items="detailItems(item)"
            :ui="{
              root: 'flex flex-col gap-2',
              item: 'rounded-lg bg-default border-b-0',
              trigger: 'cursor-pointer px-4 py-3 text-base font-semibold text-text-primary',
              leadingIcon: 'size-5 text-primary',
              body: 'px-4 pb-4 text-body text-text-primary',
            }"
          >
            <template #body="{ item: section }">
              <DsMarkdown :source="section.text" />
            </template>
          </UAccordion>
        </article>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
export interface CompetitionItem {
  id: number
  title: string
  competition_type: 'vacancy' | 'reserve'
  competitionTypeLabel: string
  content?: string
  date_start?: string | null
  date_end?: string | null
  requirements?: string
  acceptance_info?: string
  contact_phones?: string
}

const props = withDefaults(defineProps<{
  typeFilter?: 'vacancy' | 'reserve' | null
}>(), {
  typeFilter: null,
})

const config = useRuntimeConfig()

const { data: allCompetitions, pending } = await useAsyncData(
  'competitions',
  () => $fetch<CompetitionItem[]>(`${config.public.apiBaseUrl}/api/competitions/`),
  { server: false },
)

const competitions = computed(() => {
  const items = allCompetitions.value ?? []
  if (!props.typeFilter) return items
  return items.filter(item => item.competition_type === props.typeFilter)
})

function detailItems(item: CompetitionItem) {
  return [
    { label: 'О конкурсе', icon: 'i-lucide-file-text', text: item.content },
    { label: 'Требования', icon: 'i-lucide-list-checks', text: item.requirements },
    { label: 'Место и время приёма документов', icon: 'i-lucide-map-pin', text: item.acceptance_info },
  ]
    .filter(section => section.text)
    .map(section => ({ ...section, value: `${item.id}-${section.label}` }))
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

function formatDateRange(start?: string | null, end?: string | null) {
  if (start && !end) return `с ${formatDate(start)}`
  if (!start && end) return `по ${formatDate(end)}`
  if (!start || !end) return ''

  const dStart = new Date(start)
  const dEnd = new Date(end)
  const sameYear = dStart.getFullYear() === dEnd.getFullYear()
  const sameMonth = sameYear && dStart.getMonth() === dEnd.getMonth()

  if (sameMonth) {
    const monthYear = dEnd.toLocaleDateString('ru-RU', { month: 'long', year: 'numeric' })
    return `${dStart.getDate()}–${dEnd.getDate()} ${monthYear}`
  }

  if (sameYear) {
    const startPart = dStart.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' })
    const endPart = formatDate(end)
    return `${startPart} — ${endPart}`
  }

  return `${formatDate(start)} — ${formatDate(end)}`
}
</script>
