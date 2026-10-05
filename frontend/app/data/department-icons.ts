/** Иконки (Lucide) органов администрации по адресу страницы органа — для карточек на странице структуры */
const departmentIcons: Record<string, string> = {
  'dep-vnutrenney-politiki': 'i-lucide-megaphone',
  'yuridicheskiy-komitet': 'i-lucide-scale',
  'uo-it-cifra': 'i-lucide-cpu',
  'uo-municipal-sluzhba': 'i-lucide-id-card',
  'uo-organizacii-deyatelnosti': 'i-lucide-clipboard-list',
  'dep-municipal-imushchestvo': 'i-lucide-key-round',
  'dep-stroitelstvo-zemlya': 'i-lucide-hard-hat',
  'dep-zhkh-ekologiya': 'i-lucide-leaf',
  'uo-investicii-predprinimatelstvo': 'i-lucide-trending-up',
  'dep-obrazovaniya': 'i-lucide-graduation-cap',
  'uo-molodezhnaya-politika': 'i-lucide-users-round',
  'uo-kultury': 'i-lucide-drama',
  'uo-fizkultury-sport': 'i-lucide-dumbbell',
  'otdel-komissii-nesovershennoletnih': 'i-lucide-shield-check',
  'dep-finansov': 'i-lucide-wallet',
  'dep-ekonomicheskogo-razvitiya': 'i-lucide-chart-line',
  'uo-finansovyy-kontrol': 'i-lucide-search-check',
  'otdel-buhgalterii': 'i-lucide-calculator',
  'dep-obschestvennoy-bezopasnosti': 'i-lucide-shield-alert',
  'uo-go-chs': 'i-lucide-siren',
  'otdel-zags': 'i-lucide-heart-handshake',
  'specsluzhba': 'i-lucide-lock'
}

export const defaultDepartmentIcon = 'i-lucide-building-2'

export function departmentIcon(slug: string): string {
  return departmentIcons[slug] ?? defaultDepartmentIcon
}
