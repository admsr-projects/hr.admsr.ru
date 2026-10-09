declare const __KIOSK__: boolean

/**
 * Режим информационного киоска (kiosk-hr.admsr.ru, экран 1080×1920).
 * Включается при сборке (KIOSK_MODE=true, см. nuxt.config.ts), в режиме киоска нет форм и ввода с клавиатуры.
 */
export const IS_KIOSK: boolean = typeof __KIOSK__ !== 'undefined' && __KIOSK__

export function useKiosk() {
  return IS_KIOSK
}
