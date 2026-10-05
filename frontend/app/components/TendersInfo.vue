<template>
  <div class="ds-container py-8">
    <div class="mb-6 rounded-xl bg-elevated p-6">
      <p class="text-base lg:text-lg text-gray-900 dark:text-white mb-6">
        Здесь представлены ключевые документы и информация о конкурсах, проводимых Администрацией Сургутского района.
      </p>
      <div v-if="mainPageTenders.length > 0" class="space-y-3">
        <div
          v-for="doc in mainPageTenders"
          :key="doc.id"
          class="flex items-center justify-between gap-3 rounded-xl bg-elevated p-4 transition-colors duration-200 hover:bg-accented"
        >
          <span class="text-base font-medium text-text-primary">{{ doc.name }}</span>
          <UButton
            :to="doc.link"
            target="_blank"
            external
            label="Скачать"
            icon="i-lucide-download"
            color="primary"
            :aria-label="'Скачать: ' + doc.name"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const { data: allTenders } = await useAsyncData('tenders-main-page', () =>
  $fetch(`${useRuntimeConfig().public.apiBaseUrl}/api/tenders/`), { server: false }
)
const mainPageTenders = computed(() =>
  (allTenders.value ?? []).filter(t => t.show_on_main_page)
)
</script>
