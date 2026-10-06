// Счётчик Яндекс.Метрики подключаем только в продакшене, чтобы разработка не попадала в статистику
const YANDEX_METRIKA_ID = 113462586
const isProduction = process.env.NODE_ENV === 'production'
// Режим информационного киоска (kiosk.hr.admsr.ru, экран 1080×1920): отдельная сборка, см. docs/DESIGN-RULES.md §10
const isKiosk = process.env.KIOSK_MODE === 'true'

const yandexMetrikaScript = `(function(m,e,t,r,i,k,a){
  m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
  m[i].l=1*new Date();
  for (var j = 0; j < document.scripts.length; j++) {if (document.scripts[j].src === r) { return; }}
  k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)
})(window, document,'script','https://mc.yandex.ru/metrika/tag.js?id=${YANDEX_METRIKA_ID}', 'ym');

ym(${YANDEX_METRIKA_ID}, 'init', {ssr:true, webvisor:true, clickmap:true, ecommerce:"dataLayer", referrer: document.referrer, url: location.href, accurateTrackBounce:true, trackLinks:true});`

export default defineNuxtConfig({
  // Сборка киоска живёт в своих каталогах и не затирает обычную
  buildDir: isKiosk ? '.nuxt-kiosk' : '.nuxt',

  nitro: {
    preset: 'node-server',
    ...(isKiosk ? { output: { dir: '.output-kiosk', publicDir: '.output-kiosk/public' } } : {})
  },

  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL !== undefined
        ? process.env.NUXT_PUBLIC_API_BASE_URL
        : (process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000'),
      yandexMetrikaId: isProduction ? YANDEX_METRIKA_ID : 0,
      esiaFeedbackUrl: process.env.NUXT_PUBLIC_ESIA_FEEDBACK_URL || 'https://pos.gosuslugi.ru/landing/'
    }
  },

  modules: [
    '@nuxt/eslint',
    '@nuxt/image',
    '@nuxt/ui',
    '@nuxt/content',
    '@nuxt/fonts',
    '@nuxt/a11y'
  ],

  // Статика на nginx без Nitro/IPX — NuxtImg должен отдавать прямые URL
  image: {
    provider: 'none',
  },

  vite: {
    // Режим киоска для модулей данных вне контекста Nuxt (см. composables/useKiosk.ts)
    define: {
      __KIOSK__: JSON.stringify(isKiosk)
    },
    optimizeDeps: {
      include: [
        '@vue/devtools-core',
        '@vue/devtools-kit',
      ]
    }
  },

  fonts: {
    families: [
      { name: 'Inter', provider: 'google', weights: [400, 500, 600, 700] },
    ],
  },
  
  devtools: {
    enabled: true
  },

  // В киоске — тот же стиль, но с крупным масштабом и пересчитанными брейкпоинтами
  css: [isKiosk ? '~/assets/css/kiosk.css' : '~/assets/css/main.css'],

  // Киоск всегда светлый: переключатель темы там скрыт
  colorMode: isKiosk ? { preference: 'light', fallback: 'light', storageKey: 'nuxt-color-mode-kiosk' } : undefined,

  icon: {
    clientBundle: { sizeLimitKb: 1024 },
    customCollections: [{
      prefix: 'custom',
      dir: './public/Icons'
    }]
  },

  ui: {
    theme: {
      colors: [
        'primary',
        'neutral',
        'success',
        'warning',
        'error',
        'info',
      ],
    },
  },

  mdc: {
    highlight: {
      noApiRoute: false
    }
  },

  compatibilityDate: '2025-01-15',

  app: {
    head: {
      meta: [
        { name: 'viewport', content: isKiosk ? 'width=device-width, initial-scale=1, user-scalable=no' : 'width=device-width, initial-scale=1' },
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/logos/logoASR.svg' },
        { rel: 'apple-touch-icon', href: '/logos/logoASR.svg' },
      ],
      script: isProduction
        ? [{ key: 'yandex-metrika', type: 'text/javascript', innerHTML: yandexMetrikaScript }]
        : [],
      noscript: isProduction
        ? [{
            key: 'yandex-metrika-noscript',
            tagPosition: 'bodyOpen',
            innerHTML: `<div><img src="https://mc.yandex.ru/watch/${YANDEX_METRIKA_ID}" style="position:absolute; left:-9999px;" alt="" /></div>`,
          }]
        : [],
    },
  },

  eslint: {
    config: {
      stylistic: {
        commaDangle: 'never',
        braceStyle: '1tbs'
      }
    }
  }
  
})