<template>
  <Transition
    enter-active-class="transition duration-200 motion-reduce:transition-none"
    leave-active-class="transition duration-200 motion-reduce:transition-none"
    enter-from-class="translate-y-2 opacity-0"
    leave-to-class="translate-y-2 opacity-0"
  >
    <section
      v-if="bannerVisible"
      aria-labelledby="cookie-consent-title"
      class="fixed inset-x-4 bottom-4 z-50 flex flex-col gap-4 rounded-xl bg-default p-6 shadow-xl ring ring-default sm:right-auto sm:bottom-6 sm:left-6 sm:w-[26rem]"
    >
      <div class="flex items-center gap-3">
        <span
          class="flex size-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary"
          aria-hidden="true"
        >
          <UIcon
            name="i-lucide-cookie"
            class="size-5"
          />
        </span>
        <h2
          id="cookie-consent-title"
          class="text-h3 text-text-primary"
        >
          Мы используем cookie
        </h2>
      </div>

      <p class="text-caption text-text-muted text-pretty">
        Необходимые cookie нужны для работы сайта. С вашего согласия мы также используем Яндекс.Метрику,
        чтобы понимать, как посетители пользуются порталом. Подробнее — в
        <NuxtLink
          to="/privacy"
          class="text-primary underline underline-offset-2"
        >Политике обработки персональных данных</NuxtLink>.
      </p>

      <div class="flex flex-wrap gap-2">
        <UButton
          label="Принять все"
          color="primary"
          class="cursor-pointer"
          @click="acceptAll"
        />
        <UButton
          label="Отказаться"
          color="neutral"
          variant="soft"
          class="cursor-pointer"
          @click="rejectAll"
        />
        <UButton
          label="Настроить"
          color="neutral"
          variant="soft"
          class="cursor-pointer"
          @click="openSettings"
        />
      </div>
    </section>
  </Transition>

  <UModal
    v-model:open="settingsOpen"
    title="Настройки cookie"
    description="Выберите, какие cookie разрешить. Изменить выбор можно в любой момент по ссылке «Настройки cookie» внизу страницы."
  >
    <template #body>
      <ul class="flex flex-col gap-3">
        <li class="rounded-lg bg-elevated p-4">
          <USwitch
            :model-value="true"
            disabled
            label="Необходимые"
            description="Обеспечивают работу портала: запоминают тему оформления и ваш выбор по cookie. Отключить нельзя."
          />
        </li>
        <li class="rounded-lg bg-elevated p-4">
          <USwitch
            v-model="draft.analytics"
            label="Аналитика — Яндекс.Метрика"
            description="Обезличенная статистика посещений: какие страницы смотрят и откуда приходят. Помогает улучшать портал."
          />
        </li>
        <li class="rounded-lg bg-elevated p-4">
          <USwitch
            v-model="draft.webvisor"
            :disabled="!draft.analytics"
            label="Вебвизор и карта кликов"
            description="Обезличенные записи того, как посетители прокручивают страницы и куда нажимают. Работает только вместе с аналитикой."
          />
        </li>
      </ul>
    </template>

    <template #footer>
      <div class="flex w-full flex-wrap justify-end gap-2">
        <UButton
          label="Отказаться от всех"
          color="neutral"
          variant="soft"
          class="cursor-pointer"
          @click="rejectAll"
        />
        <UButton
          label="Принять все"
          color="neutral"
          variant="soft"
          class="cursor-pointer"
          @click="acceptAll"
        />
        <UButton
          label="Сохранить выбор"
          color="primary"
          class="cursor-pointer"
          @click="save(draft)"
        />
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import type { CookieConsentChoice } from '~/composables/useCookieConsent'

const { consent, settingsOpen, save, acceptAll, rejectAll, openSettings } = useCookieConsent()

// Показываем только в браузере, чтобы серверная и клиентская разметка совпадали
const mounted = ref(false)
const bannerVisible = computed(() => mounted.value && !consent.value && !settingsOpen.value)

onMounted(() => {
  mounted.value = true
})

// Переключатели в окне настроек меняют черновик; сохраняется он только кнопкой
const draft = reactive<CookieConsentChoice>({ analytics: false, webvisor: false })

watch(settingsOpen, (open) => {
  if (!open) return
  draft.analytics = consent.value?.analytics ?? false
  draft.webvisor = consent.value?.webvisor ?? false
})

watch(() => draft.analytics, (analytics) => {
  if (!analytics) draft.webvisor = false
})
</script>
