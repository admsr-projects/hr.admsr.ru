<template>
  <span class="inline-flex items-center gap-2 text-sm font-semibold text-text-primary">
    <span
      class="size-2.5 shrink-0 rounded-full"
      :class="reserveDot[reserve]"
      aria-hidden="true"
    />
    {{ findReserve(reserve).short }}
  </span>
</template>

<script setup lang="ts">
import { findReserve, reserveDot, type ReserveId } from '~/data/staff-reserve-review'

defineProps<{
  reserve: ReserveId
}>()
</script>
