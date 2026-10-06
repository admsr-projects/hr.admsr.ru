<template>
  <component
    :is="promo ? 'section' : 'div'"
    :class="promo ? 'bg-default overflow-x-clip' : embedded ? undefined : block ? undefined : 'ds-container py-8 lg:py-10'"
  >
    <UContainer
      v-if="promo"
      class="min-w-0 py-12 lg:py-16"
    >
      <article class="min-w-0 w-full overflow-hidden rounded-xl bg-elevated p-6 lg:p-8">
        <PromoCardContent
          :heading-id="headingId"
          :highlights="highlights"
          :form="form"
          :loading="loading"
          :submitted="submitted"
          :submitted-email="submittedEmail"
          :submitted-ofo="submittedOfo"
          :validate="validate"
          @submit="onSubmit"
          @reset="resetForm"
        />
      </article>
    </UContainer>

    <article
      v-else-if="block"
      class="min-w-0 w-full overflow-hidden rounded-xl bg-elevated p-6 lg:p-8"
    >
      <PromoCardContent
        :heading-id="headingId"
        :highlights="blockHighlights"
        :form="form"
        :loading="loading"
        :submitted="submitted"
        :submitted-email="submittedEmail"
        :submitted-ofo="submittedOfo"
        :validate="validate"
        @submit="onSubmit"
        @reset="resetForm"
      />
    </article>

    <div
      v-else
      :class="embedded && !bare ? 'ds-container py-8 lg:py-10' : undefined"
    >
      <div class="mx-auto flex max-w-2xl flex-col gap-4">
        <div class="flex flex-col gap-2">
          <h2 class="text-h2 text-highlighted text-balance">
            Подписка на новые вакансии
          </h2>
          <p class="text-pretty leading-7 text-muted">
            Укажите email и выберите отраслевой функциональный орган — мы сообщим о новых вакансиях.
          </p>
        </div>

        <SubscribeFormPanel
          :form="form"
          :loading="loading"
          :submitted="submitted"
          :submitted-email="submittedEmail"
          :submitted-ofo="submittedOfo"
          :validate="validate"
          @submit="onSubmit"
          @reset="resetForm"
        />
      </div>
    </div>
  </component>
</template>

<script setup lang="ts">
import PromoCardContent from './VacancySubscribePromoCard.vue'
import SubscribeFormPanel from './VacancySubscribeFormPanel.vue'
import { ofoAnyValue, ofoApiBranch, ofoLabel, ofoList } from '~/data/ofo-list'

const props = defineProps({
  initialBranch: {
    type: String,
    default: '',
  },
  embedded: {
    type: Boolean,
    default: false,
  },
  bare: {
    type: Boolean,
    default: false,
  },
  promo: {
    type: Boolean,
    default: false,
  },
  block: {
    type: Boolean,
    default: false,
  },
  headingId: {
    type: String,
    default: 'vacancy-subscribe',
  },
})

const config = useRuntimeConfig()
const toast = useToast()
const loading = ref(false)
const submitted = ref(false)
const submittedEmail = ref('')
const submittedOfo = ref('')

const highlights = [
  {
    icon: 'i-lucide-bell',
    title: 'По выбранному ОФО',
    text: 'Или сразу по всем вакансиям — пункт «Любой ОФО / не имеет значения»',
  },
  {
    icon: 'i-lucide-briefcase',
    title: 'Актуальные должности',
    text: 'Смотреть открытые вакансии на сайте',
    to: '/vacancies',
  },
]

// На странице вакансий вторая подсказка ведёт к списку вакансий на этой же странице
const blockHighlights = highlights.map(item => (item.to ? { ...item, to: '#vacancies-list' } : item))

const form = reactive({
  name: '',
  email: '',
  branch: resolveInitialBranch(props.initialBranch) || ofoAnyValue,
  consentPersonalData: false,
  // Резюме необязательно: можно приложить файл или заполнить поля прямо в форме
  resumeMode: 'none' as 'none' | 'file' | 'form',
  resumeFile: null as File | null,
  phone: '',
  desiredPosition: '',
  education: '',
  workExperience: '',
  about: '',
})

