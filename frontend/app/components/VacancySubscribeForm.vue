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
          :verification="verification"
          @submit="onSubmit"
          @reset="resetForm"
          @confirm="onConfirm"
          @resend="onResend"
          @back="backToForm"
          @edit="verification.error = ''"
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
        :verification="verification"
        @submit="onSubmit"
        @reset="resetForm"
        @confirm="onConfirm"
        @resend="onResend"
        @back="backToForm"
        @edit="verification.error = ''"
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
          :verification="verification"
          @submit="onSubmit"
          @reset="resetForm"
          @confirm="onConfirm"
          @resend="onResend"
          @back="backToForm"
          @edit="verification.error = ''"
        />
      </div>
    </div>
  </component>
</template>

<script setup lang="ts">
import PromoCardContent from './VacancySubscribePromoCard.vue'
import SubscribeFormPanel from './VacancySubscribeFormPanel.vue'
import { ofoAnyValue, ofoApiBranch, ofoLabel, ofoList } from '~/data/ofo-list'
import type { SubscribeVerification } from '~/utils/subscription-verification'

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

// Подписка включается после ввода кода из письма: шаг 1 — форма, шаг 2 — код
const pendingId = ref<number | null>(null)
const verification = reactive<SubscribeVerification>({
  active: false,
  email: '',
  loading: false,
  resending: false,
  error: '',
  resendIn: 0,
})

let resendTimer: ReturnType<typeof setInterval> | undefined

function startResendCountdown(seconds: number) {
  verification.resendIn = Math.max(0, Math.ceil(seconds))
  clearInterval(resendTimer)
  if (!verification.resendIn) return
  resendTimer = setInterval(() => {
    verification.resendIn -= 1
    if (verification.resendIn <= 0) clearInterval(resendTimer)
  }, 1000)
}

onBeforeUnmount(() => clearInterval(resendTimer))

interface ApiErrorData {
  detail?: string
  reason?: string
  resend_after?: number
  email?: string[]
}

function apiError(error: unknown): { status: number, data: ApiErrorData } {
  const { status, statusCode, data } = (error ?? {}) as { status?: number, statusCode?: number, data?: ApiErrorData }
  return { status: status ?? statusCode ?? 0, data: data ?? {} }
}

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
  verification.active = false
  pendingId.value = null
  clearFields()
}

// «Изменить email»: вернуться к форме, введённые данные сохраняются
function backToForm() {
  clearInterval(resendTimer)
  verification.active = false
  verification.error = ''
  verification.resendIn = 0
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

    const response = await $fetch<{ id: number, email: string, resend_after: number }>(
      `${config.public.apiBaseUrl}/api/vacancy-subscribe/`,
      { method: 'POST', body },
    )

    pendingId.value = response.id
    verification.email = response.email
    verification.error = ''
    verification.active = true
    startResendCountdown(response.resend_after)

    toast.add({
      title: 'Код отправлен',
      description: `Проверьте почту ${response.email} и введите код из письма.`,
      color: 'success',
    })
  } catch (error) {
    const { status, data } = apiError(error)
    toast.add({
      title: 'Не удалось оформить подписку',
      description: data.email?.[0] ?? data.detail
        ?? (status === 400 ? 'Проверьте данные и попробуйте снова' : 'Попробуйте ещё раз позже'),
      color: 'error',
    })
  } finally {
    loading.value = false
  }
}

async function onConfirm(code: string) {
  if (!pendingId.value || verification.loading) return
  verification.loading = true
  verification.error = ''
  try {
    await $fetch(`${config.public.apiBaseUrl}/api/vacancy-subscribe/confirm/`, {
      method: 'POST',
      body: { id: pendingId.value, code },
    })

    submittedEmail.value = verification.email
    submittedOfo.value = ofoLabel(form.branch)
    submitted.value = true
    verification.active = false
    pendingId.value = null
    clearInterval(resendTimer)

    toast.add({
      title: 'Подписка оформлена',
      description: 'Уведомления о новых вакансиях будут приходить на указанный email.',
      color: 'success',
    })

    clearFields()
  } catch (error) {
    const { status, data } = apiError(error)
    if (status === 404) {
      // Заявка удалена (например, устарела) — оформить заново
      verification.active = false
      pendingId.value = null
      toast.add({ title: 'Заявка устарела', description: data.detail ?? 'Оформите подписку заново.', color: 'error' })
    }
    else {
      verification.error = data.detail ?? 'Не удалось проверить код. Попробуйте ещё раз.'
    }
  } finally {
    verification.loading = false
  }
}

async function onResend() {
  if (!pendingId.value || verification.resending || verification.resendIn > 0) return
  verification.resending = true
  verification.error = ''
  try {
    const response = await $fetch<{ email: string, resend_after: number }>(
      `${config.public.apiBaseUrl}/api/vacancy-subscribe/resend/`,
      { method: 'POST', body: { id: pendingId.value } },
    )
    startResendCountdown(response.resend_after)
    toast.add({ title: 'Новый код отправлен', description: `Проверьте почту ${response.email}.`, color: 'success' })
  } catch (error) {
    const { status, data } = apiError(error)
    if (status === 429 && data.resend_after) startResendCountdown(data.resend_after)
    else if (status === 404) {
      verification.active = false
      pendingId.value = null
    }
    verification.error = data.detail ?? 'Не удалось отправить код. Попробуйте позже.'
  } finally {
    verification.resending = false
  }
}
</script>
