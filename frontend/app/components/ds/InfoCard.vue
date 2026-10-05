<template>
  <UCard
    variant="soft"
    :ui="{
      root: 'h-full',
      body: 'flex flex-col gap-2 p-6 sm:p-6',
    }"
  >
    <UIcon
      :name="icon"
      class="size-6 shrink-0 text-primary"
      aria-hidden="true"
    />
    <div class="flex flex-col gap-1">
      <h3 class="text-base font-semibold text-text-primary">
        {{ title }}
      </h3>
      <div class="text-sm text-text-muted">
        <slot />
      </div>
    </div>
  </UCard>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  title: string
  icon?: string
}>(), {
  icon: 'i-lucide-info',
})
</script>
