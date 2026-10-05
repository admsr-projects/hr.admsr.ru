<template>
  <div class="ds-inner">
    <DsSectionToolbar
      v-if="sectionNavItems.length"
      :items="sectionNavItems"
      class="lg:hidden"
    />

    <DsBreadcrumbs :items="breadcrumbs" />

    <div class="ds-container pb-12 pt-4 lg:pb-16 lg:pt-0">
      <div
        class="lg:grid lg:items-start lg:gap-6"
        :class="menu ? 'lg:grid-cols-[282px_minmax(0,1fr)]' : undefined"
      >
        <aside
          v-if="menu"
          class="hidden lg:block lg:sticky lg:top-[calc(var(--ui-header-height,4rem)+1.5rem)]"
        >
          <DsSectionSidebar
            :title="menu.title"
            :items="sidebarItems"
          />
        </aside>

        <div class="flex w-full min-w-0 flex-col gap-4">
          <DsStandardPageHeader
            :title="title"
            :description="description"
          >
            <template
              v-if="$slots.heroActions"
              #actions
            >
              <slot name="heroActions" />
            </template>
          </DsStandardPageHeader>

          <p
            v-if="intro"
            class="text-body-lg text-text-secondary leading-relaxed whitespace-pre-line text-pretty"
          >
            {{ intro }}
          </p>

          <div class="flex flex-col gap-4">
            <slot />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { BreadcrumbItem } from '~/data/breadcrumbs'
import {
  type SidebarItem,
  resolveSectionMenu,
  resolveStandardSection,
  toNavigationMenuItems
} from '~/data/standard-pages'

const props = withDefaults(defineProps<{
  title: string
  description?: string
  intro?: string
  /** @deprecated Не отображается — контекст раздела даёт меню слева и хлебные крошки */
  badge?: string
}>(), {
  description: undefined,
  intro: undefined,
  badge: undefined
})

const route = useRoute()

const menu = computed(() => resolveSectionMenu(route.path))

// Подпункты «Структуры администрации» (заместители → органы) нужны только на её страницах
const inStructure = route.path.startsWith('/about/structure') || route.path.startsWith('/about/departments/')
const structureGroups = inStructure ? useAdminStructureMenu() : undefined

const sidebarItems = computed<SidebarItem[]>(() =>
  (menu.value?.items ?? []).map(item =>
    item.to === '/about/structure' && structureGroups
      ? { ...item, expanded: true, children: structureGroups.value }
      : item
  )
)

const sectionNavItems = computed(() =>
  menu.value ? toNavigationMenuItems(menu.value) : []
)

const breadcrumbs = computed<BreadcrumbItem[]>(() => {
  const items: BreadcrumbItem[] = [{ label: 'Главная', to: '/', icon: 'i-lucide-home' }]
  const section = resolveStandardSection(route.path)

  if (section) {
    items.push({ label: section.label })
  }

  if (route.path.startsWith('/about/departments/')) {
    items.push({ label: 'Структура администрации', to: '/about/structure' })
  }
  else if (route.path.startsWith('/vacancyinfo/')) {
    items.push({ label: 'Вакансии', to: '/vacancies' })
  }

  items.push({ label: props.title })
  return items
})
</script>
