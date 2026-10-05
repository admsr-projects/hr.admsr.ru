<template>
  <div>
    <div
      v-if="pending"
      class="flex flex-col gap-3 rounded-xl bg-elevated p-6"
      aria-busy="true"
      aria-label="Загрузка документов о конкурсах"
    >
      <USkeleton
        v-for="index in 3"
        :key="index"
        class="h-10 w-full"
      />
    </div>

    <DsEmptyState
      v-else-if="!rules.length"
      icon="i-lucide-file-x"
      title="Документы отсутствуют"
      description="Опубликованные документы появятся здесь после размещения в административной панели."
    />

    <DsDocumentsTable
      v-else
      :documents="rules"
      caption="Документы о проведении конкурсов"
      pagination-label="Страницы списка документов о конкурсах"
    />
  </div>
</template>

<script setup lang="ts">
export interface CompetitionRuleItem {
  id: number
  name: string
  link?: string | null
  created_at?: string | null
}

const config = useRuntimeConfig()

const { data: rulesData, pending } = await useAsyncData(
  'competition-rules',
  () => $fetch<CompetitionRuleItem[]>(`${config.public.apiBaseUrl}/api/tenders/`),
  { server: false },
)

const rules = computed(() => rulesData.value ?? [])
</script>
