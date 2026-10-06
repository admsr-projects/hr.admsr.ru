<template>
  <ul :class="nested ? 'ms-5 mt-1 border-s border-default' : 'ms-5 mt-1 border-s border-default pb-1.5'">
    <li
      v-for="item in items"
      :key="item.to ?? item.label"
    >
      <!-- Группа без страницы: раскрывается по клику -->
      <template v-if="!item.to">
        <button
          type="button"
          class="-ms-px flex w-full cursor-pointer items-start gap-1 border-s border-transparent px-1.5 text-start"
          :aria-expanded="isOpen(item)"
          :title="item.title"
          @click="toggle(item)"
        >
          <span class="flex min-w-0 flex-1 items-start gap-1 rounded-lg px-2.5 py-1.5 text-sm font-medium text-text-muted transition-colors duration-200 hover:text-text-primary">
            <span class="min-w-0 flex-1 text-pretty">{{ item.label }}</span>
            <UIcon
              name="i-lucide-chevron-down"
              class="mt-0.5 size-4 shrink-0 transition-transform duration-200"
              :class="isOpen(item) ? 'rotate-180' : undefined"
              aria-hidden="true"
            />
          </span>
        </button>
        <DsSectionSidebarList
          v-if="isOpen(item) && item.children?.length"
          :items="item.children"
          nested
        />
      </template>

      <!-- Обычный пункт; подпункты видны, когда пункт помечен expanded -->
      <template v-else>
        <NuxtLink
          :to="item.to"
          class="-ms-px flex border-s px-1.5"
          :class="item.active ? 'border-primary' : 'border-transparent'"
          :aria-current="item.active ? 'page' : undefined"
        >
          <span
            class="rounded-lg px-2.5 py-1.5 text-sm font-medium text-pretty transition-colors duration-200"
            :class="item.active ? 'text-primary' : 'text-text-muted hover:text-text-primary'"
          >
            {{ item.label }}
          </span>
        </NuxtLink>
        <DsSectionSidebarList
          v-if="item.expanded && item.children?.length"
          :items="item.children"
          nested
        />
      </template>
    </li>
  </ul>
</template>

<script setup lang="ts">
import type { SidebarItem } from '~/data/standard-pages'

defineProps<{
  items: SidebarItem[]
  nested?: boolean
}>()

const manual = reactive<Record<string, boolean>>({})

function isOpen(item: SidebarItem) {
  return manual[item.label] ?? item.expanded ?? false
}

function toggle(item: SidebarItem) {
  manual[item.label] = !isOpen(item)
}
</script>
