<template>
  <UModal
    :open="!!position"
    :title="position ? `Позиция № ${position.id}` : undefined"
    :description="position?.title"
    :ui="{ content: 'max-w-3xl', body: 'flex flex-col gap-6', title: 'text-caption font-semibold text-primary', description: 'text-h3 text-text-primary' }"
    @update:open="onOpenChange"
  >
    <template
      v-if="position"
      #body
    >
      <div class="flex flex-wrap gap-2">
        <UBadge
          color="neutral"
          variant="soft"
        >
          <span
            class="size-2 shrink-0 rounded-full"
            :class="categoryColor(category?.color ?? '').dot"
            aria-hidden="true"
          />
          {{ category?.name }}
        </UBadge>
        <UBadge
          :color="position.outcome ? outcomeStyle(position.outcome).badge : 'neutral'"
          variant="soft"
        >
          {{ position.outcome ? position.outcome_label : OUTCOME_NONE_LABEL }}
        </UBadge>
        <UBadge
          v-if="position.page"
          color="neutral"
          variant="soft"
        >
          Стр. {{ position.page }} PDF
        </UBadge>
      </div>

      <section class="flex flex-col gap-2">
        <h3 class="text-caption font-semibold text-primary">
          Правовая позиция — дословно
        </h3>
        <blockquote class="rounded-lg bg-elevated p-4 text-body text-text-primary text-pretty">
          {{ position.key_quote }}
        </blockquote>
      </section>

      <UAlert
        v-if="position.notes.length"
        color="warning"
        variant="soft"
        title="Норма изменена"
        :description="position.notes.map(note => note.text).join(' ')"
      />

      <section
        v-if="position.facts_summary"
        class="flex flex-col gap-2"
      >
        <h3 class="text-caption font-semibold text-primary">
          Фабула дела
        </h3>
        <p class="text-body text-text-primary text-pretty">
          {{ position.facts_summary }}
        </p>
        <p
          v-if="position.outcome_note"
          class="text-caption text-text-muted"
        >
          Итог: {{ position.outcome_note }}.
        </p>
      </section>

      <section
        v-if="position.lesson"
        class="flex flex-col gap-2"
      >
        <h3 class="text-caption font-semibold text-primary">
          Что важно служащему
        </h3>
        <div class="rounded-lg bg-primary/10 p-4">
          <p class="text-body text-text-primary text-pretty">
            {{ position.lesson }}
          </p>
          <p class="mt-2 text-overline text-text-muted">
            Редакционный вывод для практики, не является текстом обзора.
          </p>
        </div>
      </section>

      <section
        v-if="position.subjects.length || position.municipal"
        class="flex flex-col gap-2"
      >
        <h3 class="text-caption font-semibold text-primary">
          Кто фигурирует
        </h3>
        <div class="flex flex-wrap gap-1.5">
          <UBadge
            v-for="subject in position.subjects"
            :key="subject"
            color="neutral"
            variant="soft"
          >
            {{ subject }}
          </UBadge>
          <UBadge
            v-if="position.municipal"
            color="success"
            variant="soft"
          >
            Муниципальный уровень
          </UBadge>
        </div>
      </section>

      <section
        v-if="position.legal_basis.length"
        class="flex flex-col gap-2"
      >
        <h3 class="text-caption font-semibold text-primary">
          Применённые нормы
        </h3>
        <ul class="flex flex-col gap-2">
          <li
            v-for="norm in position.legal_basis"
            :key="norm.tag"
            class="grid grid-cols-1 gap-1 rounded-lg bg-elevated px-4 py-3 sm:grid-cols-[minmax(8rem,12rem)_1fr] sm:gap-4"
          >
            <span class="flex flex-wrap items-center gap-2 text-caption font-semibold text-text-primary">
              {{ norm.tag }}
              <UBadge
                v-if="edu.actByAbbr.value.get(norm.act)?.changed_note"
                color="warning"
                variant="soft"
              >
                Норма изменена
              </UBadge>
            </span>
            <span class="text-caption text-text-muted">{{ edu.actByAbbr.value.get(norm.act)?.full_name }}</span>
          </li>
        </ul>
      </section>

      <section
        v-if="position.amount"
        class="flex flex-col gap-2"
      >
        <h3 class="text-caption font-semibold text-primary">
          Обращено в доход РФ
        </h3>
        <p class="text-h2 text-text-primary">
          {{ formatRubles(position.amount) }}
        </p>
      </section>

      <section
        v-if="related.length"
        class="flex flex-col gap-2"
      >
        <h3 class="text-caption font-semibold text-primary">
          Связанные позиции
        </h3>
        <ul class="flex flex-col gap-2">
          <li
            v-for="item in related"
            :key="item.position.id"
          >
            <button
              type="button"
              class="grid w-full grid-cols-[auto_1fr] items-start gap-3 rounded-lg bg-elevated px-4 py-3 text-left transition-colors duration-150 hover:bg-accented motion-reduce:transition-none"
              @click="edu.openPosition(item.position.id)"
            >
              <EducationDiamond
                :id="item.position.id"
                :color="edu.categoryById.value.get(item.position.category)?.color ?? ''"
              />
              <span class="flex flex-col gap-0.5">
                <span class="text-caption font-medium text-text-primary">{{ item.position.title }}</span>
                <span class="text-overline text-text-muted">Общие нормы: {{ item.shared.join(', ') }}</span>
              </span>
            </button>
          </li>
        </ul>
      </section>
    </template>

    <template
      v-if="position"
      #footer
    >
      <div class="flex flex-wrap gap-2">
        <UButton
          color="neutral"
          variant="soft"
          icon="i-lucide-calendar-range"
          @click="edu.showOnTimeline(position.id)"
        >
          Показать на таймлайне
        </UButton>
        <UButton
          color="neutral"
          variant="soft"
          icon="i-lucide-file-text"
          @click="edu.showInText(position.id)"
        >
          Читать полный текст
        </UButton>
        <UButton
          v-if="!kiosk"
          color="neutral"
          variant="soft"
          :icon="copied ? 'i-lucide-check' : 'i-lucide-link'"
          @click="copyLink(position.id)"
        >
          {{ copied ? 'Ссылка скопирована' : 'Скопировать ссылку' }}
        </UButton>
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { OUTCOME_NONE_LABEL, categoryColor, formatRubles, outcomeStyle } from '~/utils/education'

const edu = useEducationReview()
const kiosk = useKiosk()

const position = computed(() => edu.openId.value === null ? undefined : edu.positionById.value.get(edu.openId.value))
const category = computed(() => position.value ? edu.categoryById.value.get(position.value.category) : undefined)

// Позиции с общими нормами — ближайшие по смыслу, до шести штук
const related = computed(() => {
  const current = position.value
  if (!current) return []
  const tags = new Set(current.legal_basis.map(norm => norm.tag))
  return edu.positions.value
    .filter(other => other.id !== current.id)
    .map(other => ({ position: other, shared: other.legal_basis.map(norm => norm.tag).filter(tag => tags.has(tag)) }))
    .filter(item => item.shared.length)
    .sort((a, b) => b.shared.length - a.shared.length || a.position.id - b.position.id)
    .slice(0, 6)
})

function onOpenChange(open: boolean) {
  if (!open) edu.closePosition()
}

const copied = ref(false)

async function copyLink(id: number) {
  const url = `${location.origin}${location.pathname}#pos-${id}`
  try {
    await navigator.clipboard.writeText(url)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  }
  catch {
    window.prompt('Скопируйте ссылку:', url)
  }
}

watch(() => edu.openId.value, () => {
  copied.value = false
})
</script>
