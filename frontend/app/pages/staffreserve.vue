<script setup lang="ts">
interface StaffReservePosition {
  id: number
  title: string
  description: string
  order: number
}

interface StaffReserveInfo {
  purpose?: string
  positions?: StaffReservePosition[]
  additional_content?: string
  updated_at?: string
}

useHead({ title: 'Кадровый резерв' })

const config = useRuntimeConfig()

const { data: info, pending } = await useAsyncData('staff-reserve-info', () =>
  $fetch<StaffReserveInfo>(`${config.public.apiBaseUrl}/api/staff-reserve/`), {
  server: false,
})

const positions = computed(() => info.value?.positions ?? [])
</script>

<template>
  <DsStandardPage
    title="Кадровый резерв"
    description="Информация об организации кадрового резерва в администрации Сургутского района: цели формирования, должности для включения в резерв и архив результатов конкурсов."
  >
    <DsContentSection
      title="Цель формирования кадрового резерва"
      overline="О резерве"
      heading-id="reserve-purpose"
      spacing="lg"
    >
      <div
        v-if="pending"
        class="flex flex-col gap-3 rounded-xl bg-elevated p-6"
        aria-busy="true"
        aria-label="Загрузка информации о кадровом резерве"
      >
        <USkeleton class="h-4 w-full" />
        <USkeleton class="h-4 w-full" />
        <USkeleton class="h-4 w-3/4" />
      </div>

      <div
        v-else
        class="flex items-start gap-4 rounded-xl bg-elevated p-6"
      >
        <span
          class="flex size-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary"
          aria-hidden="true"
        >
          <UIcon
            name="i-lucide-flag"
            class="size-5"
          />
        </span>
        <p class="min-w-0 pt-2 text-base text-text-primary whitespace-pre-line text-pretty">
          {{ info?.purpose }}
        </p>
      </div>
    </DsContentSection>

    <DsContentSection
      v-if="pending || positions.length"
      title="Должности, на которые формируется резерв"
      description="Перечень должностей муниципальной службы с описанием требований к кандидатам для включения в кадровый резерв"
      overline="Должности"
      heading-id="reserve-positions"
      spacing="lg"
    >
      <div
        v-if="pending"
        class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
        aria-busy="true"
      >
        <USkeleton
          v-for="index in 3"
          :key="index"
          class="h-40 w-full rounded-xl"
        />
      </div>

      <ul
        v-else
        class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
      >
        <li
          v-for="position in positions"
          :key="position.id"
        >
          <DsInfoCard
            :title="position.title"
            icon="i-lucide-briefcase"
          >
            {{ position.description }}
          </DsInfoCard>
        </li>
      </ul>
    </DsContentSection>

    <DsContentSection
      v-if="info?.additional_content"
      title="Дополнительная информация"
      heading-id="reserve-extra"
      spacing="lg"
    >
      <div class="flex items-start gap-4 rounded-xl bg-elevated p-6">
        <span
          class="flex size-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary"
          aria-hidden="true"
        >
          <UIcon
            name="i-lucide-info"
            class="size-5"
          />
        </span>
        <p class="min-w-0 pt-2 text-base text-text-primary whitespace-pre-line text-pretty">
          {{ info.additional_content }}
        </p>
      </div>
    </DsContentSection>

    <DsContentSection
      title="Документы"
      description="Нормативные и информационные материалы о формировании и работе кадрового резерва администрации Сургутского района."
      overline="Материалы"
      heading-id="reserve-documents"
      spacing="lg"
    >
      <StaffReserveDocumentsList />
    </DsContentSection>

    <DsContentSection
      title="Результаты конкурсов"
      description="Архив завершённых конкурсов на формирование кадрового резерва: постановление о проведении и постановление о результатах в виде прикреплённых файлов."
      overline="Архив"
      heading-id="competition-results"
      spacing="lg"
    >
      <CompetitionResultsList type-filter="reserve" />
    </DsContentSection>

    <DsContentSection
      title="Связанные разделы"
      description="Другие разделы карьерного портала администрации Сургутского района"
      overline="Карьера"
      heading-id="reserve-related"
      spacing="lg"
    >
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <DsLinkCard
          title="Вакансии"
          description="Актуальный перечень вакантных должностей в администрации Сургутского района."
          icon="i-lucide-briefcase"
          to="/vacancies"
        />

        <DsLinkCard
          title="Конкурсы"
          description="Действующие конкурсы на замещение должностей и формирование кадрового резерва."
          icon="i-lucide-file-badge"
          to="/tenders?type=reserve"
        />
      </div>
    </DsContentSection>
  </DsStandardPage>
</template>
