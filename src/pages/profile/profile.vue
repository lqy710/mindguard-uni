<template>
  <view class="profile-page">
    <!-- 1. 页面头部：标题 + 设置按钮 -->
    <view class="page-header">
      <text class="page-title">我的</text>
      <view class="icon-btn" @tap="onSettings">
        <MIcon name="settings" :size="20" color="#4A453E" />
      </view>
    </view>

    <!-- 2. 用户信息：居中头像 + 昵称 + 副标题 + 3 项统计 -->
    <view class="profile-header">
      <view class="profile-avatar">
        <image
          v-if="userStore.userInfo?.avatar"
          class="avatar-img"
          :src="userStore.userInfo.avatar"
          mode="aspectFill"
        />
        <text v-else class="avatar-text">{{ avatarLetter }}</text>
      </view>
      <text class="profile-name">{{ displayName }}</text>
      <text class="profile-sub">{{ profileSub }}</text>
      <view class="profile-stats">
        <view class="profile-stat">
          <text class="profile-stat-num">{{ stats.streakDays }}</text>
          <text class="profile-stat-label">连续打卡</text>
        </view>
        <view class="profile-stat">
          <text class="profile-stat-num">{{ stats.assessmentCount }}</text>
          <text class="profile-stat-label">测评次数</text>
        </view>
        <view class="profile-stat">
          <text class="profile-stat-num">{{ stats.diaryCount }}</text>
          <text class="profile-stat-label">日记篇数</text>
        </view>
      </view>
    </view>

    <!-- 3. 功能列表1：我的日记 / 测评记录 / 对话历史 -->
    <view class="profile-list">
      <view class="profile-row" @tap="goDiary">
        <view class="profile-row-icon sage">
          <MIcon name="notebook-pen" :size="18" color="#3A6359" />
        </view>
        <text class="profile-row-name">我的日记</text>
        <text class="profile-row-val">{{ stats.diaryCount }} 篇</text>
        <MIcon name="chevron" :size="14" color="#6B645C" />
      </view>
      <view class="profile-row" @tap="goAssessmentList">
        <view class="profile-row-icon lavender">
          <MIcon name="heart-pulse" :size="18" color="#6B5B9E" />
        </view>
        <text class="profile-row-name">测评记录</text>
        <text class="profile-row-val">{{ stats.assessmentCount }} 次</text>
        <MIcon name="chevron" :size="14" color="#6B645C" />
      </view>
      <view class="profile-row" @tap="goChat">
        <view class="profile-row-icon amber">
          <MIcon name="chat" :size="18" color="#B8862F" />
        </view>
        <text class="profile-row-name">对话历史</text>
        <text class="profile-row-val">{{ chatCount }} 条</text>
        <MIcon name="chevron" :size="14" color="#6B645C" />
      </view>
    </view>

    <!-- 4. 功能列表2：打卡提醒 / 隐私与安全 / 帮助与反馈 -->
    <view class="profile-list">
      <view class="profile-row" @tap="comingSoon">
        <view class="profile-row-icon sage">
          <MIcon name="bell-ring" :size="18" color="#3A6359" />
        </view>
        <text class="profile-row-name">打卡提醒</text>
        <text class="profile-row-val">每天 9:00</text>
        <MIcon name="chevron" :size="14" color="#6B645C" />
      </view>
      <view class="profile-row" @tap="comingSoon">
        <view class="profile-row-icon coral">
          <MIcon name="shield" :size="18" color="#C26B4F" />
        </view>
        <text class="profile-row-name">隐私与安全</text>
        <MIcon name="chevron" :size="14" color="#6B645C" />
      </view>
      <view class="profile-row" @tap="comingSoon">
        <view class="profile-row-icon lavender">
          <MIcon name="circle-help" :size="18" color="#6B5B9E" />
        </view>
        <text class="profile-row-name">帮助与反馈</text>
        <MIcon name="chevron" :size="14" color="#6B645C" />
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/stores/user'
import { getUserStats } from '@/api/auth'
import { getAssessmentHistory, type AssessmentResult } from '@/api/assessment'
import MIcon from '@/components/MIcon.vue'

const userStore = useUserStore()

const loading = ref(false)
const stats = reactive({
  assessmentCount: 0,
  diaryCount: 0,
  streakDays: 0
})

// 对话历史条数（暂无独立接口，前端兜底占位）
const chatCount = ref(0)

interface RecentAssessment {
  id: number
  name: string
  date: string
  score: number
  riskLabel: string
  riskColor: string
  riskBg: string
  icon: string
  gradient: string
}

const recentAssessments = ref<RecentAssessment[]>([])

