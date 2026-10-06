/** Разделы, которые состоят из форм: на киоске их нет, ведём на ближайший полезный раздел */
const kioskRedirects: Record<string, string> = {
  '/feedback': '/contacts'
}

export default defineNuxtRouteMiddleware((to) => {
  if (!IS_KIOSK) return
  const target = kioskRedirects[to.path]
  if (target) return navigateTo(target, { replace: true })
})
