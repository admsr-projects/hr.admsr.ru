export const TABLE_PAGE_SIZES = [5, 10, 20, 50] as const

/**
 * Поиск, сортировка и постраничный вывод строк таблицы.
 * Порядок: поиск → сортировка → страница. Любое изменение условий возвращает на первую страницу.
 */
export function useTableView<T, K extends string>(
  items: Ref<T[]> | ComputedRef<T[]>,
  options: {
    sort: Record<K, (item: T) => string | number | null | undefined>
    searchText: (item: T) => string
  },
) {
  const search = ref('')
  const pageSize = ref<number>(TABLE_PAGE_SIZES[0])
  const currentPage = ref(1)

  const filtered = computed(() => {
    const query = search.value.trim().toLowerCase()
    if (!query) return items.value
    return items.value.filter(item => options.searchText(item).toLowerCase().includes(query))
  })

  const { sorted, sortKey, sortDirection, toggleSort, ariaSort } = useTableSort(filtered, options.sort)

  const pageItems = computed(() => {
    const start = (currentPage.value - 1) * pageSize.value
    return sorted.value.slice(start, start + pageSize.value)
  })

  watch([search, sortKey, sortDirection, pageSize], () => {
    currentPage.value = 1
  })

  watch(() => items.value.length, () => {
    currentPage.value = 1
  })

  return {
    search,
    pageSize,
    currentPage,
    total: computed(() => filtered.value.length),
    pageItems,
    toggleSort,
    ariaSort,
  }
}
