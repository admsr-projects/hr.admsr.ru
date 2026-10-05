/**
 * Режим крупного шрифта (версия для слабовидящих, до 200%) увеличивает размер корневого шрифта,
 * но media-query `lg:` по-прежнему считает ширину окна в «обычных» пикселях. Поэтому на широком экране
 * вёрстка оставалась десктопной, а текст не помещался. Здесь считаем «эффективную» ширину
 * (ширина окна ÷ масштаб шрифта) и, если она меньше 1024px, ставим на <html> атрибут data-compact:
 * по нему a11y-overrides.css включает мобильную раскладку (меню-бургер, меню раздела полосой).
 */
export default defineNuxtPlugin(() => {
  const root = document.documentElement

  function update() {
    const rootPx = Number.parseFloat(getComputedStyle(root).fontSize) || 16
    const effectiveWidth = window.innerWidth / (rootPx / 16)
    root.toggleAttribute('data-compact', window.innerWidth >= 1024 && effectiveWidth < 1024)
  }

  update()
  window.addEventListener('resize', update)
  new MutationObserver(update).observe(root, { attributes: true, attributeFilter: ['class', 'style'] })
})
