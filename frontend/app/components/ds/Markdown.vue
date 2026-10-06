<template>
  <!-- eslint-disable-next-line vue/no-v-html -- HTML собирает renderMarkdown: сырой HTML экранируется, ссылки проверяются -->
  <div
    class="ds-markdown"
    v-html="html"
  />
</template>

<script setup lang="ts">
const props = defineProps<{
  source?: string | null
}>()

const html = computed(() => renderMarkdown(props.source))
</script>
