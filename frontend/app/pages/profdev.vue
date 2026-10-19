<script setup lang="ts">
import type { TabsItem } from '@nuxt/ui'
import type { TrainingEvent } from '~/components/TrainingEventsList.vue'

useHead({ title: 'Профессиональное развитие' })

const kiosk = useKiosk()

const route = useRoute()
const router = useRouter()
const config = useRuntimeConfig()

type ProfdevTab = 'all' | 'training' | 'leadership' | 'masterclass' | 'best_practice'

const activeTab = ref<ProfdevTab>('all')

const tabItems: TabsItem[] = [
  { label: 'Все', value: 'all' },
  { label: 'Обучение', value: 'training' },
  { label: 'Встречи', value: 'leadership' },
  { label: 'Мастер-классы', value: 'masterclass' },
  { label: 'Лучшие практики', value: 'best_practice' },
]

function resolveTab(value: unknown): ProfdevTab {
  const allowed: ProfdevTab[] = ['all', 'training', 'leadership', 'masterclass', 'best_practice']
  return allowed.includes(value as ProfdevTab) ? value as ProfdevTab : 'all'
}

watch(
  () => route.query.tab,
  (value) => {
    activeTab.value = resolveTab(value)
  },
  { immediate: true },
)

watch(activeTab, (value) => {
  const nextQuery = { ...route.query }
  if (value === 'all') {
    delete nextQuery.tab
  }
  else {
    nextQuery.tab = value
  }
  if (route.query.tab !== nextQuery.tab) {
    router.replace({ query: nextQuery })
  }
})

const { data: events, pending } = await useAsyncData('training-events', () =>
  $fetch<TrainingEvent[]>(`${config.public.apiBaseUrl}/api/training-events/`), {
  server: false,
})

function filterEventsByTab(tab: ProfdevTab) {
  const items = events.value ?? []
  if (tab === 'all') return items
  return items.filter(event => event.event_type === tab)
}

function sectionMetaForTab(tab: ProfdevTab) {
  switch (tab) {
    case 'training':
      return {
        title: 'Обучающие мероприятия',
        description: 'Программы повышения квалификации и профессиональные курсы для сотрудников администрации района.',
        overline: 'Обучение',
      }
    case 'leadership':
      return {
        title: 'Встречи с руководством',
        description: 'Диалоги с руководителями администрации: актуальные вопросы, обмен опытом и обратная связь.',
        overline: 'Встречи',
      }
    case 'masterclass':
      return {
        title: 'Мастер-классы',
        description: 'Практические занятия и разбор кейсов от специалистов отраслевых органов.',
        overline: 'Мастер-классы',
      }
    case 'best_practice':
      return {
        title: 'Лучшие практики',
        description: 'Успешные подходы и решения, которыми делятся команды администрации Сургутского района.',
        overline: 'Практики',
      }
    default:
      return {
        title: 'Расписание мероприятий',
        description: 'Перечень и расписание обучающих мероприятий, встреч с руководством, мастер-классов и лучших практик для сотрудников администрации.',
        overline: 'Расписание',
      }
  }
}
</script>

<template>
  <DsStandardPage
    title="Профессиональное развитие"
    description="Раздел для действующих сотрудников администрации Сургутского района: расписание обучающих программ, встреч с руководством, мастер-классов и лучших практик, а также форма предложений по организации обучения."
  >
    <UTabs
      v-model="activeTab"
      color="primary"
      variant="link"
      :items="tabItems"
      :unmount-on-hide="false"
      class="w-full"
    >
      <template #content="{ item }">
        <div class="mt-6 space-y-10 lg:space-y-12">
          <!-- Презентация — отдельная страница из public/presentations; в ней есть калькулятор, поэтому в киоске не показываем -->
          <DsCalloutPanel
            v-if="!kiosk && item.value === 'training'"
            color="primary"
            icon="i-lucide-presentation"
            title="Обучение муниципальных служащих"
            description="Справочная презентация отдела развития и мотивации персонала: виды программ, как попасть в план обучения, ученический договор и калькулятор срока отработки, ответы на частые вопросы, правовые акты и контакты."
          >
            <template #actions>
              <UButton
                label="Открыть презентацию"
                trailing-icon="i-lucide-arrow-up-right"
                to="/presentations/training.html"
                target="_blank"
                external
                color="primary"
              />
            </template>
          </DsCalloutPanel>

          <DsContentSection
            :title="sectionMetaForTab(item.value as ProfdevTab).title"
            :description="sectionMetaForTab(item.value as ProfdevTab).description"
            :overline="sectionMetaForTab(item.value as ProfdevTab).overline"
            :heading-id="`profdev-${item.value}`"
            :toc-active="activeTab === item.value"
            spacing="lg"
          >
            <TrainingEventsList
              :events="filterEventsByTab(item.value as ProfdevTab)"
              :pending="pending"
              :show-type-badge="item.value === 'all'"
              :empty-title="item.value === 'all'
                ? 'Мероприятия пока не запланированы'
                : 'В этой категории пока нет мероприятий'"
              :empty-description="item.value === 'all'
                ? 'Загляните позже — расписание обновляется по мере появления новых программ.'
                : 'Попробуйте другую вкладку или загляните позже.'"
            />
          </DsContentSection>

          <DsContentSection
            v-if="!kiosk && activeTab === item.value"
            title="Предложения по организации обучения"
            description="Поделитесь идеями по темам, форматам и расписанию мероприятий. Форма не предназначена для подачи официальных обращений."
            overline="Обратная связь"
            heading-id="profdev-feedback"
            spacing="lg"
          >
            <TrainingFeedbackForm />
          </DsContentSection>
        </div>
      </template>
    </UTabs>
  </DsStandardPage>
</template>
