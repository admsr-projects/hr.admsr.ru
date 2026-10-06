type Ym = (id: number, method: string, ...args: unknown[]) => void

/**
 * Первый заход Яндекс.Метрика учитывает сама (init в head, см. nuxt.config.ts).
 * Сайт — одностраничный, поэтому остальные переходы между страницами отправляем вручную.
 */
export default defineNuxtPlugin((nuxtApp) => {
  const counterId = useRuntimeConfig().public.yandexMetrikaId as number
  if (!counterId) return

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
    const ym = (window as unknown as { ym?: Ym }).ym
    ym?.(counterId, 'hit', url, { title: document.title, referer: previousUrl })
    previousUrl = url
  })
})
