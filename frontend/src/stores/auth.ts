import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

import api from '@/lib/http'
import type { AuthUser, CompanyMembership, LoginResponse } from '@/types/auth'
import { applyThemeFromCompany, resetThemeToDefault } from '@/lib/theme'

interface LoginPayload {
  email: string
  password: string
  persist?: boolean
}

type UpdateProfilePayload = Partial<Pick<AuthUser, 'first_name' | 'last_name' | 'phone'>>
interface ChangePasswordPayload {
  current_password: string
  new_password: string
  new_password_confirm: string
}

const STORAGE_KEYS = {
  access: 'access_token',
  refresh: 'refresh_token',
  user: 'user',
  company: 'selected_company',
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<AuthUser | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem(STORAGE_KEYS.access))
  const refreshToken = ref<string | null>(localStorage.getItem(STORAGE_KEYS.refresh))
  const selectedCompany = ref<CompanyMembership | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => Boolean(user.value && accessToken.value))

  const getErrorMessage = (err: any, fallback = 'Algo deu errado. Tente novamente.') => {
    const data = err?.response?.data
    if (!data) return fallback
    if (typeof data === 'string') return data
    if (typeof data.detail === 'string') return data.detail
    const firstValue = Object.values(data)[0]
    if (Array.isArray(firstValue)) return String(firstValue[0])
    if (typeof firstValue === 'string') return firstValue
    return fallback
  }

  const persistAuthState = () => {
    if (user.value) localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(user.value))
    if (selectedCompany.value) {
      localStorage.setItem(STORAGE_KEYS.company, JSON.stringify(selectedCompany.value))
    }
  }

  const setCompany = (company: CompanyMembership | null) => {
    selectedCompany.value = company
    if (company) {
      localStorage.setItem(STORAGE_KEYS.company, JSON.stringify(company))
      applyThemeFromCompany(company)
    } else {
      localStorage.removeItem(STORAGE_KEYS.company)
      resetThemeToDefault()
    }
  }

  const initializeFromStorage = () => {
    const storedUser = localStorage.getItem(STORAGE_KEYS.user)
    const storedCompany = localStorage.getItem(STORAGE_KEYS.company)
    if (storedUser) {
      user.value = JSON.parse(storedUser) as AuthUser
    }
    if (storedCompany) {
      selectedCompany.value = JSON.parse(storedCompany) as CompanyMembership
    } else if (user.value?.companies?.length) {
      setCompany(user.value.companies[0] ?? null)
    }
    if (selectedCompany.value) applyThemeFromCompany(selectedCompany.value)
  }

  const login = async (payload: LoginPayload) => {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.post<LoginResponse>('/auth/login/', payload)
      accessToken.value = data.access
      refreshToken.value = data.refresh
      user.value = data.user
      if (payload.persist) {
        localStorage.setItem(STORAGE_KEYS.access, data.access)
        localStorage.setItem(STORAGE_KEYS.refresh, data.refresh)
        persistAuthState()
      }

      const companies = data.user.companies ?? []
      if (companies.length === 1) {
        setCompany(companies[0] ?? null)
      } else {
        setCompany(null)
      }
      return true
    } catch (err: any) {
      error.value = err?.response?.data?.detail ?? 'Não foi possível autenticar. Verifique as credenciais.'
      return false
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    selectedCompany.value = null
    error.value = null
    Object.values(STORAGE_KEYS).forEach((key) => localStorage.removeItem(key))
    resetThemeToDefault()
  }

  const updateProfile = async (payload: UpdateProfilePayload) => {
    try {
      const { data } = await api.patch<AuthUser>('/auth/me/', payload)
      user.value = data
      if (localStorage.getItem(STORAGE_KEYS.user)) {
        persistAuthState()
      }
      return { success: true, data }
    } catch (err: any) {
      const message = getErrorMessage(err, 'Não foi possível atualizar o perfil.')
      return { success: false, message }
    }
  }

  const changePassword = async (payload: ChangePasswordPayload) => {
    try {
      const { data } = await api.post('/auth/me/password/', payload)
      return { success: true, data }
    } catch (err: any) {
      const message = getErrorMessage(err, 'Não foi possível alterar a senha.')
      const errors = err?.response?.data && typeof err.response.data === 'object' ? err.response.data : null
      return { success: false, message, errors }
    }
  }

  initializeFromStorage()

  return {
    user,
    accessToken,
    refreshToken,
    selectedCompany,
    loading,
    error,
    isAuthenticated,
    login,
    logout,
    setCompany,
    updateProfile,
    changePassword,
  }
})
