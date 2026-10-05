<template>
  <NuxtLink
    :to="to"
    class="group flex h-full flex-col gap-3 rounded-xl border border-default bg-surface-raised p-6 transition-colors duration-200 hover:border-primary focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary motion-reduce:transition-none"
  >
    <div class="flex items-start justify-between gap-3">
      <UIcon
        :name="icon"
        class="size-6 shrink-0 text-primary"
        aria-hidden="true"
      />
      <span class="flex items-center gap-1 text-sm font-medium text-text-muted transition-colors duration-200 group-hover:text-text-primary">
        Перейти в раздел
        <UIcon
          name="i-lucide-arrow-up-right"
          class="size-4"
          aria-hidden="true"
        />
      </span>
    </div>
    <div class="flex flex-col gap-1">
      <h3 class="text-lg font-semibold leading-snug text-text-primary">
        {{ title }}
      </h3>
      <p
        v-if="description"
        class="text-sm leading-5 text-text-muted text-pretty"
      >
        {{ description }}
      </p>
    </div>
  </NuxtLink>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  description?: string
  icon: string
  to: string
}>()
</script>
