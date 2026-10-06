<template>
  <DsEmptyState
    v-if="!list.length"
    icon="i-lucide-bar-chart-3"
    title="Нет данных для диаграмм"
    description="Под выбранные условия не подходит ни одна позиция. Сбросьте фильтры, чтобы увидеть аналитику."
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
    <div class="grid grid-cols-1 gap-4 lg:grid-cols-3">
      <div
        v-for="insight in insights"
        :key="insight.text"
        class="flex flex-col gap-2 rounded-xl bg-elevated p-6"
      >
        <p class="text-text-primary">
          <span class="text-h2">{{ insight.value }}</span>
          <span class="ml-1 text-caption text-text-muted">{{ insight.unit }}</span>
        </p>
        <p class="text-caption text-text-secondary">
          {{ insight.text }}
        </p>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <DsPanelCard title="Распределение по категориям">
        <p class="mb-4 text-caption text-text-muted">
          Какие темы Верховный Суд разбирает чаще всего. Нажмите на категорию, чтобы отфильтровать позиции.
        </p>
        <EducationDoughnutChart
          :items="categoryRows"
          @select="edu.toggleCategory(Number($event))"
        />
      </DsPanelCard>

      <DsPanelCard title="Исходы дел">
        <p class="mb-4 text-caption text-text-muted">
          Чем заканчиваются споры в позициях обзора.
        </p>
        <EducationBarChart
          :items="outcomeRows"
          :active-key="edu.filters.outcome"
          @select="edu.toggleOutcome($event)"
        />
      </DsPanelCard>

      <DsPanelCard title="Топ-10 норм">
        <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
          <p class="text-caption text-text-muted">
            На какие нормы суды опираются чаще всего.
          </p>
          <div
            class="flex gap-2"
            role="group"
            aria-label="Уровень группировки"
          >
            <UButton
              v-for="option in normLevels"
              :key="option.value"
              :color="normLevel === option.value ? 'primary' : 'neutral'"
              variant="soft"
              :aria-pressed="normLevel === option.value"
              @click="normLevel = option.value"
            >
              {{ option.label }}
            </UButton>
          </div>
        </div>
        <EducationBarChart
          :items="normRows"
          horizontal
          :active-key="normLevel === 'tag' ? edu.filters.norm : ''"
          @select="normLevel === 'tag' ? edu.toggleNorm($event) : undefined"
        />
      </DsPanelCard>

      <DsPanelCard title="Кто фигурирует в делах">
        <p class="mb-4 text-caption text-text-muted">
          Какие категории лиц чаще становятся участниками споров.
        </p>
        <EducationBarChart
          :items="subjectRows"
          horizontal
          :active-key="edu.filters.subject"
          @select="edu.toggleSubject($event)"
        />
      </DsPanelCard>

      <DsPanelCard
        title="Суммы, обращённые в доход РФ"
        class="lg:col-span-2"
      >
        <p class="mb-4 text-caption text-text-muted">
          Позиции, где обзор называет взысканную сумму. Ширина полосы — в логарифмической шкале: суммы различаются в тысячи раз.
        </p>
        <ul
          v-if="amountRows.length"
          class="flex flex-col gap-3"
        >
          <li
            v-for="row in amountRows"
            :key="row.id"
            class="grid grid-cols-[auto_1fr_auto] items-center gap-3"
          >
            <EducationNumberChip :id="row.id" />
            <div class="flex min-w-0 flex-col gap-1.5">
              <span class="text-caption text-text-primary">{{ row.title }}</span>
              <span
                class="block h-2 overflow-hidden rounded-full bg-default"
                aria-hidden="true"
              >
                <span
                  class="block h-full rounded-full bg-primary"
                  :style="{ width: `${row.width}%` }"
                />
              </span>
            </div>
            <span class="text-base font-semibold text-text-primary">{{ formatAmount(row.amount) }}</span>
          </li>
        </ul>
        <p
          v-else
          class="text-caption text-text-muted"
        >
          В текущей выборке нет позиций с названной суммой взыскания.
        </p>
      </DsPanelCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { OUTCOME_NONE, OUTCOME_NONE_LABEL, capitalize, categoryColor, formatAmount, outcomeStyle } from '~/utils/education'

