/** Через сколько секунд без касаний киоск возвращается на главную */
const IDLE_SECONDS = 120

/**
 * Поведение киоска: возврат на главную после бездействия, запрет контекстного меню
 * и переходов на внешние сайты (в киоске нет адресной строки, вернуться оттуда нельзя).
 */
export default defineNuxtPlugin(() => {
  if (!IS_KIOSK) return

  const apiBaseUrl = useRuntimeConfig().public.apiBaseUrl as string
  const allowedOrigins = new Set([window.location.origin])
  if (apiBaseUrl) allowedOrigins.add(new URL(apiBaseUrl, window.location.origin).origin)

  // Внешние сайты, почта и телефон на киоске не открываются
  document.addEventListener('click', (event) => {
    const link = (event.target as Element | null)?.closest?.('a[href]') as HTMLAnchorElement | null
    if (!link) return
    const url = new URL(link.href, window.location.href)
    if (!allowedOrigins.has(url.origin)) event.preventDefault()
  }, true)

  document.addEventListener('contextmenu', event => event.preventDefault())

  // Было ли взаимодействие после последнего сброса: без этого пустой киоск перезагружался бы каждые 2 минуты
  let touched = false
  let timer: ReturnType<typeof setTimeout> | undefined

  function reset() {
    touched = false
    // Полная перезагрузка: закрывает окна, чистит фильтры и подтягивает свежие вакансии и новости
    window.location.assign('/')
  }

  function arm() {
    touched = true
    clearTimeout(timer)
    timer = setTimeout(() => {
      if (touched) reset()
    }, IDLE_SECONDS * 1000)
  }

  for (const name of ['pointerdown', 'pointermove', 'keydown', 'wheel', 'scroll', 'touchstart']) {
    window.addEventListener(name, arm, { passive: true, capture: true })
  }
})
