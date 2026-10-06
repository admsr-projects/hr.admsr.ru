<template>
  <NuxtLink
    :to="to"
    class="group flex h-full flex-col overflow-hidden rounded-xl bg-elevated transition-colors duration-200 hover:bg-accented motion-reduce:transition-none"
  >
    <DsBlurredImage
      :src="post.imageUrl"
      :alt="post.title"
      :loading="eager ? 'eager' : 'lazy'"
    />
    <div class="flex flex-1 flex-col gap-2 p-6">
      <time
        v-if="post.date"
        :datetime="post.date"
        class="text-sm text-text-muted"
      >
        {{ formatNewsDate(post.date) }}
      </time>
      <h3 class="text-lg font-semibold leading-snug text-text-primary line-clamp-2 group-hover:text-primary">
        {{ post.title }}
      </h3>
      <p
        v-if="post.description"
        class="text-sm text-text-muted line-clamp-3"
      >
        {{ post.description }}
      </p>
      <span class="mt-auto flex items-center gap-1 pt-2 text-sm font-medium text-primary">
        Читать
        <UIcon
          name="i-lucide-arrow-right"
          class="size-4 transition-transform duration-200 group-hover:translate-x-0.5"
          aria-hidden="true"
        />
      </span>
    </div>
  </NuxtLink>
</template>

<script setup lang="ts">
export interface NewsCardPost {
  id: number | string
  title: string
  description?: string
  date?: string
  imageUrl?: string
  url?: string
}

const props = defineProps<{
  post: NewsCardPost
  eager?: boolean
}>()

const to = computed(() => props.post.url ?? `/news/${props.post.id}`)

function formatNewsDate(value: string) {
  try {
    return new Intl.DateTimeFormat('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' }).format(new Date(value))
  } catch {
    return value
  }
}
</script>
