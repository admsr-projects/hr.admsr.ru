import type { ComputedRef, InjectionKey, Ref } from 'vue'
import {
  OUTCOME_NONE,
  normalizeText,
  type EducationAct,
  type EducationCategory,
  type EducationPosition,
  type EducationReview,
} from '~/utils/education'

export type EducationTab = 'overview' | 'analytics' | 'norms' | 'timeline' | 'text'

export interface EducationFilters {
  q: string
  cats: number[]
  subject: string
  outcome: string
  norm: string
  municipal: boolean
  changed: boolean
  favor: boolean
}

function emptyFilters(): EducationFilters {
  return { q: '', cats: [], subject: '', outcome: '', norm: '', municipal: false, changed: false, favor: false }
}

function countBy<T>(items: EducationPosition[], pick: (position: EducationPosition) => T | T[]) {
  const counts = new Map<T, number>()
  for (const position of items) {
    for (const key of [pick(position)].flat() as T[]) {
      counts.set(key, (counts.get(key) ?? 0) + 1)
    }
  }
  return counts
}

function createEducationReview(review: Ref<EducationReview | null | undefined>) {
  const filters = reactive<EducationFilters>(emptyFilters())
  const tab = ref<EducationTab>('overview')
  /** Позиция, открытая в окне */
  const openId = ref<number | null>(null)
  /** Позиция, подсвеченная на таймлайне после перехода из окна */
  const pulseId = ref<number | null>(null)
  /** Раскрытые пункты вкладки «Полный текст» */
  const expanded = ref<string[]>([])

  const positions = computed(() => review.value?.positions ?? [])
  const categories = computed(() => review.value?.categories ?? [])
  const acts = computed(() => review.value?.acts ?? [])

  const categoryById = computed(() => new Map<number, EducationCategory>(categories.value.map(c => [c.id, c])))
  const actByAbbr = computed(() => new Map<string, EducationAct>(acts.value.map(a => [a.abbr, a])))
  const positionById = computed(() => new Map<number, EducationPosition>(positions.value.map(p => [p.id, p])))

  // Поисковый индекс считается один раз на позицию
  const searchIndex = computed(() => new Map(positions.value.map(p => [
    p.id,
    normalizeText([
      p.id, p.title, p.key_quote, p.facts_summary, p.lesson, p.outcome_label, p.outcome_note,
      ...p.subjects, ...p.legal_basis.map(n => n.tag), ...p.paragraphs, ...p.notes.map(n => n.text),
    ].join(' ')),
  ])))

  function matches(position: EducationPosition) {
    if (filters.cats.length && !filters.cats.includes(position.category)) return false
    if (filters.subject && !position.subjects.includes(filters.subject)) return false
    if (filters.outcome) {
      const outcome = position.outcome || OUTCOME_NONE
      if (outcome !== filters.outcome) return false
    }
    if (filters.norm && !position.legal_basis.some(n => n.tag === filters.norm)) return false
    if (filters.municipal && !position.municipal) return false
    if (filters.changed && !position.norm_changed) return false
    if (filters.favor && !position.in_favor_of_official) return false
    if (filters.q.trim()) {
      const index = searchIndex.value.get(position.id) ?? ''
      if (!normalizeText(filters.q).split(/\s+/).filter(Boolean).every(term => index.includes(term))) return false
    }
    return true
  }

  const filtered = computed(() => positions.value.filter(matches))
  const filteredIds = computed(() => new Set(filtered.value.map(p => p.id)))

  const activeCount = computed(() =>
    (filters.q.trim() ? 1 : 0) + filters.cats.length + (filters.subject ? 1 : 0) + (filters.outcome ? 1 : 0)
    + (filters.norm ? 1 : 0) + Number(filters.municipal) + Number(filters.changed) + Number(filters.favor),
  )

  // Варианты выпадающих списков считаются по всем позициям, а не по выборке
  const subjectCounts = computed(() => [...countBy(positions.value, p => p.subjects)].sort((a, b) => b[1] - a[1]))
  const outcomeCounts = computed(() => countBy(positions.value, p => p.outcome || OUTCOME_NONE))
  const normCounts = computed(() =>
    [...countBy(positions.value, p => p.legal_basis.map(n => n.tag))]
      .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0], 'ru')),
  )
  const categoryCounts = computed(() => countBy(positions.value, p => p.category))

  function resetFilters() {
    Object.assign(filters, emptyFilters())
  }

  function toggleCategory(id: number) {
    const index = filters.cats.indexOf(id)
    if (index === -1) filters.cats.push(id)
    else filters.cats.splice(index, 1)
  }

  function toggleSubject(subject: string) {
    filters.subject = filters.subject === subject ? '' : subject
  }

  function toggleOutcome(outcome: string) {
    filters.outcome = filters.outcome === outcome ? '' : outcome
  }

  function toggleNorm(tag: string) {
    filters.norm = filters.norm === tag ? '' : tag
  }

  function setHash(hash: string) {
    if (!import.meta.client) return
    history.replaceState(history.state, '', `${location.pathname}${location.search}${hash}`)
  }

  function openPosition(id: number) {
    openId.value = id
    setHash(`#pos-${id}`)
  }

  function closePosition() {
    openId.value = null
    setHash('')
  }

  /** Если позиции нет в текущей выборке, сбрасываем фильтры, чтобы её показать */
  function ensureVisible(id: number) {
    if (!filteredIds.value.has(id)) resetFilters()
  }

  async function scrollToId(elementId: string) {
    await nextTick()
    // Пока окно закрывается, прокрутка страницы заблокирована — ждём снятия блокировки
    for (let attempt = 0; attempt < 20 && document.body.style.overflow === 'hidden'; attempt++) {
      await new Promise(resolve => setTimeout(resolve, 50))
    }
    document.getElementById(elementId)?.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' })
  }

  async function showOnTimeline(id: number) {
    closePosition()
    ensureVisible(id)
    tab.value = 'timeline'
    pulseId.value = id
    await scrollToId(`tl-${id}`)
    setTimeout(() => {
      if (pulseId.value === id) pulseId.value = null
    }, 3200)
  }

  async function showInText(id: number) {
    closePosition()
    ensureVisible(id)
    tab.value = 'text'
    const value = `ft-${id}`
    if (!expanded.value.includes(value)) expanded.value = [...expanded.value, value]
    await scrollToId(value)
  }

  return {
    review,
    filters,
    tab,
    openId,
    pulseId,
    expanded,
    positions,
    categories,
    acts,
    categoryById,
    actByAbbr,
    positionById,
    filtered,
    filteredIds,
    activeCount,
    subjectCounts,
    outcomeCounts,
    normCounts,
    categoryCounts,
    resetFilters,
    toggleCategory,
    toggleSubject,
    toggleOutcome,
    toggleNorm,
    openPosition,
    closePosition,
    showOnTimeline,
    showInText,
  }
}

export type EducationContext = ReturnType<typeof createEducationReview>

const EDUCATION_KEY: InjectionKey<EducationContext> = Symbol('education-review')

/** Создаёт состояние страницы и отдаёт его вложенным компонентам */
export function provideEducationReview(review: Ref<EducationReview | null | undefined> | ComputedRef<EducationReview | null | undefined>) {
  const context = createEducationReview(review)
  provide(EDUCATION_KEY, context)
  return context
}

export function useEducationReview(): EducationContext {
  const context = inject(EDUCATION_KEY)
  if (!context) throw new Error('useEducationReview() вызван вне страницы «Антикоррупционное просвещение»')
  return context
}
