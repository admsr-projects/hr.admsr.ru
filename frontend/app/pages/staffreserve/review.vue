<script setup lang="ts">
import { staffReserveReview } from '~/data/staff-reserve-review'

const { meta, system, antiCorruption } = staffReserveReview

useHead({ title: 'Кадровые резервы: порядок формирования' })
</script>

<template>
  <DsStandardPage
    title="Кадровые резервы: порядок формирования"
    :description="meta.subtitle"
    :menu="false"
  >
    <ReserveReviewHero />

    <DsContentSection
      title="Три резерва — три порядка"
      description="Нормативное основание, ответственный орган, лимит кандидатов и сроки — по действующим редакциям актов. Нажмите «Подробнее», чтобы увидеть способы включения, ИПР и основания исключения."
      heading-id="review-overview"
      spacing="lg"
    >
      <ReserveReviewCards />

      <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <section class="flex flex-col gap-4 rounded-xl bg-elevated p-6">
          <h3 class="text-lg font-medium text-text-primary">
            Место резерва в системе подбора кадров
          </h3>
          <ol class="flex flex-col gap-2">
            <li
              v-for="(step, index) in system.steps"
              :key="step.name"
              class="flex items-start gap-3 rounded-lg bg-default p-4"
            >
              <span
                class="flex size-6 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary"
                aria-hidden="true"
              >
                {{ index + 1 }}
              </span>
              <span class="flex flex-col gap-0.5">
                <span class="text-base font-semibold text-text-primary">{{ step.name }}</span>
                <span class="text-sm text-text-muted text-pretty">{{ step.desc }}</span>
              </span>
            </li>
          </ol>
        </section>

        <section class="flex flex-col gap-4 rounded-xl bg-elevated p-6">
          <h3 class="text-lg font-medium text-text-primary">
            Откуда приходят кандидаты
          </h3>
          <ul class="flex flex-col gap-2">
            <li
              v-for="source in system.sources"
              :key="source.name"
              class="flex flex-col gap-0.5 rounded-lg bg-default p-4"
            >
              <span class="text-base font-semibold text-text-primary">{{ source.name }}</span>
              <span class="text-sm text-text-muted text-pretty">{{ source.desc }}</span>
            </li>
          </ul>
        </section>
      </div>
    </DsContentSection>

    <DsContentSection
      title="Требования к кандидатам"
      description="Сравнение условий допуска к конкурсу по трём резервам. Ячейка «Не установлено актом» означает, что соответствующее требование в акте о резерве не закреплено."
      heading-id="review-requirements"
      spacing="lg"
    >
      <ReserveReviewRequirements />
    </DsContentSection>

    <DsContentSection
      title="Этапы формирования резерва"
      description="Последовательность конкурсных процедур со сроками, ответственными и пунктами актов."
      heading-id="review-stages"
      spacing="lg"
    >
      <ReserveReviewStages />
    </DsContentSection>

    <DsContentSection
      title="Уровни готовности"
      description="Одинаковая трёхуровневая шкала во всех трёх резервах: чем ниже уровень, тем больше мероприятий нужно до назначения."
      heading-id="review-levels"
      spacing="lg"
    >
      <ReserveReviewLevels />
    </DsContentSection>

    <DsContentSection
      title="Методы оценки"
      description="Какие методы допускает каждый акт и какие обязательны по единой методике. Выберите строку — справа появится описание и источник."
      heading-id="review-methods"
      spacing="lg"
    >
      <ReserveReviewMethods />
    </DsContentSection>

    <DsContentSection
      title="Перечень должностей"
      description="Целевые управленческие должности учреждений и предприятий — поимённо по приложению 2 к постановлению № 492-нпа; для резерва администрации и кадрового резерва акты устанавливают группы должностей."
      heading-id="review-positions"
      spacing="lg"
    >
      <ReserveReviewPositions />
    </DsContentSection>

    <DsContentSection
      title="Комиссии и антикоррупционные гарантии"
      description="Меры минимизации коррупционных рисков при приёме документов на конкурс на включение в кадровый резерв."
      heading-id="review-commissions"
      spacing="lg"
    >
      <section class="flex flex-col gap-3 rounded-xl bg-success/10 p-6">
        <h3 class="text-lg font-medium text-text-primary">
          Меры минимизации
        </h3>
        <ul class="flex list-disc flex-col gap-1.5 pl-5 text-sm text-text-primary">
          <li
            v-for="measure in antiCorruption.measures"
            :key="measure"
            class="text-pretty"
          >
            {{ measure }}
          </li>
        </ul>
        <p class="text-xs text-text-muted">
          {{ antiCorruption.act }}
        </p>
      </section>
    </DsContentSection>

    <DsContentSection
      title="Нормативная база"
      :description="meta.actsCheckedNote"
      heading-id="review-sources"
      spacing="lg"
    >
      <ReserveReviewSources />
    </DsContentSection>
  </DsStandardPage>
</template>
