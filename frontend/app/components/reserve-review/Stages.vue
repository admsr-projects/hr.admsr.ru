<template>
  <div class="flex flex-col gap-4">
    <UTabs
      v-model="selected"
      :items="tabItems"
      :content="false"
      variant="link"
      class="w-full"
      aria-label="Выбор резерва"
    >
      <template #leading="{ item }">
        <span
          v-if="item.dot"
          class="size-2.5 shrink-0 rounded-full"
          :class="item.dot"
          aria-hidden="true"
        />
      </template>
    </UTabs>

    <ol
      class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4"
      :aria-label="`Этапы: ${reserve.short}`"
    >
      <li
        v-for="(item, index) in stages"
        :key="`${id}-${index}`"
        class="flex"
      >
        <button
          type="button"
          class="flex min-h-36 w-full cursor-pointer flex-col items-start gap-3 rounded-xl p-4 text-left transition-colors duration-200 motion-reduce:transition-none"
          :class="index === stepIndex ? 'bg-primary/10' : 'bg-elevated hover:bg-accented'"
          :aria-pressed="index === stepIndex"
          :aria-controls="detailId"
          @click="stepIndex = index"
        >
          <span
            class="flex size-8 shrink-0 items-center justify-center rounded-full text-sm font-semibold"
            :class="index === stepIndex ? 'bg-primary text-inverted' : 'bg-default text-primary'"
          >
            {{ index + 1 }}
          </span>
          <span class="text-base font-semibold text-text-primary text-pretty">{{ item.title }}</span>
          <span
            v-if="item.days != null"
            class="mt-auto flex items-baseline gap-1.5"
          >
            <span class="text-h2 text-primary">{{ item.days }}</span>
            <span class="text-xs text-text-muted">{{ item.unit }}</span>
          </span>
          <span
            v-else
            class="mt-auto text-xs text-text-muted text-pretty"
          >{{ item.term || 'Срок актом не установлен' }}</span>
        </button>
      </li>
    </ol>

    <div
      v-if="stage"
      :id="detailId"
      class="grid grid-cols-1 gap-4 rounded-xl bg-elevated p-6 lg:grid-cols-3"
      aria-live="polite"
    >
      <div class="flex flex-col gap-1">
        <p class="text-xs font-medium text-text-muted">
          Этап {{ stepIndex + 1 }} · {{ reserve.short }}
        </p>
        <h3 class="text-lg font-medium text-text-primary">
          {{ stage.title }}
        </h3>
        <p class="text-sm text-text-primary text-pretty">
          <template v-if="stage.term">
            {{ stage.term }}
          </template>
          <span
            v-else
            class="text-text-muted"
          >Срок актом не установлен</span>
        </p>
        <p
          v-if="stage.termNote"
          class="text-sm text-text-muted text-pretty"
        >
          {{ stage.termNote }}
        </p>
      </div>
      <div class="flex flex-col gap-1">
        <p class="text-xs font-medium text-text-muted">
          Ответственный
        </p>
        <p class="text-sm text-text-primary text-pretty">
          {{ stage.responsible }}
        </p>
      </div>
      <div class="flex flex-col gap-1">
        <p class="text-xs font-medium text-text-muted">
          Нормативное основание
        </p>
        <p class="text-sm text-text-primary">
          <span class="font-semibold">{{ reserve.normative }}</span>
          <span
            v-if="stage.ref && stage.ref !== '—'"
            class="block text-text-muted"
          >{{ stage.ref }}</span>
        </p>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <section class="flex flex-col gap-3 rounded-xl bg-elevated p-6">
        <div class="flex flex-col gap-1">
          <h3 class="text-lg font-medium text-text-primary">
            Как оценивают испытания
          </h3>
          <p class="text-xs text-text-muted">
            <span class="font-semibold">{{ reserve.normative }}</span>, {{ scoring.ref }}
          </p>
        </div>
        <ul class="flex flex-col gap-2">
          <li
            v-for="rule in scoring.rules"
            :key="rule"
            class="rounded-lg bg-default px-4 py-3 text-sm text-text-primary text-pretty"
          >
            {{ rule }}
          </li>
        </ul>
      </section>

      <section class="flex flex-col gap-3 rounded-xl bg-elevated p-6">
        <h3 class="text-lg font-medium text-text-primary">
          Способы включения в резерв
        </h3>
        <ul class="flex flex-col gap-2">
          <li
            v-for="way in reserve.ways"
            :key="way.name"
            class="flex flex-col gap-0.5 rounded-lg bg-default px-4 py-3"
          >
            <span class="text-base font-semibold text-text-primary">{{ way.name }}</span>
            <span class="text-sm text-text-muted text-pretty">{{ way.detail }}</span>
            <span class="text-xs text-text-muted">{{ way.ref }}</span>
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { findReserve, reserveDot, reserveIds, staffReserveReview, type ReserveId } from '~/data/staff-reserve-review'

const selected = ref<string>(reserveIds[0]!)
const stepIndex = ref(0)

const tabItems = reserveIds.map(id => ({ label: findReserve(id).short, value: id, dot: reserveDot[id] }))

const id = computed(() => selected.value as ReserveId)
const reserve = computed(() => findReserve(id.value))
const stages = computed(() => staffReserveReview.stages[id.value])
const stage = computed(() => stages.value[stepIndex.value])
const scoring = computed(() => staffReserveReview.scoring[id.value])
const detailId = 'review-stage-detail'

// У другого резерва — другой набор этапов, начинаем с первого
watch(selected, () => {
  stepIndex.value = 0
})
</script>
