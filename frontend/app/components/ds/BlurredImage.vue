<template>
  <div
    class="relative w-full overflow-hidden bg-elevated"
    :class="ratioClass"
  >
    <template v-if="src">
      <!-- Размытая копия заполняет свободные поля, чтобы любое фото смотрелось в одном размере -->
      <img
        :src="src"
        alt=""
        aria-hidden="true"
        class="absolute inset-0 size-full scale-110 object-cover blur-2xl"
        :loading="loading"
      >
      <div
        class="absolute inset-0 bg-black/10"
        aria-hidden="true"
      />
      <img
        :src="src"
        :alt="alt"
        class="relative size-full object-contain"
        :loading="loading"
      >
    </template>
    <div
      v-else
      class="flex size-full items-center justify-center text-text-muted"
    >
      <UIcon
        name="i-lucide-newspaper"
        class="size-10"
        aria-hidden="true"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  src?: string | null
  alt?: string
  ratioClass?: string
  loading?: 'lazy' | 'eager'
}>(), {
  src: undefined,
  alt: '',
  ratioClass: 'aspect-video',
  loading: 'lazy'
})
</script>
