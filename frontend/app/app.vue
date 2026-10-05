<template>
  <UApp
    :locale="ru"
    :toaster="{ position: 'bottom-right' }"
  >
    <LoadingOverlay />
    <div class="min-h-screen">
      <a
        href="#main-content"
        class="skip-link"
      >
        Перейти к основному содержимому
      </a>
      <AppHeader />
      <UMain
        id="main-content"
        tabindex="-1"
      >
        <NuxtPage />
      </UMain>
      <AppFooter />
      <ScrollToTop />
    </div>
  </UApp>
</template>

<script setup lang="ts">
import { ru } from '@nuxt/ui/locale'

useHead({
  titleTemplate: '%s — Кадровый портал Сургутского района',
  htmlAttrs: {
    lang: 'ru'
  }
})

const { init } = useAccessibility()

usePrimaryFavicon()

const cookieConsent = useCookie('cookieConsent', {
  maxAge: 60 * 60 * 24 * 365,
  sameSite: 'lax',
  path: '/'
})
const toast = useToast()

onMounted(() => {
  init()

  if (!cookieConsent.value) {
    toast.add({
      id: 'cookie-consent',
      title: 'Файлы cookie',
      description: 'Используем cookie для корректной работы сайта и сохранения пользовательских настроек. Подробнее о защите данных — в Политике обработки персональных данных.',
      icon: 'i-lucide-cookie',
      color: 'neutral',
      duration: 0,
      progress: false,
      actions: [{
        label: 'Политика',
        color: 'neutral',
        variant: 'outline',
        to: '/privacy'
      }, {
        label: 'Понятно',
        color: 'primary',
        onClick: (event) => {
          event?.stopPropagation()
          cookieConsent.value = 'true'
          toast.remove('cookie-consent')
        }
      }]
    })
  }
})
</script>