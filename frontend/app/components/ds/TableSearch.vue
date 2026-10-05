<template>
  <UInput
    v-model="model"
    type="search"
    icon="i-lucide-search"
    :placeholder="placeholder"
    :aria-label="placeholder"
    class="w-full"
  >
    <template
      v-if="model"
      #trailing
    >
      <UButton
        icon="i-lucide-x"
        color="neutral"
        variant="link"
        size="sm"
        aria-label="Очистить поиск"
        class="cursor-pointer"
        @click="model = ''"
      />
    </template>
  </UInput>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  placeholder?: string
}>(), {
  placeholder: 'Поиск по названию',
})

const model = defineModel<string>({ default: '' })
</script>
