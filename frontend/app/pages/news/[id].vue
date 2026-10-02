<template>
  <DsStandardPage
    :title="pending ? 'Загрузка новости…' : post?.title ?? 'Новость'"
    :description="post?.description"
  >
    <div
      v-if="pending"
      class="max-w-3xl space-y-3"
      aria-busy="true"
      aria-label="Загрузка новости"
    >
      <USkeleton class="h-5 w-28" />
      <USkeleton class="h-64 w-full rounded-lg" />
      <USkeleton class="h-5 w-full" />
      <USkeleton class="h-5 w-11/12" />
      <USkeleton class="h-5 w-4/5" />
    </div>

    <template v-else>
      <time
        v-if="post?.date"
        :datetime="post.date"
        class="text-sm text-text-muted"
      >
        {{ formatDate(post.date) }}
      </time>

      <figure
        v-if="post?.imageUrl"
        class="w-full max-w-4xl overflow-hidden rounded-lg border border-default bg-elevated"
      >
        <img
          :src="post.imageUrl"
          :alt="post.title"
          loading="eager"
          class="block h-auto w-full"
        >
      </figure>

      <div
        v-if="contentParagraphs.length"
        class="max-w-3xl space-y-4"
      >
        <p
          v-for="(paragraph, index) in contentParagraphs"
          :key="index"
          class="whitespace-pre-line text-pretty text-base leading-6 text-text-muted"
        >
          {{ paragraph }}
        </p>
      </div>

      <DsEmptyState
        v-else
        icon="i-lucide-file-text"
        title="Полный текст готовится"
        description="Мы опубликуем материал в ближайшее время."
      />
    </template>

    <section
      v-if="!pending && relatedPosts.length"
      aria-labelledby="news-related"
      class="pt-4"
    >
      <h2
        id="news-related"
        class="mb-4 text-xl font-bold text-text-primary"
      >
        Ещё новости
      </h2>

      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <NuxtLink
          v-for="(item, index) in relatedPosts"
          :key="item.id"
          :to="`/news/${item.id}`"
          class="group flex h-full flex-col overflow-hidden rounded-lg border border-default bg-default transition-colors duration-200 hover:border-primary/40 motion-reduce:transition-none"
        >
          <img
            v-if="item.imageUrl"
            :src="item.imageUrl"
            :alt="item.title"
            class="block h-auto w-full"
            :loading="index === 0 ? 'eager' : 'lazy'"
          >

          <div class="flex flex-1 flex-col gap-1 p-6">
            <time
              v-if="item.date"
              :datetime="item.date"
              class="text-sm text-text-muted"
            >
              {{ formatDate(item.date) }}
            </time>
            <h3 class="text-base font-semibold leading-6 text-text-primary line-clamp-2 group-hover:text-primary">
              {{ item.title }}
            </h3>
            <p
              v-if="item.description"
              class="text-sm leading-5 text-text-muted line-clamp-2"
            >
              {{ item.description }}
            </p>
          </div>
        </NuxtLink>
      </div>
    </section>
  </DsStandardPage>
</template>

<script setup lang="ts">
interface NewsPost {
  id: number | string
  title: string
  description?: string
  content?: string
  date?: string
  imageUrl?: string
}

const config = useRuntimeConfig()
const route = useRoute()

const postId = computed(() => String(route.params.id ?? ''))

const { data: post, pending } = await useAsyncData(
  () => `news-post-${postId.value}`,
  () => $fetch<NewsPost>(`${config.public.apiBaseUrl}/api/news/${postId.value}/`),
  { server: false },
)

useHead(() => ({
  title: post.value?.title ?? 'Новость',
  meta: post.value?.description
    ? [{ name: 'description', content: post.value.description }]
    : [],
}))

const { data: list } = await useAsyncData(
  'news-posts-related',
  () => $fetch<NewsPost[]>(`${config.public.apiBaseUrl}/api/news/`),
  { server: false },
)

const relatedPosts = computed(() =>
  (list.value ?? [])
    .filter(item => String(item.id) !== postId.value)
    .slice(0, 3),
)

const contentParagraphs = computed(() => {
  const raw = post.value?.content?.trim()
  if (!raw) return []
  return raw
    .split(/\n{2,}/g)
    .map(p => p.trim())
    .filter(Boolean)
})

function formatDate(value: string) {
  try {
    return new Intl.DateTimeFormat('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    }).format(new Date(value))
  } catch {
    return value
  }
}
</script>
