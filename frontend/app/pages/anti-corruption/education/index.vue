<script setup lang="ts">
import type { EducationReview } from '~/utils/education'

useHead({ title: 'Нет коррупции! — антикоррупционное просвещение' })

const config = useRuntimeConfig()

// Тот же запрос, что и на странице обзора: данные берутся из общего кэша
const { data: review } = await useAsyncData('anti-corruption-education', () =>
  $fetch<EducationReview>(`${config.public.apiBaseUrl}/api/anti-corruption-education/`), {
  server: false,
})
</script>

<template>
  <DsStandardPage
    title="Антикоррупционное просвещение"
    description="Материалы по профилактике коррупции и формированию антикоррупционного поведения муниципальных служащих и жителей Сургутского района."
  >
    <DsContentSection
      title="Материалы раздела"
      description="Разборы судебной практики и другие материалы по антикоррупционному просвещению"
      spacing="md"
    >
      <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <DsLinkCard
          :title="review?.page.title || '27 правовых позиций по антикоррупционным делам'"
          :description="review?.page.lead || 'Практика Верховного Суда РФ по делам о противодействии коррупции: правовые позиции, нормы, аналитика и хронология.'"
          icon="i-lucide-scale"
          to="/anti-corruption/education/positions"
        />
      </div>
    </DsContentSection>
  </DsStandardPage>
</template>
