/**
 * Компоненты Reka UI (select, checkbox, radio) добавляют в DOM служебные скрытые <input data-hidden>
 * для отправки формы. Они без подписи и могут озвучиваться программами экранного доступа как
 * «поле без названия». Скрываем их от вспомогательных технологий (на работу форм это не влияет).
 */
export default defineNuxtPlugin(() => {
  function hide(root: ParentNode) {
    root.querySelectorAll<HTMLInputElement>('input[data-hidden]:not([aria-hidden])').forEach((input) => {
      input.setAttribute('aria-hidden', 'true')
    })
  }

  hide(document)
  new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      mutation.addedNodes.forEach((node) => {
        if (node instanceof HTMLElement) hide(node.matches('input[data-hidden]') ? node.parentElement ?? node : node)
      })
    }
  }).observe(document.body, { childList: true, subtree: true })
})
