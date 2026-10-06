<template>
  <DsEmptyState
    v-if="!edu.filtered.value.length"
    icon="i-lucide-search-x"
    title="Ничего не найдено"
    description="Под выбранные условия не подходит ни одна позиция. Ослабьте фильтры или сбросьте их."
  >
    <template #action>
      <UButton
        color="neutral"
        variant="soft"
        @click="edu.resetFilters()"
      >
        Сбросить фильтры
      </UButton>
    </template>
  </DsEmptyState>

  <ul
    v-else
    class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
  >
    <li
      v-for="position in edu.filtered.value"
      :key="position.id"
    >
      <article class="relative flex h-full flex-col gap-3 rounded-xl bg-elevated p-6 transition-colors duration-150 hover:bg-accented motion-reduce:transition-none">
        <div class="flex items-start justify-between gap-3">
          <EducationDiamond
            :id="position.id"
            :color="edu.categoryById.value.get(position.category)?.color ?? ''"
            size="size-12"
          />
          <UBadge
            color="neutral"
            variant="soft"
            :title="edu.categoryById.value.get(position.category)?.name"
          >
            <span
              class="size-2 shrink-0 rounded-full"
              :class="categoryColor(edu.categoryById.value.get(position.category)?.color ?? '').dot"
              aria-hidden="true"
            />
            {{ edu.categoryById.value.get(position.category)?.short_name }}
          </UBadge>
        </div>

        <h3 class="text-base font-semibold text-text-primary text-pretty">
          {{ position.title }}
        </h3>

        <div
          v-if="position.subjects.length"
          class="flex flex-wrap gap-1.5"
        >
          <UBadge
            v-for="subject in position.subjects.slice(0, 3)"
            :key="subject"
            color="neutral"
            variant="soft"
          >
            {{ subject }}
          </UBadge>
          <UBadge
            v-if="position.subjects.length > 3"
            color="neutral"
            variant="soft"
          >
            +{{ position.subjects.length - 3 }}
          </UBadge>
        </div>

        <div
          v-if="position.municipal || position.norm_changed"
          class="flex flex-wrap gap-1.5"
        >
          <UBadge
            v-if="position.municipal"
            color="success"
            variant="soft"
          >
            Муниципальный уровень
          </UBadge>
          <UBadge
            v-if="position.norm_changed"
            color="warning"
            variant="soft"
          >
            Норма изменена
          </UBadge>
        </div>

        <div class="mt-auto flex items-center justify-between gap-3 pt-2">
          <span class="flex items-center gap-2 text-caption font-medium text-text-primary">
            <span
              class="size-2 shrink-0 rounded-full"
              :class="position.outcome ? outcomeStyle(position.outcome).dot : 'bg-neutral-400'"
              aria-hidden="true"
            />
            {{ position.outcome ? position.outcome_label : OUTCOME_NONE_LABEL }}
          </span>
          <button
            type="button"
            class="inline-flex items-center gap-1 text-caption font-medium text-primary after:absolute after:inset-0 after:rounded-xl"
            :aria-label="`Подробнее о позиции ${position.id}`"
            @click="edu.openPosition(position.id)"
          >
            Подробнее
            <UIcon
              name="i-lucide-arrow-right"
              class="size-4"
              aria-hidden="true"
            />
          </button>
        </div>
      </article>
    </li>
  </ul>
</template>

<script setup lang="ts">
import { OUTCOME_NONE_LABEL, categoryColor, outcomeStyle } from '~/utils/education'

const edu = useEducationReview()
</script>
