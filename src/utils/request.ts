/**
 * uni.request 请求封装（替代 axios）
 * 对应原项目 legacy/frontend-src/utils/request.ts
 * 后端接口约定：{ code: number, message: string, data: T }，code===200 为成功
 */
import { API_BASE_URL } from '@/config'

export interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: Record<string, unknown> | string
  header?: Record<string, string>
  /** 是否跳过自动 401 跳转登录页 */
  skipAuthRedirect?: boolean
}

function getToken(): string {
  return uni.getStorageSync('token') || ''
}

function showError(msg: string) {
  uni.showToast({ title: msg || '请求失败', icon: 'none' })
}

/**
 * 核心请求函数，返回 Promise<T>（已自动解包 data 字段）
 */
export function request<T = unknown>(options: RequestOptions): Promise<T> {
  const { url, method = 'GET', data, header = {}, skipAuthRedirect = false } = options

  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...header
  }
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  return new Promise<T>((resolve, reject) => {
    uni.request({
      url: url.startsWith('http') ? url : API_BASE_URL + url,
      method,
      data,
      header: headers,
      success: (res) => {
        const statusCode = res.statusCode
        const body = res.data as { code?: number; message?: string; data?: unknown }

        if (statusCode === 401 && !skipAuthRedirect) {
          uni.removeStorageSync('token')
          uni.reLaunch({ url: '/pages/login/login' })
          showError('登录已过期，请重新登录')
          reject(new Error('未授权'))
          return
        }

        if (statusCode === 403) {
          showError('没有权限访问')
          reject(new Error('无权限'))
          return
        }

        if (statusCode < 200 || statusCode >= 300) {
          showError(`网络错误(${statusCode})`)
          reject(new Error(`HTTP ${statusCode}`))
          return
        }

        // 后端统一响应体
        if (body && typeof body.code === 'number') {
          if (body.code === 200) {
            resolve(body.data as T)
          } else {
            showError(body.message || '请求失败')
            reject(new Error(body.message || '业务错误'))
          }
          return
        }

        // 非标准响应体直接返回
        resolve(body as unknown as T)
      },
      fail: (err) => {
        showError(err.errMsg || '网络请求失败')
        reject(new Error(err.errMsg))
      }
    })
  })
}

/** GET 请求 */
export function get<T = unknown>(url: string, params?: Record<string, unknown>): Promise<T> {
  let queryUrl = url
  if (params) {
    const qs = Object.entries(params)
      .filter(([, v]) => v !== undefined && v !== null)
      .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
      .join('&')
    if (qs) queryUrl += (url.includes('?') ? '&' : '?') + qs
  }
  return request<T>({ url: queryUrl, method: 'GET' })
}

/** POST 请求 */
export function post<T = unknown>(url: string, data?: Record<string, unknown>): Promise<T> {
  return request<T>({ url, method: 'POST', data })
}

/** PUT 请求 */
export function put<T = unknown>(url: string, data?: Record<string, unknown>): Promise<T> {
  return request<T>({ url, method: 'PUT', data })
}

/** DELETE 请求 */
export function del<T = unknown>(url: string): Promise<T> {
  return request<T>({ url, method: 'DELETE' })
}

export default request
