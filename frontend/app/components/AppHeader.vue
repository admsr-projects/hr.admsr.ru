<template>
  <UHeader>
    <template #left>
      <NuxtLink
        to="/"
        class="flex min-w-0 items-center gap-2.5 rounded-md"
        aria-label="На главную — Кадровый портал Администрации Сургутского района"
      >
        <AppLogo :size="28" />
        <div class="hidden min-w-0 flex-col sm:flex">
          <span class="truncate font-semibold text-highlighted">
            {{ siteContact.portalName }}
          </span>
          <span class="truncate text-xs text-muted">
            {{ siteContact.organization }}
          </span>
        </div>
      </NuxtLink>
    </template>

    <UNavigationMenu
      :items="desktopNavItems"
      variant="link"
      color="primary"
      content-orientation="vertical"
      aria-label="Основная навигация"
      arrow
      class="hidden lg:flex"
      :ui="{
        link: 'font-medium',
        linkLabel: 'font-medium',
        childLink: 'items-start gap-2 font-medium',
        childLinkIcon: 'size-5 mt-0.5 text-dimmed shrink-0',
        childLinkWrapper: 'flex min-w-0 flex-col gap-0.5',
        childLinkLabel: 'font-medium',
        childLinkDescription: 'text-xs text-muted leading-snug whitespace-normal',
        viewport: 'p-1',
        content: 'w-80 overflow-x-hidden',
      }"
    />

    <template #right>
      <div class="flex items-center gap-1.5">
        <AppSearch />
        <UColorModeButton />
        <UButton
          label="Вакансии"
          to="/vacancies"
          icon="i-lucide-briefcase"
          color="primary"
          class="hidden lg:inline-flex"
        />
      </div>
    </template>

    <template #body>
      <UButton
        block
        variant="soft"
        color="neutral"
        icon="i-lucide-search"
        label="Поиск по порталу"
        class="mb-4"        
        @click="openSearch"
      />

      <UNavigationMenu
        :items="mobileNavItems"
        orientation="vertical"
        variant="link"
        color="primary"
        class="-mx-2.5"
        :ui="{
          link: 'font-medium',
          linkLabel: 'font-medium',
          childLink: 'items-start gap-2 py-2 font-medium',
          childLinkIcon: 'size-5 mt-0.5 text-dimmed shrink-0',
          childLinkWrapper: 'flex min-w-0 flex-col gap-0.5',
          childLinkLabel: 'font-medium',
          childLinkDescription: 'text-xs text-muted leading-snug',
        }"
      />

      <UButton
        label="Вакансии"
        to="/vacancies"
        icon="i-lucide-briefcase"
        color="primary"
        variant="solid"
        block
        class="mt-4"
      />
    </template>
  </UHeader>
</template>

<script setup lang="ts">
import { buildDesktopNavItems, buildMobileNavItems, siteContact } from '~/data/navigation'

const route = useRoute()
const desktopNavItems = computed(() => buildDesktopNavItems(route.path))
const mobileNavItems = computed(() => buildMobileNavItems(route.path))
const { openSearch } = usePortalSearch()
</script>
