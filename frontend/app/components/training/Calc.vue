<template>
  <div class="grid grid-cols-1 gap-4 xl:grid-cols-2">
    <form
      class="flex flex-col gap-6 rounded-xl bg-elevated p-6"
      novalidate
      aria-describedby="training-calc-note"
      @submit.prevent
    >
      <UBadge
        label="Пример расчёта — подставьте свои значения"
        color="neutral"
        variant="soft"
        class="self-start"
      />

      <UFormField label="Вид программы">
        <URadioGroup
          v-model="programId"
          :items="programItems"
          orientation="vertical"
        />
      </UFormField>

      <UFormField
        label="Стоимость программы"
        hint="Сумма из муниципального контракта или ученического договора"
      >
        <UInput
          v-model="costText"
          inputmode="numeric"
          autocomplete="off"
          class="w-full"
          @blur="formatCost"
        >
          <template #trailing>
            <span class="text-caption text-text-muted">₽</span>
          </template>
        </UInput>
      </UFormField>

      <UFormField
        v-if="matches.length"
        :label="`Проработано после окончания обучения: ${monthsText(workedShown)}`"
        hint="Периоды из п. 5.4 договора (больничный, отпуск по уходу за ребёнком и др.) в этот срок не включаются"
      >
        <USlider
          v-model="worked"
          :min="0"
          :max="maxWorked"
          :step="1"
          aria-label="Проработано месяцев после обучения"
        />
      </UFormField>

      <p
        id="training-calc-note"
        class="text-overline text-text-muted"
      >
        Расчёт выполняется в браузере. Введённые значения никуда не передаются и не сохраняются.
      </p>
    </form>

    <div
      class="flex flex-col gap-4 rounded-xl bg-elevated p-6"
      aria-live="polite"
    >
      <template v-if="verdict.kind === 'result'">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div class="flex flex-col gap-1 rounded-lg bg-default p-4">
            <span class="text-caption text-text-muted">Срок обязательной работы</span>
            <span class="text-h2 text-text-primary">{{ monthsText(verdict.months) }}</span>
            <span class="text-overline text-text-muted">{{ bandLabel(verdict.band) }}</span>
          </div>
          <div class="flex flex-col gap-1 rounded-lg bg-default p-4">
            <span class="text-caption text-text-muted">Возмещение при увольнении через {{ monthsText(verdict.worked) }}</span>
            <span class="text-h2 text-text-primary">{{ rub2(verdict.refund) }}</span>
            <span class="text-overline text-text-muted">
              {{ verdict.left ? `${nf.format(cost)} × ${verdict.left}/${verdict.months}` : 'срок отработан полностью' }}
            </span>
          </div>
        </div>

        <div class="flex flex-col gap-2">
          <div
            class="flex h-3 w-full gap-0.5 overflow-hidden rounded-full bg-accented"
            role="img"
            :aria-label="`Отработано ${verdict.worked} из ${verdict.months} месяцев`"
          >
            <span
              v-if="verdict.worked"
              class="bg-(--training-good)"
              :style="{ flex: verdict.worked }"
            />
            <span
              v-if="verdict.left"
              class="bg-(--training-bad)"
              :style="{ flex: verdict.left }"
            />
          </div>
          <p class="flex flex-wrap justify-between gap-x-4 text-overline font-medium text-text-muted">
            <span><i class="mr-1.5 inline-block size-2 rounded-full bg-(--training-good)" />отработано: {{ monthsText(verdict.worked) }}</span>
            <span><i class="mr-1.5 inline-block size-2 rounded-full bg-(--training-bad)" />не отработано: {{ monthsText(verdict.left) }}</span>
          </p>
        </div>

        <UAlert
          v-if="matches.length > 1"
          color="warning"
          variant="soft"
          icon="i-lucide-triangle-alert"
          :description="`Сумма ${rub(cost)} попадает на границу двух диапазонов приложения 2 (${matches.map(band => monthsText(band.months)).join(' или ')}). Срок определяется ученическим договором — уточните в ${dept}.`"
        />

        <p class="text-caption text-text-muted">
          Возмещение применяется при увольнении по основаниям п. 3.3 договора — например, по собственному желанию без уважительной причины.
          При уважительной причине, подтверждённой документально, затраты не возмещаются.
        </p>
      </template>

      <UAlert
        v-else
        :color="verdict.kind === 'warning' ? 'warning' : verdict.kind === 'free' ? 'success' : 'info'"
        variant="soft"
        :icon="verdict.kind === 'warning' ? 'i-lucide-triangle-alert' : 'i-lucide-info'"
        :description="verdict.text"
      />

      <div class="flex flex-col gap-2">
        <p class="text-caption font-medium text-text-primary">
          Шкала сроков отработки
          <span class="font-normal text-text-muted">· {{ rules.retention_basis }}</span>
        </p>
        <ul
          class="flex flex-col gap-2"
          aria-label="Срок отработки в месяцах по диапазонам стоимости переподготовки"
        >
          <li
            v-for="band in rules.retention_scale"
            :key="band.months"
            class="grid grid-cols-[7.5rem_minmax(0,1fr)_4.5rem] items-center gap-3 text-caption"
          >
            <span class="text-text-muted">{{ bandShort(band) }}</span>
            <span class="h-3 rounded-full bg-accented">
              <span
                class="block h-3 rounded-full"
                :class="active.includes(band) ? 'bg-(--training-bar-on)' : 'bg-(--training-bar)'"
                :style="{ width: `${band.months / scaleTop * 100}%` }"
              />
            </span>
            <span class="text-right font-medium text-text-primary">{{ band.months }} мес.</span>
          </li>
        </ul>
      </div>

      <p class="text-overline text-text-muted">
        Расчёт носит справочный характер; окончательные условия — в ученическом договоре.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TrainingRetentionBand } from '~/data/training-info'
