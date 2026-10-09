<template>
  <div class="flex flex-col gap-6">
    <dl class="grid grid-cols-1 gap-3 sm:grid-cols-2">
      <div class="rounded-lg bg-elevated p-4 sm:col-span-2">
        <ReserveReviewFact
          label="Для каких должностей"
          :ref-text="reserve.targetRef"
        >
          {{ reserve.targetPositions }}
        </ReserveReviewFact>
      </div>
      <div class="rounded-lg bg-elevated p-4 sm:col-span-2">
        <ReserveReviewFact label="Комиссия">
          {{ reserve.commission }}
          <span class="block text-text-muted">{{ reserve.commissionAct }}</span>
        </ReserveReviewFact>
      </div>
      <div class="rounded-lg bg-elevated p-4">
        <ReserveReviewFact label="Продление">
          {{ reserve.extension }}, {{ reserve.extensionNote }}
        </ReserveReviewFact>
      </div>
      <div class="rounded-lg bg-elevated p-4">
        <ReserveReviewFact label="Редакции акта">
          {{ reserve.editions }}
        </ReserveReviewFact>
      </div>
    </dl>

    <section class="flex flex-col gap-3">
      <h3 class="text-lg font-medium text-text-primary">
        Как попасть в резерв
      </h3>
      <ul class="flex flex-col gap-2">
        <li
          v-for="way in reserve.ways"
          :key="way.name"
          class="flex flex-col gap-1 rounded-lg bg-elevated p-4"
        >
          <span class="text-base font-semibold text-text-primary">{{ way.name }}</span>
          <span class="text-sm text-text-muted text-pretty">{{ way.detail }}</span>
          <span class="text-xs text-text-muted">{{ way.ref }}</span>
        </li>
      </ul>
    </section>

    <section class="flex flex-col gap-3">
      <h3 class="text-lg font-medium text-text-primary">
        Индивидуальный план развития
      </h3>
      <dl class="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div class="rounded-lg bg-elevated p-4">
          <ReserveReviewFact
            label="Когда разрабатывается"
            :ref-text="reserve.ipr.developRef"
          >
            {{ reserve.ipr.develop }}
          </ReserveReviewFact>
        </div>
        <div class="rounded-lg bg-elevated p-4">
          <ReserveReviewFact
            label="Отчётность"
            :ref-text="reserve.ipr.reportRef"
          >
            {{ reserve.ipr.report }}
          </ReserveReviewFact>
        </div>
        <div class="rounded-lg bg-elevated p-4">
          <ReserveReviewFact
            label="Наставничество"
            :ref-text="reserve.ipr.mentorRef"
          >
            {{ reserve.ipr.mentor }}
          </ReserveReviewFact>
        </div>
        <div
          v-if="reserve.use"
          class="rounded-lg bg-elevated p-4"
        >
          <ReserveReviewFact
            label="Назначение на должность из резерва"
            :ref-text="reserve.useRef"
          >
            {{ reserve.use }}
          </ReserveReviewFact>
        </div>
      </dl>
    </section>

    <section
      v-if="reserve.development"
      class="flex flex-col gap-3"
    >
      <div class="flex flex-col gap-1">
        <h3 class="text-lg font-medium text-text-primary">
          Мероприятия по развитию компетенций
        </h3>
        <p class="text-sm text-text-muted text-pretty">
          {{ reserve.development.act }}. Для кого: {{ reserve.development.scope }}.
        </p>
      </div>
      <ul class="grid grid-cols-1 gap-2 sm:grid-cols-3">
        <li
          v-for="format in reserve.development.formats"
          :key="format.name"
          class="flex flex-col gap-1 rounded-lg bg-elevated p-4"
        >
          <span class="text-base font-semibold text-text-primary">{{ format.name }}</span>
          <span class="text-sm text-text-muted">{{ format.detail }}</span>
        </li>
      </ul>
      <p class="text-xs text-text-muted">
        {{ reserve.development.frequency }}. Период действия: {{ reserve.development.period }} ({{ reserve.development.ref }})
      </p>
    </section>

    <section class="flex flex-col gap-3">
      <div class="flex flex-col gap-1">
        <h3 class="text-lg font-medium text-text-primary">
          Когда исключают из резерва
        </h3>
        <p class="text-xs text-text-muted">
          {{ reserve.exclusionsRef }}
        </p>
      </div>
      <ul class="grid grid-cols-1 gap-2 sm:grid-cols-2">
        <li
          v-for="item in reserve.exclusions"
          :key="item"
          class="rounded-lg bg-elevated px-4 py-3 text-sm text-text-primary text-pretty"
        >
          {{ item }}
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup lang="ts">
import type { Reserve } from '~/data/staff-reserve-review'

defineProps<{
  reserve: Reserve
}>()
</script>
