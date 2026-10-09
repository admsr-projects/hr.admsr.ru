<template>
  <div class="flex flex-col gap-6">
    <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
      <UTabs
        v-model="reserveFilter"
        :items="reserveTabs"
        :content="false"
        variant="link"
        aria-label="Выбор резерва"
        class="min-w-0 lg:flex-1"
      >
        <template #leading="{ item }">
          <span
            v-if="item.dot"
            class="size-2.5 shrink-0 rounded-full"
            :class="item.dot"
            aria-hidden="true"
          />
        </template>
      </UTabs>
      <UFormField
        label="Группа должностей"
        class="w-full lg:w-72"
      >
        <USelect
          v-model="group"
          :items="groupItems"
          class="w-full"
        />
      </UFormField>
    </div>

    <p
      v-if="groupNote"
      class="rounded-lg bg-elevated p-4 text-sm text-text-muted text-pretty"
    >
      {{ groupNote }}
      <NuxtLink
        to="#review-positions"
        class="text-primary underline"
      >
        Открыть перечень должностей
      </NuxtLink>
    </p>

    <div class="rounded-xl bg-elevated p-2 sm:p-4">
      <table class="block w-full text-left lg:table">
        <caption class="sr-only">
          Требования к кандидатам
        </caption>
        <thead class="max-lg:sr-only lg:table-header-group">
          <tr>
            <th
              scope="col"
              class="w-56 px-4 py-3 text-sm font-medium text-text-muted"
            >
              Требование
            </th>
            <th
              v-for="reserve in shown"
              :key="reserve.id"
              scope="col"
              class="px-4 py-3 text-left font-normal"
            >
              <ReserveReviewLabel :reserve="reserve.id" />
              <span class="block text-xs text-text-muted">{{ reserve.normative }}</span>
            </th>
          </tr>
        </thead>
        <tbody class="block lg:table-row-group">
          <tr
            v-for="requirement in requirements"
            :key="requirement.key"
            class="block border-t border-default py-3 first:border-t-0 lg:table-row lg:py-0"
          >
            <th
              scope="row"
              class="block px-4 py-1 text-left lg:table-cell lg:w-56 lg:py-3 lg:align-top"
            >
              <span class="flex items-center gap-2 text-base font-semibold text-text-primary">
                <UIcon
                  :name="requirementIcons[requirement.key] ?? 'i-lucide-circle'"
                  class="size-5 shrink-0 text-primary"
                  aria-hidden="true"
                />
                {{ requirement.label }}
              </span>
            </th>
            <td
              v-for="reserve in shown"
              :key="reserve.id"
              class="block px-4 py-1 lg:table-cell lg:py-3 lg:align-top"
            >
              <p class="mb-1 lg:hidden">
                <ReserveReviewLabel :reserve="reserve.id" />
              </p>
              <template v-if="requirement.values[reserve.id]">
                <UBadge
                  :label="requirement.values[reserve.id]!.status === 'cond' ? 'с условием' : 'установлено'"
                  :color="requirement.values[reserve.id]!.status === 'cond' ? 'warning' : 'success'"
                  variant="soft"
                  class="mb-2"
                />
                <p class="text-sm text-text-primary text-pretty">
                  {{ requirement.values[reserve.id]!.text }}
                </p>
                <p class="mt-1 text-xs text-text-muted">
                  <span class="font-semibold">{{ reserve.normative }}</span>, {{ requirement.values[reserve.id]!.ref }}
                </p>
              </template>
              <UBadge
                v-else
                label="не установлено актом"
                color="neutral"
                variant="soft"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="flex flex-col gap-4">
      <h3 class="text-lg font-medium text-text-primary">
        Ограничения — наглядно
      </h3>
      <ul class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <li
          v-for="limit in limits"
          :key="limit.key"
          class="flex flex-col gap-3 rounded-xl bg-elevated p-6"
        >
          <h4 class="flex items-center gap-2 text-base font-semibold text-text-primary">
            <UIcon
              :name="requirementIcons[limit.key] ?? 'i-lucide-circle'"
              class="size-5 shrink-0 text-primary"
              aria-hidden="true"
            />
            {{ limit.label }}
          </h4>

          <template v-if="limit.key === 'age'">
            <div
              v-for="reserve in shown"
              :key="reserve.id"
              class="flex flex-col gap-1.5"
            >
              <ReserveReviewLabel :reserve="reserve.id" />
              <template v-if="limit.values[reserve.id]?.min != null">
                <div
                  class="relative h-6 rounded-lg bg-default"
                  role="img"
                  :aria-label="`Возраст от ${limit.values[reserve.id]!.min} до ${limit.values[reserve.id]!.max} лет`"
                >
                  <span
                    class="absolute inset-y-0 rounded-lg"
                    :class="reserveDot[reserve.id]"
                    :style="ageBar(limit.values[reserve.id]!)"
                  />
                </div>
                <div
                  class="relative h-4 text-xs text-text-muted"
                  aria-hidden="true"
                >
                  <span
                    class="absolute -translate-x-1/2"
                    :style="{ left: `${position(limit.values[reserve.id]!.min!)}%` }"
                  >{{ limit.values[reserve.id]!.min }}</span>
                  <span
                    class="absolute -translate-x-1/2"
                    :style="{ left: `${position(limit.values[reserve.id]!.max!)}%` }"
                  >{{ limit.values[reserve.id]!.max }}</span>
                </div>
              </template>
              <p
                v-else
                class="text-sm text-text-muted"
              >
                не установлен
              </p>
            </div>
          </template>

          <ul
            v-else
            class="flex flex-col gap-3"
          >
            <li
              v-for="reserve in shown"
              :key="reserve.id"
              class="flex flex-col gap-0.5 text-sm"
            >
              <ReserveReviewLabel :reserve="reserve.id" />
              <span
                v-if="limit.values[reserve.id]"
                class="font-semibold text-text-primary"
              >
                {{ limit.values[reserve.id]!.status === 'cond' ? 'с условием' : 'требование установлено' }}
              </span>
              <span
                v-else
                class="text-text-muted"
              >не установлено актом</span>
            </li>
          </ul>
        </li>
      </ul>
    </div>

    <div class="flex flex-col gap-4">
      <h3 class="text-lg font-medium text-text-primary">
        Документы для участия
      </h3>
      <ul
        :key="shown.map(reserve => reserve.id).join()"
        class="grid grid-cols-1 items-start gap-4 lg:grid-cols-3"
      >
        <li
          v-for="reserve in shown"
          :key="reserve.id"
        >
          <details
            v-if="documents[reserve.id]"
            class="group rounded-xl bg-elevated"
            :open="shown.length === 1"
          >
            <summary class="flex cursor-pointer list-none items-center justify-between gap-3 rounded-xl px-6 py-4">
              <span class="flex flex-col gap-0.5">
                <ReserveReviewLabel :reserve="reserve.id" />
                <span class="text-sm text-text-muted">{{ documents[reserve.id]!.items.length }} документов</span>
              </span>
              <UIcon
                name="i-lucide-chevron-down"
                class="size-5 shrink-0 text-text-muted transition-transform duration-200 group-open:rotate-180 motion-reduce:transition-none"
                aria-hidden="true"
              />
            </summary>
            <div class="flex flex-col gap-3 px-6 pb-6">
              <ol class="flex list-decimal flex-col gap-2 pl-5">
                <li
                  v-for="item in documents[reserve.id]!.items"
                  :key="item"
                  class="text-sm text-text-primary text-pretty"
                >
                  {{ item }}
                </li>
              </ol>
              <p
                v-if="documents[reserve.id]!.note"
                class="rounded-lg bg-default p-3 text-sm text-text-muted text-pretty"
              >
                {{ documents[reserve.id]!.note }}
              </p>
              <p class="text-xs text-text-muted">
                <span class="font-semibold">{{ reserve.normative }}</span>, {{ documents[reserve.id]!.ref }}
              </p>
            </div>
          </details>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  findReserve,
  reserveDot,
  reserveIds,
  staffReserveReview,
  type ReserveId,
  type RequirementValue
} from '~/data/staff-reserve-review'

