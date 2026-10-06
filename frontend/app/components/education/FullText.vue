<template>
  <div class="flex flex-col gap-4">
    <div class="flex flex-wrap gap-2">
      <UButton
        color="neutral"
        variant="soft"
        icon="i-lucide-chevrons-up-down"
        @click="edu.expanded.value = allValues"
      >
        Развернуть все
      </UButton>
      <UButton
        color="neutral"
        variant="soft"
        icon="i-lucide-chevrons-down-up"
        @click="edu.expanded.value = []"
      >
        Свернуть все
      </UButton>
    </div>

    <UAccordion
      v-model="edu.expanded.value"
      type="multiple"
      :items="items"
      :unmount-on-hide="false"
      :ui="{
        root: 'flex flex-col gap-2',
        item: 'rounded-xl bg-elevated border-b-0 scroll-mt-28',
        trigger: 'items-start gap-3 px-4 py-3 text-left',
        label: 'whitespace-normal',
        body: 'px-4 pb-4 text-body',
        content: 'overflow-hidden',
      }"
    >
      <template #default="{ item }">
        <span
          :id="item.value"
          class="flex items-start gap-3"
        >
          <span
            class="min-w-8 shrink-0 text-h3 text-text-primary"
            :class="item.value === 'ft-intro' ? 'text-text-muted' : undefined"
          >
            {{ item.number }}
          </span>
          <!-- eslint-disable-next-line vue/no-v-html -->
          <span
            class="text-base font-semibold text-text-primary text-pretty"
            v-html="item.labelHtml"
          />
        </span>
      </template>

      <template #body="{ item }">
        <div class="flex flex-col gap-3 md:pl-11">
          <DsMarkdown
            v-if="item.markdown"
            :source="item.markdown"
          />
          <!-- eslint-disable vue/no-v-html -->
          <p
            v-for="(html, index) in item.paragraphHtml"
            :key="index"
            class="max-w-prose text-pretty"
            v-html="html"
          />
          <!-- eslint-enable vue/no-v-html -->

          <div
            v-if="item.notes?.length"
            class="flex flex-col gap-2 border-t border-default pt-3 text-caption text-text-muted"
          >
            <p
              v-for="note in item.notes"
              :id="`fn-${item.position}-${note.n}`"
              :key="note.n"
            >
              <a
                :href="`#fnr-${item.position}-${note.n}`"
                class="font-semibold text-primary underline underline-offset-2 hover:no-underline"
              >&lt;{{ note.n }}&gt;</a>
              {{ note.text }}
            </p>
          </div>

          <div
            v-if="item.position"
            class="flex flex-wrap items-center gap-2"
          >
            <UButton
              color="neutral"
              variant="soft"
              @click="edu.openPosition(item.position)"
            >
              Открыть карточку
            </UButton>
            <UBadge
              v-if="item.page"
              color="neutral"
              variant="soft"
            >
              Стр. {{ item.page }} PDF
            </UBadge>
          </div>
        </div>
      </template>
    </UAccordion>

    <DsEmptyState
      v-if="!edu.filtered.value.length"
      icon="i-lucide-file-search"
      title="Ничего не найдено"
      description="Под выбранные условия не подходит ни одна позиция."
    >
      <template #action>
        <UButton
          color="neutral"
          variant="soft"
          @click="edu.resetFilters()"
        >
          Сбросить фильтры
        </UButton>
      </template>
    </DsEmptyState>
  </div>
</template>

<script setup lang="ts">
import type { EducationNote } from '~/utils/education'
import { highlightHtml, paragraphHtml } from '~/utils/education'

const edu = useEducationReview()

interface TextItem {
  value: string
  label: string
  number: string
  labelHtml: string
  paragraphHtml: string[]
  /** Текст в формате Markdown (вводная часть) */
  markdown?: string
  position: number
  page: number | null
  notes: EducationNote[]
}

const items = computed<TextItem[]>(() => {
  const query = edu.filters.q
  const result: TextItem[] = []

  // Вводная часть показывается только без фильтров: она не относится ни к одной позиции
  const intro = edu.review.value?.page.intro?.trim() ?? ''
  if (!edu.activeCount.value && intro) {
    result.push({
      value: 'ft-intro',
      label: 'Вводная часть обзора',
      number: '—',
      labelHtml: highlightHtml('Вводная часть обзора', query),
      paragraphHtml: [],
      markdown: intro,
      position: 0,
      page: null,
      notes: [],
    })
  }

  for (const position of edu.filtered.value) {
    result.push({
      value: `ft-${position.id}`,
      label: position.key_quote,
      number: `${position.id}.`,
      labelHtml: highlightHtml(position.key_quote, query),
      paragraphHtml: position.paragraphs.map(text => paragraphHtml(text, query, position.id)),
      position: position.id,
      page: position.page,
      notes: position.notes,
    })
  }
  return result
})

const allValues = computed(() => items.value.map(item => item.value))

// При поиске по тексту сразу раскрываем найденное, если позиций немного
watch(() => edu.filters.q, (query) => {
  if (query.trim() && edu.filtered.value.length <= 5) {
    edu.expanded.value = edu.filtered.value.map(position => `ft-${position.id}`)
  }
})
</script>
