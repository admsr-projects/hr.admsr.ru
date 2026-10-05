<template>
  <div>
    <div
      v-if="pending"
      class="flex flex-col gap-3 rounded-xl bg-elevated p-6"
      aria-busy="true"
      aria-label="Загрузка документов"
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
      description="В этой категории пока нет опубликованных материалов"
    />

    <DsDocumentsTable
      v-else
      :documents="tableItems"
      caption="Антикоррупционные документы"
      pagination-label="Страницы списка антикоррупционных документов"
    />
  </div>
</template>

<script setup lang="ts">
export interface AntiCorruptionDocument {
  id: number
  category: string
  name: string
  file?: string | null
  created_at?: string
}

const props = withDefaults(defineProps<{
  documents: AntiCorruptionDocument[]
  pending?: boolean
}>(), {
  pending: false,
})

const tableItems = computed(() =>
  props.documents.map(doc => ({
    id: doc.id,
    name: doc.name,
    link: doc.file,
    created_at: doc.created_at,
  })),
)
</script>
