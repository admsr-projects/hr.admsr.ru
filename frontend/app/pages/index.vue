<template>
  <div class="relative min-w-0 overflow-x-clip">
    <AppContainerGuides />

    <HomeHero />

    <VacancyCarousel
      title="Актуальные вакансии"
      subtitle="Открытые должности в администрации Сургутского района"
      :vacancies="vacanciesData ?? []"
      :pending="vacanciesPending"
    />

    <PartnersLogos />

    <HomeNews :posts="posts" />

    <HomeValuesBento />

    <VacancySubscribeForm
      v-if="!kiosk"
      promo
    />

    <HomeFaq />

  </div>
</template>

<script setup lang="ts">
useHead({ title: 'Главная' })

const config = useRuntimeConfig()
const kiosk = useKiosk()

const { data: vacanciesData, pending: vacanciesPending } = await useAsyncData('vacancies', () =>
  $fetch(`${config.public.apiBaseUrl}/api/vacancies/`), { server: false })

const { data: posts } = await useAsyncData('news-posts', () =>
  $fetch(`${config.public.apiBaseUrl}/api/news/`), { server: false })
</script>
