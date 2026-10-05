<template>
  <div class="ds-inner">
    <DsBreadcrumbs :items="breadcrumbs" />

    <div class="ds-container pb-12 lg:pb-16">
      <article
        class="mx-auto flex max-w-3xl flex-col gap-4"
        :aria-busy="pending"
      >
        <template v-if="pending">
          <USkeleton class="h-4 w-28" />
          <USkeleton class="h-10 w-full" />
          <USkeleton class="h-10 w-3/4" />
          <USkeleton class="aspect-video w-full rounded-lg" />
          <USkeleton class="h-5 w-full" />
          <USkeleton class="h-5 w-11/12" />
        </template>

        <template v-else-if="post">
          <time
            v-if="post.date"
            :datetime="post.date"
            class="text-sm text-text-muted"
          >
            {{ formatDate(post.date) }}
          </time>

          <h1 class="text-h1 text-text-primary text-balance">
            {{ post.title }}
          </h1>

          <p
            v-if="post.description"
            class="text-xl leading-8 text-text-muted text-pretty"
          >
            {{ post.description }}
          </p>

          <DsBlurredImage
            v-if="post.imageUrl"
            :src="post.imageUrl"
            :alt="post.title"
            loading="eager"
            class="rounded-lg"
          />

          <div
            v-if="contentParagraphs.length"
            class="flex flex-col gap-4"
          >
            <p
              v-for="(paragraph, index) in contentParagraphs"
              :key="index"
              class="whitespace-pre-line text-lg leading-8 text-text-primary text-pretty"
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

        <DsEmptyState
          v-else
          icon="i-lucide-search-x"
          title="Новость не найдена"
          description="Материал снят с публикации или адрес указан неверно."
        />
      </article>

      <section
        v-if="!pending && relatedPosts.length"
        aria-labelledby="news-related"
        class="mt-12"
      >
        <h2
          id="news-related"
          class="mb-4 text-xl font-bold text-text-primary"
        >
          Ещё новости
        </h2>

        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <NewsCard
            v-for="item in relatedPosts"
            :key="item.id"
            :post="item"
          />
        </div>
      </section>
    </div>
  </div>
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

const breadcrumbs = computed(() => [
  { label: 'Главная', to: '/', icon: 'i-lucide-home' },
  { label: 'Новости', to: '/#news' },
  { label: post.value?.title ?? 'Новость' },
])

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
