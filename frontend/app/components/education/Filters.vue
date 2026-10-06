<template>
  <UCard
    variant="soft"
    :ui="{ body: 'flex flex-col gap-4 p-4 sm:p-4' }"
    role="search"
    aria-label="Фильтры позиций (применяются ко всем вкладкам)"
  >
    <div class="flex flex-wrap items-center gap-2">
      <UInput
        v-if="!kiosk"
        v-model="edu.filters.q"
        type="search"
        icon="i-lucide-search"
        placeholder="Поиск: «супруг», «займ», «ст. 13.1»…"
        aria-label="Поиск по позициям"
        autocomplete="off"
        class="min-w-48 flex-1"
      />

      <UButton
        label="Фильтры"
        icon="i-lucide-sliders-horizontal"
        color="neutral"
        variant="soft"
        class="cursor-pointer bg-default"
        :trailing-icon="open ? 'i-lucide-chevron-up' : 'i-lucide-chevron-down'"
        :aria-expanded="open"
        aria-controls="education-filters"
        @click="open = !open"
      >
        <template
          v-if="edu.activeCount.value"
          #trailing
        >
          <UBadge
            color="primary"
            variant="soft"
          >
            {{ edu.activeCount.value }}
          </UBadge>
        </template>
      </UButton>

      <UButton
        v-if="edu.activeCount.value"
        label="Сбросить"
        icon="i-lucide-x"
        color="neutral"
        variant="soft"
        class="cursor-pointer bg-default"
        @click="edu.resetFilters()"
      />

      <UDropdownMenu
        v-if="!kiosk"
        :items="actions"
        :content="{ align: 'end' }"
      >
        <UButton
          icon="i-lucide-ellipsis"
          color="neutral"
          variant="soft"
          class="cursor-pointer bg-default"
          aria-label="Экспорт и печать"
        />
      </UDropdownMenu>

      <p
        class="ml-auto text-caption text-text-muted"
        aria-live="polite"
      >
        Показано <span class="font-semibold text-text-primary">{{ edu.filtered.value.length }}</span> из {{ edu.positions.value.length }}
      </p>
    </div>

    <div
      v-show="open"
      id="education-filters"
      class="flex flex-col gap-4"
    >
      <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <USelectMenu
          v-model="edu.filters.cats"
          :items="categoryItems"
          value-key="value"
          multiple
          :search-input="false"
          placeholder="Все категории"
          aria-label="Категории"
          class="w-full"
        />
        <USelect
          v-model="subjectModel"
          :items="subjectItems"
          aria-label="Кто фигурирует"
          class="w-full"
        />
        <USelect
          v-model="outcomeModel"
          :items="outcomeItems"
          aria-label="Исход дела"
          class="w-full"
        />
        <USelect
          v-model="normModel"
          :items="normItems"
          aria-label="Применённая норма"
          class="w-full"
        />
      </div>

      <div class="flex flex-wrap items-center gap-x-6 gap-y-3">
        <UCheckbox
          v-model="edu.filters.municipal"
          label="Касается муниципального уровня"
        />
        <UCheckbox
          v-model="edu.filters.changed"
          label="Норма изменена"
        />
        <UCheckbox
          v-model="edu.filters.favor"
          label="Решено в пользу служащего / ответчика"
        />
      </div>
    </div>
  </UCard>
</template>

<script setup lang="ts">
import { OUTCOME_NONE, OUTCOME_NONE_LABEL } from '~/utils/education'

const ALL = '__all'

const edu = useEducationReview()
const kiosk = useKiosk()
const open = ref(false)

const categoryItems = computed(() =>
  edu.categories.value.map(category => ({
    label: `${category.short_name} (${edu.categoryCounts.value.get(category.id) ?? 0})`,
    value: category.id,
  })),
)

const actions = computed(() => [[
  { label: 'Экспорт JSON', icon: 'i-lucide-download', disabled: !edu.filtered.value.length, onSelect: exportJson },
  { label: 'Печать', icon: 'i-lucide-printer', onSelect: printPage },
]])

function selectModel(key: 'subject' | 'outcome' | 'norm') {
  return computed({
    get: () => edu.filters[key] || ALL,
    set: (value: string) => {
      edu.filters[key] = value === ALL ? '' : value
    },
  })
}

const subjectModel = selectModel('subject')
const outcomeModel = selectModel('outcome')
const normModel = selectModel('norm')

const subjectItems = computed(() => [
  { label: 'Все субъекты', value: ALL },
  ...edu.subjectCounts.value.map(([subject, count]) => ({ label: `${subject} (${count})`, value: subject })),
])

const outcomeItems = computed(() => {
  const labels = new Map((edu.review.value?.outcomes ?? []).map(o => [o.id, o.label]))
  const counts = edu.outcomeCounts.value
  return [
    { label: 'Все исходы', value: ALL },
    ...[...labels].map(([id, label]) => ({ label: `${label} (${counts.get(id) ?? 0})`, value: id })),
    { label: `${OUTCOME_NONE_LABEL} (${counts.get(OUTCOME_NONE) ?? 0})`, value: OUTCOME_NONE },
  ]
})

const normItems = computed(() => [
  { label: 'Все нормы', value: ALL },
  ...edu.normCounts.value.map(([tag, count]) => ({ label: `${tag} (${count})`, value: tag })),
])

function exportJson() {
  const list = edu.filtered.value
  const payload = {
    source: edu.review.value?.page.eyebrow,
    exported: new Date().toISOString(),
    count: list.length,
    positions: list.map(position => ({
      id: position.id,
      title: position.title,
      category: edu.categoryById.value.get(position.category)?.name,
      subjects: position.subjects,
      legal_basis: position.legal_basis.map(norm => norm.tag),
      outcome: position.outcome_label || null,
      outcome_note: position.outcome_note || null,
      facts_summary: position.facts_summary,
      key_quote: position.key_quote,
      page: position.page,
    })),
  }
  const url = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' }))
  const link = document.createElement('a')
  link.href = url
  link.download = `antikorruptsionnoe-prosveshchenie_${list.length}-pozitsiy.json`
  document.body.appendChild(link)
  link.click()
  link.remove()
  setTimeout(() => URL.revokeObjectURL(url), 2000)
}

function printPage() {
  window.print()
}
</script>
