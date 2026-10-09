<template>
  <div class="rounded-xl bg-elevated p-2 sm:p-4">
    <table class="block w-full text-left sm:table">
      <caption class="sr-only">
        Нормативная база
      </caption>
      <thead class="max-sm:sr-only sm:table-header-group">
        <tr class="text-caption font-medium text-text-muted">
          <th
            scope="col"
            class="px-4 py-3 font-medium"
          >
            Название документа
          </th>
          <th
            scope="col"
            class="px-4 py-3 font-medium"
          >
            О чём
          </th>
        </tr>
      </thead>
      <tbody class="block sm:table-row-group">
        <tr
          v-for="source in sources"
          :key="source.id"
          class="block border-t border-default py-3 first:border-t-0 sm:table-row sm:py-0"
        >
          <td class="block px-4 py-1 text-base text-text-primary text-pretty sm:table-cell sm:w-1/2 sm:py-3 sm:align-top">
            {{ source.title }}
          </td>
          <td class="block px-4 py-1 text-sm text-text-muted text-pretty sm:table-cell sm:py-3 sm:align-top">
            {{ source.about }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { staffReserveReview } from '~/data/staff-reserve-review'

const sources = staffReserveReview.sources
</script>
