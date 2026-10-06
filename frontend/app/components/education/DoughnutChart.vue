<template>
  <div class="relative h-72 w-full">
    <canvas
      ref="canvas"
      role="img"
      :aria-label="ariaLabel"
    />
  </div>
</template>

<script setup lang="ts">
import type { Chart as ChartInstance } from 'chart.js'

export interface DoughnutItem {
  key: string
  /** Подпись в легенде */
  label: string
  /** Полное название для подсказки */
  title?: string
  count: number
  /** Имя CSS-переменной цвета, например `--color-indigo-500` */
  colorVar: string
}

const props = defineProps<{
  items: DoughnutItem[]
}>()

const emit = defineEmits<{
  select: [key: string]
}>()

const canvas = ref<HTMLCanvasElement>()
const colorMode = useColorMode()

let chart: ChartInstance<'doughnut'> | undefined

const ariaLabel = computed(() =>
  `Круговая диаграмма: ${props.items.map(item => `${item.label} — ${item.count}`).join(', ')}`,
)

function legendPosition() {
  return (canvas.value?.parentElement?.clientWidth ?? 0) < 480 ? 'bottom' : 'right'
}

function build() {
  return (async () => {
    const { Chart, ArcElement, DoughnutController, Legend, Tooltip } = await import('chart.js')
    Chart.register(ArcElement, DoughnutController, Legend, Tooltip)
    if (!canvas.value) return

    const colors = chartTheme()
    const font = chartFont

    chart?.destroy()
    chart = new Chart(canvas.value, {
      type: 'doughnut',
      data: {
        labels: props.items.map(item => item.label),
        datasets: [{
          data: props.items.map(item => item.count),
          backgroundColor: props.items.map(item => resolveCssColor(cssVar(item.colorVar))),
          borderColor: colors.surface,
          borderWidth: 2,
        }],
      },
      options: {
        maintainAspectRatio: false,
        cutout: '58%',
        plugins: {
          legend: {
            position: legendPosition(),
            labels: { color: colors.text, boxWidth: 12, padding: 10, font },
            // Нажатие на пункт легенды включает фильтр по категории, а не скрывает сегмент
            onClick: (_event, legendItem) => emit('select', props.items[legendItem.index ?? -1]?.key ?? ''),
          },
          tooltip: {
            backgroundColor: colors.tooltip,
            titleColor: colors.tooltipText,
            bodyColor: colors.tooltipText,
            titleFont: { ...font, weight: 'bold' },
            bodyFont: font,
            padding: 10,
            cornerRadius: 8,
            callbacks: {
              title: items => props.items[items[0]?.dataIndex ?? -1]?.title ?? '',
              label: item => ` позиций: ${item.raw}`,
            },
          },
        },
        onClick: (_event, elements) => {
          const element = elements[0]
          if (element) emit('select', props.items[element.index]?.key ?? '')
        },
        onResize: (instance) => {
          const position = legendPosition()
          if (instance.options.plugins!.legend!.position !== position) {
            instance.options.plugins!.legend!.position = position
            instance.update()
          }
        },
      },
    })
  })()
}

onMounted(build)

// Данные и тема меняются без пересоздания холста лишь частично, поэтому диаграмму собираем заново
watch(() => props.items, build, { deep: true })
watch(() => colorMode.value, () => nextTick(build))

onBeforeUnmount(() => {
  chart?.destroy()
})
</script>
