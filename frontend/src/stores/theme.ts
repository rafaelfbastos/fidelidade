import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import api from '@/lib/http'
import type { CompanyTheme } from '@/types/auth'
import { useAuthStore } from './auth'

export interface ThemeFormValues {
  logoMode: 'upload' | 'url'
  logoUrl: string
  logoFile: File | null
  primaryColor: string
  secondaryColor: string
  accentColor: string
  successColor: string
  warningColor: string
  errorColor: string
  textPrimary: string
  textSecondary: string
  backgroundPrimary: string
  backgroundSecondary: string
  backgroundCard: string
}

const FALLBACK_FORM: ThemeFormValues = {
  logoMode: 'upload',
  logoUrl: '',
  logoFile: null,
  primaryColor: '#2563eb',
  secondaryColor: '#4338ca',
  accentColor: '#4c1d95',
  successColor: '#16a34a',
  warningColor: '#facc15',
  errorColor: '#dc2626',
  textPrimary: '#0f172a',
  textSecondary: '#475569',
  backgroundPrimary: '#f4f6fb',
  backgroundSecondary: '#eef2ff',
  backgroundCard: '#ffffff',
}

const buildFormFromTheme = (theme?: CompanyTheme | null, fallbackLogo?: string): ThemeFormValues => {
  const currentOverride = theme?.extra_config?.logo_url_override as string | undefined
  return {
    logoMode: currentOverride ? 'url' : 'upload',
    logoUrl: currentOverride ?? theme?.logos?.light ?? fallbackLogo ?? FALLBACK_FORM.logoUrl,
    logoFile: null,
    primaryColor: theme?.colors?.primary ?? FALLBACK_FORM.primaryColor,
    secondaryColor: theme?.colors?.secondary ?? FALLBACK_FORM.secondaryColor,
    accentColor: theme?.colors?.accent ?? FALLBACK_FORM.accentColor,
    successColor: theme?.colors?.success ?? FALLBACK_FORM.successColor,
    warningColor: theme?.colors?.warning ?? FALLBACK_FORM.warningColor,
    errorColor: theme?.colors?.error ?? FALLBACK_FORM.errorColor,
    textPrimary: theme?.text?.primary ?? FALLBACK_FORM.textPrimary,
    textSecondary: theme?.text?.secondary ?? FALLBACK_FORM.textSecondary,
    backgroundPrimary: theme?.background?.primary ?? FALLBACK_FORM.backgroundPrimary,
    backgroundSecondary: theme?.background?.secondary ?? FALLBACK_FORM.backgroundSecondary,
    backgroundCard: theme?.background?.card ?? FALLBACK_FORM.backgroundCard,
  }
}

type ThemeUpdatePayload = Record<string, unknown>

