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
      <template v-if="kiosk">
        <KioskNav />
      </template>
      <template v-else>
        <ScrollToTop />
        <CookieConsent />
      </template>
    </div>
  </UApp>
</template>

<script setup lang="ts">
import { ru } from '@nuxt/ui/locale'

const kiosk = useKiosk()

useHead({
  titleTemplate: '%s — Кадровый портал Сургутского района',
  htmlAttrs: {
    lang: 'ru',
    class: kiosk ? 'kiosk' : undefined
  }
})

usePrimaryFavicon()
</script>