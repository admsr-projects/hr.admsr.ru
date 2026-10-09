<template>
  <div class="flex flex-col gap-4">
    <ul class="grid grid-cols-1 gap-4 lg:grid-cols-3">
      <li
        v-for="level in levels"
        :key="level.id"
        class="flex flex-col gap-4 rounded-xl bg-elevated p-6"
      >
        <h3 class="text-lg font-medium text-text-primary">
          {{ level.name }}
        </h3>
        <p class="text-sm text-text-muted text-pretty">
          {{ level.criterion }}
        </p>
        <ul class="mt-auto flex flex-col gap-2 border-t border-default pt-4">
          <li
            v-for="activity in activities"
            :key="activity.key"
            class="flex items-start gap-2 text-sm"
            :class="level.activities[activity.key] ? 'text-text-primary' : 'text-text-muted'"
          >
            <UIcon
              :name="level.activities[activity.key] ? 'i-lucide-check' : 'i-lucide-minus'"
              class="mt-0.5 size-4 shrink-0"
              :class="level.activities[activity.key] ? 'text-primary' : undefined"
              aria-hidden="true"
            />
            <span>
              {{ activity.label }}
              <span class="sr-only">{{ level.activities[activity.key] ? ': требуется' : ': не требуется' }}</span>
            </span>
          </li>
        </ul>
      </li>
    </ul>

    <div class="flex flex-col gap-3 rounded-xl bg-elevated p-6">
      <p class="flex items-start gap-2 text-sm text-text-muted text-pretty">
        <UIcon
          name="i-lucide-info"
          class="mt-0.5 size-4 shrink-0"
          aria-hidden="true"
        />
        {{ levelsNote }}
      </p>
      <dl class="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <div
          v-for="id in reserveIds"
          :key="id"
          class="flex flex-col gap-1 rounded-lg bg-default p-4"
        >
          <dt>
            <ReserveReviewLabel :reserve="id" />
          </dt>
          <dd class="text-xs text-text-muted">
            {{ levelsRefs[id] }}
          </dd>
        </div>
      </dl>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reserveIds, staffReserveReview } from '~/data/staff-reserve-review'

const { levels, levelsNote, levelsRefs } = staffReserveReview

const activities = [
  { key: 'dpo', label: 'Дополнительное профессиональное образование' },
  { key: 'internship', label: 'Стажировка в профильных структурах' },
  { key: 'testing', label: 'Тестирование на готовность к назначению' }
] as const
</script>
