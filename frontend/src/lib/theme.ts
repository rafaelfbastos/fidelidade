import type { CompanyMembership } from '@/types/auth'

export interface ThemeOverrides {
  primaryColor?: string
  secondaryColor?: string
  accentColor?: string
  backgroundColor?: string
  textColor?: string
}

const hexToHsl = (hex?: string | null) => {
  if (!hex) return null
  let sanitized = hex.replace('#', '')
  if (sanitized.length === 3) {
    sanitized = sanitized
      .split('')
      .map((char) => char + char)
      .join('')
  }
  if (sanitized.length !== 6) return null
  const bigint = Number.parseInt(sanitized, 16)
  const r = ((bigint >> 16) & 255) / 255
  const g = ((bigint >> 8) & 255) / 255
  const b = (bigint & 255) / 255

  const max = Math.max(r, g, b)
  const min = Math.min(r, g, b)
  let h = 0
  let s = 0
  const l = (max + min) / 2

  if (max !== min) {
    const d = max - min
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min)
    switch (max) {
      case r:
        h = (g - b) / d + (g < b ? 6 : 0)
        break
      case g:
        h = (b - r) / d + 2
        break
      case b:
        h = (r - g) / d + 4
        break
    }
    h /= 6
  }

  return `${Math.round(h * 360)} ${Math.round(s * 100)}% ${Math.round(l * 100)}%`
}

const setCssVar = (name: string, value: string | null) => {
  if (!value) return
  document.documentElement.style.setProperty(name, value)
}

export const applyThemeFromCompany = (company?: CompanyMembership | null, mode: 'light' | 'dark' = 'light') => {
  if (!company?.theme) return
  const theme = company.theme
  const primaryBackground = theme.background?.primary
  const secondaryBackground = theme.background?.secondary
  const background = mode === 'dark' ? primaryBackground ?? secondaryBackground : secondaryBackground ?? primaryBackground
  const text = mode === 'dark' ? theme.text?.secondary ?? theme.text?.primary : theme.text?.primary

  setCssVar('--primary', hexToHsl(theme.colors?.primary) ?? '0 0% 9%')
  setCssVar('--secondary', hexToHsl(theme.colors?.secondary) ?? '0 0% 96%')
  setCssVar('--accent', hexToHsl(theme.colors?.accent) ?? '0 0% 96%')
  setCssVar('--destructive', hexToHsl(theme.colors?.error) ?? '0 84% 60%')
  setCssVar('--muted', hexToHsl(theme.background?.secondary) ?? '0 0% 96%')
  setCssVar('--border', hexToHsl(theme.background?.card) ?? '0 0% 89%')
  setCssVar('--input', hexToHsl(theme.background?.card) ?? '0 0% 89%')
  setCssVar('--ring', hexToHsl(theme.colors?.primary) ?? '0 0% 9%')
  setCssVar('--background', hexToHsl(background) ?? '0 0% 100%')
  setCssVar('--foreground', hexToHsl(text) ?? '0 0% 3.9%')
  setCssVar('--card', hexToHsl(theme.background?.card) ?? '0 0% 100%')
  setCssVar('--card-foreground', hexToHsl(text) ?? '0 0% 3.9%')
}

export const applyCustomTheme = (overrides: ThemeOverrides) => {
  if (overrides.primaryColor) setCssVar('--primary', hexToHsl(overrides.primaryColor))
  if (overrides.secondaryColor) setCssVar('--secondary', hexToHsl(overrides.secondaryColor))
  if (overrides.accentColor) setCssVar('--accent', hexToHsl(overrides.accentColor))
  if (overrides.backgroundColor) {
    const converted = hexToHsl(overrides.backgroundColor)
    setCssVar('--background', converted)
    setCssVar('--card', converted)
  }
  if (overrides.textColor) {
    const converted = hexToHsl(overrides.textColor)
    setCssVar('--foreground', converted)
    setCssVar('--card-foreground', converted)
  }
}

export const resetThemeToDefault = () => {
  document.documentElement.removeAttribute('style')
}