const avatarLetter = computed(
  () =>
    userStore.userInfo?.nickname?.charAt(0) ||
    userStore.userInfo?.username?.charAt(0) ||
    'U'
)
const displayName = computed(
  () => userStore.userInfo?.nickname || userStore.userInfo?.username || '用户'
)
const userEmail = computed(() => userStore.userInfo?.email || '未设置邮箱')
const profileSub = computed(() => `使用 MindGuard 第 ${stats.streakDays} 天`)

const ICON_GRADIENTS = [
  'linear-gradient(135deg, #4A7C6F, #3A6359)',
  'linear-gradient(135deg, #C26B4F, #A85638)',
  'linear-gradient(135deg, #6B5B9E, #574A82)',
  'linear-gradient(135deg, #B8862F, #9A7027)'
]

const badges = [
  { name: '坚持记录', icon: 'flame', gradient: 'linear-gradient(135deg, #C26B4F, #A85638)', earned: true },
  { name: '积极心态', icon: 'star', gradient: 'linear-gradient(135deg, #4A7C6F, #3A6359)', earned: true },
  { name: '关爱自己', icon: 'heart', gradient: 'linear-gradient(135deg, #4A7C6F, #3A6359)', earned: true },
  { name: '月度达人', icon: 'trophy', gradient: 'linear-gradient(135deg, #6B5B9E, #574A82)', earned: false },
  { name: '心理大师', icon: 'award', gradient: 'linear-gradient(135deg, #B8862F, #9A7027)', earned: false }
]

const menuAccount = [
  { icon: 'user', text: '编辑资料', action: () => comingSoon() },
  { icon: 'lock', text: '账户安全', action: () => comingSoon() },
  { icon: 'bell', text: '消息通知', action: () => comingSoon() }
]
const menuOther = [
  { icon: 'circle-help', text: '关于我们', action: () => comingSoon() },
  { icon: 'mail', text: '意见反馈', action: () => comingSoon() },
  { icon: 'clipboard-check', text: '隐私政策', action: () => comingSoon() },
  { icon: 'file-text', text: '用户协议', action: () => comingSoon() }
]

function getScaleEmoji(name: string): string {
  if (name.includes('抑郁')) return 'heart'
  if (name.includes('焦虑')) return 'wind'
  if (name.includes('压力')) return 'activity'
  if (name.includes('睡眠')) return 'moon-star'
  if (name.includes('症状') || name.includes('SCL')) return 'clipboard-check'
  return 'sparkles'
}

function getRiskStyle(riskLevel: string, riskText: string) {
  const level = (riskLevel || '').toLowerCase()
  const text = riskText || ''
  if (level.includes('severe') || text.includes('重度')) {
    return { label: '重度', color: '#C26B4F', bg: 'rgba(194,107,79,0.14)' }
  }
  if (level.includes('moderate') || text.includes('中度')) {
    return { label: '中度', color: '#B8862F', bg: 'rgba(184,134,47,0.14)' }
  }
  if (level.includes('mild') || text.includes('轻度')) {
    return { label: '轻度', color: '#B8862F', bg: 'rgba(184,134,47,0.14)' }
  }
  return { label: '正常', color: '#3A6359', bg: 'rgba(58,99,89,0.14)' }
}

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  if (Number.isNaN(d.getTime())) return dateStr.slice(0, 10)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function mapRecent(records: AssessmentResult[]): RecentAssessment[] {
  return records.map((r, idx) => {
    const style = getRiskStyle(r.riskLevel, r.riskText)
    return {
      id: r.assessmentId,
      name: r.scaleName,
      date: formatDate(r.createdAt),
      score: r.totalScore,
      riskLabel: style.label,
      riskColor: style.color,
      riskBg: style.bg,
      icon: getScaleEmoji(r.scaleName),
      gradient: ICON_GRADIENTS[idx % ICON_GRADIENTS.length]
    }
  })
}

