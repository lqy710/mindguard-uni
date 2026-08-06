/**
 * 用户状态管理（从原项目复用，改造点：
 * - localStorage/sessionStorage → uni.setStorageSync / uni.getStorageSync
 * - 移除 wsService（WebSocket 后续单独封装为 uni.connectSocket）
 * 对应 legacy/frontend-src/stores/user.ts
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo } from '@/types/user'
import { login, getCurrentUser } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(uni.getStorageSync('token') || '')
  const userInfo = ref<UserInfo | null>(null)

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.role === 'admin')

  async function loginAction(username: string, password: string) {
    const res = await login({ username, password })
    token.value = res.token
    userInfo.value = res.user
    uni.setStorageSync('token', res.token)
    return res
  }

  async function fetchUserInfo() {
    if (!token.value) return
    try {
      const user = await getCurrentUser()
      userInfo.value = user
      return user
    } catch (error) {
      logoutAction()
      throw error
    }
  }

  function logoutAction() {
    token.value = ''
    userInfo.value = null
    uni.removeStorageSync('token')
  }

  function setToken(newToken: string) {
    token.value = newToken
    uni.setStorageSync('token', newToken)
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    isAdmin,
    loginAction,
    logoutAction,
    fetchUserInfo,
    setToken
  }
})
