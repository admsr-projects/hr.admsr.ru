<template>
  <section
    v-if="documents.length"
    :aria-labelledby="headingId"
  >
    <h3
      :id="headingId"
      class="mb-3 text-h3 text-text-primary"
    >
      {{ title }}
    </h3>
    <DsDocumentsTable
      :documents="documents"
      :caption="title"
      pagination-label="Страницы списка нормативных документов о конкурсах"
    />
  </section>
</template>

<script setup lang="ts">
interface CompetitionDocumentItem {
  id: number
  name: string
  link?: string | null
  created_at?: string | null
}

const props = withDefaults(defineProps<{
  type: 'vacancy' | 'reserve'
  title?: string
}>(), {
  title: 'Нормативные документы',
})

const config = useRuntimeConfig()
const headingId = `competition-docs-${props.type}`

const { data } = await useAsyncData(
  `competition-documents-${props.type}`,
  () => $fetch<CompetitionDocumentItem[]>(
    `${config.public.apiBaseUrl}/api/competition-documents/`,
    { query: { type: props.type } },
  ),
  { server: false },
)

const documents = computed(() => data.value ?? [])
</script>
