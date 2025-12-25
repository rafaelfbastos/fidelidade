export interface CompanyThemeLogos {
  light?: string
  dark?: string
  favicon?: string
}

export interface CompanyThemeColors {
  primary?: string
  secondary?: string
  accent?: string
  success?: string
  warning?: string
  error?: string
}

export interface CompanyThemeText {
  primary?: string
  secondary?: string
}

export interface CompanyThemeBackground {
  primary?: string
  secondary?: string
  card?: string
}

export interface CompanyTheme {
  uuid: string
  logos: CompanyThemeLogos
  colors: CompanyThemeColors
  text: CompanyThemeText
  background: CompanyThemeBackground
  custom_css?: string
  extra_config?: Record<string, unknown>
  is_active: boolean
}

export interface Company {
  uuid: string
  trade_name: string
  legal_name: string
  cnpj: string
  email: string
  phone: string
  logo?: string
  points_per_real: string
  is_active: boolean
}

export interface CompanyMembership {
  uuid: string
  role: string
  role_display: string
  is_active: boolean
  created_at: string
  company: Company
  theme?: CompanyTheme
}

export interface AuthUser {
  id: number
  email: string
  first_name: string
  last_name: string
  full_name: string
  phone: string
  is_active: boolean
  date_joined: string
  avatar?: string
  companies: CompanyMembership[]
}

export interface LoginResponse {
  access: string
  refresh: string
  user: AuthUser
}
