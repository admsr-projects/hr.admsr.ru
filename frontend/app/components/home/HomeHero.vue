<template>
  <section class="bg-default">
    <UContainer class="flex min-w-0 flex-col gap-8 py-12 lg:gap-10 lg:py-16">
      <div class="grid min-w-0 gap-8 lg:grid-cols-2 lg:items-center lg:gap-12">
        <div class="flex min-w-0 flex-col items-start gap-5">
          <UBadge
            label="Кадровый портал администрации Сургутского района"
            color="primary"
            variant="soft"
            class="max-w-full whitespace-normal leading-snug"
          />

          <h1 class="text-balance text-4xl font-bold text-text-primary sm:text-5xl">
            Успешная команда
            <span class="text-primary">успешный район</span>
          </h1>

          <p class="max-w-xl text-pretty text-base text-text-muted">
            Вакансии, кадровый резерв и развитие для тех, кто работает на жителей Сургутского района — рядом с домом, с понятными условиями и предсказуемым ростом.
          </p>

          <div class="flex flex-wrap items-center gap-3">
            <UButton
              label="Смотреть вакансии"
              to="/vacancies"
              icon="i-lucide-briefcase"
            />
            <UButton
              label="О нас"
              to="/about"
              color="neutral"
              variant="soft"
              trailing-icon="i-lucide-arrow-up-right"
            />
            <UButton
              v-if="!kiosk"
              label="Обратная связь"
              to="/feedback"
              icon="i-lucide-message-square"
              color="neutral"
              variant="link"
            />
          </div>
        </div>

        <ul class="grid min-w-0 grid-cols-2 gap-3 sm:gap-4">
          <li
            v-for="item in careerItems"
            :key="item.to"
          >
            <NuxtLink
              :to="item.to"
              class="group flex h-full flex-col gap-3 rounded-xl bg-elevated p-4 transition-colors sm:p-6 duration-200 hover:bg-accented motion-reduce:transition-none"
            >
              <span
                class="flex size-10 items-center justify-center rounded-full bg-default text-primary"
                aria-hidden="true"
              >
                <UIcon
                  :name="item.icon"
                  class="size-5"
                />
              </span>
              <span class="flex flex-col gap-1">
                <span class="text-base font-semibold text-text-primary">
                  {{ item.label }}
                </span>
                <span class="hidden text-caption text-text-muted text-pretty sm:block">
                  {{ item.description }}
                </span>
              </span>
            </NuxtLink>
          </li>
        </ul>
      </div>

      <div class="relative h-56 w-full overflow-hidden rounded-xl sm:h-72 lg:h-96">
        <img
          src="/images/Picture.png"
          alt="Команда администрации Сургутского района"
          width="1408"
          height="420"
          loading="eager"
          class="block size-full object-cover"
        >
        <div class="absolute left-4 top-4 flex max-w-[calc(100%-2rem)] items-center gap-2 rounded-full bg-default/85 px-3 py-1.5 text-overline text-text-primary backdrop-blur-md">
          <span class="relative flex size-2 shrink-0">
            <span class="absolute inline-flex size-full animate-ping rounded-full bg-primary opacity-75 motion-reduce:hidden" />
            <span class="relative inline-flex size-2 rounded-full bg-primary" />
          </span>
          <span class="text-pretty">
            Сейчас в команде 420+ человек
          </span>
        </div>
      </div>
    </UContainer>
  </section>
</template>

<script setup lang="ts">
import { navIcons } from '~/data/navigation'

const kiosk = useKiosk()

const careerItems = [
  {
    label: 'Вакансии',
    description: kiosk ? 'Актуальные должности администрации района.' : 'Актуальные должности и форма отклика на сайте.',
    to: '/vacancies',
    icon: navIcons['/vacancies'],
  },
  {
    label: 'Молодёжь',
    description: 'Стажировки и первые профессиональные шаги.',
    to: '/youth',
    icon: navIcons['/youth'],
  },
  {
    label: 'Кадровый резерв',
    description: 'Путь для тех, кто планирует рост в муниципальной службе.',
    to: '/staffreserve',
    icon: navIcons['/staffreserve'],
  },
  {
    label: 'Профразвитие',
    description: 'Обучение, повышение квалификации и наставничество.',
    to: '/profdev',
    icon: navIcons['/profdev'],
  },
]
</script>
