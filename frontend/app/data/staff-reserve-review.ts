// Страница «Кадровые резервы: порядок формирования» (/staffreserve/review).
// Сами данные лежат в staff-reserve-review.json — это пересказ трёх муниципальных актов с указанием пунктов.
// Чтобы обновить страницу после изменения актов, замените JSON и поправьте дату в meta.actsCheckedOn.
import raw from './staff-reserve-review.json'

export type ReserveId = 'admin' | 'institutions' | 'personnel'

/** Значение показателя по каждому из трёх резервов; null — акт этого не устанавливает */
export type PerReserve<T> = Record<ReserveId, T | null>

export interface ReserveWay {
  name: string
  detail: string
  ref: string
}

export interface Reserve {
  id: ReserveId
  short: string
  name: string
  normative: string
  act: string
  editions: string
  federalBasis: string | null
  targetPositions: string
  targetRef: string
  positionsCount: number | null
  positionsNote: string
  responsible: string
  responsibleRef: string
  responsibleDetail?: string
  commission: string
  commissionAct: string
  maxCandidates: number
  maxCandidatesRef: string
  term: string
  termYears: number
  termRef: string
  extension: string
  extensionYears: number
  extensionNote: string
  levels: string[]
  levelsRef: string
  ways: ReserveWay[]
  ipr: {
    develop: string
    developRef: string
    report: string
    reportRef: string
    mentor: string
    mentorRef: string
  }
  use: string | null
  useRef: string | null
  development?: {
    act: string
    scope: string
    formats: Array<{ name: string, detail: string }>
    frequency: string
    period: string
    ref: string
  }
  exclusions: string[]
  exclusionsRef: string
}

export interface RequirementValue {
  /** yes — требование действует всегда, cond — только для отдельных должностей */
  status: 'yes' | 'cond'
  text: string
  ref: string
  /** Для возраста: границы в годах */
  min?: number
  max?: number
}

export interface Requirement {
  key: string
  label: string
  values: PerReserve<RequirementValue>
}

export interface DocumentsList {
  ref: string
  items: string[]
  note: string | null
}

export interface Stage {
  title: string
  term: string | null
  /** Срок в днях для крупной цифры на карточке этапа; null — срок не числовой */
  days?: number | null
  unit?: string | null
  termNote?: string
  responsible: string
  ref: string
}

export interface Scoring {
  ref: string
  rules: string[]
}

export interface ReadinessLevel {
  id: string
  name: string
  criterion: string
  activities: { dpo: boolean, internship: boolean, testing: boolean }
}

export interface EvaluationMethod {
  id: string
  name: string
  mandatory: boolean
  desc: string
  source: string
  allowed: PerReserve<string>
}

export interface PositionGroup {
  id: string
  name: string
  reserve: ReserveId
}

export interface ReservePosition {
  id: string
  name: string
  category: string
  group: string
  kind: string
  reserve: ReserveId
  source: string
  ref: string
  isGroup?: boolean
}

export interface ReviewSource {
  id: string
  title: string
  about: string
}

export interface StaffReserveReview {
  meta: {
    title: string
    subtitle: string
    organization: string
    actsCheckedOn: string
    actsCheckedNote: string
  }
  reserves: Reserve[]
  requirements: Requirement[]
  documents: PerReserve<DocumentsList>
  stages: Record<ReserveId, Stage[]>
  scoring: Record<ReserveId, Scoring>
  levels: ReadinessLevel[]
  levelsRefs: Record<ReserveId, string>
  levelsNote: string
  evaluationMethods: EvaluationMethod[]
  methodsNote: string
  positionGroups: PositionGroup[]
  positionsRepealed: string
  positions: ReservePosition[]
  system: {
    steps: Array<{ name: string, desc: string }>
    sources: Array<{ name: string, desc: string }>
  }
  antiCorruption: {
    act: string
    measures: string[]
  }
  sources: ReviewSource[]
}

export const staffReserveReview = raw as unknown as StaffReserveReview

/** Цветная точка у названия резерва: различает три резерва, название всегда стоит рядом */
export const reserveDot: Record<ReserveId, string> = {
  admin: 'bg-indigo-500',
  institutions: 'bg-teal-500',
  personnel: 'bg-amber-500'
}

/** Цвет сферы в структуре перечня должностей учреждений */
export const groupDot: Record<string, string> = {
  culture: 'bg-indigo-500',
  sport: 'bg-teal-500',
  education: 'bg-emerald-500',
  housing: 'bg-slate-500',
  other: 'bg-violet-400'
}

/** Цвет метки с номером акта (вариант soft) */
export const reserveBadge: Record<ReserveId, 'info' | 'success' | 'warning'> = {
  admin: 'info',
  institutions: 'success',
  personnel: 'warning'
}

export const reserveIds: ReserveId[] = ['admin', 'institutions', 'personnel']

export function findReserve(id: ReserveId): Reserve {
  return staffReserveReview.reserves.find(reserve => reserve.id === id)!
}
