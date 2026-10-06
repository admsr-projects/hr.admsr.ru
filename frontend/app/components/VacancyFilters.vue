<template>
  <section
    aria-label="Фильтры вакансий"
    class="flex flex-col gap-4 rounded-xl bg-elevated p-6"
  >
    <UInput
      :model-value="model.q"
      type="search"
      icon="i-lucide-search"
      placeholder="Поиск по названию вакансии"
      aria-label="Поиск по названию вакансии"
      class="w-full"
      @update:model-value="set('q', String($event ?? ''))"
    />

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <UFormField label="Подразделение">
        <USelectMenu
          :model-value="model.branch"
          :items="branchItems"
          value-key="value"
          :search-input="{
            placeholder: 'Поиск подразделения…',
            icon: 'i-lucide-search',
          }"
          class="w-full"
          @update:model-value="set('branch', $event as string)"
        />
      </UFormField>

      <UFormField label="Опыт работы">
        <USelect
          :model-value="model.required_experience"
          :items="experienceItems"
          class="w-full"
          @update:model-value="set('required_experience', $event as string)"
        />
      </UFormField>

      <UFormField label="Тип должности">
        <USelect
          :model-value="model.job_type"
          :items="jobTypeItems"
          class="w-full"
          @update:model-value="set('job_type', $event as string)"
        />
      </UFormField>
    </div>

    <div class="flex flex-wrap items-center justify-between gap-3">
      <p
        class="text-caption text-text-muted"
        aria-live="polite"
        aria-atomic="true"
      >
        Найдено: <span class="font-semibold text-text-primary">{{ total }}</span>
      </p>
      <UButton
        v-if="hasActive"
        label="Сбросить фильтры"
        icon="i-lucide-x"
        color="neutral"
        variant="soft"
        class="cursor-pointer bg-default"
        @click="reset"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import { ofoList } from '~/data/ofo-list'
import { VACANCY_FILTER_ALL, emptyVacancyFilters, type VacancyFilterState } from '~/data/vacancy-filters'

interface FilterOption {
  id: number
  name: string
}

defineProps<{
  total: number
}>()

const model = defineModel<VacancyFilterState>({ required: true })

const config = useRuntimeConfig()
const ALL = VACANCY_FILTER_ALL

function loadOptions(field: string) {
  return useAsyncData(
    `vacancy-filter-${field}`,
    () => $fetch<FilterOption[]>(`${config.public.apiBaseUrl}/api/vacancy-filters/${field}/`),
    { server: false },
  )
}

const [{ data: experience }, { data: jobTypes }] = await Promise.all([
  loadOptions('required_experience'),
  loadOptions('job_type'),
])

function toItems(allLabel: string, options: FilterOption[] | null | undefined) {
  return [
    { label: allLabel, value: ALL },
    ...(options ?? []).map(option => ({ label: option.name, value: String(option.id) })),
  ]
}

const experienceItems = computed(() => toItems('Любой опыт', experience.value))
const jobTypeItems = computed(() => toItems('Любой тип', jobTypes.value))

// Подразделение из ссылки (?org=…) может не входить в утверждённый список — показываем и его
const branchItems = computed(() => {
  const names: string[] = [...ofoList]
  if (model.value.branch !== ALL && !names.includes(model.value.branch)) names.push(model.value.branch)
  return [
    { label: 'Все подразделения', value: ALL },
    ...names.map(name => ({ label: name, value: name })),
  ]
})

const hasActive = computed(() =>
  model.value.q.trim() !== ''
  || model.value.branch !== ALL
  || model.value.required_experience !== ALL
  || model.value.job_type !== ALL,
)

function set<K extends keyof VacancyFilterState>(key: K, value: VacancyFilterState[K]) {
  model.value = { ...model.value, [key]: value }
}

function reset() {
  model.value = emptyVacancyFilters()
}
</script>
