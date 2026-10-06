<template>
  <!-- Баннер «Госуслуги. Решаем вместе» (платформа обратной связи ПОС). Код и оформление — официальные, менять только тексты -->
  <div
    id="js-show-iframe-wrapper"
    class="overflow-hidden rounded-xl"
  >
    <div class="pos-banner-fluid bf-2">
      <div class="bf-2__decor">
        <div class="bf-2__logo-wrap">
          <img
            class="bf-2__logo"
            src="https://pos.gosuslugi.ru/bin/banner-fluid/gosuslugi-logo.svg"
            alt="Госуслуги"
          >
          <div class="bf-2__slogan">
            Решаем вместе
          </div>
        </div>
      </div>
      <div class="bf-2__content">
        <div class="bf-2__description">
          <span class="bf-2__text">
            {{ title }}
          </span>
          <span class="bf-2__text bf-2__text_small">
            {{ text }}
          </span>
        </div>

        <div class="bf-2__btn-wrap">
          <!-- pos-banner-btn_2 не удалять; другие классы не добавлять. Надпись кнопки подставляет скрипт Госуслуг -->
          <button
            class="pos-banner-btn_2"
            type="button"
          >
            Сообщить о проблеме
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  title?: string
  text?: string
}>(), {
  title: 'Знаете о фактах коррупции?',
  text: 'Сообщите о правонарушении через портал Госуслуг'
})

declare global {
  interface Window {
    Widget?: (url: string, id: number) => void
  }
}

const POS_SCRIPT = 'https://pos.gosuslugi.ru/bin/script.min.js'
const POS_FORM = 'https://pos.gosuslugi.ru/form'
const POS_FORM_ID = 811
const CSS_PREFIX = '--pos-banner-fluid-2__'

const initial: Record<string, string> = {
  'grid-template-columns': '100%',
  'grid-template-rows': '310px auto',
  'decor-grid-column': 'initial',
  'decor-grid-row': 'initial',
  'decor-padding': '30px 30px 0 30px',
  'bg-url': 'url(\'https://pos.gosuslugi.ru/bin/banner-fluid/2/banner-fluid-bg-2-small.svg\')',
  'bg-position': 'calc(10% + 64px) calc(100% - 20px)',
  'bg-size': 'cover',
  'content-padding': '0 30px 30px 30px',
  'slogan-font-size': '20px',
  'slogan-line-height': '32px',
  'logo-wrap-padding': '20px 30px 30px 40px',
  'logo-wrap-top': '0',
  'logo-wrap-bottom': 'initial',
  'logo-wrap-border-radius': '0 0 0 80px'
}

/** Адаптивные размеры баннера по ширине контейнера — как в оригинальном коде ПОС */
function layoutBanner() {
  const root = document.documentElement
  const wrapper = document.getElementById('js-show-iframe-wrapper')
  const width = wrapper ? wrapper.offsetWidth : document.body.offsetWidth
  const o = { ...initial }

  if (width > 405) {
    o['slogan-font-size'] = '24px'
    o['logo-wrap-padding'] = '30px 50px 30px 70px'
  }
  if (width > 500) {
    o['grid-template-columns'] = 'min-content 1fr'
    o['grid-template-rows'] = '100%'
    o['decor-grid-column'] = '2'
    o['decor-grid-row'] = '1'
    o['decor-padding'] = '30px 30px 30px 0'
    o['content-padding'] = '30px'
    o['bg-position'] = '0% calc(100% - 70px)'
    o['logo-wrap-padding'] = '30px 30px 24px 40px'
    o['logo-wrap-top'] = 'initial'
    o['logo-wrap-bottom'] = '0'
    o['logo-wrap-border-radius'] = '80px 0 0 0'
  }
  if (width > 585) o['bg-position'] = '0% calc(100% - 6px)'
  if (width > 800) {
    o['bg-url'] = 'url(\'https://pos.gosuslugi.ru/bin/banner-fluid/2/banner-fluid-bg-2.svg\')'
    o['bg-position'] = '0% center'
  }
  if (width > 1020) {
    o['slogan-font-size'] = '32px'
    o['logo-wrap-padding'] = '30px 30px 24px 50px'
  }

  Object.entries(o).forEach(([key, value]) => root.style.setProperty(CSS_PREFIX + key, value))
}

function loadScript(): Promise<void> {
  if (window.Widget) return Promise.resolve()
  return new Promise((resolve, reject) => {
    const existing = document.querySelector<HTMLScriptElement>(`script[src="${POS_SCRIPT}"]`)
    const script = existing ?? document.createElement('script')
    script.addEventListener('load', () => resolve(), { once: true })
    script.addEventListener('error', () => reject(new Error('Не удалось загрузить скрипт Госуслуг')), { once: true })
    if (!existing) {
      script.src = POS_SCRIPT
      document.head.appendChild(script)
    }
  })
}

