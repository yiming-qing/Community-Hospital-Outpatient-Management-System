import axios from 'axios'

import { clearAuth, getToken } from '../utils/storage'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 15000,
})

http.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  (resp) => resp,
  (err) => {
    const status = err?.response?.status
    const body = err?.response?.data

    const message = body?.error?.message || body?.msg || err?.message || '请求失败'
    const e = new Error(message)
    e.code = body?.error?.code || (status ? `http_${status}` : 'network_error')
    e.status = status
    e.details = body?.error?.details

    if (status === 401) {
      clearAuth()
    }
    throw e
  },
)

export function unwrap(resp) {
  const body = resp?.data
  if (body?.ok) return body.data
  const message = body?.error?.message || body?.msg || '请求失败'
  const e = new Error(message)
  e.code = body?.error?.code || 'request_failed'
  throw e
}

export default http
