<template>
  <div
    :class="panelClass"
    aria-live="polite"
  >
    <div
      v-if="submitted"
      class="flex flex-col items-center gap-4 py-4 text-center"
    >
      <span class="inline-flex size-14 items-center justify-center rounded-full bg-primary/10 text-primary">
        <UIcon
          name="i-lucide-check"
          class="size-7"
          aria-hidden="true"
        />
      </span>
      <div class="flex flex-col gap-2">
        <h3 class="text-xl font-semibold text-highlighted">
          Подписка оформлена
        </h3>
        <p class="text-pretty text-sm leading-6 text-muted">
          Уведомления{{ submittedOfoHint }} будут приходить на {{ submittedEmail }}
        </p>
      </div>
      <UButton
        label="Подписать другой email"
        color="neutral"
        variant="link"
        
        @click="$emit('reset')"
      />
    </div>

    <UForm
      v-else
      :state="form"
      :validate="validate"
      class="flex min-w-0 w-full max-w-full flex-col gap-4"
      @submit="$emit('submit')"
    >
      <UFormField name="name">
        <template #label>
          <DsRequiredLabel label="Имя" />
        </template>
        <UInput
          v-model="form.name"
          type="text"
          placeholder="Иван Иванов"
          autocomplete="name"
          class="w-full min-w-0"
        />
      </UFormField>

      <UFormField name="email">
        <template #label>
          <DsRequiredLabel label="Email" />
        </template>
        <UInput
          v-model="form.email"
          type="email"
          placeholder="name@example.com"
          autocomplete="email"
          class="w-full min-w-0"
        />
      </UFormField>

      <UFormField
        label="Отраслевой функциональный орган"
        name="branch"
        class="min-w-0 w-full"
      >
        <USelectMenu
          v-model="form.branch"
          :items="ofoOptions"
          aria-label="Отраслевой функциональный орган"
          value-key="value"
          :search-input="{
            placeholder: 'Поиск ОФО…',
            icon: 'i-lucide-search',
          }"
          class="w-full min-w-0 max-w-full"
          :ui="{
            base: 'w-full min-w-0 max-w-full',
            value: 'truncate',
            trailing: 'shrink-0',
            trailingIcon: 'shrink-0',
          }"
        />
      </UFormField>

      <fieldset class="flex min-w-0 flex-col gap-3 rounded-lg bg-default p-4">
        <legend class="px-1 text-sm font-medium text-highlighted">
          Резюме (необязательно)
        </legend>

        <URadioGroup
          v-model="form.resumeMode"
          :items="resumeModeItems"
          orientation="horizontal"
          variant="list"
          legend="Способ передачи резюме"
          :ui="{ fieldset: 'flex flex-wrap gap-x-6 gap-y-2', legend: 'sr-only' }"
        />

        <UFormField
          v-if="form.resumeMode === 'file'"
          name="resumeFile"
        >
          <UFileUpload
            v-model="form.resumeFile"
            variant="area"
            accept=".pdf,.doc,.docx,.rtf,.odt,.txt"
            label="Прикрепить резюме"
            description="PDF, DOC, DOCX, RTF, ODT или TXT (макс. 10 МБ)"
            class="w-full min-w-0"
          />
        </UFormField>

        <div
          v-else-if="form.resumeMode === 'form'"
          class="flex flex-col gap-4"
        >
          <UFormField name="desiredPosition">
            <template #label>
              <DsRequiredLabel label="Желаемая должность" />
            </template>
            <UInput
              v-model="form.desiredPosition"
              placeholder="Например, специалист по кадрам"
              class="w-full min-w-0"
            />
          </UFormField>

          <UFormField name="phone">
            <template #label>
              <DsRequiredLabel label="Телефон" />
            </template>
            <UInput
              v-model="form.phone"
              type="tel"
              placeholder="+7 (900) 000-00-00"
              autocomplete="tel"
              class="w-full min-w-0"
            />
          </UFormField>

          <UFormField
            label="Образование"
            name="education"
          >
            <UInput
              v-model="form.education"
              placeholder="Учебное заведение, специальность, год окончания"
              class="w-full min-w-0"
            />
          </UFormField>

          <UFormField
            label="Опыт работы"
            name="workExperience"
          >
            <UTextarea
              v-model="form.workExperience"
              :rows="4"
              placeholder="Места работы, должности, периоды"
              class="w-full min-w-0"
            />
          </UFormField>

          <UFormField
            label="О себе, навыки"
            name="about"
          >
            <UTextarea
              v-model="form.about"
              :rows="3"
              placeholder="Ключевые навыки и достижения"
              class="w-full min-w-0"
            />
          </UFormField>
        </div>
      </fieldset>

      <UFormField
        name="consentPersonalData"
        class="min-w-0 w-full"
      >
        <UCheckbox
          v-model="form.consentPersonalData"
          :ui="{
            root: 'relative flex items-start gap-1',
            wrapper: 'min-w-0 flex-1',
            label: 'min-w-0 text-pretty',
          }"
        >
          <template #label>
            <span class="block min-w-0 text-pretty text-sm leading-6 text-muted">
              Согласен на
              <NuxtLink
                to="/privacy"
                class="text-primary underline underline-offset-2 hover:no-underline"
              >
                обработку персональных данных
              </NuxtLink>
              (152-ФЗ)
              <span
                class="text-error"
                aria-hidden="true"
              > *</span>
              <span class="text-xs text-muted"> обязательно</span>
            </span>
          </template>
        </UCheckbox>
      </UFormField>

      <UButton
        type="submit"
        label="Подписаться"
        trailing-icon="i-lucide-arrow-right"
        color="primary"
        :loading="loading"
        class="w-full justify-center"
      />
    </UForm>
  </div>
</template>

<script setup lang="ts">
import { ofoAnyLabel, ofoOptions } from '~/data/ofo-list'

interface SubscribeForm {
  name: string
  email: string
  branch: string
  consentPersonalData: boolean
  resumeMode: 'none' | 'file' | 'form'
  resumeFile: File | null
  phone: string
  desiredPosition: string
  education: string
  workExperience: string
  about: string
}

const resumeModeItems = [
  { value: 'none', label: 'Без резюме' },
  { value: 'file', label: 'Прикрепить файл' },
  { value: 'form', label: 'Заполнить в форме' },
]

const props = withDefaults(defineProps<{
  form: SubscribeForm
  loading: boolean
  submitted: boolean
  submittedEmail: string
  submittedOfo: string
  validate: (state: SubscribeForm) => { name: string, message: string }[]
  plain?: boolean
  accent?: boolean
}>(), {
  plain: false,
  accent: false,
})

defineEmits<{
  submit: []
  reset: []
}>()

const submittedOfoHint = computed(() =>
  props.submittedOfo === ofoAnyLabel
    ? ' о новых вакансиях'
    : ` о вакансиях в «${props.submittedOfo}»`,
)

const panelClass = computed(() => {
  const base = 'min-w-0 w-full max-w-full rounded-xl bg-elevated'
  if (props.accent || props.plain) {
    return `${base} p-4 sm:p-6 lg:p-8`
  }
  return `${base} p-4 sm:p-5 lg:p-6`
})
</script>
