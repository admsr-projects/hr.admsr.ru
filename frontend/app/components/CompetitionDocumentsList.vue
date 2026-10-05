<template>
  <section
    v-if="documents.length"
    :aria-labelledby="headingId"
    class="rounded-xl bg-elevated"
  >
    <header class="px-6 py-4">
      <h3
        :id="headingId"
        class="text-lg font-medium text-text-primary"
      >
        {{ title }}
      </h3>
    </header>
    <ul class="flex flex-col gap-2 px-6 pb-6">
      <li
        v-for="entry in documents"
        :key="entry.id"
        class="flex flex-wrap items-center justify-between gap-3 rounded-lg bg-elevated p-4"
      >
        <span class="flex min-w-0 items-center gap-2 text-base text-text-primary">
          <UIcon
            name="i-lucide-file-text"
            class="size-5 shrink-0 text-text-muted"
            aria-hidden="true"
          />
          <span class="text-pretty">{{ entry.name }}</span>
        </span>
        <UButton
          v-if="entry.link"
          label="Скачать"
          icon="i-lucide-download"
          :to="entry.link"
          target="_blank"
          external
          color="neutral"
          variant="soft"
          class="cursor-pointer shrink-0"
          :aria-label="`Скачать: ${entry.name}`"
        />
      </li>
    </ul>
  </section>
</template>

<script setup lang="ts">
interface CompetitionDocumentItem {
  id: number
  name: string
  link?: string | null
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
