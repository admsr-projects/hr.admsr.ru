<template>
  <div>
    <ul
      v-if="pending"
      class="grid gap-4 sm:grid-cols-2"
      aria-busy="true"
      aria-label="Загрузка лауреатов"
    >
      <li
        v-for="index in 4"
        :key="index"
        class="overflow-hidden rounded-xl bg-elevated"
      >
        <USkeleton class="aspect-[4/3] w-full rounded-none" />
        <div class="space-y-3 p-6">
          <USkeleton class="h-6 w-40" />
          <USkeleton class="h-6 w-2/3" />
          <USkeleton class="h-4 w-1/2" />
        </div>
      </li>
    </ul>

    <ul
      v-else-if="items.length"
      class="grid gap-4 sm:grid-cols-2"
    >
      <li
        v-for="(item, index) in items"
        :key="`${item.surname}-${item.name}-${index}`"
      >
        <HonorBoardMemberCard :member="item" />
      </li>
    </ul>

    <DsEmptyState
      v-else
      icon="i-lucide-award"
      title="Пока нет записей"
      description="Информация о сотрудниках, отмеченных на доске почёта, появится позже."
    >
      <template #action>
        <UButton
          label="Вакансии администрации"
          to="/vacancies"
          color="primary"
          variant="soft"
          trailing-icon="i-lucide-arrow-right"
          class="cursor-pointer"
        />
      </template>
    </DsEmptyState>
  </div>
</template>

<script setup lang="ts">
import type { HonorBoardMember } from '~/components/HonorBoardMemberCard.vue'

withDefaults(defineProps<{
  items: HonorBoardMember[]
  pending?: boolean
}>(), {
  pending: false,
})
</script>
