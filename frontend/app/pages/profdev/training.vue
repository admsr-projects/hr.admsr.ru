<script setup lang="ts">
import type { AccordionItem } from '@nuxt/ui'
import { trainingInfo } from '~/data/training-info'

const TITLE = 'Обучение муниципальных служащих'

useHead({ title: `Профессиональное развитие — ${TITLE}` })

// Ссылки на внешние сайты и ввод значений на киоске недоступны
const kiosk = useKiosk()

const { contacts, federal_norms: norms, federal_law: federalLaw, legal_acts: legalActs, faq } = trainingInfo
const rules = trainingInfo.training_rules

const nf = new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 })

function norm(id: string) {
  return norms.find(item => item.id === id)
}

const retentionMonths = rules.retention_scale.map(band => band.months)

const stats = [
  {
    label: 'Повышение квалификации',
    value: rules.frequency_short,
    hint: `по мере необходимости, ${rules.frequency}`,
    basis: rules.frequency_basis
  },
  {
    label: 'Порог ученического договора',
    value: `свыше ${nf.format(rules.contract_threshold_rub)} ₽`,
    hint: 'для профессиональной переподготовки',
    basis: rules.contract_basis
  },
  {
    label: 'Срок отработки после переподготовки',
    value: `${Math.min(...retentionMonths)}–${Math.max(...retentionMonths)} мес.`,
    hint: 'зависит от стоимости программы',
    basis: rules.retention_basis
  },
  {
    label: 'Сдать копию диплома или удостоверения',
    value: `${rules.report_days} раб. дней`,
    hint: 'после окончания обучения',
    basis: rules.report_basis
  }
]

function bandLabel(band: (typeof rules.retention_scale)[number]) {
  return band.max === null
    ? `свыше ${nf.format(band.min)} ₽`
    : `${nf.format(band.min)}–${nf.format(band.max)} ₽`
}

const faqItems: AccordionItem[] = faq.map((item, index) => ({ label: item.q, value: String(index) }))
</script>

