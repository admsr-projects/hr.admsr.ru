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
        :class="sidebar ? 'lg:grid-cols-[282px_minmax(0,1fr)]' : undefined"
      >
        <aside
          v-if="sidebar"
          class="hidden lg:block lg:sticky lg:top-[calc(var(--ui-header-height,4rem)+1.5rem)]"
        >
          <DsSectionSidebar
            :title="sidebar.title"
            :items="sidebar.items"
          />
        </aside>

        <div class="flex w-full min-w-0 flex-col gap-4">
          <DsStandardPageHeader
            :title="title"
            :overline="overline"
            :description="description"
          >
            <template
              v-if="$slots.heroActions"
              #actions
            >
              <slot name="heroActions" />
            </template>
          </DsStandardPageHeader>

          <DsMarkdown
            v-if="intro"
            :source="intro"
            class="text-body-lg text-text-secondary leading-relaxed"
          />

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
  EDUCATION_PATH,
  type SidebarItem,
  resolveSectionMenu,
  resolveStandardSection,
  toNavigationMenuItems
} from '~/data/standard-pages'

const props = withDefaults(defineProps<{
  title: string
  overline?: string
  description?: string
  /** Вводный текст в формате Markdown */
  intro?: string
  /** @deprecated Не отображается — контекст раздела даёт меню слева и хлебные крошки */
  badge?: string
}>(), {
  overline: undefined,
  description: undefined,
  intro: undefined,
  badge: undefined
})

const route = useRoute()

const menu = computed(() => resolveSectionMenu(route.path))

// Страницы структуры администрации и её органов: меню не раздела «Наша команда», а самой страницы —
// все органы и заместители главы, которые их курируют
const inStructure = route.path.startsWith('/about/structure') || route.path.startsWith('/about/departments/')
const structureGroups = inStructure ? useAdminStructureMenu() : undefined

const sidebar = computed<{ title: string, items: SidebarItem[] } | null>(() => {
  if (structureGroups) {
    return {
      title: 'Структура администрации',
      items: [
        { label: 'Все органы', to: '/about/structure', active: route.path === '/about/structure' },
        ...structureGroups.value
      ]
    }
  }
  return menu.value ? { title: menu.value.title, items: menu.value.items } : null
})

// Горизонтальное меню на телефоне — только для страниц разделов (у структуры свой выбор заместителя на странице)
const sectionNavItems = computed(() =>
  menu.value && !inStructure ? toNavigationMenuItems(menu.value) : []
)

const breadcrumbs = computed<BreadcrumbItem[]>(() => {
  const items: BreadcrumbItem[] = [{ label: 'Главная', to: '/', icon: 'i-lucide-home' }]
  const section = resolveStandardSection(route.path)

  // Раздел «Антикоррупционное просвещение» вложен в «Нет коррупции!»
  if (route.path.startsWith(EDUCATION_PATH)) {
    items.push({ label: 'Нет коррупции!', to: '/anti-corruption' })
    if (route.path !== EDUCATION_PATH) items.push({ label: 'Антикоррупционное просвещение', to: EDUCATION_PATH })
    items.push({ label: props.title })
    return items
  }

  if (section) {
    // У раздела нет своей страницы — крошка ведёт на его первую страницу
    items.push({ label: section.label, to: section.items[0]?.to })
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
