<template>
  <th
    scope="col"
    :aria-sort="sort"
    class="px-4 py-3 font-medium"
  >
    <button
      type="button"
      class="-mx-2 inline-flex cursor-pointer items-center gap-1 rounded-md px-2 py-1 transition-colors duration-200 hover:bg-accented hover:text-text-primary focus-visible:outline-2 focus-visible:outline-primary motion-reduce:transition-none"
      :class="sort === 'none' ? 'text-text-muted' : 'text-text-primary'"
      @click="emit('sort')"
    >
      {{ label }}
      <UIcon
        :name="icon"
        class="size-4 shrink-0"
        aria-hidden="true"
      />
    </button>
  </th>
</template>

<script setup lang="ts">
const props = defineProps<{
  label: string
  sort: 'ascending' | 'descending' | 'none'
}>()

const emit = defineEmits<{ sort: [] }>()

const icon = computed(() => {
  if (props.sort === 'ascending') return 'i-lucide-arrow-up'
  if (props.sort === 'descending') return 'i-lucide-arrow-down'
  return 'i-lucide-arrow-up-down'
})
</script>
