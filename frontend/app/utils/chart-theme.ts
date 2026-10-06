// Общие помощники диаграмм Chart.js (только в браузере)

let probe: HTMLCanvasElement | undefined

/** Canvas и Chart.js не понимают современные цветовые форматы (oklch): приводим цвет к rgb через пиксель холста */
export function resolveCssColor(value: string, alpha = 1) {
  probe ??= document.createElement('canvas')
  const context = probe.getContext('2d', { willReadFrequently: true })
  if (!context) return value
  probe.width = probe.height = 1
  context.clearRect(0, 0, 1, 1)
  context.fillStyle = value
  context.fillRect(0, 0, 1, 1)
  const [r, g, b] = context.getImageData(0, 0, 1, 1).data
  return alpha < 1 ? `rgba(${r}, ${g}, ${b}, ${alpha})` : `rgb(${r}, ${g}, ${b})`
}

export function cssVar(name: string) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}

/** Цвета текущей темы (светлой или тёмной) для текста, сетки и подсказок */
export function chartTheme() {
  return {
    text: resolveCssColor(cssVar('--ui-text-highlighted') || '#18181b'),
    muted: resolveCssColor(cssVar('--ui-text-muted') || '#71717a'),
    grid: resolveCssColor(cssVar('--ui-border') || '#e4e4e7'),
    surface: resolveCssColor(cssVar('--ui-bg-elevated') || '#f4f4f5'),
    tooltip: resolveCssColor(cssVar('--ui-bg-inverted') || '#18181b'),
    tooltipText: resolveCssColor(cssVar('--ui-text-inverted') || '#ffffff'),
  }
}

export const chartFont = { family: 'Inter, system-ui, sans-serif', size: 12 }

/** Перенос подписи по словам на строки не длиннее `max` символов */
export function wrapLabel(text: string, max: number): string[] {
  const lines: string[] = []
  let current = ''
  for (const word of text.split(' ')) {
    if (current && `${current} ${word}`.length > max) {
      lines.push(current)
      current = word
    }
    else {
      current = current ? `${current} ${word}` : word
    }
  }
  if (current) lines.push(current)
  return lines
}
