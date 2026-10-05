<template>
  <DsStandardPage
    :title="department.name"
    :description="heroDescription"
  >
    <template #heroActions>
      <UButton
        label="Вакансии органа"
        :to="vacanciesLink"
        color="primary"
        size="lg"
        icon="i-lucide-briefcase"
        class="cursor-pointer"
      />
      <UButton
        label="Обратная связь"
        to="/feedback"
        color="neutral"
        variant="outline"
        size="lg"
        icon="i-lucide-message-square"
        class="cursor-pointer"
      />
    </template>

    <div class="grid gap-4 md:grid-cols-2">
      <DsPanelCard
        title="Контакты"
        heading-id="dept-contacts"
      >
        <ul
          v-if="contactPhone || contactEmail"
          class="space-y-1.5 text-base text-text-muted"
        >
          <li
            v-if="contactPhone"
            class="flex items-center gap-1.5"
          >
            <UIcon
              name="i-lucide-phone"
              class="size-5 shrink-0"
              aria-hidden="true"
            />
            <a
              v-if="phoneHref"
              :href="phoneHref"
              class="hover:text-text-primary transition-colors duration-200"
            >
              {{ contactPhone }}
            </a>
            <span v-else>{{ contactPhone }}</span>
          </li>
          <li
            v-if="contactEmail"
            class="flex items-center gap-1.5"
          >
            <UIcon
              name="i-lucide-mail"
              class="size-5 shrink-0"
              aria-hidden="true"
            />
            <a
              :href="`mailto:${contactEmail}`"
              class="break-all hover:text-text-primary transition-colors duration-200"
            >
              {{ contactEmail }}
            </a>
          </li>
        </ul>
        <p
          v-else
          class="text-base text-text-muted"
        >
          Контактная информация будет опубликована администрацией.
        </p>
      </DsPanelCard>

      <DsPanelCard
        title="Руководитель"
        heading-id="dept-head"
      >
        <div
          v-if="department.head"
          class="flex items-center gap-2.5"
        >
          <UAvatar
            :alt="department.head.name"
            size="xl"
          />
          <div class="min-w-0">
            <p class="text-base font-medium text-text-primary">
              {{ department.head.name }}
            </p>
            <p class="text-sm text-text-muted">
              {{ department.head.role }}
            </p>
          </div>
        </div>
        <p
          v-else
          class="text-base text-text-muted"
        >
          Информация о руководителе будет опубликована администрацией.
        </p>
      </DsPanelCard>
    </div>

    <DsPanelCard
      title="Функции отраслевого функционального органа"
      heading-id="dept-activity"
    >
      <div class="space-y-4 text-base text-text-muted">
        <p
          v-for="(paragraph, index) in aboutParagraphs"
          :key="index"
          class="text-pretty"
        >
          {{ paragraph }}
        </p>

        <div v-if="department.units?.length">
          <h3 class="mb-2 text-base font-semibold text-text-primary">
            {{ unitsHeading }}
          </h3>
          <ul class="space-y-1 ps-5 list-disc marker:text-text-muted/60">
            <li
              v-for="unit in department.units"
              :key="unit"
            >
              {{ unit }}
            </li>
          </ul>
        </div>

        <div v-if="department.tasks?.length">
          <h3 class="mb-2 text-base font-semibold text-text-primary">
            {{ tasksHeading }}
          </h3>
          <ul class="space-y-1 ps-5 list-disc marker:text-text-muted/60">
            <li
              v-for="task in department.tasks"
              :key="task"
            >
              {{ task }}
            </li>
          </ul>
        </div>

        <p v-if="!aboutParagraphs.length && !department.tasks?.length && !department.units?.length">
          Подробное описание функций и задач органа будет дополнено администрацией.
        </p>
      </div>
    </DsPanelCard>

    <DsContentSection
      title="Открытые вакансии"
      :description="careerDescription"
      heading-id="dept-vacancies"
      spacing="lg"
    >
      <div
        v-if="vacanciesPending"
        class="grid grid-cols-1 gap-4 sm:grid-cols-2"
        aria-busy="true"
      >
        <DsSkeletonCard
          v-for="index in 2"
          :key="index"
        />
      </div>

      <div
        v-else-if="relatedVacancies.length"
        class="space-y-6"
      >
        <VacancyCards
          embedded
          title=""
          :vacancies="relatedVacancies"
          :skeleton-count="2"
        />

        <div class="flex flex-wrap gap-3">
          <UButton
            :label="`Все вакансии органа (${relatedVacancies.length})`"
            :to="vacanciesLink"
            color="primary"
            size="lg"
            trailing-icon="i-lucide-arrow-right"
            class="cursor-pointer"
          />
        </div>
      </div>

      <DsCalloutPanel
        v-else
        title="Свободных вакансий пока нет"
        description="В данном органе пока нет свободных вакансий, но вы можете найти предложения в общем разделе."
        icon="i-lucide-briefcase"
        color="primary"
        variant="soft"
      >
        <template #actions>
          <UButton
            label="Смотреть все вакансии"
            to="/vacancies"
            color="primary"
            size="lg"
            trailing-icon="i-lucide-arrow-right"
            class="cursor-pointer"
          />
        </template>
      </DsCalloutPanel>
    </DsContentSection>
  </DsStandardPage>
</template>

<script setup lang="ts">
import type { Department } from '~/data/departments'
import type { Vacancy } from '~/components/VacancyCard.vue'

const props = defineProps<{
  department: Department
  relatedVacancies: Vacancy[]
  vacanciesLink: string
  vacanciesPending?: boolean
}>()

const heroDescription = computed(
  () => props.department.intro ?? props.department.aboutParagraphs?.[0],
)

/** Абзацы описания без того, что уже показано под заголовком страницы */
const aboutParagraphs = computed(() =>
  (props.department.aboutParagraphs ?? []).filter(paragraph => paragraph !== heroDescription.value),
)

const unitsHeading = computed(() =>
  props.department.aboutParagraphs?.length
    ? 'В состав управления входят'
    : 'Структурные подразделения',
)

const tasksHeading = computed(() =>
  props.department.aboutParagraphs?.length
    ? 'Ключевые задачи в работе управления'
    : 'Ключевые задачи',
)

const contactPhone = computed(
  () => props.department.phone ?? props.department.head?.phone,
)

const contactEmail = computed(
  () => props.department.email ?? props.department.head?.email,
)

const phoneHref = computed(() => {
  const digits = (contactPhone.value ?? '').replace(/[^\d+]/g, '')
  return digits ? `tel:${digits}` : undefined
})

const vacancyLabel = computed(() => {
  const count = props.relatedVacancies.length
  const mod10 = count % 10
  const mod100 = count % 100

  if (mod10 === 1 && mod100 !== 11) return 'актуальная вакансия'
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return 'актуальные вакансии'
  return 'актуальных вакансий'
})

const careerDescription = computed(() => {
  if (props.relatedVacancies.length) {
    return `В органе сейчас ${props.relatedVacancies.length} ${vacancyLabel.value}`
  }
  return 'Актуальные предложения по работе в администрации Сургутского района'
})
</script>