const { requirements, documents, positionGroups, positions } = staffReserveReview

const requirementIcons: Record<string, string> = {
  citizenship: 'i-lucide-id-card',
  age: 'i-lucide-clock',
  criminal: 'i-lucide-scale',
  capacity: 'i-lucide-gavel',
  health: 'i-lucide-heart-pulse',
  disqual: 'i-lucide-ban',
  qualification: 'i-lucide-graduation-cap',
  submission: 'i-lucide-file-text'
}

const reserveFilter = ref('all')
const group = ref('all')

const reserveTabs = [
  { label: 'Все резервы', value: 'all' },
  ...reserveIds.map(id => ({ label: findReserve(id).short, value: id, dot: reserveDot[id] }))
]

const groupItems = computed(() => [
  { label: 'Все группы', value: 'all' },
  ...positionGroups
    .filter(item => reserveFilter.value === 'all' || item.reserve === reserveFilter.value)
    .map(item => ({ label: item.name, value: item.id }))
])

// Выбрали другой резерв — группа из прежнего выбора может ему не принадлежать
watch(reserveFilter, () => {
  group.value = 'all'
})

const selectedGroup = computed(() => positionGroups.find(item => item.id === group.value))

const shown = computed(() => {
  const ids: ReserveId[] = selectedGroup.value
    ? [selectedGroup.value.reserve]
    : reserveFilter.value === 'all' ? reserveIds : [reserveFilter.value as ReserveId]
  return ids.map(findReserve)
})

const groupNote = computed(() => {
  const item = selectedGroup.value
  if (!item) return ''
  const reserve = findReserve(item.reserve)
  const count = positions.filter(position => position.group === item.id).length
  return `Группа «${item.name}» относится к резерву «${reserve.short}» (${reserve.normative}); позиций в перечне: ${count}.`
})

const limits = ['age', 'citizenship', 'criminal', 'health']
  .map(key => requirements.find(requirement => requirement.key === key))
  .filter(requirement => !!requirement)

// Шкала возраста на диаграмме: от 0 до 85 лет
const AGE_SCALE = 85

function position(years: number): number {
  return Number(((years / AGE_SCALE) * 100).toFixed(1))
}

function ageBar(value: RequirementValue) {
  return {
    left: `${position(value.min!)}%`,
    width: `${position(value.max! - value.min!)}%`
  }
}
</script>
