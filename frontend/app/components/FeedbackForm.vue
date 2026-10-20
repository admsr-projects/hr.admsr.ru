<template>
  <DsSurface
    elevation="none"
    padding="lg"
    class="w-full"
  >
    <VacancySubscribeCodeStep
      v-if="verification.active"
      :verification="verification"
      purpose="отправить сообщение"
      @confirm="onConfirm"
      @resend="resend"
      @back="close"
      @edit="verification.error = ''"
    />

    <UForm
      v-else
      :state="form"
      :validate="validate"
      class="flex flex-col gap-6"
      @submit="onSubmit"
    >
      <!-- Баннер: тон основного цвета, чтобы не сливаться с серой панелью вокруг -->
      <div
        class="flex items-start gap-3 rounded-xl bg-primary/10 px-4 py-4 sm:px-5"
        role="note"
      >
        <UIcon
          name="i-lucide-info"
          class="mt-0.5 size-6 shrink-0 text-primary"
          aria-hidden="true"
        />
        <div class="min-w-0 space-y-1">
          <p class="text-body font-semibold text-text-primary">
            Сообщение для команды портала
          </p>
          <p class="text-caption leading-relaxed text-pretty text-text-muted">
            Форма предназначена для вопросов, предложений и замечаний к работе кадрового портала. Для официальных обращений используйте вкладку «Госуслуги».
          </p>
        </div>
      </div>

      <UFormField name="message">
        <template #label>
          <DsRequiredLabel label="Сообщение" />
        </template>
        <UTextarea
          v-model="form.message"
          :rows="6"
          placeholder="Опишите вопрос, предложение или замечание"
          class="w-full"
        />
      </UFormField>

      <UFormField name="email">
        <template #label>
          <DsRequiredLabel label="Электронная почта" />
        </template>
        <UInput
          v-model="form.email"
          type="email"
          placeholder="name@example.com"
          autocomplete="email"
          class="w-full"
        />
      </UFormField>

      <UFormField
        label="Фото (необязательно)"
        name="photo"
        hint="JPG, PNG или GIF — для иллюстрации проблемы или предложения"
      >
        <UFileUpload
          v-model="form.photo"
          variant="area"
          accept="image/*"
          label="Прикрепить изображение"
          description="JPG, PNG или GIF"
          class="w-full"
        />
      </UFormField>

      <UButton
        type="submit"
        label="Получить код и отправить"
        color="primary"
        trailing-icon="i-lucide-arrow-right"
        :loading="loading"
        class="w-full justify-center sm:w-auto"
      />
    </UForm>
  </DsSurface>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()
const toast = useToast()
const loading = ref(false)

const form = reactive({
  message: '',
  email: '',
  photo: null as File | null
})

// Сообщение уходит команде портала после ввода кода из письма: шаг 1 — форма, шаг 2 — код
const { verification, begin, close, confirm, resend } = useEmailCodeStep(`${config.public.apiBaseUrl}/api/submit-feedback`)

function validate(state: typeof form) {
  const errors: { name: string, message: string }[] = []
  if (!state.message?.trim()) {
    errors.push({ name: 'message', message: 'Введите сообщение' })
  }
  if (!state.email?.trim()) {
    errors.push({ name: 'email', message: 'Укажите электронную почту' })
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(state.email.trim())) {
    errors.push({ name: 'email', message: 'Проверьте формат электронной почты' })
  }
  return errors
}

function resetForm() {
  form.message = ''
  form.email = ''
  form.photo = null
}

async function onSubmit() {
  loading.value = true

  try {
    const formData = new FormData()
    formData.append('message', form.message.trim())
    formData.append('email', form.email.trim())
    if (form.photo) {
      formData.append('photo', form.photo)
    }

    begin(await $fetch<{ id: number, email: string, resend_after: number }>(
      `${config.public.apiBaseUrl}/api/submit-feedback/`,
      { method: 'POST', body: formData }
    ))
  } catch (error: unknown) {
    const { data } = apiError(error)
    toast.add({
      title: 'Не удалось отправить',
      description: (data.email?.[0] ?? data.detail ?? data.error) || 'Произошла ошибка при отправке. Попробуйте позже.',
      color: 'error'
    })
  } finally {
    loading.value = false
  }
}

async function onConfirm(code: string) {
  const { ok, message } = await confirm(code)
  if (!ok) return

  toast.add({
    title: 'Сообщение отправлено',
    description: message || 'Мы рассмотрим ваше обращение в ближайшее время.',
    color: 'success'
  })
  resetForm()
}
</script>
