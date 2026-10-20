<template>
  <article class="flex flex-col gap-4 rounded-xl bg-elevated p-6">
    <header class="flex items-center gap-3">
      <span class="flex size-10 shrink-0 items-center justify-center rounded-full bg-default text-primary">
        <UIcon
          :name="icon"
          class="size-5"
          aria-hidden="true"
        />
      </span>
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
