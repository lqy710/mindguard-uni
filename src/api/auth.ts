/**
 * 认证相关 API（从原项目复用，仅改 import 路径）
 * 对应 legacy/frontend-src/api/auth.ts
 */
import { get, post, put } from '@/utils/request'
import type { UserInfo } from '@/types/user'

export interface LoginParams {
  username: string
  password: string
}

export interface RegisterParams {
  username: string
  password: string
  email?: string
  phone?: string
  nickname?: string
  gender?: number
  age?: number
}

export interface LoginResult {
  token: string
  user: UserInfo
  expiresAt: string
}

export function login(data: LoginParams): Promise<LoginResult> {
  return post<LoginResult>('/auth/login', data as unknown as Record<string, unknown>)
}

export function register(data: RegisterParams): Promise<UserInfo> {
  return post<UserInfo>('/auth/register', data as unknown as Record<string, unknown>)
}

export function getCurrentUser(): Promise<UserInfo> {
  return get<UserInfo>('/auth/me')
}

export function updateProfile(data: Partial<UserInfo>): Promise<UserInfo> {
  return put<UserInfo>('/user/profile', data as unknown as Record<string, unknown>)
}

export function getUserStats(): Promise<{
  assessmentCount: number
  diaryCount: number
  streakDays: number
}> {
  return get('/user/stats')
}

export function logout(): Promise<void> {
  return Promise.resolve()
}
