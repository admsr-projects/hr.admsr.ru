<template>
  <UButton
    icon="i-lucide-search"
    color="neutral"
    variant="ghost"
    aria-label="Поиск по порталу"
    @click="open = true"
  />

  <UModal
    v-model:open="open"
    title="Поиск по порталу"
    description="Разделы, вакансии, новости, мероприятия, конкурсы, документы, структура и контакты"
    :ui="{ content: 'sm:max-w-xl' }"
  >
    <template #content>
      <UCommandPalette
        v-model:search-term="searchTerm"
        :groups="groups"
        placeholder="Введите запрос: вакансия, документ, новость, фамилия…"
        :input="{ fixed: true }"
        :ui="{ viewport: 'max-h-[60vh]' }"
        :fuse="{ resultLimit: 200 }"
        preserve-group-order
        @update:model-value="onSelect"
      />
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { useDebounceFn } from '@vueuse/core'
import { mainNavItems, navIcons } from '~/data/navigation'

interface PortalSearchResponse {
  vacancies?: Array<{ id: number, title: string, branch?: string | null }>
  news?: Array<{ id: number, title: string, date?: string }>
  events?: Array<{ id: number, title: string, date?: string, location?: string }>
  competitions?: Array<{ title: string, section: string, to: string }>
  documents?: Array<{ title: string, section: string, to: string, page: string, file: boolean }>
  structure?: Array<{ title: string, section: string, to: string }>
  contacts?: Array<{
    id: number
    surname?: string | null
    name?: string | null
    patronym?: string | null
    role?: string | null
    phone?: string | null
    email?: string | null
    to?: string
  }>
}

interface SearchItem {
  label: string
  description?: string
  to: string
  icon: string
  target?: string
}

const { open, closeSearch } = usePortalSearch()
const searchTerm = ref('')
const config = useRuntimeConfig()

const results = ref<Record<string, SearchItem[]>>({})

const extraPages = [
  { label: 'Обратная связь', to: '/feedback', icon: navIcons['/feedback'] ?? 'i-lucide-arrow-right' },
  { label: 'Политика конфиденциальности', to: '/privacy', icon: 'i-lucide-shield' },
]

const resultGroups = [
  { id: 'vacancies', label: 'Вакансии' },
  { id: 'news', label: 'Новости' },
  { id: 'events', label: 'Мероприятия' },
  { id: 'competitions', label: 'Конкурсы' },
  { id: 'documents', label: 'Документы' },
  { id: 'structure', label: 'Структура и кадровый резерв' },
  { id: 'contacts', label: 'Контакты' },
]

const groups = computed(() => {
  const result: Array<{
    id: string
    label: string
    ignoreFilter?: boolean
    items: SearchItem[]
  }> = []

  result.push({
    id: 'pages',
    label: 'Разделы',
    items: [
      ...mainNavItems.map(item => ({
        label: item.label,
        to: item.to,
        icon: navIcons[item.to] ?? 'i-lucide-arrow-right',
      })),
      ...extraPages,
    ],
  })

  for (const group of resultGroups) {
    const items = results.value[group.id] ?? []
    if (items.length) {
      result.push({ id: group.id, label: group.label, ignoreFilter: true, items })
    }
  }

  return result
})

function formatFullName(value: { surname?: string | null, name?: string | null, patronym?: string | null }) {
  return [value.surname, value.name, value.patronym].filter(Boolean).join(' ').trim()
}

function formatDate(value?: string) {
  if (!value) return ''
  return new Date(value).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
}

function mapResults(data: PortalSearchResponse): Record<string, SearchItem[]> {
  return {
    vacancies: (data.vacancies ?? []).map(v => ({
      label: v.title,
      description: v.branch || 'Администрация Сургутского района',
      to: `/vacancyinfo/${v.id}`,
      icon: 'i-lucide-briefcase',
    })),
    news: (data.news ?? []).map(n => ({
      label: n.title,
      description: formatDate(n.date),
      to: `/news/${n.id}`,
      icon: 'i-lucide-newspaper',
    })),
    events: (data.events ?? []).map(e => ({
      label: e.title,
      description: [formatDate(e.date), e.location].filter(Boolean).join(' · '),
      to: `/events/${e.id}`,
      icon: 'i-lucide-calendar',
    })),
    competitions: (data.competitions ?? []).map(c => ({
      label: c.title,
      description: c.section,
      to: c.to,
      icon: 'i-lucide-file-badge',
    })),
    documents: (data.documents ?? []).map(d => ({
      label: d.title,
      description: d.file ? `${d.section} · открыть файл` : d.section,
      to: d.to,
      icon: 'i-lucide-file-text',
      ...(d.file ? { target: '_blank' } : {}),
    })),
    structure: (data.structure ?? []).map(s => ({
      label: s.title,
      description: s.section,
      to: s.to,
      icon: 'i-lucide-network',
    })),
    contacts: (data.contacts ?? []).map((c) => {
      const details = [c.role, c.phone, c.email].filter(Boolean).join(' · ')
      return {
        label: formatFullName(c) || 'Сотрудник',
        description: details || 'Справочник сотрудников',
        to: c.to || '/contacts#contacts-directory',
        icon: 'i-lucide-users',
      }
    }),
  }
}

const fetchPortalSearch = useDebounceFn(async (term: string) => {
  const query = term.trim()
  if (query.length < 2) {
    results.value = {}
    return
  }

  try {
    const data = await $fetch<PortalSearchResponse>(`${config.public.apiBaseUrl}/api/search/`, {
      params: { q: query, limit: 50 },
    })
    results.value = mapResults(data)
  }
  catch {
    results.value = {}
  }
}, 300)

watch(searchTerm, fetchPortalSearch)

watch(open, (isOpen) => {
  if (!isOpen) {
    searchTerm.value = ''
    results.value = {}
  }
})

function onSelect() {
  closeSearch()
  searchTerm.value = ''
  results.value = {}
}

defineShortcuts({
  meta_k: {
    usingInput: true,
    handler: () => {
      open.value = !open.value
    },
  },
})
</script>
