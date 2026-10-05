<template>
  <div>
    <div
      v-if="pending"
      class="flex flex-col gap-3 rounded-xl bg-elevated p-6"
      aria-busy="true"
      aria-label="Загрузка документов раздела вакансий"
    >
      <USkeleton
        v-for="index in 3"
        :key="index"
        class="h-10 w-full"
      />
    </div>

    <DsEmptyState
      v-else-if="!documents.length"
      icon="i-lucide-file-x"
      title="Документы отсутствуют"
      description="Опубликованные документы появятся здесь после размещения в административной панели."
    />

    <DsDocumentsTable
      v-else
      :documents="documents"
      caption="Документы о вакансиях"
      pagination-label="Страницы списка документов о вакансиях"
    />
  </div>
</template>

<script setup lang="ts">
export interface VacancyDocumentItem {
  id: number
  name: string
  link?: string | null
  created_at?: string | null
}

const config = useRuntimeConfig()

const { data: documentsData, pending } = await useAsyncData(
  'vacancy-documents',
  () => $fetch<VacancyDocumentItem[]>(`${config.public.apiBaseUrl}/api/vacancy-documents/`),
  { server: false },
)

const documents = computed(() => documentsData.value ?? [])
</script>
