export type SortDirection = 'asc' | 'desc'

/**
 * Сортировка строк таблицы по клику на заголовок столбца.
 * Клики по одному столбцу: по возрастанию → по убыванию → порядок с сервера.
 */
export function useTableSort<T, K extends string>(
  items: Ref<T[]> | ComputedRef<T[]>,
  accessors: Record<K, (item: T) => string | number | null | undefined>,
) {
  const sortKey = ref<K | null>(null)
  const sortDirection = ref<SortDirection>('asc')

  const sorted = computed(() => {
    const key = sortKey.value
    if (!key) return items.value

    const read = accessors[key]
    const factor = sortDirection.value === 'asc' ? 1 : -1

    return [...items.value].sort((a, b) => {
      const left = read(a)
      const right = read(b)
      if (left == null && right == null) return 0
      if (left == null) return 1
      if (right == null) return -1
      if (typeof left === 'number' && typeof right === 'number') return (left - right) * factor
      return String(left).localeCompare(String(right), 'ru', { numeric: true }) * factor
    })
  })

  function toggleSort(key: K) {
    if (sortKey.value !== key) {
      sortKey.value = key
      sortDirection.value = 'asc'
    }
    else if (sortDirection.value === 'asc') {
      sortDirection.value = 'desc'
    }
    else {
      sortKey.value = null
    }
  }

  function ariaSort(key: K): 'ascending' | 'descending' | 'none' {
    if (sortKey.value !== key) return 'none'
    return sortDirection.value === 'asc' ? 'ascending' : 'descending'
  }

  return { sorted, sortKey, sortDirection, toggleSort, ariaSort }
}
