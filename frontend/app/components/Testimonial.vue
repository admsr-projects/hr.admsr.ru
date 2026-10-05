<template>
  <figure class="grid grid-cols-1 overflow-hidden rounded-xl bg-elevated sm:grid-cols-[240px_1fr] lg:grid-cols-[320px_1fr]">
    <div class="relative aspect-[4/3] w-full sm:aspect-auto sm:min-h-full">
      <img
        :src="image"
        :alt="alt"
        class="absolute inset-0 size-full object-cover object-top"
        loading="lazy"
      >
    </div>

    <div class="flex min-w-0 flex-col justify-center gap-6 p-6 lg:p-8">
      <UIcon
        name="i-lucide-quote"
        class="size-6 text-primary"
        aria-hidden="true"
      />

      <blockquote class="text-h3 font-normal text-text-primary text-pretty">
        «{{ quote }}»
      </blockquote>

      <figcaption class="flex flex-col gap-1">
        <span class="text-base font-semibold text-text-primary">
          {{ author }}
        </span>
        <span
          v-if="role"
          class="text-caption text-text-muted"
        >
          {{ role }}
        </span>
      </figcaption>
    </div>
  </figure>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  image: string
  quote: string
  author: string
  role?: string
  alt?: string
}>(), {
  role: undefined,
  alt: 'Фото руководителя',
})
</script>
