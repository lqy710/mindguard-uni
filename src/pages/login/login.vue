<template>
  <view class="login-page">
    <!-- 1. 顶部品牌区域（占屏幕 40% 高度） -->
    <view class="brand-section">
      <view class="status-bar-spacer" :style="{ height: statusBarHeight + 'px' }"></view>
      <view class="brand-content">
        <view class="logo-circle">
          <MIcon class="logo-heart" name="heart" :size="25" color="#FBFAF6" />
        </view>
        <text class="brand-title">心灵驿站</text>
        <text class="brand-subtitle">每一份情绪都值得被温柔以待</text>
      </view>
    </view>

    <!-- 2. 表单区域（surface 卡片，距顶部 -60rpx 叠加） -->
    <view class="form-card">
      <!-- Tab 切换 -->
      <view class="tabs">
        <view
          class="tab"
          :class="{ active: activeTab === 'login' }"
          @click="switchTab('login')"
        >
          <text class="tab-text">登录</text>
          <view v-if="activeTab === 'login'" class="tab-bar"></view>
        </view>
        <view
          class="tab"
          :class="{ active: activeTab === 'register' }"
          @click="switchTab('register')"
        >
          <text class="tab-text">注册</text>
          <view v-if="activeTab === 'register'" class="tab-bar"></view>
        </view>
      </view>

      <!-- 表单内容容器 -->
      <view class="form-container">
        <!-- 登录表单 -->
        <view class="form-body" :class="{ 'form-hidden': activeTab !== 'login' }">
          <view class="input-item" :class="{ focused: focusedField === 'loginUsername' }">
            <MIcon class="input-icon" name="user" :size="20" color="#6B645C" />
            <input
              class="input"
              v-model="loginForm.username"
              placeholder="手机号/邮箱"
              placeholder-class="input-placeholder"
              :maxlength="64"
              @focus="focusedField = 'loginUsername'"
              @blur="focusedField = ''"
            />
          </view>

          <view class="input-item" :class="{ focused: focusedField === 'loginPassword' }">
            <MIcon class="input-icon" name="lock" :size="20" color="#6B645C" />
            <input
              class="input"
              v-model="loginForm.password"
              :password="!showLoginPassword"
              placeholder="请输入密码"
              placeholder-class="input-placeholder"
              :maxlength="32"
              @focus="focusedField = 'loginPassword'"
              @blur="focusedField = ''"
            />
            <view class="eye-btn" @click="showLoginPassword = !showLoginPassword">
              <MIcon :name="showLoginPassword ? 'eye-off' : 'eye'" :size="20" color="#6B645C" />
            </view>
          </view>

          <view class="forgot-row">
            <text class="forgot-link" @click="onForgotPassword">忘记密码？</text>
          </view>

          <button class="submit-btn" :loading="loginLoading" @click="handleLogin">
            登 录
          </button>

          <view class="switch-link-row">
            <text class="switch-text">还没有账号？</text>
            <text class="switch-link" @click="switchTab('register')">立即注册</text>
          </view>
        </view>

        <!-- 注册表单 -->
        <view class="form-body" :class="{ 'form-hidden': activeTab !== 'register' }">
          <view class="input-item" :class="{ focused: focusedField === 'regUsername' }">
            <MIcon class="input-icon" name="user" :size="20" color="#6B645C" />
            <input
              class="input"
              v-model="registerForm.username"
              placeholder="设置用户名"
              placeholder-class="input-placeholder"
              :maxlength="20"
              @focus="focusedField = 'regUsername'"
              @blur="focusedField = ''"
            />
          </view>

          <view class="input-item" :class="{ focused: focusedField === 'regPassword' }">
            <MIcon class="input-icon" name="lock" :size="20" color="#6B645C" />
            <input
              class="input"
              v-model="registerForm.password"
              :password="!showRegPassword"
              placeholder="设置密码（不少于 6 位）"
              placeholder-class="input-placeholder"
              :maxlength="32"
              @focus="focusedField = 'regPassword'"
              @blur="focusedField = ''"
            />
            <view class="eye-btn" @click="showRegPassword = !showRegPassword">
              <MIcon :name="showRegPassword ? 'eye-off' : 'eye'" :size="20" color="#6B645C" />
            </view>
          </view>

          <view class="input-item" :class="{ focused: focusedField === 'regConfirm' }">
            <MIcon class="input-icon" name="lock" :size="20" color="#6B645C" />
            <input
              class="input"
              v-model="registerForm.confirmPassword"
              :password="!showRegConfirm"
              placeholder="确认密码"
              placeholder-class="input-placeholder"
              :maxlength="32"
              @focus="focusedField = 'regConfirm'"
              @blur="focusedField = ''"
            />
            <view class="eye-btn" @click="showRegConfirm = !showRegConfirm">
              <MIcon :name="showRegConfirm ? 'eye-off' : 'eye'" :size="20" color="#6B645C" />
            </view>
          </view>

          <view class="input-item" :class="{ focused: focusedField === 'regEmail' }">
            <MIcon class="input-icon" name="mail" :size="20" color="#6B645C" />
            <input
              class="input"
              v-model="registerForm.email"
              placeholder="邮箱（选填）"
              placeholder-class="input-placeholder"
              :maxlength="64"
              @focus="focusedField = 'regEmail'"
              @blur="focusedField = ''"
            />
          </view>

          <button class="submit-btn" :loading="registerLoading" @click="handleRegister">
            注 册
          </button>

          <view class="switch-link-row">
            <text class="switch-text">已有账号？</text>
            <text class="switch-link" @click="switchTab('login')">去登录</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 3. 底部信任标识 -->
    <view class="trust-badges">
      <view class="badge"><MIcon class="badge-icon" name="shield" :size="18" color="#3A6359" /><text class="badge-text">隐私保护</text></view>
      <view class="badge"><MIcon class="badge-icon" name="clipboard-check" :size="18" color="#3A6359" /><text class="badge-text">专业量表</text></view>
      <view class="badge"><MIcon class="badge-icon" name="brain" :size="18" color="#3A6359" /><text class="badge-text">AI陪伴</text></view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useUserStore } from '@/stores/user'