async function loadStats() {
  try {
    const data = await getUserStats()
    if (data) {
      stats.assessmentCount = data.assessmentCount || 0
      stats.diaryCount = data.diaryCount || 0
      stats.streakDays = data.streakDays || 0
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

async function loadRecentAssessments() {
  try {
    const res = await getAssessmentHistory({ current: 1, size: 3 })
    recentAssessments.value = res?.records ? mapRecent(res.records) : []
  } catch (error) {
    console.error('加载最近测评失败:', error)
    recentAssessments.value = []
  }
}

async function refreshAll() {
  if (!userStore.token) return
  loading.value = true
  if (!userStore.userInfo) {
    await userStore.fetchUserInfo().catch(() => {})
  }
  await Promise.all([loadStats(), loadRecentAssessments()])
  loading.value = false
}

function goAssessmentList() {
  uni.switchTab({ url: '/pages/assessment/list' })
}

function goDiary() {
  uni.navigateTo({ url: '/pages/diary/diary' })
}

function goChat() {
  uni.switchTab({ url: '/pages/chat/chat' })
}

function goResult(id: number) {
  uni.navigateTo({ url: `/pages/assessment/result?id=${id}` })
}

function comingSoon() {
  uni.showToast({ title: '功能开发中', icon: 'none' })
}

function onSettings() {
  uni.showToast({ title: '功能开发中', icon: 'none' })
}

function handleLogout() {
  uni.showModal({
    title: '提示',
    content: '确定要退出登录吗？',
    confirmColor: '#C26B4F',
    success: (res) => {
      if (!res.confirm) return
      userStore.logoutAction()
      uni.showToast({ title: '已退出登录', icon: 'success' })
      setTimeout(() => {
        uni.reLaunch({ url: '/pages/login/login' })
      }, 300)
    }
  })
}

onShow(() => {
  // 登录守卫：未登录跳转登录页
  if (!userStore.isLoggedIn) {
    uni.reLaunch({ url: '/pages/login/login' })
    return
  }
  refreshAll()
})
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: #EDE9E1; /* bg */
  padding-bottom: 48rpx;
}

/* 1. 页面头部 */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 32rpx 40rpx 24rpx; /* sp-4 sp-5 sp-3 */
}

.page-title {
  font-size: 48rpx; /* fz-display 24px */
  font-weight: 700;
  color: #2A2722; /* ink */
  letter-spacing: -0.6rpx;
}

.icon-btn {
  width: 80rpx; /* 40px */
  height: 80rpx;
  border-radius: 999rpx;
  background: #FBFAF6; /* surface */
  border: 2rpx solid #E2DDD2; /* border */
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-btn:active {
  background: #F2EFE8; /* surface-2 */
}

/* 2. 用户信息 */
.profile-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48rpx 40rpx 40rpx; /* sp-6 sp-5 sp-5 */
}

.profile-avatar {
  width: 160rpx; /* 80px */
  height: 160rpx;
  border-radius: 999rpx;
  background: #E6EEEA; /* sage-tint */
  border: 4rpx solid #4A7C6F; /* sage */
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24rpx; /* sp-3 */
  overflow: hidden;
}

.avatar-img {
  width: 100%;
  height: 100%;
}

.avatar-text {
  font-size: 64rpx; /* 32px */
  font-weight: 600;
  color: #3A6359; /* sage-deep */
}

.profile-name {
  font-size: 34rpx; /* fz-h2 17px */
  font-weight: 700;
  color: #2A2722; /* ink */
}

.profile-sub {
  font-size: 26rpx; /* fz-cap 13px */
  color: #6B645C; /* muted */
  margin-top: 6rpx;
}

.profile-stats {
  display: flex;
  gap: 64rpx; /* sp-8 32px */
  margin-top: 40rpx; /* sp-5 */
}

.profile-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.profile-stat-num {
  font-size: 44rpx; /* 22px */
  font-weight: 700;
  color: #3A6359; /* sage-deep */
  line-height: 1.1;
}

.profile-stat-label {
  font-size: 24rpx; /* fz-micro 12px */
  color: #6B645C; /* muted */
  margin-top: 4rpx;
}

/* 3 & 4. 功能列表（surface 卡片） */
.profile-list {
  margin: 40rpx 40rpx 0; /* sp-5 sp-5 */
  background: #FBFAF6; /* surface */
  border: 2rpx solid #E2DDD2; /* border */
  border-radius: 32rpx; /* r-md */
  overflow: hidden;
  box-shadow: 0 2rpx 6rpx rgba(42, 39, 34, 0.04);
}

.profile-row {
  display: flex;
  align-items: center;
  gap: 24rpx; /* sp-3 */
  padding: 24rpx 32rpx; /* sp-3 sp-4 */
  border-bottom: 2rpx solid #E2DDD2; /* border */
  transition: background 0.2s;
}

.profile-row:last-child {
  border-bottom: none;
}

.profile-row:active {
  background: #F2EFE8; /* surface-2 */
}

.profile-row-icon {
  width: 68rpx; /* 34px */
  height: 68rpx;
  border-radius: 16rpx; /* r-xs */
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.profile-row-icon.sage {
  background: #E6EEEA; /* sage-tint */
}

.profile-row-icon.coral {
  background: #F4E3DB; /* coral-tint */
}

.profile-row-icon.lavender {
  background: #E8E3F0; /* lavender-tint */
}

.profile-row-icon.amber {
  background: #F0E8D4; /* amber-tint */
}

.profile-row-name {
  flex: 1;
  font-size: 28rpx; /* fz-body 14px */
  font-weight: 500;
  color: #2A2722; /* ink */
}

.profile-row-val {
  font-size: 24rpx; /* fz-micro 12px */
  color: #6B645C; /* muted */
}
</style>
