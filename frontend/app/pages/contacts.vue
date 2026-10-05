<script setup lang="ts">
import type { StaffContact } from '~/components/ContactMemberCard.vue'

useHead({ title: 'Контакты' })

const config = useRuntimeConfig()

const { data: managementHeadData, pending: managementHeadPending } = await useAsyncData(
  'contacts-management-head',
  () => $fetch<StaffContact[]>(`${config.public.apiBaseUrl}/api/staff/?management_head=true`),
  { server: false },
)

const managementHead = computed(() => managementHeadData.value?.[0])
const managementUnitTitle = computed(
  () => managementHead.value?.branch_name ?? 'Управление муниципальной службы, кадров и наград',
)
</script>

<template>
  <DsStandardPage
    title="Контакты"
    description="Телефоны, адреса и режим работы отделов кадровой политики администрации Сургутского района"
  >
    <DsContentSection
      v-if="managementHeadPending || managementHead"
      :title="managementUnitTitle"
      description="Руководитель управления, курирующего кадровой работой администрации района"
      overline="Руководство"
      heading-id="contacts-hr-management"
      spacing="lg"
    >
      <div class="rounded-xl bg-elevated p-6">
        <USkeleton
          v-if="managementHeadPending"
          class="h-20 w-full rounded-lg"
        />
        <ContactMemberCard
          v-else-if="managementHead"
          :member="managementHead"
        />
      </div>
    </DsContentSection>

    <DsContentSection
      title="Справочник сотрудников"
      description="Контактные данные сотрудников отделов кадровой политики администрации района"
      overline="Контакты"
      heading-id="contacts-directory"
      spacing="lg"
    >
      <ContactsTable />
    </DsContentSection>

    <DsContentSection
      title="Нужна помощь?"
      description="Если вы не нашли нужный контакт, оставьте обращение — мы ответим в рабочее время"
      overline="Обратная связь"
      heading-id="contacts-feedback"
      spacing="lg"
    >
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <UPageCard
          title="Обратная связь"
          description="Задайте вопрос или оставьте предложение через форму на портале."
          icon="i-lucide-message-square"
          to="/feedback"
          variant="soft"
          class="h-full cursor-pointer"
          :ui="{
            root: 'h-full',
            container: 'h-full',
            wrapper: 'h-full',
          }"
        />

        <UPageCard
          title="Структура администрации"
          description="Узнайте, какие отраслевые органы курируют направления работы района."
          icon="i-lucide-network"
          to="/about/structure"
          variant="soft"
          class="h-full cursor-pointer"
          :ui="{
            root: 'h-full',
            container: 'h-full',
            wrapper: 'h-full',
          }"
        />
      </div>
    </DsContentSection>
  </DsStandardPage>
</template>
