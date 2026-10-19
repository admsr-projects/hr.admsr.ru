<template>
  <div class="flex flex-col gap-4">
    <template v-if="pending">
      <USkeleton
        v-for="index in 2"
        :key="index"
        class="h-52 w-full rounded-xl"
      />
    </template>

    <DsEmptyState
      v-else-if="groupedStaff.length === 0"
      icon="i-lucide-phone-off"
      title="Контакты не найдены"
      description="Данные о сотрудниках временно недоступны."
    />

    <section
      v-for="group in groupedStaff"
      v-else
      :id="group.anchor"
      :key="group.branchId"
      :aria-labelledby="`branch-${group.branchId}`"
      class="scroll-mt-24 rounded-xl bg-elevated"
    >
      <header class="px-6 py-4">
        <h3
          :id="`branch-${group.branchId}`"
          class="text-h3 text-text-primary text-balance"
        >
          {{ group.branchName }}
        </h3>
        <p
          v-if="group.branchAddress"
          class="mt-1 flex items-start gap-1.5 text-sm text-text-muted"
        >
          <UIcon
            name="i-lucide-map-pin"
            class="mt-0.5 size-4 shrink-0"
            aria-hidden="true"
          />
          {{ group.branchAddress }}
        </p>
      </header>

      <ul class="flex flex-col gap-2 px-6 pb-6">
        <li
          v-for="member in group.members"
          :key="memberKey(member)"
        >
          <ContactMemberCard :member="member" />
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup lang="ts">
import type { StaffContact } from '~/components/ContactMemberCard.vue'

interface StaffGroup {
  branchId: string
  /** Якорь отдела для ссылок извне, например /contacts#otdel-3 (номер отдела в админке) */
  anchor?: string
  branchName: string
  branchAddress: string
  members: StaffContact[]
}

const config = useRuntimeConfig()
const route = useRoute()

const { data: allStaff, pending } = await useAsyncData('contacts-staff', () =>
  $fetch<StaffContact[]>(`${config.public.apiBaseUrl}/api/staff/?contacts=true`), {
  server: false,
})

const groupedStaff = computed<StaffGroup[]>(() => {
  const items = (allStaff.value ?? []).filter(member => !isPinnedHead(member))
  const groups: Record<string, StaffGroup> = {}

  for (const member of items) {
    const key = member.branch_name || '__none__'
    if (!groups[key]) {
      groups[key] = {
        branchId: key,
        anchor: member.branch ? `otdel-${member.branch}` : undefined,
        branchName: member.branch_name || 'Без отдела',
        branchAddress: member.branch_address || '',
        members: [],
      }
    }
    groups[key].members.push(member)
  }

  return Object.values(groups)
})

// Список приходит после открытия страницы, поэтому к отделу из ссылки вида #otdel-3 прокручиваем сами
watch([groupedStaff, () => route.hash], async ([groups, hash]) => {
  if (!import.meta.client || !hash.startsWith('#otdel-') || !groups.length) return
  await nextTick()
  document.getElementById(hash.slice(1))?.scrollIntoView({ block: 'start' })
}, { immediate: true })

function isPinnedHead(member: StaffContact) {
  return member.is_management_head === true
}

function memberKey(member: StaffContact) {
  return `${member.surname}-${member.name}-${member.patronym}-${member.role}`
}
</script>