import { register } from '@/api/auth'
import MIcon from '@/components/MIcon.vue'

const userStore = useUserStore()

const statusBarHeight = ref(0)
const activeTab = ref<'login' | 'register'>('login')
const focusedField = ref('')
const loginLoading = ref(false)
const registerLoading = ref(false)
const showLoginPassword = ref(false)
const showRegPassword = ref(false)
const showRegConfirm = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  email: ''
})

onLoad(() => {
  try {
    const sys = uni.getSystemInfoSync()
    statusBarHeight.value = sys.statusBarHeight || 0
  } catch {
    statusBarHeight.value = 0
  }
})

function switchTab(tab: 'login' | 'register') {
  activeTab.value = tab
  focusedField.value = ''
}

function validateLogin(): boolean {
  if (!loginForm.username.trim()) {
    uni.showToast({ title: '请输入用户名', icon: 'none' })
    return false
  }
  if (!loginForm.password) {
    uni.showToast({ title: '请输入密码', icon: 'none' })
    return false
  }
  if (loginForm.password.length < 6) {
    uni.showToast({ title: '密码不少于 6 位', icon: 'none' })
    return false
  }
  return true
}

function validateRegister(): boolean {
  if (!registerForm.username.trim()) {
    uni.showToast({ title: '请输入用户名', icon: 'none' })
    return false
  }
  if (registerForm.username.trim().length < 3) {
    uni.showToast({ title: '用户名至少 3 个字符', icon: 'none' })
    return false
  }
  if (!registerForm.password || registerForm.password.length < 6) {
    uni.showToast({ title: '密码不少于 6 位', icon: 'none' })
    return false
  }
  if (registerForm.confirmPassword !== registerForm.password) {
    uni.showToast({ title: '两次密码不一致', icon: 'none' })
    return false
  }
  if (registerForm.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(registerForm.email)) {
    uni.showToast({ title: '邮箱格式不正确', icon: 'none' })
    return false
  }
  return true
}

async function handleLogin() {
  if (!validateLogin()) return
  loginLoading.value = true
  try {
    await userStore.loginAction(loginForm.username.trim(), loginForm.password)
    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(() => {
      uni.switchTab({ url: '/pages/home/home' })
    }, 400)
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : '登录失败'
    uni.showToast({ title: msg || '登录失败', icon: 'none' })
  } finally {
    loginLoading.value = false
  }
}

