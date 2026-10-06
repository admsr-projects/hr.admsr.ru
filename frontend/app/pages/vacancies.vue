<script setup lang="ts">
import { VACANCY_FILTER_ALL, emptyVacancyFilters } from '~/data/vacancy-filters'

useHead({ title: 'Вакансии' })

interface VacancyListItem {
  id: number
  title: string
  branch?: string | null
  company?: string | null
  [key: string]: unknown
}

const route = useRoute()
const router = useRouter()
const config = useRuntimeConfig()

// Подразделение из ссылки (?org=…), например со страницы отдела
const orgFromRoute = computed(() => {
  const org = route.query.org
  return typeof org === 'string' ? decodeURIComponent(org) : ''
})

const filters = ref({ ...emptyVacancyFilters(), branch: orgFromRoute.value || VACANCY_FILTER_ALL })

// Адрес и фильтр подразделения связаны в обе стороны
watch(orgFromRoute, (org) => {
  const branch = org || VACANCY_FILTER_ALL
  if (filters.value.branch !== branch) filters.value = { ...filters.value, branch }
})

watch(() => filters.value.branch, (branch) => {
  const org = branch === VACANCY_FILTER_ALL ? undefined : branch
  if ((org ?? '') !== orgFromRoute.value) {
    router.replace({ path: '/vacancies', query: { ...route.query, org } })
  }
})

const { data: vacanciesData, pending } = await useAsyncData('vacancies-page', () => {
  const { branch, required_experience, job_type } = filters.value
  const params = new URLSearchParams()
  if (branch !== VACANCY_FILTER_ALL) params.append('branch', branch)
  if (required_experience !== VACANCY_FILTER_ALL) params.append('required_experience', required_experience)
  if (job_type !== VACANCY_FILTER_ALL) params.append('job_type', job_type)
  const queryString = params.toString()
  return $fetch<VacancyListItem[]>(`${config.public.apiBaseUrl}/api/vacancies/${queryString ? `?${queryString}` : ''}`)
}, {
  server: false,
  watch: [
    () => filters.value.branch,
    () => filters.value.required_experience,
    () => filters.value.job_type,
  ],
})

// Поиск по названию — на клиенте, без запроса к серверу
const visibleVacancies = computed(() => {
  const items = vacanciesData.value ?? []
  const query = filters.value.q.trim().toLowerCase()
  if (!query) return items
  return items.filter(item => item.title.toLowerCase().includes(query))
})
</script>

<template>
  <DsStandardPage
    title="Вакансии"
    description="Актуальный перечень вакантных должностей в администрации Сургутского района. Квалификационные требования, оплата труда и условия поступления на муниципальную службу — в одном разделе."
  >
    <DsContentSection
      title="Актуальные вакансии"
      description="Выберите подходящую должность, уточните условия и откликнитесь онлайн"
      overline="Вакансии"
      heading-id="vacancies-list"
      spacing="lg"
    >
      <div class="space-y-6">
        <VacancyFilters
          v-model="filters"
          :total="visibleVacancies.length"
        />

        <VacancyCards
          embedded
          title=""
          :vacancies="visibleVacancies"
          :pending="pending"
          :skeleton-count="6"
        />
      </div>
    </DsContentSection>

    <DsContentSection
      heading-id="vacancies-subscribe"
      toc-label="Подписка на вакансии"
      spacing="lg"
    >
      <VacancySubscribeForm
        block
        heading-id="vacancies-subscribe"
        :initial-branch="orgFromRoute"
      />
    </DsContentSection>

    <DsContentSection
      title="Документы"
      description="Нормативные и информационные материалы о поступлении на муниципальную службу и работе с вакансиями администрации Сургутского района."
      overline="Материалы"
      heading-id="vacancies-documents"
      spacing="lg"
    >
      <VacancyDocumentsList />
    </DsContentSection>

    <DsContentSection
      title="Связанные разделы"
      description="Конкурсы на замещение должностей и программа кадрового резерва администрации Сургутского района"
      overline="Карьера"
      heading-id="vacancies-related"
      spacing="lg"
    >
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <DsLinkCard
          title="Конкурсы"
          description="Действующие конкурсы на замещение вакантных должностей и на включение в кадровый резерв."
          icon="i-lucide-clipboard-list"
          to="/tenders"
        />

        <DsLinkCard
          title="Кадровый резерв"
          description="Как вступить в резерв и развивать карьеру в администрации района."
          icon="i-lucide-users"
          to="/staffreserve"
        />
      </div>
    </DsContentSection>
  </DsStandardPage>
</template>
