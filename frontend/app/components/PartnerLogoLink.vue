<template>
  <NuxtLink
    :to="logo.url"
    target="_blank"
    rel="noopener noreferrer"
    class="group flex flex-col items-center gap-4 rounded-xl bg-default p-5 text-center transition-colors duration-200 hover:bg-accented motion-reduce:transition-none"
    :class="$attrs.class"
  >
    <div class="flex h-14 w-full items-center justify-center">
      <img
        :src="logo.image"
        alt=""
        width="56"
        height="56"
        loading="lazy"
        class="max-h-12 max-w-full object-contain"
      >
    </div>

    <span class="text-caption font-medium text-text-primary text-balance">
      {{ logo.name }}
      <span class="sr-only"> (откроется в новой вкладке)</span>
    </span>
  </NuxtLink>
</template>

<script setup lang="ts">
defineProps<{
  logo: {
    url: string
    image: string
    name: string
  }
}>()

defineOptions({ inheritAttrs: false })
</script>
