<template>
  <div class="flex flex-col gap-4">
    <div class="grid grid-cols-1 items-start gap-4 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
      <div class="flex flex-col gap-4">
        <div class="overflow-x-auto rounded-xl bg-elevated p-2 sm:p-4">
          <table class="w-full min-w-[32rem] text-left">
            <caption class="sr-only">
              Методы оценки по актам. Выберите метод, чтобы увидеть описание.
            </caption>
            <thead>
              <tr class="text-sm font-medium text-text-muted">
                <th
                  scope="col"
                  class="px-4 py-3 font-medium"
                >
                  Метод
                </th>
                <th
                  v-for="reserve in reserves"
                  :key="reserve.id"
                  scope="col"
                  class="px-2 py-3 text-center font-medium"
                >
                  {{ shortNormative(reserve.normative) }}
                </th>
                <th
                  scope="col"
                  class="px-2 py-3 text-center font-medium"
                >
                  Обязателен <span class="block text-xs">(единая методика)</span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="method in methods"
                :key="method.id"
                class="cursor-pointer border-t border-default transition-colors duration-200 motion-reduce:transition-none"
                :class="method.id === selected.id ? 'bg-primary/10' : 'hover:bg-accented'"
                @click="selectedId = method.id"
              >
                <th
                  scope="row"
                  class="px-4 py-3 text-left"
                >
                  <button
                    type="button"
                    class="cursor-pointer text-left text-base font-semibold text-text-primary"
                    :aria-pressed="method.id === selected.id"
                    @click.stop="selectedId = method.id"
                  >
                    {{ method.name }}
                  </button>
                </th>
                <td
                  v-for="reserve in reserves"
                  :key="reserve.id"
                  class="px-2 py-3 text-center"
                >
                  <span
                    class="inline-block size-3 rounded-full"
                    :class="method.allowed[reserve.id] ? reserveDot[reserve.id] : 'bg-accented'"
                    aria-hidden="true"
                  />
                  <span class="sr-only">{{ method.allowed[reserve.id] ? 'допускается' : 'не предусмотрен' }}</span>
                </td>
                <td class="px-2 py-3 text-center">
                  <UBadge
                    v-if="method.mandatory"
                    label="да"
                    color="success"
                    variant="soft"
                  />
                  <span
                    v-else
                    class="text-text-muted"
                  >—</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <p class="flex items-start gap-2 rounded-xl bg-elevated p-4 text-sm text-text-muted text-pretty">
          <UIcon
            name="i-lucide-info"
            class="mt-0.5 size-4 shrink-0"
            aria-hidden="true"
          />
          {{ methodsNote }}
        </p>
      </div>

      <section
        class="flex flex-col gap-3 rounded-xl bg-elevated p-6 lg:sticky lg:top-[calc(var(--ui-header-height,4rem)+1.5rem)]"
        aria-live="polite"
      >
        <UBadge
          :label="selected.mandatory ? 'обязательный по единой методике' : 'дополнительный метод'"
          :color="selected.mandatory ? 'info' : 'neutral'"
          variant="soft"
          class="self-start"
        />
        <h3 class="text-lg font-medium text-text-primary">
          {{ selected.name }}
        </h3>
        <p class="text-sm text-text-primary text-pretty">
          {{ selected.desc }}
        </p>
        <div class="flex flex-col gap-2">
          <h4 class="text-base font-semibold text-text-primary">
            Где предусмотрен
          </h4>
          <ul
            v-if="places.length"
            class="flex list-disc flex-col gap-1 pl-5 text-sm text-text-primary"
          >
            <li
              v-for="place in places"
              :key="place.id"
            >
              <span class="font-semibold">{{ place.normative }}</span>, {{ place.ref }}
            </li>
          </ul>
          <p
            v-else
            class="text-sm text-text-muted text-pretty"
          >
            В актах района не назван; применим как «иная форма» по решению о проведении конкурса
          </p>
        </div>
        <p class="text-xs text-text-muted">
          Источник описания: {{ selected.source }}
        </p>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reserveDot, staffReserveReview } from '~/data/staff-reserve-review'

const { reserves, evaluationMethods: methods, methodsNote } = staffReserveReview

const selectedId = ref(methods[0]!.id)
const selected = computed(() => methods.find(method => method.id === selectedId.value) ?? methods[0]!)

const places = computed(() =>
  reserves.flatMap((reserve) => {
    const ref = selected.value.allowed[reserve.id]
    return ref ? [{ id: reserve.id, normative: reserve.normative, ref }] : []
  })
)

function shortNormative(normative: string): string {
  return normative.replace('Постановление ', '')
}
</script>
