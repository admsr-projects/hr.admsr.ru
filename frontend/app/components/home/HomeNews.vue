<template>
  <section class="bg-elevated/40">
    <UContainer class="flex flex-col gap-8 py-16 lg:py-20">
      <div class="flex max-w-2xl flex-col gap-3">
        <UBadge
          label="Новости"
          color="primary"
          variant="soft"
          class="w-fit"
        />
        <h2
          id="news"
          class="text-h2 text-highlighted text-balance"
        >
          Как живёт команда
        </h2>
        <p class="text-pretty text-lg leading-8 text-muted">
          События и достижения — коротко о том, что происходит в администрации района прямо сейчас.
        </p>
      </div>

      <div
        v-if="displayPosts.length"
        class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
      >
        <NewsCard
          v-for="(post, index) in displayPosts"
          :key="post.id"
          :post="post"
          :eager="index === 0"
        />
      </div>

      <div
        v-else
        class="flex flex-col items-center gap-4 rounded-xl border border-dashed border-default bg-elevated/40 px-6 py-14 text-center"
      >
        <UIcon
          name="i-lucide-newspaper"
          class="size-10 text-muted"
          aria-hidden="true"
        />
        <div class="flex flex-col gap-2">
          <p class="font-semibold text-highlighted">
            Новости скоро появятся
          </p>
          <p class="max-w-md text-sm text-muted text-pretty">
            Мы готовим материалы о мероприятиях и достижениях команды
          </p>
        </div>
      </div>
    </UContainer>
  </section>
</template>

<script setup lang="ts">
interface NewsPost {
  id: number | string
  title: string
  description?: string
  date?: string
  imageUrl?: string
  url?: string
}

const props = defineProps<{
  posts?: NewsPost[] | null
}>()

const displayPosts = computed(() => props.posts?.slice(0, 3) ?? [])
</script>
