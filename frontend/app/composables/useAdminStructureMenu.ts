import type { SidebarItem } from '~/data/standard-pages'
import type { Deputy } from '~/data/departments'

function deputyShortName(deputy: Deputy) {
  return `${deputy.surname} ${deputy.name.charAt(0)}.${deputy.patronymic.charAt(0)}.`
}

/**
 * Подпункты «Структуры администрации» для бокового меню:
 * заместитель главы → курируемые им органы. Группа с текущим органом раскрыта.
 */
export function useAdminStructureMenu() {
  const route = useRoute()
  const { data: deputies } = useDeputiesList()
  const { departmentName } = useDepartmentNameMap()

  return computed<SidebarItem[]>(() =>
    (deputies.value ?? []).map((deputy) => {
      const children = deputy.departmentSlugs.map((slug) => {
        const to = `/about/departments/${slug}`
        return { label: departmentName(slug), to, active: route.path === to }
      })

      return {
        label: deputyShortName(deputy),
        title: deputy.role,
        active: false,
        expanded: children.some(child => child.active),
        children
      }
    })
  )
}
