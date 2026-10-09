<template>
  <div class="grid grid-cols-1 gap-4 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
    <section
      class="flex flex-col gap-6 rounded-xl bg-elevated p-6"
      aria-labelledby="review-term-title"
    >
      <div class="flex flex-col gap-1">
        <h2
          id="review-term-title"
          class="text-lg font-medium text-text-primary"
        >
          Срок нахождения в резерве
        </h2>
        <p class="text-sm text-text-muted text-pretty">
          Основной срок и однократное продление, лет. По № 492-нпа — «не более» указанных значений
        </p>
      </div>

      <div class="relative flex flex-col gap-4">
        <div
          class="pointer-events-none absolute inset-x-0 top-0 bottom-7 grid grid-cols-5"
          aria-hidden="true"
        >
          <span
            v-for="year in YEARS"
            :key="year"
            class="border-l border-default last:border-r"
          />
        </div>

        <div
          v-for="reserve in reserves"
          :key="reserve.id"
          class="relative flex flex-col gap-1.5"
        >
          <ReserveReviewLabel :reserve="reserve.id" />
          <div
            class="grid h-9 grid-cols-5"
            role="img"
            :aria-label="`${reserve.short}: ${reserve.term}, продление ${reserve.extension}`"
          >
            <div
              class="relative flex items-center justify-end overflow-hidden rounded-lg bg-default pr-3 text-sm font-semibold text-text-primary"
              :style="{ gridColumn: `span ${reserve.termYears}` }"
            >
              <span
                class="absolute inset-y-0 left-0 w-1.5"
                :class="reserveDot[reserve.id]"
              />
              {{ years(reserve.termYears) }}
            </div>
            <div
              class="ml-1 flex items-center justify-center rounded-lg bg-accented text-sm text-text-muted"
              :style="{ gridColumn: `span ${reserve.extensionYears}` }"
            >
              +{{ years(reserve.extensionYears) }}
            </div>
          </div>
        </div>

        <div
          class="relative flex justify-between pt-1 text-xs text-text-muted"
          aria-hidden="true"
        >
          <span
            v-for="year in AXIS"
            :key="year"
          >{{ year }}</span>
        </div>
      </div>
    </section>

    <ul class="grid grid-cols-1 gap-4 sm:grid-cols-3 lg:grid-cols-1">
      <li
        v-for="stat in stats"
        :key="stat.caption"
        class="flex flex-col justify-center gap-1 rounded-xl bg-elevated p-6"
      >
        <span class="text-h2 text-primary">{{ stat.value }}</span>
        <span class="text-sm text-text-muted text-pretty">{{ stat.caption }}</span>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { reserveDot, staffReserveReview } from '~/data/staff-reserve-review'

const reserves = staffReserveReview.reserves

const YEARS = [1, 2, 3, 4, 5]
const AXIS = [0, 1, 2, 3, 4, 5]

function years(count: number): string {
  if (count === 1) return '1 год'
  return `${count} ${count < 5 ? 'года' : 'лет'}`
}

const stats = [
  { value: reserves.length, caption: 'резерва' },
  { value: Math.max(...reserves.map(reserve => reserve.maxCandidates)), caption: 'кандидата — предел на одну должность' },
  { value: staffReserveReview.positions.filter(position => !position.isGroup).length, caption: 'целевых должностей учреждений и предприятий' }
]
</script>
