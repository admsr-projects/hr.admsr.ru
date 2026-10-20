import type { SubscribeVerification } from '~/utils/subscription-verification'

interface ApiErrorData {
  detail?: string
  reason?: string
  resend_after?: number
  email?: string[]
  error?: string
}

/** Статус и тело ответа API из ошибки $fetch */
export function apiError(error: unknown): { status: number, data: ApiErrorData } {
  const { status, statusCode, data } = (error ?? {}) as { status?: number, statusCode?: number, data?: ApiErrorData }
  return { status: status ?? statusCode ?? 0, data: data ?? {} }
}

/**
 * Шаг «введите код из письма» после отправки формы: заявка уже сохранена на сервере,
 * а действие (подписка, сообщение) выполнится после подтверждения email.
 *
 * `endpoint` — адрес без завершающего слэша, например `${apiBaseUrl}/api/submit-feedback`:
 * код проверяется на `${endpoint}/confirm/`, повторно отправляется через `${endpoint}/resend/`.
 */
export function useEmailCodeStep(endpoint: string) {
  const toast = useToast()
  const pendingId = ref<number | null>(null)
  const verification = reactive<SubscribeVerification>({
    active: false,
    email: '',
    loading: false,
    resending: false,
    error: '',
    resendIn: 0
  })

  let timer: ReturnType<typeof setInterval> | undefined

  function startCountdown(seconds: number) {
    verification.resendIn = Math.max(0, Math.ceil(seconds))
    clearInterval(timer)
    if (!verification.resendIn) return
    timer = setInterval(() => {
      verification.resendIn -= 1
      if (verification.resendIn <= 0) clearInterval(timer)
    }, 1000)
  }

  onBeforeUnmount(() => clearInterval(timer))

  /** Письмо с кодом отправлено — показать шаг ввода кода */
  function begin(response: { id: number, email: string, resend_after: number }) {
    pendingId.value = response.id
    verification.email = response.email
    verification.error = ''
    verification.active = true
    startCountdown(response.resend_after)
    toast.add({
      title: 'Код отправлен',
      description: `Проверьте почту ${response.email} и введите код из письма.`,
      color: 'success'
    })
  }

  /** Закрыть шаг кода (форма остаётся заполненной) */
  function close() {
    clearInterval(timer)
    verification.active = false
    verification.error = ''
    verification.resendIn = 0
    pendingId.value = null
  }

  /** Проверить код. true — email подтверждён, заявка принята сервером */
  async function confirm(code: string): Promise<{ ok: boolean, message?: string }> {
    if (!pendingId.value || verification.loading) return { ok: false }
    verification.loading = true
    verification.error = ''
    try {
      const data = await $fetch<{ message?: string }>(`${endpoint}/confirm/`, {
        method: 'POST',
        body: { id: pendingId.value, code }
      })
      close()
      return { ok: true, message: data.message }
    } catch (error) {
      const { status, data } = apiError(error)
      if (status === 404) {
        // Заявка удалена (например, устарела) — отправить форму заново
        close()
        toast.add({ title: 'Заявка устарела', description: data.detail ?? 'Отправьте форму заново.', color: 'error' })
      } else {
        verification.error = data.detail ?? 'Не удалось проверить код. Попробуйте ещё раз.'
      }
      return { ok: false }
    } finally {
      verification.loading = false
    }
  }

  async function resend() {
    if (!pendingId.value || verification.resending || verification.resendIn > 0) return
    verification.resending = true
    verification.error = ''
    try {
      const response = await $fetch<{ email: string, resend_after: number }>(`${endpoint}/resend/`, {
        method: 'POST',
        body: { id: pendingId.value }
      })
      startCountdown(response.resend_after)
      toast.add({ title: 'Новый код отправлен', description: `Проверьте почту ${response.email}.`, color: 'success' })
    } catch (error) {
      const { status, data } = apiError(error)
      if (status === 429 && data.resend_after) startCountdown(data.resend_after)
      else if (status === 404) close()
      verification.error = data.detail ?? 'Не удалось отправить код. Попробуйте позже.'
    } finally {
      verification.resending = false
    }
  }

  return { verification, begin, close, confirm, resend }
}
