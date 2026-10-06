<template>
  <article class="flex h-full min-w-0 flex-col overflow-hidden rounded-xl bg-elevated">
    <div class="aspect-[3/4] w-full overflow-hidden bg-default">
      <img
        v-if="member.image"
        :src="member.image"
        :alt="fullName"
        class="size-full object-cover object-top"
        loading="lazy"
      >
      <div
        v-else
        class="flex size-full items-center justify-center text-text-muted"
      >
        <UIcon
          name="i-lucide-user"
          class="size-16"
          aria-hidden="true"
        />
      </div>
    </div>

    <div class="flex flex-1 flex-col gap-3 p-6">
      <UBadge
        label="Лауреат доски почёта"
        icon="i-lucide-award"
        color="primary"
        class="w-fit"
      />

      <div class="flex flex-col gap-1">
        <h3 class="text-h3 text-text-primary text-balance">
          {{ fullName }}
        </h3>
        <p
          v-if="member.role"
          class="text-base text-text-primary text-pretty"
        >
          {{ member.role }}
        </p>
        <p
          v-if="member.branch_name"
          class="text-sm text-text-muted text-pretty"
        >
          {{ member.branch_name }}
        </p>
      </div>

      <p
        v-if="member.description"
        class="text-sm leading-6 text-text-muted text-pretty"
      >
        {{ member.description }}
      </p>
    </div>
  </article>
</template>

<script setup lang="ts">
export interface HonorBoardMember {
  name?: string
  surname?: string
  patronym?: string
  role?: string
  description?: string
  image?: string | null
  branch_name?: string
}

const props = defineProps<{
  member: HonorBoardMember
}>()

const fullName = computed(() => {
  const parts = [props.member.surname, props.member.name, props.member.patronym]
    .filter(Boolean)
  return parts.join(' ') || 'Сотрудник'
})
</script>
