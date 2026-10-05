<template>
  <div class="flex flex-col gap-4">
    <DsTableSearch v-model="search" />

    <div class="rounded-xl bg-elevated p-2 sm:p-4">
      <table class="block w-full text-left sm:table">
        <caption class="sr-only">
          {{ caption }}
        </caption>
        <thead class="max-sm:sr-only sm:table-header-group">
          <tr class="text-caption font-medium text-text-muted">
            <DsSortableTh
              label="Опубликован"
              class="w-36"
              :sort="ariaSort('date')"
              @sort="toggleSort('date')"
            />
            <DsSortableTh
              label="Название документа"
              :sort="ariaSort('name')"
              @sort="toggleSort('name')"
            />
            <th
              scope="col"
              class="w-40 px-4 py-3 font-medium"
            >
              Файл
            </th>
          </tr>
        </thead>
        <tbody class="block sm:table-row-group">
          <tr
            v-for="entry in pageItems"
            :key="entry.id"
            class="block border-t border-default py-3 first:border-t-0 sm:table-row sm:py-0"
          >
            <td class="block px-4 py-1 text-caption text-text-muted sm:table-cell sm:w-36 sm:whitespace-nowrap sm:py-3 sm:align-middle">
              <time
                v-if="entry.created_at"
                :datetime="entry.created_at"
              >
                {{ formatDate(entry.created_at) }}
              </time>
            </td>
            <td class="block px-4 py-1 text-base text-text-primary text-pretty sm:table-cell sm:py-3 sm:align-middle">
              {{ entry.name }}
            </td>
            <td class="block px-4 py-1 sm:table-cell sm:w-40 sm:py-3 sm:align-middle">
              <UButton
                v-if="entry.link"
                label="Скачать"
                icon="i-lucide-download"
                :to="entry.link"
                target="_blank"
                external
                color="neutral"
                variant="soft"
                class="cursor-pointer"
                :aria-label="`Скачать: ${entry.name}`"
              />
            </td>
          </tr>
          <tr v-if="!pageItems.length">
            <td
              colspan="3"
              class="block px-4 py-6 text-center text-base text-text-muted sm:table-cell"
            >
              Ничего не найдено
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <DsTableFooter
      v-model:page="currentPage"
      v-model:page-size="pageSize"
      :total="total"
      :total-all="documents.length"
      :pagination-label="paginationLabel"
    />
  </div>
</template>

<script setup lang="ts">
export interface DocumentsTableItem {
  id: number | string
  name: string
  link?: string | null
  created_at?: string | null
}

const props = defineProps<{
  documents: DocumentsTableItem[]
  caption: string
  paginationLabel: string
}>()

const documentsRef = toRef(props, 'documents')

const { search, pageSize, currentPage, total, pageItems, toggleSort, ariaSort } = useTableView(documentsRef, {
  sort: {
    date: entry => (entry.created_at ? new Date(entry.created_at).getTime() : null),
    name: entry => entry.name,
  },
  searchText: entry => entry.name,
})

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('ru-RU')
}
</script>
