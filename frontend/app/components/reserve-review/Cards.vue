<template>
  <ul class="flex flex-col gap-4">
    <li
      v-for="reserve in reserves"
      :key="reserve.id"
      class="flex flex-col gap-4 rounded-xl bg-elevated p-6"
    >
      <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div class="flex min-w-0 flex-col items-start gap-3">
          <UBadge
            :label="reserve.normative"
            :color="reserveBadge[reserve.id]"
            variant="soft"
          />
          <h3 class="text-lg font-medium text-text-primary">
            <ReserveReviewLabel :reserve="reserve.id" />
          </h3>
          <p class="max-w-3xl text-sm text-text-muted text-pretty">
            {{ reserve.name }}
          </p>
        </div>

        <UModal
          :title="reserve.short"
          :description="reserve.name"
          :ui="{ content: 'max-w-3xl', body: 'flex flex-col gap-6', description: 'text-sm text-text-muted' }"
        >
          <UButton
            label="Подробнее"
            trailing-icon="i-lucide-arrow-right"
            color="primary"
            variant="soft"
            class="shrink-0 self-start"
          />
          <template #body>
            <ReserveReviewDetails :reserve="reserve" />
          </template>
        </UModal>
      </div>

      <dl class="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
        <div class="rounded-lg bg-default p-4">
          <ReserveReviewFact label="Основание">
            {{ reserve.normative }}
            <span class="block text-text-muted">Последняя редакция: {{ lastEdition(reserve) }}</span>
            <span
              v-if="reserve.federalBasis"
              class="block text-text-muted"
            >{{ reserve.federalBasis }}</span>
          </ReserveReviewFact>
        </div>
        <div class="rounded-lg bg-default p-4">
          <ReserveReviewFact
            label="Ответственный"
            :ref-text="reserve.responsibleRef"
          >
            {{ reserve.responsible }}
          </ReserveReviewFact>
        </div>
        <div class="rounded-lg bg-default p-4">
          <ReserveReviewFact
            label="Должностей"
            :ref-text="reserve.targetRef"
          >
            <span
              v-if="reserve.positionsCount"
              class="text-h2 text-text-primary"
            >{{ reserve.positionsCount }}</span>
            <span
              v-else
              class="text-text-muted"
            >группы должностей</span>
          </ReserveReviewFact>
        </div>
        <div class="rounded-lg bg-default p-4">
          <ReserveReviewFact
            label="Кандидатов"
            :ref-text="reserve.maxCandidatesRef"
          >
            <span class="text-h2 text-text-primary">≤ {{ reserve.maxCandidates }}</span>
            на должность
          </ReserveReviewFact>
        </div>
        <div class="rounded-lg bg-default p-4">
          <ReserveReviewFact
            label="Срок"
            :ref-text="reserve.termRef"
          >
            {{ reserve.term }} + {{ reserve.extension }}
          </ReserveReviewFact>
        </div>
        <div class="rounded-lg bg-default p-4">
          <ReserveReviewFact label="Комиссия">
            {{ reserve.commissionAct }}
          </ReserveReviewFact>
        </div>
      </dl>
    </li>
  </ul>
</template>

<script setup lang="ts">
import { reserveBadge, staffReserveReview, type Reserve } from '~/data/staff-reserve-review'

const reserves = staffReserveReview.reserves

function lastEdition(reserve: Reserve): string {
  return reserve.editions.split(', ').at(-1) ?? ''
}
</script>
