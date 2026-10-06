<template>
  <div class="grid w-full min-w-0 grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] lg:items-start lg:gap-8">
    <div
      class="min-w-0"
      :class="compact ? 'flex flex-col gap-4' : 'flex flex-col gap-6 sm:gap-8'"
    >
      <div class="flex min-w-0 flex-col gap-3 sm:gap-4">
        <UBadge
          label="Уведомления о вакансиях"
          color="primary"
          variant="soft"
          class="w-fit max-w-full"
        />
        <h2
          :id="headingId"
          class="text-h2 text-text-primary text-balance"
        >
          Не пропустите подходящую должность
        </h2>
        <p class="max-w-lg text-pretty text-base text-text-muted">
          Укажите имя и email — сообщим, когда в выбранном ОФО появится новая вакансия в администрации района.
        </p>
      </div>

      <ul
        v-if="!compact && highlights.length"
        class="flex min-w-0 flex-col gap-4 sm:gap-5"
      >
        <li
          v-for="item in highlights"
          :key="item.title"
          class="flex min-w-0 items-start gap-3 sm:gap-4"
        >
          <span class="inline-flex size-10 shrink-0 items-center justify-center rounded-full bg-default text-primary">
            <UIcon
              :name="item.icon"
              class="size-5"
              aria-hidden="true"
            />
          </span>
          <div class="min-w-0 flex flex-col gap-0.5 pt-0.5">
            <span class="text-base font-semibold text-text-primary text-balance">
              {{ item.title }}
            </span>
            <NuxtLink
              v-if="item.to"
              :to="item.to"
              class="text-caption text-text-muted text-pretty transition-colors duration-200 hover:text-primary"
            >
              {{ item.text }}
            </NuxtLink>
            <p
              v-else
              class="text-caption text-text-muted text-pretty"
            >
              {{ item.text }}
            </p>
          </div>
        </li>
      </ul>
    </div>

    <SubscribeFormPanel
      class="min-w-0 w-full max-w-full"
      :form="form"
      :loading="loading"
      :submitted="submitted"
      :submitted-email="submittedEmail"
      :submitted-ofo="submittedOfo"
      :validate="validate"
      accent
      plain
      @submit="$emit('submit')"
      @reset="$emit('reset')"
    />
  </div>
</template>

<script setup lang="ts">
import SubscribeFormPanel from './VacancySubscribeFormPanel.vue'

defineProps<{
  headingId: string
  compact?: boolean
  highlights: Array<{
    icon: string
    title: string
    text: string
    to?: string
  }>
  form: {
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
  loading: boolean
  submitted: boolean
  submittedEmail: string
  submittedOfo: string
  validate: (state: {
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
  }) => { name: string, message: string }[]
}>()

defineEmits<{
  submit: []
  reset: []
}>()
</script>
