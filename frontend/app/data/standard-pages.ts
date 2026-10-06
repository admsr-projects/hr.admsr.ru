import type { NavigationMenuItem } from '@nuxt/ui'
import { IS_KIOSK } from '~/composables/useKiosk'
import {
  anticorruptionNavGroup,
  careerNavGroup,
  educationNavItems,
  navIcons,
  teamNavGroup,
  type NavItem
} from '~/data/navigation'

export type StandardSectionId = 'team' | 'career' | 'anticorruption' | 'education' | 'info'

export interface StandardSection {
  id: StandardSectionId
  label: string
  items: NavItem[]
}

/**
 * Разделы для бокового меню и хлебных крошек.
 * «Вакансии» и «Информация» — только в боковом меню, в хедере они вынесены отдельно.
 */
export const standardSections: StandardSection[] = [
  {
    id: 'team',
    label: teamNavGroup.label,
    items: teamNavGroup.items
  },
  {
    id: 'career',
    label: careerNavGroup.label,
    items: careerNavGroup.items
  },
  {
    id: 'anticorruption',
    label: anticorruptionNavGroup.label,
    items: anticorruptionNavGroup.items
  },
  {
    id: 'education',
    label: 'Антикоррупционное просвещение',
    items: educationNavItems
  },
  {
    id: 'info',
    label: 'Информация',
    items: [
      // На киоске форм нет, раздел обратной связи скрыт
      ...(IS_KIOSK ? [] : [{ label: 'Обратная связь', to: '/feedback' }]),
      { label: 'Политика персональных данных', to: '/privacy' }
    ]
  }
]

/** Страницы, вложенные в пункт раздела: путь-префикс → путь пункта меню */
const nestedPaths: Array<{ prefix: string, parent: string }> = [
  { prefix: '/about/departments/', parent: '/about/structure' },
  { prefix: '/vacancyinfo/', parent: '/vacancies' }
]

function resolveMenuPath(path: string): string {
  return nestedPaths.find(entry => path.startsWith(entry.prefix))?.parent ?? path
}

export const EDUCATION_PATH = '/anti-corruption/education'

export function resolveStandardSection(path: string): StandardSection | undefined {
  // Вложенные страницы «Антикоррупционного просвещения» показывают меню своего раздела,
  // а сама страница раздела — меню «Нет коррупции!»
  if (path.startsWith(`${EDUCATION_PATH}/`)) return standardSections.find(section => section.id === 'education')
  const menuPath = resolveMenuPath(path)
  return standardSections.find(section =>
    section.items.some(item => item.to === menuPath)
  )
}

/** Пункт бокового меню; `children` — подпункты (до двух уровней вложенности) */
export interface SidebarItem {
  label: string
  /** Без `to` пункт — раскрывающаяся группа */
  to?: string
  active: boolean
  /** Подпункты показаны (для пункта со ссылкой) или группа раскрыта (для группы) */
  expanded?: boolean
  title?: string
  children?: SidebarItem[]
}

export interface SectionMenu {
  title: string
  items: SidebarItem[]
}

/** Меню раздела для боковой панели: все страницы раздела, активная помечена */
export function resolveSectionMenu(path: string): SectionMenu | null {
  const section = resolveStandardSection(path)
  if (!section) return null

  const menuPath = resolveMenuPath(path)
  return {
    title: section.label,
    items: section.items.map(item => ({
      label: item.label,
      to: item.to,
      active: item.to === menuPath
    }))
  }
}

export function toNavigationMenuItems(menu: SectionMenu): NavigationMenuItem[] {
  return menu.items.map(item => ({
    label: item.label,
    to: item.to,
    icon: item.to ? navIcons[item.to] : undefined,
    active: item.active
  }))
}
