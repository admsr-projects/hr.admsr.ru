<template>
  <div class="flex flex-col gap-4">
    <div class="flex flex-col gap-4 lg:flex-row lg:items-center">
      <DsTableSearch
        v-model="search"
        variant="outline"
        placeholder="Поиск по наименованию: детский сад, Лянтор, спортивная школа"
        class="min-w-0 lg:flex-1"
      />
      <USelect
        v-model="reserve"
        :items="reserveItems"
        aria-label="Резерв"
        class="w-full lg:w-64"
      />
      <USelect
        v-model="sort"
        :items="sortItems"
        aria-label="Сортировка"
        class="w-full lg:w-52"
      />
    </div>

    <div
      class="flex flex-wrap gap-2"
      role="group"
      aria-label="Группы должностей"
    >
      <UButton
        v-for="item in groupChips"
        :key="item.id"
        :label="item.label"
        :color="group === item.id ? 'primary' : 'neutral'"
        variant="soft"
        :aria-pressed="group === item.id"
        @click="group = item.id"
      />
    </div>

    <div
      v-if="structureTotal"
      class="flex flex-col gap-2"
    >
      <p class="text-xs text-text-muted">
        Структура перечня № 492-нпа по сферам, {{ structureTotal }} должностей
      </p>
      <div
        class="flex h-3 overflow-hidden rounded-full bg-elevated"
        role="img"
        aria-label="Структура перечня по сферам"
      >
        <span
          v-for="item in structure"
          :key="item.id"
          :class="groupDot[item.id]"
          :style="{ width: `${item.count / structureTotal * 100}%` }"
          :title="`${item.name}: ${item.count}`"
        />
      </div>
      <ul class="flex flex-wrap gap-x-4 gap-y-1 text-xs text-text-muted">
        <li
          v-for="item in structure"
          :key="item.id"
          class="flex items-center gap-1.5"
        >
          <span
            class="size-2.5 rounded-full"
            :class="groupDot[item.id]"
            aria-hidden="true"
          />
          {{ item.name }} — {{ item.count }}
        </li>
      </ul>
    </div>

    <div
      class="max-h-[40rem] overflow-y-auto rounded-xl bg-elevated p-2 sm:p-4"
      role="region"
      aria-label="Перечень целевых должностей"
      tabindex="0"
    >
      <table class="block w-full text-left lg:table">
        <caption class="sr-only">
          Перечень целевых должностей
        </caption>
        <thead class="max-lg:sr-only lg:table-header-group">
          <tr class="text-sm font-medium text-text-muted">
            <th
              scope="col"
              class="w-28 px-4 py-3 font-medium"
            >
              Пункт
            </th>
            <th
              scope="col"
              class="px-4 py-3 font-medium"
            >
              Наименование
            </th>
            <th
              scope="col"
              class="w-40 px-4 py-3 font-medium"
            >
              Категория
            </th>
            <th
              scope="col"
              class="w-44 px-4 py-3 font-medium"
            >
              Группа
            </th>
            <th
              scope="col"
              class="w-52 px-4 py-3 font-medium"
            >
              Источник
            </th>
          </tr>
        </thead>
        <tbody class="block lg:table-row-group">
          <tr
            v-for="position in filtered"
            :key="position.id"
            class="block border-t border-default py-3 first:border-t-0 lg:table-row lg:py-0"
          >
            <td class="block px-4 py-1 text-sm text-text-muted lg:table-cell lg:py-3 lg:align-top">
              {{ position.ref }}
            </td>
            <td class="block px-4 py-1 text-base text-text-primary text-pretty lg:table-cell lg:py-3 lg:align-top">
              <template
                v-for="(part, index) in highlight(position.name)"
                :key="index"
              >
                <mark
                  v-if="part.hit"
                  class="rounded-sm bg-primary/20 text-text-primary"
                >{{ part.text }}</mark>
                <template v-else>
                  {{ part.text }}
                </template>
              </template>
              <UBadge
                v-if="position.isGroup"
                label="группа должностей"
                color="info"
                variant="soft"
                class="mt-1 block w-fit"
              />
            </td>
            <td class="block px-4 py-1 text-sm text-text-muted lg:table-cell lg:py-3 lg:align-top">
              {{ position.category }}
            </td>
            <td class="block px-4 py-1 text-sm text-text-muted lg:table-cell lg:py-3 lg:align-top">
              {{ groupName(position.group) }}
            </td>
            <td class="block px-4 py-1 lg:table-cell lg:py-3 lg:align-top">
              <span class="flex items-start gap-1.5 text-sm font-medium text-text-primary">
                <span
                  class="mt-1.5 size-2.5 shrink-0 rounded-full"
                  :class="reserveDot[position.reserve]"
                  aria-hidden="true"
                />
                {{ position.source }}
              </span>
            </td>
          </tr>
          <tr v-if="!filtered.length">
            <td
              colspan="5"
              class="block px-4 py-6 text-center text-base text-text-muted lg:table-cell"
            >
              Ничего не найдено — измените запрос или фильтр.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p class="text-xs text-text-muted text-pretty">
      {{ staffReserveReview.positionsRepealed }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { groupDot, reserveDot, reserveIds, staffReserveReview, findReserve, type ReservePosition } from '~/data/staff-reserve-review'

const { positions, positionGroups } = staffReserveReview

const search = ref('')
const reserve = ref('all')
const sort = ref('ref')
const group = ref('all')

const reserveItems = [
  { label: 'Все резервы', value: 'all' },
  ...reserveIds.map(id => ({ label: findReserve(id).short, value: id }))
]

const sortItems = [
  { label: 'По пункту акта', value: 'ref' },
  { label: 'По наименованию', value: 'name' }
]

const counts = positions.reduce<Record<string, number>>((result, position) => {
  result[position.group] = (result[position.group] ?? 0) + 1
  return result
}, {})

const groupChips = [
  { id: 'all', label: 'Все группы' },
  ...positionGroups.map(item => ({ id: item.id, label: `${item.name} · ${counts[item.id] ?? 0}` }))
]

// Структура перечня учреждений и предприятий по сферам
const structure = positionGroups
  .filter(item => item.reserve === 'institutions')
  .map(item => ({ id: item.id, name: item.name, count: counts[item.id] ?? 0 }))
const structureTotal = structure.reduce((sum, item) => sum + item.count, 0)

const groupOrder = positionGroups.map(item => item.id)

function groupName(id: string): string {
  return positionGroups.find(item => item.id === id)?.name ?? id
}

// «гл. 1, п. 2.1» → 1002 : порядок по номеру пункта акта
function refKey(ref: string): number {
  const match = ref.match(/(\d+)\.(\d+)/)
  return match ? Number(match[1]) * 1000 + Number(match[2]) : 0
}

const query = computed(() => search.value.trim().toLowerCase())

const filtered = computed<ReservePosition[]>(() => {
  const list = positions.filter(position =>
    (group.value === 'all' || position.group === group.value)
    && (reserve.value === 'all' || position.reserve === reserve.value)
    && (!query.value || `${position.name} ${position.ref}`.toLowerCase().includes(query.value))
  )
  return list.toSorted(sort.value === 'name'
    ? (a, b) => a.name.localeCompare(b.name, 'ru')
    : (a, b) => groupOrder.indexOf(a.group) - groupOrder.indexOf(b.group) || refKey(a.ref) - refKey(b.ref))
})

// Подсветка найденного фрагмента в названии
function highlight(text: string): Array<{ text: string, hit: boolean }> {
  if (!query.value) return [{ text, hit: false }]
  const parts: Array<{ text: string, hit: boolean }> = []
  const lower = text.toLowerCase()
  let from = 0
  let at = lower.indexOf(query.value)
  while (at !== -1) {
    if (at > from) parts.push({ text: text.slice(from, at), hit: false })
    parts.push({ text: text.slice(at, at + query.value.length), hit: true })
    from = at + query.value.length
    at = lower.indexOf(query.value, from)
  }
  if (from < text.length) parts.push({ text: text.slice(from), hit: false })
  return parts
}
</script>
