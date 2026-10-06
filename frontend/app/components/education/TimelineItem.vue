<template>
  <button
    :id="`tl-${position.id}`"
    type="button"
    class="flex w-full items-start gap-3 rounded-lg bg-default p-3 text-left transition-colors duration-150 hover:bg-accented motion-reduce:transition-none"
    :class="edu.pulseId.value === position.id ? 'ring-2 ring-primary' : undefined"
    @click="edu.openPosition(position.id)"
  >
    <EducationDiamond
      :id="position.id"
      :color="edu.categoryById.value.get(position.category)?.color ?? ''"
      on-default
    />
    <span class="flex min-w-0 flex-col gap-1">
      <span class="text-caption font-medium text-text-primary text-pretty">{{ position.title }}</span>
      <span class="text-overline text-text-muted">
        {{ position.years ? `Период в фабуле: ${position.years}` : 'Даты в фабуле не указаны' }}
      </span>
    </span>
  </button>
</template>

<script setup lang="ts">
import type { EducationPosition } from '~/utils/education'

defineProps<{
  position: EducationPosition
}>()

const edu = useEducationReview()
</script>