const RESUME_MAX_BYTES = 10 * 1024 * 1024
const RESUME_EXTENSIONS = ['.pdf', '.doc', '.docx', '.rtf', '.odt', '.txt']

watch(() => props.initialBranch, (value) => {
  if (value) form.branch = resolveInitialBranch(value)
})

function resolveInitialBranch(value: string): string {
  if (!value) return ofoAnyValue
  const match = ofoList.find(ofo => ofo === value || value.includes(ofo) || ofo.includes(value))
  return match ?? ofoAnyValue
}

function validate(state: typeof form) {
  const errors: { name: string, message: string }[] = []
  if (!state.name?.trim()) errors.push({ name: 'name', message: 'Укажите имя' })
  if (!state.email?.trim()) errors.push({ name: 'email', message: 'Укажите email' })
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(state.email.trim())) {
    errors.push({ name: 'email', message: 'Проверьте формат email' })
  }
  if (state.resumeMode === 'file') {
    const file = state.resumeFile
    if (!file) errors.push({ name: 'resumeFile', message: 'Прикрепите файл резюме' })
    else if (file.size > RESUME_MAX_BYTES) errors.push({ name: 'resumeFile', message: 'Размер файла не должен превышать 10 МБ' })
    else if (!RESUME_EXTENSIONS.some(ext => file.name.toLowerCase().endsWith(ext))) {
      errors.push({ name: 'resumeFile', message: 'Допустимые форматы: PDF, DOC, DOCX, RTF, ODT, TXT' })
    }
  }
  if (state.resumeMode === 'form') {
    if (!state.desiredPosition?.trim()) errors.push({ name: 'desiredPosition', message: 'Укажите желаемую должность' })
    if (!state.phone?.trim()) errors.push({ name: 'phone', message: 'Укажите телефон' })
  }
  if (!state.consentPersonalData) errors.push({ name: 'consentPersonalData', message: 'Необходимо согласие' })
  return errors
}

function clearFields() {
  form.name = ''
  form.email = ''
  form.branch = resolveInitialBranch(props.initialBranch)
  form.consentPersonalData = false
  form.resumeMode = 'none'
  form.resumeFile = null
  form.phone = ''
  form.desiredPosition = ''
  form.education = ''
  form.workExperience = ''
  form.about = ''
}

function resetForm() {
  submitted.value = false
  submittedEmail.value = ''
  submittedOfo.value = ''
  clearFields()
}

async function onSubmit() {
  loading.value = true
  try {
    const body = new FormData()
    body.append('name', form.name.trim())
    body.append('email', form.email.trim())
    body.append('branch', ofoApiBranch(form.branch))

    if (form.resumeMode === 'file' && form.resumeFile) {
      body.append('resume', form.resumeFile)
    }
    if (form.resumeMode === 'form') {
      body.append('phone', form.phone.trim())
      body.append('desired_position', form.desiredPosition.trim())
      body.append('education', form.education.trim())
      body.append('work_experience', form.workExperience.trim())
      body.append('about', form.about.trim())
    }

    await $fetch(`${config.public.apiBaseUrl}/api/vacancy-subscribe/`, {
      method: 'POST',
      body,
    })

    submittedEmail.value = form.email.trim()
    submittedOfo.value = ofoLabel(form.branch)
    submitted.value = true

    toast.add({
      title: 'Подписка оформлена',
      description: 'Уведомления о новых вакансиях будут приходить на указанный email.',
      color: 'success',
    })

    clearFields()
  } catch {
    toast.add({
      title: 'Не удалось оформить подписку',
      description: 'Проверьте данные и попробуйте снова',
      color: 'error',
    })
  } finally {
    loading.value = false
  }
}
</script>