<template>
  <DsStandardPage
    :title="TITLE"
    overline="Муниципальная служба · Дополнительное профессиональное образование"
    description="Дополнительное профессиональное образование: на что вы имеете право, какие условия действуют и что будет, если не отработать срок после переподготовки. Каждое утверждение — со ссылкой на пункт акта."
  >
    <template #heroActions>
      <UBadge
        label="Для муниципальных служащих администрации района"
        color="primary"
        variant="soft"
      />
      <UBadge
        label="Для лиц в кадровом резерве"
        color="primary"
        variant="soft"
      />
      <UBadge
        :label="`Сверено с актами ${trainingInfo.last_checked}`"
        color="neutral"
        variant="soft"
      />
    </template>

    <DsContentSection
      title="Главное в цифрах"
      description="Ключевые параметры из Положения о ДПО. Источник указан под каждой цифрой."
      heading-id="training-overview"
      spacing="lg"
    >
      <dl class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div
          v-for="stat in stats"
          :key="stat.label"
          class="flex flex-col gap-2 rounded-xl bg-elevated p-4"
        >
          <dt class="text-caption text-text-muted">
            {{ stat.label }}
          </dt>
          <dd class="flex flex-col gap-1">
            <span class="text-h2 text-text-primary">{{ stat.value }}</span>
            <span class="text-caption text-text-muted">{{ stat.hint }}</span>
            <TrainingBasis :text="stat.basis" />
          </dd>
        </div>
      </dl>

      <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <TrainingPanel
          title="Почему это важно"
          icon="i-lucide-users"
        >
          <template v-if="norm('fz32')">
            <p class="text-body text-text-primary">
              {{ norm('fz32')!.quote }}
            </p>
            <TrainingBasis :text="`25-ФЗ, ${norm('fz32')!.ref}`" />
          </template>
        </TrainingPanel>

        <TrainingPanel
          title="Кто оплачивает"
          icon="i-lucide-wallet"
        >
          <p class="text-body text-text-primary">
            {{ rules.funding_text }}
          </p>
          <TrainingBasis :text="rules.funding_basis" />
          <p class="text-caption text-text-muted">
            {{ rules.guarantees_text }}
          </p>
          <TrainingBasis :text="rules.guarantees_basis" />
        </TrainingPanel>
      </div>
    </DsContentSection>

    <DsContentSection
      title="Что даёт обучение"
      description="Только правовые факты. Связь с кадровым резервом показывается, если она закреплена в муниципальном акте."
      heading-id="training-benefits"
      spacing="lg"
    >
      <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <TrainingPanel
          v-for="item in [
            { id: 'fz11', title: 'Право на обучение', icon: 'i-lucide-scale' },
            { id: 'fz18', title: 'Связь с аттестацией', icon: 'i-lucide-clipboard-check' }
          ]"
          :key="item.id"
          :title="item.title"
          :icon="item.icon"
        >
          <template v-if="norm(item.id)">
            <p class="text-body text-text-primary">
              {{ norm(item.id)!.quote }}
            </p>
            <p class="text-caption text-text-muted">
              <ULink
                v-if="!kiosk"
                :href="norm(item.id)!.url"
                target="_blank"
                rel="noopener"
                class="text-primary underline"
              >
                25-ФЗ, {{ norm(item.id)!.ref }}
              </ULink>
              <template v-else>
                25-ФЗ, {{ norm(item.id)!.ref }}
              </template>
            </p>
          </template>
        </TrainingPanel>

        <TrainingPanel
          title="Связь с кадровым резервом"
          icon="i-lucide-users"
        >
          <p class="text-body text-text-primary">
            {{ rules.reserve_priority_text }}
          </p>
          <TrainingBasis :text="rules.reserve_priority_basis" />
          <ul class="flex flex-col gap-3">
            <li
              v-for="extra in rules.reserve_extra"
              :key="extra.text"
              class="flex flex-col gap-1 rounded-lg bg-default p-4"
            >
              <p class="text-caption text-text-primary">
                {{ extra.text }}
              </p>
              <TrainingBasis :text="extra.basis" />
            </li>
          </ul>
        </TrainingPanel>
      </div>
    </DsContentSection>

    <DsContentSection
      title="Как это работает"
      description="Путь от планирования до отработки по Положению о ДПО."
      heading-id="training-process"
      spacing="lg"
    >
      <ol class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <li
          v-for="(step, index) in rules.process_steps"
          :key="step.title"
          class="flex flex-col gap-2 rounded-xl bg-elevated p-4"
        >
          <div class="flex items-center justify-between gap-3">
            <span
              class="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary text-caption font-semibold text-inverted"
              aria-hidden="true"
            >
              {{ index + 1 }}
            </span>
            <UBadge
              v-if="step.when"
              :label="step.when"
              color="neutral"
              variant="soft"
            />
          </div>
          <h3 class="text-base font-semibold text-text-primary">
            {{ step.title }}
          </h3>
          <p class="text-caption text-text-muted">
            {{ step.text }}
          </p>
          <TrainingBasis :text="step.basis" />
        </li>
      </ol>

      <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <TrainingPanel
          title="Кого включают в план обучения"
          icon="i-lucide-clipboard-check"
        >
          <ul class="flex list-disc flex-col gap-2 pl-5 text-caption text-text-primary marker:text-primary">
            <li
              v-for="criterion in rules.plan_criteria"
              :key="criterion"
            >
              {{ criterion }}
            </li>
          </ul>
          <p class="text-caption text-text-muted">
            {{ rules.plan_criteria_note }}
          </p>
          <TrainingBasis :text="rules.plan_basis" />
        </TrainingPanel>

        <TrainingPanel
          title="Кто организует обучение"
          icon="i-lucide-building-2"
        >
          <p class="text-body text-text-primary">
            {{ rules.organizer_text }}
          </p>
          <TrainingBasis :text="rules.organizer_basis" />
          <div
            v-if="norm('fz28')"
            class="flex flex-col gap-2 rounded-lg bg-default p-4"
          >
            <p class="text-caption text-text-primary">
              {{ norm('fz28')!.quote }}
            </p>
            <p class="text-caption text-text-muted">
              {{ norm('fz28')!.note }}
            </p>
            <p class="text-caption text-text-muted">
              <ULink
                v-if="!kiosk"
                :href="norm('fz28')!.url"
                target="_blank"
                rel="noopener"
                class="text-primary underline"
              >
                25-ФЗ, {{ norm('fz28')!.ref }}
              </ULink>
              <template v-else>
                25-ФЗ, {{ norm('fz28')!.ref }}
              </template>
            </p>
          </div>
        </TrainingPanel>
      </div>
    </DsContentSection>

    <DsContentSection
      title="Условия, которые важно знать"
      description="Формы обучения, ученический договор, возмещение затрат и исключения из срока отработки."
      heading-id="training-terms"
      spacing="lg"
    >
      <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <TrainingPanel
          title="Формы обучения"
          icon="i-lucide-book-open"
        >
          <ul class="flex list-disc flex-col gap-2 pl-5 text-body text-text-primary marker:text-primary">
            <li
              v-for="form in rules.forms"
              :key="form"
            >
              {{ form }}
            </li>
          </ul>
          <TrainingBasis :text="rules.forms_basis" />
          <ul class="flex flex-col gap-3">
            <li
              v-for="program in rules.programs"
              :key="program.id"
              class="rounded-lg bg-default p-4 text-caption text-text-primary"
            >
              <span class="font-semibold">{{ program.name }}.</span> {{ program.aim }}
            </li>
          </ul>
        </TrainingPanel>

        <TrainingPanel
          title="Ученический договор"
          icon="i-lucide-file-text"
        >
          <p class="text-body text-text-primary">
            Заключается до начала обучения, если вид программы — профессиональная переподготовка, а её стоимость
            <span class="font-semibold">свыше {{ nf.format(rules.contract_threshold_rub) }} ₽</span>.
            В договоре фиксируется срок обязательной работы после обучения.
          </p>
          <TrainingBasis :text="rules.contract_basis" />
          <table class="w-full text-left text-caption">
            <caption class="sr-only">
              Срок обязательной работы по стоимости переподготовки
            </caption>
            <thead>
              <tr class="text-text-muted">
                <th
                  scope="col"
                  class="border-b border-default py-2 pr-3 font-medium"
                >
                  Стоимость переподготовки
                </th>
                <th
                  scope="col"
                  class="border-b border-default py-2 text-right font-medium"
                >
                  Срок отработки
                </th>
              </tr>
            </thead>
            <tbody class="text-text-primary">
              <tr
                v-for="band in rules.retention_scale"
                :key="band.months"
              >
                <td class="border-b border-default py-2 pr-3">
                  {{ bandLabel(band) }}
                </td>
                <td class="border-b border-default py-2 text-right font-medium">
                  {{ band.months }} мес.
                </td>
              </tr>
            </tbody>
          </table>
          <TrainingBasis :text="rules.retention_basis" />
        </TrainingPanel>

        <TrainingPanel
          title="Возмещение затрат"
          icon="i-lucide-wallet"
        >
          <p class="text-body text-text-primary">
            {{ rules.reimbursement_rule }} Основания:
          </p>
          <ul class="flex list-disc flex-col gap-2 pl-5 text-caption text-text-primary marker:text-primary">
            <li
              v-for="ground in rules.reimbursement_grounds"
              :key="ground"
            >
              {{ ground }}
            </li>
          </ul>
          <TrainingBasis :text="rules.reimbursement_basis" />
          <ul class="flex flex-col gap-3">
            <li
              v-for="item in rules.full_reimbursement_cases"
              :key="item.text"
              class="flex flex-col gap-1 rounded-lg bg-default p-4"
            >
              <p class="text-caption text-text-primary">
                {{ item.text }}
              </p>
              <TrainingBasis :text="item.basis" />
            </li>
          </ul>
        </TrainingPanel>

        <TrainingPanel
          title="Уважительные причины увольнения"
          icon="i-lucide-clipboard-check"
        >
          <p class="text-caption text-text-muted">
            При увольнении по собственному желанию по этим причинам затраты не возмещаются:
          </p>
          <ul class="flex list-disc flex-col gap-2 pl-5 text-body text-text-primary marker:text-primary">
            <li
              v-for="excuse in rules.valid_excuses"
              :key="excuse"
            >
              {{ excuse }}
            </li>
          </ul>
          <p class="text-caption text-text-muted">
            {{ rules.valid_excuses_note }}
          </p>
          <TrainingBasis :text="rules.valid_excuses_basis" />
          <div class="flex flex-col gap-2 rounded-lg bg-default p-4">
            <p class="text-caption font-semibold text-text-primary">
              Не входят в срок отработки:
            </p>
            <ul class="flex list-disc flex-col gap-2 pl-5 text-caption text-text-primary marker:text-primary">
              <li
                v-for="period in rules.excluded_periods"
                :key="period"
              >
                {{ period }}
              </li>
            </ul>
            <TrainingBasis :text="rules.excluded_periods_basis" />
          </div>
        </TrainingPanel>
      </div>

      <UAlert
        color="warning"
        variant="soft"
        icon="i-lucide-triangle-alert"
        description="Расчёт носит справочный характер; окончательные условия — в ученическом договоре."
      />
    </DsContentSection>

    <DsContentSection
      v-if="!kiosk"
      title="Калькулятор отработки"
      description="Срок — по шкале приложения 2 к Положению; сумма — пропорционально недоработанному сроку (п. 3.3 договора). Данные никуда не передаются."
      heading-id="training-calc"
      spacing="lg"
    >
      <TrainingCalc />
    </DsContentSection>

    <DsContentSection
      title="Вопросы и ответы"
      heading-id="training-faq"
      spacing="lg"
    >
      <UAccordion
        :items="faqItems"
        :ui="{
          root: 'flex flex-col gap-2',
          item: 'rounded-xl bg-elevated border-b-0',
          trigger: 'cursor-pointer px-6 py-4 text-base font-semibold text-text-primary',
          body: 'px-6 pb-4 text-body text-text-primary'
        }"
      >
        <template #body="{ item }">
          <div class="flex flex-col gap-2">
            <p>{{ faq[Number(item.value)]?.a }}</p>
            <TrainingBasis :text="faq[Number(item.value)]?.basis" />
          </div>
        </template>
      </UAccordion>
    </DsContentSection>

    <DsContentSection
      title="Документы и контакты"
      heading-id="training-docs"
      spacing="lg"
    >
      <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <TrainingPanel
          title="Правовые акты"
          icon="i-lucide-file-text"
        >
          <ul class="flex flex-col gap-3">
            <li class="flex flex-col gap-1 rounded-lg bg-default p-4">
              <span class="text-base font-semibold text-text-primary">{{ federalLaw.title }}</span>
              <span class="flex flex-wrap gap-x-3 text-caption text-text-muted">
                <template v-if="!kiosk">
                  <ULink
                    v-for="item in norms"
                    :key="item.id"
                    :href="item.url"
                    target="_blank"
                    rel="noopener"
                    class="text-primary underline"
                  >
                    {{ item.ref }}
                  </ULink>
                  <ULink
                    :href="federalLaw.url"
                    target="_blank"
                    rel="noopener"
                    class="text-primary underline"
                  >
                    полный текст
                  </ULink>
                </template>
                <template v-else>
                  {{ norms.map(item => item.ref).join(' · ') }}
                </template>
              </span>
            </li>
            <li
              v-for="act in legalActs"
              :key="act.id"
              class="flex flex-col gap-1 rounded-lg bg-default p-4"
            >
              <span class="text-base font-semibold text-text-primary">{{ act.title }}</span>
              <span class="text-caption text-text-muted">{{ act.kind }}</span>
              <span class="flex flex-wrap gap-x-3 text-caption text-text-muted">
                <span class="text-text-primary">№ {{ act.number }} от {{ act.date }}</span>
                <span v-if="act.edition">{{ act.edition }}</span>
                <ULink
                  v-if="act.url && !kiosk"
                  :href="act.url"
                  target="_blank"
                  rel="noopener"
                  class="text-primary underline"
                >
                  текст акта
                </ULink>
                <span v-else-if="!act.url">текст — в {{ contacts.department_short }}</span>
              </span>
            </li>
          </ul>
        </TrainingPanel>

        <div class="flex flex-col gap-4">
          <TrainingPanel
            title="Куда обращаться"
            icon="i-lucide-phone"
          >
            <ul class="flex flex-col gap-4">
              <li class="flex items-start gap-3">
                <UIcon
                  name="i-lucide-building"
                  class="mt-0.5 size-5 shrink-0 text-text-muted"
                  aria-hidden="true"
                />
                <div class="flex flex-col gap-0.5">
                  <span class="text-overline text-text-muted">Ответственное подразделение</span>
                  <span class="text-body text-text-primary">{{ contacts.department }}, {{ contacts.unit }}</span>
                </div>
              </li>
              <li class="flex items-start gap-3">
                <UIcon
                  name="i-lucide-map-pin"
                  class="mt-0.5 size-5 shrink-0 text-text-muted"
                  aria-hidden="true"
                />
                <div class="flex flex-col gap-0.5">
                  <span class="text-overline text-text-muted">Адрес</span>
                  <span class="text-body text-text-primary">{{ contacts.address }}</span>
                </div>
              </li>
              <li class="flex items-start gap-3">
                <UIcon
                  name="i-lucide-phone"
                  class="mt-0.5 size-5 shrink-0 text-text-muted"
                  aria-hidden="true"
                />
                <div class="flex flex-col gap-0.5">
                  <span class="text-overline text-text-muted">Телефоны и электронная почта</span>
                  <NuxtLink
                    :to="contacts.portal_contacts_url"
                    class="text-body text-primary underline"
                  >
                    Контакты отдела на кадровом портале
                  </NuxtLink>
                </div>
              </li>
              <li
                v-if="!kiosk"
                class="flex items-start gap-3"
              >
                <UIcon
                  name="i-lucide-globe"
                  class="mt-0.5 size-5 shrink-0 text-text-muted"
                  aria-hidden="true"
                />
                <div class="flex flex-col gap-0.5">
                  <span class="text-overline text-text-muted">Официальный сайт</span>
                  <ULink
                    :href="contacts.site"
                    target="_blank"
                    rel="noopener"
                    class="text-body text-primary underline"
                  >
                    {{ contacts.site.replace(/^https?:\/\//, '') }}
                  </ULink>
                </div>
              </li>
            </ul>
          </TrainingPanel>

          <TrainingPanel
            title="Задать вопрос"
            icon="i-lucide-message-circle-question"
          >
            <p class="text-caption text-text-primary">
              С вопросами об обучении обращайтесь к сотрудникам отдела развития и мотивации персонала:
              <NuxtLink
                :to="contacts.portal_contacts_url"
                class="text-primary underline"
              >
                контакты на кадровом портале.
              </NuxtLink>
            </p>
          </TrainingPanel>
        </div>
      </div>
    </DsContentSection>
  </DsStandardPage>
</template>