onMounted(async () => {
  layoutBanner()
  window.addEventListener('resize', layoutBanner)
  try {
    await loadScript()
    window.Widget?.(POS_FORM, POS_FORM_ID)
  } catch {
    // Скрипт Госуслуг недоступен — баннер остаётся без действия, остальная страница работает
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', layoutBanner)
  const root = document.documentElement
  Object.keys(initial).forEach(key => root.style.removeProperty(CSS_PREFIX + key))
})
</script>

<style>
@font-face{font-family:LatoWeb;src:url(https://pos.gosuslugi.ru/bin/fonts/Lato/fonts/Lato-Regular.woff2) format("woff2"),url(https://pos.gosuslugi.ru/bin/fonts/Lato/fonts/Lato-Regular.woff) format("woff"),url(https://pos.gosuslugi.ru/bin/fonts/Lato/fonts/Lato-Regular.ttf) format("truetype");font-style:normal;font-weight:400;font-display:swap}
@font-face{font-family:LatoWebBold;src:url(https://pos.gosuslugi.ru/bin/fonts/Lato/fonts/Lato-Bold.woff2) format("woff2"),url(https://pos.gosuslugi.ru/bin/fonts/Lato/fonts/Lato-Bold.woff) format("woff"),url(https://pos.gosuslugi.ru/bin/fonts/Lato/fonts/Lato-Bold.ttf) format("truetype");font-style:normal;font-weight:400;font-display:swap}

#js-show-iframe-wrapper{position:relative;display:flex;align-items:center;justify-content:center;width:100%;min-width:293px;max-width:100%;background:linear-gradient(138.4deg,#38bafe 26.49%,#2d73bc 79.45%);color:#fff;cursor:pointer}
#js-show-iframe-wrapper .pos-banner-fluid *{box-sizing:border-box}
#js-show-iframe-wrapper .pos-banner-fluid .pos-banner-btn_2{display:block;width:240px;min-height:56px;font-size:18px;line-height:24px;cursor:pointer;background:#0d4cd3;color:#fff;border:none;border-radius:8px;outline:0}
#js-show-iframe-wrapper .pos-banner-fluid .pos-banner-btn_2:hover{background:#1d5deb}
#js-show-iframe-wrapper .pos-banner-fluid .pos-banner-btn_2:focus{background:#2a63ad}
#js-show-iframe-wrapper .pos-banner-fluid .pos-banner-btn_2:focus-visible{outline:2px solid #fff;outline-offset:2px}
#js-show-iframe-wrapper .pos-banner-fluid .pos-banner-btn_2:active{background:#2a63ad}
#js-show-iframe-wrapper .bf-2{position:relative;display:grid;grid-template-columns:var(--pos-banner-fluid-2__grid-template-columns);grid-template-rows:var(--pos-banner-fluid-2__grid-template-rows);width:100%;max-width:1060px;font-family:LatoWeb,sans-serif;box-sizing:border-box}
#js-show-iframe-wrapper .bf-2__decor{grid-column:var(--pos-banner-fluid-2__decor-grid-column);grid-row:var(--pos-banner-fluid-2__decor-grid-row);padding:var(--pos-banner-fluid-2__decor-padding);background:var(--pos-banner-fluid-2__bg-url) var(--pos-banner-fluid-2__bg-position) no-repeat;background-size:var(--pos-banner-fluid-2__bg-size)}
#js-show-iframe-wrapper .bf-2__logo-wrap{position:absolute;top:var(--pos-banner-fluid-2__logo-wrap-top);bottom:var(--pos-banner-fluid-2__logo-wrap-bottom);right:0;display:flex;flex-direction:column;align-items:flex-end;padding:var(--pos-banner-fluid-2__logo-wrap-padding);background:#2d73bc;border-radius:var(--pos-banner-fluid-2__logo-wrap-border-radius)}
#js-show-iframe-wrapper .bf-2__logo{width:128px}
#js-show-iframe-wrapper .bf-2__slogan{font-family:LatoWebBold,sans-serif;font-size:var(--pos-banner-fluid-2__slogan-font-size);line-height:var(--pos-banner-fluid-2__slogan-line-height);color:#fff}
#js-show-iframe-wrapper .bf-2__content{padding:var(--pos-banner-fluid-2__content-padding)}
#js-show-iframe-wrapper .bf-2__description{display:flex;flex-direction:column;margin-bottom:24px}
#js-show-iframe-wrapper .bf-2__text{margin-bottom:12px;font-size:24px;line-height:32px;font-family:LatoWebBold,sans-serif;color:#fff}
#js-show-iframe-wrapper .bf-2__text_small{margin-bottom:0;font-size:16px;line-height:24px;font-family:LatoWeb,sans-serif}
#js-show-iframe-wrapper .bf-2__btn-wrap{display:flex;align-items:center;justify-content:center}
</style>
