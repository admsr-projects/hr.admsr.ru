type Ym = ((id: number, method: string, ...args: unknown[]) => void) & { a?: unknown[], l?: number }
type MetrikaWindow = Window & { ym?: Ym } & Record<string, unknown>

/** Подключает счётчик так же, как стандартный код Яндекс.Метрики; init сразу учитывает текущую страницу */
function loadMetrika(counterId: number, webvisor: boolean) {
  const w = window as unknown as MetrikaWindow
  w.ym = w.ym || function () {
    // eslint-disable-next-line prefer-rest-params
    (w.ym!.a = w.ym!.a || []).push(arguments)
  }
  w.ym.l = Date.now()

  const script = document.createElement('script')
  script.async = true
  script.src = `https://mc.yandex.ru/metrika/tag.js?id=${counterId}`
  document.head.appendChild(script)

  w.ym(counterId, 'init', {
    ssr: true,
    webvisor,
    clickmap: webvisor,
    ecommerce: 'dataLayer',
    referrer: document.referrer,
    url: location.href,
    accurateTrackBounce: true,
    trackLinks: true
  })
}

/** Cookie Метрики на домене сайта: _ym_uid, _ym_d, _ym_isad и др., а также mdd (без префикса) */
function isMetrikaCookie(name: string) {
  return name.startsWith('_ym') || name === 'mdd'
}

/** Удаляет cookie и записи Метрики, оставшиеся от прошлых посещений */
function clearMetrikaStorage() {
  const hostParts = location.hostname.split('.')
  // Метрика ставит cookie на домен второго уровня, поэтому перебираем все родительские домены
  const domains = ['', ...hostParts.map((_, i) => `; domain=.${hostParts.slice(i).join('.')}`)]
  for (const entry of document.cookie.split(';')) {
    const name = entry.split('=')[0]!.trim()
    if (!isMetrikaCookie(name)) continue
    for (const domain of domains) {
      document.cookie = `${name}=; max-age=0; path=/${domain}`
    }
  }
  for (const key of Object.keys(localStorage)) {
    if (key.startsWith('_ym')) localStorage.removeItem(key)
  }
}

/**
 * Яндекс.Метрика запускается только после согласия посетителя на аналитические cookie.
 * Сайт — одностраничный, поэтому переходы между страницами после первого отправляем вручную.
 */
export default defineNuxtPlugin({
  name: 'yandex-metrika',
  dependsOn: ['cookie-consent'],
  setup(nuxtApp) {
    const counterId = useRuntimeConfig().public.yandexMetrikaId as number
    const { consent } = useCookieConsent()

    if (consent.value?.analytics === false) clearMetrikaStorage()
    if (!counterId) return

    // С какими настройками счётчик запущен на этой странице; null — не запускался
    let loadedWebvisor: boolean | null = null
    let disabled = false

    watch(consent, (choice) => {
      if (!choice) return
      if (loadedWebvisor === null) {
        if (choice.analytics) {
          loadMetrika(counterId, choice.webvisor)
          loadedWebvisor = choice.webvisor
        }
        return
      }
      if (!choice.analytics) {
        // Выгрузить запущенный счётчик нельзя — запрещаем ему отправку данных и убираем его cookie
        (window as unknown as MetrikaWindow)[`disableYaCounter${counterId}`] = true
        disabled = true
        clearMetrikaStorage()
        return
      }
      // Настройки счётчика задаются только при инициализации, поэтому новый выбор применяем перезагрузкой
      if (disabled || choice.webvisor !== loadedWebvisor) window.location.reload()
    }, { immediate: true })

    const router = useRouter()
    let lastPath: string | null = null
    let previousUrl = window.location.href

    // page:finish приходит после отрисовки страницы, поэтому заголовок уже новый
    nuxtApp.hook('page:finish', () => {
      const route = router.currentRoute.value

      // Первая страница уже посчитана при инициализации счётчика
      if (lastPath === null) {
        lastPath = route.path
        return
      }
      // Смена только якоря или параметров на той же странице — не новый просмотр
      if (route.path === lastPath) return
      lastPath = route.path

      const url = new URL(route.fullPath, window.location.origin).href
      if (consent.value?.analytics) {
        const ym = (window as unknown as MetrikaWindow).ym
        ym?.(counterId, 'hit', url, { title: document.title, referer: previousUrl })
      }
      previousUrl = url
    })
  }
})
