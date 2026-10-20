<template>
  <div class="flex min-w-0 w-full max-w-full flex-col gap-6">
    <div class="flex flex-col items-center gap-4 text-center">
      <span class="inline-flex size-14 items-center justify-center rounded-full bg-primary/10 text-primary">
        <UIcon
          name="i-lucide-mail-check"
          class="size-7"
          aria-hidden="true"
        />
      </span>
      <div class="flex flex-col gap-2">
        <h3 class="text-h3 text-text-primary">
          Подтвердите email
        </h3>
        <p class="text-pretty text-caption text-text-muted">
          Мы отправили 6-значный код на
          <span class="font-semibold text-text-primary break-all">{{ verification.email }}</span>.
          Введите его, чтобы {{ purpose }}. Если письма нет, проверьте папку «Спам».
        </p>
      </div>
    </div>

    <form
      class="flex flex-col items-center gap-4"
      @submit.prevent="submit"
    >
      <UPinInput
        v-model="digits"
        :length="6"
        type="number"
        otp
        autofocus
        :disabled="verification.loading"
        :color="verification.error ? 'error' : 'primary'"
        aria-label="Код подтверждения из письма"
        @update:model-value="onInput"
        @complete="submit"
      />

      <p
        v-if="verification.error"
        class="text-pretty text-center text-caption text-error"
        role="alert"
      >
        {{ verification.error }}
      </p>

      <UButton
        type="submit"
        label="Подтвердить"
        color="primary"
        :loading="verification.loading"
        :disabled="digits.length < 6"
        class="w-full justify-center"
      />
    </form>

    <div class="flex flex-col items-center gap-1">
      <UButton
        :label="verification.resendIn > 0 ? `Отправить код ещё раз через ${verification.resendIn} с` : 'Отправить код ещё раз'"
        color="neutral"
        variant="link"
        :disabled="verification.resendIn > 0"
        :loading="verification.resending"
        @click="$emit('resend')"
      />
      <UButton
        label="Изменить email"
        color="neutral"
        variant="link"
        @click="$emit('back')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { SubscribeVerification } from '~/utils/subscription-verification'

const props = withDefaults(defineProps<{
  verification: SubscribeVerification
  /** Что произойдёт после подтверждения: «включить подписку», «отправить сообщение» */
  purpose?: string
}>(), {
  purpose: 'включить подписку'
})

const emit = defineEmits<{
  confirm: [code: string]
  resend: []
  back: []
  edit: []
}>()

const digits = ref<number[]>([])

// После неверного кода и после нового письма поле очищается, чтобы вводить заново
watch(() => props.verification.error, (value) => {
  if (value) digits.value = []
})
watch(() => props.verification.resendIn, (value, previous) => {
  if (value > previous) digits.value = []
})

// Ошибка относится к прошлому вводу — как только человек правит код, убираем её
function onInput() {
  if (props.verification.error) emit('edit')
}

function submit() {
  if (digits.value.length < 6 || props.verification.loading) return
  emit('confirm', digits.value.join(''))
}
</script>
