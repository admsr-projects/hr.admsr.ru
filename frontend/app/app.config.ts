// Глобальные настройки Nuxt UI. Правила — в docs/DESIGN-RULES.md (дизайн SOFT):
// на месте эти значения не переопределять.
export default defineAppConfig({
  ui: {
    colors: {
      primary: 'emerald',
      secondary: 'neutral',
      neutral: 'zinc',
    },
    card: {
      slots: {
        root: 'rounded-xl shadow-none',
      },
      variants: {
        variant: {
          // Мягкая панель: серый фон без рамки и тени
          soft: {
            root: 'bg-elevated ring-0',
          },
          subtle: {
            root: 'bg-elevated ring-0',
          },
        },
      },
      defaultVariants: {
        variant: 'soft',
      },
    },
    input: {
      slots: {
        root: 'relative inline-flex items-center',
        base: 'rounded-lg ring-[var(--color-border-default)] bg-surface-raised text-text-primary',
      },
    },
    textarea: {
      slots: {
        base: 'rounded-lg ring-[var(--color-border-default)] bg-surface-raised text-text-primary',
      },
    },
    select: {
      slots: {
        base: 'rounded-lg',
      },
    },
    selectMenu: {
      slots: {
        base: 'rounded-lg',
      },
    },
    inputDate: {
      slots: {
        base: 'rounded-lg',
      },
    },
    formField: {
      slots: {
        label: 'text-text-primary font-medium',
        error: 'text-red-700 dark:text-red-300',
      },
    },
    container: {
      base: 'w-full max-w-(--ui-container) mx-auto px-4 sm:px-6 lg:px-8',
    },
    button: {
      slots: {
        base: 'rounded-md',
      },
    },
    badge: {
      slots: {
        base: 'rounded-md',
      },
      defaultVariants: {
        variant: 'soft',
      },
    },
    alert: {
      defaultVariants: {
        variant: 'soft',
      },
    },
    checkbox: {
      slots: {
        base: 'rounded-md',
      },
    },
    pagination: {
      slots: {
        root: 'pagination-controls',
      },
    },
  },
})
