<template>
  <button
    type="button"
    class="group inline-flex rounded-lg transition-opacity duration-150 motion-reduce:transition-none"
    :class="dim ? 'opacity-40' : undefined"
    :title="position?.title"
    :aria-label="`Открыть позицию ${id}${position ? `: ${position.title}` : ''}`"
    @click="edu.openPosition(id)"
  >
    <EducationDiamond
      :id="id"
      :color="categoryKey"
      hover-class="group-hover:fill-[var(--ui-bg-accented)]"
    />
  </button>
</template>

<script setup lang="ts">
const props = defineProps<{
  id: number
  /** Приглушить, если позиции нет в текущей выборке */
  dim?: boolean
}>()

const edu = useEducationReview()

const position = computed(() => edu.positionById.value.get(props.id))
const categoryKey = computed(() => edu.categoryById.value.get(position.value?.category ?? -1)?.color ?? '')
</script>