const edu = useEducationReview()
const list = edu.filtered

type NormLevel = 'tag' | 'act'
const normLevel = ref<NormLevel>('tag')
const normLevels: Array<{ value: NormLevel, label: string }> = [
  { value: 'tag', label: 'Статьи' },
  { value: 'act', label: 'Акты' },
]

function countBy<T>(pick: (position: (typeof list.value)[number]) => T | T[]) {
  const counts = new Map<T, number>()
  for (const position of list.value) {
    for (const key of [pick(position)].flat() as T[]) counts.set(key, (counts.get(key) ?? 0) + 1)
  }
  return counts
}

const categoryRows = computed(() => {
  const counts = countBy(position => position.category)
  return edu.categories.value
    .filter(category => counts.get(category.id))
    .map(category => ({
      key: String(category.id),
      label: category.short_name,
      title: category.name,
      count: counts.get(category.id) ?? 0,
      colorVar: categoryColor(category.color).cssVar,
    }))
})

const outcomeRows = computed(() => {
  const counts = countBy(position => position.outcome || OUTCOME_NONE)
  const rows = (edu.review.value?.outcomes ?? [])
    .filter(outcome => counts.get(outcome.id))
    .map(outcome => ({
      key: outcome.id,
      label: capitalize(outcome.label),
      count: counts.get(outcome.id) ?? 0,
      colorVar: outcomeStyle(outcome.id).cssVar,
    }))
  if (counts.get(OUTCOME_NONE)) {
    rows.push({
      key: OUTCOME_NONE,
      label: OUTCOME_NONE_LABEL,
      count: counts.get(OUTCOME_NONE) ?? 0,
      colorVar: '--ui-color-neutral-400',
    })
  }
  return rows
})

const normRows = computed(() => {
  const counts = normLevel.value === 'tag'
    ? countBy(position => position.legal_basis.map(norm => norm.tag))
    : countBy(position => [...new Set(position.legal_basis.map(norm => norm.act))])
  return [...counts]
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0], 'ru'))
    .slice(0, 10)
    .map(([key, count], index) => {
      const act = normLevel.value === 'tag'
        ? edu.review.value?.positions.flatMap(p => p.legal_basis).find(norm => norm.tag === key)?.act
        : key
      return {
        key,
        label: key,
        count,
        title: key,
        note: edu.actByAbbr.value.get(act ?? '')?.full_name,
        colorVar: index === 0 ? '--ui-color-primary-700' : '--ui-color-primary-500',
      }
    })
})

const subjectRows = computed(() =>
  [...countBy(position => position.subjects)]
    .sort((a, b) => b[1] - a[1])
    .map(([key, count]) => ({ key, label: key, count })),
)

const amountRows = computed(() => {
  const withAmount = list.value
    .filter(position => position.amount)
    .sort((a, b) => (b.amount ?? 0) - (a.amount ?? 0))
  const max = Math.log10(Math.max(...withAmount.map(p => p.amount ?? 0), 10))
  const min = 6
  return withAmount.map(position => ({
    id: position.id,
    title: position.title,
    amount: position.amount ?? 0,
    width: Math.max(4, ((Math.log10(position.amount ?? 1) - min) / Math.max(max - min, 0.1)) * 100),
  }))
})

const insights = computed(() => {
  const total = list.value.length
  const top = [...categoryRows.value].sort((a, b) => b.count - a.count)[0]
  const favor = list.value.filter(position => position.in_favor_of_official)
  const remanded = list.value.filter(position => position.outcome === 'remanded').length
  return [
    {
      value: top?.count ?? 0,
      unit: `из ${total}`,
      text: top ? `позиций — по теме «${top.title}»: самая крупная тема в текущей выборке.` : '',
    },
    {
      value: favor.length,
      unit: `из ${total}`,
      text: `позиций решены в пользу служащего или ответчика${favor.length ? ` (№ ${favor.map(p => p.id).join(', ')})` : ''}: решающими были доказательства законности своих действий и доходов.`,
    },
    {
      value: remanded,
      unit: 'дел',
      text: 'направлены на новое рассмотрение: вышестоящие суды поправили нижестоящие в оценке обстоятельств дела.',
    },
  ]
})
</script>
