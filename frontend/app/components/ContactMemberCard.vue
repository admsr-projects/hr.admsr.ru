<template>
  <div class="flex min-w-0 flex-col gap-3 rounded-lg bg-default p-4 md:flex-row md:items-center md:gap-6">
    <div class="flex min-w-0 items-center gap-3 md:w-2/5">
      <UAvatar
        :alt="fullName"
        size="lg"
        class="shrink-0"
      />
      <div class="min-w-0">
        <p class="text-base font-semibold leading-snug text-text-primary text-pretty">
          {{ fullName }}
        </p>
        <p
          v-if="member.role"
          class="text-sm text-text-muted text-pretty"
        >
          {{ member.role }}
        </p>
      </div>
    </div>

    <ul class="flex min-w-0 flex-1 flex-wrap gap-x-6 gap-y-2 text-sm text-text-primary">
      <li
        v-if="member.phone"
        class="flex items-center gap-2"
      >
        <UIcon
          name="i-lucide-phone"
          class="size-4 shrink-0 text-text-muted"
          aria-hidden="true"
        />
        <a
          v-if="phoneHref"
          :href="phoneHref"
          class="hover:text-primary transition-colors duration-200"
        >
          {{ member.phone }}
        </a>
        <span v-else>{{ member.phone }}</span>
      </li>

      <li
        v-if="member.cabinet_number"
        class="flex items-center gap-2"
      >
        <UIcon
          name="i-lucide-door-open"
          class="size-4 shrink-0 text-text-muted"
          aria-hidden="true"
        />
        <span>Кабинет {{ member.cabinet_number }}</span>
      </li>

      <li
        v-if="member.email"
        class="flex min-w-0 items-center gap-2"
      >
        <UIcon
          name="i-lucide-mail"
          class="size-4 shrink-0 text-text-muted"
          aria-hidden="true"
        />
        <a
          :href="`mailto:${member.email}`"
          class="break-all hover:text-primary transition-colors duration-200"
        >
          {{ member.email }}
        </a>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
export interface StaffContact {
  name?: string
  surname?: string
  patronym?: string
  role?: string
  phone?: string
  email?: string
  cabinet_number?: string
  branch_name?: string
  branch_address?: string
  is_management_head?: boolean
}

const props = defineProps<{
  member: StaffContact
}>()

const fullName = computed(() => {
  const parts = [props.member.surname, props.member.name, props.member.patronym]
    .filter(Boolean)
  return parts.join(' ') || 'Сотрудник'
})

const phoneHref = computed(() => {
  const digits = (props.member.phone ?? '').replace(/[^\d+]/g, '')
  return digits ? `tel:${digits}` : undefined
})
</script>
