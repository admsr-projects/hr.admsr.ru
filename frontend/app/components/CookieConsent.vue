<template>
  <Transition
    enter-active-class="transition duration-200 motion-reduce:transition-none"
    leave-active-class="transition duration-200 motion-reduce:transition-none"
    enter-from-class="translate-y-2 opacity-0"
    leave-to-class="translate-y-2 opacity-0"
  >
    <section
      v-if="visible"
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
        Файлы cookie нужны для корректной работы сайта и сохранения ваших настроек.
        Подробнее — в
        <NuxtLink
          to="/privacy"
          class="text-primary underline underline-offset-2"
        >Политике обработки персональных данных</NuxtLink>.
      </p>

      <div class="flex flex-wrap gap-2">
        <UButton
          label="Понятно"
          color="primary"
          class="cursor-pointer"
          @click="accept"
        />
        <UButton
          label="Подробнее"
          to="/privacy"
          color="neutral"
          variant="soft"
          class="cursor-pointer"
        />
      </div>
    </section>
  </Transition>
</template>

<script setup lang="ts">
const cookieConsent = useCookie('cookieConsent', {
  maxAge: 60 * 60 * 24 * 365,
  sameSite: 'lax',
  path: '/',
})

// Показываем только в браузере, чтобы серверная и клиентская разметка совпадали
const mounted = ref(false)
const visible = computed(() => mounted.value && !cookieConsent.value)

onMounted(() => {
  mounted.value = true
})

function accept() {
  cookieConsent.value = 'true'
}
</script>