export const useThemeStore = defineStore('theme', () => {
  const authStore = useAuthStore()

  const loadingTheme = ref(false)
  const savingTheme = ref(false)
  const resettingTheme = ref(false)
  const error = ref<string | null>(null)

  const selectedTheme = computed(() => authStore.selectedCompany?.theme ?? null)

  const formDefaults = computed<ThemeFormValues>(() =>
    buildFormFromTheme(selectedTheme.value, authStore.selectedCompany?.company.logo),
  )

  const getCompanyUuid = () => authStore.selectedCompany?.company.uuid

  const updateCompanyTheme = (theme: CompanyTheme) => {
    const currentCompany = authStore.selectedCompany
    if (!currentCompany) return
    authStore.setCompany({ ...currentCompany, theme })
  }

  const buildUpdatePayload = (form: ThemeFormValues): ThemeUpdatePayload | FormData => {
    const payload: ThemeUpdatePayload = {
      primary_color: form.primaryColor,
      secondary_color: form.secondaryColor,
      accent_color: form.accentColor,
      success_color: form.successColor,
      warning_color: form.warningColor,
      error_color: form.errorColor,
      text_primary: form.textPrimary,
      text_secondary: form.textSecondary,
      background_color: form.backgroundPrimary,
      background_secondary: form.backgroundSecondary,
      card_background: form.backgroundCard,
    }

    const currentExtraConfig = (authStore.selectedCompany?.theme?.extra_config ?? {}) as Record<string, unknown>
    const nextExtraConfig = { ...currentExtraConfig }

    if (form.logoMode === 'url') {
      if (form.logoUrl) {
        nextExtraConfig.logo_url_override = form.logoUrl
      } else {
        delete nextExtraConfig.logo_url_override
      }
    } else if (nextExtraConfig.logo_url_override) {
      delete nextExtraConfig.logo_url_override
    }

    if (JSON.stringify(nextExtraConfig) !== JSON.stringify(currentExtraConfig)) {
      payload.extra_config = nextExtraConfig
    }

    const shouldSendFile = form.logoMode === 'upload' && !!form.logoFile
    if (shouldSendFile) {
      const formData = new FormData()
      Object.entries(payload).forEach(([key, value]) => {
        if (value === undefined || value === null) return
        if (key === 'extra_config' && typeof value === 'object') {
          formData.append(key, JSON.stringify(value))
        } else {
          formData.append(key, String(value))
        }
      })

      formData.append('logo_light', form.logoFile as File)
      return formData
    }

    return payload
  }

  const fetchCompanyTheme = async (companyUuid?: string) => {
    const targetUuid = companyUuid ?? getCompanyUuid()
    if (!targetUuid) return null
    loadingTheme.value = true
    error.value = null
    try {
      const { data } = await api.get<CompanyTheme>(`/companies/themes/${targetUuid}/`)
      updateCompanyTheme(data)
      return data
    } catch (err: any) {
      error.value = err?.response?.data?.detail ?? 'Não foi possível carregar o tema da empresa.'
      throw err
    } finally {
      loadingTheme.value = false
    }
  }

  const updateTheme = async (form: ThemeFormValues) => {
    const companyUuid = getCompanyUuid()
    if (!companyUuid) {
      throw new Error('Nenhuma empresa selecionada.')
    }
    savingTheme.value = true
    error.value = null
    try {
      const payload = buildUpdatePayload(form)
      const { data } = await api.patch<CompanyTheme>(`/companies/themes/${companyUuid}/`, payload)

      if (form.logoMode === 'url' && form.logoUrl) {
        data.logos = {
          ...data.logos,
          light: form.logoUrl,
        }
        data.extra_config = {
          ...(data.extra_config ?? {}),
          logo_url_override: form.logoUrl,
        }
      } else if (form.logoMode === 'url' && !form.logoUrl) {
        if (data.extra_config) {
          delete data.extra_config.logo_url_override
        }
      } else if (form.logoMode === 'upload' && data.extra_config) {
        delete data.extra_config.logo_url_override
      }

      updateCompanyTheme(data)

      try {
        await fetchCompanyTheme(companyUuid)
      } catch (refreshError) {
        console.warn('Não foi possível atualizar o tema após salvar.', refreshError)
      }

      return data
    } catch (err: any) {
      error.value = err?.response?.data?.detail ?? 'Não foi possível salvar o tema.'
      throw err
    } finally {
      savingTheme.value = false
    }
  }

  const resetThemeToCompanyDefaults = async () => {
    const companyUuid = getCompanyUuid()
    if (!companyUuid) {
      throw new Error('Nenhuma empresa selecionada.')
    }
    resettingTheme.value = true
    error.value = null
    try {
      const { data } = await api.post<CompanyTheme>(`/companies/themes/${companyUuid}/reset_to_default/`)
      updateCompanyTheme(data)
      return data
    } catch (err: any) {
      error.value = err?.response?.data?.detail ?? 'Não foi possível restaurar o tema.'
      throw err
    } finally {
      resettingTheme.value = false
    }
  }

  return {
    loadingTheme,
    savingTheme,
    resettingTheme,
    error,
    selectedTheme,
    formDefaults,
    fetchCompanyTheme,
    updateTheme,
    resetThemeToCompanyDefaults,
  }
})
