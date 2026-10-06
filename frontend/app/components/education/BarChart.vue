<template>
  <div
    class="relative w-full"
    :style="{ height: `${height}px` }"
  >
    <canvas
      ref="canvas"
      role="img"
      :aria-label="ariaLabel"
    />
  </div>
</template>

<script setup lang="ts">
import type { Chart as ChartInstance } from 'chart.js'

export interface BarChartItem {
  key: string
  /** Подпись столбца */
  label: string
  count: number
  /** Имя CSS-переменной цвета, например `--ui-color-primary-500`; по умолчанию основной */
  colorVar?: string
  /** Заголовок подсказки, по умолчанию подпись */
  title?: string
  /** Дополнительная строка подсказки */
  note?: string
}

const props = withDefaults(defineProps<{
  items: BarChartItem[]
  /** Полосы идут слева направо, подписи — слева */
  horizontal?: boolean
  /** Выбранный столбец; остальные приглушаются */
  activeKey?: string
  /** Высота диаграммы, px; для горизонтальной по умолчанию зависит от числа полос */
  chartHeight?: number
}>(), {
  horizontal: false,
  activeKey: '',
  chartHeight: undefined,
})

const emit = defineEmits<{
  select: [key: string]
}>()

const canvas = ref<HTMLCanvasElement>()
const colorMode = useColorMode()

let chart: ChartInstance<'bar'> | undefined

const height = computed(() => props.chartHeight ?? (props.horizontal ? props.items.length * 30 + 48 : 288))

const ariaLabel = computed(() =>
  `Диаграмма: ${props.items.map(item => `${item.label} — ${item.count}`).join(', ')}`,
)

async function build() {
  const { Chart, BarController, BarElement, CategoryScale, LinearScale, Tooltip } = await import('chart.js')
  Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip)
  if (!canvas.value) return

  const colors = chartTheme()
  const font = chartFont
  const hasActive = !!props.activeKey

  chart?.destroy()
  chart = new Chart(canvas.value, {
    type: 'bar',
    data: {
      // Для вертикальных столбцов длинные подписи переносятся на несколько строк
      labels: props.items.map(item => props.horizontal ? item.label : wrapLabel(item.label, 12)),
      datasets: [{
        data: props.items.map(item => item.count),
        backgroundColor: props.items.map(item =>
          resolveCssColor(cssVar(item.colorVar ?? '--ui-color-primary-500'), hasActive && item.key !== props.activeKey ? 0.4 : 1),
        ),
        borderRadius: 6,
        maxBarThickness: props.horizontal ? 22 : 46,
      }],
    },
    options: {
      indexAxis: props.horizontal ? 'y' : 'x',
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: colors.tooltip,
          titleColor: colors.tooltipText,
          bodyColor: colors.tooltipText,
          titleFont: { ...font, weight: 'bold' },
          bodyFont: font,
          padding: 10,
          cornerRadius: 8,
          callbacks: {
            title: tooltipItems => {
              const item = props.items[tooltipItems[0]?.dataIndex ?? -1]
              return item?.title ?? item?.label ?? ''
            },
            label: tooltipItem => ` позиций: ${tooltipItem.raw}`,
            afterLabel: tooltipItem => wrapLabel(props.items[tooltipItem.dataIndex]?.note ?? '', 60).join('\n'),
          },
        },
      },
      scales: {
        [props.horizontal ? 'x' : 'y']: {
          beginAtZero: true,
          ticks: { color: colors.muted, precision: 0, font },
          grid: { color: colors.grid },
          border: { display: false },
        },
        [props.horizontal ? 'y' : 'x']: {
          ticks: { color: colors.text, font, autoSkip: false, maxRotation: 0 },
          grid: { display: false },
          border: { display: false },
        },
      },
      onClick: (_event, elements) => {
        const element = elements[0]
        if (element) emit('select', props.items[element.index]?.key ?? '')
      },
      // Курсор-рука показывает, что столбец можно нажать
      onHover: (event, elements) => {
        const target = event.native?.target as HTMLElement | undefined
        if (target) target.style.cursor = elements.length ? 'pointer' : 'default'
      },
    },
  })
}

onMounted(build)

watch(() => [props.items, props.activeKey, props.horizontal], build, { deep: true })
watch(() => colorMode.value, () => nextTick(build))

onBeforeUnmount(() => {
  chart?.destroy()
})
</script>
