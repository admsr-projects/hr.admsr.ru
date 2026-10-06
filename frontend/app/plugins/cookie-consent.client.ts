/** Читает сохранённый выбор по cookie до того, как его используют баннер и Яндекс.Метрика */
export default defineNuxtPlugin({
  name: 'cookie-consent',
  setup() {
    useCookieConsent().syncFromCookie()
  }
})
