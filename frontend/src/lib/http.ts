import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

let isRefreshing = false
let refreshQueue: Array<(token: string | null, error?: unknown) => void> = []

const processRefreshQueue = (token: string | null, error?: unknown) => {
  refreshQueue.forEach((callback) => callback(token, error))
  refreshQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          refreshQueue.push((token, queueError) => {
            if (queueError || !token) {
              reject(queueError ?? new Error('Unable to refresh token'))
              return
            }
            originalRequest.headers.Authorization = `Bearer ${token}`
            resolve(api(originalRequest))
          })
        })
      }

      isRefreshing = true
      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) {
        isRefreshing = false
        processRefreshQueue(null, new Error('Missing refresh token'))
        return Promise.reject(error)
      }

      try {
        const { data } = await axios.post(
          `${API_BASE_URL}/auth/refresh/`,
          { refresh: refreshToken },
          { headers: { 'Content-Type': 'application/json' } },
        )

        localStorage.setItem('access_token', data.access)
        localStorage.setItem('refresh_token', data.refresh)
        api.defaults.headers.common.Authorization = `Bearer ${data.access}`

        processRefreshQueue(data.access)
        originalRequest.headers.Authorization = `Bearer ${data.access}`
        return api(originalRequest)
      } catch (refreshError) {
        processRefreshQueue(null, refreshError)
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        localStorage.removeItem('selected_company')
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  },
)

export default api
