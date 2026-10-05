<template>
  <div class="flex flex-col gap-4">
    <template v-if="pending">
      <USkeleton
        v-for="index in 3"
        :key="index"
        class="h-56 w-full rounded-xl"
      />
    </template>

    <section
      v-for="(deputy, index) in deputies"
      v-else
      :id="`deputy-${index}`"
      :key="`${deputy.surname}-${deputy.name}`"
      :aria-labelledby="`deputy-${index}-name`"
      class="scroll-mt-24 rounded-xl bg-elevated"
    >
      <header class="flex items-center gap-4 px-6 py-4">
        <img
          v-if="deputy.image"
          :src="deputy.image"
          alt=""
          class="size-14 shrink-0 rounded-full object-cover"
          loading="lazy"
        >
        <UAvatar
          v-else
          :alt="deputyFullName(deputy)"
          size="xl"
        />
        <div class="min-w-0 flex-1">
          <h2
            :id="`deputy-${index}-name`"
            class="text-h3 text-text-primary"
          >
            {{ deputyFullName(deputy) }}
          </h2>
          <p class="text-sm text-text-muted">
            {{ deputy.role }}
          </p>
        </div>
      </header>

      <ul class="grid gap-3 px-6 pb-6 sm:grid-cols-2">
        <li
          v-for="slug in deputy.departmentSlugs"
          :key="slug"
        >
          <NuxtLink
            :to="`/about/departments/${slug}`"
            class="group flex h-full items-center gap-3 rounded-lg bg-default p-4 transition-colors duration-200 hover:bg-accented focus-visible:outline-2 focus-visible:outline-primary motion-reduce:transition-none"
          >
            <UIcon
              :name="departmentIcon(slug)"
              class="size-5 shrink-0 text-primary"
              aria-hidden="true"
            />
            <span class="min-w-0 flex-1 text-sm font-medium leading-snug text-text-primary text-pretty">
              {{ departmentName(slug) }}
            </span>
            <UIcon
              name="i-lucide-arrow-right"
              class="size-4 shrink-0 text-text-muted transition-transform duration-200 group-hover:translate-x-0.5"
              aria-hidden="true"
            />
          </NuxtLink>
        </li>
      </ul>
    </section>

    <p
      v-if="!pending && !deputies.length"
      class="rounded-xl bg-elevated p-6 text-base text-text-muted"
    >
      Структура администрации скоро будет опубликована.
    </p>
  </div>
</template>

<script setup lang="ts">
import type { Deputy } from '~/data/departments'
import { departmentIcon } from '~/data/department-icons'

const { data: deputiesData, pending } = await useDeputiesList()
const { departmentName } = useDepartmentNameMap()
const deputies = computed(() => deputiesData.value ?? [])

function deputyFullName(deputy: Deputy) {
  return `${deputy.surname} ${deputy.name} ${deputy.patronymic}`
}
</script>
