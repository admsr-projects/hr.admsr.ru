/** Выбор посетителя по необязательным cookie. Необходимые cookie работают всегда и в выбор не входят. */
export interface CookieConsentChoice {
  /** Яндекс.Метрика: статистика посещений */
  analytics: boolean
  /** Вебвизор и карта кликов; без аналитики не работает */
  webvisor: boolean
}

interface StoredConsent extends CookieConsentChoice {
  v: number
}

const COOKIE_NAME = 'cookieConsent'
// Версия меняется, когда меняется состав категорий — тогда согласие спрашиваем заново.
// Старое значение «true» (кнопка «Понятно» без выбора) тоже считается отсутствием решения.
const CONSENT_VERSION = 1

function parseConsent(value: unknown): CookieConsentChoice | null {
  if (!value || typeof value !== 'object') return null
  const stored = value as Partial<StoredConsent>
  if (stored.v !== CONSENT_VERSION) return null
  const analytics = stored.analytics === true
  return { analytics, webvisor: analytics && stored.webvisor === true }
}

export function useCookieConsent() {
  const cookie = useCookie<StoredConsent | null>(COOKIE_NAME, {
    maxAge: 60 * 60 * 24 * 365,
    sameSite: 'lax',
    path: '/',
    default: () => null
  })
  // null — посетитель ещё не решил. Значение читается из cookie в плагине cookie-consent.client.ts:
  // страницы собираются заранее, и на сервере выбора посетителя не видно
  const consent = useState<CookieConsentChoice | null>('cookie-consent', () => null)
  const settingsOpen = useState('cookie-settings-open', () => false)

  function syncFromCookie() {
    consent.value = parseConsent(cookie.value)
  }

  function save(choice: CookieConsentChoice) {
    const normalized = { analytics: choice.analytics, webvisor: choice.analytics && choice.webvisor }
    cookie.value = { v: CONSENT_VERSION, ...normalized }
    consent.value = normalized
    settingsOpen.value = false
  }

  return {
    consent,
    settingsOpen,
    syncFromCookie,
    save,
    acceptAll: () => save({ analytics: true, webvisor: true }),
    rejectAll: () => save({ analytics: false, webvisor: false }),
    openSettings: () => {
      settingsOpen.value = true
    }
  }
}
