<template>
  <section
    v-if="pending || partners.length"
    class="bg-default"
  >
    <UContainer class="pb-12 lg:pb-16">
      <!-- До трёх организаций: заголовок слева, логотипы справа. Больше — заголовок сверху, сетка по четыре в ряд -->
      <div
        class="grid min-w-0 gap-6 rounded-xl bg-elevated p-6 lg:p-8"
        :class="many ? 'lg:gap-8' : 'lg:grid-cols-[minmax(0,1fr)_minmax(0,2fr)] lg:items-center lg:gap-8'"
      >
        <div class="flex min-w-0 flex-col gap-3">
          <h2 class="text-h2 text-text-primary text-balance">
            С нами работают
          </h2>
          <p
            class="text-pretty text-base text-text-muted"
            :class="many && 'max-w-3xl'"
          >
            Федеральные и региональные организации, с которыми мы выстраиваем прозрачную кадровую политику и социальные гарантии для сотрудников.
          </p>
        </div>

        <div class="flex min-w-0 flex-col items-start gap-4">
          <ul
            v-if="pending"
            class="grid w-full gap-4 sm:grid-cols-3"
            aria-busy="true"
            aria-label="Загрузка партнёров"
          >
            <li
              v-for="index in 3"
              :key="index"
            >
              <USkeleton class="h-28 w-full rounded-xl" />
            </li>
          </ul>

          <ul
            v-else
            class="grid w-full gap-4"
            :class="many ? 'grid-cols-2 sm:grid-cols-3 lg:grid-cols-4' : 'sm:grid-cols-3'"
            aria-label="Партнёры администрации"
          >
            <li
              v-for="partner in visiblePartners"
              :key="partner.id"
            >
              <PartnerLogoLink
                :logo="partner"
                class="h-full"
              />
            </li>
          </ul>

          <UButton
            v-if="partners.length > COLLAPSED_COUNT"
            :label="expanded ? 'Свернуть' : `Показать всех (${partners.length})`"
            :icon="expanded ? 'i-lucide-chevron-up' : 'i-lucide-chevron-down'"
            color="neutral"
            variant="soft"
            class="cursor-pointer bg-default"
            :aria-expanded="expanded"
            @click="expanded = !expanded"
          />
        </div>
      </div>
    </UContainer>
  </section>
</template>

<script setup lang="ts">
export interface WorkPartnerItem {
  id: number
  name: string
  url: string
  image: string
}

const config = useRuntimeConfig()

const { data: partnersData, pending } = await useAsyncData(
  'work-partners',
  () => $fetch<WorkPartnerItem[]>(`${config.public.apiBaseUrl}/api/work-partners/`),
  { server: false },
)

const partners = computed(() => partnersData.value ?? [])

// Показываем первые 8 организаций, остальные — по кнопке
const COLLAPSED_COUNT = 8
const expanded = ref(false)
const many = computed(() => partners.value.length > 3)
const visiblePartners = computed(() =>
  expanded.value ? partners.value : partners.value.slice(0, COLLAPSED_COUNT),
)
</script>
