<script setup lang="ts">
import type { TabsItem } from '@nuxt/ui'
import type { EducationTab } from '~/composables/useEducationReview'
import type { EducationReview } from '~/utils/education'

const TITLE = '27 правовых позиций по антикоррупционным делам'

useHead({ title: `Нет коррупции! — ${TITLE}` })

const route = useRoute()
const router = useRouter()
const config = useRuntimeConfig()

const { data: review, error } = await useAsyncData('anti-corruption-education', () =>
  $fetch<EducationReview>(`${config.public.apiBaseUrl}/api/anti-corruption-education/`), {
  server: false,
})

const edu = provideEducationReview(review)

const tabs: Array<TabsItem & { value: EducationTab, title: string, description: string }> = [
  {
    label: 'Обзор',
    value: 'overview',
    title: 'Правовые позиции',
    description: 'Каждая карточка — одна позиция Верховного Суда. Откройте карточку, чтобы увидеть дословную формулировку, фабулу дела, применённые нормы и связанные позиции.',
  },
  {
    label: 'Аналитика',
    value: 'analytics',
    title: 'Что показывает практика',
    description: 'Диаграммы строятся по текущей выборке. Нажмите на категорию, исход или норму — они станут фильтром.',
  },
  {
    label: 'Нормы и законы',
    value: 'norms',
    title: 'Нормы и законы',
    description: 'Сколько раз каждая норма упоминается в позициях текущей выборки. Нажмите на норму, чтобы отфильтровать позиции, или на номер, чтобы открыть позицию.',
  },
  {
    label: 'Таймлайн',
    value: 'timeline',
    title: 'Хронология кейсов',
    description: 'Позиция размещена по последнему году событий, упомянутому в её фабуле (подпись — весь упомянутый период). Даты судебных актов обзор не приводит, поэтому позиции без дат в фабуле собраны в отдельный блок.',
  },
  {
    label: 'Полный текст',
    value: 'text',
    title: 'Полный текст обзора',
    description: 'Вводная часть и позиции со сносками. Совпадения с поисковым запросом подсвечиваются.',
  },
]

const activeTab = computed(() => tabs.find(tab => tab.value === edu.tab.value) ?? tabs[0]!)

// Вкладка хранится в адресе (?tab=norms), чтобы ссылкой можно было поделиться
watch(() => route.query.tab, (value) => {
  const tab = tabs.find(item => item.value === value)
  edu.tab.value = tab ? tab.value : 'overview'
}, { immediate: true })

watch(edu.tab, (value) => {
  const query = { ...route.query }
  if (value === 'overview') delete query.tab
  else query.tab = value
  if (route.query.tab !== query.tab) router.replace({ query })
})

// Ссылка вида #pos-12 открывает позицию — в том числе из поиска по порталу
function openFromHash(hash: string) {
  const id = Number(/^#pos-(\d+)$/.exec(hash)?.[1])
  if (id && edu.positionById.value.has(id)) edu.openPosition(id)
}

watch([review, () => route.hash], ([value, hash]) => {
  if (import.meta.client && value) openFromHash(hash)
}, { immediate: true })

// Описание под заголовком: краткое содержание обзора и реквизиты утверждения
const description = computed(() =>
  [review.value?.page.lead, review.value?.page.approved_note].filter(Boolean).join('\n\n') || undefined,
)

const stats = computed(() => {
  const positions = edu.positions.value
  const total = positions.length
  const amounts = positions.filter(position => position.amount)
  const sum = amounts.reduce((acc, position) => acc + (position.amount ?? 0), 0)
  const items = [
    { value: String(total), unit: '', label: 'правовых позиций с примерами из практики' },
    { value: String(edu.categories.value.length), unit: '', label: 'тематических категорий' },
  ]
  if (review.value?.page.period) {
    items.push({ value: review.value.page.period, unit: '', label: 'период изученной судебной практики' })
  }
  if (sum) {
    items.push({
      value: (sum / 1e9).toFixed(1).replace('.', ','),
      unit: 'млрд ₽',
      label: `обращено в доход РФ по ${amounts.length} делам, где сумма названа`,
    })
  }
  items.push(
    {
      value: String(positions.filter(position => position.municipal).length),
      unit: `из ${total}`,
      label: 'позиций касаются муниципальных должностей и службы',
    },
    {
      value: String(positions.filter(position => position.in_favor_of_official).length),
      unit: `из ${total}`,
      label: 'позиций решены в пользу служащего или ответчика',
    },
  )
  return items
})
</script>

<template>
  <DsStandardPage
    :title="review?.page.title || TITLE"
    :overline="review?.page.eyebrow"
    :description="description"
  >
    <div
      v-if="!review && !error"
      class="flex flex-col gap-4"
      aria-busy="true"
    >
      <USkeleton class="h-48 w-full rounded-xl" />
      <div class="grid grid-cols-2 gap-4 lg:grid-cols-3 xl:grid-cols-6">
        <USkeleton
          v-for="index in 6"
          :key="index"
          class="h-24 rounded-xl"
        />
      </div>
      <USkeleton class="h-11 w-full max-w-xl rounded-full" />
    </div>

    <DsEmptyState
      v-else-if="!review?.positions.length"
      icon="i-lucide-book-marked"
      title="Материалы готовятся"
      description="Здесь появятся правовые позиции, разборы дел и памятки по антикоррупционному просвещению."
    />

    <template v-else>
      <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <section
          class="rounded-xl bg-elevated p-6"
          aria-label="Все позиции обзора"
        >
          <EducationLattice class="mx-auto max-w-md" />
        </section>

        <dl class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div
            v-for="stat in stats"
            :key="stat.label"
            class="flex flex-col gap-1 rounded-xl bg-elevated p-4"
          >
            <dt class="text-h2 text-text-primary">
              {{ stat.value }}<span
                v-if="stat.unit"
                class="ml-1 text-caption font-medium text-text-muted"
              >{{ stat.unit }}</span>
            </dt>
            <dd class="text-caption text-text-muted text-pretty">
              {{ stat.label }}
            </dd>
          </div>
        </dl>
      </div>

      <UTabs
        v-model="edu.tab.value"
        color="primary"
        variant="link"
        :items="tabs"
        :content="false"
        class="w-full"
      />

      <EducationFilters />

      <DsContentSection
        :title="activeTab.title"
        :description="activeTab.description"
        spacing="md"
      >
        <EducationCards v-if="edu.tab.value === 'overview'" />
        <EducationAnalytics v-else-if="edu.tab.value === 'analytics'" />
        <EducationNorms v-else-if="edu.tab.value === 'norms'" />
        <EducationTimeline v-else-if="edu.tab.value === 'timeline'" />
        <EducationFullText v-else />
      </DsContentSection>

      <p
        v-if="review.page.source_note"
        class="max-w-3xl text-caption text-text-muted text-pretty"
      >
        {{ review.page.source_note }}
      </p>

      <EducationPositionModal />
    </template>
  </DsStandardPage>
</template>
