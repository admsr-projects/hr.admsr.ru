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
      <CookieConsent />
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

usePrimaryFavicon()
</script>