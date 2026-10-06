import { Marked } from 'marked'

/**
 * Markdown из админки (новости, мероприятия) → безопасный HTML.
 * Сырой HTML в тексте экранируется, картинки не выводятся, ссылки — только http(s), mailto, tel и внутренние.
 */
function escapeHtml(value: string) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function safeUrl(href: string) {
  const url = href.trim()
  return /^(https?:|mailto:|tel:|\/|#)/i.test(url) ? url : null
}

const marked = new Marked({
  gfm: true,
  // Одинарный перенос строки остаётся переносом: так выглядели старые тексты без разметки
  breaks: true,
  renderer: {
    html({ text }) {
      return escapeHtml(text)
    },
    image({ text }) {
      return escapeHtml(text)
    },
    heading({ tokens, depth }) {
      // Заголовок страницы уже h1, поэтому «#» в тексте становится h2
      const level = Math.min(depth + 1, 4)
      return `<h${level}>${this.parser.parseInline(tokens)}</h${level}>\n`
    },
    link({ href, title, tokens }) {
      const text = this.parser.parseInline(tokens)
      const safe = safeUrl(href)
      if (!safe) return text
      const external = /^https?:/i.test(safe)
      const titleAttr = title ? ` title="${escapeHtml(title)}"` : ''
      const targetAttr = external ? ' target="_blank" rel="noopener noreferrer"' : ''
      return `<a href="${escapeHtml(safe)}"${titleAttr}${targetAttr}>${text}</a>`
    },
  },
})

export function renderMarkdown(source?: string | null): string {
  const text = source?.trim()
  if (!text) return ''
  return marked.parse(text, { async: false })
}

/** Текст без разметки — для коротких анонсов в таблицах и карточках. */
export function markdownToPlain(source?: string | null): string {
  if (!source) return ''
  return source
    .replace(/!\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
    .replace(/^\s{0,3}(#{1,6}|>|[-*+]|\d+\.)\s+/gm, '')
    .replace(/(\*\*|\*|`|~~)/g, '')
    .replace(/\s*\n+\s*/g, ' ')
    .trim()
}
