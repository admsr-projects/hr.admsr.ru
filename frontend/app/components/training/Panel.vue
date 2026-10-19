<template>
  <article class="flex flex-col gap-4 rounded-xl bg-elevated p-6">
    <header class="flex items-center gap-3">
      <UIcon
        :name="icon"
        class="size-6 shrink-0 text-primary"
        aria-hidden="true"
      />
      <h3 class="text-h3 text-text-primary">
        {{ title }}
      </h3>
    </header>
    <slot />
  </article>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  icon: string
}>()
</script>