import { trainingInfo } from '~/data/training-info'

const rules = trainingInfo.training_rules
const dept = trainingInfo.contacts.department_short

const nf = new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 })
const nf2 = new Intl.NumberFormat('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
const rub = (value: number) => `${nf.format(value)} ₽`
const rub2 = (value: number) => `${nf2.format(value)} ₽`

function monthsText(count: number) {
  const mod10 = count % 10
  const mod100 = count % 100
  const word = mod10 === 1 && mod100 !== 11
    ? 'месяц'
    : mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14) ? 'месяца' : 'месяцев'
  return `${count} ${word}`
}

function bandLabel(band: TrainingRetentionBand) {
  return band.max === null
    ? `свыше ${nf.format(band.min)} ₽`
    : `${nf.format(band.min)}–${nf.format(band.max)} ₽`
}

function bandShort(band: TrainingRetentionBand) {
  const thousands = (value: number) => nf.format(value / 1000)
  return band.max === null
    ? `свыше ${thousands(band.min)} тыс. ₽`
    : `${thousands(band.min)}–${thousands(band.max)} тыс. ₽`
}

const programItems = rules.programs.map(program => ({ label: program.name, value: program.id }))
const programId = ref(rules.contract_applies_to)
const cost = ref(85000)
const costText = ref(nf.format(cost.value))
const worked = ref(6)

watch(costText, (value) => {
  const digits = value.replace(/\D/g, '')
  cost.value = digits ? Math.min(Number.parseInt(digits, 10), 99999999) : 0
})

function formatCost() {
  costText.value = cost.value ? nf.format(cost.value) : ''
}

const scaleTop = Math.ceil(Math.max(...rules.retention_scale.map(band => band.months)) / 12) * 12

// Суммы на стыке диапазонов (70 000, 120 000, 200 000) в акте входят в два диапазона сразу
const matches = computed(() => {
  if (cost.value <= rules.contract_threshold_rub) return []
  return rules.retention_scale.filter((band) => {
    const aboveMin = band.min_exclusive ? cost.value > band.min : cost.value >= band.min
    return aboveMin && (band.max === null || cost.value <= band.max)
  })
})

const applies = computed(() => programId.value === rules.contract_applies_to)
const active = computed(() => applies.value ? matches.value : [])

const maxWorked = computed(() => matches.value[0]?.months ?? 60)
const workedShown = computed(() => Math.min(worked.value, maxWorked.value))

type Verdict
  = | { kind: 'result', band: TrainingRetentionBand, months: number, worked: number, left: number, refund: number }
    | { kind: 'info' | 'free' | 'warning', text: string }

const verdict = computed<Verdict>(() => {
  const programName = rules.programs.find(program => program.id === programId.value)?.name ?? ''
  if (!cost.value) return { kind: 'info', text: 'Введите стоимость программы.' }
  if (!applies.value) {
    return {
      kind: 'free',
      text: `Для программы «${programName}» Положение не устанавливает обязательный ученический договор и срок отработки (${rules.contract_basis}). Если договор с вами всё же заключается, условия определяет он.`
    }
  }
  if (cost.value <= rules.contract_threshold_rub) {
    return {
      kind: 'free',
      text: `Стоимость не превышает ${rub(rules.contract_threshold_rub)}: ученический договор по п. 10 Положения не обязателен, срок отработки шкалой не устанавливается.`
    }
  }
  const band = matches.value[0]
  if (!band) return { kind: 'warning', text: `Сумма не попадает в шкалу. Уточните в ${dept}.` }
  const done = workedShown.value
  const left = band.months - done
  return { kind: 'result', band, months: band.months, worked: done, left, refund: cost.value * left / band.months }
})
</script>
