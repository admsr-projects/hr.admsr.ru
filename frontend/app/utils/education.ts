// Страница «Антикоррупционное просвещение»: типы данных API и общие помощники

export interface EducationPage {
  eyebrow: string
  title: string
  lead: string
  approved_note: string
  period: string
  /** Markdown */
  intro: string
  source_note: string
}

export interface EducationCategory {
  id: number
  name: string
  short_name: string
  color: string
}

export interface EducationAct {
  abbr: string
  full_name: string
  changed_note: string
}

export interface EducationNorm {
  tag: string
  act: string
}

export interface EducationNote {
  n: number
  text: string
}

export interface EducationPosition {
  id: number
  title: string
  category: number
  subjects: string[]
  legal_basis: EducationNorm[]
  outcome: string
  outcome_label: string
  outcome_note: string
  in_favor_of_official: boolean
  municipal: boolean
  norm_changed: boolean
  key_quote: string
  facts_summary: string
  lesson: string
  page: number | null
  year: number | null
  years: string
  amount: number | null
  paragraphs: string[]
  notes: EducationNote[]
}

export interface EducationReview {
  page: EducationPage
  categories: EducationCategory[]
  acts: EducationAct[]
  outcomes: Array<{ id: string, label: string }>
  positions: EducationPosition[]
}

/** Цвет категории: классы Tailwind написаны целиком, чтобы попасть в сборку */
export const categoryColors: Record<string, { dot: string, bar: string, stroke: string, cssVar: string }> = {
  indigo: { dot: 'bg-indigo-500', bar: 'bg-indigo-500', stroke: 'stroke-indigo-500', cssVar: '--color-indigo-500' },
  violet: { dot: 'bg-violet-400', bar: 'bg-violet-400', stroke: 'stroke-violet-400', cssVar: '--color-violet-400' },
  teal: { dot: 'bg-teal-500', bar: 'bg-teal-500', stroke: 'stroke-teal-500', cssVar: '--color-teal-500' },
  emerald: { dot: 'bg-emerald-500', bar: 'bg-emerald-500', stroke: 'stroke-emerald-500', cssVar: '--color-emerald-500' },
  amber: { dot: 'bg-amber-500', bar: 'bg-amber-500', stroke: 'stroke-amber-500', cssVar: '--color-amber-500' },
  slate: { dot: 'bg-slate-500', bar: 'bg-slate-500', stroke: 'stroke-slate-500', cssVar: '--color-slate-500' },
}

export function categoryColor(color: string) {
  return categoryColors[color] ?? categoryColors.slate!
}

type BadgeColor = 'primary' | 'success' | 'info' | 'warning' | 'error' | 'neutral'

/** Исход дела: цвет метки (soft) и цвет точки / полосы */
export const outcomeStyles: Record<string, { badge: BadgeColor, dot: string, cssVar: string }> = {
  granted: { badge: 'success', dot: 'bg-success-500', cssVar: '--ui-color-success-500' },
  granted_partly: { badge: 'info', dot: 'bg-info-500', cssVar: '--ui-color-info-500' },
  lawful: { badge: 'primary', dot: 'bg-primary-500', cssVar: '--ui-color-primary-500' },
  denied: { badge: 'error', dot: 'bg-error-500', cssVar: '--ui-color-error-500' },
  remanded: { badge: 'warning', dot: 'bg-warning-500', cssVar: '--ui-color-warning-500' },
  motion_rejected: { badge: 'neutral', dot: 'bg-neutral-400', cssVar: '--ui-color-neutral-400' },
}

export const OUTCOME_NONE = 'none'
export const OUTCOME_NONE_LABEL = 'Итог прямо не назван'

export function outcomeStyle(outcome: string) {
  return outcomeStyles[outcome] ?? { badge: 'neutral' as BadgeColor, dot: 'bg-neutral-400', cssVar: '--ui-color-neutral-400' }
}

export function capitalize(value: string) {
  return value ? value[0]!.toUpperCase() + value.slice(1) : value
}

const rubles = new Intl.NumberFormat('ru-RU')

/** Сумма для списков: «8,60 млрд ₽», «7,97 млн ₽» */
export function formatAmount(value: number) {
  if (value >= 1e9) return `${(value / 1e9).toFixed(2).replace('.', ',')} млрд ₽`
  if (value >= 1e6) return `${(value / 1e6).toFixed(2).replace('.', ',')} млн ₽`
  return `${rubles.format(value)} ₽`
}

export function formatRubles(value: number) {
  return `${rubles.format(value)} ₽`
}

export function normalizeText(value: string) {
  return value.toLowerCase().replace(/ё/g, 'е')
}

export function escapeHtml(value: string) {
  return value.replace(/[&<>"']/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', '\'': '&#39;' })[ch]!)
}

function highlightPlain(text: string, pattern: RegExp | null) {
  const safe = escapeHtml(text)
  if (!pattern) return safe
  // Подсвечиваем только текст, не трогая HTML-сущности вроде &amp;
  return safe.split(/(&[a-z0-9#]+;)/i).map(part =>
    part.startsWith('&') && part.endsWith(';') ? part : part.replace(pattern, '<mark class="rounded-sm bg-primary/20 text-inherit">$1</mark>'),
  ).join('')
}

export function highlightPattern(query: string): RegExp | null {
  const terms = query.trim().split(/\s+/).filter(term => term.length > 1)
    .map(term => term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/[её]/gi, '[её]'))
  return terms.length ? new RegExp(`(${terms.join('|')})`, 'gi') : null
}

/** HTML абзаца: текст экранирован, совпадения с запросом подсвечены, «<1>» превращены в ссылки на сноски */
export function paragraphHtml(text: string, query: string, positionId: number) {
  const pattern = highlightPattern(query)
  return text.split(/(<\d+>)/).map((part) => {
    const marker = /^<(\d+)>$/.exec(part)
    if (marker) {
      const n = marker[1]
      return `<sup><a href="#fn-${positionId}-${n}" id="fnr-${positionId}-${n}" class="font-semibold text-primary no-underline">${n}</a></sup>`
    }
    return highlightPlain(part, pattern)
  }).join('')
}

export function highlightHtml(text: string, query: string) {
  return highlightPlain(text, highlightPattern(query))
}