async function handleRegister() {
  if (!validateRegister()) return
  registerLoading.value = true
  try {
    await register({
      username: registerForm.username.trim(),
      password: registerForm.password,
      email: registerForm.email || undefined
    })
    uni.showToast({ title: '注册成功，请登录', icon: 'success' })
    loginForm.username = registerForm.username.trim()
    registerForm.username = ''
    registerForm.password = ''
    registerForm.confirmPassword = ''
    registerForm.email = ''
    activeTab.value = 'login'
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : '注册失败'
    uni.showToast({ title: msg || '注册失败', icon: 'none' })
  } finally {
    registerLoading.value = false
  }
}

function onForgotPassword() {
  uni.showToast({ title: '请联系管理员重置密码', icon: 'none' })
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: #EDE9E1;
  display: flex;
  flex-direction: column;
}

/* 1. 顶部品牌区域：sage-deep 纯色背景 */
.brand-section {
  height: 40vh;
  background: #3A6359;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.status-bar-spacer {
  width: 100%;
}

.brand-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.logo-circle {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  background: rgba(251, 250, 246, 0.18);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24rpx;
}

.logo-heart {
  font-size: 52rpx;
  line-height: 1;
}

.brand-title {
  font-size: 40rpx;
  font-weight: 700;
  color: #FBFAF6;
  letter-spacing: 4rpx;
  margin-bottom: 12rpx;
}

.brand-subtitle {
  font-size: 26rpx;
  color: rgba(251, 250, 246, 0.85);
  letter-spacing: 2rpx;
}

/* 2. 表单区域：surface 背景 */
.form-card {
  margin-top: -60rpx;
  background: #FBFAF6;
  border-radius: 40rpx 40rpx 0 0;
  padding: 48rpx 40rpx 40rpx;
  min-height: 60vh;
}

.tabs {
  display: flex;
  margin-bottom: 48rpx;
}

.tab {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-bottom: 20rpx;
  position: relative;
}

.tab-text {
  font-size: 32rpx;
  font-weight: 600;
  color: #6B645C;
  transition: color 0.25s;
}

.tab.active .tab-text {
  color: #2A2722;
}

.tab-bar {
  position: absolute;
  bottom: 0;
  width: 64rpx;
  height: 6rpx;
  border-radius: 3rpx;
  background: #3A6359;
}

.form-container {
  width: 100%;
}

.form-body {
  display: flex;
  flex-direction: column;
}

.form-body.form-hidden {
  display: none !important;
}

/* 输入框：surface-2 背景 + hairline 边框 */
.input-item {
  display: flex;
  align-items: center;
  height: 96rpx;
  background: #F2EFE8;
  border: 2rpx solid #E2DDD2;
  border-radius: 20rpx;
  padding: 0 24rpx;
  margin-bottom: 28rpx;
  transition: all 0.25s;
}

.input-item.focused {
  background: #FBFAF6;
  border-color: #3A6359;
}

.input-icon {
  font-size: 32rpx;
  margin-right: 16rpx;
  line-height: 1;
}

.input {
  flex: 1;
  height: 96rpx;
  font-size: 30rpx;
  color: #2A2722;
  background: transparent;
}

.input-placeholder {
  color: #6B645C;
  font-size: 28rpx;
}

.eye-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10rpx;
}

.forgot-row {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 32rpx;
  margin-top: -4rpx;
}

.forgot-link {
  font-size: 26rpx;
  color: #3A6359;
  font-weight: 500;
}

/* 提交按钮：sage-deep 背景 */
.submit-btn {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  border-radius: 48rpx;
  background: #3A6359;
  color: #FBFAF6;
  font-size: 32rpx;
  font-weight: 600;
  letter-spacing: 8rpx;
  border: none;
  box-shadow: 0 8rpx 24rpx rgba(58, 99, 89, 0.3);
}

.submit-btn::after {
  border: none;
}

.switch-link-row {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 36rpx;
}

.switch-text {
  font-size: 26rpx;
  color: #6B645C;
}

.switch-link {
  font-size: 26rpx;
  color: #3A6359;
  font-weight: 600;
  margin-left: 6rpx;
}

/* 3. 底部信任标识：surface 背景 */
.trust-badges {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40rpx 32rpx;
  padding-bottom: calc(40rpx + env(safe-area-inset-bottom));
}

.badge {
  display: flex;
  align-items: center;
  padding: 12rpx 24rpx;
  background: #FBFAF6;
  border-radius: 32rpx;
  margin: 0 12rpx;
  border: 2rpx solid #E2DDD2;
}

.badge-icon {
  font-size: 24rpx;
  margin-right: 8rpx;
  line-height: 1;
}

.badge-text {
  font-size: 22rpx;
  color: #6B645C;
}
</style>
