<template>
  <!-- В1 — карточка (сетка, главная, блок вакансий органа) -->
  <article
    v-if="layout === 'card'"
    class="flex h-full flex-col gap-4 rounded-lg border border-default bg-default p-6"
  >
    <p
      v-if="organization"
      class="text-sm text-text-muted line-clamp-2"
    >
      {{ organization }}
    </p>

    <h3 class="text-lg font-semibold leading-snug text-text-primary text-balance">
      {{ vacancy.title }}
    </h3>

    <p
      v-if="salary"
      class="text-2xl font-bold text-text-primary"
    >
      {{ salary }}
    </p>

    <ul
      v-if="facts.length"
      class="flex flex-col gap-2 text-sm text-text-muted"
    >
      <li
        v-for="fact in facts"
        :key="fact.text"
        class="flex items-start gap-2"
      >
        <UIcon
          :name="fact.icon"
          class="mt-0.5 size-4 shrink-0"
          aria-hidden="true"
        />
        <span>{{ fact.text }}</span>
      </li>
    </ul>

    <div class="mt-auto flex flex-wrap gap-2 pt-2">
      <UButton
        label="Подробнее"
        :aria-label="`Подробнее о вакансии: ${vacancy.title}`"
        :to="detailsLink"
        color="neutral"
        variant="outline"
      />
      <UButton
        label="Откликнуться"
        :aria-label="`Откликнуться на вакансию: ${vacancy.title}`"
        color="primary"
        @click="$emit('apply', vacancy)"
      />
    </div>
  </article>

  <!-- В2 — строка списка (страница «Вакансии») -->
  <article
    v-else
    class="flex flex-col gap-4 rounded-lg border border-default bg-default p-6 transition-colors duration-200 hover:border-primary motion-reduce:transition-none lg:flex-row lg:items-center lg:gap-8"
  >
    <div class="min-w-0 lg:w-2/5">
      <div class="flex flex-wrap items-center gap-2">
        <h3 class="text-lg font-semibold leading-snug text-text-primary">
          <NuxtLink
            :to="detailsLink"
            class="hover:text-primary focus-visible:outline-2 focus-visible:outline-primary"
          >
            {{ vacancy.title }}
          </NuxtLink>
        </h3>
      </div>
      <p
        v-if="organization"
        class="mt-1 text-sm text-text-muted"
      >
        {{ organization }}
      </p>
    </div>

    <ul
      v-if="rowFacts.length"
      class="flex flex-1 flex-wrap content-center gap-x-5 gap-y-1 text-sm text-text-muted"
    >
      <li
        v-for="fact in rowFacts"
        :key="fact.text"
        class="flex items-center gap-1.5"
      >
        <UIcon
          :name="fact.icon"
          class="size-4 shrink-0"
          aria-hidden="true"
        />
        {{ fact.text }}
      </li>
    </ul>
    <div
      v-else
      class="flex-1"
    />

    <div class="flex items-center justify-between gap-4 lg:justify-end">
      <p
        v-if="salary"
        class="text-lg font-bold text-text-primary"
      >
        {{ salary }}
      </p>
      <UButton
        label="Откликнуться"
        :aria-label="`Откликнуться на вакансию: ${vacancy.title}`"
        color="primary"
        class="shrink-0"
        @click="$emit('apply', vacancy)"
      />
    </div>
  </article>
</template>

<script setup lang="ts">
export interface Vacancy {
  id?: number | string
  title: string
  branch?: string
  company?: string
  location?: string
  salary?: string
  employmentType?: string
  experience?: string
  workSchedule?: string
  requiredExperience?: string
  workingHours?: string
  jobType?: string
  description?: string
  isNew?: boolean
  skills?: string[]
  detailsLink?: string
  created_at?: string
}

const props = withDefaults(defineProps<{
  vacancy: Vacancy
  /** card — карточка для сетки, row — строка списка */
  layout?: 'card' | 'row'
  /** @deprecated Не используется */
  size?: 'default' | 'lg'
}>(), {
  layout: 'card',
  size: 'default',
})

defineEmits<{
  apply: [vacancy: Vacancy]
}>()

/** Структурное подразделение показываем, только если он указан: «Администрация Сургутского района» по умолчанию не подставляем */
const organization = computed(() => {
  const value = (props.vacancy.company || props.vacancy.branch || '').trim()
  return value === 'Администрация Сургутского района' ? '' : value
})

const detailsLink = computed(() => {
  if (props.vacancy.detailsLink) return props.vacancy.detailsLink
  if (props.vacancy.id) return `/vacancyinfo/${props.vacancy.id}`
  return '/vacancies'
})

/** Оклад указывают не всегда: прочерк или пустое значение считаем «не указан» */
const salary = computed(() => {
  const value = (props.vacancy.salary ?? '').trim()
  return /^[-–—\s]*$/.test(value) ? '' : value
})

const facts = computed(() => {
  const v = props.vacancy
  const experience = v.requiredExperience || v.experience
  const items = [
    v.employmentType && { icon: 'i-lucide-clock', text: v.employmentType },
    experience && { icon: 'i-lucide-briefcase', text: `Опыт ${experience}` },
    v.jobType && { icon: 'i-lucide-landmark', text: v.jobType },
  ].filter(Boolean) as { icon: string, text: string }[]

  return items.slice(0, 4)
})

const rowFacts = computed(() => facts.value.filter(fact => fact.icon !== 'i-lucide-clock'))
</script>
